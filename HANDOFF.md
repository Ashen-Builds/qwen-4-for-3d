# Astra 3D overnight experiment

Updated November17,2026 at00:00EST. Repository `Ashen-Builds/qwen-4-for-3d`, branch `Astra`, draft PR#1. The overnight goal is active. No improved Astra asset has been demonstrated.

## Authority and fixed deadline

The owner explicitly answered **Start now as requested**, superseding the attachment's stale9pm restriction. Experiment start20:42:39EST November16; hard stop07:42:39EST November17. Intermediate comparison04:42:39, main-training cutoff06:27:39, shutdown reserve starts07:40:39. Variants never reset the clock.

Local training, evaluation, routine Codex reviews, branch pushes and practical private Drive backups are authorized. No spend, model-weight publication, deployment, main merge, or takeover of another session. Optional critics: verified free Devin SWE2 only; Gemini Hydrogen4 only, currently not available in the installed CLI catalog.

## Current owned state

The workspace's sibling `work/` contains models, private data and run state; it is not inside this checkout. Actual machine: M3 Ultra,256GiB. Python3.12,MLX0.32.4,MLX-LM0.32.2,Transformers5.23.0. Use the shared GPU-slot wrapper and inspect actual processes before every handoff. The watchdog currently reduces the cap to2; do not weaken it. Run model jobs serially. Preserve streaming/global flags and foreign sessions.

- Current controller: tmux `astra-direct-20261116`; config `configs/overnight-direct-code.json`; private authorization `work/sprint-prep/owner-start-direct-20261116.json`.
- Run root: `work/sprint-prep/overnight/astra-direct-20261116`. At this update it is cleanly **paused locally**, with no active job, after three100-step main segments. This is an orchestration hold, not a paused user goal.
- Confirmed controller updates:313=13qualification+300main. Latest immutable checkpoint `checkpoints/job-00007`; no visually accepted best checkpoint yet. Job00007 completed536.94s,reported peak29.56GB.
- Cached-prefix two-layer short qualification passed, but the5327-token length step breached the24GiB reclaimable-memory floor before any update. Owned processes were SIGTERMed and memory recovered; no two-layer adoption/retry. Root now owns the GPU for300-step primary evaluation (exec75778,labelastra-300step-evaluation,worker73552); inspect before any launch. `capacity2_probe` is CPU-only preparing a rank16 layer31 warm expansion, with NO GPU permission until explicit new handoff.
- Earlier `astra-manual-20261116` controller is stopped; preserve its42-step checkpoint and failed outputs. Older scheduled `astra-overnight-20261116` never trained and must not be restarted.
- Local server `http://localhost:8767/` serves only sibling `outputs/babylon-comparison`. Inspect its actual process before restarting. Task-owned server was restarted after allowing localblob fetches required by embedded GLB textures; exec93118. The200-step diagnostic review tab was closed and its slot released.

## Model, data and training semantics

Base is pinned `ccore/Qwen3.5-4B-GLB-3D-Coder` revision `8f32a199f8b22fe3157b9c5c8b42b052a0750dd3`, derived BF16 text checkpoint in `work/models-derived/ccore-bf16`. Original CCORE weights are retained. Official Qwen3.5-4B weights and derived copies were deleted at the owner's request; historical outputs remain.

Current one-layer LoRA: layer31 only,rank8,scale20,dropout0,479232trainable parameters,learning rate1e-5. Each segment warm-starts adapter weights; Adam state and iterator restart with seed42+segment_index. This is not exact optimizer continuation. Complete outputs are trained without truncation. Frozen layers0–30 use eval kernels, with gradient detached only at layer31 input.

The initial training-ops equivalence check failed strict tolerances and remains recorded. A separate short check against full-model eval computation **inside autodiff** passed logits/loss/gradients/update/reload exactly. Later independent diagnostics found that eval-prefix computation inside autodiff differs numerically from materializing it outside; do not describe the one-layer runtime as proven identical to every ordinary-inference arithmetic path. The pending two-layer candidate materializes frozen prefix0–29 outside autodiff and tests the native suffix against an independent oracle.

Direct-code dataset: `work/sprint-prep/direct-code-proposal/data-v1`,manifest SHA256 `c49f37efe977377c86f221a4579decc55b2841038230194504e6a91828703cb6`.401/47 full-program replay train/dev,64/16 generic repair examples,465/63mixture. Reasoning removed; original final code unchanged. Explicit no-thinking chat formatting in training and matched primary evaluation. Full-field alias exclusion plus canonical-title/normalized-JS connected-component split; zero algorithmic group overlap is not proof of complete semantic independence or absence from CCORE pretraining. Babylon prompt, outputs and scene-specific repairs never enter training.

Earlier reasoning-heavy data over-weighted helper rows and missed Bellows/SignalBeacon/observatory components in code. The old Bellows pair is diagnostic, not independent heldout evidence. The fresh direct-code run starts a new adapter from CCORE and does not resume the old42-step lineage.

