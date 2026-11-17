# Proposed 48-hour CCORE LoRA pilot

Status: preparation only; training has not started or been scheduled. Working name: **Astra-3D Sprint 01**. The owner’s latest time takes precedence: **Monday November 16, 2026 at 11 p.m. EST** (8 p.m. PST), not the earlier 11 a.m. PST wording. Proposed hard stop: **Wednesday November 18 at 11 p.m. EST**. Start remains conditional on readiness and an explicit owner instruction. Goal: a measurable improvement over untouched CCORE in valid animated GLB generation while preserving its visual strengths. A substantial visual improvement is possible, not guaranteed by elapsed training time. Small-model inference speed measured previously is not training throughput.

## Eight-hour milestones

| Elapsed | EST | PST | What the owner can inspect |
| --- | --- | --- | --- |
| 0 h | Mon Nov 16, 11 p.m. | Mon 8 p.m. | Frozen CCORE control, data/config receipt and start checks |
| 8 h | Tue Nov 17, 7 a.m. | Tue 4 a.m. | First adapter checkpoint: same Babylon prompt, raw GLB attempt, split view, metrics and failures |
| 10 h | Tue Nov 17, 9 a.m. | Tue 6 a.m. | Morning review of the completed 7 a.m. pair; heavy owned compute paused for computer use |
| 16 h | Tue Nov 17, 3 p.m. | Tue noon | Second checkpoint or explicit unchanged/paused status |
| 24 h | Tue Nov 17, 11 p.m. | Tue 8 p.m. | Day-one checkpoint, fixed probes and regression decision |
| 32 h | Wed Nov 18, 7 a.m. | Wed 4 a.m. | Second overnight result, same views and motion evidence |
| 40 h | Wed Nov 18, 3 p.m. | Wed noon | Latest checkpoint and development comparison; final candidate frozen |
| 48 h | Wed Nov 18, 11 p.m. | Wed 8 p.m. | Hard stop, final comparison and report, including any unfinished/failed work |

These are wall-clock milestones including evaluation and pauses. Save the adapter early enough to finish the preview before each deadline; reserve up to an hour per milestone, adjusting from measured inference time. Checkpoints are also saved more frequently for recovery. If paused or no new valid adapter exists, show the last completed output with its age and reason; never invent progress. No process wakes automatically from this document. [Machine-readable plan](../configs/sprint-48h.json).

For 9 a.m., provide a browser gallery with CCORE versus Astra, downloadable raw GLBs (or a clear raw-failure result), identical camera/light/time samples, a short motion capture or reproducible playback, and a compact scorecard. Existing official-Qwen/CCORE repaired snapshots remain separately labeled historical references. Training remains paused until daytime availability is cleared; existing streaming detection still applies. A 48-hour deadline may contain substantially fewer training hours when the owner is using the machine.

## Launch qualification

Preparation passes the CPU-only checks in [the preflight receipt](../configs/preflight.json). The original CCORE backup and all selected datasets are uploaded, complete-target replay and generic repair data are frozen, the actual training tokenizer/masks match, and a zero-update adapter shape/dtype audit passed. No gradients or optimizer steps have run. Live qualification is the first authorized action, not an unobserved assumption.

After the owner explicitly starts: run the short ten-step configuration, verify finite gradients/loss and adapter save/reload, then run the three complete representative-length examples. Measure memory, seconds/step and tokens/step before choosing segment iterations. Stop on failure. The main config's 200 iterations are a provisional segment ceiling, not a measured 48-hour budget. Preserve data/template/runtime/config hashes and use isolated run directories. Model training/save/reload and the supervised multi-checkpoint loop remain unvalidated until actually exercised.

The prepared [entrypoint](../scripts/run_qualification.py) prints a plan by default. It requires an explicit start flag and an authorization record from the owner's actual start instruction before launching; the file grants no authority by itself. Missing authorization was tested to refuse without creating a run. Qualification stops after ten minutes or on the streaming guard, terminates only its owned process group, and does not automatically start the main run. The 48-hour run is supervised by the current Codex session; no independent daemon, cron, automation or training goal is active.

## What counts as an improvement

Use the exact Babylon user/system prompt at every milestone, with seed 42 and common runtime, precision, output limit, dependency bundle and rendering. Preserve untouched CCORE as the principal control. Regenerate that control once on the selected evaluation runtime; the prior repaired native Q 8 output cannot be a raw matched control for BF 16/MLX adapter output. Run one model at a time and unload between arms. Freeze runtime after qualification; a backend change requires rerunning the control.

