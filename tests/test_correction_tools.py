"""Small CPU-only tests. Fixtures are synthetic; no real qualification is issued."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("assembler", SCRIPTS / "assemble_correction_revision.py")
assembler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembler)


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.evidence = self.directory / "synthetic-evidence.txt"
        self.evidence.write_text("Synthetic unit-test evidence; never a real candidate qualification.\n")
        digest = assembler.sha(self.evidence.read_bytes())
        self.expected = {identifier: {key: assembler.sha(identifier + key) for key in
            ("clean_html_sha256", "corrupt_html_sha256", "conversation_sha256")}
            for identifier in assembler.EXPECTED_IDS}
        self.manifest_sha = assembler.sha("synthetic-manifest")
        self.receipt = {"schema": 1, "status": "qualified", "qualified_by": "/root",
            "correction_manifest_sha256": self.manifest_sha, "approved": [
                {"id": identifier, **hashes,
                 "checks": {check: True for check in assembler.CHECKS},
                 "evidence": {check: [{"path": self.evidence.name, "sha256": digest}]
                              for check in assembler.CHECKS}}
                for identifier, hashes in sorted(self.expected.items())]}

    def tearDown(self):
        self.temp.cleanup()

    def verify(self, receipt=None):
        return assembler.validate_qualification(receipt or self.receipt, self.directory,
                                                self.manifest_sha, self.expected)

    def test_synthetic_complete_receipt_identity(self):
        self.assertEqual(len(self.verify()), 6 * len(assembler.CHECKS))

    def test_pending_refused(self):
        self.receipt["status"] = "pending"
        with self.assertRaisesRegex(ValueError, "pending"):
            self.verify()

    def test_wrong_manifest_refused(self):
        self.receipt["correction_manifest_sha256"] = assembler.sha("different")
        with self.assertRaisesRegex(ValueError, "manifest hash"):
            self.verify()

    def test_partial_approval_refused(self):
        self.receipt["approved"].pop()
        with self.assertRaisesRegex(ValueError, "Exactly six"):
            self.verify()

    def test_wrong_row_hash_refused(self):
        self.receipt["approved"][0]["clean_html_sha256"] = assembler.sha("wrong")
        with self.assertRaisesRegex(ValueError, "row hash"):
            self.verify()

    def test_incomplete_visual_check_refused(self):
        self.receipt["approved"][0]["checks"]["visual_motion"] = False
        with self.assertRaisesRegex(ValueError, "visual_motion"):
            self.verify()

    def test_missing_evidence_refused(self):
        self.receipt["approved"][0]["evidence"]["negative_check"] = []
        with self.assertRaisesRegex(ValueError, "Evidence missing"):
            self.verify()

    def test_modified_evidence_refused(self):
        self.evidence.write_text("Changed synthetic evidence")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.verify()

    def test_declared_coordinator_required(self):
        self.receipt["qualified_by"] = ""
        with self.assertRaisesRegex(ValueError, "qualified_by"):
            self.verify()


class PanelAndStagingTests(unittest.TestCase):
    def test_exact_panel_membership_and_modified_line_refusal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            full = root / "full.jsonl"
            source_lines = [(json.dumps({"fixture": i}) + "\n").encode() for i in range(63)]
            full.write_bytes(b"".join(source_lines))
            panel = root / "panel"
            panel.mkdir()
            (panel / "valid.jsonl").write_bytes(b"".join(source_lines[:10]))
            meta = {assembler.sha(assembler.canon(json.loads(line))):
                    {"group_id": f"fixture-group-{i}", "split": "valid"}
                    for i, line in enumerate(source_lines)}
            manifest = {"source_valid_sha256": assembler.sha(full.read_bytes()),
                "panel_file_sha256": assembler.sha((panel / "valid.jsonl").read_bytes()),
                "row_count": 10, "rows": [{"source_valid_index_zero_based": i,
                    "source_line_sha256": assembler.sha(line.rstrip(b"\r\n")),
                    "provenance": {"group_id": f"fixture-group-{i}"}}
                    for i, line in enumerate(source_lines[:10])]}
            (panel / "manifest.json").write_text(json.dumps(manifest))
            self.assertEqual(len(assembler.select_panel(panel, full, meta)[3]), 10)
            altered = (panel / "valid.jsonl").read_bytes().replace(b'"fixture": 0', b'"fixture": 99', 1)
            (panel / "valid.jsonl").write_bytes(altered)
            manifest["panel_file_sha256"] = assembler.sha(altered)
            (panel / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "exact full-dev source line"):
                assembler.select_panel(panel, full, meta)

    def test_stage_keeps_raw_and_localizes_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); run = root / "run"; run.mkdir()
            original = '<!doctype html><html><head><script type="module">import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js";</script></head><body></body></html>'
            (run / "generated.html").write_text(original)
            destination = root / "review"
            subprocess.run([sys.executable, str(SCRIPTS / "stage_generated_page.py"),
                            "--run", str(run), "--destination", str(destination)], check=True)
            self.assertEqual((destination / "raw-model.html").read_text(), original)
            served = (destination / "generated.html").read_text()
            self.assertIn('/vendor/three/build/three.module.js', served)
            self.assertIn('1000/60', served)
            self.assertFalse(json.loads((destination / "adaptation.json").read_text())['asset_geometry_or_animation_edited'])

    def test_cli_help_without_data_or_dependencies(self):
        for filename in ("prepare_full_program_corrections.py", "assemble_correction_revision.py"):
            result = subprocess.run([sys.executable, str(SCRIPTS / filename), "--help"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for flag in ("--workspace", "--repo", "--tokenizer"):
                self.assertIn(flag, result.stdout)


if __name__ == "__main__":
    unittest.main()
