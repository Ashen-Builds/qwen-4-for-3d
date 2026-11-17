"""Fail-closed CCORE sprint coordinator. Default is plan-only; no MLX imports."""
from __future__ import annotations
import argparse
from datetime import datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from zoneinfo import ZoneInfo

TERMINAL = {'stopped', 'deadline', 'complete'}
QUALIFICATION = ['baseline', 'short', 'reload', 'length']


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def milestone_hours(config):
    duration=(datetime.fromisoformat(config['hard_stop'])-datetime.fromisoformat(config['start'])).total_seconds()/3600
    hours=[x['elapsed_hours'] for x in config['milestones'] if x['elapsed_hours']>0]
    if not hours or hours!=sorted(set(hours)) or any(h>duration for h in hours):
        raise ValueError('Milestones must be ordered, unique and within run budget')
    return hours


def window_bounds(config, now):
    local=datetime.fromtimestamp(now,ZoneInfo(config['timezone']))
    window=config.get('compute_window',{'start_hour':23,'stop_hour':9,'drain_minutes':2})
    start=window['start_hour']*60;end=window['stop_hour']*60;current=local.hour*60+local.minute
    drain=end-window.get('drain_minutes',2)
    allowed=current>=start or current<drain
    return allowed,local.replace(hour=window['stop_hour'],minute=0,second=0,microsecond=0).timestamp()-window.get('drain_minutes',2)*60


def new_state(config, run_id):
    start = datetime.fromisoformat(config['start']).timestamp()
    end = datetime.fromisoformat(config['hard_stop']).timestamp()
    if not 0 < end - start <= 48 * 3600:
        raise ValueError('Budget must be positive and at most 48 hours')
    milestone_hours(config)
    return {'schema': 1, 'run_id': run_id, 'config_hash': digest(config),
            'start': start, 'deadline': end, 'phase': 'baseline', 'status': 'ready',
            'active_job': None, 'awaiting_review': None, 'packet_number': 0,
            'qualification': {}, 'latest_checkpoint': None, 'best_checkpoint': None,
            'segment_number': 0, 'job_number': 0, 'confirmed_training_steps': 0, 'crashes': 0, 'regressions': 0,
            'milestones': {}, 'events': [], 'training_started': False,
            'seconds_per_step': None, 'last_sample': None}


