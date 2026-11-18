# HANDOFF — qwen-4-for-3d (Astra, image-to-3D)

Date: 2026-11-18 · Branch: `Astra` · Host: Mac Studio (M3 Ultra, Mac15,14, 256 GiB) · Status: **paused until Qwen 4 is released**

## What this is

A local model turns one reference image into a GLB asset (characters first) that a 16 GB laptop can produce overnight for free. The model does not output a shape: it writes a Three.js program, and running that program builds and exports the GLB. The work so far used CCORE's `Qwen3.5-4B-GLB-3D-Coder` as the base. On November 18 the owner paused the project until Qwen 4 is out, and had every local model on the Studio deleted. The earlier handoff, with the full history of the November 16 to 18 runs, is archived at [docs/handoffs/HANDOFF-astra-20261118.md](docs/handoffs/HANDOFF-astra-20261118.md).

## Repo / branch map

| Repo | Checkout | Branch |
|---|---|---|
| `Ashen-Builds/qwen-4-for-3d` (public) | `~/work/qwen-4-for-3d` | `Astra` (draft PR #1, unmerged) |

One worktree, no stashes, no sibling checkouts.

## Where things stand

- **First full fine-tune did not clearly beat CCORE.** 240 image-to-program pairs CCORE had never seen, one pass, 451.5 training minutes. Five concept images, three tries each: CCORE 7 of 15 working GLBs, ours 10 of 15, within noise. Report: [docs/image-to-3d-result-20261118.md](docs/image-to-3d-result-20261118.md).
- **Scoring panel, partial.** Stopped at 44 of 150 generations. On the 22 held-out renders that both models finished (seed 42 only): CCORE 15 working, ours 16; five worked only on CCORE, six only on ours. No difference. Evidence and scores: `eval/panel-v1/partial-20261118/`.
- **Description test, not finished.** Two of five locally written descriptions exist (`eval/five-asset-described/prompts-local/`). No asset was built from any description, so "description beats image" is still only the CCORE author's statement.
- **Held-out loss during the fine-tune:** 0.846 at the start, 0.725 after 15 examples, 0.644 after 32, 0.623 after 240. Almost all of the gain came from the first 32 examples. Log and loss record: `eval/results/image-to-asset-run-20261118/`.
- **How tries fail:** every generation wrote a complete program. Of 17 failed tries in the five-image test (all three models), 14 stopped while running on a slip such as a name that was never defined, 2 failed in the export step and 1 exported an invalid file. Training on token loss does not target this.

## Owner decisions (November 18)

- Pause until Qwen 4 is released. No training, inference or downloads until then.
- Stop the panel run and the description test before they finished.
- Delete all local models, including our own fine-tuned model. It existed nowhere else and is gone; only its test results remain in this repo.
- Direction agreed in discussion, not yet a committed plan: keep the reference image, but use it around the model rather than feeding it straight in. A describe step turns the image into a detailed written request, and each try's render is scored against the image so the loop keeps the best of many tries. Train once on Qwen 4, on CCORE's 3,918 public examples plus our own new pairs.

## What happened this session

- `9bab2f3`: partial panel evidence and scores added under `eval/panel-v1/partial-20261118/` (local run paths removed from the result files).
- This commit: fine-tune training log and loss record added, previous handoff archived, this file written.
- Stopped the two background jobs left by the previous session (`scripts/run_panel.py` and `scripts/describe_images_llama.py`) with SIGTERM; both were idle in the stream-guard wait and exited in one second. A `STOP` file is in `~/work/runs/panel-v1/`.
- Deleted nine model folders, 75 GB (free space 139 GiB to 214 GiB):
  - `~/work/models/`: original `Qwen/Qwen3.5-4B`, CCORE scene model `ccore/Qwen3.5-4B-3D-Coder`, our fine-tune in Hugging Face layout.
  - `~/work/models-native/`: original Qwen Q8 GGUF with its vision projector, our fine-tune as Q8 GGUF.
  - In the November 16 Codex workspace: CCORE asset model `ccore/Qwen3.5-4B-GLB-3D-Coder` and its three converted copies (BF16, two Q8).

## Verification done

- `git rev-list --left-right --count Astra...origin/Astra` printed `0 0` after the first push.
- Staged secret scan (Gitleaks 8.30.1 with the shared custom rules) found no leaks; GLB JSON chunks and PNG text chunks checked for local paths, none found.
- After deletion, a search of `~/work` and the Codex workspace for `.gguf` and `.safetensors` files over 50 MB returned nothing, and no process was reading a model file.
- `scripts/score_panel.py` produced the partial scores from the committed files.

## Not done / explicitly out of scope

- No clear win over CCORE exists. No model of ours exists any more.
- The panel is 22 of 25 held-out images on one seed, with no likeness scores. The 30 concept-art images it still needs (`eval/panel-v1/concept-requests.md`) were never made.
- The description test produced no result.
- The per-example review page and the overnight generate-and-check loop are not built.
- The CCORE author has not been asked for his full fine-tune settings, his teacher model, or what he rejects by eye.
- Nothing is known here about Qwen 4 itself: size, licence, vision support, or whether the MLX trainer can load it.
- Draft PR #1 is unmerged and its description predates the image-to-3D work.

## Next steps (when Qwen 4 is released)

1. Check that a small Qwen 4 can be loaded and fine-tuned locally, and that `scripts/train_image_to_asset.py` still applies (it depends on the `mlx-vlm` Qwen3.5 model class).
2. Download the base model and CCORE's dataset `ccore/ThreeJS-3D-GLB-Assets`. Run the raw model through the panel first; that pass rate is the number to beat.
3. Finish the panel before any training: add the concept-art images and likeness scoring, three tries per image.
4. Run the description test properly: image, then description, then build, against building straight from the image.
5. Fine-tune on all 3,918 CCORE examples (they are new to Qwen 4, unlike on CCORE). Gate the long run on a short pilot that passes the behaviour check on held-out images, not on loss alone.
6. To go beyond CCORE, build new verified pairs: generate tries overnight, keep those that pass the automatic checks, and add a keep-or-reject review page for the owner.

## Key files

- `docs/image-to-3d-plan.md`: goal, stages, pilot history.
- `docs/image-to-3d-result-20261118.md`: three-way result and what was trained.
- `scripts/train_image_to_asset.py`, `scripts/run_training_segments.sh`: full fine-tune trainer (Adafactor, float32) and its segment driver.
- `scripts/run_panel.py`, `scripts/score_panel.py`, `scripts/score_likeness.py`: panel runner and scorers.
- `scripts/describe_images_llama.py`: image-to-description step.
- `scripts/export_and_render.mjs`: runs a generated page, exports and validates the GLB, renders two views.
- `eval/panel-v1/`: panel images, manifest and partial results.

## How to run it

Nothing runs without models. To restore the Qwen 3.5 setup for a comparison:

```bash
hf download ccore/Qwen3.5-4B-GLB-3D-Coder --revision 8f32a199f8b22fe3157b9c5c8b42b052a0750dd3
hf download Qwen/Qwen3.5-4B --revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a
hf download lmstudio-community/Qwen3.5-4B-GGUF Qwen3.5-4B-Q8_0.gguf mmproj-Qwen3.5-4B-BF16.gguf
```

CCORE also publishes quantized files on its model page. Panel and test commands are in `docs/image-to-3d-plan.md` and `eval/panel-v1/README.md`.

## Running processes / infra

None. No LaunchAgent, port or background job belongs to this project. Every GPU job must go through `gpu_slot`, and nothing may start while the stream guard flag exists.

## Picking this up on the other machine

- Branch is pushed to `origin/Astra`; pull with `git fetch origin && git switch Astra && git pull`.
- Written on: Studio.
- **Local-only, did NOT travel:** `~/work/data/a3d` (training pairs and captions, 1.3 GB), `~/work/envs/a3d` (training environment), `~/work/runs` and `~/work/outputs` (raw runs), and the November 16 Codex workspace (9.9 GB: datasets, earlier run's adapters and archives, llama.cpp build `4ddf2b9`, convert environment).
- **Needs rebuilding there:** `node_modules` (`npm ci`), the training environment (`mlx==0.32.4 mlx-lm==0.32.2 mlx-vlm==0.8.0 pyarrow pillow safetensors numpy`), all models.
- **Studio-only:** training and generation.

## Secrets

None. The models and datasets used are public downloads.

## Gotchas

- CCORE has memorized its own training split, so on CCORE only its 417 validation pairs teach anything. On a new base model all 3,918 are usable.
- Loss alone hid two pilots that stopped following the image. Always check behaviour on held-out images against the untouched base.
- Resuming training must fill `optimizer.state` in place; replacing it doubled memory.
- One try per image is too noisy to read: the same model went 4, 1 and 2 of 5 across three seeds.
- A page staged with a 60 fps cap can starve a program's export handler and record a correct program as "nothing exported". The harness was fixed for this on November 18; keep that fix.

## Resume command

```
Work in ~/work/qwen-4-for-3d on branch Astra. Read HANDOFF.md and docs/image-to-3d-plan.md. Qwen 4 is out: start at "Next steps", step 1, and do not download or train anything until I say go.
```
