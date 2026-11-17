"""Caption training renders with the base model's own vision, so each training target can
open by describing its image. Resumable; launch through gpu_slot. No paid service."""

import argparse
import json
import os
from pathlib import Path
import re
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--rows", type=Path, nargs="+", required=True)
    p.add_argument("--image-cache", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-minutes", type=float, default=30)
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()
    if not os.environ.get("GPU_SLOT_HELD"):
        raise SystemExit("Launch through gpu_slot")
    from mlx_vlm import generate, load
    from mlx_vlm.prompt_utils import apply_chat_template
    import mlx.core as mx

    done = {}
    if args.out.exists():
        for line in args.out.open():
            r = json.loads(line)
            done[r["id"]] = r
    rows, seen = [], set()
    for f in args.rows:
        for line in f.open():
            r = json.loads(line)
            if r["id"] not in seen and r["id"] not in done:
                seen.add(r["id"])
                rows.append(r)
    if args.limit:
        rows = rows[: args.limit]
    model, processor = load(args.model)
    started = time.monotonic()
    n = 0
    with args.out.open("a") as out:
        for r in rows:
            if time.monotonic() - started > args.max_minutes * 60:
                break
            question = (f"This picture shows a game asset called \"{r['title']}\". In one sentence, describe what the "
                        "picture shows: the subject, its main parts, their colours and the pose. Do not mention that "
                        "it is a render, a model or low-poly.")
            prompt = apply_chat_template(processor, model.config, question, num_images=1, enable_thinking=False)
            image = str(args.image_cache / f"{r['id']}.png")
            result = generate(model, processor, prompt, image=[image], max_tokens=90, verbose=False, enable_thinking=False)
            text = getattr(result, "text", result).strip()
            text = re.sub(r"\s+", " ", text)
            m = re.match(r"(.+?[.!?])(\s|$)", text)
            sentence = m.group(1) if m else text
            ok = 25 <= len(sentence) <= 420 and not re.search(r"HTML|Three\.js|GLB|export", sentence, re.I)
            out.write(json.dumps({"id": r["id"], "title": r["title"], "caption": sentence, "ok": ok, "raw": text[:500]}) + "\n")
            out.flush()
            n += 1
            mx.clear_cache()
    print(json.dumps({"captioned": n, "remaining": len(rows) - n, "seconds": round(time.monotonic() - started, 1)}))


if __name__ == "__main__":
    main()
