# Pipeline and comparison plan

Updated 2026-11-16. This is a plan, not an active trainer or automation.

## Objective and current authority

Extend a small CCORE 4B specialization to produce useful game-importable 3D assets locally, with GLB as the primary exchange format. Preserve existing Three.js strengths; introduce Blender Python/MCP where it improves the outcome. Low-memory inference is a measured release goal, not a claim based solely on weight size.

Owner subsequently authorized local tests, improved prompts, Chrome previews and optional CLI critiques. These are now completed as documented in [comparison results](comparison-results.md). No training or deployment authorized by this comparison task.

## A/B/C comparison

| Arm | Checkpoint | Purpose |
| --- | --- | --- |
| B, second | `ccore/Qwen3.5-4B-GLB-3D-Coder` | Existing 3D specialization |
| A, first | `Qwen/Qwen3.5-4B` | Official upstream before CCORE's specialization; already generally post-trained |
| C, future | B plus our tracked LoRA | Measure additional improvement; absent until actually trained |

Pin revisions in `configs/model-snapshots.json`. CCORE identifies the upstream repository, but the inspected GLB materials do not specify its exact historical training-input commit. Do not claim a byte-for-byte reconstruction of that historical input. Do not substitute `Qwen3.5-4B-Base` or a community quantization for B without changing the declaration.

Use identical asset/system prompts, a common runtime/effective precision, sampling, seed, context/output/time limits and dependency bundle. Save exact rendered input, tokenizer/template/config hashes and settings. CCORE has FP32 text weights; Qwen's original precision differs, so common compute precision must be selected during the later preflight. Static inspection found matching BPE vocabulary and identical chat-template text, but different added-token records and normalized tokenizer JSON. Tokenizer file-byte differences are not automatically semantic differences; runtime behavior still needs qualification. Qwen has 15 extra `mtp.*` tensors absent from CCORE; disable multi-token prediction/speculative decoding for the controlled baseline and record the backend handling.

The first demonstration uses one attempt per arm with no repairs. A single result is qualitative evidence, not a general ranking. Repeat later across predeclared seeds and independent tasks. Compare repair-assisted results separately with equal budgets. Preserve every raw output, truncation, timeout and failure; never polish one arm invisibly.

## First asset: animated voxel Babylon marketplace

Owner wants a super-detailed voxel village/town inspired by ancient Iraq/Babylon: people walking and trading in a marketplace, flowing water, moving clouds and animated components. Canonical request: `eval/prompts/babylon-marketplace-v3.txt`. It replaces the earlier suggested static treasure chest. Primary v3 native results and earlier v2 failures are retained; see results.

Use the documented CCORE system instruction from its pinned downloaded README. Keep the request concise while judging all requirements below. Source retrieval must not improve only one arm: this benchmark explicitly requests each model's own generated voxel output. Any later sourced assets/motion must be declared and offered under identical conditions to every arm.

This whole-town animation is an intentionally demanding owner-selected task. Do not replace it silently with a simpler prop or score a static thumbnail as animated success. Preview motion and exported-file motion are separate results. JavaScript shader/time loops do not automatically become glTF clips; inspect exported animation and reimported playback. Water/cloud effects may need exportable geometry/clip representations or documented renderer-specific materials. Record what survives.

## Qualification before model testing

1. Confirm manifests and index/shard/header integrity without loading remote custom code.
2. Choose a backend supporting Qwen3.5's hybrid architecture and original checkpoints; qualify short load/generation only after the owner starts testing.
3. Select common precision and limits from measured memory. Primary native limits and completed status are recorded in the comparison config.
4. Check session ownership, desktop health, stream flag and shared GPU slots. Run models serially with task-owned processes. Never unload another session's model or bypass a tripwire.
5. Qualify a controlled local browser/export runner and common local dependencies. Log URL substitutions separately. Constrain external network, filesystem and process access from generated code.

## Evidence and rubric

