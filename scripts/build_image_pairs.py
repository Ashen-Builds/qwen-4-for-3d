"""Build image-to-program pairs from the CCORE asset dataset: its own render + its own program.

CPU only. Writes images and train/dev JSONL with token counts. The dataset's published
validation split becomes the dev set and is never trained on.
"""

import argparse
import glob
import json
from pathlib import Path

import pyarrow.parquet as pq
from transformers import AutoTokenizer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", type=Path, required=True)
    p.add_argument("--tokenizer", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    (args.out / "images").mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(str(args.tokenizer))
    images = {}
    for f in sorted(glob.glob(str(args.dataset / "previews/*.parquet"))):
        for r in pq.read_table(f).to_pylist():
            path = args.out / "images" / f"{r['id']}.png"
            if not path.exists():
                path.write_bytes(r["image"]["bytes"])
            images[r["id"]] = str(path)
    counts = {}
    for split in ("train", "validation"):
        rows = []
        for f in sorted(glob.glob(str(args.dataset / f"data/{split}-*.parquet"))):
            rows += pq.read_table(f).to_pylist()
        name = "train" if split == "train" else "dev"
        with (args.out / f"{name}.jsonl").open("w") as out:
            for r in rows:
                msgs = r["messages"]
                assistant = [m for m in msgs if m["role"] == "assistant"]
                system = [m for m in msgs if m["role"] == "system"]
                user = [m for m in msgs if m["role"] == "user"]
                if len(assistant) != 1 or r["id"] not in images:
                    continue
                reasoning = assistant[0].get("reasoning_content") or ""
                code = assistant[0]["content"] or ""
                n = len(tok(reasoning + code, add_special_tokens=False)["input_ids"])
                out.write(json.dumps({"id": r["id"], "title": r["title"], "domain": r["domain"],
                                      "image": images[r["id"]], "system": system[0]["content"] if system else "",
                                      "original_user": user[0]["content"] if user else "",
                                      "reasoning": reasoning, "code": code, "target_tokens": n}) + "\n")
                counts[name] = counts.get(name, 0) + 1
    print(json.dumps({"images": len(images), **counts}))


if __name__ == "__main__":
    main()
