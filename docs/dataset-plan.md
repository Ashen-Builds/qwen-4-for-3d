# Dataset plan

> "that dataset is the whole project." [@johnroodepic](https://x.com/johnroodepic/status/2122008709681565717)

The goal is a training set that teaches a Qwen model to drive Blender correctly. That means calling the **Blender MCP server's real tools with valid arguments**, writing `bpy` code that runs, and doing modeling and animation steps that produce the intended scene.

## 0. Decide the scope (answering @0xHaley_)

**v1 is Blender tool use, not general 3D knowledge.** It's narrower, easier to verify and easier to eval. Knowledge (docs Q&A) is a small mix-in at most.

| Track | v1? | Why |
| --- | --- | --- |
| A. MCP tool-call traces (multi-turn: prompt → tool calls → results → final) | **Yes, the core** | This is what nobody publishes (@johnroodepic, @waitingforASI_) |
| B. Prompt → single `bpy` script (one shot) | **Yes** | Easy to verify headlessly. BlendNet already has 12k of these. |
| C. Animation (keyframes, drivers, NLA, shape keys, armatures) | Yes, as a tagged subset | The hardest data to find (@yasu0x1), so build it deliberately |
| D. Docs Q&A (OpenBlender_Train) | ≤10–20% mix | Grounds API names. Too much of it teaches chatting instead of doing. |
| E. Vision (viewport screenshot → next action) | Later | Needs a VL fine-tune. The before/after timelapse idea (@xxsaissa) goes here. |

## 1. Sources, in priority order

### 1a. Your own logged traces: the main source

The loop that @johnroodepic, @crum7355608 and @grok all described:

1. Run Blender with the Blender MCP add-on, and run an MCP client against a **local** Qwen (or a strong hosted model for bootstrapping, the "teacher").
2. Give it a **tight system prompt**: the tool list, two worked examples, and short rules.
3. **Log every step**: the user prompt, tool name, args, tool result, and the scene state before and after (`get_scene_info`), plus a viewport capture at the end.
4. Label each episode **accept / reject / correction**.
5. Keep only verified-good episodes for SFT. Keep the rejected ones too: they're preference/RL data later.

**Our notes on the upstream server (checked 2026-11-16):** [`ahujasid/blender-mcp`](https://github.com/ahujasid/blender-mcp) exposes tools including `get_scene_info`, `execute_blender_code`, `viewport_capture`, `search_assets`, `import_asset`, `generate_3d` and `record_trajectory_feedback`. Its built-in trajectory recorder writes **only to the maintainers' Supabase, with "no local/JSONL storage"**, and it's tied to its telemetry consent. That means:

- **Don't rely on it for your dataset.** Log locally yourself, either in the MCP client or with a thin MCP proxy that tees every request and response to `traces/*.jsonl`.
- Decide on purpose whether you want telemetry on. The server has a `disable_telemetry` tool, and a private project probably wants it off.
- Snapshot the **exact tool schemas** from the server version you train against (`tools/list`) into `schemas/blender-mcp-<version>.json`. Training data has to match the tool names and args the model will see at inference (@waitingforASI_).

### 1b. Public datasets: bootstrapping and mix-ins

All confirmed on Hugging Face 2026-11-16. Check each license before redistributing.

| Dataset | Size | License | Use |
| --- | --- | --- | --- |
| [`FreedomIntelligence/BlendNet`](https://huggingface.co/datasets/FreedomIntelligence/BlendNet) | 12k instruction→`bpy` (2k human-annotated) | Apache-2.0 | Track B. Re-run each script headlessly and keep only those that execute. |
| [`YipengGao/3DCodeBench`](https://huggingface.co/datasets/YipengGao/3DCodeBench) | 10k–100k procedural 3D code | MIT | Track B and eval ideas. Its card warns some scripts don't execute, so filter them. |
| [`nolabs/deepfabric-blender-mcp`](https://huggingface.co/datasets/nolabs/deepfabric-blender-mcp) | 1k–10k synthetic MCP rows | not stated | Track A *format reference*. Check that the tool names match your server, and don't redistribute until the license is clear. |
| [`PGCRYPT/OpenBlender_Train`](https://huggingface.co/datasets/PGCRYPT/OpenBlender_Train) | 31.4k docs/API Q&A | Apache-2.0 | Track D mix-in |
| [`ccore/ThreeJS-3D-Scenes`](https://huggingface.co/datasets/ccore/ThreeJS-3D-Scenes) | three.js scenes | see card | A format reference from a successful 3D Qwen fine-tune (@SandeshRajx) |

### 1c. Synthetic generation with a teacher

- A strong model writes prompt→script pairs. **Every script must run headlessly in Blender and pass a check** before it goes in. (@vishalskotak spent about $3 of Claude on a small tool-calling set. @BarryDeenTech suggested the same.)
- Vary the prompts on purpose: primitives, modifiers, materials, geometry nodes, rigging, keyframes, cameras and lights, and render settings.
- Distillation, as @Vidyut put it: let the big model work in Blender, save the scripts that worked as reusable procedures, then train the small model to call them.

### 1d. Scraped `bpy` code (@amybuildsAI)

Take permissively licensed add-ons and snippets (MIT/Apache/GPL; GPL needs care if you redistribute) and have a teacher write the matching natural-language prompt. Keep only scripts that run on the target Blender version.

## 2. Verification: what makes a sample "good"

A sample only goes into training if **all** of these pass:

1. **It runs.** `blender --background --factory-startup --python sample.py` exits 0 with no Python traceback. For MCP traces, every tool result has no error.
2. **The state is right.** A per-task assertion over scene state, e.g. "an object named `Chair` exists, has ≥4 leg children, and its bounding box height is 0.8–1.1 m", or "the `Cube` location has keyframes at frames 1 and 60".
3. **It looks right** (optional for v1). A viewport render is spot-checked by a human or a VLM judge.
4. **It uses the schema.** Tool names and args validate against `schemas/blender-mcp-<version>.json`.

The same checks become **RLVR rewards** later (@crum7355608, @robeotx, @tensorfiend).

## 3. Format

For Mac training with `mlx-lm`, write `data/train.jsonl`, `data/valid.jsonl` and `data/test.jsonl`, one JSON object per line.

**Track A (tools format, from the mlx-lm docs):**

```jsonl
{"messages":[{"role":"system","content":"You control Blender through MCP tools."},{"role":"user","content":"Add a red cube 2m tall and keyframe it rising from z=0 to z=3 over 60 frames."},{"role":"assistant","tool_calls":[{"id":"c1","type":"function","function":{"name":"execute_blender_code","arguments":"{\"code\": \"import bpy\\n...\"}"}}]}],"tools":[{"type":"function","function":{"name":"execute_blender_code","description":"Run Python in Blender","parameters":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}}}]}
```

**Track B (chat):**

```jsonl
{"messages":[{"role":"user","content":"Write a bpy script that makes a low-poly tree."},{"role":"assistant","content":"import bpy\n..."}]}
```

- Train with `--mask-prompt` so loss is only on the assistant's output.
- Keep each sample **under about 16K tokens** (@SandeshRajx). Split long sessions into steps.
- If you want to keep Qwen's reasoning ability, Unsloth's Qwen3.8 guide says to mix in reasoning-style samples (they suggest ≥75% reasoning data if preserving thinking matters).

## 4. Target sizes

| Milestone | Verified samples | Source |
| --- | --- | --- |
| First LoRA ("know within a day", @fufeng1688) | **300–500** Track A + ~1–2k Track B | Own traces + filtered BlendNet |
| v1 | 1k–10k (@grok's range) | + synthetic, + animation subset |
| Held-out eval (never trained on) | **50 tasks** to start, growing to 200 | Hand-written, see below |

## 5. Eval set (build it before training: @EternitiesAI)

- **50 tasks** in `eval/tasks.jsonl`, each with: a prompt, the starting `.blend` (or empty scene), and a Python assertion over the final scene state.
- Mix: 15 modeling, 10 materials/shading, 10 animation/keyframes, 5 rigging, 5 scene/camera/light, 5 multi-step "build a small scene".
- Metrics: **pass rate**, **tool-call validity rate**, **average tool calls per task**, and **error recoveries**.
- Run it on the base model first (that's the baseline), then on every checkpoint (@MikeBrave_Maker). When Qwen 4 lands, run the stock model too: if it's already "really solid at 3D" (@snapsnocaps), you'll see it.
- Never let eval prompts or near-duplicates leak into training. Dedupe by normalized prompt.

## 6. Repo layout to grow into

```
schemas/   blender-mcp-<version>.json   exact tool list you train against
traces/    raw/*.jsonl                  everything logged (gitignored if large)
data/      train.jsonl valid.jsonl test.jsonl
eval/      tasks.jsonl  checks/*.py  run_eval.py
scripts/   verify_sample.py  build_dataset.py  proxy_logger.py
```
