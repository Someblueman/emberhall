"""Journal summary collapses boilerplate and keeps substance one line per event."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.journal_summary import summarize


PAGE = {
    "events": [
        {"sequence": 18633, "op": "say", "actor": "watch-keeper",
         "data": {"text": "house-home-result-v1 {\"elapsed_seconds\": 1474.2}"}},
        {"sequence": 18634, "op": "say", "actor": "watch-keeper",
         "data": {"text": "house-mailbox-time-v1 {\"mailbox_seconds\": 1292.8}"}},
        {"sequence": 18635, "op": "life", "actor": "watch-keeper",
         "data": {"kind": "run-finish", "outcome": "success", "run": "faebf6"}},
        {"sequence": 18636, "op": "finish", "actor": "resident-abc",
         "data": {"task": "recover-lantern-signal-front-door", "result": "Public commit 32bdd40 recovers Lantern Loop."}},
        {"sequence": 18637, "op": "say", "actor": "resident-xyz",
         "data": {"text": "Hawthorn preserved a researched proposal for a room-scale Emberhall visit."}},
        {"sequence": 18638, "op": "shelf", "actor": "resident-xyz",
         "data": {"kind": "explore-release", "round": "hawthorn-house-6bc3b802"}},
        {"sequence": 18639, "op": "shelf", "actor": "resident-d31e",
         "data": {"kind": "project-done", "project": "great-after-dance-20261118"}},
    ],
    "through": 18639,
    "has_more": False,
}


class JournalSummaryTests(unittest.TestCase):
    def test_collapses_boilerplate_and_keeps_substance(self):
        out = summarize(PAGE)
        self.assertIn("7 events (4 kept, 3 boilerplate collapsed)", out)
        self.assertIn("through 18639", out)
        # kept lines
        self.assertIn("18636 finish", out)
        self.assertIn("recover-lantern-signal-front-door", out)
        self.assertIn("18637 say", out)
        self.assertIn("18639 shelf", out)
        # noise hidden
        self.assertNotIn("house-home-result-v1", out)
        self.assertNotIn("house-mailbox-time-v1", out)
        # one line per kept event (header + 4 lines)
        lines = out.rstrip("\n").split("\n")
        self.assertEqual(len(lines), 5)

    def test_include_noise_shows_all(self):
        out = summarize(PAGE, include_noise=True)
        self.assertIn("7 events (7 kept, 0 boilerplate collapsed)", out)
        self.assertIn("18633 say", out)

    def test_file_and_stdin_cli(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "journal_summary.py"
        payload = json.dumps(PAGE)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write(payload)
            path = f.name
        file_out = subprocess.run([sys.executable, str(script), path], capture_output=True, text=True, check=True)
        self.assertIn("18636 finish", file_out.stdout)
        stdin_out = subprocess.run([sys.executable, str(script), "-"], input=payload, capture_output=True, text=True, check=True)
        self.assertIn("18637 say", stdin_out.stdout)

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            summarize({"nope": 1})
        # quota run-finish is surfaced, not collapsed
        quota = {"events": [{"sequence": 1, "op": "life", "actor": "watch-keeper",
                             "data": {"kind": "run-finish", "outcome": "quota", "run": "abc"}}],
                 "through": 1, "has_more": False}
        out = summarize(quota)
        self.assertIn("quota", out)


if __name__ == "__main__":
    unittest.main()
