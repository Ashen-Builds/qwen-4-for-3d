"""Likeness between a reference image and an exported asset's renders.

Uses the base model's own vision tower on CPU (no GPU slot, no paid service): each
image becomes the mean of its vision tokens, and likeness is the cosine similarity
between the reference and the better of the front and back renders. Scores are
only comparable within one panel. `--check` reports how often a render is closer
to its own reference than to every other reference in the panel.
"""

import argparse
import json
from pathlib import Path

import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="Hugging Face checkpoint directory with the vision tower")
    p.add_argument("--references", type=Path, required=True, help="Directory of reference images named <id>.png")
    p.add_argument("--outputs", type=Path, nargs="+", required=True,
                   help="One or more roots laid out as <root>/<arm>/<id>/view-front.png")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()

    import mlx.core as mx
    mx.set_default_device(mx.cpu)
    from mlx_vlm import load
    from PIL import Image

    model, processor = load(args.model)
    image_processor = processor.image_processor
    cache = {}

    def embed(path: Path):
        key = str(path)
        if key not in cache:
            image = Image.open(path).convert("RGB").resize((448, 448), Image.LANCZOS)
            feats = image_processor(images=[image], return_tensors="np")
            pixels = mx.array(np.asarray(feats["pixel_values"])).astype(model.vision_tower.patch_embed.proj.weight.dtype)
            grid = mx.array(np.asarray(feats["image_grid_thw"]))
            hidden, _ = model.vision_tower(pixels, grid)
            v = np.array(hidden.astype(mx.float32)).mean(axis=0)
            cache[key] = v / (np.linalg.norm(v) + 1e-9)
        return cache[key]

    refs = {f.stem: embed(f) for f in sorted(args.references.glob("*.png"))}
    rows = []
    for root in args.outputs:
        for front in sorted(root.glob("*/*/view-front.png")):
            name, arm = front.parent.name, front.parent.parent.name
            if name not in refs:
                continue
            views = [embed(front)]
            back = front.with_name("view-back.png")
            if back.exists():
                views.append(embed(back))
            own = max(float(v @ refs[name]) for v in views)
            row = {"root": root.name, "arm": arm, "id": name, "likeness": round(own, 4)}
            if args.check:
                others = {k: max(float(v @ r) for v in views) for k, r in refs.items()}
                row["nearest"] = max(others, key=others.get)
                row["own_is_nearest"] = row["nearest"] == name
            rows.append(row)
    summary = {"n": len(rows)}
    if args.check and rows:
        summary["own_is_nearest_rate"] = round(sum(r["own_is_nearest"] for r in rows) / len(rows), 3)
    args.out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
