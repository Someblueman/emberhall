"""A good idea-second says ready; anything else lists why not."""
import subprocess
import sys
from pathlib import Path
import unittest

from scripts.idea_second_check import problems

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "idea_second_check.py"
GOOD = {
    "kind": "idea-second",
    "idea": "page-the-shelf",
    "verdict": "keep",
    "finding": "I opened the brief and the linked shelf pages, and I saw that "
               "the askers are quoted on the page itself and the reach is the "
               "whole house, so I keep this idea for the weeks it needs.",
}


class IdeaSecondCheckTests(unittest.TestCase):
    def test_good_payload_is_ready(self):
        self.assertEqual(problems(GOOD), [])

    def test_bad_kind_and_verdict_fail(self):
        payload = dict(GOOD, kind="idea", verdict="maybe")
        issues = problems(payload)
        self.assertTrue(any("kind" in i for i in issues))
        self.assertTrue(any("verdict" in i for i in issues))

    def test_short_finding_fails(self):
        issues = problems(dict(GOOD, finding="saw it"))
        self.assertTrue(any("120" in i for i in issues))

    def test_missing_and_extra_fields_fail(self):
        payload = {k: v for k, v in GOOD.items() if k != "idea"}
        self.assertTrue(any("idea" in i for i in problems(payload)))
        self.assertTrue(any("unexpected" in i for i in problems(dict(GOOD, note="x"))))
        self.assertTrue(problems(["not", "object"]))

    def test_cli_exit_codes(self):
        import json

        ok = subprocess.run([sys.executable, str(SCRIPT), json.dumps(GOOD)],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self.assertIn("ready", ok.stdout)
        bad = subprocess.run([sys.executable, str(SCRIPT), json.dumps(dict(GOOD, verdict="no"))],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("not ready", bad.stdout)
        empty = subprocess.run([sys.executable, str(SCRIPT)], input="  ",
                               capture_output=True, text=True)
        self.assertEqual(empty.returncode, 2)
        junk = subprocess.run([sys.executable, str(SCRIPT), "{not json"],
                              capture_output=True, text=True)
        self.assertEqual(junk.returncode, 2)


if __name__ == "__main__":
    unittest.main()
