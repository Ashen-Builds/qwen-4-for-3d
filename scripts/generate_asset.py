"""Run one task-owned MLX model, stream evidence, then exit to release all weights."""

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--adapter", type=Path, help="Frozen adapter directory for a future checkpoint; omitted for untouched CCORE")
    p.add_argument("--prompt", type=Path)
    p.add_argument("--card", type=Path)
    p.add_argument("--max-tokens", type=int, default=32768)
    p.add_argument("--benchmark", action="store_true")
    p.add_argument("--no-thinking", action="store_true")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gpu-kind", default="mlx")
    args = p.parse_args()
    if not os.environ.get("GPU_SLOT_HELD"):
        raise SystemExit("Launch through gpu_slot; direct GPU launches are refused")
    if Path.home().joinpath(".cache/gpu-slot/STREAMING").exists():
        raise SystemExit("Stream guard is active")

    import mlx.core as mx
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler

    if args.out.exists() and any((args.out / name).exists() for name in ["metrics.json", "response.txt"]):
        raise SystemExit("Preserve existing run evidence; choose a new output directory")
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    load_options = {"tokenizer_config": {"trust_remote_code": False}}
    if args.adapter is not None:
        if not args.adapter.is_dir():
            raise SystemExit("Adapter directory missing")
        load_options["adapter_path"] = str(args.adapter)
        adapter_files = []
        for file in sorted(args.adapter.iterdir()):
            if file.is_file() and file.suffix in {".json", ".safetensors"}:
                adapter_files.append({"file": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    else:
        adapter_files = []
    (args.out / "adapter-input.json").write_text(json.dumps({"adapter_present": args.adapter is not None, "files": adapter_files}, indent=2) + "\n")
    model, tokenizer = load(args.model, **load_options)
    model.eval()
    loaded = time.monotonic()
    mx.set_cache_limit(2 * 1024**3)
    if args.benchmark:
        messages = [{"role": "user", "content": "Write a Python function that returns the first n Fibonacci numbers, with type hints and a short explanation."}]
    else:
        card = args.card.read_text()
        section = card.split("### System prompt", 1)[1]
        system = re.search(r"```(?:text)?\s*\n(.*?)```", section, re.S).group(1).strip()
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": args.prompt.read_text().strip()}]
    prompt_ids = tokenizer.apply_chat_template(messages, tokenize=True,
                                               add_generation_prompt=True,
                                               return_dict=False,
                                               enable_thinking=not (args.benchmark or args.no_thinking))
    (args.out / "input.json").write_text(json.dumps({"messages": messages,
        "token_ids": prompt_ids, "seed": args.seed, "thinking": not (args.benchmark or args.no_thinking), "temperature": 0.8,
        "top_p": 0.95, "top_k": 40, "max_tokens": args.max_tokens}, indent=2) + "\n")
    mx.random.seed(args.seed)
    sampler = make_sampler(temp=0.8, top_p=0.95, top_k=40)
    last = None
    last_report = 0
    with (args.out / "response.txt").open("w") as f:
        for response in stream_generate(model, tokenizer, prompt=prompt_ids,
                                         max_tokens=args.max_tokens, sampler=sampler,
                                         prefill_step_size=512):
            f.write(response.text)
            last = response
            if response.generation_tokens - last_report >= 256:
                f.flush()
                progress = {"tokens": response.generation_tokens,
                            "tokens_per_second": response.generation_tps,
                            "peak_gb": response.peak_memory,
                            "elapsed_s": time.monotonic() - loaded}
                (args.out / "progress.json").write_text(json.dumps(progress) + "\n")
                print(json.dumps(progress), flush=True)
                last_report = response.generation_tokens
    if last is None:
        raise RuntimeError("Model returned no generation response")
    metrics = {"model_directory": Path(args.model).name, "pid": os.getpid(),
               "load_seconds": loaded - started, "elapsed_seconds": time.monotonic() - started,
               "prompt_tokens": last.prompt_tokens, "prompt_tps": last.prompt_tps,
               "generation_tokens": last.generation_tokens,
               "generation_tps": last.generation_tps, "peak_gb": last.peak_memory,
               "finish_reason": last.finish_reason,
               "prompt_token_sha256": hashlib.sha256(json.dumps(prompt_ids).encode()).hexdigest(),
               "versions": {x: importlib.metadata.version(x) for x in ["mlx", "mlx-lm", "transformers"]}}
    raw = (args.out / "response.txt").read_text()
    if not args.benchmark:
        answer = raw.rsplit("</think>", 1)[-1]
        blocks = re.findall(r"```(?:html)?\s*\n(.*?)```", answer, re.S | re.I)
        htmls = [x for x in blocks if "<html" in x.lower() or "<!doctype" in x.lower()]
        candidate = htmls[-1] if htmls else answer[answer.lower().find("<!doctype"):]
        if "</html>" in candidate.lower():
            (args.out / "generated.html").write_text(candidate.strip() + "\n")
            metrics["complete_html"] = True
        else:
            metrics["complete_html"] = False
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics), flush=True)


if __name__ == "__main__":
    main()
