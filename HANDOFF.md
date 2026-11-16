# Qwen 4 for 3D — Astra

Updated 2026-11-16. Remote: `Ashen-Builds/qwen-4-for-3d`, branch `Astra`.

## Authorization and verified state

- Owner asked for explanation, source review and local dataset copies. Do not download model weights yet. Training/inference and engine work have not started.
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
