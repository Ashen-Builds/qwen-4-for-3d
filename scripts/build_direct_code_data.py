"""Build an isolated CPU/tokenizer-only no-thinking data proposal; never train.

The output keeps every retained assistant content string byte-for-byte. Original
reasoning is scanned for leakage, then replaced by an explicit empty string.
No checkpoint weights, JavaScript, supplied GLBs, or browser are executed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from transformers import AutoTokenizer

CAP = 16384
SEED = "direct-code-no-thinking-v1"
ADJECTIVES = set("ancient antique armored basic broken bronze ceramic compact crystal decorative elegant enchanted futuristic golden heavy industrial large magical medieval miniature modern ornate portable reinforced retro robotic rustic small stone stylized wooden weathered vintage low poly lowpoly simple tiny metal steel brass copper silver old new rusty sci fi scifi".split())
KEYWORDS = set("as async await break case catch class const continue debugger default delete do else export extends false finally for from function get if import in instanceof let new null of return set static super switch this throw true try typeof undefined var void while with yield".split())
LEX = re.compile(r"(?P<space>\s+)|(?P<line>//[^\n]*)|(?P<block>/\*[\s\S]*?\*/)|(?P<string>'(?:\\[\s\S]|[^'\\])*'|\"(?:\\[\s\S]|[^\"\\])*\"|`(?:\\[\s\S]|[^`\\])*`)|(?P<number>(?:0[xX][0-9a-fA-F]+|0[bB][01]+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?))|(?P<ident>[A-Za-z_$][\w$]*)|(?P<other>.)", re.S)


def sha(data):
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(path):
    return json.loads(path.read_text())


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_rows(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in data))


def digest_file(path):
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}


def compact(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def title_key(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    # Remove only a declared leading adjective sequence, never arbitrary nouns.
    while len(words) > 1 and words[0] in ADJECTIVES:
        words.pop(0)
    return " ".join(words)


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active = False
        self.parts = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            attrs = dict(attrs)
            self.active = attrs.get("type", "").lower() != "importmap" and not attrs.get("src")
            self.current = []

    def handle_data(self, data):
        if self.active:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.active:
            self.parts.append("".join(self.current))
            self.active = False


def javascript(content, kind):
    if kind == "repair":
        match = re.fullmatch(r"```(?:javascript|js)\s*\n([\s\S]*?)\n```", content)
        if not match:
            raise ValueError("Unrecognized repair code fence")
        return match.group(1)
    parser = Scripts()
    parser.feed(content)
    if not parser.parts:
        raise ValueError("No inline script in replay target")
    return "\n/* SCRIPT BOUNDARY */\n".join(parser.parts)


def normalized_program(code):
    names = {}
    tokens = []
    for match in LEX.finditer(code):
        kind, value = match.lastgroup, match.group()
        if kind in {"space", "line", "block"}:
            continue
        if kind == "string":
            value = "<STRING>"
        elif kind == "number":
            value = "<NUMBER>"
        elif kind == "ident" and value not in KEYWORDS:
            if value not in names:
                names[value] = f"ID{len(names)}"
            value = names[value]
        tokens.append(value)
    return sha(canonical(tokens))


def scan_fields(item):
    fields = {"title": item.get("title", "")}
    for index, message in enumerate(item["original"]["messages"]):
        # The fixed system instruction is not an asset specification.
        if message["role"] in {"user", "assistant"}:
            for key in ("content", "reasoning_content"):
                fields[f"messages[{index}].{message['role']}.{key}"] = message.get(key) or ""
    return fields


def leakage(item, aliases):
    hits = []
    topics = ["babylon", "mesopotami", "iraq", "market", "village", "canal", "town"]
    for field, value in scan_fields(item).items():
        haystack = compact(value)
        for term in topics:
            if term in haystack:
                hits.append({"reason": "showcase_topic", "field": field, "term": term})
        for family, alias in aliases:
            if compact(alias) in haystack:
                hits.append({"reason": "reserved_eval_alias", "field": field, "family": family, "alias": alias})
    return hits


def summary(items):
    lengths = sorted(item["tokens"] for item in items)
    return {"count": len(lengths), "min_tokens": min(lengths) if lengths else None,
            "median_tokens": statistics.median(lengths) if lengths else None,
            "max_tokens": max(lengths) if lengths else None,
            "total_tokens": sum(lengths), "cap": CAP, "truncation": False,
            "exact_mask_prefix": all(item["exact_mask_prefix"] for item in items)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    work = repo.parent / "work"
    prep = work / "sprint-prep"
    source = prep / "training-ready"
    candidate = prep / "replay-candidate"
    tokenizer_path = work / "models-derived/ccore-bf16"
    out = args.out.resolve()
    allowed = prep / "direct-code-proposal"
    assert out.is_relative_to(allowed) and out != allowed
    assert not out.exists(), "Output is frozen: choose a new directory instead of overwriting"
    source_paths = [source / "REPLAY_PROVENANCE.json", source / "DATA_MANIFEST.json",
                    candidate / "PROVENANCE.json", candidate / "GLB_VALIDATION.json",
                    prep / "repair-curriculum/CURRICULUM_REPORT.json", repo / "eval/sprint-probes-v1.json"]
    for kind in ("replay", "repairs"):
        source_paths += [source / kind / name for name in ("train.jsonl", "valid.jsonl", "LICENSE.source")]
    tokenizer_files = [tokenizer_path / name for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")]
    source_paths += tokenizer_files
    source_hashes = [digest_file(path) for path in source_paths]
    probes = read_json(repo / "eval/sprint-probes-v1.json")
    aliases = [(row["family"], alias) for row in probes["final"] + probes["development"] for alias in row["exclude_training_aliases"]]
    provenance = read_json(source / "REPLAY_PROVENANCE.json")["selected"]
    validation = read_json(candidate / "GLB_VALIDATION.json")
    validations = {row["id"]: row for row in validation["rows"]}
    assert len(validations) == len(validation["rows"])
    curriculum = read_json(prep / "repair-curriculum/CURRICULUM_REPORT.json")
    repair_checks = {row["code_sha256"]: row for row in curriculum["checks"]}
    tok = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
    items, excluded = [], []
    for kind in ("replay", "repair"):
        for split in ("train", "valid"):
            path = source / ("replay" if kind == "replay" else "repairs") / f"{split}.jsonl"
            rows = read_rows(path)
            metadata = [row for row in provenance if row["split"] == split] if kind == "replay" else [{} for _ in rows]
            assert len(rows) == len(metadata)
            for index, (original, meta) in enumerate(zip(rows, metadata)):
                assert [m["role"] for m in original["messages"]] == ["system", "user", "assistant"]
                item = {"id": meta.get("id", f"repair-{split}-{index:03d}"), "kind": kind,
                        "original_split": split, "source_row_index": index, "source_path": str(path),
                        "title": meta.get("title", ""), "source_metadata": meta, "original": original}
                content = original["messages"][-1]["content"]
                code = javascript(content, kind)
                item.update({"assistant_content_sha256": sha(content), "javascript_sha256": sha(code),
                             "normalized_js_sha256": normalized_program(code),
                             "title_key": title_key(item["title"]) if kind == "replay" else None,
                             "removed_reasoning_sha256": sha(original["messages"][-1].get("reasoning_content") or ""),
                             "removed_reasoning_characters": len(original["messages"][-1].get("reasoning_content") or "")})
                reasons = leakage(item, aliases)
                if kind == "replay":
                    v = validations.get(item["id"])
                    if not v or v["errors"] != 0:
                        reasons.append({"reason": "missing_or_failed_supplied_glb_validation"})
                    else:
                        glb = candidate / "provided-glbs" / f"{item['id']}.glb"
                        evidence = digest_file(glb)
                        if evidence["sha256"] != meta["provided_glb_sha256"] or evidence["bytes"] != meta["provided_glb_bytes"] or evidence["bytes"] != v["bytes"]:
                            raise ValueError(f"Supplied GLB drift: {item['id']}")
                        item["supplied_glb_evidence"] = evidence | {"validator_errors": v["errors"], "validator_warnings": v["warnings"]}
                else:
                    check = repair_checks.get(sha(code))
                    assert check and check["passed"] and check["split"] == split
                    item["repair_family"] = check["family"]
                direct = deepcopy(original)
                for message in direct["messages"]:
                    message["reasoning_content"] = ""
                assert direct["messages"][-1]["content"] == content
                full = tok.apply_chat_template(direct["messages"], tokenize=True, return_dict=False, enable_thinking=False)
                prefix = tok.apply_chat_template(direct["messages"][:-1], tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)
                exact = bool(prefix) and len(prefix) < len(full) and full[:len(prefix)] == prefix
                assert exact, f"Prompt mask mismatch: {item['id']}"
                item.update({"row": direct, "tokens": len(full), "masked_prefix_tokens": len(prefix),
                             "target_tokens": len(full) - len(prefix), "exact_mask_prefix": exact,
                             "prompt_ids_sha256": sha(canonical(prefix)), "full_ids_sha256": sha(canonical(full)),
                             "prompt_text_sha256": sha(tok.decode(prefix)),
                             "conversation_sha256": sha(canonical(direct))})
                if len(full) > CAP:
                    reasons.append({"reason": "overlength_excluded_not_truncated", "tokens": len(full), "cap": CAP})
                item["reasons"] = reasons
                items.append(item)

    # Build transitive grouping over ALL input rows before any filtering. A
    # removed row may still join two related rows; components never straddle splits.
    parent = {item["id"]: item["id"] for item in items}
    assert len(parent) == len(items)
    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    grouping_keys = defaultdict(list)
    for item in items:
        keys = ["normalized-js:" + item["normalized_js_sha256"], "exact-js:" + item["javascript_sha256"]]
        if item["kind"] == "replay":
            keys += ["title:" + item["title_key"]]
        else:
            keys += ["repair-family:" + item["repair_family"]]
        item["grouping_keys"] = keys
        for key in keys:
            grouping_keys[key].append(item["id"])
    for ids in grouping_keys.values():
        for key in ids[1:]:
            union(ids[0], key)
    components = defaultdict(list)
    by_id = {item["id"]: item for item in items}
    for item in items:
        components[find(item["id"])].append(item)
    for members in components.values():
        group = sha(canonical(sorted(item["id"] for item in members)))
        repair_splits = {item["original_split"] for item in members if item["kind"] == "repair"}
        assert len(repair_splits) <= 1, "Repair family collision across frozen train/valid"
        split = next(iter(repair_splits)) if repair_splits else ("valid" if int(sha(SEED + group)[:8], 16) % 10 == 0 else "train")
        for item in members:
            item.update({"group_id": group, "split": split})
    drill = [item for item in items if item["title"].lower() in {"weathered factory drill rig", "factory drill rig"}]
    assert len(drill) == 2 and len({item["group_id"] for item in drill}) == 1
    seen = {}
    for item in sorted(items, key=lambda x: x["id"]):
        if item["reasons"]:
            continue
        key = item["conversation_sha256"]
        if key in seen:
            item["reasons"].append({"reason": "duplicate_conversation", "retained_id": seen[key]})
        else:
            seen[key] = item["id"]
    train_replay = [item for item in items if item["kind"] == "replay" and item["split"] == "train" and not item["reasons"]]
    train_repairs = [item for item in items if item["kind"] == "repair" and item["split"] == "train" and not item["reasons"]]
    allowed_repairs = math.floor(len(train_replay) * 15 / 85)
    assert allowed_repairs >= 8, "Cannot preserve all eight repair families under 15 percent cap"
    family_buckets = defaultdict(list)
    for item in train_repairs:
        family_buckets[item["repair_family"]].append(item)
    assert len(family_buckets) == 8
    # Balanced round-robin preserves all eight families, no repeated conversation.
    ranked = []
    for family in family_buckets:
        family_buckets[family].sort(key=lambda item: item["id"])
    for index in range(max(map(len, family_buckets.values()))):
        for family in sorted(family_buckets):
            if index < len(family_buckets[family]):
                ranked.append(family_buckets[family][index])
    for item in ranked[allowed_repairs:]:
        item["reasons"].append({"reason": "repair_fraction_cap", "max_fraction": 0.15, "allowed_train_repairs": allowed_repairs})
    retained = [item for item in items if not item["reasons"]]
    excluded = [item for item in items if item["reasons"]]
    out.mkdir(parents=True)
    splits = {}
    for kind, folder in (("replay", "replay"), ("repair", "repairs")):
        for split in ("train", "valid"):
            subset = sorted([item for item in retained if item["kind"] == kind and item["split"] == split], key=lambda item: item["id"])
            splits[(folder, split)] = subset
            assert subset
            write_rows(out / folder / f"{split}.jsonl", [item["row"] for item in subset])
        shutil.copyfile(source / folder / "LICENSE.source", out / folder / "LICENSE.source")
    for split in ("train", "valid"):
        subset = splits[("replay", split)] + splits[("repairs", split)]
        splits[("mixture", split)] = subset
        write_rows(out / "mixture" / f"{split}.jsonl", [item["row"] for item in subset])
    ordered = sorted(splits[("replay", "train")], key=lambda item: (item["tokens"], item["id"]))
    length_probes = [ordered[0], ordered[len(ordered) // 2], ordered[-1]]
    assert len({item["id"] for item in length_probes}) == 3
    valid_ordered = sorted(splits[("replay", "valid")], key=lambda item: (item["tokens"], item["id"]))
    write_rows(out / "length-probe/train.jsonl", [item["row"] for item in length_probes])
    write_rows(out / "length-probe/valid.jsonl", [valid_ordered[len(valid_ordered) // 2]["row"]])
    # Training/dev are algorithmically separated; probes intentionally reuse train.
    overlaps = {}
    train, valid = splits[("mixture", "train")], splits[("mixture", "valid")]
    for key in ("id", "group_id", "normalized_js_sha256", "javascript_sha256", "assistant_content_sha256", "conversation_sha256", "title_key", "repair_family"):
        intersection = {item.get(key) for item in train if item.get(key)} & {item.get(key) for item in valid if item.get(key)}
        overlaps[key] = sorted(intersection)
        assert not intersection, f"Train/valid overlap: {key}"
    fraction = len(splits[("repairs", "train")]) / len(train)
    assert fraction <= 0.15
    assert len({item["repair_family"] for item in splits[("repairs", "valid")]}) == 2
    assert all(not leakage(item, aliases) for item in retained)
    assert all(0 < item["masked_prefix_tokens"] < item["tokens"] <= CAP for item in retained)
    assert all(item["row"]["messages"][-1]["content"] == item["original"]["messages"][-1]["content"] for item in retained)
    strip = lambda item: {key: value for key, value in item.items() if key not in {"row", "original"}}
    write_json(out / "REPLAY_PROVENANCE.json", {"selected": [strip(item) for item in retained if item["kind"] == "replay"]})
    write_json(out / "ROW_PROVENANCE.json", {"selected": [strip(item) for item in retained]})
    write_json(out / "EXCLUSIONS.json", {"scope": "All input training-ready replay and repair rows; all matching reasons retained", "excluded": [strip(item) for item in excluded]})
    write_json(out / "GROUPS.json", {"components": [{"group_id": members[0]["group_id"], "split": members[0]["split"], "members": [{"id": item["id"], "title": item["title"], "included": not item["reasons"], "keys": item["grouping_keys"]} for item in members]} for members in components.values()]})
    write_json(out / "EVAL_VARIANT.json", {"variant": "direct-code-no-thinking-v1", "enable_thinking": False,
        "tokenizer": str(tokenizer_path), "local_files_only": True, "max_training_full_tokens": CAP,
        "assistant_reasoning_content": "", "required_pairing": "Fresh unadapted CCORE control and newly trained adapter must both use identical prompts, system messages, sampler, seeds, token cap and enable_thinking=False. Do not compare this variant directly with a thinking-on score as a matched test.",
        "source_probes_file": str(repo / "eval/sprint-probes-v1.json"), "probes_sha256": sha((repo / "eval/sprint-probes-v1.json").read_bytes()),
        "runtime_requirement": "Every full/prefix chat template call must explicitly pass enable_thinking=False. MLX ChatDataset needs a worker-local wrapper; default template behavior is not equivalent. No tokenizer file was edited.",
        "adoption_status": "Proposal only; no runtime or existing dataset modified, no training/inference performed by this build."})
    frozen = out / "source-evidence"
    frozen.mkdir()
    for path, name in [(candidate / "GLB_VALIDATION.json", "GLB_VALIDATION.json"),
                       (prep / "repair-curriculum/CURRICULUM_REPORT.json", "CURRICULUM_REPORT.json"),
                       (repo / "eval/sprint-probes-v1.json", "sprint-probes-v1.json")]:
        shutil.copyfile(path, frozen / name)
    write_json(out / "SOURCE_HASHES.json", {"inputs": source_hashes, "builder": digest_file(Path(__file__).resolve()),
        "versions": {name: importlib.metadata.version(name) for name in ("transformers", "tokenizers")},
        "scope": "Only tokenizer companion files hashed in model folder; no weights loaded or copied. Supplied GLB hashes are in row provenance."})
    report = {"variant": "direct-code-no-thinking-v1", "status": "proposal-not-adopted-or-trained",
        "inputs": {"replay": len(provenance), "repair": sum(item["kind"] == "repair" for item in items)},
        "datasets": {folder: {split: summary(splits[(folder, split)]) for split in ("train", "valid")} for folder in ("replay", "repairs", "mixture")},
        "repair_train_fraction": fraction, "repair_repeat_multiplier": 1,
        "repair_program_families": {split: dict(Counter(item["repair_family"] for item in splits[("repairs", split)])) for split in ("train", "valid")},
        "repair_qualification": "Use repairs/train.jsonl and repairs/valid.jsonl as complete short repair-only qualification; no replay or train-family rows are in validation.",
        "length_probes": [{"position": position, "id": item["id"], "title": item["title"], "tokens": item["tokens"], "masked_prefix_tokens": item["masked_prefix_tokens"], "complete_target": True} for position, item in zip(("min", "median", "max"), length_probes)],
        "exclusions": {"total": len(excluded), "reason_rows": dict(Counter(reason for item in excluded for reason in {r["reason"] for r in item["reasons"]})), "all_ids_and_reasons": "EXCLUSIONS.json"},
        "leakage_scan": {"fields": ["title", "user content", "user reasoning_content", "assistant content including HTML/JS", "original assistant reasoning_content"], "normalization": "Lowercase then remove all non-ASCII-alphanumeric characters; substring search per field. Finds camelCase and punctuation/spacing variants. Original reasoning is checked before deletion.", "showcase_terms": ["babylon", "mesopotami", "iraq", "market", "village", "canal", "town"], "aliases": aliases, "retained_hits": 0,
            "false_positive_risk": "Conservative compact substring matching may exclude unrelated concepts, discarded reasoning ideas, literal/comment text or terms spanning adjacent words. It intentionally prefers exclusion; alias absence does not prove semantic or upstream-pretraining independence."},
        "grouping": {"algorithm": "Connected components over all 649 original rows, including excluded rows, using equality of normalized title, exact extracted inline JS, normalized inline JS, and declared repair family. Replay title: lowercase ASCII word tokens and strip only leading words from the recorded adjective vocabulary; domain is deliberately ignored. Program: extract non-importmap inline scripts; lexical scan drops comments/whitespace, replaces strings (including entire backtick templates) and numeric literals with placeholders, and consistently renames every non-keyword identifier by first occurrence. Equality merges components transitively. Repair frozen train/valid family assignments are preserved and checked for collisions; other components split by sha256(seed+group_id) first8hex modulo10==0 for valid. This is lexical grouping, not AST or semantic equivalence; regex literals/template interpolations are not fully parsed. It can overgroup and can miss semantically related independently implemented code.",
            "seed": SEED, "adjectives": sorted(ADJECTIVES), "javascript_keywords": sorted(KEYWORDS), "semantic_independence_claim": False,
            "component_count": len(components), "overlaps": overlaps,
            "factory_drill_regression": [{"id": item["id"], "title": item["title"], "group_id": item["group_id"], "split": item["split"], "included": not item["reasons"]} for item in drill]},
        "verification": {"all_content_strings_preserved": True, "all_reasoning_content_empty": True, "exact_full_token_prefix": True,
            "enable_thinking_explicit_false": True, "max_seq_length": CAP, "truncated_rows": 0, "models_loaded": 0,
            "supplied_glb_hashes_match": True, "retained_replay_validator_errors": 0,
            "source_execution": False, "glb_execution": False, "rendered_or_visual_qa": False},
        "limits": ["Existing supplied publisher GLB validator results certify those binaries only; unchanged source HTML was not re-executed and might not reproduce the export.",
                   "No rendered quality, animation contact or visual acceptance evidence was created.",
                   "Replay is from CCORE's upstream corpus and is not independent model pretraining evaluation; developer validation families only establish the recorded lexical split.",
                   "Removing reasoning changes the experiment and requires fresh matched no-thinking baseline and prospective qualification.",
                   "Parent task owns adoption, training, runtime changes and repository publication."]}
    report["grouping"]["algorithm"] = report["grouping"]["algorithm"].replace("649 original rows", f"{len(items)} original rows")
    write_json(out / "REPORT.json", report)
    (out / "README.md").write_text("# Direct-code no-thinking proposal\n\nProposal only. No training, inference, source execution, visual QA, or runtime adoption occurred.\n\nEvery retained assistant content string is unchanged. Original reasoning is scanned for reserved topics then replaced by an empty string. All tokenization uses the pinned local tokenizer with enable_thinking=False. Full sequences over 16,384 tokens are excluded, never truncated.\n\nUse mixture for prospective training; repairs for short qualification; length-probe for complete min/median/max replay examples. Full row identities, exclusions, lexical groups, length/prefix checks, supplied GLB hashes and limits are in REPORT.json and its linked JSON files.\n\nBoth license notices are retained. No raw GLB, tokenizer, or model weight is redistributed here. The original training-ready data and live runtime are untouched.\n")
    for before, path in zip(source_hashes, source_paths):
        assert before == digest_file(path), f"Input changed during build: {path}"
    datasets = {}
    for folder in ("replay", "repairs"):
        combined = splits[(folder, "train")] + splits[(folder, "valid")]
        datasets[folder] = summary(combined) | {"counts": {split: len(splits[(folder, split)]) for split in ("train", "valid")}}
    files = [digest_file(path) | {"path": str(path.relative_to(out))} for path in sorted(out.rglob("*")) if path.is_file()]
    manifest = {"schema": 2, "status": "proposal-not-adopted-or-trained", "variant": "direct-code-no-thinking-v1", "enable_thinking": False,
        "source_revision": read_json(candidate / "PROVENANCE.json")["revision"], "datasets": datasets,
        "family_overlap": 0, "grouping_overlap_scope": "Algorithmic title/JS connected components only; not complete semantic independence",
        "repair_checks": curriculum, "mixture": {"mixing": "One copy per retained wording variant, balanced cap at15percent train examples", "mixture_counts": {split: len(splits[("mixture", split)]) for split in ("train", "valid")}, "repair_train_fraction": fraction, "length_probe_tokens": [item["tokens"] for item in length_probes]},
        "provided_glbs": "Retained replay supplied GLBs have existing independent validator errors=0 and current SHA256/byte identity matches; no new source execution or visual certification",
        "input_files_unchanged": True, "files": files}
    write_json(out / "DATA_MANIFEST.json", manifest)
    print(json.dumps({"out": str(out), "counts": {folder: {split: len(splits[(folder, split)]) for split in ("train", "valid")} for folder in ("replay", "repairs", "mixture")}, "repair_fraction": fraction, "length_probes": report["length_probes"], "exclusions": report["exclusions"], "manifest_sha256": sha((out / "DATA_MANIFEST.json").read_bytes())}, indent=2), flush=True)


if __name__ == "__main__":
    main()
