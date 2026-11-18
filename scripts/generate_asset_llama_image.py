"""Asset generation: one task-owned llama.cpp process per request, then exit.

With --image the request is the image plus a short instruction; without it the
prompt file is the whole request (a written description).
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="GGUF text model")
    p.add_argument("--mmproj", help="GGUF vision projector; needed with --image")
    p.add_argument("--image", type=Path, help="Reference image; omit for a text-only request")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--prompt", required=True, help="File holding the user request (the instruction that accompanies the image, or the full description)")
    p.add_argument("--system", required=True, help="File holding the system prompt")
    p.add_argument("--binary", default="llama-cli")
    p.add_argument("--predict", type=int, default=32768)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    if not os.environ.get("GPU_SLOT_HELD"):
        raise SystemExit("Launch through gpu_slot")
    if Path.home().joinpath(".cache/gpu-slot/STREAMING").exists():
        raise SystemExit("Stream guard is active")
    if args.out.exists() and any((args.out / n).exists() for n in ["metrics.json", "response.txt"]):
        raise SystemExit("Preserve existing run evidence; choose a new output directory")
    args.out.mkdir(parents=True, exist_ok=True)
    if args.image and not args.mmproj:
        raise SystemExit("--image needs --mmproj")
    media = ["--mmproj", args.mmproj, "--image", str(args.image)] if args.image else []
    command = [args.binary, "--model", args.model, *media,
               "--gpu-layers", "99", "--flash-attn", "on",
               "--ctx-size", "65536", "--batch-size", "1024", "--ubatch-size", "512",
               "--threads", "8", "--temp", "0.8", "--top-k", "40", "--top-p", "0.95",
               "--min-p", "0", "--repeat-penalty", "1", "--seed", str(args.seed), "--predict", str(args.predict),
               "--system-prompt-file", args.system, "--file", args.prompt,
               "--single-turn", "--no-display-prompt", "--reasoning", "on"]
    (args.out / "input.json").write_text(json.dumps({
        "image": args.image.name if args.image else None,
        "image_sha256": hashlib.sha256(args.image.read_bytes()).hexdigest() if args.image else None,
        "user": Path(args.prompt).read_text().strip(), "system": Path(args.system).read_text().strip(),
        "command": command}, indent=2) + "\n")
    started = time.monotonic()
    with (args.out / "response.txt").open("w") as out, (args.out / "runtime.log").open("w") as err:
        child = subprocess.Popen(command, stdout=out, stderr=err, stdin=subprocess.DEVNULL)
        (args.out / "pid.json").write_text(json.dumps({"pid": child.pid}) + "\n")
        code = child.wait()
    raw = (args.out / "response.txt").read_text(errors="replace")
    answer = re.split(r"</think>|\[End thinking\]", raw)[-1]
    blocks = re.findall(r"```(?:html)?\s*\n(.*?)```", answer, re.S | re.I)
    htmls = [b for b in blocks if "<html" in b.lower() or "<!doctype" in b.lower()]
    start = answer.lower().find("<!doctype")
    candidate = htmls[-1] if htmls else (answer[start:] if start >= 0 else "")
    end = candidate.lower().rfind("</html>")
    complete = end >= 0
    if complete:
        (args.out / "generated.html").write_text(candidate[:end + len("</html>")].strip() + "\n")
    log = (args.out / "runtime.log").read_text(errors="replace")
    metrics = {"backend": "llama.cpp", "model_file": Path(args.model).name, "mmproj_file": Path(args.mmproj).name if args.image else None,
               "elapsed_seconds": round(time.monotonic() - started, 2), "exit_code": code,
               "response_chars": len(raw), "complete_html": complete, "seed": args.seed,
               "thinking": True, "predict_cap": args.predict,
               "image_loaded": ("Loaded media from" in raw or "Loaded media from" in log) if args.image else None}
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics), flush=True)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
