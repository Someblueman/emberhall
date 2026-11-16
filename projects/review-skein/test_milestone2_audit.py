"""Drift guards for MILESTONE2_AUDIT.md.

The audit is a dated map from TRIAL.md's ten human steps to the checks
that already cover them. These tests re-derive the audit's load-bearing
numbers -- sample hashes and identity, probe findings on the committed
sample, and the pre-audit test count -- so the document cannot stay
plausible after the facts move. They run no browser and no screen
reader, and they cannot make the milestone-2 try pass. The view-criteria
tests additionally guard that TRIAL.md, TRIAL_EDITOR.md, and README.md
keep viewer PASS conditions strictly within returned observables, treat
true overflow as a failure without DOM-text overrides, mark unobserved
phone geometry NOT RUN / uncertain, and keep keyboard, zoom, and speech
explicitly NOT RUN.
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

    def test_trial_close_requires_only_view_observable_steps(self) -> None:
        trial = TRIAL.read_text(encoding="utf-8")
        text = _normalized(trial).lower()
        # The view-based close never requires steps 1-8 (zoom).
        self.assertIn("limited rendered-content inspection", text)
        self.assertIn("steps 1–6 are all `pass`", text)
        self.assertNotIn("steps 1-8 are", text)
        self.assertNotIn("steps 1–8 are", text)
        self.assertNotIn("steps 1-8 all", text)
        self.assertNotIn("steps 1–8 all", text)
        # Steps 8-10 are excluded from the close rule.
        self.assertIn("steps 8–10 are", text)
        self.assertNotIn("steps 8–10 all", text)
        self.assertNotIn("steps 8–10 are all", text)
        # Unavailable actions are named as viewer limits, never required.
        for phrase in ("presses no real keys", "takes no zoom",
                       "speaks nothing"):
            self.assertIn(phrase, text)

    def test_trial_view_steps_name_returned_signals(self) -> None:
        sections = self._step_sections(TRIAL)
        self.assertEqual(list(range(1, 11)), sorted(sections))
        signals = ("text", "headings", "tab_order", "wider_than_screen",
                   "focused_after_steps", "unlabelled_controls",
                   "screenshot")
        for step in range(1, 8):
            body = sections[step]
            self.assertTrue(
                any(signal in body for signal in signals),
                f"step {step} names no view signal",
            )
        # Unavailable actions are explicitly NOT RUN in place.
        for step in (2, 3, 6, 7, 8, 9, 10):
            self.assertIn("NOT RUN", sections[step], f"step {step}")
        # Step 6 keeps DOM-snapshot honesty and names the full interactive surface
        # (including comment links and #orphans when present, as in the mixed sample).
        step6 = _normalized(sections[6]).lower()
        self.assertIn("snapshot", step6)
        self.assertIn("skip link", step6)
        self.assertIn("changed-files index", step6)
        self.assertIn("orphaned and unplaced comments", step6)
        self.assertIn("comment link", step6)

    def test_trial_does_not_require_unperformed_interaction(self) -> None:
        trial = TRIAL.read_text(encoding="utf-8")
        text = _normalized(trial)
        sections = self._step_sections(TRIAL)
        lowered = text.lower()
        self.assertNotIn("press `tab` once", lowered)
        self.assertNotIn("press `enter`", lowered)
        self.assertNotIn("8. **zoom.**", lowered)
        self.assertNotIn("6. **keyboard only.**", lowered)
        self.assertIn("never claim activation", text)
        self.assertIn("never claim them from this snapshot", text)
        self.assertIn("cannot zoom to 200", _normalized(sections[8]).lower())
        self.assertIn("NOT RUN", sections[8])

    def test_trial_and_editor_geometry_honesty(self) -> None:
        trial_raw = TRIAL.read_text(encoding="utf-8")
        editor_raw = TRIAL_EDITOR.read_text(encoding="utf-8")
        trial_steps = self._step_sections(TRIAL)
        editor_steps = self._step_sections(TRIAL_EDITOR)

        for name, text in (("TRIAL.md", trial_raw), ("TRIAL_EDITOR.md", editor_raw)):
            lowered = _normalized(text).lower()
            for forbidden in (
                "without an explanation that the text contradicts",
                "without a contradiction from",
                "contradiction from `text`",
                "judge this step from `text` and the desktop screenshot",
                "judge this step from `wider_than_screen`, `text`, `tab_order` and the desktop screenshot",
                "cropped phone screenshot alone is **not** a `fail`",
                "cropped phone screenshot alone is neither a `pass` nor a `fail`",
                "steps 1–7 `pass` through the house viewer",
                "steps 1–7 are all `pass`",
            ):
                self.assertNotIn(forbidden, lowered, f"{name}: {forbidden}")

        # Step 1 & Step 7 in TRIAL.md and Step 7 in TRIAL_EDITOR.md must:
        # (1) fail any wider_than_screen == true without DOM/desktop overrides,
        # (2) record null/clipped phone geometry as NOT RUN / uncertain (never phone-fit PASS),
        # (3) require observed false + unclipped phone screenshot for phone-fit PASS.
        for label, section in (
            ("TRIAL step 1", trial_steps[1]),
            ("TRIAL step 7", trial_steps[7]),
            ("TRIAL_EDITOR step 7", editor_steps[7]),
        ):
            norm = _normalized(section)
            lowered = norm.lower()
            self.assertIn("wider_than_screen", norm, label)
            self.assertIn("NOT RUN / uncertain", norm, label)
            self.assertIn("cannot override", lowered, label)
            self.assertIn("fail", lowered, label)

        for label, section in (
            ("TRIAL step 7", trial_steps[7]),
            ("TRIAL_EDITOR step 7", editor_steps[7]),
        ):
            lowered = _normalized(section).lower()
            self.assertIn("never a phone-fit `pass`", lowered, label)
            self.assertIn("unclipped", lowered, label)

    def test_readme_and_trial_editor_agree_with_view_limits(self) -> None:
        readme = README.read_text(encoding="utf-8")
        readme_norm = _normalized(readme).lower()
        self.assertIn("limited rendered-content inspection", readme_norm)
        self.assertIn("not run / uncertain", readme_norm)
        self.assertNotIn("steps 1–7 `pass`", readme_norm)
        self.assertNotIn("steps 1-7 `pass`", readme_norm)
        self.assertIn("milestone 2 is not closed", readme_norm)

        editor = TRIAL_EDITOR.read_text(encoding="utf-8")
        editor_norm = _normalized(editor)
        self.assertIn("House viewer limits", editor)
        self.assertIn("presses no real keys", editor_norm)
        self.assertIn('never "full"', editor_norm)
        self.assertIn("steps 2–6, 8 and 9 are", editor_norm)
        self.assertIn("limited rendered-content", editor_norm.lower())
        self.assertIn("NOT RUN / uncertain", editor_norm)

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
        sections = self._step_sections(TRIAL)
        text, headings, tab_order = signals["text"], signals["headings"], signals["tab_order"]
        names = [entry.split(": ", 1)[1] for entry in tab_order]
        # Step 1: identity, language, base/head and diff content are returned.
        self.assertEqual("Skein review", signals["title"])
        self.assertEqual("en", signals["language"])
        for side in ("base", "head"):
            self.assertIn(packet[side]["commit"], text)
        # Step 2: only the first stop's returned name is observable. The
        # viewer returns no href and no non-focusable element ID, so the
        # skip target cannot be found in any returned field, and TRIAL.md
        # must not require it (or a screenshot of the unfocused link).
        self.assertEqual("1. a: Skip to changed files", tab_order[0])
        self.assertNotIn("#files", text)
        self.assertFalse(any("#files" in field for field in headings + tab_order))
        self.assertNotIn("href", json.dumps(signals))
        step2 = _normalized(sections[2])
        for forbidden in ("contain its `#files` target",
                          "desktop screenshot shows where the link sits",
                          "the target is missing from"):
            self.assertNotIn(forbidden, step2)
        self.assertIn("no `href`", step2)
        self.assertIn("NOT RUN", step2)
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
        # Step 1 must not fail on the phone screenshot's right-edge
        # clipping alone; step 7 owns that as NOT RUN / uncertain.
        self.assertIn("not a step 1 `FAIL`", _normalized(sections[1]))


if __name__ == "__main__":
    unittest.main()
