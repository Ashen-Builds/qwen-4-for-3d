#!/bin/bash
# After training: export the best checkpoint, convert to Q8 GGUF, run the five test
# images through it as the "ours" arm, and build the three-model gallery.
# Usage: finish_our_model.sh RUN_DIR
# Needs A3D_PY, A3D_ORIGINAL (CCORE HF dir), A3D_LLAMA_SRC (llama.cpp checkout),
# A3D_CONVERT_PY (python with gguf deps), FIVE_ASSET_LLAMA, FIVE_ASSET_MMPROJ.
set -eu
RUN="$1"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(cd "$REPO/.." && pwd)"
CK="$(python3 -c "import json;s=json.load(open('$RUN/state.json'));print((s.get('best') or {}).get('checkpoint') or s['checkpoint'])")"
echo "[$(date +%T)] exporting $CK"
HF="$WORK/models/a3d-ours-hf"; GGUF="$WORK/models-native/a3d/ours-Q8_0.gguf"
"${A3D_PY:?}" "$REPO/scripts/export_trained_to_hf.py" --original "${A3D_ORIGINAL:?}" --weights "$RUN/$CK/lm.safetensors" --out "$HF"
( cd "${A3D_LLAMA_SRC:?}" && "${A3D_CONVERT_PY:?}" convert_hf_to_gguf.py "$HF" --outfile "$GGUF" --outtype q8_0 2>&1 | grep -E "n_tensors|successfully|rror" )
echo "$CK" > "$WORK/models-native/a3d/ours-Q8_0.checkpoint.txt"
FIVE_ASSET_OUT="$WORK/outputs/five-asset-v2" "$REPO/scripts/run_five_asset_image_test.sh" ours "$GGUF"
python3 "$REPO/scripts/build_five_asset_gallery.py" --images "$REPO/eval/prompts/five-asset-20261117/images" \
  --outputs "$WORK/outputs/five-asset-v2" --arm "qwen-original=Original Qwen 3.5 4B" --arm "ccore=CCORE" --arm "ours=Ours" \
  --page "$WORK/outputs/five-asset-v2/index.html"
echo "[$(date +%T)] done"
