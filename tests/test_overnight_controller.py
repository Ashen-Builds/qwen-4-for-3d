import copy
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import tempfile
import types
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from overnight_controller import Engine,new_state,digest,atomic_json,process_identity,terminate_owned
from overnight_runtime import adapter_valid,inputs_fingerprint
REPO=Path(__file__).resolve().parents[1]
CONFIG=json.loads((REPO/'configs/sprint-48h.json').read_text())


def engine():return Engine(new_state(CONFIG,'dry-test'),CONFIG,simulated=True)


def ack(e,now,**extra):
    e.acknowledge(now,{'packet_sha256':e.s['awaiting_review']['sha256'],'decision':'continue','raw_export_status':'pass','evidence':['fixture-only'],'glb_validation_errors':0,'assistance':'none','regression':False,**extra})


def qualify(e,t):
    for kind in ['baseline','short','reload','length']:
        job=e.tick(t)
        assert job['kind']==kind,(job,kind)
        e.finish(t+1,{'simulated':True,'okay':True,'seconds_per_step':2,'checkpoint':'fixture-only/'+kind})
        t+=2
        if kind=='baseline':ack(e,t,baseline_frozen=True)
    ack(e,t,live_gates_passed=True)
    return t+1


class StateTests(unittest.TestCase):
    def test_plan_has_no_model_import_or_live_job(self):
        p=subprocess.run([sys.executable,'scripts/overnight_controller.py'],cwd=REPO,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);self.assertFalse(json.loads(p.stdout)['training_started'])

    def test_unapproved_run_cannot_launch(self):
        p=subprocess.run([sys.executable,'scripts/overnight_controller.py','--run'],cwd=REPO,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('no worker launched',p.stderr)

    def test_before_start_does_not_schedule(self):
        e=engine();self.assertIsNone(e.tick(e.s['start']-1));self.assertEqual(e.s['status'],'not-started')

    def test_budget_never_exceeds_48h(self):
        c=copy.deepcopy(CONFIG);c['hard_stop']='2026-11-19T23:00:00-05:00'
        with self.assertRaises(ValueError):new_state(c,'x')

    def test_qualification_order_and_explicit_review(self):
        e=engine();t=qualify(e,e.s['start']);self.assertEqual(e.s['phase'],'main');self.assertFalse(e.s['training_started']);self.assertIsNone(e.s['latest_checkpoint']);self.assertEqual(e.tick(t)['kind'],'segment')

    def test_baseline_requires_real_review_record(self):
        e=engine();t=e.s['start'];e.tick(t);e.finish(t+1,{'simulated':True,'okay':True})
        with self.assertRaises(ValueError):ack(e,t+2)
        self.assertIsNone(e.tick(t+3))

    def test_stale_review_rejected(self):
        e=engine();e.review(e.s['start'],'baseline',{})
        with self.assertRaises(ValueError):e.acknowledge(e.s['start'],{'packet_sha256':'wrong','decision':'continue'})

    def test_missing_qualification_gate_rejected(self):
        e=engine();e.review(e.s['start'],'qualification',{})
        with self.assertRaises(ValueError):ack(e,e.s['start'],live_gates_passed=True)

    def test_fake_result_never_enters_live_engine(self):
        e=Engine(new_state(CONFIG,'live-shape-only'),CONFIG);e.tick(e.s['start'])
        with self.assertRaises(ValueError):e.finish(e.s['start']+1,{'simulated':True,'okay':True})

    def test_streaming_hold_and_resume(self):
        e=engine();t=e.s['start'];self.assertIsNone(e.tick(t,{'streaming':True}));self.assertEqual(e.s['status'],'paused');self.assertEqual(e.tick(t+2)['kind'],'baseline')

    def test_global_pause_never_removed(self):
        e=engine();self.assertIsNone(e.tick(e.s['start'],{'global_pause':True}));self.assertEqual(e.s['pause_reason'],'global-gpu-pause')

    def test_manual_pause(self):
        e=engine();self.assertIsNone(e.tick(e.s['start'],{'manual':True}));self.assertEqual(e.s['pause_reason'],'manual-pause')

    def test_nine_am_handoff_stops_active_job(self):
        e=engine();t=e.s['start'];qualify(e,t);e.tick(t+9*3600)
        a=e.tick(t+10*3600);self.assertEqual(a['action'],'stop');self.assertEqual(a['reason'],'owner-computer-time')
        e.finish(t+10*3600,{'simulated':True,'okay':False,'paused':True,'checkpoint':'fixture-partial'});self.assertEqual(e.s['status'],'paused')

    def test_daytime_permission_is_explicit(self):
        e=engine();t=e.s['start']+10*3600;self.assertIsNone(e.tick(t));self.assertEqual(e.tick(t,{'daytime_approved':True})['kind'],'baseline')

    def test_deadline_survives_worker_cleanup(self):
        e=engine();e.tick(e.s['start']);a=e.tick(e.s['deadline']);self.assertEqual(a['reason'],'hard-deadline')
        e.finish(e.s['deadline'],{'simulated':True,'okay':False,'paused':True});self.assertEqual(e.s['status'],'deadline');self.assertIsNone(e.tick(e.s['deadline']+1))

    def test_first_failure_waits_for_diagnosis(self):
        e=engine();t=e.s['start'];e.tick(t);e.finish(t+1,{'simulated':True,'okay':False});self.assertIsNone(e.tick(t+2))
        with self.assertRaises(ValueError):ack(e,t+3)

    def test_two_failures_stop_relaunch(self):
        e=engine();t=e.s['start'];e.tick(t);e.finish(t+1,{'simulated':True,'okay':False})
        e.acknowledge(t+2,{'packet_sha256':e.s['awaiting_review']['sha256'],'decision':'retry'});e.tick(t+3);e.finish(t+4,{'simulated':True,'okay':False});self.assertEqual(e.s['status'],'stopped');self.assertIsNone(e.tick(t+5))

    def test_midstep_pause_keeps_checkpoint(self):
        e=engine();t=qualify(e,e.s['start']);e.tick(t);e.tick(t+1,{'streaming':True});e.finish(t+2,{'simulated':True,'paused':True,'okay':False,'checkpoint':'fixture-saved'});self.assertEqual(e.s['latest_checkpoint'],'fixture-saved');self.assertEqual(e.s['crashes'],0)

    def test_segments_fit_measured_budget(self):
        e=engine();t=qualify(e,e.s['start']);e.s['seconds_per_step']=100;a=e.tick(t);self.assertLessEqual(a['iterations']*150+60,a['max_seconds'])

    def test_checkpoint_immutable_and_best_retained(self):
        e=engine();t=qualify(e,e.s['start']);e.tick(t);e.finish(t+1,{'simulated':True,'okay':True,'checkpoint':'fixture-cp1','seconds_per_step':2})
        a=e.tick(e.s['start']+7*3600);self.assertEqual(a['kind'],'sample');self.assertEqual(a['checkpoint'],'fixture-cp1')
        e.finish(e.s['start']+7*3600+1,{'simulated':True,'okay':True})
        ack(e,e.s['start']+7*3600+2,export_and_visual_reviewed=True,accept_checkpoint=True,regression=False)
        self.assertEqual(e.s['best_checkpoint'],'fixture-cp1');self.assertEqual(e.s['milestones']['8']['status'],'reviewed')

    def test_no_fabricated_daytime_outputs(self):
        e=engine();qualify(e,e.s['start']);e.tick(e.s['start']+16*3600);self.assertEqual(e.s['milestones']['16']['status'],'no-new-output');self.assertTrue(e.s['milestones']['16']['sample_attempted'])

    def test_all_six_milestones_and_hard_stop(self):
        e=engine();t=qualify(e,e.s['start'])
        e.tick(t);e.finish(t+1,{'simulated':True,'okay':True,'checkpoint':'fixture-cp','seconds_per_step':2})
        for h in [8,16,24,32,40,48]:
            a=e.tick(e.s['start']+h*3600-3500,{'daytime_approved':True})
            if a and a['action']=='launch':
                e.finish(e.s['start']+h*3600-3400,{'simulated':True,'okay':True})
                ack(e,e.s['start']+h*3600-3300,export_and_visual_reviewed=True,accept_checkpoint=True)
            e.tick(e.s['start']+h*3600,{'daytime_approved':True})
        self.assertEqual(set(e.s['milestones']),{'8','16','24','32','40','48'});self.assertEqual(e.s['status'],'deadline')

    def test_resume_preserves_review_and_blocks_duplicate(self):
        e=engine();t=e.s['start'];e.tick(t);e.finish(t+1,{'simulated':True,'okay':False})
        restored=Engine(json.loads(json.dumps(e.s)),CONFIG,True);self.assertIsNone(restored.tick(t+2));self.assertEqual(restored.s['awaiting_review']['kind'],'failure')

    def test_changed_config_refuses_resume(self):
        e=engine();c=copy.deepcopy(CONFIG);c['showcase_seed']=9
        with self.assertRaises(ValueError):Engine(e.s,c,True)

    def test_repeated_regression_stops(self):
        e=engine();qualify(e,e.s['start']);e.s['latest_checkpoint']='fixture'
        for h in [8,16]:
            e.tick(e.s['start']+h*3600-3500,{'daytime_approved':True});e.finish(e.s['start']+h*3600-3400,{'simulated':True,'okay':True});ack(e,e.s['start']+h*3600-3300,export_and_visual_reviewed=True,regression=True)
        self.assertEqual(e.s['status'],'stopped')

    def test_atomic_state_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json';s=engine().s;atomic_json(p,s);self.assertEqual(json.loads(p.read_text()),s)


class ProcessTests(unittest.TestCase):
    def spawn(self,ignore=False):
        self.temp=tempfile.TemporaryDirectory();marker=Path(self.temp.name)/'fixture.json';cmd=[sys.executable,str(REPO/'tests/fixtures/fake_sprint_worker.py'),'--marker',str(marker)]
        if ignore:cmd.append('--ignore-term')
        child=subprocess.Popen(cmd,start_new_session=True)
        for _ in range(200):
            if marker.exists():break
            time.sleep(.01)
        self.assertTrue(marker.exists());self.assertFalse(json.loads(marker.read_text())['training_started']);return child

    def test_owned_child_sigterm_and_wait(self):
        c=self.spawn()
        try:terminate_owned(c,process_identity(c.pid),grace=2);self.assertEqual(c.returncode,-signal.SIGTERM)
        finally:
            if c.poll() is None:os.killpg(c.pid,signal.SIGKILL);c.wait()
            self.temp.cleanup()

    def test_pid_identity_mismatch_never_signalled(self):
        c=self.spawn()
        try:
            with self.assertRaises(RuntimeError):terminate_owned(c,'wrong identity',grace=.1)
            self.assertIsNone(c.poll());terminate_owned(c,process_identity(c.pid),grace=2)
        finally:
            if c.poll() is None:os.killpg(c.pid,signal.SIGKILL);c.wait()
            self.temp.cleanup()

    def test_last_resort_only_after_term_grace(self):
        c=self.spawn(True)
        try:t=time.monotonic();terminate_owned(c,process_identity(c.pid),grace=.15);self.assertGreaterEqual(time.monotonic()-t,.15);self.assertEqual(c.returncode,-signal.SIGKILL)
        finally:
            if c.poll() is None:os.killpg(c.pid,signal.SIGKILL);c.wait()
            self.temp.cleanup()


class IntegrationTests(unittest.TestCase):
    def test_full_48h_runtime_with_real_fake_subprocesses(self):
        from unittest.mock import patch
        from overnight_runtime import run_loop
        e=engine();now=[e.s['start']];commands=[];real_sleep=time.sleep
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'reviews').mkdir();(root/'fixture-evidence.json').write_text('{"simulated":true,"real_training_steps":0}')
            def make_command(repo,job,directory):
                cmd=[sys.executable,str(REPO/'tests/fixtures/fake_sprint_worker.py'),'--marker',str(directory/'fixture.json'),'--exit-after','.001'];commands.append((job['kind'],cmd));return cmd
            def fake_collect(job,directory,runroot,code,reason,elapsed):
                self.assertTrue((directory/'fixture.json').exists());self.assertFalse(json.loads((directory/'fixture.json').read_text())['training_started'])
                now[0]+=1200 if job['kind']=='segment' else 60
                r={'simulated':True,'okay':True,'seconds_per_step':2,'real_training_steps':0}
                if job['kind'] in {'short','length','segment'}:r['checkpoint']='fixture-only/'+job['id']
                return r
            def advance(_):
                packet=e.s['awaiting_review']
                if packet:
                    record={'packet_sha256':packet['sha256'],'decision':'continue','baseline_frozen':True,'live_gates_passed':True,'export_and_visual_reviewed':True,'accept_checkpoint':True,'regression':False,'raw_export_status':'fail','evidence':[{'path':'fixture-evidence.json','sha256':__import__('hashlib').sha256((root/'fixture-evidence.json').read_bytes()).hexdigest()}],'glb_validation_errors':0,'assistance':'none'}
                    record['accept_checkpoint']=False
                    (root/'reviews'/(packet['sha256']+'.json')).write_text(json.dumps(record))
                now[0]+=1 if e.s['active_job'] else 600;real_sleep(.005)
            with patch('training_preflight.inspect',return_value={'status':'ready-for-authorized-qualification'}),patch('overnight_runtime.inputs_fingerprint',return_value={'fake':'explicit-test-inputs'}),patch('overnight_runtime.memory_available',return_value=1024**4),patch('overnight_runtime.command',side_effect=make_command),patch('overnight_runtime.collect',side_effect=fake_collect),patch('overnight_runtime.time.time',side_effect=lambda:now[0]),patch('overnight_runtime.time.sleep',side_effect=advance):
                run_loop(REPO,root,e,{'allow_daytime_compute':False})
            self.assertEqual(e.s['status'],'deadline');self.assertFalse(e.s['training_started']);self.assertIsNone(e.s['active_job'])
            self.assertEqual(set(e.s['milestones']),{'8','16','24','32','40','48'})
            self.assertTrue(all('fake_sprint_worker.py' in cmd[1] for _,cmd in commands))
            self.assertTrue({'baseline','short','reload','length','segment','sample'}.issubset({kind for kind,_ in commands}))
            self.assertTrue(any(x['status']=='no-new-output' for x in e.s['milestones'].values()))
            report=os.environ.get('ASTRA_DRY_REPORT_DIR')
            if report:
                from collections import Counter
                directory=Path(report);directory.mkdir(parents=True,exist_ok=True)
                atomic_json(directory/'timeline.json',{'simulated':True,'simulated_wall_hours':48,'final_status':e.s['status'],'real_training_steps':0,'real_model_workers_started':0,'fake_worker_script':'tests/fixtures/fake_sprint_worker.py','fake_worker_counts':dict(Counter(kind for kind,_ in commands)),'milestones':e.s['milestones'],'events':e.s['events']})


    def test_adapter_validator_rejects_corrupt_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'test.safetensors'
            for value in [0.0,float('nan')]:
                h={'layer.lora_b':{'dtype':'F32','shape':[1],'data_offsets':[0,4]}};raw=json.dumps(h).encode();p.write_bytes(struct.pack('<Q',len(raw))+raw+struct.pack('<f',value))
                with self.assertRaises(ValueError):adapter_valid(p)
            p.write_bytes(b'bad')
            with self.assertRaises(struct.error):adapter_valid(p)

    def test_adapter_validator_checks_real_binary_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'test.safetensors';h={'layer.lora_b':{'dtype':'F32','shape':[1],'data_offsets':[0,4]}};raw=json.dumps(h).encode();p.write_bytes(struct.pack('<Q',len(raw))+raw+struct.pack('<f',.1));self.assertEqual(adapter_valid(p)['parameters'],1)

    def test_frozen_source_change_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp)/'repo';(r/'configs').mkdir(parents=True);f=r/'configs/lora-test.yaml';f.write_text('train: false');a=inputs_fingerprint(r);f.write_text('train: true');self.assertNotEqual(a,inputs_fingerprint(r))

