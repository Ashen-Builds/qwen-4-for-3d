# Authorized overnight window — November 16–17

The active owner's **Start now** instruction overrides the stale 21:00 text in the attachment. The experiment began **20:42:39 EST November 16** and must stop by **07:42:39 EST November 17**, eleven hours including qualification, pauses and reviews. The direct-code revision retains this original clock; it does not extend the deadline.

Current run: `astra-direct-20261116`; config: `configs/overnight-correction-phase.json`; private authorization: `work/sprint-prep/owner-start-correction-20261117.json` under the workspace, outside this checkout. Its scope is `manual-overnight-sprint`. This record documents existing owner authority and the exact config hash; it grants no extra scope. The earlier timed and reasoning-heavy variants are stopped. There is no recurring automation. Codex supervises routine reviews.

The intermediate comparison is due **04:42:39 EST November 17**, with its generation window beginning 03:42:39. Main training drains by **06:27:39**; the final generation window begins 06:42:39. Owned compute shutdown begins **07:40:39**, preserving the configured **120-second shutdown reserve** before the **07:42:39** hard stop. These times derive from the active config's numeric schedule fields. Historical 48-hour fixtures are regression coverage only.

## Controller operation

Live direct-code qualification has passed: ten short backward steps, ordinary adapter-effect/reload verification, and three complete-code length probes. Three main segments have completed 300 training steps. The first evaluation at200steps produced complete-length HTML but failed raw JavaScript syntax; no successful raw Astra GLB or visual improvement is established. A separately qualified rank16/lower-learning-rate continuation now starts from the200-step parent; the300-step follow-up was rejected for degeneration. All earlier counts and checkpoints remain recorded. Use the current Codex session as supervisor/reviewer. Completed HTML, lower loss and a repaired diagnostic do not prove raw export success.

## Sequence

Frozen matched CCORE generation → Codex baseline review → ten short training steps → adapter-effect/reload check → three complete length probes → Codex qualification review → bounded training segments → checkpoint generation and review at configured milestones and supervised early checks. The direct-code variant uses no-thinking generation for both fresh control and adapter, with fresh adapter initialization rather than resuming the stopped variant.

The live gates check completed backward steps, finite losses and adapter tensors, nonzero learned B matrices, measured step time, and adapter-effect/reload logits. Gradient norms are not separately instrumented. These qualification gates passed for the current variant; exported-asset quality remains a separate review gate.

Each training segment uses at most 25 minutes including resource wait, respects the shared GPU slot, saves every step and copies a valid checkpoint into an immutable directory. Segment iteration count is estimated conservatively from the slowest measured step. A segment resumes **adapter weights only**; Adam state and sampling restart. This is an explicit warm-restart experiment, not bit-exact optimizer continuation.

The current fixed layer scope and data/model/runtime fingerprints cannot silently change mid-run. Source/data bytes, library versions, tokenizer metadata and model-weight size/mtime are checked before jobs. A changed input requires a stopped, reviewed/rebaselined run.

## What is autonomous

The controller runs phase ordering, resource waits, safety stops, checkpoints, artifact packets and clock deadlines. **Codex must remain active to inspect and acknowledge review packets**, including source/export checks, GLB validation, playback/appearance and the fixed development probes. With no reviewer, it waits safely. Routine reviews do not require waking the owner. Optional CLI critics remain subject to the owner's model restrictions.

The independent final suite is a supervisor responsibility: freeze a candidate before final testing, reserve an allowed compute window, and do not use those scores to tune subsequent checkpoints. If the eleven-hour window is exhausted, report incomplete evaluation and stop owned compute. Do not extend this run into daytime or another night.

## Inspect or resume the authorized run

The owner has already authorized this run. Do not launch a second controller or resume either stopped earlier variant. Inspect current process ownership, the run lock and live worker state before any recovery. The following command reads the current variant's status and launches no worker:

