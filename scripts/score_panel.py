"""Score the panel: working-GLB rate per model, a paired comparison, and likeness.

A try counts as working when its result.json status is "ok": the program ran, its own
Export button produced a file, and the validator found zero errors. The paired comparison
looks at the same image and seed on both models; the sign test uses only the pairs where
exactly one model worked.
"""

import argparse
import json
from math import comb
from pathlib import Path


def sign_test(a_only: int, b_only: int) -> float:
    n = a_only + b_only
    if n == 0:
        return 1.0
    k = min(a_only, b_only)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--outputs", type=Path, required=True)
    p.add_argument("--arms", nargs=2, required=True, metavar=("BASELINE", "CANDIDATE"))
    p.add_argument("--likeness", type=Path, nargs="*", default=[])
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--md", type=Path)
    args = p.parse_args()
    manifest = {m["id"]: m for m in json.loads((args.panel / "manifest.json").read_text())}
    a, b = args.arms
    status = {}
    for f in args.outputs.glob("seed*/*/*/result.json"):
        seed, arm, pid = f.parts[-4], f.parts[-3], f.parts[-2]
        if pid in manifest and arm in (a, b):
            status[(seed, arm, pid)] = json.loads(f.read_text())["status"]
    like = {}
    for lf in args.likeness:
        for r in json.loads(lf.read_text())["rows"]:
            like[(r["root"], r["arm"], r["id"])] = r["likeness"]
    pairs = sorted({(s, pid) for (s, arm, pid) in status} & {(s, pid) for (s, arm, pid) in status if arm == a}
                   & {(s, pid) for (s, arm, pid) in status if arm == b})

    def block(keys):
        out = {"pairs": len(keys)}
        for arm in (a, b):
            oks = [status[(s, arm, pid)] == "ok" for s, pid in keys]
            out[arm] = {"working": sum(oks), "rate": round(sum(oks) / len(oks), 3) if oks else None}
        both = sum(status[(s, a, pid)] == "ok" and status[(s, b, pid)] == "ok" for s, pid in keys)
        a_only = sum(status[(s, a, pid)] == "ok" and status[(s, b, pid)] != "ok" for s, pid in keys)
        b_only = sum(status[(s, a, pid)] != "ok" and status[(s, b, pid)] == "ok" for s, pid in keys)
        out.update({"both": both, f"only_{a}": a_only, f"only_{b}": b_only, "neither": len(keys) - both - a_only - b_only,
                    "sign_test_p": round(sign_test(a_only, b_only), 4)})
        la = [like[(s, a, pid)] for s, pid in keys if status[(s, a, pid)] == "ok" and (s, a, pid) in like]
        lb = [like[(s, b, pid)] for s, pid in keys if status[(s, b, pid)] == "ok" and (s, b, pid) in like]
        diffs = [like[(s, b, pid)] - like[(s, a, pid)] for s, pid in keys
                 if status[(s, a, pid)] == "ok" and status[(s, b, pid)] == "ok" and (s, a, pid) in like and (s, b, pid) in like]
        if la and lb:
            out["likeness"] = {a: round(sum(la) / len(la), 4), b: round(sum(lb) / len(lb), 4),
                               "paired_n": len(diffs),
                               "paired_mean_diff": round(sum(diffs) / len(diffs), 4) if diffs else None,
                               f"{b}_closer": sum(d > 0 for d in diffs)}
        return out

    groups = {"all": pairs}
    for kind in sorted({m["kind"] for m in manifest.values()}):
        groups[f"kind={kind}"] = [k for k in pairs if manifest[k[1]]["kind"] == kind]
    for cat in ("character",):
        groups[f"category={cat}"] = [k for k in pairs if manifest[k[1]]["category"] == cat]
        groups[f"category=not {cat}"] = [k for k in pairs if manifest[k[1]]["category"] != cat]
    for seed in sorted({s for s, _ in pairs}):
        groups[seed] = [k for k in pairs if k[0] == seed]
    scores = {name: block(keys) for name, keys in groups.items() if keys}
    reasons = {}
    for (s, arm, pid), st in status.items():
        if st != "ok":
            reasons.setdefault(arm, {}).setdefault(st, 0)
            reasons[arm][st] += 1
    result = {"arms": [a, b], "scores": scores, "failure_kinds": reasons}
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    lines = [f"| Group | Tries | {a} working | {b} working | Only {a} | Only {b} | Sign test p |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, s in scores.items():
        lines.append(f"| {name} | {s['pairs']} | {s[a]['working']} ({s[a]['rate']:.0%}) | {s[b]['working']} ({s[b]['rate']:.0%}) | "
                     f"{s['only_' + a]} | {s['only_' + b]} | {s['sign_test_p']} |")
    table = "\n".join(lines)
    if args.md:
        args.md.write_text(table + "\n")
    print(table)
    if "likeness" in scores.get("all", {}):
        print("likeness:", json.dumps(scores["all"]["likeness"]))
    print("failure kinds:", json.dumps(reasons))


if __name__ == "__main__":
    main()