## Actual evaluation findings

Use exact unchanged `eval/prompts/babylon-marketplace-v3.txt`,same system prompt/seed42/sampler/49152-token limit/precision/dependencies per matched condition. Raw source is immutable. Every repair stays separately labeled; no manual beautification or sourced-asset insertion into scored outputs.

- Historical repaired CCORE remains the owner's visual reference. It looked richer than repaired official Qwen but lacked walking/full-town coverage. Both historical raw outputs failed.
- Fresh thinking-on BF16 CCORE:39594tokens,631.28s; raw syntax/runtime failures. Mechanical diagnostic repairs produced a real reopened2040220-byteGLB with13clips/35channels,Khronos0errors/0warnings. Six villagers,no legwalking,floating palm fronds. Source/patch/provenance/screenshots retained.
- Old42-step adapter:49152-token showcase cap,no completeHTML/GLB; Bellows cap32768. Approach stopped.
- Fresh no-thinking CCORE control:49152-token cap/798.47s,repetitive planning and skeletonHTML with ellipses; raw syntaxfail. Merely outperforming this failure is not a visual win.
- Direct-code200-main-step checkpoint00006:primary no-thinking output finishes12837tokens/202.32s,fullHTML, but raw pseudocode/syntax/runtime/export failures; no rawGLB. About11villager assemblies plus2merchant assemblies; no exportable animation clips. Thinking-on crosscheck also finishes27121tokens/435.88s but fails syntax/export. No demonstrated visual improvement.
- Checkpoint00006 static diagnostic was actually exported/reopened:1603028bytes,628meshdefinitions,742nodes,0clips,Khronos0errors/0warnings. It looks worse: floating roofs/walls/reeds and detached parts, hugewaterplane,smallcentralmarket. It interprets pseudocode, omits ambiguous palms/signart, and adds a static exporter. No raw pass/trainingtarget. Screenshots0/4s under sibling `outputs/babylon-comparison/diagnostic-200`; CCORE motion changes whileAstra remainsstatic. Threecontrol embeddedtexture loaderrors were observed; serverblob-fetch policy fixed afterward but browserreverification is pending.

The common render harness in `eval/render-harness` has actual browser0/4second seek checks and reimportedGLBs. The firstpair has different generationmodes/repairassistance, explicitlylabeled; it cannotestablishmatchedcausality. Embeddedcontroltexture reload remains to be rechecked afterserverpolicyfix. Visual/playback inspection, not a validator or clip count alone, establishes an artifact result.

## Next actions

1. Monitor existing300step inference until exit; preserveexactinputmatch (alreadyverifiedagainstfreshno-thinkingcontrol). GetCPU rank16proposal, grantonlyoneboundedGPUqualificationatcleanhandoff. Two-layerlongpathisrejected; preserveallfailures.
2. Inspect300steprawoutput and recheckviewertextures atsafeGPUboundary.200stepdiagnosticisobservedworse; keepfailure/assistancelabels. Adoptrank16onlyaftershort/full-length/save-reloadgates;retain300stepinputweights.
3. Continue a justified bounded approach within the same deadline. Inspect review packets; routine continuation is Codex's responsibility. Preserve independent final tests and all raw failures. Do not call falling loss a quality win.
4. Deliver intermediate/final comparisons at the fixed times. By hard stop, stop all owned heavy jobs, leave a labeled localhost GLB comparison in Chrome, save real screenshots/playback evidence, and report better/worse/mixed honestly.
5. Push sanitized source/results and this rolling handoff; back up new data/checkpoints/results through the **direct Google Drive connector only**, then update the GitHub-backed wiki. Do not claim the old archive contains new live-run checkpoints.

## Archive and publication evidence

The private source archive is complete:6packages,216canonicalpayload files/parts,21484759314bytes. Remote names/sizes were verified; localSHA256manifests uploaded; no whole-cloud byte redownload. Models and research-restricted corpora stay private. New direct-code data-v1 and the300-step snapshot (100/200/300-step checkpoints, raw200-step evaluations, metrics and manifests) are also uploaded through the connector; remote names/sizes/parents verified. Sizes6113719 and5435769bytes respectively. Later checkpoints still need backup. Account is Haarith; private folder/file IDs are in the archive records, not public Git.

Publication scans use repository-security guidance and the custom gitleaks rules. A prior command mistakenly continued after a scanner finding and pushed commit2936edf. The finding was a recomputed prompt-token SHA256, not a credential; corrective741003f removed the redundant field and narrowly allowlisted its historical fingerprint. Preserve this disclosure and do not claim that original scan passed. Subsequent full-history scans passed with that exact classified false positive.

See `docs/overnight-run-20261116.md` for the experiment narrative, `docs/overnight-controller.md` for operation, `docs/comparison-results.md` for historical comparisons, and earlier Git revisions for superseded preparation history.
