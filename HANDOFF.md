# Astra 3D overnight experiment

Updated November 17, 2026 at 13:55 EST. Repository `Ashen-Builds/qwen-4-for-3d`, branch `Astra`, draft PR #1. **Direction changed on November 17: image-to-3D single assets.** Read [docs/image-to-3d-plan.md](docs/image-to-3d-plan.md) first; it has the goal, stages, resume commands and the Haiku manager brief. The sections below it in this file describe the stopped November 16 to 17 experiment and remain accurate history.

## Current state (November 17, 13:55 EST)

- Goal: a local model turns one concept-art image into a GLB asset (characters first) that a laptop can produce overnight for free. Base is CCORE `Qwen3.5-4B-GLB-3D-Coder`; the scene model is downloaded but parked. Full fine-tune with Adafactor on the M3 Ultra, owner's decision. No training is authorized yet.
- Stage 0 baseline test is built: five Codex reference images, image-capable runner (`llama.cpp` with the vision projector), headless export/validate/render harness, gallery page. One of ten generations ran: original Qwen read the lamp image, wrote a program in 60 s, program crashed (`florishGeo is not defined`), no GLB. The run was stopped at 13:45 because another session's Blender renders held both GPU slots; nine generations remain. Resume commands are in the plan.
- Machine-local, not in Git: `~/work/models/` (original Qwen 3.5 4B at `851bf6e8`, CCORE 3D Coder at `4b9f05f3`), `~/work/models-derived/qwen-bf16`, `~/work/models-native/lmstudio-community--Qwen3.5-4B-GGUF/` (Q8 + vision projector), `~/work/runs/five-asset-image-20261117/`, `~/work/outputs/five-asset-image-20261117/`. Last night's workspace with the CCORE asset model copies, llama.cpp build and datasets is `~/Documents/Codex/2026-11-16/hey-buddy-we-re-going-to/work/`; the owner chose to keep both models.
- Checked today: both CCORE models accept images (Qwen3.5 vision tower, untouched), but no dataset example used one. Scenes dataset (4,146) belongs to the scene model, exports no GLB and animates in the render loop. Asset dataset (3,918) characters are rigid parts, no skins, 2 use bones, about a third animated.
- Nothing is running. No GPU slot is held by this work. Preserve all shared flags.

## Previous experiment: next steps as written at 11:48 EST

1. Read [the final experiment report](docs/overnight-final-20261117.md), [discussion notes](docs/next-eight-hour-discussion.md), and [original reply summary](docs/replies-summary.md). Keep untouched CCORE as the control. Do not treat the repaired Babylon files as raw successes.
2. Inventory the acquired GLB and older Scenes data by source ID, program family, task type and token length. GLB replay supplied the previous candidate; Scenes was archived but not in its main mixture. Select candidate town/architecture/voxel examples and preserve provenance. Do not silently mix their different output interfaces.
3. Build verified additions for layout, villagers/gait, path loops, water/cloud motion and export. Run source code, export/reopen GLBs and inspect motion before accepting targets. Existing CCORE replay alone is not a demonstrated improvement strategy. Keep Babylon and final-test outputs/repairs out of training; reserve new independent tests.
4. Freeze a larger development panel and final evaluation set, with automatic syntax/runtime/export/motion checks and common viewing conditions. Bound review time and retain raw failures; avoid repairing each checkpoint preview during the training window.
5. Settle one training recipe before the next clock: explicit thinking/chat-template/mask configuration, representative-length memory qualification, measured adapter coverage, save/reload and exact documented resume behavior. The previous one-layer adapter worked within measured memory limits; broader coverage remains unqualified. Do not restart old controllers.
6. Prepare an eight-hour schedule with measured step/token/example-coverage targets, bounded evaluations, recovery checkpoints, memory/regression stops and explicit shutdown reserve. Most of the window should be training. This remains unbuilt and must not be described as ready.
7. Wait for a new explicit owner instruction to start the next run. On that turn, recheck machine identity, live process ownership and GPU/streaming flags, then perform the required live checks inside the authorized scope.

