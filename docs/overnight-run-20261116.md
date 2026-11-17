# Overnight experiment — November16–17,2026

Status: active; no demonstrated visual-quality improvement yet. Owner clarified immediate manual start after submitting stale9pm wording. Overall start20:42:39 EST, hard stop07:42:39 EST the next morning. The deadline remains fixed across variants.

| Approach | Evidence so far | Decision |
| --- | --- | --- |
| Thinking-on, reasoning+code replay plus heavily repeated helper snippets | Live qualification passed; first42 main steps completed. Same-prompt showcase exhausted49,152tokens without completeHTML. Diagnostic bellows also exhausted32,768tokens; untouched CCORE completed that probe but has static geometry/track defects. | Stopped; all checkpoints and failures retained. No usable trained GLB or improvement claim. |
| Direct-code, fresh adapter from original CCORE | Reasoning removed intentionally, original final code unchanged;401/47 replay and64/16 repair train/dev; no repeated8x helper weighting. Both new control and adapter use no-thinking mode. Qualification passes complete5327/9648/15909token examples,slowest9.575s/trainstep,29.90GBpeak. Main training active. | Early checkpoint review after two segments, before scheduled intermediate output. |

The unadapted direct-code control itself exhausted49,152tokens with repetitive planning and an HTML skeleton containing ellipses. A closing HTML tag is not a usable scene. Any future Astra result must be compared with the preserved richer historical repairedCCORE reference as well; merely beating a broken fresh control does not establish the requested visual win. All conditions/assistance remain labeled.

A data audit corrected the initial split claim: title/request filtering missed reserved components inside assistant code, and full-title hashing split adjective variants across train/development. Bellows therefore is diagnostic, not clean heldout evidence for the initial mixture. The revised dataset scans title, requests, code and original reasoning, excluding121rows, and groups connected canonical-title/normalized-JS variants. This is explicit lexical grouping, not a guarantee of complete semantic independence or absence from base pretraining. Exact source contents and licenses are retained; no Babylon prompt/output/diagnostic repairs enter training.

The frozen-prefix runtime uses inference kernels for frozen layers0–30 and cuts gradients only at the final full-attention layer input. Guarded LoRA tensors remain exclusively in layer31. Original training-ops numerical equivalence failed strict tolerances and is not relabeled as passed. A separate same-state comparison against ordinary deployed-eval computation passed full-sequence logits,loss,LoRAgradients,one-update and ordinary-loader reload on a short nonzero-adapter case. Long training then passed. This is a documented runtime revision, not a claimed universally identical implementation or unmeasured speedup.

Main segments use immutable adapter snapshots and explicit optimizer/sampler warm restarts. Current Codex reviews actual exports/playback/appearance and controls continuation. No public model publication, spend or deployment is authorized. Current run IDs, process ownership, checkpoints, failures and next actions are recorded in HANDOFF.md; private raw logs/weights stay outside Git.

The common [review harness](../eval/render-harness/README.md) adds shared0/2/4second seeks for repeatable future screenshots. It has syntax checks only until the next actual browser review; it does not manufacture geometry, materials or animation.
