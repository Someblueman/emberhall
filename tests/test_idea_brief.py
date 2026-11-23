import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "idea_brief.py"
sys.path.insert(0, str(ROOT / "scripts"))
import idea_brief  # noqa: E402

FINDING = "opened the cited page and it matches " + "detail " * 80
DOC = {
    "idea_id": "sample-idea",
    "brief_revision": 42,
    "caller": {"authored_idea": False, "authored_current_brief": False,
               "checked_current_brief": True},
    "idea": {
        "title": "A Sample Idea", "scale": "house", "status": "shelved", "losses": 0,
        "plain": "Something a person will notice.",
        "what": "Build the sample thing.",
        "why": "Because the sample problem is real.",
        "first_step": "Measure the sample cost first.",
        "brief": {
            "for": "house", "field": "software", "worth": "useful",
            "benefit": "Saves every resident time.",
            "first_version": "A script anyone can run.",
            "interest": "Measured cost in the record.",
            "exists": "Nothing like it yet.",
            "check": "A non-author reruns the measurement.",
            "rather": "Cheaper than repeated manual work.",
            "reach": "All residents.",
            "asked": [{"who": "Steward", "where": "docs/STEWARD_ORDERS.md",
                       "said": "make sessions more efficient"}],
        },
        "seconds": [
            {"sequence": 10, "author": "resident-abcdef1234567890", "kind": "muse",
             "brief": 42, "finding": FINDING},
            {"sequence": 9, "author": "resident-0011223344556677", "kind": "codex",
             "brief": 41, "finding": FINDING},
        ],
    },
}


class IdeaBriefTests(unittest.TestCase):
    def test_brief_covers_case_and_collapses_checks(self):
        raw = len(json.dumps(DOC))
        out = idea_brief.brief(DOC, raw)
        self.assertIn("sample-idea | A Sample Idea", out)
        self.assertIn("checked_current_brief=True", out)
        for key in ("plain:", "what:", "why:", "first_step:", "benefit:",
                    "first_version:", "reach:", "asked (1):"):
            self.assertIn(key, out)
        self.assertIn("checks: 2 total, 1 on current brief", out)
        self.assertNotIn(FINDING.strip(), out)  # findings collapsed by default
        self.assertLess(len(out), raw)
        self.assertIn("saved ", out)

    def test_checks_flag_lists_one_line_each(self):
        out = idea_brief.brief(DOC, 0, show_checks=True)
        self.assertIn("seq=10 abcdef12 kind=muse brief=42", out)
        self.assertIn("seq=9 00112233 kind=codex brief=41", out)
        self.assertIn("…", out)  # long finding marked as shortened

    def test_full_field_expands_and_rejects_unknown(self):
        self.assertEqual(idea_brief.full_field(DOC, "benefit"),
                         "Saves every resident time.")
        self.assertIn(FINDING[:40], idea_brief.full_field(DOC, "seconds"))
        with self.assertRaises(ValueError):
            idea_brief.full_field(DOC, "no-such-field")

    def test_bad_shapes_rejected(self):
        with self.assertRaises(ValueError):
            idea_brief.brief({}, 0)
        with self.assertRaises(ValueError):
            idea_brief.brief({"idea": {}}, 0)

    def test_cli_stdin_and_errors(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "-"], input=json.dumps(DOC),
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("A Sample Idea", run.stdout)
        bad = subprocess.run([sys.executable, str(SCRIPT), "-"], input="not json",
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
