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

## Readiness before the clock starts

Downloaded files alone are not training readiness. Still unbuilt: verified new task/response examples for the specific weaknesses, family-level train/development/final splits, exact loss-mask/length checks, a proven Qwen3.5 hybrid-model LoRA backward/save/reload cycle at representative lengths, and the safe checkpoint/export evaluation controller. Do not claim an improved 7 a.m. asset if these gates fail. Launch checks and the short pilot occur only after owner start authorization; no model or gradient job runs during current data preparation.

Before an overnight run, record immutable model/data/template/runtime revisions; selected adapter layers/trainable parameter count; full sequence-length distribution and target preservation; actual memory, seconds/step and tokens/step; checkpoint-save/reload behavior; recoverable optimizer/RNG/data position; and a tested stop/streaming path. Freeze rank, learning rate, batch/accumulation, warmup and step/token budgets from the pilot rather than pretending unmeasured hyperparameters are ready. Start with ordinary LoRA if the verified BF 16 path fits; QLoRA is a measured alternative.

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

Four additional pinned sources acquired and digest-verified: CCORE GLB dataset 1,030,742,497 bytes; BlendNet 22,283,412 bytes; Bioinspired3D 12,429,105 bytes; Pixel Atlas reference selection 482,979,530 bytes. See [inventory](../configs/sprint-data-inventory.json) and [static data audit](../configs/sprint-data-audit.json). They supplement the already acquired CCORE scenes and isolated 3DCodeVerse research copy. Original official Qwen weights remain deleted.

Static inspection: CCORE 3,918 conversations,3,501 train/417 validation, no exact ID or whitespace-normalized response overlap, all responses contain a closing HTML tag. This does not certify code correctness or family independence. BlendNet 12,059 rows, Bioinspired3D 4,557 rows, Pixel Atlas 6,194 finished asset rows. The latter is reference geometry, not text-to-code demonstrations.

A deterministic 65-example tokenizer-only sample has median 18,424 rendered tokens, maximum 46,376;64/65 exceed 8,192 and 4/65 exceed 32,768. [Length sample](../configs/sprint-length-sample.json). These lengths include reasoning when used by the pinned template. Full dataset/mask qualification still remains; do not silently truncate. No model weights or GPU were used for the audit.

The direct Codex Drive connector passed a 143-byte upload with identical-byte readback and a 34.7 MBZIP upload. Large file routes expose 100 MiB and 512 MiB limits; use 96 MiBnumbered parts with SHA 256 manifests. `scripts/reassemble_archive.py` verifies every part and the whole ZIP before creating the destination; it never extracts or executes data. A 34.7 MBround-trip reassembly passed. Archive transfer is **partial**, not complete: a supplement ZIP and some research/CCORE parts reached Drive; model backup, other parts and final checksum/readback completion remain. No continued transfer worker is left running. Do not treat incomplete ZIP parts as usable datasets. Keep private folder/file identifiers in the private receipt/wiki.
