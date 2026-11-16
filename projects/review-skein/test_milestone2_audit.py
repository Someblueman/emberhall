"""Drift guards for MILESTONE2_AUDIT.md.

The audit is a dated map from TRIAL.md's ten human steps to the checks
that already cover them. These tests re-derive the audit's load-bearing
numbers -- sample hashes and identity, probe findings on the committed
sample, and the pre-audit test count -- so the document cannot stay
plausible after the facts move. They run no browser and no screen
reader, and they cannot make the milestone-2 try pass. The method checks
keep the rebuilt viewer contract separate from unobserved speech, zoom
and download evidence. The sample checks below
exercise the static DOM reader only, not the native keyboard driver.
"""
from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

import probe

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "MILESTONE2_AUDIT.md"
README = ROOT / "README.md"
TRIAL = ROOT / "TRIAL.md"
TRIAL_EDITOR = ROOT / "TRIAL_EDITOR.md"
SAMPLE = ROOT / "sample" / "milestone-2"
MIXED = ROOT / "sample" / "milestone-2-mixed"
VIEW = ROOT.parents[1] / "house" / "view.py"

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
        # View-criteria tests in this file do not change the pre-audit
        # floor: discovery minus the current own count stays >= PRE_AUDIT.
        # The audit is a dated snapshot at 6 tests (144 total), so its
        # historical total is checked literally, not against today's own.
        self.assertGreaterEqual(total - own, PRE_AUDIT_TESTS)
        self.assertIn(f"Ran {PRE_AUDIT_TESTS} tests", self.audit)
        self.assertIn("144 - 6 = 138", self.audit)

    def test_audit_names_every_category_and_the_closing_requirement(self) -> None:
        for category in CATEGORIES:
            # Once in the definitions and at least once in the step map.
            self.assertGreaterEqual(self.audit.count(category), 2, category)
        text = _normalized(self.audit)
        self.assertIn("exact spoken sentence from step 9", text)
        self.assertIn("not an eligible unspoiled triallist", text)

    def _step_sections(self, doc_path: Path) -> dict[int, str]:
        doc = doc_path.read_text(encoding="utf-8")
        steps_section = doc.partition("## The steps")[2]
        matches = list(re.finditer(r"^(\d+)\. \*\*", steps_section,
                                   flags=re.MULTILINE))
        sections: dict[int, str] = {}
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(steps_section)
            sections[int(match.group(1))] = steps_section[start:end]
        return sections

    def test_trial_methods_use_rebuilt_viewer_contract(self) -> None:
        self.assertEqual(list(range(1, 11)), sorted(self._step_sections(TRIAL)))
        self.assertEqual(list(range(1, 13)), sorted(self._step_sections(TRIAL_EDITOR)))
        for path in (TRIAL, TRIAL_EDITOR):
            text = path.read_text(encoding="utf-8")
            for signal in ("keyboard_walk", "step_log", "layout_width", "pictured_to"):
                self.assertIn(signal, text, path.name)
            for obsolete in ("presses no real keys", "never presses real keys",
                             "content policy blocks measurement",
                             "steps are not observed on this content-policy page"):
                self.assertNotIn(obsolete, _normalized(text).lower(), path.name)

    def test_trial_methods_keep_unobserved_evidence_explicit(self) -> None:
        for path in (TRIAL, TRIAL_EDITOR):
            steps = self._step_sections(path)
            # Native input and geometry are available; browser zoom and speech
            # remain separate evidence, not inferred from markup or keys.
            self.assertIn("NOT RUN", steps[8])
            speech = steps[9] if path == TRIAL else steps[6]
            self.assertIn("NOT RUN", speech)
            geometry = _normalized(steps[7])
            for phrase in ("wider_than_screen", "false", "unclipped",
                           "NOT RUN / uncertain", "cannot override", "FAIL"):
                self.assertIn(phrase, geometry, path.name)
        editor = TRIAL_EDITOR.read_text(encoding="utf-8")
        self.assertIn('never "full"', editor)
        self.assertIn("transcribed returned JSON", editor)
        self.assertIn("NOT RUN", self._step_sections(TRIAL_EDITOR)[9])
        self.assertIn("milestone 2 is not closed", README.read_text(encoding="utf-8").lower())

    def _mixed_viewer_signals(self) -> dict:
        # house/view.py is stdlib-only; load it by path and run its own
        # DOM reader on the preferred sample. This page has no scripts,
        # so the reader's fields are the fields a `view` return carries.
        spec = importlib.util.spec_from_file_location("house_view", VIEW)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.read((MIXED / "review.html").read_text(encoding="utf-8"))

    def test_mixed_sample_viewer_signals_satisfy_required_steps(self) -> None:
        signals = self._mixed_viewer_signals()
        packet = json.loads((MIXED / "packet.json").read_text(encoding="utf-8"))
        comments = json.loads((MIXED / "comments.json").read_text(encoding="utf-8"))
        text, headings, tab_order = signals["text"], signals["headings"], signals["tab_order"]
        names = [entry.split(": ", 1)[1] for entry in tab_order]
        # Step 1: identity, language, base/head and diff content are returned.
        self.assertEqual("Skein review", signals["title"])
        self.assertEqual("en", signals["language"])
        for side in ("base", "head"):
            self.assertIn(packet[side]["commit"], text)
        # Static reader snapshots establish names only. Actual activation,
        # focus and phone geometry require the native viewer trial.
        self.assertEqual("1. a: Skip to changed files", tab_order[0])
        self.assertNotIn("href", json.dumps(signals))
        # Step 3: file stops correspond to file headings by returned name,
        # and statuses appear as rendered (packet values, lower-case here).
        files = packet["files"]
        file_headings = [h.split(": ", 1)[1] for h in headings
                         if h.startswith("h2: ") and "Comments in view" not in h]
        self.assertEqual(file_headings, names[1:1 + len(files)])
        for entry in files:
            self.assertIn(f"{entry['status']}:", text)
        # Steps 4-5: column names, line counts and every status word are
        # in the returned text.
        for phrase in ("Old", "New", "Base text", "Head text", "old /",
                       "Added.", "Removed.", "Changed.", "Unchanged.", "Comment."):
            self.assertIn(phrase, text)
        # Step 6: stops are skip + one per file + one per comment, all named.
        self.assertEqual(1 + len(files) + len(comments["comments"]), signals["tab_stops"])
        self.assertFalse(any(name == "(no name)" for name in names))
        self.assertEqual(0, signals["unlabelled_controls"])


if __name__ == "__main__":
    unittest.main()
