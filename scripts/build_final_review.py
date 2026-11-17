"""Stage the frozen overnight GLB comparison without loading a model or renderer."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    # Staging is intentionally separate from source, weights and private run logs.
    if out == repo or repo in out.parents:
        raise SystemExit("Choose a deliverable directory outside the repository")
    files = {
        "viewer/final-review.html": "final-review/index.html",
        "viewer/final-review.js": "final-review/final-review.js",
        "eval/baselines/babylon-bf16-20261116/asset.glb": "diagnostic-thinking48/control/asset.glb",
        "eval/checkpoints/astra-thinking48-diagnostic/asset.glb": "diagnostic-thinking48/ours/asset.glb",
        "eval/baselines/babylon-20261116/ccore.glb": "ccore/asset.glb",
    }
    for arm in ("waterwheel-control", "waterwheel-astra", "orrery-control"):
        files[f"eval/final-tests/overnight-20261117/{arm}/asset.glb"] = f"final-tests/{arm}/asset.glb"
    missing = [name for name in files if not (repo / name).is_file()]
    three = repo / "node_modules/three"
    if missing or not (three / "build/three.module.js").is_file():
        raise SystemExit(f"Missing inputs: {missing}; install pinned dependencies with npm ci if needed")
    manifest = []
    for source, destination in files.items():
        src, dst = repo / source, out / destination
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest.append({"source": source, "destination": destination,
                         "bytes": dst.stat().st_size,
                         "sha256": hashlib.sha256(dst.read_bytes()).hexdigest()})
    for name in ("build", "examples/jsm"):
        shutil.copytree(three / name, out / "vendor/three" / name, dirs_exist_ok=True)
    shutil.copy2(three / "LICENSE", out / "vendor/three/LICENSE")
    (out / "final-review/staging-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Staged {len(files)} frozen files at {out / 'final-review'}")


if __name__ == "__main__":
    main()