## Not done / limits

- No accepted Astra replacement for CCORE and no raw successful Babylon GLB.
- No newly curated full-scene dataset, broad independent evaluation suite, broader-layer training configuration, exact optimizer resume, or validated next eight-hour controller is complete.
- Local GPU status at handoff has no holders/waiters/clients, but effective capture slots are zero and the watchdog is stale. Treat current guard/streaming state as a live boundary; never remove shared flags to make a run start.
- No new training, inference, model download, spend, deployment, public weights or project-main merge is authorized by this handoff.


## Authority and deadline

Owner's “Start now as requested” overrode stale 9 p.m. wording. The actual start was November 16 at 20:42:39 EST. Hard stop November 17 at 07:42:39; shutdown reserve 07:40:39. Intermediate report was written at 04:56:02, after the derived 04:42 milestone but before the original 5 a.m. requirement. Do not reset or extend this window.

Local training/evaluation, routine supervision, Astra pushes and private Drive backup were authorized. No spend, public model weights, deployment, project-main merge or foreign-session takeover. The project PR remains draft and unmerged. Optional critics were restricted to verified free Devin SWE2 or Gemini Hydrogen 4; no substitute model is authorized.

## Current ownership and deliverable

- All three controller roots are stopped: `astra-manual-20261116`, `astra-direct-20261116`, `astra-thinking-clean-20261117`. Private roots are under the workspace sibling `work/sprint-prep/overnight/`, outside this checkout. All final-test and paired-repair model jobs exited and released their GPU slots. Never restart these loops from stale status notes.
- Comparison: `http://localhost:8767/final-review/`. Actual GLBs were inspected during the completed experiment; the browser was not re-tested during this documentation handoff. The server is currently listening on loopback port 8767 (PID 73893, started November 16 at 23:58:31, `scripts/serve_comparison.py --directory ../outputs/babylon-comparison --port 8767`). The viewer defaults to paused/on-demand rendering, with 30 fps playback. Recheck PID identity before managing it.
- Final browser review lease exec 23876 was released after the paused display was verified. A previous review lease expired at 06:00:08 while fixture review continued until about 06:04; those tabs were then closed. This was a process-control gap, not a qualified GPU performance measurement. No model overlap or foreign interference was observed.
- Hardware verified: M3 Ultra, Mac15,14, 256 GiB. Shared watchdog clamps GPU capacity to two. Preserve all flags and foreign sessions. The final owner display does not require any model to remain loaded.
- Before any new run, inspect actual processes, shared GPU status, branch and receipts. No automatic overnight continuation is scheduled.

## Outcome and evidence

Read [the final report](docs/overnight-final-20261117.md) and [sanitized results](eval/results/overnight-20261117.json). Raw responses, source failures and patches remain separate from diagnostic assets. Babylon prompts, outputs and scene-specific repairs were excluded from training. Recorded full-field lexical and family grouping checks found no reserved-task overlap; they do not prove complete semantic independence.

- **Primary Babylon: no improvement.** Fresh CCORE and Astra raw programs failed. Thinking48 passed syntax but failed at runtime. Its mechanical diagnostic exports 2,198,120 bytes, 16 actors and one 106-channel clip, but has static legs, path snaps, sparse composition and a collapsed canal. More clips, actors or geometry are not quality acceptance.
- Thinking72 regressed to a syntax error; its assisted diagnostic also looked worse. It was rejected, and this training variant stopped after two reviewed regressions. No accepted raw Babylon checkpoint exists.
- The original, richer CCORE reference the owner saw remains in the comparison, explicitly labeled repair-assisted. The matched BF16 control is also retained; its repaired file has six villagers and no convincing walking.
- **Final waterwheel, raw outputs:** both export valid animated GLBs. CCORE rotates the wheel about the wrong axis; Astra48 preserves axle rotation. This is a narrow functional win on one task and seed.
- **Final orrery, raw outputs:** CCORE exports a static file with no clips. Astra48 throws `ReferenceError: duration is not defined` before export. Neither fulfills the animated request; Astra regresses export reliability.
- Final tasks and seed were fixed before generation. Both arms used identical input JSON, original thinking mode, BF16 runtime, seed 42, temperature 0.8, top-p 0.95, top-k 40 and 32,768-token cap. Candidate weights were frozen before tests; no training or candidate reselection used final results. Upstream pretraining exposure is unknown.
- A separate one-round FloorSwitch repair development probe used direct C10, **not Thinking48**. CCORE redeclared `exportButton` and failed syntax. C10 passed syntax but preserved `binary:false`; an actual Chrome download was 15 bytes containing `[object Object]`. Both repair attempts failed. No second round or Codex source repair was performed; historical/upstream exposure caveats prevent independent-test claims.

