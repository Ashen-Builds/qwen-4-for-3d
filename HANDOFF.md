# Qwen 4 for 3D — Astra

Updated 2026-11-16. Remote: `Ashen-Builds/qwen-4-for-3d`, branch `Astra`.

## Authorization and verified state

- Initial authority covered explanation/source review/dataset copies only; on 2026-11-16 the owner subsequently authorized downloading CCORE GLB and its official upstream Qwen model, plus updating the open-source plan. Tests follow a later start instruction. Training/inference and engine work have not started.
- Read all 132 archived replies. Reviewed CCORE and 3DCodeVerse primary cards and official Hub/PEFT documentation.
- `docs/practice-data.md` records fit, pinned revisions, terms and copy scope. `scripts/copy_practice_datasets.py` reproduces dataset-only copies and verifies upstream digests.
- Dataset files live outside this checkout under sibling `work/datasets`, in repo-ID/revision folders. Keep raw corpora and machine caches out of GitHub; acquisition manifest and instructions travel in Git instead.
- Completed 72 file downloads, 2,425,999,835 upstream bytes, checked against upstream digests. Opened all 57 Parquet footers: CCORE has 4,146 text rows plus 4,146 matching preview rows; unique training/validation IDs are disjoint. 3DCodeVerse has 2,028,286 merged text rows plus focused SFT sets of 19,609 Blender, 15,704 bootstrapped Blender, 549 Three.js, and 143 held-out test rows. Footer/schema/ID checks are not code execution or visual verification. Inspection used a temporary `uv` PyArrow environment; no training environment installed.
- CCORE data is permissive by publisher declaration; 3DCodeVerse aggregate/adapter is noncommercial research. Do not silently mix the aggregate into a permissively released model/data product.

## Next work, not built

- Select the exact model/base and training backend after owner direction; no model benchmark or compatibility test has been run.
- Build held-out Blender tasks, capture real MCP schemas/episodes and an isolated execution/scene/visual verifier.
- Filter rights, duplicates, sample families, token lengths and failures before training.
- Compare stock base, existing specialization and our adapter on independent tasks before claiming improvement.

## Owner clarification and research — 2026-11-16

- Owner prefers extending CCORE's existing 4B work and serving low-memory local users. End result is portable game-importable 3D assets (prefer GLB); Blender MCP is optional. Still no training or model-weight downloads.
- Found a closer candidate: `ccore/Qwen3.5-4B-GLB-3D-Coder` and matching `ccore/ThreeJS-3D-GLB-Assets`, separate from the scene checkpoint/data already reviewed. Recommendation is to evaluate this GLB specialization, then add a new LoRA for measured gaps. Exact compatibility and quality remain untested.
- `docs/glb-direction-and-neyra.md` records pinned resources, actual model-file metadata, Neyra source findings and proposed tests. Neyra source cloned for static review only; not installed/executed. No new dataset or weights downloaded.
- Neyra lint/verdict/merge-integrity ideas fit, but defaults (512 training / 32 evaluation output tokens, greedy decoding) do not fit CCORE's ~20K-token sampled output recipe. Need custom exported-asset scoring and backend checks.


## Model acquisition and comparison plan — 2026-11-16

- Owner authorized both model downloads. `configs/model-snapshots.json` pins CCORE GLB to `8f32a199f8b22fe3157b9c5c8b42b052a0750dd3` and `Qwen/Qwen3.5-4B` to `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`. This is the identified upstream repository, not proof of the undisclosed historical input commit.
- Downloader copies original Safetensors plus config/tokenizer/license companions; no GGUF/projector/gallery duplicates. `scripts/download_comparison_models.py` verifies upstream digests and index shard presence without loading or executing models.
- Both original checkpoints complete: CCORE 15 files / 17,510,218,308 bytes; official Qwen 13 files / 9,342,905,899 bytes. All upstream digests verified. All 7 shard headers, tensor shapes/offsets and index maps are valid (723 CCORE / 738 Qwen tensors). Sanitized receipt: `configs/download-receipt.json`. No model loaded or executed.
- Models are outside this checkout under sibling `work/models`, source-ID/revision directories. Raw weights/caches must not enter GitHub.
- Owner selected a super-detailed animated voxel Babylon marketplace, people walking/trading, flowing water and moving clouds. Canonical prompt in `eval/prompts/babylon-marketplace-v1.txt`; previous treasure-chest suggestion is superseded.
- Updated root README, `docs/PIPELINE.md`, `docs/ccore-training-evidence.md` and proposed comparison config. First pass uses same prompts/settings and no repairs; output C is absent until our LoRA exists. Babylon prompt/output/corrections stay held out from training.
- No inference, asset generation, training goal, automation, external critic invocation or model server started. Devin/Gemini model IDs, access and budgets remain unverified candidates.

- Static tokenizer inspection: BPE vocabulary and chat-template text match, while added-token records and normalized tokenizer JSON differ. Runtime/tokenizer behavior still needs qualification; do not declare identical tokenization from template equality alone. Original compute precision differs and must be normalized for comparison.
- Header inspection located all 15 upstream-only tensors under `mtp.*`; comparison config disables MTP/speculative decoding. No model tensors were modified.

## Streaming and archive selection — 2026-11-16

- Owner is streaming; STREAMING guard verified active. Do not launch local inference/training or bulk uplink transfers during the stream. No model generation/test has begun.
- Owner clarified optional subscription CLI critics: Gemini Hydrogen 4 only, Devin SWE2 only. No critic CLI called.
- Owner selected core relevant datasets plus both original checkpoints for a Drive archive. Metadata-only subagent compiled sources; `configs/core-archive.json` inventories 5 sources / 88 files / 27,918,579,221 bytes. No archive payload downloaded/uploaded in this task.
- Owner selected the intended Drive account. Search worked, but folder creation was rejected with ACCESS_TOKEN_SCOPE_INSUFFICIENT / PERMISSION_DENIED. No Drive folder/file was created; connection reauthentication with the requested write scope is required. Local source index/manifest are prepared. The uploader accepts local paths; direct remote transfer is unqualified. Bulk transfer needs an authenticated remote worker or off-stream upload. `docs/archive-plan.md` records scope/status.
