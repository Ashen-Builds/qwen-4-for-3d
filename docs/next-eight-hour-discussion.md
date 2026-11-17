# Next eight-hour run: discussion notes

Updated November 17, 2026. This is a preparation discussion, not authorization to start another training run. Owner wants a better chance of beating untouched CCORE and explicitly judged the present output poor.

## Supplied CCORE collection and actual usage

[CCORE High-Quality Datasets for 3D Creation](https://huggingface.co/collections/ccore/ccore-high-quality-datasets-for-3d-creation) currently lists two dataset repositories. Reviewed their cards and compared against saved run manifests on November 17:

| Source | What we have used | Next-run relevance |
| --- | --- | --- |
| [ThreeJS-3D-GLB-Assets](https://huggingface.co/datasets/ccore/ThreeJS-3D-GLB-Assets) | Downloaded/archived; source for replay and derived correction tasks. Selected Thinking48 had 399 source replay examples available for main training and inherited 48 batch-one updates, not a full pass through those 399. Its 47 replay-development rows stayed separate. | Replay to retain existing asset/export ability; inspect full-program source/export/motion. It is existing CCORE training material, so replay alone is not a demonstrated route to surpassing CCORE. |
| [ThreeJS-3D-Scenes](https://huggingface.co/datasets/ccore/ThreeJS-3D-Scenes) | Downloaded/archived earlier, but not included in selected Thinking48's main training mixture. | Candidate for broader layout, environment and voxel examples after inspection. Its published interface uses core Three.js without addons; preview animation is not proof of exported GLB animation. Do not mix unchanged into the GLB curriculum blindly. |

Collection entries are references, not additional independent samples. Scenes has 4,146 unique scene examples; text and previews are paired views of the same IDs, not twice the training data. GLB card reports 3,918 tested/rendered/export-validated examples. Publisher quality claims do not replace our source execution and task-compliance checks. Cards declare MIT subject to publisher rights; preserve attribution, pinned revisions and source notices. Do not treat publisher validation rows as new clean tests for its already-trained model.

The selected run uses GLB source revision `276821245d5714b95571465569ed5b844ac6adc7`, with prepared manifest `e8404afb752910be8e0ca7e1242d3d62e32fa6f5a31740ae6b0e40d1f8d1acdd`. Saved manifest status describes its original proposal; subsequent job/config/accounting receipts establish that it actually trained. See the final report and accounting correction.

## Findings to carry forward

- Prior experiment: 74.65 minutes of successful training-job wall time across attempts, 54.16 minutes of update-loop timers. Thinking48 inherited 48 main updates / 987,295 real target exposures, about 15.4 minutes of main-job time. Total work across branches must not be presented as one candidate's training.
- Both displayed Babylon GLBs are repair-assisted. CCORE needed syntax/argument/reference/track repairs and calls to existing unused animation builders. Astra needed object/index/tuple/quaternion/scale wiring fixes and omission of eight unresolved sway tracks. No raw Babylon success; assisted visuals remain poorer than the requested scene.
- Preserve small-model LoRA direction. Limited new supervision, one-layer coverage and short inherited training are hypotheses, not isolated causes. Padding-mask defect was fixed but not proven responsible for degeneration. A later failed checkpoint is not proof that more training generally harms quality.
- Original replies emphasized successful verified examples, real tool schemas where relevant, and held-out evaluations. Three.js-to-GLB remains this benchmark; Blender MCP was optional and is a distinct curriculum if adopted.

## Proposed preparation before another run

1. Audit scene-level candidates from both sources, with actual runtime, exported-file, reimport and animation checks. Record architecture/material/animation/length distributions and deduplicate by program family. Convert any preview-only scene to the GLB interface explicitly, execute it, and retain provenance; do not fabricate reasoning traces or silently concatenate incompatible formats.
2. Add independently verified examples for measured weaknesses: coherent multi-building layouts, voxel construction, character gait, correct path loops, water/cloud motion and reliable export. Use a licensed source or permitted teacher workflow; replay retains skills, additions teach the intended improvement. Babylon and final-test outputs/repairs remain excluded.
3. Freeze training data, explicit thinking/template/mask settings and a safe trainer configuration before the eight-hour clock. Qualify representative sequence lengths and adapter coverage, ordinary save/reload and actual resume semantics. Do not mistake a controller dry run for training readiness.
4. Prepare a larger fixed development panel and independent final tasks before training. Automatically classify syntax/runtime/export/motion failures; inspect common multi-view renders and animation samples. Do not spend each checkpoint review repairing its scene. Preserve raw outputs and score repaired diagnostics separately.
5. Reserve most of the training window for one deliberate training recipe, with bounded checkpoint evaluations, recoverable saves and regression stops. Set measured step/token/example-coverage targets; do not promise a quality win based on elapsed hours. Final scheduling and launch require a new owner instruction.

No new downloads, inference or training were started for this discussion. The collection is not a newly discovered training corpus we had entirely missed; the improvement opportunity is how we select, verify, augment and train on its examples.
