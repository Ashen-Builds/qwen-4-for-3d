# Overnight controller

Preparation only. The controller is implemented and dry-tested with fake CPU workers; no live trainer has been started. Use the current Codex session as the supervisor/reviewer. The controller does not claim that completed HTML or lower loss proves a good GLB.

## Sequence

Frozen CCORE generation → Codex baseline review → ten short training steps → adapter-effect/reload check → three complete length probes → Codex qualification review → bounded training segments → checkpoint generation and review before each eight-hour deadline.

The live gates check completed backward steps, finite losses and adapter tensors, nonzero learned B matrices, measured step time, and adapter-effect/reload logits. Gradient norms are not separately instrumented. Live training still has to pass these gates after the owner starts it.

Each training segment uses at most 25 minutes including resource wait, respects the shared GPU slot, saves every step and copies a valid checkpoint into an immutable directory. Segment iteration count is estimated conservatively from the slowest measured step. A segment resumes **adapter weights only**; Adam state and sampling restart. This is an explicit warm-restart experiment, not bit-exact optimizer continuation.

The current fixed layer scope and data/model/runtime fingerprints cannot silently change mid-run. Source/data bytes, library versions, tokenizer metadata and model-weight size/mtime are checked before jobs. A changed input requires a stopped, reviewed/rebaselined run.

## What is autonomous

The controller runs phase ordering, resource waits, safety stops, checkpoints, artifact packets and clock deadlines. **Codex must remain active to inspect and acknowledge review packets**, including source/export checks, GLB validation, playback/appearance and the fixed development probes. With no reviewer, it waits safely. Routine reviews do not require waking the owner. Optional CLI critics remain subject to the owner's model restrictions.

The independent final suite is a supervisor responsibility: freeze a candidate before final testing, reserve an allowed compute window, and do not use those scores to tune subsequent checkpoints. If the window/budget is exhausted, report incomplete evaluation. A default overnight-only run has less than 48 compute hours; daytime reports may reuse the last actual output and state its age.

## Start later, only after the owner's instruction

`python3 scripts/overnight_controller.py` prints a plan/config hash and launches nothing. There is no cron, timer or scheduled start.

After the actual start instruction, Codex records a private authorization JSON with `owner_authorized: true`, `scope: "48-hour-sprint"`, `run_id: "astra-sprint-01"`, the exact printed `config_sha256`, and `allow_daytime_compute: false` unless the owner explicitly permits daytime use. This record documents existing authority; a file itself grants none.

From the checkout, a live start can then run headlessly:

```sh
tmux new-session -d -s astra-sprint-01 -c "$PWD" \
  ../work/qwen-eval-env/bin/python scripts/overnight_controller.py \
  --run --authorization-file ../work/sprint-prep/owner-start.json
```

Do not run this command during preparation. The start refuses before the planned start time. The run directory is exclusive; a second controller cannot acquire its lock. `--status` is read-only. `--run --resume` requires the same authorization/config and refuses a recorded live worker or orphan. It does not take over another session's process.

## Review protocol

Read `work/sprint-prep/overnight/RUN_ID/review-packet.json`. Review files name its exact `packet_sha256`; stale packets cannot advance. Queue a reviewed JSON using `--ack-review FILE --authorization-file FILE` (the owning controller applies it under its lock).

A baseline review needs `baseline_frozen: true`; a qualification review needs `live_gates_passed: true`, backed by the worker's successful checks. Baseline/milestone reviews record `raw_export_status: "pass" | "fail"` and `evidence: [{"path": "relative/path", "sha256": "..."}]`. Evidence must exist inside this run and match its hash. For a raw pass, include `glb_file`, `validation_file` and the actual validator receipt. A milestone also requires `export_and_visual_reviewed: true`, an explicit boolean `regression`, and `glb_validation_errors: 0` plus `assistance: "none"` before `accept_checkpoint: true`. Repaired diagnostic exports cannot be promoted as raw passes.

Decisions are `continue`, `retry` or `stop`. A failed worker cannot be acknowledged as successful. One diagnosed retry is permitted; two worker failures stop further launches. Two consecutive reviewed regressions stop training and retain the best accepted checkpoint. Save the scorecard and screenshots/playback evidence before acknowledging.

## Safety and timing

- Streaming, shared GPU pause and this run's `PAUSE` file stop owned compute. Neither global flag is removed by this controller. GPU gate code75 is an availability hold with a five-minute cooldown, not a model crash.
- Without explicit daytime permission, drain begins at **8:58 a.m. EST**, leaving termination grace before the owner's 9 a.m. use; compute resumes in the next 11 p.m. window. An authorized `DAYTIME_APPROVED` marker can change availability within this run; it never overrides streaming/global pause.
- The fixed hard deadline includes pauses and evaluation. No new heavy job starts after it. Reports say unchanged, missing or unreviewed when appropriate; no fabricated GLB is created.
- The parent monitors reported memory, owned-group RSS and reclaimable system memory. The live training worker sets a 160 GiB **advisory** MLX memory limit and 2 GiB cache; this is not an OS-enforced cap. Live memory/throughput qualification remains mandatory.
- Stop uses SIGTERM, waits up to 60 seconds for the whole owned group, and uses SIGKILL only for still-verified members as a last resort. An unverified/stuck descendant prevents another launch and requires inspected recovery.
- `STOP` ends the run; `PAUSE` is the reversible local hold. The controller owns no other engine/session. It opens no terminal window or network listener. A per-controller `caffeinate -w` assertion is created only in live mode and released on exit.
- Local workers receive offline Hugging Face settings, disabled telemetry and an environment stripped of common API credentials. No paid critic, model upload, merge or deployment is performed automatically.

## Dry test

```sh
python3 scripts/dry_test_controller.py --out ../outputs/controller-dry-run
```

The test advances a fake clock through 48 hours and uses real CPU-only fixture subprocesses for lifecycle checks. No MLX import, model load, optimizer or training step occurs. The report and timeline explicitly label simulated checkpoints and reviews. Live training and GLB quality are not certified by this test.
