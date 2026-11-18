"""Preserve raw model HTML; adapt dependency URLs and cap preview frames equally."""

import argparse
import hashlib
import json
from pathlib import Path
import re


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    args = p.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    raw = (args.run / "generated.html").read_text()
    (args.destination / "raw-model.html").write_text(raw)
    replacements = []

    def local(match):
        url = match.group(0)
        tail = re.sub(r"https://(?:cdn\.jsdelivr\.net/npm|unpkg\.com)/three@[^/]+/", "", url)
        if tail == "+esm":
            tail = "build/three.module.js"
        target = "/vendor/three/" + tail
        replacements.append({"from": url, "to": target})
        return target

    html = re.sub(r"https://(?:cdn\.jsdelivr\.net/npm|unpkg\.com)/three@[^/\"'\s]+/[^\"'\s<]*", local, raw)
    html = re.sub(r"https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^/]+/three\.module(?:\.min)?\.js",
                  "/vendor/three/build/three.module.js", html)
    prelude = """<script>
    (() => { const raf=window.requestAnimationFrame.bind(window); let last=-Infinity, cur=-1;
      // Cap at 60 fps per frame, not per callback: every callback queued for an accepted frame runs,
      // so a render loop cannot starve a second requestAnimationFrame user such as an export handler.
      window.requestAnimationFrame=cb=>raf(function tick(t){
        if(t===cur||t-last>=1000/60-0.5){if(t!==cur){last=t;cur=t}cb(t)}else raf(tick);
      });
    })();
    </script>"""
    html = re.sub(r"<head\b[^>]*>", lambda m: m.group(0) + prelude, html, count=1, flags=re.I)
    (args.destination / "generated.html").write_text(html)
    (args.destination / "adaptation.json").write_text(json.dumps({
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "served_sha256": hashlib.sha256(html.encode()).hexdigest(),
        "dependency_rewrites": replacements, "preview_fps_cap": 60,
        "asset_geometry_or_animation_edited": False}, indent=2) + "\n")


if __name__ == "__main__":
    main()
