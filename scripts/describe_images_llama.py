"""Have a local vision model turn each reference image into a written asset request.

This is the free, fully local version of "describe the image in detail": one short
llama.cpp process per image through the shared GPU slot, low temperature, no thinking.
The request follows the wording of the CCORE asset dataset's own detailed prompts.
Finished descriptions are skipped; waits while the stream guard is active.
"""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

SLOT = Path.home() / ".cache/gpu-slot/bin/gpu_slot.sh"
STREAMING = Path.home() / ".cache/gpu-slot/STREAMING"
INSTRUCTION = (
    "Look at the object in this image and write a request for a 3D artist to build it. "
    "Use exactly this form:\n"
    "Please create <what it is>. Include <its main parts, as a comma-separated list of what is visible>. "
    "Use <its main colours and materials>. Make the main structure read clearly, with plausible supports, "
    "attachments, and spacing between parts. Use a plain presentation without extra scenery. Keep it static.\n"
    "For a character or creature, start the second sentence with \"Depict\" and say its pose and what it wears or carries. "
    "Mention only what is visible. Reply with the request only, as one paragraph.")


def worker(args):
    if not os.environ.get("GPU_SLOT_HELD"):
        raise SystemExit("Launch through gpu_slot")
    if STREAMING.exists():
        raise SystemExit("Stream guard is active")
    prompt = args.work / "instruction.txt"
    prompt.write_text(INSTRUCTION + "\n")
    command = [args.llama, "--model", args.model, "--mmproj", args.mmproj, "--image", str(args.image),
               "--gpu-layers", "99", "--ctx-size", "8192", "--threads", "8", "--temp", "0.2", "--seed", "42",
               "--predict", "400", "--file", str(prompt), "--single-turn", "--no-display-prompt", "--reasoning", "off"]
    with (args.work / "response.txt").open("w") as out, (args.work / "runtime.log").open("w") as err:
        raise SystemExit(subprocess.run(command, stdout=out, stderr=err, stdin=subprocess.DEVNULL).returncode)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--llama", required=True)
    p.add_argument("--model", required=True, help="GGUF model that writes the description")
    p.add_argument("--mmproj", required=True)
    p.add_argument("--images", type=Path, help="Directory of <id>.png")
    p.add_argument("--out", type=Path, help="Directory for <id>.txt")
    p.add_argument("--runs", type=Path, help="Directory for raw responses and logs")
    p.add_argument("--image", type=Path, help=argparse.SUPPRESS)
    p.add_argument("--work", type=Path, help=argparse.SUPPRESS)
    args = p.parse_args()
    if args.image:
        worker(args)
    args.out.mkdir(parents=True, exist_ok=True)
    for image in sorted(args.images.glob("*.png")):
        target = args.out / f"{image.stem}.txt"
        if target.exists():
            continue
        work = args.runs / image.stem
        work.mkdir(parents=True, exist_ok=True)
        for attempt in range(40):
            while STREAMING.exists():
                time.sleep(300)
            code = subprocess.run(
                [str(SLOT), "capture", "--label", f"describe-{image.stem}", "--json", str(args.runs / f"{image.stem}-gpu.json"),
                 "--", sys.executable, __file__, "--llama", args.llama, "--model", args.model, "--mmproj", args.mmproj,
                 "--image", str(image), "--work", str(work)],
                stdout=(args.runs / f"{image.stem}.log").open("w"), stderr=subprocess.STDOUT).returncode
            if code == 0:
                break
            print(time.strftime("[%H:%M:%S]"), image.stem, f"exit {code}; retry in 2 minutes", flush=True)
            time.sleep(120)
        else:
            raise SystemExit(f"{image.stem}: no description after 40 attempts")
        raw = (work / "response.txt").read_text(errors="replace")
        text = re.split(r"</think>|\[End thinking\]", raw)[-1]
        text = re.sub(r"\[ Prompt:.*", "", text, flags=re.S)
        text = " ".join(text.split()).strip()
        start = text.rfind("Please create")  # the CLI echoes the instruction first
        if start < 0 or len(text) - start < 80:
            raise SystemExit(f"{image.stem}: no usable description; see {work / 'response.txt'}")
        text = text[start:]
        target.write_text(text + "\n")
        print(time.strftime("[%H:%M:%S]"), image.stem, json.dumps(text), flush=True)


if __name__ == "__main__":
    main()
