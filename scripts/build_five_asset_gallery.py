"""Build one self-contained HTML page: reference image beside each model's exported result."""

import argparse
import base64
import html
import json
from pathlib import Path
import subprocess
import tempfile

REASONS = {
    "no_html": "No complete program",
    "page_error": "Program crashed",
    "no_export": "Nothing exported",
    "invalid_glb": "Export was not a valid GLB",
    "harness_error": "Test harness error",
    "stage_failed": "Could not stage page",
    "missing": "Not run yet",
}


def jpeg_data(path: Path, size: int) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "x.jpg"
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", "-Z", str(size), str(path), "--out", str(out)],
                       check=True, capture_output=True)
        return "data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()


def cell(out_dir: Path) -> str:
    result_file = out_dir / "result.json"
    if not result_file.exists():
        return f'<div class="cell fail"><p>{REASONS["missing"]}</p></div>'
    r = json.loads(result_file.read_text())
    if r["status"] == "ok" and (out_dir / "view-front.png").exists():
        g = r["glb"]
        bits = [f'{g["triangles"]:,} triangles' if g.get("triangles") else f'{g["meshes"]} meshes']
        if g.get("animations"):
            bits.append("animated")
        front, back = jpeg_data(out_dir / "view-front.png", 640), jpeg_data(out_dir / "view-back.png", 640)
        return (f'<div class="cell"><img src="{front}" data-alt="{back}" alt="" onclick="const s=this.src;this.src=this.dataset.alt;this.dataset.alt=s">'
                f'<p>{" · ".join(bits)}</p></div>')
    detail = (r.get("page_errors") or [""])[0]
    reason = REASONS.get(r["status"], r["status"])
    text = f"{reason}: {detail}" if detail else reason
    return f'<div class="cell fail"><p>{html.escape(text[:140])}</p></div>'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--images", type=Path, required=True)
    p.add_argument("--outputs", type=Path, required=True)
    p.add_argument("--arm", action="append", required=True, help="dir=Column title, repeatable, in column order")
    p.add_argument("--page", type=Path, required=True)
    args = p.parse_args()
    arms = [a.split("=", 1) for a in args.arm]
    rows = []
    for image in sorted(args.images.glob("*.png")):
        cells = [f'<div class="cell"><img src="{jpeg_data(image, 640)}" alt=""></div>']
        cells += [cell(args.outputs / d / image.stem) for d, _ in arms]
        rows.append("".join(cells))
    heads = "".join(f"<div class='head'>{html.escape(t)}</div>" for t in ["Reference image"] + [t for _, t in arms])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Image to 3D test</title><style>
:root{{--bg:#14161a;--panel:#1e2127;--line:#2c3038;--text:#e8eaee;--mute:#9aa1ad;--bad:#e0806f}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:20px 16px 40px}}
.grid{{display:grid;grid-template-columns:repeat({len(arms) + 1},minmax(0,1fr));gap:10px;max-width:1500px;margin:0 auto}}
.head{{font-weight:600;padding:6px 2px;position:sticky;top:0;background:var(--bg);z-index:1}}
.cell{{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column}}
.cell img{{width:100%;aspect-ratio:1;object-fit:cover;display:block;cursor:pointer}}
.cell p{{margin:0;padding:8px 10px;color:var(--mute);font-size:13px}}
.fail{{aspect-ratio:1;align-items:center;justify-content:center;text-align:center}}.fail p{{color:var(--bad);font-size:15px;padding:16px}}
@media(max-width:700px){{.grid{{gap:6px}}.cell p{{font-size:11px;padding:5px 6px}}.fail p{{font-size:12px;padding:6px}}.head{{font-size:12px}}}}
</style></head><body><div class="grid">{heads}{"".join(rows)}</div></body></html>
"""
    args.page.write_text(page)
    print(f"{args.page} {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
