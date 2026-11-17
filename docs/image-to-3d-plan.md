# Image-to-3D plan

Written November 17, 2026, 13:50 EST, on branch `Astra`. This replaces the full-scene direction. Nothing here authorizes training; the owner starts each stage.

## Goal

A Roblox or Godot developer gives the model one picture (ChatGPT-style concept art) and says "turn this 2D image into a 3D asset." The local model writes a Three.js program that builds the asset and exports a GLB, and a laptop can run that loop overnight for free. The thing we train is the image-to-asset step. Export is a fixed script, not a model skill.

Decided with the owner today:

- Single assets, not scenes. Characters first, then props.
- Base model: CCORE `Qwen3.5-4B-GLB-3D-Coder` (the asset model). The scene model `Qwen3.5-4B-3D-Coder` is downloaded but parked.
- Full fine-tune with Adafactor, on the owner's word that the CCORE author's advice is law (he reported full fine-tuning beat LoRA for these tasks). Local M3 Ultra only, no rented GPU.
- Judge on the exported GLB, not the browser page.
- Overnight supervision is a cheap cloud agent (Haiku 5.5) that does the minimum: alive checks, kill stuck tries, morning report. It never writes 3D code and never judges every try.
- Reference images for tests come from Codex or Higgsfield, not from the dataset's own renders.

## Stage 0: baseline test (built, partly run)

Five reference images, 1024x1024, made by Codex: lamp, police officer, dragon, green van, skyscraper. Each goes to original Qwen 3.5 4B and to CCORE with the same instruction, system prompt, seed 42 and sampler. The exported GLB is validated and rendered from two fixed angles beside the reference.

Result so far: original Qwen read the lamp image correctly (its reasoning names the cream patterned shade, golden brim and dark base), wrote a complete program in 60 seconds, and the program crashed on an undefined variable. No GLB. Nine of ten generations remain. The run was stopped at 13:45 because another session's Blender renders held both GPU slots.

Resume (both arms skip anything already recorded):

```sh
cd ~/work/qwen-4-for-3d
export FIVE_ASSET_LLAMA=/Users/midir/Documents/Codex/2026-11-16/hey-buddy-we-re-going-to/work/llama-native-build/bin/llama-cli
export FIVE_ASSET_MMPROJ=$HOME/work/models-native/lmstudio-community--Qwen3.5-4B-GGUF/mmproj-Qwen3.5-4B-BF16.gguf
scripts/run_five_asset_image_test.sh qwen-original $HOME/work/models-native/lmstudio-community--Qwen3.5-4B-GGUF/Qwen3.5-4B-Q8_0.gguf
scripts/run_five_asset_image_test.sh ccore /Users/midir/Documents/Codex/2026-11-16/hey-buddy-we-re-going-to/work/models-native/ccore-q8/Qwen3.5-4B-GLB-3D-Coder-Q8_0.gguf
python3 scripts/build_five_asset_gallery.py --images eval/prompts/five-asset-20261117/images --outputs ~/work/outputs/five-asset-image-20261117 --arm "qwen-original=Original Qwen 3.5 4B" --arm "ccore=CCORE" --page ~/work/outputs/five-asset-image-20261117/index.html
```

Expect about one minute per generation once a GPU slot opens. The third column, our trained model, is added with the same scripts after Stage 3.

Files: `scripts/generate_asset_llama_image.py`, `scripts/run_five_asset_image_test.sh`, `scripts/export_and_render.mjs`, `scripts/build_five_asset_gallery.py`, `eval/prompts/five-asset-20261117/`. Runs land in `~/work/runs/five-asset-image-20261117/`, outputs in `~/work/outputs/five-asset-image-20261117/`.

## Stage 1: scoring panel

- 30 to 50 reference images, at least half characters, in the concept-art style users will bring. Three seeds each. Hold them out of all training.
- Automatic checks per try: program runs, GLB exports, validator clean, animation present when asked, render matches the reference (image-similarity score). Owner spot-checks renders.
- Score the 4-bit version of each model, since that is what a 16 GB laptop runs.
- Run CCORE and original Qwen through it first. Their pass rates are the numbers to beat.

## Stage 2: data

Picture-to-program pairs. Every example is executed, exported and checked before it counts.

1. Dataset pairs: each of the 3,918 CCORE asset examples ships a rendered picture of its result. Pair picture with program. About 900 are characters.
2. Style bridge: the dataset pictures are low-poly renders; users bring concept art. Restyle a share of the pictures into concept art with a paid image model (Higgsfield, owner approval for spend) or test whether the gap matters first.
3. Self-generated pairs: run the overnight loop on new reference images, keep tries that pass every check and the owner's eye. This is the CCORE author's method.
4. Hold out the Stage 1 panel and never train on test outputs or repairs.

Open question for the CCORE author: what he looks at in hand review, learning rate, epochs, max sequence length, whether reasoning traces are in training.

## Stage 3: trainer pilot, then the run

- Full fine-tune with Adafactor on the M3 Ultra, with image inputs through the vision tower. Last night's text-only LoRA trainer does not cover this; the trainer is new work.
- Pilot before any clock: memorize 20 examples, then a 30-minute run at a normal learning rate and confirm the Stage 1 score moves.
- Eight-hour run: one frozen recipe, at least 6.5 hours of actual training, automatic panel checks at checkpoints, stop on regression, no hand repairs or approach changes mid-run.
- Shrink the result to 4-bit, score it, test a real import into Roblox Studio.

## Stage 4: the overnight product loop

Plain script on the user's laptop: generate, run, export, check, score against the reference, keep the best, repeat. The supervising agent only checks it is alive.

## Why last night failed, kept as a checklist

- 75 minutes of training in an 11-hour window; the tested checkpoint saw 48 examples.
- One layer out of 32 at learning rate 3e-6: too small to change anything.
- Training data was CCORE's own training data; nothing new to learn.
- The main test was a whole town on the asset model, one seed; CCORE fails it raw too.
- The recipe was not settled before the clock started.

## Haiku manager

When the owner says start, the main session spawns one `haiku-scout` subagent (Haiku 5.5) with a brief that limits it to:

1. Launch the queued script in the background.
2. Every 10 to 15 minutes, read the run log and `gpu_status.sh`. Report one line: generations done, failures, GPU waiting.
3. Kill a try that has produced no new output for 20 minutes (stuck repetition) and let the script move on. Never touch other sessions' processes or shared flags.
4. Stop everything on memory pressure, disk under 20 GB, or a watchdog trip.
5. When the script finishes, build the gallery page and report counts: programs complete, GLBs exported, crashes by reason.

It does not read code, write code, repair outputs or judge quality. The same brief, with longer check-ins, becomes the overnight training manager in Stage 3.
