# GLB asset direction and Neyra review — 2026-11-16

## Owner direction

Prefer building on CCORE's existing 4B specialization, with low-memory local inference as a product goal. Deliver importable 3D assets for browsers, Godot, Unreal, Unity and Roblox. GLB is preferred, with other interoperable formats acceptable. Blender MCP is optional; exported asset quality and portability are the goal. Research only: no training or model-weight downloads authorized yet.

## Better-matched CCORE candidate

[ccore/Qwen3.5-4B-GLB-3D-Coder](https://huggingface.co/ccore/Qwen3.5-4B-GLB-3D-Coder), reviewed revision `8f32a199f8b22fe3157b9c5c8b42b052a0750dd3`, is a different release from the earlier scene-generation checkpoint. Its card describes a Qwen3.5-4B specialization generating low-poly asset HTML/Three.js code with preview and Export GLB. The recommendation is to evaluate this as the starting checkpoint, not rebuild its specialization from stock Qwen. Keeping stock Qwen as an optional comparison does not require using it as the training base.

Continue training by attaching a fresh compatible LoRA to CCORE's full checkpoint, preserving the original for comparison. Future merging/quantization must be tested; exact MLX/checkpoint compatibility has not been established here. A model outputs executable code that constructs/exports the asset, not binary GLB tokens.

Hub metadata only: Q4_K_M is 2,708,804,128 bytes, Q8_0 is 4,482,402,848 bytes; five original Safetensors shards total 17,490,122,528 bytes (FP32 text + BF16 vision according to the card). These are storage sizes, not peak inference RAM. The nominal 4B model includes an optional vision companion; text-only distribution can avoid requiring that companion. Card recommends thinking and long generations (average ~20K tokens, training examples up to 72K); shorter, cheaper generation is an improvement target, not an established capability. Nothing was downloaded beyond source/docs metadata.

Matching [ThreeJS-3D-GLB-Assets](https://huggingface.co/datasets/ccore/ThreeJS-3D-GLB-Assets), revision `276821245d5714b95571465569ed5b844ac6adc7`: 3,918 examples, 3,501 train / 417 validation, 40 domains. Publisher reports all examples rendered and GLB-validated, with conversations, previews and meshes. Dataset declares MIT to extent of publisher rights; model declares Apache-2.0. Not copied in this session. Original scene dataset already copied is a separate resource. Use new independent tests rather than claim improvement from scoring the checkpoint on its own training data.

## Neyra: selected reusable components

Repository [noah-thing/neyra-protocol](https://github.com/noah-thing/neyra-protocol), inspected at `2d4c0bb4776664d4c6bc2c837ed01cc762d1dade`, Apache-2.0. Source cloned and read only; not installed, imported or executed. No runtime compatibility or performance claims.

- `tune lint`: inspect chat template/token IDs, assistant loss masks, end tokens, truncation, repeats and validation overlap. Useful before training; cannot establish semantic/visual quality or program-family independence.
- `tune verdict`: compare starting model, few-shot prompting, adapted model and quantized files; per-case results, bootstrap intervals and small regression checks. Supports `python:FILE` custom scoring. A generated-code/GLB validator can potentially be integrated as a scorer, but the default final-text evaluation is not a live multi-turn asset agent benchmark.
- `check`, `hop`: verify adapter merges and locate conversion/quantization pipeline mistakes. Useful for a downloadable small-model release.
- Manifests/digests and bounded experiment/holdout accounting: reusable reproducibility patterns. Cryptographic identity/integrity does not prove asset quality.
- `tune train`: wraps MLX-LM rather than providing a new training algorithm. Reviewed code refuses quantized bases and supports ordinary LoRA, not QLoRA. Its exact-patch arithmetic differs from an ordinary MLX fuse by rounding; choose and verify the artifact pipeline explicitly.
- Direct neuron/fact edits and loop patches are not demonstrated substitutes for training new modeling skill. Defer them.

Important source-level limits: `src/neyra/cli.py` defaults training to 512 tokens and verdict outputs to 32 tokens, with greedy evaluation; these do not match CCORE's long, sampled generation recipe. `docs/limits.md` says verdict needs Torch, but the dedicated verdict guide and backend code include MLX; verify actual installed behavior rather than trusting the older summary. Neyra remains alpha and its training demonstration is one small style task. Do not run training with default truncation or override a failed lint simply to proceed.

## Proposed architecture and evaluation (not implemented)

Prompt → local 4B CCORE GLB checkpoint → Three.js code → controlled local execution → GLB export → structural/visual/budget checks → target-engine import. Bundle Three.js/exporter dependencies locally so first-generation pages do not require CDN access for an offline product. Blender can add optional repair, UV/optimization, rigging, format conversion and export work; forcing a new Blender tool interface at the outset could discard the checkpoint's existing output strengths.

Validate actual exported files separately from browser previews: geometry, scale, pivot, transforms, materials, textures, naming/hierarchy, triangle/draw-call/file budgets, and applicable animation/rig checks. Static low-poly props and modular pieces are an initial recommendation, not an owner restriction. Runtime JavaScript motion must be converted to exported animation clips; gameplay logic, collision, controller behavior and platform-specific avatar requirements need separate integration.

Official import references reviewed: [Godot](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html) supports glTF/GLB; [Unreal](https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-gltf-files-into-unreal-engine) supports glTF/GLB; [Unity glTFast](https://github.com/Unity-Technologies/com.unity.cloud.gltfast/blob/main/Packages/com.unity.cloud.gltfast/Documentation~/ImportEditor.md) supplies editor import; [Roblox importer](https://create.roblox.com/docs/studio/importer) explicitly describes GLB/glTF hierarchy and FBX/OBJ support. These are documented routes, not imports tested in this session. Robust import is not identical rendering or automatic game readiness.

Future training should target measured failures: export reliability, clean geometry, engine-specific budgets, preserved materials, requested parts and fewer/shorter repair steps. Retain selected original examples to monitor preservation of earlier ability; keep independent tests and provenance/license separation. Keep the noncommercial 3DCodeVerse aggregate outside a permissive release mixture unless applicable terms are resolved. Train on Studio; evaluate Q4/Q8 distribution on declared lower-memory device targets before making RAM or speed claims.
