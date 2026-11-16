"""Drift guards for MILESTONE2_AUDIT.md.

The audit is a dated map from TRIAL.md's ten human steps to the checks
that already cover them. These tests re-derive the audit's load-bearing
numbers -- sample hashes and identity, probe findings on the committed
sample, and the pre-audit test count -- so the document cannot stay
plausible after the facts move. They run no browser and no screen
reader, and they cannot make the milestone-2 try pass.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import unittest
from pathlib import Path

import probe

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "MILESTONE2_AUDIT.md"
TRIAL = ROOT / "TRIAL.md"
SAMPLE = ROOT / "sample" / "milestone-2"

CATEGORIES = {
    "covered-by-automated-check",
    "covered-by-unexecuted-browser-try",
    "blocked-on-Steward",
}
PRE_AUDIT_TESTS = 138


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _step_rows(audit_text: str) -> list[tuple[int, str, str]]:
    rows = []
    for line in audit_text.splitlines():
        match = re.match(r"\| (\d+) \| ([^|]+) \| ([a-zA-Z-]+) \|", line)
        if match:
            rows.append((int(match.group(1)), match.group(2).strip(),
                         match.group(3)))
    return rows


class Milestone2AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = AUDIT.read_text(encoding="utf-8")

    def test_trial_has_ten_steps_and_audit_covers_each_once(self) -> None:
        trial = TRIAL.read_text(encoding="utf-8")
        steps_section = trial.partition("## The steps")[2]
        # Numbered steps 1..10 with bold titles, e.g. "1. **Open it offline.**"
        trial_steps = re.findall(r"^(\d+)\. \*\*", steps_section,
                                 flags=re.MULTILINE)
        self.assertEqual([str(n) for n in range(1, 11)], trial_steps)
        rows = _step_rows(self.audit)
        self.assertEqual(list(range(1, 11)), [row[0] for row in rows])
        for _, _, category in rows:
            self.assertIn(category, CATEGORIES)
        self.assertEqual(
            {"covered-by-automated-check": 3,
             "covered-by-unexecuted-browser-try": 5,
             "blocked-on-Steward": 2},
            dict(collections.Counter(row[2] for row in rows)),
        )

    def test_audit_makes_no_browser_or_completion_claim(self) -> None:
        text = _normalized(self.audit)
        self.assertIn("used no browser and no screen reader", text)
        self.assertIn("does not complete milestone 2", text)
        self.assertIn("0 of 10 human steps executed", text)
        for claim in ("milestone 2 is complete", "all ten steps passed",
                      "screen reader was run", "browser try passed"):
            self.assertNotIn(claim, text.lower())

    def test_sample_identity_and_hashes_match_audit(self) -> None:
        packet = json.loads((SAMPLE / "packet.json").read_text(encoding="utf-8"))
        self.assertEqual("review-skein-packet", packet["format"])
        for side in ("base", "head"):
            self.assertIn(packet[side]["commit"], self.audit)
        self.assertEqual(3, len(packet["files"]))
        self.assertEqual(["added"] * 3, [f["status"] for f in packet["files"]])
        self.assertEqual(370, sum(f["new_lines"] for f in packet["files"]))
        anchors = json.loads((SAMPLE / "anchors.json").read_text(encoding="utf-8"))
        self.assertEqual(370, len(anchors["anchors"]))
        comments = json.loads((SAMPLE / "comments.json").read_text(encoding="utf-8"))
        self.assertEqual([], comments["comments"])
        for name in ("review.html", "packet.json", "anchors.json", "comments.json"):
            data = (SAMPLE / name).read_bytes()
            self.assertIn(hashlib.sha256(data).hexdigest(), self.audit, name)
            self.assertIn(f"{len(data)} bytes", self.audit, name)

    def test_probe_audit_of_sample_matches_audit_counts(self) -> None:
        tree, notes = probe.load_packet(SAMPLE)
        findings = probe.audit(tree, notes)
        errors = [f for f in findings if f.severity == "error"]
        self.assertEqual([], errors)
        self.assertEqual(["packet-identity"], [f.code for f in findings])
        summary = probe.summarize(tree)
        self.assertEqual(
            {"headings": 4, "rows": 373, "sections": 3, "tables": 3}, summary)
        self.assertIn(
            '{"headings": 4, "rows": 373, "sections": 3, "tables": 3}',
            self.audit)
        lines = probe.transcript(tree, max_rows=10000)
        self.assertEqual(393, len(lines))
        self.assertEqual(
            370, sum(1 for line in lines if line.startswith("  Added.")))
        _, standalone_notes = probe.load_packet(SAMPLE / "review.html")
        self.assertEqual(["standalone-html"],
                         [f.code for f in standalone_notes])

    def test_pre_audit_test_count_matches_discovery_minus_this_file(self) -> None:
        loader = unittest.TestLoader()
        total = loader.discover(str(ROOT)).countTestCases()
        own = loader.loadTestsFromTestCase(Milestone2AuditTests).countTestCases()
        self.assertEqual(PRE_AUDIT_TESTS, total - own)
        self.assertIn(f"Ran {PRE_AUDIT_TESTS} tests", self.audit)
        self.assertIn(str(PRE_AUDIT_TESTS + own), self.audit)

    def test_audit_names_every_category_and_the_closing_requirement(self) -> None:
        for category in CATEGORIES:
            # Once in the definitions and at least once in the step map.
            self.assertGreaterEqual(self.audit.count(category), 2, category)
        text = _normalized(self.audit)
        self.assertIn("exact spoken sentence from step 9", text)
        self.assertIn("not an eligible unspoiled triallist", text)


if __name__ == "__main__":
    unittest.main()
