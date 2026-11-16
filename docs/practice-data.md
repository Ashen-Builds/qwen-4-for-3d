# Practice data review — 2026-11-16

The owner authorized local dataset copies and research, but explicitly withheld model-weight downloads. No training, inference, Blender execution, dataset-code execution, or model-weight downloads were performed.

## Sources

| Source | Fit | Reviewed revision | Terms |
| --- | --- | --- | --- |
| [CCORE model](https://huggingface.co/ccore/Qwen3.5-4B-3D-Coder) | Already fine-tuned Qwen3.5-4B, primarily Three.js code; candidate comparison, not verified Blender MCP expertise | `4b9f05f3a0382725b679c5e32a338b88acaf0064` | Apache-2.0 model card; base/dependency rights remain |
| [CCORE dataset](https://huggingface.co/datasets/ccore/ThreeJS-3D-Scenes) | 4,146 unique scene examples, 3,933 train + 213 validation; text/code plus matching previews, not 8,292 independent examples | `57b77a19d38eee8316c8b1f9e71c772046d9f48c` | MIT to extent of publisher rights; teacher-generated data |
| [3DCodeVerse-2M](https://huggingface.co/datasets/3dcodeverse/3dcodeverse-2m) | Mixed Blender/CAD/shader/web code; 2,028,286 program-caption rows, not that many distinct Blender tasks | `1d3935d94760922ef7a55f4a1a3e19a3b90ec702` | CC-BY-NC-SA-4.0; noncommercial research and source-specific terms; keep separate from permissive publication track |
| [3DCodeVerse 27B adapter](https://huggingface.co/3dcodeverse/3dcodeverse-qwen3.8-27b-lora) | Existing rank-16 LoRA for Qwen3.8-27B, includes Blender Python; author reports no held-out eval logged for this run | `481e1821db103209e3e565559d1124e11dd2fce0` | CC-BY-NC-SA-4.0; requires compatible base, not standalone; not downloaded |

The model author's stated experiment concerns small-model feasibility. Lower cost and faster iteration are reasonable size-based explanations for 4B, not a documented comparative decision against 27B. Neither model has been evaluated by this session. Continuing training from a specialized checkpoint is possible with compatible training software, but a fresh stock-base LoRA gives a clearer experiment. Do not evaluate an existing model's generalization solely on its own training examples.

## Local copies

Run from the repository with an existing `huggingface_hub` installation:

```sh
python3 scripts/copy_practice_datasets.py --destination ../work/datasets
python3 scripts/copy_practice_datasets.py --destination ../work/datasets --download
```

The first command inventories without downloading. The second uses the official Hub SDK, immutable revisions, four download workers and upstream digest verification. It accepts only the dataset repositories explicitly listed in the script and never loads downloaded code. It requires an additional 20 GiB free-space reserve. `COPY_MANIFEST.json` in each revision folder records exact files, sizes and verified SHA256 values. Data and caches stay outside the GitHub source tree.

- CCORE: complete current snapshot, 32 files, 1,504,196,639 upstream bytes, including preview Parquet files.
- 3DCodeVerse: 40 files, 921,803,196 upstream bytes: all 30 merged text shards, selected `finetune/sft/{blender,blender_bootstrapped,threejs}` files, matching Blender/Three.js held-out tests and source documentation. Media archive, most other dialect-specific fine-tuning copies, DPO pairs and other tests excluded. Full upstream archive is advertised around 1.25 TB; this is intentionally a partial snapshot.
- Keep upstream tests separate from training. Deduplicate by program/sample family, not only prompt wording. Some rows are alternate captions of the same program, and sources overlap across datasets.
- Copy integrity is not training-data quality: no runnable/visual verification is claimed. External script execution needs an isolated verifier and the shared engine/GPU protocol.

Completed copy verification: 72 files / 2,425,999,835 upstream bytes. All 57 Parquet footers opened successfully. CCORE has 4,146 unique scene IDs across disjoint train/validation splits, plus 4,146 preview rows. 3DCodeVerse merged text has 2,028,286 rows; focused SFT has 19,609 Blender, 15,704 bootstrapped Blender and 549 Three.js rows; copied held-out tests have 103 Blender and 40 Three.js rows. This inspection did not execute embedded code or validate rendering.

## Additional candidates (reviewed cards only; not downloaded)

- [BlendNet](https://huggingface.co/datasets/FreedomIntelligence/BlendNet): ~12.1k instruction/Blender-script rows, Apache-2.0 declaration; filter and verify locally.
- [Bioinspired3D](https://huggingface.co/datasets/lamm-mit/Bioinspired3D): ~4.56k Blender prompt/code rows, MIT declaration; repeated paraphrases require program-level deduplication. Obtain directly upstream to inspect its own terms independently of the restricted aggregate.
- [OpenBlender_Train](https://huggingface.co/datasets/PGCRYPT/OpenBlender_Train): documentation Q&A; optional knowledge supplement, not proof of tool skill.
- [deepfabric-blender-mcp](https://huggingface.co/datasets/nolabs/deepfabric-blender-mcp): synthetic MCP-format reference; license unresolved and actual tool compatibility/execution unverified.
- [BlenderFORGE](https://arxiv.org/abs/2611.10768): research lead on verified scene editing, teacher trajectories and rewards; abstract inspected, data/code availability and rights not established here.

Public code datasets supplement our verified MCP episodes; raw meshes or `.blend` assets alone do not teach a text model the action sequence. Capture prompt, initial state, real tool schema, actions, results, corrections and acceptance evidence for our own data.

## Method recommendation (not a training configuration)

Prefer a small stock Qwen baseline with ordinary LoRA for a first controlled experiment if the chosen MLX/model combination supports it. QLoRA keeps the frozen base quantized while learning adapters; it is useful for memory savings, especially as model/context size grows, but does not guarantee faster training or identical results. 4B versus 27B is roughly a 6.75× nominal parameter difference; weight-only FP16 estimates are about 8 GB versus 54 GB before activations, caches, adapters and optimizer memory. Actual architecture and training measurements govern capacity.
