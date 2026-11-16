"""Cross-check native GGUF decoding in one task-owned CLI process."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--system", required=True)
    p.add_argument("--binary", default="llama-cli")
    args = p.parse_args()
    if not os.environ.get("GPU_SLOT_HELD"):
        raise SystemExit("Launch through gpu_slot")
    args.out.mkdir(parents=True, exist_ok=True)
    command = [args.binary, "--model", args.model, "--gpu-layers", "99", "--flash-attn", "on",
               "--ctx-size", "65536", "--batch-size", "1024", "--ubatch-size", "512",
               "--threads", "8", "--temp", "0.8", "--top-k", "40", "--top-p", "0.95",
               "--min-p", "0", "--repeat-penalty", "1", "--seed", "42", "--predict", "49152",
               "--system-prompt-file", args.system, "--file", args.prompt,
               "--single-turn", "--no-display-prompt", "--reasoning", "on"]
    started = time.monotonic()
    with (args.out / "response.txt").open("w") as out, (args.out / "runtime.log").open("w") as err:
        child = subprocess.Popen(command, stdout=out, stderr=err)
        (args.out / "pid.json").write_text(json.dumps({"pid": child.pid}) + "\n")
        code = child.wait()
    raw = (args.out / "response.txt").read_text()
    answer = raw.rsplit("</think>", 1)[-1]
    blocks = re.findall(r"```(?:html)?\s*\n(.*?)```", answer, re.S | re.I)
    htmls = [b for b in blocks if "<html" in b.lower()]
    start = answer.lower().find("<!doctype")
    candidate = htmls[-1] if htmls else (answer[start:] if start >= 0 else "")
    complete = "</html>" in candidate.lower()
    if complete:
        (args.out / "generated.html").write_text(candidate.strip() + "\n")
    metrics = {"backend": "llama.cpp", "model_file": Path(args.model).name,
               "elapsed_seconds": time.monotonic() - started, "exit_code": code,
               "process_exited": True, "complete_html": complete, "seed": 42,
               "thinking": True, "quantization": "Q8_0"}
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics), flush=True)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