## Checkpoint, data and runtime

Base: `ccore/Qwen3.5-4B-GLB-3D-Coder@8f32a199f8b22fe3157b9c5c8b42b052a0750dd3`; derived BF16 text weights in sibling `work/models-derived/ccore-bf16`. Original CCORE stays preserved. Official Qwen original/Q8 weights were deleted at the owner's request; historical outputs remain.

Final evaluation candidate: `astra-thinking-clean-20261117/checkpoints/job-00005`, SHA256 `553644f2a1d85c06642484f327b657eca0cf8e7516a874ca1182ed6b9720ab66`. It inherits **48 main updates only**, covering 987,295 real target-token exposures. This is a retained candidate, not an accepted replacement for CCORE.

Thinking data manifest `e8404afb752910be8e0ca7e1242d3d62e32fa6f5a31740ae6b0e40d1f8d1acdd`: 399 original reasoning-plus-code replay training rows, 47 replay development rows; fixed ten-row panel and full development pool retained. Helpers were separate qualification work. Original code/reasoning is byte-exact; all 526 unique original rows passed explicit thinking-mode prefix checks without truncation. Six empty-reasoning corrections were excluded from this variant.

Python 3.12, MLX 0.32.4, MLX-LM 0.32.2, Transformers 5.23.0. Final full-attention layer 31 only, rank 16, scale 20, dropout zero, 958,464 trainable parameters, learning rate 3e-6. Frozen prefix stays in evaluation mode and gradients detach at layer 31. Segments warm-start adapter weights but restart Adam and sampling; this is not exact optimizer continuation.

The corrected `exclusive_end_v1` loss excludes one synthetic padding label that the native inclusive-end mask selected. Short and long numerical comparisons passed the declared loss/gradient/update/reload gates. This fix is not established as the cause of earlier degeneration. The two-layer alternative failed system-memory qualification and was rejected. The cached-prefix alternative passed its declared checks but was not adopted; ordinary evaluation and autodiff distinctions remain documented.

## Accounting erratum

Earlier operator notes incorrectly counted ordinary length qualification as inherited main training. `Engine.acknowledge()` clears the warm parent after qualification. Thinking48 therefore inherits 48 main updates, Thinking72 inherits 72, and the initial manual candidate inherits 42. Their qualification weights are separate, discarded work. Frozen final plan v2 is preserved with a separate [accounting correction](eval/final-evaluation-accounting-correction.json).

Direct C10 is different: it inherits 200 main + 3 explicitly adopted external rank-expansion qualification + 99 replay + 12 targeted correction updates = **314**, not 317.

The three controller roots completed **574 optimizer updates** across all attempts and qualification jobs, with **5,353,558 real target-token exposures** after subtracting 477 legacy padding labels. This is total experimental work, not one model's lineage. Successful training-job wall time was 74.65 minutes; failed attempts added 6.19 minutes. The remainder of the night included generation, inspection, data/runtime qualification and publication. At least 19 external numerical-probe updates were separately receipted; that inventory is explicitly nonexhaustive.

Maximum accepted training-job reported MLX memory was 51.269 GB. The rejected two-layer attempt caused substantially greater system memory pressure before being stopped; 51.269 GB is not the experiment's maximum physical-memory usage.

## Validation, publication and next work

