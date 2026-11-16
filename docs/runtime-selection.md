# M3 Ultra runtime selection — 2026-11-16

Verified host: Apple M3 Ultra Mac Studio, 256 GiB unified memory. This session performs the asset comparison; no training.

## Reviewed candidates

| Project | GitHub stars observed | Relevant strengths | Decision |
| --- | ---: | --- | --- |
| [MLX-LM](https://github.com/ml-explore/mlx-lm) | 7,669 | Native Apple Silicon/Metal, Qwen3.5 text inference, fused gated-delta kernels and local conversion/quantization | Qualified and benchmarked; two v2 pairs failed raw export |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | 135,301 | Mature Metal/GGUF runtime, CLI/server and broad deployment support | Selected for final native v3 cross-check; Q8_0 pair also failed raw export |
| [MLX-VLM](https://github.com/Neywa-Labs/mlx-vlm) | 5,852 | Native multimodal inference on Apple Silicon | No image inputs needed here; MLX-LM's Qwen3.5 loader accepts the acquired text component |
| [oMLX](https://github.com/jundot/omlx) | 23,666 | MLX server with continuous batching and memory/SSD prompt caching | Features are more relevant to repeated/concurrent requests than two serial first-pass generations |

Counts are discovery signals, not quality/performance evidence. Runtime compatibility and measured workload matter. Source review used MLX-LM main at `56230fa02b8ff8330daf26dc95c28480423ed5fe`; installed official packages are pinned to MLX-LM 0.32.2, MLX/Metal 0.32.4, Transformers 5.23.0 in a task-owned Python 3.12 environment. No foreign repository was edited or pushed.

## Local short benchmark

Same official Qwen checkpoint, same short prompt, seed, sampler and 223 generated tokens:

| Preset | Decode tokens/sec | Peak reported memory |
| --- | ---: | ---: |
| BF16 MLX | 55.88 | 8.55 GB |
| 8-bit affine MLX, group 64 | 96.34 | 4.69 GB |

These are short observations under an active desktop, not an exhaustive backend benchmark. They used the shared capture gate rather than an exclusive perf lock; sidecars explicitly mark nonexclusive measurements. They do not prove MLX is universally fastest. 8-bit was the faster tested preset, about 1.72× BF16 decode throughput here, and is applied identically to both models. Quantization can affect output, so this is an equal-8-bit comparison, not a full-precision result. Originals remain untouched.

The installed Qwen3.5 loader removes vision weights for text-only use, drops MTP weights and applies the required tensor-layout/norm sanitization. No speculative/draft model is used. Metal GPU is used through the standard native runtime; no CPU-only inference, remote custom model code or persistent multi-model server. Common generation uses temperature 0.8, top-p .95, top-k 40, seed 42, thinking enabled, 65,536 output-token cap and 512-token prefill chunks. No KV compression needed for this host/workload initially; record actual memory growth.

## Execution and ownership

Owner changed daily stream cutoff to 13:00 ET and explicitly ended the stream. Supported `stream_guard.py off` cleared the current guard. The existing daily LaunchAgent was updated from 13:30 to 13:00 and reloaded; live/off-schedule detection remains. No stream process, other engine session or competing loop was stopped. Shared watchdog state is stale, so gpu_slot conservatively caps at two clients; no guard was weakened to raise capacity.

Every conversion/inference process is task-owned and launched through gpu_slot. Run official Qwen first. After it exits, record process disappearance before loading CCORE. Complete process exit releases its Metal model context; OS file cache is not a loaded model. Preview rendering occurs after model inference is finished. Browser previews/viewer are capped at 60 fps, use local dependencies and a loopback-only server.

This is an owner-requested original-output model benchmark. No prebuilt assets or sourced motion are silently inserted into either model's result, and no concept image is generated as an extra hidden input. Both receive the same upgraded task prompt and the same system instruction extracted from the pinned CCORE card. Any import-path adaptation, export repair or asset modification must be recorded separately from untouched model output.

## Native cross-check and final selection

After two failed MLX pairs, use a separate concise v3 art prompt for a native GGUF cross-check. This changes both backend and prompt; it cannot establish which change caused different output. Both native arms receive the same v3 prompt, author system prompt and sampler. CCORE uses its published Q8_0; official original weights were converted with llama.cpp source `4ddf2b9470b44b122e8a5404ae199f04cd03bcec`. Different quantizer provenance is a limitation.

Installed llama.cpp build 10809 rejected the new converter schema (`blk.0.ssm_beta.weight` missing). One initialization failure was retained separately from quality trials. Built an isolated Release/Metal CLI from the matching source; global installation untouched. Native settings: 65,536 context, 49,152 output cap, 1,024/512 batch/microbatch, 8 CPU threads, 99 GPU layers, flash attention, thinking on, seed42 and the same sampler as above. No speculative decoding.

Official completed in 81.00 seconds and exited before CCORE loaded. CCORE completed in 423.55 seconds and exited. Both raw outputs failed; repaired diagnostic exports are documented in [results](comparison-results.md). The faster MLX short benchmark does not imply a valid GLB or rank native throughput. Use MLX Q8 as a promising speed candidate for future repeated tests; keep matching native GGUF as a compatibility cross-check. No universal fastest-runtime claim is established.
