"""Fail-closed, CPU/tokenizer-only assembly after explicit root qualification.

qualified_by is a declared coordination field, NOT authentication. This script
checks a receipt and evidence identity; it cannot decide visual acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics

CAP = 16384
EXPECTED_IDS = {"asset-000168", "asset-000348", "asset-000448", "asset-000518", "asset-000622", "asset-003882"}
EXCLUDED_IDS = {"asset-000368", "asset-002237"}
CHECKS = ("clean_source_runtime", "clean_export_and_reimport", "geometry_hierarchy_clips", "visual_motion", "negative_check")
HEX = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read(path):
    return json.loads(Path(path).read_text())


def lines(path):
    return Path(path).read_bytes().splitlines(keepends=True)


def rows(path):
    return [json.loads(line) for line in lines(path)]


def digest(path):
    path = Path(path).resolve()
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def verify_manifest(root, expected):
    manifest_path = root / "DATA_MANIFEST.json"
    require(sha(manifest_path.read_bytes()) == expected, f"Frozen manifest mismatch: {root}")
    manifest = read(manifest_path)
    for entry in manifest["files"]:
        file = (root / entry["path"]).resolve()
        require(file.is_relative_to(root), "Manifest path escapes dataset")
        require(file.is_file() and file.stat().st_size == entry["bytes"] and sha(file.read_bytes()) == entry["sha256"], f"Frozen file mismatch: {file}")
    return manifest


def validate_qualification(receipt, receipt_dir, manifest_sha, expected):
    """Read-only gate. No output directory/file is created here."""
    require(receipt.get("schema") == 1, "Qualification schema must be1")
    require(receipt.get("status") == "qualified", "Qualification is missing/pending/rejected")
    require(receipt.get("qualified_by") == "/root", "Qualification must declare qualified_by=/root")
    require(receipt.get("correction_manifest_sha256") == manifest_sha, "Qualification correction manifest hash mismatch")
    approved = receipt.get("approved")
    require(isinstance(approved, list) and len(approved) == 6, "Exactly six approved rows required")
    require({entry.get("id") for entry in approved} == EXPECTED_IDS, "Approved IDs must match all six exactly, without duplicates")
    verified_evidence = []
    for entry in approved:
        identifier = entry["id"]
        for key in ("clean_html_sha256", "corrupt_html_sha256", "conversation_sha256"):
            require(isinstance(entry.get(key), str) and HEX.fullmatch(entry[key]) and entry[key] == expected[identifier][key], f"Qualification row hash mismatch: {identifier}/{key}")
        for check in CHECKS:
            require(entry.get("checks", {}).get(check) is True, f"Qualification check incomplete: {identifier}/{check}")
            evidence = entry.get("evidence", {}).get(check)
            require(isinstance(evidence, list) and evidence, f"Evidence missing: {identifier}/{check}")
            for item in evidence:
                require(isinstance(item, dict) and isinstance(item.get("path"), str) and item["path"].strip(), "Evidence path missing")
                require(isinstance(item.get("sha256"), str) and HEX.fullmatch(item["sha256"]), "Evidence SHA256 missing/malformed")
                file = Path(item["path"]).expanduser()
                file = file if file.is_absolute() else receipt_dir / file
                require(file.is_file() and file.stat().st_size > 0, f"Evidence file missing/empty: {file}")
                current = digest(file)
                require(current["sha256"] == item["sha256"], f"Evidence file hash mismatch: {file}")
                if "bytes" in item:
                    require(item["bytes"] == current["bytes"], f"Evidence byte count mismatch: {file}")
                verified_evidence.append({"id": identifier, "check": check, **current})
    return verified_evidence


def select_panel(path, full_valid, full_meta):
    panel_file = path / "valid.jsonl" if path.is_dir() else path
    panel_manifest = panel_file.parent / "manifest.json"
    panel = read(panel_manifest)
    source_lines, panel_lines = lines(full_valid), lines(panel_file)
    require(panel["source_valid_sha256"] == sha(full_valid.read_bytes()), "Panel full-dev hash mismatch")
    require(panel["panel_file_sha256"] == sha(panel_file.read_bytes()), "Panel content hash mismatch")
    require(panel["row_count"] == len(panel_lines) == len(panel["rows"]) == 10, "Panel must have exactly ten rows")
    seen, selected = set(), []
    for line, entry in zip(panel_lines, panel["rows"]):
        index = entry["source_valid_index_zero_based"]
        require(type(index) is int and 0 <= index < 63 and index not in seen, "Panel source index invalid/duplicated")
        seen.add(index)
        require(line == source_lines[index], "Panel row differs from exact full-dev source line")
        require(sha(line.rstrip(b"\r\n")) == entry["source_line_sha256"], "Panel source-line hash mismatch")
        row_sha = sha(canon(json.loads(line)))
        meta = full_meta[row_sha]
        require(entry["provenance"]["group_id"] == meta["group_id"] and meta["split"] == "valid", "Panel group/source split mismatch")
        selected.append(meta)
    return panel_file, panel_manifest, panel, selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "repo", "tokenizer", "source", "corrections", "qualification", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-manifest-sha256", required=True)
    parser.add_argument("--correction-manifest-sha256", required=True)
    parser.add_argument("--include-targeted", action="store_true")
    parser.add_argument("--validation-panel", type=Path)
    args = parser.parse_args()
    workspace=args.workspace.expanduser().resolve()
    def resolve(value):
        return value.expanduser().resolve() if value.is_absolute() else (workspace/value).resolve()
    repo=resolve(args.repo)
    require(repo.is_dir(), "Repository path is not a directory")
    tokenizer_path=resolve(args.tokenizer)
    source, corrections, qualification, out = [resolve(getattr(args, name)) for name in ("source", "corrections", "qualification", "out")]
    source_manifest_sha=args.source_manifest_sha256
    correction_manifest_sha=args.correction_manifest_sha256
    require(HEX.fullmatch(source_manifest_sha) and HEX.fullmatch(correction_manifest_sha), "Expected manifest SHA256 values must be lowercase hex")
    require(not out.exists(), "Output exists; never overwrite a revision")
    require(not out.is_relative_to(source) and not source.is_relative_to(out) and not out.is_relative_to(corrections) and not corrections.is_relative_to(out), "Output overlaps an input dataset")
    # Receipt gate happens before tokenizer import, tokenization or ANY output creation.
    source_manifest = verify_manifest(source, source_manifest_sha)
    correction_manifest = verify_manifest(corrections, correction_manifest_sha)
    correction_rows = rows(corrections / "train.jsonl")
    io_rows = rows(corrections / "pairs.jsonl")
    require(len(correction_rows) == len(io_rows) == 6 and {x["id"] for x in io_rows} == EXPECTED_IDS, "Correction candidate IDs/count mismatch")
    records, expected = {}, {}
    for io, row in zip(io_rows, correction_rows):
        identifier = io["id"]
        record = read(corrections / "examples" / identifier / "PAIR.json")
        require(row["messages"][1]["content"] == io["input"] and row["messages"][-1]["content"] == io["output"], "Correction row/pair order or content mismatch")
        records[identifier] = record
        expected[identifier] = {key: record[key] for key in ("clean_html_sha256", "corrupt_html_sha256")}
        expected[identifier]["conversation_sha256"] = sha(canon(row))
    receipt = read(qualification)
    evidence = validate_qualification(receipt, qualification.parent, correction_manifest_sha, expected)
    snapshot = [digest(source / "DATA_MANIFEST.json"), digest(corrections / "DATA_MANIFEST.json"), digest(qualification)] + evidence

    provenance = read(source / "ROW_PROVENANCE.json")["selected"]
    by_conversation = {x["conversation_sha256"]: x for x in provenance}
    require(len(by_conversation) == len(provenance), "Duplicate original conversation provenance")
    replay_lines = lines(source / "replay/train.jsonl")
    replay_meta = [by_conversation[sha(canon(json.loads(line)))] for line in replay_lines]
    require(len(replay_lines) == 401 and {m["id"] for m in replay_meta if m["id"] in EXCLUDED_IDS} == EXCLUDED_IDS, "Expected bad training IDs missing")
    kept = [(line, meta) for line, meta in zip(replay_lines, replay_meta) if meta["id"] not in EXCLUDED_IDS]
    require(len(kept) == 399 and all(meta["split"] == "train" for _, meta in kept), "Replay count/split mismatch")
    source_map = {meta["id"]: (json.loads(line), meta) for line, meta in kept}
    train_meta = [meta for _, meta in kept]
    for split, expected_count in (("train", 64), ("valid", 16)):
        require(len(rows(source / "repairs" / f"{split}.jsonl")) == expected_count, "Original helper count changed")
    require(len(rows(source / "replay/valid.jsonl")) == 47 and len(rows(source / "mixture/valid.jsonl")) == 63, "Original development counts changed")
    helper_meta = [by_conversation[sha(canon(row))] for row in rows(source / "repairs/train.jsonl")]
    full_valid_meta = [by_conversation[sha(canon(row))] for row in rows(source / "mixture/valid.jsonl")]
    correction_meta = []
    for io, row in zip(io_rows, correction_rows):
        record = records[io["id"]]
        original, original_meta = source_map[io["id"]]
        require(record["original_split"] == original_meta["split"] == "train" and record["original_group_id"] == original_meta["group_id"], "Correction original train-group mismatch")
        clean = (corrections / "examples" / io["id"] / "clean/generated.html").read_text()
        corrupt = (corrections / "examples" / io["id"] / "corrupt/generated.html").read_text()
        require(sha(clean) == record["clean_html_sha256"] and sha(corrupt) == record["corrupt_html_sha256"], "Correction HTML hash mismatch")
        blocks = re.findall(r"```html\s*\n([\s\S]*?)\n```", original["messages"][-1]["content"])
        require(blocks == [clean], "Correction clean target is not exact original HTML")
        require(io["output"] == "```html\n" + clean + "\n```" and io["input"].endswith("```html\n" + corrupt + "\n```"), "Correction content not bound to frozen HTML")
        meta = {**original_meta, "id": "correction:" + io["id"], "source_asset_id": io["id"], "kind": "correction", "correction_family": record["correction_family"], "conversation_sha256": sha(canon(row)), "derived_target": True}
        correction_meta.append(meta)
    train_meta += helper_meta + correction_meta
    overlap = {}
    for key in ("group_id", "normalized_js_sha256", "javascript_sha256", "title_key", "repair_family"):
        both = {m[key] for m in train_meta if m.get(key)} & {m[key] for m in full_valid_meta if m.get(key)}
        overlap[key] = sorted(both)
        require(not both, f"Training/full-dev group overlap: {key}")
    require(len({m["conversation_sha256"] for m in train_meta}) == 469, "Repeated train conversation")
    runtime_valid = source / "mixture/valid.jsonl"
    panel_info = None
    if args.validation_panel:
        runtime_valid, panel_manifest, panel, selected = select_panel(resolve(args.validation_panel), runtime_valid, by_conversation)
        snapshot += [digest(runtime_valid), digest(panel_manifest)]
        panel_info = {"panel_manifest": digest(panel_manifest), "runtime_rows": 10, "full_dev_rows": 63, "selection": "exact pre-existing panel; no new data split", "recommended_val_batches": -1, "evaluation_boundary": "segment boundary only; do not mutate training RNG"}

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
    all_rows = [json.loads(line) for line, _ in kept] + rows(source / "repairs/train.jsonl") + correction_rows + rows(source / "mixture/valid.jsonl")
    token_records = {}
    for row in all_rows:
        require(not any(m.get("reasoning_content") for m in row["messages"]), "Unexpected reasoning content")
        full = tokenizer.apply_chat_template(row["messages"], tokenize=True, return_dict=False, enable_thinking=False)
        prefix = tokenizer.apply_chat_template(row["messages"][:-1], tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)
        require(0 < len(prefix) < len(full) <= CAP and full[:len(prefix)] == prefix, "Length or exact mask-prefix failure")
        token_records[sha(canon(row))] = {"tokens": len(full), "masked_prefix_tokens": len(prefix), "target_tokens": len(full) - len(prefix), "full_ids_sha256": sha(canon(full)), "prompt_ids_sha256": sha(canon(prefix)), "exact_mask_prefix": True}
    for meta in train_meta:
        meta.update(token_records[meta["conversation_sha256"]])
    for io, row in zip(io_rows, correction_rows):
        current = token_records[sha(canon(row))]
        frozen = records[io["id"]]["tokenization"]
        require(current["tokens"] == frozen["full_tokens"] and current["full_ids_sha256"] == frozen["full_ids_sha256"] and current["prompt_ids_sha256"] == frozen["prefix_ids_sha256"], "Frozen correction tokenization changed")
    # Recheck all evidence, metadata and source manifests immediately before write.
    for entry in snapshot:
        current = digest(entry["path"])
        require(current["bytes"] == entry["bytes"] and current["sha256"] == entry["sha256"], "Input/evidence changed during assembly")
    verify_manifest(source, source_manifest_sha)
    verify_manifest(corrections, correction_manifest_sha)
    require(not out.exists(), "Output appeared concurrently")
    out.mkdir(parents=True, exist_ok=False)
    def copy(src, relative):
        dst = out / relative; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dst)
    def write_bytes(relative, data):
        dst = out / relative; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(data)
    write_bytes("replay/train.jsonl", b"".join(line for line, _ in kept))
    copy(source / "replay/valid.jsonl", "replay/valid.jsonl")
    for split in ("train", "valid"):
        copy(source / "repairs" / f"{split}.jsonl", f"repairs/{split}.jsonl")
    copy(corrections / "train.jsonl", "corrections/train.jsonl")
    write_bytes("corrections/valid.jsonl", b"")
    write_bytes("mixture/train.jsonl", (out / "replay/train.jsonl").read_bytes() + (source / "repairs/train.jsonl").read_bytes() + (corrections / "train.jsonl").read_bytes())
    copy(runtime_valid, "mixture/valid.jsonl")
    copy(source / "mixture/valid.jsonl", "full-dev/valid.jsonl")
    for folder in ("replay", "repairs"):
        copy(source / folder / "LICENSE.source", f"{folder}/LICENSE.source")
    copy(corrections / "LICENSE.source", "corrections/LICENSE.source")
    if args.include_targeted:
        copy(corrections / "train.jsonl", "targeted-correction/train.jsonl")
        copy(runtime_valid, "targeted-correction/valid.jsonl")
        write_json(out / "targeted-correction/PROSPECTIVE_SETTINGS.json", {"status": "recommendation-only; no runtime modified", "updates": 12, "epochs": 2, "train_rows": 6, "batch_size": 1, "packing": False, "file_repetition_multiplier": 1, "enable_thinking": False, "mask_prompt": True, "max_seq_length": CAP, "val_batches": -1, "evaluation_boundary": "boundary only", "runtime_valid_rows": 10 if panel_info else 63, "qualification_does_not_authorize_new_deadlines": True})
    for src, name in ((source / "DATA_MANIFEST.json", "source-manifest.json"), (corrections / "DATA_MANIFEST.json", "correction-manifest.json"), (qualification, "qualification.json")):
        copy(src, "lineage/" + name)
    write_json(out / "ROW_PROVENANCE.json", {"selected": train_meta + full_valid_meta})
    write_json(out / "REPLAY_PROVENANCE.json", {"selected": [m for m in train_meta + full_valid_meta if m["kind"] == "replay"]})
    write_json(out / "EXCLUSIONS.json", {"removed_train_ids": sorted(EXCLUDED_IDS), "reasons": {"asset-000368": "Degenerate full-turn quaternion keys; no sampled visible rotation", "asset-002237": "Known animation defect reported by root source audit"}, "all_existing_splits_preserved": True})
    write_json(out / "TOKEN_CHECKS.json", {"enable_thinking": False, "local_files_only": True, "rows": token_records})
    write_json(out / "LINEAGE.json", {"repository": str(repo), "source_root": str(source), "corrections_root": str(corrections), "source_manifest_sha256": source_manifest_sha, "correction_manifest_sha256": correction_manifest_sha, "qualification": digest(qualification), "evidence": evidence, "builder": digest(Path(__file__)), "tokenizer_files": [digest(tokenizer_path / name) for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")], "train_group_overlap": overlap, "intentional_overlap": "Correction rows share existing training asset/program families; derived CCORE targets, not independent targets or new motion.", "qualified_by_semantics": "Declared coordination field, not authentication", "validation_panel": panel_info})
    datasets = {}
    for kind in ("replay", "repairs", "corrections"):
        counts = {split: len(rows(out / kind / f"{split}.jsonl")) for split in ("train", "valid")}
        lengths = [token_records[sha(canon(row))]["tokens"] for split in ("train", "valid") for row in rows(out / kind / f"{split}.jsonl")]
        datasets[kind] = {"counts": counts, "min_tokens": min(lengths), "median_tokens": statistics.median(lengths), "max_tokens": max(lengths), "cap": CAP, "truncation": False, "exact_mask_prefix": True}
    for relative, expected_count in (("replay/train.jsonl", 399), ("replay/valid.jsonl", 47), ("mixture/train.jsonl", 469), ("full-dev/valid.jsonl", 63)):
        require(len(rows(out / relative)) == expected_count, "Assembled row-count failure")
    require((out / "full-dev/valid.jsonl").read_bytes() == (source / "mixture/valid.jsonl").read_bytes(), "Full-dev bytes changed")
    files = [{**digest(file), "path": str(file.relative_to(out))} for file in sorted(out.rglob("*")) if file.is_file()]
    write_json(out / "DATA_MANIFEST.json", {"schema": 3, "status": "assembled-after-declared-root-qualification; not-trained-or-runtime-adopted", "source_revision": source_manifest["source_revision"], "enable_thinking": False, "response_only_training": True, "datasets": datasets, "family_overlap": 0, "grouping_overlap_scope": "Existing algorithmic title/JS groups, not semantic independence", "repair_checks": source_manifest["repair_checks"], "mixture": {"mixture_counts": {"train": 469, "valid": 10 if panel_info else 63}, "replay_train": 399, "repair_train": 64, "correction_train": 6, "repetition_multiplier": 1}, "target_novelty": {"correction_conversations": 6, "existing_replay_target_programs_reused": 6, "independent_full_program_claim": False, "description": "Six new correction tasks reuse six retained CCORE training target programs; 405 full-program conversations are not 405 independent programs."}, "validation": {"runtime_rows": 10 if panel_info else 63, "full_dev_rows": 63, "full_dev_path": "full-dev/valid.jsonl", "mode": "explicit-fixed-panel" if panel_info else "unchanged-full-dev", "val_batches_recommendation": -1, "evaluation_boundary": "segment boundary only"}, "targeted_correction_included": args.include_targeted, "files": files})
    print(json.dumps({"out": str(out), "manifest": digest(out / "DATA_MANIFEST.json"), "train_rows": 469, "runtime_valid_rows": 10 if panel_info else 63, "full_dev_rows": 63}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit("ASSEMBLY REFUSED: " + str(error))
