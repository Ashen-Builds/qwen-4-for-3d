# Full-program correction tools

Portable, CPU-only source for preparing and qualifying a small derived Three.js correction curriculum. These tools do not train a model, launch a browser or renderer, download data, or alter an active training configuration. Generated datasets, GLBs, model files and qualification evidence are deliberately absent.

The six targets are licensed CCORE procedural HTML programs. Their geometry and authored motion are unchanged; each input introduces one controlled API, hierarchy, track or export error. These are new correction conversations over existing target programs, not independent assets or new modeling knowledge.

## Files and dependencies

- `scripts/prepare_full_program_corrections.py` extracts six original HTML targets, inserts one controlled defect, checks complete no-thinking token sequences, and stages review copies. The bundled `stage_generated_page.py` is its only local code dependency.
- `scripts/assemble_correction_revision.py` validates a root qualification receipt before creating a filtered revision. It retains the original validation lineage and can use an explicitly selected fixed validation panel.
- `scripts/verify_full_program_export.mjs` compares an actual exported binary with its supplied reference. It preserves geometry, hierarchy, clip/binding and CPU-motion checks, while allowing only proven animation-targeted captured-pose differences. This does not replace browser or visual review.
- `tests/` contains small synthetic CPU tests. Binary fixtures exist only in temporary directories and are removed afterward.

Preparation and assembly require Python 3.12 and a local tokenizer compatible with the source data. They were checked with Transformers 5.23.0 and tokenizers 0.23.3. Every tokenizer call uses `local_files_only=True`, `trust_remote_code=False`, and `enable_thinking=False`; weights are not loaded. The verifier uses the caller's installed `three@0.160.0` and `gltf-validator@2.0.0-dev.3.10` dependencies, resolved through `--repo`. Nothing is installed automatically.

`--workspace` is an explicit base for relative data paths. Python `--repo` and `--tokenizer` paths resolve against it; the Node verifier resolves its `--repo` and `--workspace` against the invoking directory, then resolves data paths against the workspace. Absolute paths are also accepted. No home directory or inferred multi-level work-parent layout is required. `--help` requires no dataset or tokenizer loading.

## Preparation

Supply a previously frozen, rights-reviewed no-thinking replay dataset with `DATA_MANIFEST.json`, `ROW_PROVENANCE.json`, `replay/train.jsonl`, and `replay/LICENSE.source`. The repository must provide `eval/sprint-probes-v1.json`. Preserve the original upstream acquisition manifest and source notices; these tools do not acquire or redistribute those inputs.

```sh
python scripts/prepare_full_program_corrections.py \
  --workspace /path/to/workspace \
  --repo /path/to/repository \
  --tokenizer /path/to/pinned-local-tokenizer \
  --source /path/to/frozen-replay \
  --out /path/to/new-correction-candidates \
  --serve-root /path/to/existing-loopback-root/correction-review \
  --base-url http://localhost:8767/correction-review
```

The loopback server must already exist and serve the review directory with the pinned Three.js files under `/vendor/three/`. Preparation creates no server and no browser session. It refuses existing output directories. Model targets contain the original HTML; dependency URL rewrites, a 60 FPS cap and the error overlay exist only in review copies. One rolling-log source uses Three.js 0.164.1; reviewing it with the local 0.160.0 dependency is an explicit adaptation that must be qualified.

Do not execute negative pages unattended. A malformed track can hang a page even when its syntax is valid. Preserve the failure, close the owned tab, and do not automatically retry. Where a negative cannot safely complete, record the actual observation and a bounded API/representation check; the qualifying coordinator must decide whether that evidence establishes the intended defect.

The drawer negative intentionally exports `assetRoot.children[0]`, its first actual mesh. Exporting `assetScene.children[0]` would retain the entire asset and is an ineffective negative. The floor-fan source is excluded because its full-turn quaternion keys interpolate without visible motion; the ceiling-fan source supplies the quaternion task instead.

## Qualification and assembly

For every candidate, retain actual clean browser execution, exported GLB validation/reimport, geometry/hierarchy/clip checks, visual motion evidence, and an effective negative check. An existing publisher GLB or a source hash alone proves none of those browser observations.

```sh
node scripts/verify_full_program_export.mjs \
  --repo /path/to/repository \
  --workspace /path/to/evidence \
  --reference supplied-reference.glb \
  --actual actual-browser-download.glb \
  --out comparison.json
```

The qualification receipt has `schema: 1`, `status: "qualified"`, `qualified_by: "/root"`, the exact candidate `correction_manifest_sha256`, and exactly six `approved` entries. Each entry binds its `id`, `clean_html_sha256`, `corrupt_html_sha256`, and `conversation_sha256`. All checks must be true: `clean_source_runtime`, `clean_export_and_reimport`, `geometry_hierarchy_clips`, `visual_motion`, and `negative_check`. Each check has a nonempty evidence list of existing files with `path` and `sha256` values. Relative evidence paths resolve beside the receipt. Conversation hashes cover compact, sorted-key, UTF-8 JSON for the complete `{"messages": [...]}` row with `ensure_ascii=False`.

`qualified_by` is coordination metadata, not authentication. Hash checks establish evidence identity, not the truth of a visual judgment. Never populate a real receipt from the synthetic unit tests.

```sh
python scripts/assemble_correction_revision.py \
  --workspace /path/to/workspace \
  --repo /path/to/repository \
  --tokenizer /path/to/pinned-local-tokenizer \
  --source /path/to/frozen-replay \
  --source-manifest-sha256 SOURCE_MANIFEST_SHA256 \
  --corrections /path/to/qualified-candidates \
  --correction-manifest-sha256 CORRECTION_MANIFEST_SHA256 \
  --qualification /path/to/root-qualification.json \
  --out /path/to/new-revision \
  --include-targeted
```

This bounded revision expects the original 401 replay training rows and removes only `asset-000368` and `asset-002237`. It retains 399 replay rows, 64 helper rows, and six correction conversations once each: 469 main training rows. The original 47 replay and 16 helper validation rows remain unchanged. Corrections intentionally reuse six training target programs and inherit their groups; do not count them as six independent programs.

Optional `--validation-panel /path/to/fixed-panel` verifies the neighboring `manifest.json` and exactly ten byte-identical members of the original 63 validation rows. The complete original file remains `full-dev/valid.jsonl`; only the explicitly selected runtime validation file uses ten rows. Evaluation recommendations are `val_batches=-1`, every selected row, and segment-boundary evaluation without consuming training RNG.

The optional targeted dataset has six rows once and the same selected validation panel. Its settings recommend twelve updates as two epochs only at batch size one without packing, with prompt masking enabled. Settings are prospective: assembly changes no worker, optimizer, model, schedule, deadline, or active input. The complete qualified receipt, rights, source hashes, token masks and lineage are preserved in the new local artifact.

## Tests

```sh
python -B -m unittest discover -s tests -p 'test_correction_tools.py' -v
node tests/test_verify_full_program_export.mjs --repo /path/to/repository
```

The tests check refusal, identity, validation membership and the verifier's transform/curve rules. They are not visual evidence or training-gain evidence. Before publication, scan the intended source files and repository history with the project's security policy. Keep generated data, local evidence, model files, logs and runtime receipts outside the public source tree.