```sh
../work/qwen-eval-env/bin/python scripts/overnight_controller.py \
  --config configs/overnight-correction-phase.json \
  --run-id astra-direct-20261116 --status
```

Recovery with `--run --resume` requires the same explicit config/run ID and private authorization file. It refuses a recorded live worker or orphan and cannot take over another session's process. Default invocation without live flags is plan-only, but its defaults refer to the older timed configuration; always select this variant explicitly.

## Review protocol

Read `work/sprint-prep/overnight/RUN_ID/review-packet.json`. Review files name its exact `packet_sha256`; stale packets cannot advance. Queue a reviewed JSON using `--ack-review FILE --authorization-file FILE` (the owning controller applies it under its lock).

A baseline review needs `baseline_frozen: true`; a qualification review needs `live_gates_passed: true`, backed by the worker's successful checks. Baseline/milestone reviews record `raw_export_status: "pass" | "fail"` and `evidence: [{"path": "relative/path", "sha256": "..."}]`. Evidence must exist inside this run and match its hash. For a raw pass, include `glb_file`, `validation_file` and the actual validator receipt. A milestone also requires `export_and_visual_reviewed: true`, an explicit boolean `regression`, and `glb_validation_errors: 0` plus `assistance: "none"` before `accept_checkpoint: true`. Repaired diagnostic exports cannot be promoted as raw passes.

Decisions are `continue`, `retry` or `stop`. A failed worker cannot be acknowledged as successful. One diagnosed retry is permitted; two worker failures stop further launches. Two consecutive reviewed regressions stop training and retain the best accepted checkpoint. Save the scorecard and screenshots/playback evidence before acknowledging.

## Safety and timing

- Streaming, shared GPU pause and this run's `PAUSE` file stop owned compute. Neither global flag is removed by this controller. GPU gate code75 is an availability hold with a five-minute cooldown, not a model crash.
- This run's main-training cutoff is **06:27:39 EST November 17**. The **120-second** deadline reserve starts owned-compute shutdown at **07:40:39**, before the **07:42:39** hard stop. There is no next-night resume under this authorization; availability markers never extend the deadline or override streaming/global pause.
- The fixed hard deadline includes pauses and evaluation. No new heavy job starts after it. Reports say unchanged, missing or unreviewed when appropriate; no fabricated GLB is created.
- The parent monitors reported memory, owned-group RSS and reclaimable system memory. The live training worker sets a 160 GiB **advisory** MLX memory limit and 2 GiB cache; this is not an OS-enforced cap. Live memory/throughput qualification remains mandatory.
- Stop uses SIGTERM, waits up to 60 seconds for the whole owned group, and uses SIGKILL only for still-verified members as a last resort. An unverified/stuck descendant prevents another launch and requires inspected recovery.
- `STOP` ends the run; `PAUSE` is the reversible local hold. The controller owns no other engine/session. It opens no terminal window or network listener. A per-controller `caffeinate -w` assertion is created only in live mode and released on exit.
- Local workers receive offline Hugging Face settings, disabled telemetry and an environment stripped of common API credentials. No paid critic, model upload, merge or deployment is performed automatically.

## Historical 48-hour dry test

```sh
python3 scripts/dry_test_controller.py --out ../outputs/controller-dry-run
```

This historical regression test advances a fake clock through the original 48-hour schedule and uses real CPU-only fixture subprocesses for lifecycle checks. Its simulated nightly windows and checkpoints do not describe the active eleven-hour run. No MLX import, model load, optimizer or training step occurs in the dry test. Its report and timeline explicitly label simulated checkpoints and reviews; they do not certify live training or GLB quality.

## Bounded correction phase

The current configuration caps each segment at12updates and holds at total segmentcount5 with `phase_complete`, preventing another automatic launch after the targeted pass. Codex must inspect checkpoint00010 and explicitly rebaseline the next phase; a missing reviewer cannot silently repeat the six correction examples. The original deadline and shutdown reserve still apply. The worker uses `exclusive_end_v1` for both training and validation so padding labels are excluded.
