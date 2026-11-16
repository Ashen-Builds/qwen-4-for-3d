"""Download and hash-check pinned original checkpoints. Never load or run a model."""

import argparse
import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    lock = Path(__file__).resolve().parents[1] / "configs/model-snapshots.json"
    sources = json.loads(lock.read_text())["models"]
    api = HfApi(token=False)
    plans = []
    for source in sources:
        files = []
        for entry in api.list_repo_tree(source["repo"], repo_type="model", revision=source["revision"]):
            # Original checkpoint and companion text/config files only. Excludes
            # alternate GGUFs, projectors, gallery media and executable loaders.
            if not hasattr(entry, "size") or "/" in entry.path:
                continue
            if not (entry.path.endswith((".safetensors", ".json", ".jinja", ".txt"))
                    or entry.path in {"README.md", "LICENSE", "NOTICE"}):
                continue
            files.append({"path": entry.path, "bytes": entry.size,
                          "sha256": getattr(getattr(entry, "lfs", None), "sha256", None),
                          "git_blob": getattr(entry, "blob_id", None)})
        if not any(f["path"].endswith(".safetensors") for f in files):
            raise RuntimeError("No checkpoint shards found")
        plan = {**source, "files": files}
        plans.append(plan)
        print(json.dumps({"role": source["role"], "files": len(files),
                          "bytes": sum(f["bytes"] for f in files)}), flush=True)
    if not args.download:
        return
    args.destination.mkdir(parents=True, exist_ok=True)
    needed = sum(f["bytes"] for p in plans for f in p["files"])
    if shutil.disk_usage(args.destination).free < needed + 20 * 1024**3:
        raise RuntimeError("Insufficient space including 20 GiB reserve")
    for plan in plans:
        folder = args.destination / plan["repo"].replace("/", "--") / plan["revision"]
        folder.mkdir(parents=True, exist_ok=True)

        def copy(file):
            path = Path(hf_hub_download(plan["repo"], file["path"], repo_type="model",
                                       revision=plan["revision"], local_dir=folder, token=False))
            if path.stat().st_size != file["bytes"]:
                raise RuntimeError(f"Size mismatch: {file['path']}")
            sha = hashlib.sha256()
            blob = hashlib.sha1(f"blob {file['bytes']}\0".encode())
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                    sha.update(block)
                    blob.update(block)
            expected = file["sha256"] or file["git_blob"]
            actual = sha.hexdigest() if file["sha256"] else blob.hexdigest()
            if not expected or expected != actual:
                raise RuntimeError(f"Digest mismatch: {file['path']}")
            if file["path"].endswith(".safetensors"):
                print(json.dumps({"role": plan["role"], "verified_shard": file["path"],
                                  "bytes": file["bytes"]}), flush=True)
            return {**file, "sha256": sha.hexdigest(), "verified": True}

        with ThreadPoolExecutor(max_workers=3) as workers:
            plan["files"] = list(workers.map(copy, plan["files"]))
        index = json.loads((folder / "model.safetensors.index.json").read_text())
        inventory = {f["path"] for f in plan["files"]}
        if not set(index["weight_map"].values()) <= inventory:
            raise RuntimeError("Checkpoint index refers to missing shards")
        (folder / "DOWNLOAD_MANIFEST.json").write_text(json.dumps(plan, indent=2) + "\n")
        print(json.dumps({"role": plan["role"], "complete": True,
                          "files": len(plan["files"]),
                          "bytes": sum(f["bytes"] for f in plan["files"])}), flush=True)


if __name__ == "__main__":
    main()