class GuardTests(unittest.TestCase):
    def test_memory_guards_without_allocating_model_memory(self):
        from overnight_runtime import resource_stop
        self.assertEqual(resource_stop([{'peak_memory':201}],0,1024**4),'memory-budget')
        self.assertEqual(resource_stop([],181*1024**3,1024**4),'resident-memory-budget')
        self.assertEqual(resource_stop([],0,11*1024**3),'system-memory-pressure')
        self.assertIsNone(resource_stop([],0,100*1024**3))

    def test_failed_raw_export_cannot_become_best_checkpoint(self):
        e=engine();qualify(e,e.s['start']);e.s['latest_checkpoint']='fixture';t=e.s['start']+7*3600;e.tick(t);e.finish(t+1,{'simulated':True,'okay':True})
        with self.assertRaises(ValueError):ack(e,t+2,export_and_visual_reviewed=True,accept_checkpoint=True,raw_export_status='fail')
        self.assertIsNone(e.s['best_checkpoint'])

    def test_sample_runtime_mismatch_is_a_failure(self):
        e=engine();t=e.s['start'];e.tick(t);e.finish(t+1,{'simulated':True,'okay':True,'generation':{'prompt_token_sha256':'fixture-input','versions':{'fixture':1}}});ack(e,t+2,baseline_frozen=True)
        e.s['phase']='main';e.s['latest_checkpoint']='fixture';e.s['seconds_per_step']=1;e.tick(t+7*3600)
        e.finish(t+7*3600+1,{'simulated':True,'okay':True,'generation':{'prompt_token_sha256':'changed','versions':{'fixture':1}}});self.assertEqual(e.s['awaiting_review']['kind'],'failure')

    def test_live_worker_without_flags_refuses_before_model_import(self):
        p=subprocess.run([sys.executable,'scripts/sprint_worker.py','--job','does-not-exist.json'],cwd=REPO,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('no model loaded',p.stderr)

class DescendantTests(unittest.TestCase):
    def test_term_waits_for_descendants_before_next_launch(self):
        from overnight_controller import group_members
        with tempfile.TemporaryDirectory() as temp:
            marker=Path(temp)/'fixture.json';c=subprocess.Popen([sys.executable,str(REPO/'tests/fixtures/fake_sprint_worker.py'),'--marker',str(marker),'--descendant'],start_new_session=True)
            try:
                for _ in range(200):
                    if marker.exists():break
                    time.sleep(.01)
                self.assertTrue(marker.exists());self.assertGreaterEqual(len(group_members(c.pid)),2)
                terminate_owned(c,process_identity(c.pid),grace=.2);self.assertEqual(group_members(c.pid),[])
            finally:
                if c.poll() is None:os.killpg(c.pid,signal.SIGKILL);c.wait()

class RecoveryTests(unittest.TestCase):
    def test_live_orphan_is_never_taken_over(self):
        from overnight_controller import recover_after_restart
        e=engine();e.tick(e.s['start']);e.s['active_job']['pid']=123
        with self.assertRaises(RuntimeError):recover_after_restart(e,e.s['start']+1,lambda pid:'still-alive')
        self.assertIsNotNone(e.s['active_job'])

    def test_dead_worker_requires_review_not_duplicate_launch(self):
        from overnight_controller import recover_after_restart
        e=engine();e.tick(e.s['start']);e.s['active_job']['pid']=123;recover_after_restart(e,e.s['start']+1,lambda pid:None)
        self.assertIsNone(e.tick(e.s['start']+2));self.assertEqual(e.s['awaiting_review']['kind'],'failure')

    def test_alive_descendant_blocks_even_after_wrapper_died(self):
        from overnight_controller import recover_after_restart
        e=engine();e.tick(e.s['start']);e.s['active_job']['pid']=123;e.s['orphan_group']=[456]
        with self.assertRaises(RuntimeError):recover_after_restart(e,e.s['start']+1,lambda pid:'alive' if pid==456 else None)

    def test_second_recovery_strike_stops(self):
        from overnight_controller import recover_after_restart
        e=engine();e.tick(e.s['start']);e.s['crashes']=1;recover_after_restart(e,e.s['start']+1,lambda pid:None);self.assertEqual(e.s['status'],'stopped')

    def test_os_lock_prevents_second_owner(self):
        import fcntl
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/'lock'
            with file.open('a') as h:
                fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
                code="import fcntl,sys;h=open(sys.argv[1],'a');\ntry:fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)\nexcept BlockingIOError:sys.exit(42)"
                result=subprocess.run([sys.executable,'-c',code,str(file)]);self.assertEqual(result.returncode,42)


class HandoffTests(unittest.TestCase):
    def test_early_drain_leaves_shutdown_grace_before_nine(self):
        e=engine();qualify(e,e.s['start']);e.tick(e.s['start']+9*3600)
        action=e.tick(e.s['start']+9*3600+58*60)
        self.assertEqual(action['reason'],'owner-computer-time')

    def test_daytime_override_does_not_override_streaming(self):
        e=engine();self.assertIsNone(e.tick(e.s['start']+12*3600,{'daytime_approved':True,'streaming':True}));self.assertEqual(e.s['pause_reason'],'streaming')

class EvidenceTests(unittest.TestCase):
    def test_missing_or_wrong_evidence_refuses_acceptance(self):
        from overnight_runtime import verify_review_evidence
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);packet={'kind':'milestone'}
            with self.assertRaises(ValueError):verify_review_evidence(root,packet,{})
            p=root/'review.json';p.write_text('{}')
            with self.assertRaises(ValueError):verify_review_evidence(root,packet,{'evidence':[{'path':'review.json','sha256':'wrong'}]})

    def test_valid_evidence_hash_for_raw_failure(self):
        from overnight_runtime import verify_review_evidence
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'review.json';p.write_text('{"raw_failure":true}');r={'raw_export_status':'fail','evidence':[{'path':'review.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]};verify_review_evidence(root,{'kind':'baseline'},r)

    def test_raw_success_requires_real_glb_and_validator(self):
        from overnight_runtime import verify_review_evidence
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'review.json';p.write_text('{}');r={'raw_export_status':'pass','evidence':[{'path':'review.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]}
            with self.assertRaises(ValueError):verify_review_evidence(root,{'kind':'milestone'},r)

    def test_evidence_cannot_escape_run_directory(self):
        from overnight_runtime import verify_review_evidence
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'run';root.mkdir();p=Path(temp)/'outside';p.write_text('x')
            with self.assertRaises(ValueError):verify_review_evidence(root,{'kind':'baseline'},{'evidence':[{'path':'../outside','sha256':'x'}]})

class EnvironmentTests(unittest.TestCase):
    def test_local_worker_has_no_ambient_api_keys_or_telemetry(self):
        from overnight_runtime import worker_environment
        original={'PATH':'fixture-path','HF_TOKEN':'unit-test-placeholder','OPENAI_API_KEY':'unit-test-placeholder'}
        env=worker_environment(original,True)
        self.assertNotIn('HF_TOKEN',env);self.assertNotIn('OPENAI_API_KEY',env);self.assertEqual(env['HF_HUB_OFFLINE'],'1');self.assertEqual(env['ASTRA_LIVE_WORKER'],'0');self.assertIn('HF_TOKEN',original)

class AvailabilityTests(unittest.TestCase):
    def test_busy_gpu_gate_is_a_cooldown_not_a_model_crash(self):
        e=engine();t=e.s['start'];e.tick(t);e.finish(t+1,{'simulated':True,'okay':False,'paused':True,'resource_hold':True})
        self.assertIsNone(e.tick(t+2));self.assertEqual(e.s['status'],'waiting_resource');self.assertEqual(e.s['crashes'],0);self.assertFalse(e.s['training_started']);self.assertEqual(e.tick(t+302)['kind'],'baseline')

class AllocationTests(unittest.TestCase):
    def test_model_sized_adapter_rejected_without_reading_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/'oversize.safetensors'
            with file.open('wb') as h:h.truncate(65*1024**2)
            with self.assertRaises(ValueError):adapter_valid(file)


class PacketIdentityTests(unittest.TestCase):
    def test_unchanged_report_does_not_mislabel_old_image_as_new_adapter(self):
        e=engine();qualify(e,e.s['start']);e.s['latest_checkpoint']='fixture-cp1'
        t=e.s['start']+7*3600;e.tick(t);e.finish(t+1,{'simulated':True,'okay':True});ack(e,t+2,export_and_visual_reviewed=True)
        e.s['latest_checkpoint']='fixture-cp2';e.tick(e.s['start']+16*3600)
        packet=e.s['milestones']['16'];self.assertEqual(packet['checkpoint'],'fixture-cp1');self.assertEqual(packet['latest_training_checkpoint'],'fixture-cp2');self.assertTrue(packet['sample']['reviewed'])

if __name__=='__main__':unittest.main()

class ElevenHourTests(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads((REPO/'configs/overnight-11h.json').read_text());self.e=Engine(new_state(self.cfg,'overnight-fixture'),self.cfg,True);self.t=self.e.s['start']

    def test_exact_window(self):
        self.assertEqual(self.e.s['deadline']-self.t,11*3600);self.assertEqual(self.e.tick(self.t)['kind'],'baseline')

    def test_reports_only_five_and_eight(self):
        from overnight_controller import milestone_hours
        self.assertEqual(milestone_hours(self.cfg),[8,11]);self.e.tick(self.t+11*3600);self.assertEqual(set(self.e.s['milestones']),{'8','11'})

    def test_no_model_before_nine(self):
        self.assertIsNone(self.e.tick(self.t-1));self.assertIsNone(self.e.s['active_job'])

    def test_generation_lead_times_and_final_training_cutoff(self):
        qualify(self.e,self.t);self.e.s['latest_checkpoint']='fixture'
        a=self.e.tick(self.t+7*3600);self.assertEqual(a['milestone'],8);self.e.finish(self.t+7*3600+1,{'simulated':True,'okay':True});ack(self.e,self.t+7*3600+2,export_and_visual_reviewed=True)
        self.assertIsNone(self.e.tick(self.t+9.75*3600))
        a=self.e.tick(self.t+10*3600);self.assertEqual(a['milestone'],11)

    def test_drain_before_eight_and_no_extension(self):
        self.e.tick(self.t);self.assertEqual(self.e.tick(self.t+10*3600+58*60)['reason'],'owner-computer-time');self.assertEqual(self.e.tick(self.t+11*3600)['reason'],'hard-deadline')

    def test_out_of_window_milestone_rejected(self):
        c=copy.deepcopy(self.cfg);c['milestones'].append({'elapsed_hours':24})
        with self.assertRaises(ValueError):new_state(c,'bad')

class DetachedGPUWrapperTests(unittest.TestCase):
    def test_separate_session_child_is_stopped_with_owned_wrapper(self):
        from overnight_controller import process_tree,tracked_alive
        with tempfile.TemporaryDirectory() as temp:
            marker=Path(temp)/'fixture.json';c=subprocess.Popen([sys.executable,str(REPO/'tests/fixtures/fake_sprint_worker.py'),'--marker',str(marker),'--detached-child'],start_new_session=True)
            try:
                for _ in range(200):
                    if marker.exists():break
                    time.sleep(.01)
                tree=process_tree(c.pid);self.assertGreaterEqual(len(tree),2);tracked={pid:process_identity(pid) for pid in tree}
                terminate_owned(c,process_identity(c.pid),grace=.2,tracked=tracked);self.assertEqual(tracked_alive(tracked),[])
            finally:
                if c.poll() is None:os.killpg(c.pid,signal.SIGKILL);c.wait()

    def test_memory_counts_detached_descendants(self):
        from unittest.mock import patch
        from overnight_runtime import owned_rss
        with patch('overnight_runtime.process_tree',return_value=[11,12]),patch('overnight_runtime.subprocess.run',return_value=types.SimpleNamespace(stdout='11 100\n12 200\n13 900\n')):
            self.assertEqual(owned_rss(11),300*1024)

class LiveReviewRegressionTests(unittest.TestCase):
    def test_executable_normalization_does_not_change_process_identity(self):
        from unittest.mock import patch
        def fake_ps(command,**_):
            self.assertEqual(command[-1],'lstart=')
            return types.SimpleNamespace(returncode=0,stdout='Mon Nov 16 20:42:40 2026\n')
        with patch('overnight_controller.subprocess.run',side_effect=fake_ps):
            self.assertEqual(process_identity(111),'Mon Nov 16 20:42:40 2026')

    def test_dead_wrapper_with_recorded_detached_worker_blocks_recovery(self):
        from overnight_controller import recover_after_restart
        e=engine();e.tick(e.s['start']);e.s['active_job']['pid']=123;e.s['active_job']['process_tree']={'456':'recorded-start'}
        with self.assertRaises(RuntimeError):recover_after_restart(e,e.s['start']+1,lambda pid:'live-start' if pid==456 else None)

    def test_reserve_stops_all_workers_before_hard_deadline(self):
        cfg=copy.deepcopy(CONFIG);cfg['shutdown_reserve_seconds']=120;e=Engine(new_state(cfg,'reserve'),cfg,True);e.tick(e.s['start'])
        a=e.tick(e.s['deadline']-120,{'daytime_approved':True});self.assertEqual(a['reason'],'deadline-drain')
        e.finish(e.s['deadline']-119,{'simulated':True,'okay':False,'paused':True});self.assertIsNone(e.tick(e.s['deadline']-60,{'daytime_approved':True}));self.assertIsNone(e.s['active_job'])

    def test_worker_budget_is_clamped_to_shutdown_reserve(self):
        cfg=copy.deepcopy(CONFIG);cfg['shutdown_reserve_seconds']=120;e=Engine(new_state(cfg,'clamp'),cfg,True);a=e.tick(e.s['deadline']-180,{'daytime_approved':True});self.assertEqual(a['max_seconds'],60)

class DirectCodeModeTests(unittest.TestCase):
    def test_targeted_phase_caps_segment_at_twelve_updates(self):
        cfg=copy.deepcopy(CONFIG);cfg['max_segment_iterations']=12
        state=new_state(cfg,'targeted');state.update(phase='main',seconds_per_step=1.0)
        job=Engine(state,cfg,True).tick(state['start']+1)
        self.assertEqual(job['kind'],'segment');self.assertEqual(job['iterations'],12)

    def test_invalid_segment_caps_are_rejected(self):
        for cap in [0,-1,201,1.5,True]:
            cfg=copy.deepcopy(CONFIG);cfg['max_segment_iterations']=cap
            with self.subTest(cap=cap),self.assertRaises(ValueError):new_state(cfg,'invalid-cap')

    def test_targeted_phase_cannot_repeat_without_reviewed_rebaseline(self):
        cfg=copy.deepcopy(CONFIG);cfg.update(max_segment_iterations=12,stop_after_segment_count=5)
        state=new_state(cfg,'targeted');state.update(phase='main',seconds_per_step=1.0,segment_number=4)
        e=Engine(state,cfg,True);job=e.tick(state['start']+1)
        self.assertEqual(job['iterations'],12)
        e.finish(state['start']+20,{'simulated':True,'okay':True,'completed_steps':12,'seconds_per_step':1})
        self.assertIsNone(e.tick(state['start']+21));self.assertEqual(state['status'],'phase_complete')
        self.assertIsNone(e.tick(state['start']+100));self.assertIsNone(state['active_job'])

    def test_invalid_phase_boundaries_are_rejected(self):
        for boundary in [0,-1,1.5,True]:
            cfg=copy.deepcopy(CONFIG);cfg['stop_after_segment_count']=boundary
            with self.subTest(boundary=boundary),self.assertRaises(ValueError):new_state(cfg,'invalid-phase')

    def test_direct_control_and_candidate_share_no_thinking_flag(self):
        from unittest.mock import patch
        from overnight_runtime import command
        c=copy.deepcopy(CONFIG);c['evaluation_thinking']=False;e=Engine(new_state(c,'direct'),c,True)
        baseline=e.launch(e.s['start'],'baseline');self.assertFalse(baseline['thinking'])
        with tempfile.TemporaryDirectory() as temp,patch('overnight_runtime.verify_checkpoint'):
            control=command(REPO,baseline,Path(temp)/'jobs/job-control')
            candidate=command(REPO,{**baseline,'kind':'sample','checkpoint':'fixture-only'},Path(temp)/'jobs/job-candidate')
            self.assertIn('--no-thinking',control);self.assertIn('--no-thinking',candidate)
            self.assertEqual(control[control.index('--prompt')+1],candidate[candidate.index('--prompt')+1])
            self.assertEqual(control[control.index('--seed')+1],candidate[candidate.index('--seed')+1])

    def test_direct_variant_keeps_original_experiment_deadline(self):
        new=json.loads((REPO/'configs/overnight-direct-code.json').read_text());original=json.loads((REPO/'configs/overnight-manual.json').read_text());self.assertEqual(new['hard_stop'],original['hard_stop']);self.assertEqual(new['start'],original['start'])
