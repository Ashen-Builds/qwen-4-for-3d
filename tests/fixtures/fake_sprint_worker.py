"""CPU-only signal fixture. No model packages, optimizer, GPU or asset generation."""
import argparse
import json
from pathlib import Path
import signal
import time
p=argparse.ArgumentParser();p.add_argument('--ignore-term',action='store_true');p.add_argument('--exit-after',type=float);p.add_argument('--descendant',action='store_true');p.add_argument('--marker',type=Path,required=True);args=p.parse_args()
if args.ignore_term:signal.signal(signal.SIGTERM,signal.SIG_IGN)
if args.descendant:
 import subprocess,sys
 subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'])
 time.sleep(.05)
args.marker.write_text(json.dumps({'kind':'controller-test-fixture','training_started':False}))
if args.exit_after is not None:time.sleep(args.exit_after);raise SystemExit(0)
while True:time.sleep(.01)