Final CPU suite: 98 tests run, 96 passed and two MLX-dependent tests skipped under system Python; Node verifier 8/8 passed. Live MLX numerical/training checks are separate receipts, not inferred from skipped CPU tests. Viewer source syntax and actual four-case Chrome loading/seek/play/pause checks passed; no viewer error was observed beyond an unrelated injected browser-extension error. No engine import certification is claimed.

Final report, artifact evidence and viewer source were pushed to `Astra` at `76ad04ae1a5f70f0c361687bd8572623c682dd90`; local and remote heads matched. Draft PR #1 title/body were updated and read back. Project main remains unmerged. Staged and full 34-commit history custom secret scans passed. The final private wiki update and dated accounting erratum were merged at the checked head. Strict shared-brain sync verified the published revision and byte equality of all four updated pages; lint and staged/full-history/custom secret checks passed. Detailed receipts remain outside the public repository at sibling `work/wiki-final-audit-20261117/publication-receipt.json`. The advisory lock was removed and the authoring checkout is clean.

Private Drive backup is complete: 17 new objects including the index total 425,362,407 bytes. Four archives preserve thinking data/checkpoints/evidence, the failed paired repair, viewer/GLBs/screenshots and operational receipts. Exact remote names, sizes, expected parents and private access were verified. Status Markdown exact text readback passed; JSON index content was unavailable through text extraction, so its verification is metadata-only. Local multipart restoration and the selected adapter hash passed; no remote-byte redownload is claimed. See [sanitized archive verification](configs/overnight-final-archive.json). Private IDs/receipts remain under sibling `work/sprint-prep/final-archive`. The original six-package source archive (216 canonical payloads / 21,484,759,314 bytes) is retained without base duplication; deleted official weights are not claimed present.

Recommended next experiment, requiring a new owner instruction: retain CCORE as the control, curate representative full-scene examples with actual source/export/playback verification, and revisit training coverage/backend within measured memory limits. This run does not prove that a larger dataset dump or more iterations will fix scene quality. Do not train on the final tests or the Babylon evidence.

## Discussion after the run — November 17

Owner asked to keep talking and save preparation notes for a future eight-hour run, without starting training. [Discussion notes](docs/next-eight-hour-discussion.md) record the supplied CCORE collection, actual use of its GLB data, unused older Scenes data, and proposed preparation/verification changes. These are discussion priorities, not launch authorization or an accepted training recipe.

## Reproduce the saved comparison

With pinned Node dependencies installed (`npm ci`), use the CPU-only staging helper:

```sh
python3 scripts/build_final_review.py --out ../outputs/astra-final
python3 scripts/serve_comparison.py --directory ../outputs/astra-final --port 8767
```

Do not start a second server while the existing port is occupied. Rendering/review on the Studio still follows the shared GPU guard. This command stages saved assets; it does not generate or train a model.

## Cross-machine handoff

Source branch: `origin/Astra`; draft PR https://github.com/Ashen-Builds/qwen-4-for-3d/pull/1 remains unmerged. Last discussion commit before this handoff: `6e55f9b` (dataset usage and preparation priorities). This checkout has one worktree and no stashes; no other checkout is claimed by this handoff.

Git carries source, public evaluation GLBs/screenshots/patches and discussion notes. The sibling `work/` and `outputs/` directories are machine-local: original/derived weights, training corpora, adapters, environments, detailed receipts and served gallery do not travel with Git. Checkpoints/data/results were privately backed up through Drive; use its verified index and restore manifests. Keep the selected adapter and original CCORE preserved. Rebuild dependencies and the staged comparison on another machine; heavy model work belongs on the verified Studio. No credential values belong in the handoff; downloading public upstream data does not require a new project secret.

Resume in a fresh session:

> Work in the existing qwen-4-for-3d checkout on branch Astra. Read HANDOFF.md and docs/next-eight-hour-discussion.md, inspect current Git and process ownership, and continue at Start here: next steps. Prepare the next eight-hour experiment; do not start training until the owner explicitly requests it.