Retain raw response/termination reason, complete source, dependency/runtime versions, elapsed time, token counts and peak memory. Save fixed-camera/time preview views, GLB checksum, structural report, reimported views and playback evidence.

| Dimension | Evidence |
| --- | --- |
| Request coverage | Voxel Babylon-inspired market, buildings/stalls/traders, walking people, water/cloud motion and small details |
| Export reliability | GLB created, valid structure, nonempty meshes, finite transforms and resolved textures/materials |
| Export fidelity | Parts, appearance, scale, hierarchy and requested components after reimport |
| Motion | People/water/cloud movement in preview and exported/reimported playback; clipping, sliding and looping |
| Efficiency | Geometry, primitives/draw-call proxies, materials, textures, file size, generation time/tokens/memory and playback |
| Destination fit | Browser first; separately qualify Godot, Unreal, Unity and Roblox imports in owned projects when authorized |
| Repair burden | Retained one-shot output; count/time of later equal-budget correction steps |

Declare acceptance thresholds after hardware/backend profiling and before comparing trained improvements. Do not redefine passing to fit an attractive output. Add a broader held-out suite before claiming general improvement.

## Critique and orchestration

Owner clarified that optional critics must use the subscription CLIs: **Gemini Hydrogen 4 only** and **Devin SWE2 only**. Do not substitute Carbon or a paid Devin model. Exact CLI model IDs, available tools/accounts and any data-transfer requirements still need qualification before use. They are candidates, not active workers or confirmed providers. Devin CLI swe-2-high was verified listed Free and used for read-only sandboxed code critique. Gemini was not called.

Run deterministic file/scene checks first. Then provide anonymous equal-condition views, playback and rubric to an authorized critic; hide model labels, preserve per-dimension scores/disagreements, and have the current agent inspect each generated evaluation output. Randomize presentation independently of serial run order. Screenshots cannot verify export animation. Calibrate critics against owner/current-agent judgments rather than treating preferences as ground truth.

## Future bounded overnight goal

Start after inspected baselines and an explicit training-goal instruction. Do not create a standing automation to watch a run; monitor in the active task/goal.

Before launch, fix training mixture/rights, held-out families, run budget (time/steps/tokens/checkpoints and external dollars), GPU concurrency, eval interval, stop conditions, retention and rollback. Test one short train → export → evaluate cycle before unattended work. Verify listening tools have prior OS permission and cannot raise dialogs.

1. Curate licensed verified examples/corrections on training families. Keep the Babylon prompt, its outputs/corrections and near-duplicates out of training.
2. Lint chat templates, loss masks, sequence lengths, truncation and overlap; deduplicate program families beyond text similarity.
3. Train ordinary LoRA on untouched CCORE with an explicit compatible configuration. Rank/rate/optimizer/length require a measured pilot, not invented CCORE reproduction settings.
4. At fixed checkpoints generate equal-budget eval batches and validate exports. Inspect every output in those batches, not every gradient step or training row.
5. Optional authorized critics add blinded scores. Select checkpoints on development evaluation; retain a separate final held-out test.
6. Stop on regression, repeated failure, invalid exports, memory/GPU/desktop tripwires or exhausted budget. Never mutate holdouts or repeatedly relaunch to obtain a pass.
7. Compare selected LoRA against A/B, then fuse/quantize and repeat tests before publication. Publishing models or merging application work still needs its scoped authority.

## Sources and tooling

CCORE GLB data already helped create B, so testing B on it does not establish generalization. Use independent tests. BlendNet/Bioinspired3D and our verified trajectories can supplement after rights, overlap and version checks. Isolate noncommercial 3DCodeVerse data from permissive-release mixtures unless terms are resolved.

Neyra lint/comparison/merge/provenance patterns are useful, but its inspected defaults (512 training / 32 evaluation output tokens, greedy decoding) do not fit long-output assets. Use artifact scoring rather than final-text matching. No Neyra runtime qualification is claimed.
