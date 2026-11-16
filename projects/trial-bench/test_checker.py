"""Unittest suite for the Trial Bench checker (stdlib only).

Covers every frozen-milestone rejection case plus the valid acceptance
case: edited pre-reveal block, missing exposure declaration, empty
observation, hash mismatch, and a valid synthetic report. Run with:

    python3 -m unittest discover -s projects/trial-bench -p "test_*.py" -v
"""

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT))

import checker


def valid_report():
    return json.loads((PROJECT / "example_report.json").read_text())


class CheckerValidationTests(unittest.TestCase):
    def test_accepts_valid_synthetic_report(self):
        self.assertEqual(checker.validate_report(valid_report()), [])

    def test_rejects_edited_pre_reveal_block(self):
        report = valid_report()
        report["phase1"]["prediction"] = "Edited after the receipt."
        errors = checker.validate_report(report)
        self.assertTrue(any("hash mismatch" in e for e in errors), errors)

    def test_rejects_missing_exposure_declaration(self):
        for mutate in (
            lambda r: r["phase1"].pop("exposure"),
            lambda r: r["phase1"].update(exposure=""),
            lambda r: r["phase1"].update(exposure="   "),
        ):
            report = valid_report()
            mutate(report)
            errors = checker.validate_report(report)
            self.assertTrue(
                any("exposure" in e for e in errors),
                errors,
            )

    def test_rejects_empty_observation(self):
        for value in ("", "   "):
            report = valid_report()
            report["phase2"]["observation"] = value
            errors = checker.validate_report(report)
            self.assertTrue(
                any("observation" in e for e in errors), errors
            )

    def test_rejects_hash_mismatch(self):
        report = valid_report()
        good = report["receipt"]["hash"]
        report["receipt"]["hash"] = ("0" if good[0] != "0" else "1") + good[1:]
        errors = checker.validate_report(report)
        self.assertTrue(any("hash mismatch" in e for e in errors), errors)

    def test_rejects_empty_prediction_and_reasoning(self):
        report = valid_report()
        report["phase1"]["prediction"] = ""
        self.assertTrue(checker.validate_report(report))
        report = valid_report()
        report["phase1"]["reasoning"] = ""
        self.assertTrue(checker.validate_report(report))

    def test_rejects_wrong_version_and_missing_sections(self):
        report = valid_report()
        report["version"] = 2
        self.assertTrue(checker.validate_report(report))
        report = valid_report()
        del report["phase2"]
        self.assertTrue(checker.validate_report(report))
        self.assertTrue(checker.validate_report("not an object"))

    def test_rejects_malformed_receipt_hash(self):
        report = valid_report()
        report["receipt"]["hash"] = "not-hex"
        errors = checker.validate_report(report)
        self.assertTrue(any("hex" in e for e in errors), errors)

    def test_hash_contract_matches_example(self):
        # Documents the JS/Python shared canonicalisation: sorted keys
        # exposure/prediction/reasoning, compact separators, raw UTF-8.
        report = valid_report()
        canonical = json.dumps(
            {
                "exposure": report["phase1"]["exposure"],
                "prediction": report["phase1"]["prediction"],
                "reasoning": report["phase1"]["reasoning"],
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(digest, report["receipt"]["hash"])
        self.assertEqual(digest, checker.compute_receipt_hash(report["phase1"]))


class CheckerCliTests(unittest.TestCase):
    def run_checker(self, path):
        return subprocess.run(
            [sys.executable, str(PROJECT / "checker.py"), str(path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_cli_accepts_example_and_rejects_tampered_copy(self):
        ok = self.run_checker(PROJECT / "example_report.json")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("VALID", ok.stdout)

        bad_path = PROJECT / "example_report.json"
        report = valid_report()
        report["phase1"]["reasoning"] = "Changed after the receipt."
        tmp = PROJECT / "example_report_tampered_tmp.json"
        tmp.write_text(json.dumps(report), encoding="utf-8")
        try:
            bad = self.run_checker(tmp)
            self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
            self.assertIn("hash mismatch", bad.stderr)
        finally:
            tmp.unlink()
        _ = bad_path


class PageContractTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "page script test needs Node")
    def test_page_state_and_export_agree_with_the_checker(self):
        run = subprocess.run(["node", str(PROJECT / "test_page_ui.js")],
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(checker.validate_report(report), [])
        report["phase1"]["prediction"] += " hindsight"
        self.assertTrue(any("hash mismatch" in error for error in checker.validate_report(report)))

    def test_page_is_self_contained_and_gates_phase_two(self):
        html = (PROJECT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="exposure"', html)
        self.assertIn('id="prediction"', html)
        self.assertIn('id="reasoning"', html)
        self.assertIn('id="receipt"', html)
        self.assertIn('id="supplied-prompt"', html)
        self.assertIn('id="edit-field"', html)
        self.assertIn('id="observation"', html)
        self.assertIn('id="export-output"', html)
        # Phase 2 starts locked and is only enabled after a receipt.
        self.assertIn('id="phase2" disabled', html)
        self.assertIn("phase2Fieldset.disabled = false", html)
        # Receipt uses the real browser hash primitive.
        self.assertIn("crypto.subtle.digest", html)
        self.assertIn("'SHA-256'", html)
        # Self-contained: no external scripts, styles or network calls.
        self.assertNotIn('src="http', html)
        self.assertNotIn("src='http", html)
        self.assertNotIn('href="http', html)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("XMLHttpRequest", html)
        # Export produces exactly one JSON report view.
        self.assertEqual(html.count('id="export-output"'), 1)
        self.assertIn("JSON.stringify(report", html)


if __name__ == "__main__":
    unittest.main()
