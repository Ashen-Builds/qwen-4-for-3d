"""Full fine-tune of the CCORE asset model on image-to-program pairs (MLX, Adafactor).

One process = one bounded segment. It loads the base model, restores the latest
checkpoint if there is one, trains until its time or step budget ends, saves a
resumable checkpoint (language-model weights, optimizer state, data position)
and exits so the GPU slot is released. The vision tower stays frozen; every
language-model weight is trained. Launch through gpu_slot.
"""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import time

import numpy as np
from PIL import Image

INSTRUCTION = "Turn this 2D image into a 3D asset."
IMAGE_SIDE = 768


def prep_image(src: Path, cache_dir: Path) -> Path:
    """Crop the render to its subject, pad to a square on the background colour, resize."""
    out = cache_dir / (src.stem + ".png")
    if out.exists():
        return out
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    diff = np.abs(a - bg).max(axis=2) > 14
    ys, xs = np.where(diff)
    if len(xs) < 50:
        box = (0, 0, im.width, im.height)
    else:
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        m = int(0.08 * max(x1 - x0, y1 - y0)) + 4
        box = (max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))
    crop = im.crop(box)
    side = max(crop.size)
    canvas = Image.new("RGB", (side, side), tuple(int(v) for v in bg))
    canvas.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
    cache_dir.mkdir(parents=True, exist_ok=True)
    canvas.resize((IMAGE_SIDE, IMAGE_SIDE), Image.LANCZOS).save(out)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="CCORE Hugging Face checkpoint directory")
    p.add_argument("--data", type=Path, required=True, help="JSONL of training rows, already in training order")
    p.add_argument("--dev", type=Path, help="JSONL of fixed dev rows")
    p.add_argument("--image-cache", type=Path, required=True)
    p.add_argument("--run", type=Path, required=True, help="Run directory holding checkpoints and logs")
    p.add_argument("--lr", type=float, default=1e-4, help="Adafactor relative step size")
    p.add_argument("--warmup", type=int, default=20)
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--max-minutes", type=float, default=30.0, help="Stop this segment after this much training time")
    p.add_argument("--max-steps", type=int, default=0, help="Stop this segment after this many steps (0 = no cap)")
    p.add_argument("--budget-minutes", type=float, default=0, help="Total training time allowed for the whole run (0 = no cap)")
    p.add_argument("--max-tokens", type=int, default=24000, help="Skip rows whose full sequence is longer")
    p.add_argument("--compute", choices=["float32", "bfloat16"], default="float32",
                   help="Forward/backward precision. Master weights and the optimizer always stay float32")
    p.add_argument("--eval-only", action="store_true")
    p.add_argument("--no-save", action="store_true")
    args = p.parse_args()
    if not os.environ.get("GPU_SLOT_HELD"):
        raise SystemExit("Launch through gpu_slot")
    if Path.home().joinpath(".cache/gpu-slot/STREAMING").exists():
        raise SystemExit("Stream guard is active")

    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    from mlx.utils import tree_flatten, tree_map_with_path, tree_unflatten
    from mlx_vlm import load

    args.run.mkdir(parents=True, exist_ok=True)
    log = (args.run / "train.log").open("a")

    def say(**kw):
        kw["t"] = time.strftime("%H:%M:%S")
        line = json.dumps(kw)
        print(line, flush=True)
        log.write(line + "\n")
        log.flush()

    started = time.monotonic()
    model, processor = load(args.model)
    tokenizer = processor.tokenizer
    lm = model.language_model
    model.freeze()
    lm.unfreeze()
    n_train = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
    dtypes = sorted({str(v.dtype) for _, v in tree_flatten(lm.parameters())})

    # Gradient checkpointing: keep one decoder layer's activations at a time.
    layer_cls = type(lm.model.layers[0])
    plain_call = layer_cls.__call__

    def checkpointed_call(layer, x, mask=None, cache=None, position_ids=None, position_embeddings=None):
        if not layer.training:
            return plain_call(layer, x, mask=mask, cache=cache, position_ids=position_ids,
                              position_embeddings=position_embeddings)

        def inner(params, x):
            layer.update(params)
            return plain_call(layer, x, mask=mask, cache=cache, position_ids=position_ids,
                              position_embeddings=position_embeddings)

        return mx.checkpoint(inner)(layer.trainable_parameters(), x)

    layer_cls.__call__ = checkpointed_call

    state_file = args.run / "state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {
        "step": 0, "position": 0, "train_seconds": 0.0, "segments": 0, "tokens": 0, "checkpoint": None}
    schedule = lambda step: args.lr * mx.minimum(1.0, (step + 1) / max(1, args.warmup))
    optimizer = optim.Adafactor(learning_rate=schedule, relative_step=False, scale_parameter=True,
                                clip_threshold=1.0, weight_decay=0.0)
    if state["checkpoint"]:
        ck = args.run / state["checkpoint"]
        lm.load_weights(str(ck / "lm.safetensors"), strict=True)
    # float32 master copy; the model holds the compute-precision copy.
    master = model.trainable_parameters()
    optimizer.init(master)
    if state["checkpoint"] and not os.environ.get("A3D_DEBUG_SKIP_OPT"):
        # Fill the freshly initialised state in place. Replacing optimizer.state with a new tree
        # resets the optimizer's initialised flag and roughly doubled peak memory on resume.
        saved = mx.load(str(ck / "optimizer.safetensors"))

        def fill(node, path):
            if isinstance(node, dict):
                for key in list(node):
                    child = f"{path}.{key}" if path else key
                    if isinstance(node[key], mx.array):
                        node[key] = mx.array(saved[child])
                    else:
                        fill(node[key], child)
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    fill(item, f"{path}.{i}")

        fill(optimizer.state, "")
        missing = set(saved) - {k for k, _ in tree_flatten(optimizer.state)}
        if missing:
            raise SystemExit(f"optimizer state keys not restored: {sorted(missing)[:5]}")
    low = args.compute == "bfloat16"

    def to_compute(tree):
        if not low:
            return tree
        return tree_map_with_path(lambda path, v: v if path.endswith("A_log") else v.astype(mx.bfloat16), tree)

    if low:
        model.update(to_compute(master))
    mx.eval(master, model.parameters(), optimizer.state)
    say(event="start", segment=state["segments"], step=state["step"], position=state["position"],
        resumed=state["checkpoint"], trainable_params=n_train, lm_dtypes=dtypes, compute=args.compute,
        load_seconds=round(time.monotonic() - started, 1), lr=args.lr)

    def encode(row):
        image = Image.open(prep_image(Path(row["image"]), args.image_cache)).convert("RGB")
        reasoning = row["reasoning"]
        if row.get("caption"):
            # Open the reasoning by describing the image, so the target is grounded in what was shown.
            reasoning = f"Looking at the image: {row['caption']}\n\n{reasoning}"
        messages = [{"role": "system", "content": row["system"]},
                    {"role": "user", "content": [{"type": "image"}, {"type": "text", "text": INSTRUCTION}]},
                    {"role": "assistant", "content": row["code"], "reasoning_content": reasoning}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False,
                                             enable_thinking=True)
        head = tokenizer.apply_chat_template(messages[:2], tokenize=False, add_generation_prompt=True,
                                             enable_thinking=True)
        if not text.startswith(head):
            raise ValueError(f"{row['id']}: assistant turn does not start with the generation prompt")
        full = processor(text=[text], images=[image], return_tensors="np")
        prefix = processor(text=[head], images=[image], return_tensors="np")
        ids = np.asarray(full["input_ids"])[0]
        n_prefix = int(np.asarray(prefix["input_ids"]).shape[1])
        if row.get("max_target_tokens"):
            ids = ids[: n_prefix + int(row["max_target_tokens"])]
        if not np.array_equal(ids[:n_prefix], np.asarray(prefix["input_ids"])[0][:len(ids)]):
            raise ValueError(f"{row['id']}: prompt tokens are not a prefix of the full sequence")
        extra = {k: mx.array(np.asarray(v)) for k, v in full.items() if k not in ("input_ids", "attention_mask", "pixel_values")}
        return ids, n_prefix, mx.array(np.asarray(full["pixel_values"])), extra

    def loss_fn(ids, n_prefix, pixel_values, extra):
        inputs = mx.array(ids[None, :-1])
        targets = mx.array(ids[None, 1:])
        out = model(inputs, pixel_values, None, **extra)
        logits = out.logits.astype(mx.float32)
        ce = nn.losses.cross_entropy(logits, targets, reduction="none")
        mask = (mx.arange(targets.shape[1])[None, :] >= (n_prefix - 1)).astype(mx.float32)
        return (ce * mask).sum() / mask.sum()

    def evaluate(rows):
        model.eval()
        losses = []
        for row in rows:
            ids, n_prefix, pix, extra = encode(row)
            if len(ids) > args.max_tokens:
                continue
            value = loss_fn(ids, n_prefix, pix, extra)
            mx.eval(value)
            losses.append(float(value))
            mx.clear_cache()
        model.train()
        return losses

    rows = [json.loads(line) for line in args.data.open()]
    dev_rows = [json.loads(line) for line in args.dev.open()] if args.dev else []
    total_positions = int(len(rows) * args.epochs)

    if dev_rows and (state["step"] == 0 or args.eval_only):
        t0 = time.monotonic()
        dev = evaluate(dev_rows)
        say(event="dev", step=state["step"], loss=round(float(np.mean(dev)), 4), each=[round(x, 4) for x in dev],
            seconds=round(time.monotonic() - t0, 1), peak_gb=round(mx.get_peak_memory() / 1e9, 2))
        state.setdefault("dev", []).append({"step": state["step"], "loss": float(np.mean(dev))})
    if args.eval_only:
        return

    model.train()
    value_and_grad = nn.value_and_grad(model, loss_fn)
    segment_start = time.monotonic()
    segment_steps = 0
    recent = []
    stop_reason = "data_done"
    while state["position"] < total_positions:
        elapsed = time.monotonic() - segment_start
        if elapsed > args.max_minutes * 60:
            stop_reason = "segment_time"
            break
        if args.budget_minutes and state["train_seconds"] + elapsed > args.budget_minutes * 60:
            stop_reason = "budget"
            break
        if args.max_steps and segment_steps >= args.max_steps:
            stop_reason = "segment_steps"
            break
        row = rows[state["position"] % len(rows)]
        state["position"] += 1
        ids, n_prefix, pix, extra = encode(row)
        if len(ids) > args.max_tokens:
            say(event="skip", id=row["id"], tokens=int(len(ids)))
            mx.clear_cache()
            continue
        t0 = time.monotonic()
        value, grads = value_and_grad(ids, n_prefix, pix, extra)
        if low:
            grads = tree_map_with_path(lambda path, g: g.astype(mx.float32), grads)
        master = optimizer.apply_gradients(grads, master)
        model.update(to_compute(master))
        mx.eval(value, master, model.trainable_parameters(), optimizer.state)
        value = float(value)
        if not math.isfinite(value):
            say(event="abort", reason="non-finite loss", id=row["id"])
            raise SystemExit(3)
        del grads
        mx.clear_cache()
        state["step"] += 1
        segment_steps += 1
        state["tokens"] += int(len(ids))
        recent.append(value)
        say(event="step", step=state["step"], id=row["id"], tokens=int(len(ids)), loss=round(value, 4),
            seconds=round(time.monotonic() - t0, 1), peak_gb=round(mx.get_peak_memory() / 1e9, 2),
            active_gb=round(mx.get_active_memory() / 1e9, 2))

    state["train_seconds"] += time.monotonic() - segment_start
    state["segments"] += 1
    state["finished"] = stop_reason in ("data_done", "budget")
    if dev_rows:
        t0 = time.monotonic()
        dev = evaluate(dev_rows)
        state.setdefault("dev", []).append({"step": state["step"], "loss": float(np.mean(dev))})
        say(event="dev", step=state["step"], loss=round(float(np.mean(dev)), 4), each=[round(x, 4) for x in dev],
            seconds=round(time.monotonic() - t0, 1))
    if not args.no_save:
        name = f"checkpoint-{state['step']:06d}"
        tmp = args.run / (name + ".tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        mx.save_safetensors(str(tmp / "lm.safetensors"), dict(tree_flatten(master["language_model"])))
        mx.save_safetensors(str(tmp / "optimizer.safetensors"), dict(tree_flatten(optimizer.state)))
        final = args.run / name
        shutil.rmtree(final, ignore_errors=True)
        tmp.rename(final)
        previous = state["checkpoint"]
        state["checkpoint"] = name
        if state.get("dev"):
            last = state["dev"][-1]
            best = state.get("best")
            if best is None or last["loss"] < best["loss"]:
                state["best"] = {"step": last["step"], "loss": last["loss"], "checkpoint": name}
        state_file.write_text(json.dumps(state, indent=2) + "\n")
        keep = {name, previous, (state.get("best") or {}).get("checkpoint")}
        for old in args.run.glob("checkpoint-*"):
            if old.name not in keep:
                shutil.rmtree(old, ignore_errors=True)
    else:
        state_file.write_text(json.dumps(state, indent=2) + "\n")
    say(event="segment_end", reason=stop_reason, step=state["step"], position=state["position"],
        segment_steps=segment_steps, mean_loss=round(float(np.mean(recent)), 4) if recent else None,
        train_minutes=round(state["train_seconds"] / 60, 1), tokens=state["tokens"],
        peak_gb=round(mx.get_peak_memory() / 1e9, 2), done=state["position"] >= total_positions)


if __name__ == "__main__":
    main()
