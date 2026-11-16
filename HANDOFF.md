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
- Owner supplied an existing Drive folder. Connector writes still return ACCESS_TOKEN_SCOPE_INSUFFICIENT, but normal browser upload in the verified owner session succeeded. Archive Index (automatically converted to a native Google Doc) and Core Archive Manifest.json are uploaded; Drive list readback verifies both. No model/dataset payloads transferred. Bulk transfer still needs a remote worker or off-stream upload. Folder/file references are kept in the private wiki, not this public repo.


## Active comparison — 2026-11-16

Owner authorized execution, improved prompt and localhost Chrome GLB comparison. Explicit order is official Qwen, fully unload, then CCORE. Owner corrected stream cutoff to 13:00 ET and ended stream; supported off command cleared it, and daily LaunchAgent was updated/reloaded to end 13:00 (not 13:30). Other sessions/engines untouched.

Runtime: task-owned Python 3.12 environment under sibling work/qwen-eval-env; official MLX-LM 0.32.2 / MLX 0.32.4 / Transformers 5.23.0. Native Qwen3.5 text loader, no remote custom code/MTP. Short Qwen benchmark: BF16 55.88 tok/s / 8.55 GB; Q8 group64 96.34 tok/s / 4.69 GB. Nonexclusive capture measurements, not universal backend claims. Both original checkpoints preserved; derived Q8 copies under work/models-derived.

Prompt upgraded to eval/prompts/babylon-marketplace-v2.txt (coherent canal market, Babylonian palette/details, 16 villagers and exportable motion). First matched pass: thinking on, seed42, 65,536-token cap. Official 11,706 tokens / 127.35 s / 93.14 tok/s; CCORE 25,038 tokens / 252.58 s / 99.75 tok/s. Exact prompt token hashes match. Both processes exited and unload receipts saved in work/runs. Neither first-pass final answer is usable: official has TDZ/API/export errors; CCORE has malformed nested script markup and no scene implementation. Raw answers kept, never silently replaced. Devin CLI swe-2-high (listed Free) supplied read-only code critiques with sandbox/auto permission mode; no trust bypass.

A matched secondary retry uses thinking off, seed7, 49,152-token cap. Official retry finished in 70.51 s, 7,399 tokens and was unloaded before CCORE retry started. CCORE retry subsequently completed in 326.49 s /32,682 tokens and exited. All GPU launches wrapped. No training.

User deliverable root is sibling outputs/babylon-comparison. Task-owned loopback server is active on port 8767 (exec session 48144), serving only that directory. Viewer source is in viewer/, dependencies pinned in package.json/lock; local Three.js vendor bundle staged. Browser has not yet been opened on scenes while model inference runs. Need finish retry, unload, stage HTML, inspect in Chrome, click native exports, validate GLBs and present side-by-side. Source-first exception is the owner's explicit pure generated-output benchmark: no stock geometry/motion or agent-authored art is inserted. Mechanical export repairs must be labeled separately; raw-first-pass failures remain visible in report.


## Native GGUF cross-check in progress

MLX matched retry completed: official thinking-off output has real geometry but broken animation/export APIs; CCORE emits full scene/track code but module syntax errors and duplicated declarations. No raw pass is a functional success yet. Models are unloaded. Published CCORE Q8_0 GGUF downloaded and SHA256 verified (`68a66e251d96afdf120d7e8886964317b3f628abef5aad85e564b25b44da2a20`); official Qwen original was converted to Q8_0 using llama.cpp source `4ddf2b9470b44b122e8a5404ae199f04cd03bcec`.

Installed global llama.cpp build 10809 is too old for the current converter schema (missing expected blk.0.ssm_beta.weight); one failed load, not a model-quality result. Do not retry the old binary unchanged. Matching isolated release build is running under work/llama-native-build (exec session 41334); source work/llama-review, logs work/llama-build.log/configure.log. Global binary unchanged. Once built, scripts/generate_asset_llama.py needs --binary pointing to isolated CLI, then official native run, verify exit, CCORE native run. If another native load crashes, stop repeated launches.

Browser QA reservation was released via work/browser-qa.release; server 8767 stays active (session 48144). Chrome scene tabs not opened yet. Generated artifact staging/validator/viewer scripts are ready. Final goal remains actual GLBs visible in Chrome with honest raw/repair provenance; no training.

Matching isolated llama.cpp build completed successfully (commit 4ddf2b9, native Metal). Native cross-check is now queued/running in session 76627, official first then CCORE, with concise art-only prompt v3 and recommended thinking mode. Do not confuse the failed old-binary attempt with model quality. Both MLX pairs with v2 are preserved as failed trials; no successful raw GLB yet. Need inspect native outputs, validate in Chrome, export/reimport and retain honest provenance.


## Completed comparison and current handoff — 2026-11-16

Native v3 pair completed serially: official 81.00 s, exit; CCORE 423.55 s, exit. Both raw outputs failed. Separate labeled diagnostic repairs yielded actual GLBs: official273,832 bytes/static; CCORE1,769,872 bytes/one87-channel clip. Both Khronos0errors/0warnings and reimported visibly side by side in Chrome. CCORE has15people, no leg-animation channels;58/87channels vary, six cloud channels. No invented geometry/new movement formulas. Not a successful full animated voxel town. Full provenance and limitations: docs/comparison-results.md and eval/results.

Deliverable sibling outputs/babylon-comparison, loopback http://localhost:8767/ (task server session48144) stays open for owner; Chrome comparison screenshot and GLBs retained there. No model process/server remains, no training, no goal or automation. Browser QA slot is released at task end; HTTP server is the intentional remaining task process. Primary promptv3 copied into deliverable prompt.txt. Earlier v2 trials and raw native originals retained locally. Current best next step: independent smaller tasks and reliable animation/export validation before any LoRA pilot. Drive contains index/manifest only; bulk payload archive still pending.