class Engine:
    """Pure scheduling/state logic. Effects are returned as job descriptions."""
    def __init__(self, state, config, simulated=False):
        if state['config_hash'] != digest(config):
            raise ValueError('Config changed: explicit rebaseline/handoff required')
        self.s = state
        self.config = config
        self.simulated = simulated

    def event(self, now, kind, **fields):
        self.s['events'].append({'time': now, 'kind': kind, **fields})

    def review(self, now, kind, payload):
        self.s['packet_number'] += 1
        packet = {'schema': 1, 'number': self.s['packet_number'], 'kind': kind,
                  'run_id': self.s['run_id'], 'created': now,
                  'simulated': self.simulated, 'payload': payload}
        packet['sha256'] = digest(packet)
        self.s['awaiting_review'] = packet
        self.s['status'] = 'awaiting_review'
        return packet

    def pause_reason(self, now, flags):
        if flags.get('manual'): return 'manual-pause'
        if flags.get('streaming'): return 'streaming'
        if flags.get('global_pause'): return 'global-gpu-pause'
        allowed,_=window_bounds(self.config,now)
        if not allowed and not flags.get('daytime_approved'):
            return 'owner-computer-time'
        return None

    def milestone_reports(self, now, paused):
        # Metadata-only reports continue while compute or review is paused.
        for h in milestone_hours(self.config):
            key = str(h)
            if now >= self.s['start'] + h * 3600 and key not in self.s['milestones']:
                self.s['milestones'][key] = {
                    'due': self.s['start'] + h * 3600, 'recorded': now,
                    'checkpoint': (self.s['last_sample'] or {}).get('checkpoint'),
                    'latest_training_checkpoint': self.s['latest_checkpoint'],
                    'sample': self.s['last_sample'],
                    'status': 'no-new-output', 'sample_attempted': True,
                    'reason': paused or ('review-pending' if self.s['awaiting_review'] else 'not-yet-generated')}

    def tick(self, now, flags=None):
        flags = flags or {}
        if self.s['status'] in TERMINAL: return None
        paused = self.pause_reason(now, flags)
        self.milestone_reports(now, paused)
        if now >= self.s['deadline']:
            self.s['status'] = 'deadline'
            self.event(now, 'hard-stop')
            return {'action': 'stop', 'reason': 'hard-deadline'}
        if flags.get('stop'):
            self.s['status'] = 'stopped'
            self.event(now, 'operator-stop')
            return {'action': 'stop', 'reason': 'operator-stop'}
        if now < self.s['start']:
            self.s['status'] = 'not-started'
            return None
        if paused:
            self.s['pause_reason'] = paused
            if self.s['active_job']: return {'action': 'stop', 'reason': paused}
            self.s['status'] = 'paused'
            return None
        self.s.pop('pause_reason', None)
        if now < self.s['start']:
            self.s['status'] = 'not-started'
            return None
        if self.s['awaiting_review'] or self.s['active_job']: return None
        if now < self.s.get('defer_until',0):
            self.s['status']='waiting_resource'
            return None
        retry=self.s.pop('pending_retry',None)
        if retry:
            extra={k:retry[k] for k in ['milestone','iterations'] if k in retry}
            return self.launch(now,retry['kind'],**extra)
        phase = self.s['phase']
        if phase in QUALIFICATION:
            return self.launch(now, phase)
        if phase != 'main': return None
        # Start generation one hour before each deadline. During daytime holds,
        # the due packet instead references the last actual completed sample.
        for h in milestone_hours(self.config):
            previous = self.s['milestones'].get(str(h), {})
            if now >= self.s['start'] + h * 3600 - self.config.get('evaluation_lead_seconds',3600) and not previous.get('sample_attempted'):
                if self.s['latest_checkpoint']:
                    return self.launch(now, 'sample', milestone=h)
                previous.update(sample_attempted=True, status='no-checkpoint')
                self.s['milestones'][str(h)] = previous
        next_due = min((self.s['start'] + h*3600 - self.config.get('evaluation_lead_seconds',3600) for h in milestone_hours(self.config)
                        if self.s['start'] + h*3600 - self.config.get('evaluation_lead_seconds',3600) > now), default=self.s['deadline'])
        _,drain=window_bounds(self.config,now)
        availability=drain-now if drain>now and not flags.get('daytime_approved') else 1800
        training_end=self.s['deadline']-self.config.get('final_training_stop_seconds_before_deadline',0)
        if now>=training_end:return None
        budget=min(1500,next_due-now,training_end-now,availability)
        if budget < 90: return None
        sec = self.s['seconds_per_step']
        if not sec or not math.isfinite(sec) or sec <= 0:
            self.review(now, 'recovery', {'reason': 'missing-qualified-step-time'})
            return None
        iterations = max(1, min(200, int((budget-60)/(sec*1.5))))
        return self.launch(now, 'segment', iterations=iterations, max_seconds=budget)

    def launch(self, now, kind, **extra):
        self.s['job_number'] += 1
        limits = {'baseline': 1800, 'short': 600, 'reload': 600, 'length': 1500, 'sample': 1800, 'segment': 1500}
        job = {'action': 'launch', 'id': f"job-{self.s['job_number']:05d}",
               'kind': kind, 'started': now, 'max_seconds': limits[kind],
               'checkpoint': self.s['latest_checkpoint'], 'simulated': self.simulated, **extra}
        self.s['active_job'] = job
        self.s['status'] = 'running'
        if kind in {'short', 'length', 'segment'}:
            self.s['training_requested'] = not self.simulated
        self.event(now, 'launch', job=job['id'], worker_kind=kind)
        return job

    def finish(self, now, result):
        job = self.s['active_job']
        if not job: raise ValueError('No active job')
        if bool(result.get('simulated')) != self.simulated:
            raise ValueError('Simulation/live result mismatch')
        generation=result.get('generation',{})
        if job['kind']=='baseline' and generation.get('prompt_token_sha256'):
            self.s['control_fingerprint']={'prompt':generation['prompt_token_sha256'],'versions':generation.get('versions')}
        if job['kind']=='sample' and self.s.get('control_fingerprint'):
            actual={'prompt':generation.get('prompt_token_sha256'),'versions':generation.get('versions')}
            if actual!=self.s['control_fingerprint']:
                result={**result,'okay':False,'reason':'Control/input/runtime mismatch'}
        self.s['active_job'] = None
        self.event(now, 'worker-finished', job=job['id'], okay=bool(result.get('okay')))
        if not self.simulated and result.get('completed_steps',0)>0:
            self.s['training_started']=True
            self.s['confirmed_training_steps']+=result['completed_steps']
        if result.get('checkpoint'):
            self.s['latest_checkpoint'] = result['checkpoint']
        if self.s['status'] in TERMINAL: return
        if result.get('paused'):
            if result.get('resource_hold'):self.s['defer_until']=now+300
            self.s['status'] = 'paused'
            return
        if not result.get('okay'):
            self.s['crashes'] += 1
            if self.s['crashes'] >= 2:
                self.s['status'] = 'stopped'
                self.event(now, 'two-worker-failures')
            else:
                self.review(now, 'failure', {'job': job, 'result': result})
            return
        kind = job['kind']
        if kind == 'baseline':
            self.review(now, 'baseline', {'job': job, 'result': result})
        elif kind == 'short':
            self.s['qualification']['short'] = result
            self.s['phase'] = 'reload'; self.s['status'] = 'ready'
        elif kind == 'reload':
            self.s['qualification']['reload'] = result
            self.s['phase'] = 'length'; self.s['status'] = 'ready'
        elif kind == 'length':
            self.s['qualification']['length'] = result
            sec = result.get('seconds_per_step')
            if not sec or not math.isfinite(sec) or sec <= 0:
                self.review(now, 'failure', {'reason': 'invalid-calibration-time'})
            else:
                self.s['seconds_per_step'] = sec
                self.review(now, 'qualification', {'gates': self.s['qualification']})
        elif kind == 'segment':
            self.s['segment_number'] += 1; self.s['status'] = 'ready'
            sec = result.get('seconds_per_step')
            if sec and math.isfinite(sec) and sec > 0:
                self.s['seconds_per_step'] = max(sec, self.s['seconds_per_step'])
        elif kind == 'sample':
            h = str(job['milestone'])
            self.s['milestones'][h] = {'due': self.s['start']+int(h)*3600,
                'sample_attempted': True, 'status': 'awaiting-review', 'result': result,
                'checkpoint': job['checkpoint']}
            self.s['last_sample'] = {'milestone': int(h), 'job': job['id'], 'checkpoint':job['checkpoint'],'completed_at':now,'reviewed':False,'result':result}
            self.review(now, 'milestone', {'milestone': int(h), 'job': job, 'result': result})

    def acknowledge(self, now, record):
        packet = self.s['awaiting_review']
        if not packet or record.get('packet_sha256') != packet['sha256']:
            raise ValueError('Stale or mismatched review')
        decision = record.get('decision')
        if decision not in {'continue', 'retry', 'stop'}: raise ValueError('Invalid decision')
        if decision == 'retry' and (packet['kind'] != 'failure' or self.s['crashes'] >= 2):
            raise ValueError('Retry not allowed')
        if decision == 'continue':
            if packet['kind'] in {'baseline','milestone'}:
                if record.get('raw_export_status') not in {'pass','fail'} or not record.get('evidence'):
                    raise ValueError('Raw export outcome and review evidence required')
                if record.get('accept_checkpoint') and (record['raw_export_status']!='pass' or record.get('glb_validation_errors')!=0 or record.get('assistance')!='none'):
                    raise ValueError('Cannot accept checkpoint without a valid raw export')
            if packet['kind'] == 'failure': raise ValueError('Failed worker cannot pass as success')
            if packet['kind'] == 'baseline' and not record.get('baseline_frozen'):
                raise ValueError('Baseline freeze evidence required')
            if packet['kind'] == 'qualification':
                if not record.get('live_gates_passed') or not all(self.s['qualification'].get(k,{}).get('okay') for k in ['short','reload','length']):
                    raise ValueError('Live qualification gates not passed')
            if packet['kind'] == 'milestone':
                if not isinstance(record.get('regression'),bool):raise ValueError('Explicit regression assessment required')
                if not record.get('export_and_visual_reviewed'):
                    raise ValueError('Export/playback/visual review required')
                bad = record.get('regression') is True
                self.s['regressions'] = self.s['regressions']+1 if bad else 0
                if record.get('accept_checkpoint') and not bad:
                    self.s['best_checkpoint'] = packet['payload']['job']['checkpoint']
                self.s['milestones'][str(packet['payload']['milestone'])]['review'] = record
                self.s['milestones'][str(packet['payload']['milestone'])]['status'] = 'reviewed'
                if self.s['last_sample'] and self.s['last_sample']['job']==packet['payload']['job']['id']:
                    self.s['last_sample']['reviewed']=True
                    self.s['last_sample']['raw_export_status']=record['raw_export_status']
        if decision == 'retry' and packet['payload'].get('job'):
            self.s['pending_retry']=packet['payload']['job']
        self.s['awaiting_review'] = None
        if decision == 'stop' or self.s['regressions'] >= 2:
            self.s['status'] = 'stopped'
        else:
            if packet['kind'] == 'baseline': self.s['phase'] = 'short'
            if packet['kind'] == 'qualification':
                self.s['phase'] = 'main'
                # Calibration adapters are not the first main-training checkpoint.
                self.s['latest_checkpoint'] = None
            self.s['status'] = 'ready'
        self.event(now, 'review', review_kind=packet['kind'], decision=decision)


