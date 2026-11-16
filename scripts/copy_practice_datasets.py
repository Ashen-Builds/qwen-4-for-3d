"""Copy pinned public datasets only; never download models or execute dataset code."""

import argparse
import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download


SOURCES = [
    {
        "repo": "ccore/ThreeJS-3D-Scenes",
        "revision": "57b77a19d38eee8316c8b1f9e71c772046d9f48c",
        "license": "MIT, to the extent of publisher rights",
        "directories": [""],
        "recursive": True,
        "root_files": [],
    },
    {
        "repo": "3dcodeverse/3dcodeverse-2m",
        "revision": "1d3935d94760922ef7a55f4a1a3e19a3b90ec702",
        "license": "CC-BY-NC-SA-4.0; source terms also apply; research only",
        "directories": [
            "data/text",
            "finetune/sft/blender",
            "finetune/sft/blender_bootstrapped",
            "finetune/sft/threejs",
        ],
        "recursive": True,
        "root_files": [
            "README.md", "LICENSE", "dataset_info_text.json",
            "finetune/README.md", "finetune/dataset_info.json", "finetune/mixes.json",
            "finetune/test/blender.parquet", "finetune/test/threejs.parquet",
        ],
    },
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--download", action="store_true", help="Without this, inventory only.")
    args = parser.parse_args()
    api = HfApi(token=False)
    plans = []
    for source in SOURCES:
        entries = {}
        for directory in source["directories"]:
            for entry in api.list_repo_tree(
                source["repo"], repo_type="dataset", revision=source["revision"],
                path_in_repo=directory, recursive=source["recursive"],
            ):
                if hasattr(entry, "size"):
                    entries[entry.path] = entry
        # Targeted directories avoid enumerating the million-file media archive.
        for filename in source["root_files"]:
            found = api.get_paths_info(
                source["repo"], paths=[filename], repo_type="dataset",
                revision=source["revision"],
            )
            if found:
                entries[filename] = found[0]
            elif filename != "LICENSE":
                raise RuntimeError(f"Required source file missing: {source['repo']}/{filename}")
        files = []
        for entry in sorted(entries.values(), key=lambda f: f.path):
            lfs = getattr(entry, "lfs", None)
            files.append({"path": entry.path, "bytes": entry.size,
                          "sha256": getattr(lfs, "sha256", None),
                          "git_blob": getattr(entry, "blob_id", None)})
        plan = {"repo": source["repo"], "revision": source["revision"],
                "license": source["license"], "files": files}
        plans.append(plan)
        print(json.dumps({"repo": source["repo"], "files": len(files),
                          "bytes": sum(f["bytes"] for f in files)}), flush=True)
    if not args.download:
        return
    args.destination.mkdir(parents=True, exist_ok=True)
    required = sum(f["bytes"] for p in plans for f in p["files"])
    if shutil.disk_usage(args.destination).free < required + 20 * 1024**3:
        raise RuntimeError("Insufficient free space, including 20 GiB reserve")
    for plan in plans:
        local_dir = args.destination / plan["repo"].replace("/", "--") / plan["revision"]
        local_dir.mkdir(parents=True, exist_ok=True)

        def copy_one(file):
            path = Path(hf_hub_download(
                plan["repo"], file["path"], repo_type="dataset",
                revision=plan["revision"], local_dir=local_dir, token=False,
            ))
            if path.stat().st_size != file["bytes"]:
                raise RuntimeError(f"Size mismatch: {file['path']}")
            sha256 = hashlib.sha256()
            git_blob = hashlib.sha1(f"blob {file['bytes']}\0".encode())
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    sha256.update(block)
                    git_blob.update(block)
            if file["sha256"]:
                if sha256.hexdigest() != file["sha256"]:
                    raise RuntimeError(f"SHA256 mismatch: {file['path']}")
            elif file["git_blob"]:
                if git_blob.hexdigest() != file["git_blob"]:
                    raise RuntimeError(f"Git blob mismatch: {file['path']}")
            else:
                raise RuntimeError(f"No upstream digest: {file['path']}")
            return {**file, "sha256": sha256.hexdigest(), "verified": True}

        with ThreadPoolExecutor(max_workers=4) as executor:
            plan["files"] = list(executor.map(copy_one, plan["files"]))
        (local_dir / "COPY_MANIFEST.json").write_text(json.dumps(plan, indent=2) + "\n")
        print(json.dumps({"repo": plan["repo"], "verified_files": len(plan["files"]),
                          "bytes": sum(f["bytes"] for f in plan["files"])}), flush=True)


if __name__ == "__main__":
    main()
