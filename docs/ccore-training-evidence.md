# CCORE training process: evidence and reuse

Reviewed 2026-11-16: [GLB model card](https://huggingface.co/ccore/Qwen3.5-4B-GLB-3D-Coder), file inventory, [matching dataset](https://huggingface.co/datasets/ccore/ThreeJS-3D-GLB-Assets) and [author's response](https://huggingface.co/ccore/Qwen3.5-4B-GLB-3D-Coder/discussions/1). This is not a reproduction of an undisclosed run.

## Public evidence

- Author identifies `Qwen/Qwen3.5-4B` as the starting model and describes carefully designed supervised training. GLB specialization follows an earlier general scene-generation experiment.
- Full checkpoint and quantized versions are public. Card describes FP32 text and BF16 vision tensors; storage precision is not a training-hyperparameter record.
- GLB conversations, target code, previews and meshes are public. Dataset reports 3,918 tested/rendered/export-validated examples (3,501 train / 417 validation), across 40 domains.
- Documented interface: asset request → complete HTML/Three.js page → preview/GLB export. System instruction, inference sampling and long-output expectations are given.
- Author acknowledges dimensions, mesh correctness, naming and export-interface weaknesses, and plans tool-using iterative agents with targeted validation.

## Not established in inspected GLB materials

- Full fine-tuning versus LoRA/QLoRA for this exact run; rank/targets if adapters were used; optimizer, rate/schedule, batch/accumulation, steps/epochs, seed and full trainer configuration/version.
- Exact historical upstream commit; complete teacher-generation/filtering recipe and reproducible execution/visual-validation harness.
- A broad independent benchmark establishing gains across our target imports/tasks.

Do not present the earlier scene model's report, community speculation, inference settings or our LoRA proposal as this GLB checkpoint's exact training recipe.

## Reuse

Use the released checkpoint, expected interface, suitable licensed data and verified-export focus. Preserve attribution. Add our own transparent reproducible recipe and new examples for measured weaknesses rather than claim to duplicate unpublished training.

Community experience supports preserving the documented interface and checking exports, but individual runs are not a controlled benchmark. The author's response establishes supervised specialization, not all hyperparameters. Our ordinary LoRA is a new experiment, not a statement about the author's method.

Devin/Gemini roles and a future bounded overnight goal are described in `PIPELINE.md`. Current live-run state and actual critic/training evidence are recorded in HANDOFF.md and the overnight experiment record.
