#!/bin/bash
# Image-to-asset comparison, one arm: each reference image goes through the
# shared GPU slot (one llama.cpp process at a time), then export/validate/render on CPU.
# Usage: run_five_asset_image_test.sh ARM GGUF_MODEL [ONLY_NAME]
set -u
ARM="$1"; MODEL="$2"; ONLY="${3:-}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(cd "$REPO/.." && pwd)"
ROOT="${FIVE_ASSET_ROOT:-$WORK/runs/five-asset-image-20261117}"
OUTROOT="${FIVE_ASSET_OUT:-$WORK/outputs/five-asset-image-20261117}"
BIN="${FIVE_ASSET_LLAMA:?set FIVE_ASSET_LLAMA to the llama-cli binary}"
MMPROJ="${FIVE_ASSET_MMPROJ:?set FIVE_ASSET_MMPROJ to the vision projector GGUF}"
P="$REPO/eval/prompts/five-asset-20261117"
SLOT="$HOME/.cache/gpu-slot/bin/gpu_slot.sh"
mkdir -p "$ROOT/$ARM" "$OUTROOT/$ARM"
for image in "$P"/images/*.png; do
  name="$(basename "$image" .png)"; run="$ROOT/$ARM/$name"; out="$OUTROOT/$ARM/$name"
  [ -n "$ONLY" ] && [ "$ONLY" != "$name" ] && continue
  if [ -f "$run/metrics.json" ]; then
    echo "[$(date +%T)] $ARM/$name: generation already recorded, skipping"
  else
    echo "[$(date +%T)] $ARM/$name: waiting for GPU slot"
    "$SLOT" capture --label "five-asset-image-$ARM-$name" --json "$ROOT/$ARM/$name-gpu.json" -- \
      python3 "$REPO/scripts/generate_asset_llama_image.py" --binary "$BIN" --model "$MODEL" --mmproj "$MMPROJ" \
      --image "$image" --out "$run" --prompt "$P/image-instruction.txt" --system "$P/system.txt" > "$ROOT/$ARM/$name.log" 2>&1
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
