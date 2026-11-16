# Action items

Ordered so you can **start today** on current Qwen and port to Qwen 4 when it drops. Each item credits the replies it comes from. Commands come from the official docs (mlx-lm `LORA.md`, Unsloth's Qwen3.8 guide) as of 2026-11-16. They haven't been run in this repo yet, so expect minor flag tweaks.

**Assumed setup:** a Mac Studio (M3 Ultra, 256 GB), Blender installed, and the Blender MCP add-on.

---

## Today (about 2–4 hours)

- [ ] **1. Pick scope v1: Blender *tool use*, not general 3D knowledge.** Write it in one line at the top of `docs/dataset-plan.md`. (Answers @0xHaley_.)
- [ ] **2. Set up a training env on the Mac with `mlx-lm`.** Unsloth's Mac training isn't out yet, per their docs.
  ```bash
  python3 -m venv ~/venvs/q4-3d && source ~/venvs/q4-3d/bin/activate
  pip install -U "mlx-lm[train]" datasets
  mlx_lm.lora --help   # sanity check
  ```
- [ ] **3. Pick a small current base model** (@RedFasterX, @IHAD18BTCIN2013, @naveen_saradhi_): `mlx-community/Qwen3.5-4B-4bit`. A quantized model means `mlx-lm` does QLoRA. Step up to `mlx-community/Qwen3.5-9B-4bit` later.
  ```bash
  mlx_lm.generate --model mlx-community/Qwen3.5-4B-4bit \
    --prompt "Write a Blender bpy script that adds a cube and keyframes it moving up over 60 frames."
  ```
  If the Qwen3.5 vision-language checkpoint won't load as text-only in `mlx-lm`, fall back to a text-only Qwen3 4B/8B MLX build. The pipeline doesn't care which.
- [ ] **4. Snapshot the Blender MCP tool schema** you'll train against into `schemas/blender-mcp-<version>.json` (from the client's `tools/list`). Training data must use the server's real tool names and args (@waitingforASI_).
- [ ] **5. Turn on local logging of every MCP call** (@johnroodepic, @crum7355608): the prompt, tool, args, result, and scene before and after. Upstream `blender-mcp`'s own trajectory recorder only uploads to its maintainers' Supabase and keeps no local copy, so log in your client or a small proxy to `traces/raw/*.jsonl`. Decide whether to call `disable_telemetry`.
- [ ] **6. Write the first 10 eval tasks** (@EternitiesAI, @robeotx): a prompt plus a Python assertion on scene state (see `docs/dataset-plan.md` §5). Run the base 4B on them and record the **baseline pass rate**.
- [ ] **7. Do 20 real Blender sessions through MCP** with a tight prompt (tool list + two worked examples) and mark each accept or reject. That's the first trace batch.

## This week

- [ ] **8. Grow the eval to 50 tasks** (15 modeling, 10 materials, 10 animation, 5 rigging, 5 scene/camera, 5 multi-step). Keep it out of training forever.
- [ ] **9. Build `scripts/verify_sample.py`:** run each candidate headlessly and keep it only if it exits clean and passes its check.
  ```bash
  blender --background --factory-startup --python sample.py
  ```
