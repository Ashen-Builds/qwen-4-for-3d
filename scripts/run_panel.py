"""Run the image-to-asset scoring panel: every panel image, several seeds, several models.

One llama.cpp process per generation, each through the shared GPU slot; export, validation
and renders run on CPU after each one. Seeds are the outer loop and models alternate per
image, so a partial run is still a balanced comparison. Finished items are skipped, so the
command can be re-run. Waits while the stream guard is active and when the slot is refused.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import time

REPO = Path(__file__).resolve().parent.parent
SLOT = Path.home() / ".cache/gpu-slot/bin/gpu_slot.sh"
STREAMING = Path.home() / ".cache/gpu-slot/STREAMING"


def say(*parts):
    print(time.strftime("[%H:%M:%S]"), *parts, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--runs", type=Path, required=True)
    p.add_argument("--outputs", type=Path, required=True)
    p.add_argument("--arm", action="append", required=True, help="name=/path/to/model.gguf, repeatable")
    p.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44])
    p.add_argument("--llama", required=True)
    p.add_argument("--mmproj", required=True)
    p.add_argument("--kind", help="Only run manifest items of this kind")
    p.add_argument("--arm-prompts", action="append", default=[],
                   help="name=/dir of <id>.txt: that arm gets the written description instead of the image")
    args = p.parse_args()
    arms = [a.split("=", 1) for a in args.arm]
    written = {k: Path(v) for k, v in (a.split("=", 1) for a in args.arm_prompts)}
    manifest = json.loads((args.panel / "manifest.json").read_text())
    items = [m for m in manifest if not args.kind or m["kind"] == args.kind]
    prompts = REPO / "eval/prompts/five-asset-20261117"
    args.runs.mkdir(parents=True, exist_ok=True)
    total = len(items) * len(args.seeds) * len(arms)
    hard_failures = 0
    for seed in args.seeds:
        for item in items:
            for arm, model in arms:
                run = args.runs / f"seed{seed}" / arm / item["id"]
                out = args.outputs / f"seed{seed}" / arm / item["id"]
                if (args.runs / "STOP").exists():
                    say("STOP file present; exiting")
                    return
                if not (run / "metrics.json").exists():
                    refused = 0
                    while True:
                        waited = False
                        while STREAMING.exists():
                            if not waited:
                                say("stream guard active; waiting")
                                waited = True
                            time.sleep(300)
                        run.parent.mkdir(parents=True, exist_ok=True)
                        say(f"seed{seed} {arm} {item['id']}: generating")
                        if arm in written:
                            request = ["--prompt", str(written[arm] / f"{item['id']}.txt")]
                        else:
                            request = ["--mmproj", args.mmproj, "--image", str(args.panel / "images" / f"{item['id']}.png"),
                                       "--prompt", str(prompts / "image-instruction.txt")]
                        code = subprocess.run(
                            [str(SLOT), "capture", "--label", f"panel-{arm}-{item['id']}-s{seed}",
                             "--json", str(run.parent / f"{item['id']}-gpu.json"), "--",
                             "python3", str(REPO / "scripts/generate_asset_llama_image.py"),
                             "--binary", args.llama, "--model", model, *request, "--out", str(run),
                             "--system", str(prompts / "system.txt"), "--seed", str(seed)],
                            stdout=(run.parent / f"{item['id']}.log").open("w"), stderr=subprocess.STDOUT).returncode
                        if code == 75 or (code != 0 and not (run / "response.txt").exists()):
                            refused += 1
                            if refused >= 40:
                                say("GPU slot refused 40 times in a row; exiting")
                                raise SystemExit(75)
                            say(f"slot not granted (exit {code}); retry {refused} in 2 minutes")
                            time.sleep(120)
                            continue
                        break
                    say(f"seed{seed} {arm} {item['id']}: generation exit {code}")
                    if code != 0 or not (run / "metrics.json").exists():
                        hard_failures += 1
                        if hard_failures >= 3:
                            say("three generation failures; exiting")
                            raise SystemExit(code or 1)
                        continue
                    hard_failures = 0
                if not (out / "result.json").exists():
                    r = subprocess.run(["node", str(REPO / "scripts/export_and_render.mjs"), "--run", str(run), "--out", str(out)],
                                       capture_output=True, text=True)
                    say(f"seed{seed} {arm} {item['id']}: {r.stdout.strip()[-120:]}")
        done = sum(1 for _ in args.outputs.glob("seed*/*/*/result.json"))
        say(f"seed {seed} pass complete; results so far {done} (this invocation covers {total})")
    say("ALLDONE")


if __name__ == "__main__":
    main()
