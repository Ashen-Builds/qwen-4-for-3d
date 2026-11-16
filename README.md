# Qwen 4 for 3D

An open project to fine-tune a local Qwen model that's good at **3D modeling and animation in Blender**, mainly by driving Blender through **Blender MCP** tool calls and `bpy` scripts.

Qwen 4 hasn't shipped yet. The plan is to build the dataset, the eval and the training loop now on current Qwen (Qwen3.5 / Qwen3.8), then swap in Qwen 4 when its open weights land.

It started from this question on X by [@ashen_one](https://x.com/ashen_one):

> How hard is it to fine-tune local models? Is it super extensive? Does it take hella tokens and time? When Qwen 4 drops, I want to fine-tune a version of Qwen 4 that excels at 3D modeling and animation (via Blender MCP handling or other stuff)
>
> [source post](https://x.com/ashen_one/status/2122000927418699866)

The post got 111 replies. Everything useful from them is collected here.

## TL;DR: the answer from the replies

| Question | What the replies agreed on |
| --- | --- |
| **How hard is it?** | The training run itself is easy. Use LoRA or QLoRA, not full fine-tuning and not training from scratch. Unsloth was the most-recommended tool. |
| **What's actually hard?** | **The data.** Nearly every useful reply said it. Nobody publishes Blender MCP tool-call traces, so you have to make your own. One split of the effort: about 70% data, 5% config, 25% evals. |
| **Hella tokens?** | No. A few hundred to a few thousand good examples, not millions of tokens. Reported costs: about $3 of Claude to write the examples, about $12 of GPU for a tool-calling LoRA, and about $100 per run on AWS. |
| **Hella time?** | Hours per run on one decent GPU, or on a Mac. Expect days to weeks of data work around it. |
| **Where to start?** | Start today on a small current Qwen (4B–14B). Log successful Blender MCP calls, build a held-out eval, train a LoRA, then port it when Qwen 4 drops. |

## What's in here

| File | What it is |
| --- | --- |
| [`ACTION_ITEMS.md`](ACTION_ITEMS.md) | Checklist in three parts: **today**, this week, and when Qwen 4 drops |
| [`docs/replies-summary.md`](docs/replies-summary.md) | Deep summary of the replies, grouped by theme, with handle attribution and links |
| [`docs/dataset-plan.md`](docs/dataset-plan.md) | How to build the Blender MCP / `bpy` / animation dataset, and the eval |
| [`docs/raw-replies.md`](docs/raw-replies.md) | Every reply verbatim, with handle, likes and link |

## Hardware this targets

- **Primary:** an Apple Silicon Mac Studio (M3 Ultra, 256 GB unified memory) using [`mlx-lm`](https://github.com/ml-explore/mlx-lm) LoRA/QLoRA. That's enough memory for LoRA on small and mid-size Qwen models locally.
- **Alternative:** a rented NVIDIA GPU, or free Kaggle/Colab, with [Unsloth](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide). Unsloth's own docs say its Mac (MLX) training support is "coming", so on a Mac use `mlx-lm` today.

## Status

- [ ] Phase 0: Blender MCP running against a local Qwen, logging every call
- [ ] Phase 1: 50-task held-out eval and a baseline score
- [ ] Phase 2: first LoRA on about 300–1,000 verified traces
- [ ] Phase 3: port the pipeline to Qwen 4 and publish adapters on Hugging Face

## Contributing

Several repliers offered to collaborate. PRs with **verified** Blender tasks (a prompt, the tool calls or `bpy` code, and a pass/fail check) are the most valuable thing anyone can contribute. See [`docs/dataset-plan.md`](docs/dataset-plan.md).

## License

MIT. See [LICENSE](LICENSE). Reply text is quoted from public X posts and attributed by handle. Third-party datasets and models linked here keep their own licenses.