- [ ] **10. Bootstrap Track B data from public sets** (from @grok's list, verified on HF): `FreedomIntelligence/BlendNet` (12k, Apache-2.0), with every script re-run through the verifier and only passing ones kept. Optionally add ≤10–20% `PGCRYPT/OpenBlender_Train` docs Q&A.
- [ ] **11. Generate synthetic Track A traces with a teacher model** (@vishalskotak, @BarryDeenTech, @Vidyut), verify them, and aim for **300–500 good tool-call episodes** (@tymofii, @johnroodepic, @LightyLightyHi). Make about 25% of them animation.
- [ ] **12. Format to `data/{train,valid,test}.jsonl`** in mlx-lm's `tools` and `chat` formats (examples in `docs/dataset-plan.md` §3). Keep samples under about 16K tokens (@SandeshRajx).
- [ ] **13. First LoRA run on the Mac** (@fufeng1688: "you'll know within a day"):
  ```bash
  mlx_lm.lora --model mlx-community/Qwen3.5-4B-4bit --train \
    --data ./data --mask-prompt --batch-size 1 --grad-checkpoint \
    --iters 600 --adapter-path ./adapters/q35-4b-blender-v0
  mlx_lm.lora --model mlx-community/Qwen3.5-4B-4bit \
    --adapter-path ./adapters/q35-4b-blender-v0 --data ./data --test
  ```
- [ ] **14. Re-run the 50-task eval** on base vs. adapter, at several checkpoints (@MikeBrave_Maker). Log the pass rate, tool-call validity and calls per task in `eval/results.md`.
- [ ] **15. Iterate on data, not hyperparameters** (@csgriff_: 70/5/25). Mine the failures, write or collect traces that fix them, retrain.
- [ ] **16. Look at a known-good 3D fine-tune** (@SandeshRajx): [`ccore/Qwen3.5-4B-3D-Coder`](https://huggingface.co/ccore/Qwen3.5-4B-3D-Coder) and its dataset `ccore/ThreeJS-3D-Scenes`, to see the format and scope.

## Optional: rent an NVIDIA GPU to scale up

- [ ] **17. Unsloth on Kaggle/Colab or a rented GPU** for bigger bases (@eyoussef, @OliNorwell, @jobelshaji95). Per Unsloth's Qwen3.8 guide, QLoRA on Qwen3.8-27B fits in 24 GB, LoRA needs >36 GB, Kaggle gives 30 free GPU hrs/week, and the model exports to GGUF. Use the same `data/*.jsonl` rendered with the Qwen chat template.
- [ ] **18. Weights & Biases** for run tracking (@navin_hill). Both mlx-lm (`--report-to wandb`) and Unsloth/TRL support it.

## When Qwen 4 drops

- [ ] **19. Run the 50-task eval on stock Qwen 4 first.** If it's already "really solid at 3D" (@snapsnocaps), you'll know how much fine-tuning still adds.
- [ ] **20. Wait for tooling support**: an `mlx-community` Qwen 4 conversion plus `mlx-lm` architecture support, and/or an Unsloth Qwen 4 notebook. Then rerun step 13 with the new `--model`. Nothing else in the pipeline changes.
- [ ] **21. Re-validate the schema and traces** against the current Blender MCP version, and regenerate any samples whose tool names changed.
- [ ] **22. Publish on Hugging Face**, which is Ashen's stated goal (no hosting): the LoRA adapters, a fused model (`mlx_lm.fuse`), a GGUF if supported, the eval set, and a model card with the eval table. License to match Qwen 4's.

## Later: RL

- [ ] **23. RLVR on the verifier** (@crum7355608, @robeotx, @tensorfiend, @iamanishx): reward = script runs + scene assertion passes. Try a few reward functions. Unsloth documents GRPO for the Qwen3.5/3.8 architecture.
- [ ] **24. Preference data from the accept/reject logs** (rlhf/DPO), using the rejected episodes saved in step 5.
- [ ] **25. Vision track:** viewport screenshot → next action, and @xxsaissa's timelapse before/after mining.

---

**Rule of thumb from the thread:** the training run is cheap ($3–$100 per run reported). Your edge is a verified, schema-exact Blender dataset and an honest eval. Start collecting today.

## Updates

### 2026-11-16, 10:30 AM ET

- [ ] **Smoke-test the base model first.** Run the untuned Qwen against the Blender MCP tools and log where it fails before you train anything (@thesimaximalist).
- [ ] **Keep only verified episodes.** Count a training example only if the scene assertions pass, not just because the call didn't error (@sebuzdugan). Skip tutorial videos as data unless they're turned into tool-call steps (@olipdsanders, @botzero_net).
- [ ] **Free compute option:** try a Colab or Runpod setup script written by an AI before renting more (@botzero_net, @Thirty3lab). Ashen has the Google $200/m plan.
- [ ] **Hugging Face publishing:** free accounts have a 100GB private cap, so put GGUF quants in their own repo (@i2bhai8).
- [ ] **Optional no-training track:** build reference examples grounded in standards like ISO threads (@8bit_Slats).
