"""Live process supervision and artifact checks. Imported only after explicit authorization."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import struct
import subprocess
import sys
import time
from overnight_controller import atomic_json, digest, process_identity, terminate_owned, group_members, process_tree, tracked_alive, TERMINAL


def adapter_valid(file):
    """Read small adapter tensors with stdlib; do not load a model or execute pickle."""
    if Path(file).stat().st_size>64*1024**2:raise ValueError('Adapter unexpectedly large; refusing model-sized allocation')
    with Path(file).open('rb') as h:
        size=struct.unpack('<Q',h.read(8))[0]
        if size>8*1024*1024:raise ValueError('Implausible adapter header')
        header=json.loads(h.read(size));data=h.read()
    nonzero=False;count=0
    for name,item in header.items():
        if name=='__metadata__':continue
        if 'lora_a' not in name and 'lora_b' not in name:raise ValueError('Unexpected trainable tensor')
        a,b=item['data_offsets'];payload=data[a:b];dtype=item['dtype']
        if not (0<=a<=b<=len(data)):raise ValueError('Bad tensor bounds')
        if dtype in {'F32','F16'}:
            fmt='<f' if dtype=='F32' else '<e';values=(x[0] for x in struct.iter_unpack(fmt,payload))
        elif dtype=='BF16':values=(struct.unpack('<f',struct.pack('<I',x[0]<<16))[0] for x in struct.iter_unpack('<H',payload))
        else:raise ValueError('Unsupported adapter dtype')
        n=0
        for value in values:
            if not math.isfinite(value):raise ValueError('Nonfinite adapter')
            if name.endswith('lora_b') and value!=0:nonzero=True
            n+=1
        if n!=math.prod(item['shape']):raise ValueError('Tensor shape mismatch')
        count+=n
    if not nonzero:raise ValueError('No learned nonzero LoRA B values')
    return {'sha256':hashlib.sha256(Path(file).read_bytes()).hexdigest(),'parameters':count}


def snapshot(jobdir,runroot,jobid):
    directory=jobdir/'adapter';candidates=[]
    if directory.exists():
        candidates=sorted(directory.glob('*_adapters.safetensors'),reverse=True)
        if (directory/'adapters.safetensors').exists():candidates.insert(0,directory/'adapters.safetensors')
    for file in candidates:
        try:check=adapter_valid(file)
        except (ValueError,KeyError,struct.error,json.JSONDecodeError):continue
        config=directory/'adapter_config.json'
        if not config.exists():continue
        out=runroot/'checkpoints'/jobid;out.mkdir(parents=True,exist_ok=False)
        shutil.copy2(file,out/'adapters.safetensors');shutil.copy2(config,out/'adapter_config.json')
        atomic_json(out/'receipt.json',{**check,'source_job':jobid,'source_file':file.name,
            'resume_semantics':'Adapter weights only; optimizer and sampler are restarted between bounded segments.'})
        return str(out)
    return None


def read_metrics(path):
    result=[]
    if path.exists():
        for line in path.read_text().splitlines():
            try:result.append(json.loads(line))
            except json.JSONDecodeError:continue
    return result


def collect(job,jobdir,runroot,code,reason,elapsed):
    from overnight_controller import atomic_json
    result={'job_id':job['id'],'simulated':False,'exit_code':code,'stop_reason':reason,'elapsed_seconds':elapsed,'okay':False}
    if job['kind'] in {'short','length','segment'}:
        metrics=read_metrics(jobdir/'metrics.jsonl');training=[x for x in metrics if x['kind']=='train']
        finite=bool(training) and all(math.isfinite(x['train_loss']) and math.isfinite(x['iterations_per_second']) and x['iterations_per_second']>0 for x in training)
        checkpoint=snapshot(jobdir,runroot,job['id']) if finite else None
        expected=job.get('iterations',10 if job['kind']=='short' else 3)
        completed=max((x['iteration'] for x in training),default=0)
        okay=finite and checkpoint is not None and (code==0 and completed>=expected or job['kind']=='segment' and reason=='job-budget' and completed>0)
        result.update(okay=okay,checkpoint=checkpoint,completed_steps=completed,finite_losses=finite,
            seconds_per_step=max((1/x['iterations_per_second'] for x in training),default=None),
            peak_memory_gb=max((x['peak_memory'] for x in training),default=0))
    elif job['kind']=='reload':
        if (jobdir/'reload.json').exists():result.update(json.loads((jobdir/'reload.json').read_text()))
        result['okay']=code==0 and result.get('reload_verified') is True
    else:
        metrics=jobdir/'generation/metrics.json'
        result['okay']=code==0 and metrics.exists()
        if metrics.exists():result['generation']=json.loads(metrics.read_text())
        # Raw export/appearance are assessed by Codex, never inferred from HTML completion.
        result['raw_export_and_visual_review_required']=True
    if code==75:
        result['paused']=True;result['resource_hold']=True
    if reason in {'streaming','manual-pause','owner-computer-time','global-gpu-pause','deadline-drain'}:result['paused']=True
    atomic_json(jobdir/'result.json',result);return result


def verify_review_evidence(root,packet,record):
    if packet['kind'] not in {'baseline','milestone'}:return
    evidence=record.get('evidence',[])
    if not evidence:raise ValueError('Missing review evidence')
    for item in evidence:
        if not isinstance(item,dict) or not isinstance(item.get('path'),str):raise ValueError('Evidence needs path and SHA256')
        file=(root/item['path']).resolve()
        if not file.is_relative_to(root.resolve()) or not file.is_file():raise ValueError('Evidence outside this run or missing')
        if hashlib.sha256(file.read_bytes()).hexdigest()!=item.get('sha256'):raise ValueError('Evidence checksum mismatch')
    if record.get('raw_export_status')=='pass':
        glb=record.get('glb_file');validation=record.get('validation_file')
        names={x['path'] for x in evidence}
        if glb not in names or validation not in names:raise ValueError('Raw GLB and validation receipt required')
        data=(root/glb).read_bytes()
        if len(data)<20 or data[:4]!=b'glTF':raise ValueError('Missing actual GLB bytes')
        report=json.loads((root/validation).read_text())
        if report.get('summary',{}).get('errors')!=0:raise ValueError('GLB validator did not pass')


def verify_checkpoint(path,runroot):
    directory=Path(path).resolve()
    if not directory.is_relative_to((runroot/'checkpoints').resolve()):raise ValueError('Checkpoint outside this run')
    receipt=json.loads((directory/'receipt.json').read_text());actual=adapter_valid(directory/'adapters.safetensors')
    if actual['sha256']!=receipt['sha256']:raise ValueError('Frozen checkpoint bytes changed')


def command(repo,job,jobdir):
    if job.get('checkpoint'):verify_checkpoint(job['checkpoint'],jobdir.parent.parent)
    python=repo.parent/'work/qwen-eval-env/bin/python'
    if job['kind'] in {'baseline','sample'}:
        args=[str(python),str(repo/'scripts/generate_asset.py'),'--model',str(repo.parent/'work/models-derived/ccore-bf16'),
              '--out',str(jobdir/'generation'),'--prompt',str(repo/'eval/prompts/babylon-marketplace-v3.txt'),
              '--card',str(repo.parent/'work/models/ccore--Qwen3.5-4B-GLB-3D-Coder/8f32a199f8b22fe3157b9c5c8b42b052a0750dd3/README.md'),
              '--max-tokens','49152','--seed','42']
        if job['kind']=='sample':args+=['--adapter',job['checkpoint']]
        if not job.get('thinking',True):args+=['--no-thinking']
    else:args=[str(python),str(repo/'scripts/sprint_worker.py'),'--job',str(jobdir/'job.json'),'--execute-authorized']
    return ['python3',str(Path.home()/'.cache/gpu-slot/bin/gpu_slot.py'),'capture','--label','astra-'+job['id'],
            '--json',str(jobdir/'gpu.json'),'--timeout','180','--',*args]


def inputs_fingerprint(repo):
    paths=list((repo/'configs').glob('lora*.yaml'))+list((repo/'scripts').glob('*.py'))+list((repo/'scripts').glob('*.js'))
    paths+=list((repo/'viewer').glob('*'))+[repo/'eval/sprint-probes-v1.json',repo/'eval/prompts/babylon-marketplace-v3.txt',repo.parent/'work/sprint-prep/training-ready/DATA_MANIFEST.json']
    result={str(p.relative_to(repo.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    model=repo.parent/'work/models-derived/ccore-bf16'
    import yaml
    cfg=repo/'configs/lora-qualification.yaml'
    source=yaml.safe_load(cfg.read_text()) if cfg.exists() else {}
    if source.get('adapter_setup_audit'):
        audit=(repo/source['adapter_setup_audit']).resolve()
        result['adapter_setup_audit']=hashlib.sha256(audit.read_bytes()).hexdigest()
    data=(repo/source['data']).resolve().parent if source.get('data') else repo.parent/'work/sprint-prep/training-ready'
    manifest=data/'DATA_MANIFEST.json'
    if manifest.exists():
        for item in json.loads(manifest.read_text())['files']:
            target=(data/item['path']).resolve()
            if not target.is_relative_to(data.resolve()):raise ValueError('Data path outside frozen kit')
            result['data/'+item['path']]=hashlib.sha256(target.read_bytes()).hexdigest()
    result['model_weight_stats']=[{'file':p.name,'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in sorted(model.glob('*.safetensors'))]
    for name in ['config.json','tokenizer.json','tokenizer_config.json','chat_template.jinja']:
        p=model/name
        if p.exists():result['model/'+name]=hashlib.sha256(p.read_bytes()).hexdigest()
    import importlib.metadata
    versions={}
    for name in ['mlx','mlx-metal','mlx-lm','transformers','huggingface-hub','numpy','safetensors','PyYAML']:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    result['runtime_versions']=versions
    return result

def memory_available():
    import re
    out=subprocess.run(['vm_stat'],capture_output=True,text=True,timeout=3)
    if out.returncode:return None
    size=re.search(r'page size of (\d+) bytes',out.stdout)
    if not size:return None
    pages=0
    for name in ['Pages free','Pages inactive','Pages speculative']:
        match=re.search(re.escape(name)+r':\s+(\d+)',out.stdout)
        if match:pages+=int(match.group(1))
    return pages*int(size.group(1))


def owned_rss(pid):
    pids=set(process_tree(pid))
    out=subprocess.run(['ps','-axo','pid=,rss='],capture_output=True,text=True,timeout=3)
    return sum(int(fields[1])*1024 for line in out.stdout.splitlines() if len(fields:=line.split())==2 and int(fields[0]) in pids)


def resource_stop(metrics,rss,available):
    if any(x.get('peak_memory',0)>200 for x in metrics):return 'memory-budget'
    if rss>180*1024**3:return 'resident-memory-budget'
    if available is not None and available<12*1024**3:return 'system-memory-pressure'
    return None

def worker_environment(source,simulated):
    env=dict(source)
    for name in ['HF_TOKEN','HUGGING_FACE_HUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','GEMINI_API_KEY','GOOGLE_API_KEY','DEVIN_API_KEY','GH_TOKEN','GITHUB_TOKEN','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','GOOGLE_APPLICATION_CREDENTIALS']:
        env.pop(name,None)
    env.update(ASTRA_LIVE_WORKER='0' if simulated else '1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',WANDB_MODE='disabled',SWANLAB_MODE='disabled')
    return env

def run_loop(repo,root,engine,auth):
    # Validate frozen data/runtime without importing a model.
    from training_preflight import inspect
    if inspect(repo)['status']!='ready-for-authorized-qualification':raise RuntimeError('Preflight failed')
    frozen=inputs_fingerprint(repo)
    if (root/'inputs.json').exists():
        if json.loads((root/'inputs.json').read_text())!=frozen:raise RuntimeError('Frozen inputs changed; no worker launched')
    else:atomic_json(root/'inputs.json',frozen)
    state=engine.s;child=None;identity=None;log=None;stop_requested=False;awake=None
    if not engine.simulated and Path('/usr/bin/caffeinate').exists():
        awake=subprocess.Popen(['/usr/bin/caffeinate','-i','-s','-w',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def request_stop(*_):
        nonlocal stop_requested
        stop_requested=True
    old_signals={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
    for sig in old_signals:signal.signal(sig,request_stop)
    (root/'reviews').mkdir(exist_ok=True);(root/'jobs').mkdir(exist_ok=True)
    try:
        while state['status'] not in TERMINAL:
            now=time.time();flags={'streaming':(Path.home()/'.cache/gpu-slot/STREAMING').exists(),
                'global_pause':(Path.home()/'.cache/gpu-slot/PAUSED').exists(),
                'manual':(root/'PAUSE').exists(),'stop':stop_requested or (root/'STOP').exists(),
                'daytime_approved':bool(auth.get('allow_daytime_compute',False) or (root/'DAYTIME_APPROVED').exists())}
            packet=state['awaiting_review']
            if packet:
                path=root/'reviews'/(packet['sha256']+'.json')
                if path.exists():
                    if path.stat().st_size>1024*1024:raise ValueError('Oversized review')
                    try:
                        record=json.loads(path.read_text());verify_review_evidence(root,packet,record)
                        engine.acknowledge(now,record)
                    except ValueError as e:
                        engine.event(now,'rejected-review',reason=str(e));path.rename(path.with_suffix('.rejected'))
            action=engine.tick(now,flags)
            if child:
                job=state['active_job']
                tracked={int(pid):value for pid,value in job.get('process_tree',{}).items()}
                if child.poll() is None:tracked.update({pid:process_identity(pid) for pid in process_tree(child.pid)})
                job['process_tree']=tracked
                reason=action.get('reason') if action and action['action']=='stop' else None
                if not reason and now-job['started']>=job['max_seconds']:reason='job-budget'
                final_training_end=state['deadline']-engine.config.get('final_training_stop_seconds_before_deadline',0)
                if not reason and job['kind']=='segment' and now>=final_training_end:reason='job-budget'
                if not engine.simulated and (Path(job['directory'])/'train-start.json').exists():state['training_started']=True
                metrics=read_metrics(Path(job['directory'])/'metrics.jsonl')
                if not reason:
                    reason=resource_stop(metrics,owned_rss(child.pid),memory_available())
                if reason:terminate_owned(child,identity,tracked=tracked)
                if child.poll() is not None:
                    if tracked_alive(tracked):raise RuntimeError('Worker wrapper exited with live descendants')
                    log.close();result=collect(job,Path(job['directory']),root,child.returncode,reason,now-job['started'])
                    engine.finish(now,result);child=None;identity=None;log=None
            elif action and action['action']=='launch':
                if inputs_fingerprint(repo)!=frozen:raise RuntimeError('Frozen inputs changed before launch')
                job=state['active_job'];job['live_authorized']=not engine.simulated;job['segment_index']=state['segment_number']
                jobdir=root/'jobs'/job['id'];jobdir.mkdir(exist_ok=False);job['directory']=str(jobdir)
                atomic_json(jobdir/'job.json',job);log=(jobdir/'runtime.log').open('w')
                env=worker_environment(os.environ,engine.simulated)
                child=subprocess.Popen(command(repo,job,jobdir),cwd=repo,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
                identity=process_identity(child.pid);job['pid']=child.pid;job['process_identity']=identity
            packet=state['awaiting_review']
            if packet:atomic_json(root/'review-packet.json',packet)
            atomic_json(root/'state.json',state)
            time.sleep(1)
    except Exception as error:
        job=state['active_job']
        state['crashes']+=1
        engine.review(time.time(),'failure',{'reason':'controller-error: '+str(error),'job':job})
        if state['crashes']>=2:state['status']='stopped'
        atomic_json(root/'review-packet.json',state['awaiting_review'])
        raise
    finally:
        cleanup_error=None
        if child:
            try:terminate_owned(child,identity,tracked={int(k):v for k,v in (state.get('active_job') or {}).get('process_tree',{}).items()})
            except Exception as error:
                cleanup_error=error;state['status']='stopped';state['orphan_group']=tracked_alive({int(k):v for k,v in (state.get('active_job') or {}).get('process_tree',{}).items()})
        if log:log.close()
        if cleanup_error is None:state['active_job']=None
        atomic_json(root/'state.json',state)
        for sig,handler in old_signals.items():signal.signal(sig,handler)
        if awake and awake.poll() is None:
            awake.terminate()
            try:awake.wait(timeout=60)
            except subprocess.TimeoutExpired:awake.kill();awake.wait()
        if cleanup_error:raise RuntimeError('Cleanup blocked; no further launch: '+str(cleanup_error))
