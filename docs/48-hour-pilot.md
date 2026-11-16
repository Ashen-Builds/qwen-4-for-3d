# Proposed 48-hour CCORE LoRA pilot

Status: planning only; training has not started. Goal: a measurable improvement over untouched CCORE in valid animated GLB generation while preserving its visual strengths. A substantial visual improvement is possible, not guaranteed by elapsed training time. Small-model inference speed measured previously is not training throughput.

## Sequence and gates

| Elapsed target | Work | Required evidence |
| --- | --- | --- |
| 0–6 h | Freeze independent tasks and acceptance rules; curate a small licensed, working training set | Family-level deduplication; no Babylon/near-duplicates; successful scene/export checks; original CCORE scores on the same unseen tasks |
| 6–12 h | Qualify exact CCORE text loader, adapter targets, masking and short train/save/reload cycle | Finite losses/gradients, adapter actually changes intended parameters, memory/seconds per step at representative sequence lengths, matching reload output |
| 12–30 h | Bounded LoRA run with periodic checkpoint evaluation | Fixed time/step/token caps from pilot; no silent truncation; preserve baseline replay examples; stop on regression, export failures or GPU limits |
| 30–42 h | Compare checkpoints and correct data on separate development families | Equal prompts, seeds, backend, limits and assistance; retain every failure; optional authorized CLI critics |
| 42–48 h | Final held-out comparison and visual record | Untouched CCORE versus selected adapter, raw pass rates, animation coverage, appearance, speed and repair burden; add third result without replacing prior baselines |

These are work budgets, not promised completion times. Data validation and long output sequences may be the main bottlenecks. Do not train on a pile of unchecked files or repeatedly retrain against the final holdout. Keep an unused final test separate from development tasks/checkpoint selection. The already seen Babylon example can illustrate output later, but cannot be the sole evidence or tuning target.

Proposed acceptance rule to freeze before the pilot: on a 20-task independent final set with two predeclared seeds per task, improve raw valid-export rate by at least 15 percentage points over CCORE, preserve requested animation more often, and show no material visual-quality regression under blinded review. Forty paired generations are a small estimate; report task-level outcomes and uncertainty, not just the best screenshot. If baseline export rate is already near the ceiling, revise the predeclared primary metric before training. This is a practical decision threshold, not a statistical significance claim. If evaluation cannot fit the budget, report an incomplete pilot rather than manufacture success.

## Runtime and data

Use original CCORE weights as immutable source. On the verified 256 GiB Studio, test ordinary LoRA on a compatible BF16 text conversion first; compare a quantized-base adapter only if measured throughput/memory justifies it. Exact Qwen3.5 hybrid-layer training/backprop support and target selection remain unqualified; successful inference does not prove training works. A small train/save/reload gate is mandatory. MLX-LM supports LoRA/QLoRA and prompt masking, but generic documentation is not proof of this exact checkpoint/config. See [official guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md).

Prioritize verified complete exports, valid animation tracks and varied scene decomposition, with enough original-style examples to avoid visual regressions. Reusing CCORE's existing training dataset alone may add little new skill. Sources require provenance, rights, code execution/export checks and family splits. Keep noncommercial 3DCodeVerse outside a permissive release mixture until terms are resolved. Teacher or sourced-asset examples need explicit lineage and must not leak into generated-only evaluation.

No external spend, deployment or model publication is authorized by this plan. GPU slots and streaming limits still apply. Optional critics remain Devin CLI SWE2 free models or Gemini CLI Hydrogen4 only. Critique opinions supplement file/runtime/visual evidence.

## Reuse for Qwen4

Checked 2026-11-16: [official release log](https://docs.qwencloud.com/changelog/models) lists Qwen4-Max today. An authenticated-free public Hugging Face Hub API query for official author Qwen and search Qwen4 returned no models. A downloadable Qwen4 4B/8B and its release date are therefore unverified; do not schedule around an assumed release. [Official model catalog](https://huggingface.co/Qwen/models).

Reuse validated data, task splits, prompt contracts, exporter, verifier, viewer and scoring. Requalify tokenizer/chat template, architecture, adapter modules, runtime, license, precision and training throughput for Qwen4. A CCORE/Qwen3.5 LoRA is architecture/checkpoint-specific and cannot be assumed to load on Qwen4. New Qwen4 weights need new adapters; additional distillation may be possible only after quality and rights checks. Future visual comparison should keep model generation/size differences explicit.
