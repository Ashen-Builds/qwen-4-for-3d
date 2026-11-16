"""Parse/check generated module syntax without executing its JavaScript."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.modules = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attrs = dict(attrs)
            if attrs.get("type") == "module" and not attrs.get("src"):
                self.active = []

    def handle_data(self, data):
        if self.active is not None:
            self.active.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.active is not None:
            self.modules.append("".join(self.active))
            self.active = None


def inspect(path):
    parser = Scripts()
    parser.feed(path.read_text())
    checks = []
    with tempfile.TemporaryDirectory(prefix="qwen-js-check-") as tmp:
        for i, code in enumerate(parser.modules):
            p = Path(tmp) / f"module-{i}.mjs"
            p.write_text(code)
            result = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
            error = next((x.strip() for x in result.stderr.splitlines() if "Error:" in x), None)
            checks.append({"module": i, "characters": len(code),
                           "syntax_valid": result.returncode == 0, "error": error})
    return {"file": path.name, "modules": checks,
            "all_module_syntax_valid": bool(checks) and all(x["syntax_valid"] for x in checks),
            "qualification": "Syntax only; runtime, asset quality and export remain unverified."}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", type=Path)
    args = p.parse_args()
    result = inspect(args.file)
    args.file.with_suffix(".syntax.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
