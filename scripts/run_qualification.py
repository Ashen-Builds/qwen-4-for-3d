"""Print the qualification plan by default; training requires explicit start authorization."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from training_preflight import inspect


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--start-training',action='store_true');p.add_argument('--authorization-file',type=Path);p.add_argument('--run-id',default='qualification-01');args=p.parse_args()
    repo=Path(__file__).resolve().parents[1];check=inspect(repo)
    if check['status']!='ready-for-authorized-qualification':raise SystemExit('Preparation checks failed')
    if '/' in args.run_id or args.run_id in {'.','..'}:raise SystemExit('Invalid run ID')
    out=repo.parent/'work/sprint-prep'/args.run_id
    command=['python3',str(Path.home()/'.cache/gpu-slot/bin/gpu_slot.py'),'capture','--label','astra-authorized-qualification','--json',str(out/'gpu.json'),'--timeout','180','--',str(repo.parent/'work/qwen-eval-env/bin/python'),'-m','mlx_lm','lora','--config','configs/lora-qualification.yaml','--train','--adapter-path',str(out/'adapter')]
    if not args.start_training:
        print(json.dumps({'training_started':False,'mode':'plan-only','steps':10,'max_wall_seconds':600,'command':command,'live_gate':check['remaining_live_gate']},indent=2));return
    if args.authorization_file is None:raise SystemExit('Refusing: explicit owner authorization record required; no process launched')
    auth=json.loads(args.authorization_file.read_text())
    if not(auth.get('owner_authorized') is True and auth.get('scope')=='qualification' and auth.get('run_id')==args.run_id):raise SystemExit('Refusing: mismatched authorization; no process launched')
    if (Path.home()/'.cache/gpu-slot/STREAMING').exists():raise SystemExit('Refusing: stream guard active')
    if out.exists():raise SystemExit('Refusing to overwrite an existing run')
    out.mkdir();started=time.monotonic()
    # This branch is never run during preparation. The marker grants no authority by itself.
    with (out/'runtime.log').open('w') as log:
        child=subprocess.Popen(command,cwd=repo,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        stop_reason=None
        while child.poll() is None:
            if (Path.home()/'.cache/gpu-slot/STREAMING').exists():stop_reason='streaming-guard'
            elif time.monotonic()-started>=600:stop_reason='qualification-time-budget'
            if stop_reason:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=60)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                break
            time.sleep(1)
        code=124 if stop_reason else child.returncode
    (out/'exit.json').write_text(json.dumps({'exit_code':code,'elapsed_seconds':time.monotonic()-started,'training_started':True,'main_48h_run_started':False})+'\n')
    raise SystemExit(code)

if __name__=='__main__':main()
