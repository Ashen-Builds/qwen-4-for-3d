# Qwen 4 for 3D

An open research pipeline for a small local model that creates editable 3D assets and exports game-importable GLB files. Current direction: build on **CCORE Qwen3.5-4B-GLB-3D-Coder**, then add a LoRA for measured weaknesses. Blender Python/MCP is optional; the goal is a useful exported asset.

Target destinations: browsers, Godot, Unreal Engine, Unity and Roblox. Format support does not guarantee equivalent materials, animation or game readiness; imports need tests. Model inference happens during asset creation, not necessarily in the shipped game.

## Current status

- Branch: `Astra`. Source review and pinned practice dataset copies completed.
- Both original checkpoints downloaded and hash-verified: **CCORE 17.51 GB + official Qwen 9.34 GB**, 28 files total. All shard/index structures checked without loading models. [Verification receipt](configs/download-receipt.json). Weights stay outside Git.
- No inference, asset generation or training has started. Backend/export compatibility remains untested.
- First comparison: a detailed animated voxel Babylon-inspired marketplace, using identical prompts and conditions for CCORE, upstream Qwen and later our own adapter.
- A bounded overnight training goal follows inspected baselines and an explicit start instruction. No training goal or automation is active.

## Pipeline

1. **Acquire and verify:** pinned original checkpoints, tokenizer/config companions and upstream digests.
2. **Freeze the comparison:** same prompts, settings, declared limits, runtime/precision and seeds; retain raw outputs.
3. **Run baseline A/B:** CCORE first, upstream Qwen second; retain failures and successful exports.
4. **Inspect exported assets:** structure, appearance, motion and destination imports, with preview/export scores separate.
5. **Curate data:** verified corrections and suitable licensed examples; program-family deduplication and isolated held-out tasks.
6. **Train a LoRA on CCORE:** bounded checkpoints on Studio; monitor against untouched CCORE.
7. **Compare A/B/C and quantizations:** include our adapter only when it exists; measure low-memory release targets.

## Start here

| File | Purpose |
| --- | --- |
| [Pipeline plan](docs/PIPELINE.md) | Fair A/B/C testing, rubric, critic roles and future overnight gates |
| [Babylon marketplace prompt](eval/prompts/babylon-marketplace-v1.txt) | Shared request, held out from training |
| [Proposed comparison settings](configs/comparison-v1.json) | Reproducible draft settings, not an active job |
| [Pinned models](configs/model-snapshots.json) | Acquired revisions and upstream-lineage limitation |
| [Model downloader](scripts/download_comparison_models.py) | Official Hub SDK and digest checks; never loads models |
| [Training evidence](docs/ccore-training-evidence.md) | Published CCORE process/data versus missing details |
| [GLB/Neyra review](docs/glb-direction-and-neyra.md) | Tool fit and limitations |
| [Practice data](docs/practice-data.md) | Dataset copies, terms and inspection scope |
| [HANDOFF](HANDOFF.md) | Rolling verified state and next steps |

With an existing `huggingface_hub` installation, inventory model files:

```sh
python3 scripts/download_comparison_models.py --destination ../work/models
```

Add `--download` to copy the original Safetensors and companion files. This does not install a runtime, load weights, generate or train. Alternative GGUFs, gallery media and optional projector files are excluded; quantized evaluation is a separate later experiment.

## Data and rights

CCORE model declares Apache-2.0; its datasets declare MIT to the extent of publisher rights. Preserve notices/attribution. The separately copied 3DCodeVerse aggregate/adapter is noncommercial research material; isolate it from permissive-release mixtures unless terms are resolved. Keep corpora, checkpoints, credentials and caches outside GitHub; publish acquisition instructions and sanitized receipts.

## Original discussion archive

Project began with [the owner's X question](https://x.com/ashen_one/status/2122000927418699866). The 132-reply archive was collected through 2026-11-16 around 10:30 AM ET. Tweets/earlier plans are historical suggestions, not executed experiments or verified budgets.

- [Raw replies](docs/raw-replies.md)
- [Reply summary](docs/replies-summary.md)
- [Initial dataset plan](docs/dataset-plan.md)
- [Original checklist](ACTION_ITEMS.md)

Current direction supersedes earlier stock-base-first and Blender-MCP-only recommendations. Qwen 4 is a future migration/evaluation path, not a dependency of this 4B experiment.

## License

MIT for this project's original code/documentation; see [LICENSE](LICENSE). Model, dataset, quoted-post, dependency and asset rights remain with their respective licensors.
