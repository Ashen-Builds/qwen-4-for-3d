"""Write trained language-model weights back into the original Hugging Face layout.

The trainer saves weights in the MLX layout (keys relative to the language model,
RMSNorm weights stored as w, conv1d weights channel-last). The Hugging Face
checkpoint stores RMSNorm weights as w - 1 and conv1d weights channel-first, under
`model.language_model.*`. Vision and MTP tensors are copied from the original
untouched. CPU only.
"""

import argparse
import json
from pathlib import Path
import shutil

import mlx.core as mx
import numpy as np

mx.set_default_device(mx.cpu)


def load_file(path):
    return mx.load(path)


def save_file(tensors, path, metadata):
    mx.save_safetensors(path, tensors, metadata=metadata)

NORM_SUFFIXES = (".input_layernorm.weight", ".post_attention_layernorm.weight", "model.norm.weight",
                 ".q_norm.weight", ".k_norm.weight")
PREFIX = "model.language_model."


def to_hf(key: str, value: np.ndarray) -> np.ndarray:
    """key is the MLX-side key 'language_model.model.<rest>'."""
    if "conv1d.weight" in key and value.ndim == 3:
        value = np.moveaxis(value, 1, 2)
    if any(key.endswith(s) for s in NORM_SUFFIXES) and value.ndim == 1:
        value = value - 1.0
    return np.ascontiguousarray(value.astype(np.float32))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--weights", type=Path, required=True, help="lm.safetensors written by the trainer")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expect-identical", action="store_true",
                   help="Self-test: the weights are an untrained copy, so the export must equal the original")
    args = p.parse_args()
    trained = {k: np.array(v) for k, v in load_file(str(args.weights)).items()}
    index = json.loads((args.original / "model.safetensors.index.json").read_text())
    shards = sorted(set(index["weight_map"].values()))
    args.out.mkdir(parents=True, exist_ok=True)
    used, report = set(), {"replaced": 0, "copied": 0, "max_abs_diff": 0.0, "max_rel_change": 0.0, "shape_mismatch": []}
    for shard in shards:
        tensors = load_file(str(args.original / shard))
        for key in list(tensors):
            if not key.startswith(PREFIX) or key.startswith(PREFIX + "visual"):
                report["copied"] += 1
                continue
            mlx_key = "model." + key[len(PREFIX):]
            if mlx_key not in trained:
                report["copied"] += 1
                continue
            new = to_hf("language_model." + mlx_key, trained[mlx_key])
            old_dtype = tensors[key].dtype
            old = np.array(tensors[key].astype(mx.float32))
            if new.shape != old.shape:
                report["shape_mismatch"].append([key, list(old.shape), list(new.shape)])
                continue
            diff = float(np.abs(new - old.astype(np.float32)).max())
            scale = float(np.sqrt(np.mean(old.astype(np.float64) ** 2))) + 1e-12
            report["max_abs_diff"] = max(report["max_abs_diff"], diff)
            report["max_rel_change"] = max(report["max_rel_change"], float(np.sqrt(np.mean((new - old) ** 2))) / scale)
            tensors[key] = mx.array(new).astype(old_dtype)
            used.add(mlx_key)
            report["replaced"] += 1
        if not args.expect_identical:
            save_file(tensors, str(args.out / shard), metadata={"format": "pt"})
        del tensors
    report["trained_keys_unused"] = sorted(set(trained) - used)[:20]
    report["trained_keys_total"] = len(trained)
    if report["shape_mismatch"] or report["trained_keys_unused"]:
        print(json.dumps(report, indent=2))
        raise SystemExit("Export mapping is incomplete")
    if args.expect_identical:
        ok = report["max_abs_diff"] < 1e-6
        print(json.dumps({**report, "identical_within_1e-6": ok}))
        raise SystemExit(0 if ok else 1)
    for f in args.original.iterdir():
        if f.is_file() and f.suffix != ".safetensors" and f.name not in ("DOWNLOAD_MANIFEST.json", "STRUCTURE_RECEIPT.json"):
            shutil.copy2(f, args.out / f.name)
    (args.out / "export-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
