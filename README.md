# Qwen 4 for 3D

An open research pipeline for a small local model that creates editable 3D assets and exports game-importable GLB files. Current direction: build on **CCORE Qwen3.5-4B-GLB-3D-Coder**, then add a LoRA for measured weaknesses. Blender Python/MCP is optional; the goal is a useful exported asset.

Target destinations: browsers, Godot, Unreal Engine, Unity and Roblox. Format support does not guarantee equivalent materials, animation or game readiness; imports need tests. Model inference happens during asset creation, not necessarily in the shipped game.

## Current status

- Branch: `Astra`. [Frozen visual comparison and GLBs](eval/baselines/babylon-20261116/README.md) include a reserved future result for our adapter.
- Both original checkpoints were downloaded and hash-verified. Official Qwen original/Q8 copies were subsequently deleted at the owner’s request (18.44 GB logical bytes); CCORE stays available. [Acquisition receipt](configs/download-receipt.json), [removal receipt](configs/official-model-removal.json).
- Comparison completed on M3 Ultra: both raw outputs failed. Separately labeled repaired GLBs load side by side; CCORE is visually richer but misses walking/full-town requirements. [Results and limitations](docs/comparison-results.md). These are historical repaired diagnostics.
- First comparison: a detailed animated voxel Babylon-inspired marketplace, using identical prompts and conditions for CCORE, upstream Qwen and later our own adapter.
- The November 16–17 overnight experiment has stopped. **Astra did not improve the Babylon marketplace.** The selected 48-update adapter improved one raw waterwheel's rotation axis, but failed the raw orrery export. These two single-seed tests do not establish general improvement. [Final report](docs/overnight-final-20261117.md).
- Actual GLBs, raw failures, repair patches, screenshots and accounting are retained. The earlier 48-hour proposal and active-run notes are historical; no further training is scheduled. New checkpoints stay private. [Final evidence](eval/results/overnight-20261117.json), [historical archive verification](configs/archive-verification.json).

Reopen the final comparison after installing the pinned dependencies:

```sh
python3 scripts/build_final_review.py --out ../outputs/astra-final
python3 scripts/serve_comparison.py --directory ../outputs/astra-final --port 8767
```

Open `http://localhost:8767/final-review/`. The four selections include the matched BF16 Babylon diagnostics, the original CCORE reference, and both raw final tests. The viewer starts paused and renders on demand; playback is capped at 30 fps. Babylon's GLBs are explicitly repair-assisted, and the missing Astra orrery is displayed as a failure. These are browser checks, not game-engine import certification.

## Pipeline

1. **Acquire and verify:** pinned original checkpoints, tokenizer/config companions and upstream digests.
2. **Freeze the comparison:** same prompts, settings, declared limits, runtime/precision and seeds; retain raw outputs.
3. **Run baseline A/B:** official Qwen first, fully unload, CCORE second; retain failures and successful exports.
4. **Inspect exported assets:** structure, appearance, motion and destination imports, with preview/export scores separate.
5. **Curate data:** verified corrections and suitable licensed examples; program-family deduplication and isolated held-out tasks.
6. **Train a LoRA on CCORE:** bounded checkpoints on Studio; monitor against untouched CCORE.
7. **Compare A/B/C and quantizations:** include our adapter only when it exists; measure low-memory release targets.

## Start here

| File | Purpose |
| --- | --- |
| [Controller runbook](docs/overnight-controller.md) | Guarded scheduling, review protocol and dry tests |
| [48-hour pilot proposal](docs/48-hour-pilot.md) | Scoped training/evaluation plan, no job started |
| [Pipeline plan](docs/PIPELINE.md) | Fair A/B/C testing, rubric, critic roles and future overnight gates |
| [Babylon marketplace prompt](eval/prompts/babylon-marketplace-v3.txt) | Shared request, held out from training |
| [Recorded comparison settings](configs/comparison-v1.json) | Primary native-pair settings and diagnostic status |
| [Pinned models](configs/model-snapshots.json) | Acquired revisions and upstream-lineage limitation |
| [Model downloader](scripts/download_comparison_models.py) | Official Hub SDK and digest checks; never loads models |
| [Training evidence](docs/ccore-training-evidence.md) | Published CCORE process/data versus missing details |
| [Curated Drive archive](docs/archive-plan.md) | Selected core sources, exact inventory and transfer status |
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
