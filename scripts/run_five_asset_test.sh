#!/bin/bash
# Five-asset comparison, one arm: generate each prompt through the shared GPU
# slot (one model process at a time), then export/validate/render on CPU.
# Usage: run_five_asset_test.sh ARM MLX_MODEL_DIR [ADAPTER_DIR]
# Paths can be overridden with FIVE_ASSET_ENV_PY, FIVE_ASSET_CARD, FIVE_ASSET_ROOT.
set -u
ARM="$1"; MODEL="$2"; ADAPTER="${3:-}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(cd "$REPO/.." && pwd)"
ROOT="${FIVE_ASSET_ROOT:-$WORK/runs/five-asset-20261117}"
OUTROOT="${FIVE_ASSET_OUT:-$WORK/outputs/five-asset-20261117}"
PY="${FIVE_ASSET_ENV_PY:?set FIVE_ASSET_ENV_PY to the MLX environment python}"
CARD="${FIVE_ASSET_CARD:?set FIVE_ASSET_CARD to the pinned CCORE model card}"
SLOT="$HOME/.cache/gpu-slot/bin/gpu_slot.sh"
mkdir -p "$ROOT/$ARM" "$OUTROOT/$ARM"
for prompt in "$REPO"/eval/prompts/five-asset-20261117/*.txt; do
  name="$(basename "$prompt" .txt)"; run="$ROOT/$ARM/$name"; out="$OUTROOT/$ARM/$name"
  if [ -f "$run/metrics.json" ]; then
    echo "[$(date +%T)] $ARM/$name: generation already recorded, skipping"
  else
    echo "[$(date +%T)] $ARM/$name: waiting for GPU slot"
    extra=(); [ -n "$ADAPTER" ] && extra=(--adapter "$ADAPTER")
    "$SLOT" capture --label "five-asset-$ARM-$name" --json "$ROOT/$ARM/$name-gpu.json" -- \
      "$PY" "$REPO/scripts/generate_asset.py" --gpu-kind mlx --model "$MODEL" --out "$run" \
      --prompt "$prompt" --card "$CARD" --max-tokens 32768 "${extra[@]}" > "$ROOT/$ARM/$name.log" 2>&1
    code=$?
    echo "[$(date +%T)] $ARM/$name: generation exit $code"
    if [ "$code" -eq 75 ]; then echo "GPU slot not granted; stopping this arm"; exit 75; fi
  fi
  if [ -f "$out/result.json" ]; then
    echo "[$(date +%T)] $ARM/$name: export already recorded, skipping"
  else
    node "$REPO/scripts/export_and_render.mjs" --run "$run" --out "$out"
  fi
done
echo "[$(date +%T)] $ARM: done"
