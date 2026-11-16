# Babylon comparison — 2026-11-16

Both models failed to produce a usable unassisted asset. Separately labeled diagnostic repairs yielded valid GLBs, viewed after export/reimport in Chrome. CCORE is visibly richer in this example; this is not proof of a general training gain or game-ready output. No training started.

## Primary native pair

Same [v3 prompt](../eval/prompts/babylon-marketplace-v3.txt), CCORE's documented system instruction, Q8_0, llama.cpp Metal source `4ddf2b9`, seed42, thinking on and common finite limits. Official Qwen ran first and exited completely before CCORE. Both exited before preview. See [settings](../configs/comparison-v1.json) and [machine-readable report](../eval/results/babylon-20261116.json).

| Evidence | Official Qwen3.5-4B | CCORE GLB specialization |
| --- | ---: | ---: |
| Native wall time | 81.00 s | 423.55 s |
| Raw usable export | Failed | Failed |
| Repaired diagnostic GLB | 273,832 bytes | 1,769,872 bytes |
| glTF mesh definitions | 133 | 647 |
| Animation clips/channels | 0 / 0 | 1 / 87 |
| Khronos validator errors/warnings | 0 / 0 | 0 / 0 |

CCORE has fifteen person roots, below the requested sixteen, and no exported leg-animation channels. Of 87 channels, 58 have changing values; six target clouds. Existing walking flags are false. A clip count does not establish walking, water flow or good motion. Exported scene is a compact market diorama, not the complete requested town. Official export is sparse and static. Materials/shaders and later engine imports are not certified by glTF validation.

## Repairs and comparison limits

Official needed broken import-map bootstrap corrected, two unused nonexistent addon imports removed, invalid action setup removed, and exporter replaced with a static parseAsync download. Its invalid water shader remains a limitation. No new animation was added.

CCORE needed stray non-code text commented, malformed arrow callbacks and duplicate calls fixed, track value serialization guarded, existing person descriptors bound to existing scene objects, and invalid/nonfinite curves filtered. Skipped curves were not replaced. Its existing geometry, fifteen-person list, movement formulas and walking flags remain. [Official patch](../eval/results/qwen-native-repair.patch) and [CCORE patch](../eval/results/ccore-native-repair.patch) preserve the mechanical edits, separate from dependency staging.

Repairs were exploratory and did not use a predeclared equal repair budget. Do not score these as raw successes or use repair effort as a fair ranking. Original responses/source and exact repair variants remain in local evidence. No stock geometry, teacher-designed geometry or new motion curves were inserted. Generated HTML uses unseeded browser randomness; a fixed model seed does not make source re-execution deterministic. The frozen GLBs are the canonical displayed outputs. Publisher GGUF versus locally converted GGUF is another confound. The exact historical upstream training-input revision is undisclosed.

## All earlier trials retained

Two matched MLX Q8 v2 pairs preceded the native v3 pair. Thinking on/seed42: official 11,706 tokens /127.35 s; CCORE 25,038 /252.58 s. Thinking off/seed7: official 7,399 /70.51 s; CCORE 32,682 /326.49 s. All failed raw usable export due syntax, scene/API or export defects. These are separate trials, not additional successful samples. A failed old global llama.cpp initialization is infrastructure failure, not model quality. Devin SWE-2 (CLI swe-2-high listed Free) provided read-only sandboxed code critiques; no Gemini call.

## Local viewer and reproducibility

Install pinned viewer dependencies with `npm ci --ignore-scripts`. Keep weights and run evidence outside Git. Build matching llama.cpp for Metal, convert official pinned weights to Q8_0 and verify publisher CCORE GGUF digest. Extract the system instruction from the pinned card. Run `scripts/generate_asset_llama.py` through the machine's shared GPU-slot wrapper, supplying `--binary`, `--model`, `--out`, `--prompt` and `--system`. Run serially and verify process exit. The helper records raw response, runtime log and metrics; it does not repair output or guarantee export.

Use `scripts/inspect_generated_html.py` for syntax checks and `scripts/stage_generated_page.py` for recorded local dependency rewrites/frame cap. Execute generated code only in the constrained local preview; retain originals and record every repair separately. Export from the generated page. Run `node scripts/validate_glb.js FILE`, inspect actual animation values and reimport playback. Structural checks alone cannot establish appearance or motion.

The viewer expects `qwen/asset.glb`, `ccore/asset.glb`, per-arm `result.json`, `comparison-report.json` and `vendor/three/` under a dedicated deliverable directory. Copy viewer files there, Three.js from node_modules/three into vendor/three, then serve with `python3 scripts/serve_comparison.py --directory DELIVERABLE_DIRECTORY --port 8767`. It binds loopback only. The completed local deliverable is served at http://localhost:8767/; large assets and private logs are not committed.

Next: choose smaller independent held-out tasks, predeclare repeated-seed and equal correction budgets, and verify reliable animated export before training. Keep this Babylon prompt, near-duplicates, outputs and targeted repairs held out. Train only after a separately authorized, measured LoRA pilot.