def process_identity(pid):
    p = subprocess.run(['ps','-p',str(pid),'-o','lstart=,args='],capture_output=True,text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def group_members(pgid):
    out=subprocess.run(['ps','-axo','pid=,pgid=,stat='],capture_output=True,text=True)
    return [int(p[0]) for line in out.stdout.splitlines() if len(p:=line.split())==3 and p[1]==str(pgid) and not p[2].startswith('Z')]


def process_tree(pid):
    out=subprocess.run(['ps','-axo','pid=,ppid=,stat='],capture_output=True,text=True)
    records=[line.split() for line in out.stdout.splitlines() if len(line.split())==3]
    result={pid};changed=True
    while changed:
        changed=False
        for child,parent,status in records:
            if int(parent) in result and int(child) not in result and not status.startswith('Z'):
                result.add(int(child));changed=True
    return sorted(result)


def tracked_alive(owned):
    return [pid for pid,identity in owned.items() if identity and process_identity(pid)==identity and subprocess.run(['ps','-p',str(pid),'-o','stat='],capture_output=True,text=True).stdout.strip()[:1]!='Z']

def terminate_owned(child, identity, grace=60, tracked=None):
    owned=dict(tracked or {})
    if child.poll() is None:
        if process_identity(child.pid)!=identity or os.getpgid(child.pid)!=child.pid:
            raise RuntimeError('Refusing to signal a process whose identity changed')
        owned.update({pid:process_identity(pid) for pid in process_tree(child.pid)})
    elif not tracked and group_members(child.pid):
        raise RuntimeError('Exited wrapper still has unverified descendants')
    alive=tracked_alive(owned)
    if not alive:return
    # Driver/wrapper first, then any tracked detached-session children.
    for pid in sorted(alive,key=lambda p:p!=child.pid):
        if process_identity(pid)==owned[pid]:
            try:os.kill(pid,signal.SIGTERM)
            except ProcessLookupError:pass
    deadline=time.monotonic()+grace
    while tracked_alive(owned) and time.monotonic()<deadline:
        child.poll();time.sleep(min(.05,max(0,deadline-time.monotonic())))
    for pid in tracked_alive(owned):
        if process_identity(pid)!=owned[pid]:raise RuntimeError('PID identity changed during stop')
        try:os.kill(pid,signal.SIGKILL)
        except ProcessLookupError:pass
    child.wait(timeout=10);deadline=time.monotonic()+2
    while tracked_alive(owned) and time.monotonic()<deadline:time.sleep(.02)
    if tracked_alive(owned):raise RuntimeError('Owned process tree still exiting; no further launch')


def recover_after_restart(engine, now, lookup=process_identity):
    state=engine.s;old=state['active_job']
    if not old:return
    pids=state.get('orphan_group',[])+([old['pid']] if old.get('pid') else [])
    if any(lookup(pid) for pid in pids):
        raise RuntimeError('Recorded worker/descendant still alive; explicit inspected handoff required')
    state['active_job']=None;state['crashes']+=1
    engine.review(now,'failure',{'reason':'controller-restart-with-unverified-worker-result','job':old})
    if state['crashes']>=2:state['status']='stopped'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=Path('configs/overnight-11h.json'))
    p.add_argument('--run-id',default='astra-overnight-20261116')
    p.add_argument('--wait-until-start',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--authorization-file',type=Path)
    p.add_argument('--ack-review',type=Path);p.add_argument('--status',action='store_true')
    args=p.parse_args();repo=Path(__file__).resolve().parents[1]
    config=json.loads(args.config.read_text());state=new_state(config,args.run_id)
    if '/' in args.run_id or args.run_id in {'.','..'}:raise SystemExit('Invalid run ID')
    root=repo.parent/'work/sprint-prep/overnight'/args.run_id
    if not(args.run or args.ack_review or args.status):
        print(json.dumps({'mode':'plan-only','training_started':False,'config_sha256':digest(config),'run_id':args.run_id,'start':config['start'],
              'stop':config['hard_stop'],'phases':QUALIFICATION+['qualification-review','bounded-segments','configured-milestone-samples'],
              'reviewer':'Current Codex session must inspect/acknowledge packets; no owner interaction is needed for routine authorized review.',
              'resume':'Adapters only; optimizer is restarted between bounded CLI segments, explicitly recorded.'},indent=2));return
    if args.status:
        print((root/'state.json').read_text() if (root/'state.json').exists() else json.dumps({'status':'not-created','training_started':False}));return
    if args.authorization_file is None:raise SystemExit('Owner start authorization required; no worker launched')
    auth=json.loads(args.authorization_file.read_text())
    if not(auth.get('owner_authorized') is True and auth.get('scope')==config.get('authorization_scope','48-hour-sprint') and auth.get('run_id')==args.run_id and auth.get('config_sha256')==digest(config)):
        raise SystemExit('Authorization does not match this exact run/config; no worker launched')
    if args.run and time.time()>=state['deadline']:raise SystemExit('Run deadline passed; no worker launched')
    if args.run and time.time()<state['start'] and not args.wait_until_start:raise SystemExit('Before planned start: nothing scheduled or launched')
    if args.run and not args.resume:
        root.mkdir(parents=True,exist_ok=False)
    if not root.exists():raise SystemExit('Run does not exist')
    if args.ack_review:
        state=json.loads((root/'state.json').read_text());record=json.loads(args.ack_review.read_text())
        packet=state['awaiting_review']
        if not packet or record.get('packet_sha256')!=packet['sha256']:raise SystemExit('Stale review')
        target=root/'reviews'/(packet['sha256']+'.json');target.parent.mkdir(exist_ok=True)
        with target.open('x') as h:json.dump(record,h)
        print('Review queued for the owning controller');return
    with (root/'controller.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise SystemExit('Another controller owns this run')
        if (root/'state.json').exists():state=json.loads((root/'state.json').read_text())
        engine=Engine(state,config)
        # Do not adopt or stop another running process after controller failure.
        recover_after_restart(engine,time.time())
        from overnight_runtime import run_loop
        run_loop(repo,root,engine,auth)

if __name__=='__main__':main()