A fixed seed controls model sampling but original scene code may use browser randomness. Keep original source and declare an identical seeded-random harness when used for new controlled runs; preserve the prior GLBs exactly. Compare equal camera/light/viewer settings and explicit playback times. Primary scoring is unassisted; diagnostics with mechanical repairs are shown separately and never counted as a raw model gain. No manual beautification, sourced asset insertion or per-checkpoint prompt changes.

At each milestone run the showcase plus a small fixed development probe suite covering static props, multi-object composition and exportable motion. Record raw syntax/load/export pass rates, finite GLB data, clip values and actual motion, missing parts, materials, triangles/file size, latency and blinded appearance preference. Clip count alone does not prove walking or flowing water. Preserve every outcome, including regressions. Optional critics: Devin CLI SWE2 free model or Gemini CLI Hydrogen 4 only; no paid substitutions.

The Babylon case is a repeatedly viewed showcase/development monitor, not an untouched final test and never a training target. Freeze a separate 20-task final set with two seeds per task and reserve budget for paired control/adapter generations before 48 h; keep it out of checkpoint selection. Proposed success threshold: at least 15 percentage points better raw valid-export rate, better requested-motion coverage, and no material visual regression. Freeze thresholds before training. This small test is practical evidence, not a statistical-significance claim. If timing cannot fit final evaluation, report incomplete evidence rather than show only the best sample. Stop early on repeated invalid exports, sustained regression, nonfinite training, resource tripwires or loss of desktop health. Always retain the best known checkpoint and original CCORE.

## Runtime and data

Use original CCORE weights as immutable source. On the verified 256 GiB Studio, test ordinary LoRA on a compatible BF 16 text conversion first; compare a quantized-base adapter only if measured throughput/memory justifies it. Exact Qwen3.5 hybrid-layer training/backprop support and target selection remain unqualified; successful inference does not prove training works. A small train/save/reload gate is mandatory. MLX-LM supports LoRA/QLoRA and prompt masking, but generic documentation is not proof of this exact checkpoint/config. See [official guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md).

Prioritize verified complete exports, valid animation tracks and varied scene decomposition, with enough original-style examples to avoid visual regressions. Reusing CCORE's existing training dataset alone may add little new skill. Sources require provenance, rights, code execution/export checks and family splits. Keep noncommercial 3DCodeVerse outside a permissive release mixture until terms are resolved. Teacher or sourced-asset examples need explicit lineage and must not leak into generated-only evaluation.

No external spend, deployment or model publication is authorized by this plan. GPU slots and streaming limits still apply. Optional critics remain Devin CLI SWE2 free models or Gemini CLI Hydrogen 4 only. Critique opinions supplement file/runtime/visual evidence.

## Reuse for Qwen4

