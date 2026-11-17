"""Run simulated controller tests and CPU-only process fixtures. Never import MLX."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    repo=Path(__file__).resolve().parents[1];os.environ['ASTRA_DRY_REPORT_DIR']=str(args.out.resolve())
    suite=unittest.defaultTestLoader.discover(str(repo/'tests'),pattern='test_overnight_controller.py')
    with (args.out/'tests.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    files=['scripts/overnight_controller.py','scripts/overnight_runtime.py','scripts/sprint_worker.py','tests/test_overnight_controller.py','tests/fixtures/fake_sprint_worker.py']
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'kind':'controller-dry-test; simulated time and fake CPU workers only','passed':result.wasSuccessful(),'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'real_model_workers_started':0,'real_training_steps':0,'mlx_imported':'mlx.core' in sys.modules,'source_sha256':{f:hashlib.sha256((repo/f).read_bytes()).hexdigest() for f in files},'live_qualification_completed':False,'remaining':'Actual training, memory/throughput, adapter effect/reload and GLB visual review require the later owner start instruction.'}
    (args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if report['mlx_imported']:raise SystemExit('Unexpected MLX import during dry testing')
    raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__=='__main__':main()
