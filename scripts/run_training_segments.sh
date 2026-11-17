#!/bin/bash
# Drive the full fine-tune as bounded segments, each one through the shared GPU slot.
# Usage: run_training_segments.sh RUN_DIR BUDGET_MINUTES [trainer args...]
# Needs A3D_PY (training env python). Stops when the trainer reports the run finished,
# when RUN_DIR/STOP exists, after two failed segments in a row, or when the slot is
# refused 20 times. Never relaunches a crashed segment more than once.
set -u
RUN="$1"; BUDGET="$2"; shift 2
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PY="${A3D_PY:?set A3D_PY}"
SLOT="$HOME/.cache/gpu-slot/bin/gpu_slot.sh"
mkdir -p "$RUN"
fails=0; refused=0; n=0
while true; do
  if [ -f "$RUN/STOP" ]; then echo "[$(date +%T)] STOP file present; exiting"; exit 0; fi
  if [ -f "$RUN/state.json" ] && python3 -c "import json,sys; sys.exit(0 if json.load(open('$RUN/state.json')).get('finished') else 1)"; then
    echo "[$(date +%T)] run finished"; exit 0
  fi
  n=$((n+1))
  echo "[$(date +%T)] segment launch $n"
  "$SLOT" capture --label a3d-train --json "$RUN/segment-gpu-$(date +%H%M%S).json" -- \
    "$PY" "$REPO/scripts/train_image_to_asset.py" --run "$RUN" --budget-minutes "$BUDGET" "$@" >> "$RUN/driver-segments.log" 2>&1
  code=$?
  echo "[$(date +%T)] segment exit $code"
  if [ "$code" -eq 0 ]; then fails=0; refused=0
  elif [ "$code" -eq 75 ]; then
    refused=$((refused+1))
    if [ "$refused" -ge 20 ]; then echo "GPU slot refused 20 times; exiting"; exit 75; fi
    sleep 120
  else
    fails=$((fails+1))
    if [ "$fails" -ge 2 ]; then echo "two failed segments in a row; exiting"; exit "$code"; fi
    sleep 60
  fi
done