Checked 2026-11-16: [official release log](https://docs.qwencloud.com/changelog/models) lists Qwen4-Max today. An authenticated-free public Hugging Face Hub API query for official author Qwen and search Qwen4 returned no models. A downloadable Qwen4 4 B/8 B and its release date are therefore unverified; do not schedule around an assumed release. [Official model catalog](https://huggingface.co/Qwen/models).

Reuse validated data, task splits, prompt contracts, exporter, verifier, viewer and scoring. Requalify tokenizer/chat template, architecture, adapter modules, runtime, license, precision and training throughput for Qwen4. A CCORE/Qwen3.5 LoRA is architecture/checkpoint-specific and cannot be assumed to load on Qwen4. New Qwen4 weights need new adapters; additional distillation may be possible only after quality and rights checks. Future visual comparison should keep model generation/size differences explicit.

## Data preparation and public guidance

The archive separates direct Three.js prompt/code data, optional Blender code, finished asset references and restricted research data. CCORE’s GLB data is useful for format/style replay, but the model already trained on it: repeating it is not new evidence of skill gain. Add newly verified examples in different task families for export correctness, motion binding and scene composition. Start with hundreds of strong verified examples if available; sample count is subordinate to complete targets, coverage, rights and successful execution.

Follow [MLX-LM’s official LoRA guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md) for the actual Mac runtime; use [Hugging Face TRL’s SFT guidance](https://huggingface.co/docs/trl/en/sft_trainer) for chat formatting, masking, truncation and packing principles. TRL/CUDA flags are not copied into MLX. Inspect the exact rendered targets/masks: separate reasoning fields must not be accidentally dropped or trained in an inference-incompatible format. MLX prompt masking and TRL assistant-only masking have different semantics. Preserve full executable responses; do not cut long HTML mid-function to fit a convenient context length. Bucket lengths and use packing only when the backend correctly isolates examples. Verify adapter modules/trainable counts and reload behavior, as emphasized by [PEFT troubleshooting](https://huggingface.co/docs/peft/developer_guides/troubleshooting). Lower training loss is not exported-asset quality.

Raw mesh libraries require captions plus reproducible programs/actions to become text-model demonstrations. Reference assets and motions may help build licensed training episodes later, but never silently appear in the generated-only comparison. Broad asset downloads alone cannot close the missing-training-examples gate.


## Verified preparation receipt

The [source archive](../configs/archive-verification.json) is complete: six packages, 216 canonical payload files/parts, 21,484,759,314 bytes. This includes original CCORE, its GLB/scene datasets, optional BlendNet/Bioinspired3D, Pixel Atlas references and isolated noncommercial 3DCodeVerse. Every expected remote name and byte size was checked. Per-part/whole-archive SHA256 manifests were computed locally and uploaded; full cloud-byte re-download is not claimed. One duplicate was retained under a noncanonical suffix. The connector's 100 MiB downstream cap requires 96 MiB numbered parts. The reassembly helper verifies all hashes before creating a ZIP and never executes or extracts content. Local copies remain available for the sprint.

The frozen replay set has **506 train / 63 development** complete CCORE conversations, reasoning preserved, 9,096–32,659 tokens, no truncation and no subject-family overlap in our continuation split. All 576 initial candidate exports passed independent Khronos validation with zero errors/warnings; seven reserved-family examples were removed before freezing. These are supplied publisher exports, not independent source re-execution. CCORE already trained on this corpus, so it is retention material.

The new generic API curriculum has **64 train / 16 development** conversations: eight train program families and two development families, with eight wording variants each. Variants are not independent programs. Trusted helper implementations were CPU-tested on an unrelated licensed asset, including real animated GLB export and validation. It covers export calls, flattened finite track values, UUID binding, hierarchy/clip preservation and mixer actions. No Babylon prompt or scene source is included; failure classes informed the choice of generic skills. Brief reasoning summaries align the short examples with the pinned thinking template. Token/mask checks pass on the actual derived tokenizer. New helper targets are 104–177 tokens, within the 4,096-token pilot cap.

The provisional main mixture contains 1,018 weighted training rows / 79 development rows, representing 570 / 79 unique conversations. Repair rows are repeated eight times as explicit row weighting, not presented as extra independent data. This ratio is a starting proposal, not an optimized recipe. Twenty final and four development scene families are reserved by declared aliases; absence from upstream pretraining cannot be established. The exact data and hashes live in the Drive kit and Studio's preparation workspace; raw corpora/weights stay out of Git.

## Mac runtime qualification choice

Official BF16 text conversion completed and the untrained setup audit attached **479,232 trainable parameters** to the final full-attention layer. The original model is preserved. This audit did not run a training forward/backward or optimizer. The pilot configuration uses rank 8, MLX scale 20, batch 1, prompt masking and checkpointing. It is deliberately small; it does not establish the best final quality configuration.

The inspected runtime switches Qwen3.5 recurrent layers to a sequential ops path during training, corroborated by [MLX-LM issue1956](https://github.com/ml-explore/mlx-lm/issues/1956). The source finding motivates starting at the final attention layer and measuring short then long examples. Public issue measurements are from other machines, not this Studio; no foreign performance number is adopted as ours. Expand layer scope or context only after actual cost/quality evidence. No unmerged optimization patch was installed.

Use `python scripts/training_preflight.py` in the task environment for a CPU-only check and `python scripts/run_qualification.py` for a plan-only command. Both are safe to inspect during preparation; neither trains by default. `configs/lora-length-qualification.yaml` and `configs/lora-main-draft.yaml` also ship with training disabled. The current inference helper accepts a frozen `--adapter` directory, records its file digests and explicitly sets evaluation mode. Always use the same frozen runtime/precision/prompt/dependencies for control and adapter, and exit the model process between arms.

`viewer/sprint.html` is the prepared CCORE/Astra two-panel template. Stage actual exports under control/asset.glb and ours/asset.glb with per-arm result.json, preserving raw failures separately. The original historical Qwen/CCORE gallery remains unchanged and available at localhost:8767. A viewer template or a valid supplied training GLB is not evidence of a trained model gain.


## Overnight coordinator dry-tested

The [controller runbook](overnight-controller.md) now documents the implemented phase machine, lock/recovery rules, review protocol and stop conditions. [Dry-test receipt](../configs/controller-dry-test.json): 53 checks passed, including a full simulated 48-hour cycle using CPU-only fake subprocesses. No MLX import, model load, gradient or training step occurred. This tests scheduling/supervision, not trained output quality or hardware throughput.

The current Codex supervisor is required for raw GLB export/playback/visual reviews and the fixed probes. The daemon waits at review gates if the supervisor is unavailable. It never substitutes a fake worker for a failed live model. Default operation prints a plan; no controller is active or scheduled. Live backward completion, finite loss/adapter tensors, adapter-effect/reload and long-example timing still require the later owner start instruction.
