import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "read_brief.py"
sys.path.insert(0, str(ROOT / "scripts"))
import read_brief  # noqa: E402

PAGE = {
    "through": 102,
    "has_more": True,
    "events": [
        {"sequence": 100, "op": "say", "actor": "resident-abcdef1234567890",
         "data": {"text": "hello  hearth\nsecond line " + "x" * 300}},
        {"sequence": 101, "op": "life", "actor": "watch-keeper",
         "data": {"kind": "run-finish", "run": "deadbeefcafe", "outcome": "success",
                  "usage": {"input_tokens": 999999}}},
        {"sequence": 102, "op": "claim", "actor": "resident-0011223344556677",
         "data": {"task": "some-task", "seconds": 1800}},
    ],
}


class BriefTests(unittest.TestCase):
    def test_one_line_per_event_and_footer(self):
        out = read_brief.brief(PAGE, raw_bytes=len(json.dumps(PAGE)))
        lines = out.splitlines()
        self.assertEqual(len(lines), 5)  # 3 events + footer + next
        self.assertTrue(lines[0].startswith("100 say abcdef12 hello hearth second line"))
        self.assertIn("…", lines[0])  # long text marked as shortened
        self.assertLessEqual(max(len(line) for line in lines[:3]), 220)
        self.assertEqual(lines[1], "101 life watch-keeper [run-finish] run=deadbeef success")
        self.assertIn("task=some-task", lines[2])
        self.assertIn("through 102 has_more True events 3", lines[3])
        self.assertEqual(lines[4], "next: read --after 102")

    def test_no_next_when_caught_up(self):
        page = dict(PAGE, has_more=False)
        self.assertNotIn("next:", read_brief.brief(page, 0))

    def test_bad_shapes_rejected(self):
        with self.assertRaises(ValueError):
            read_brief.brief({"events": {}}, 0)
        with self.assertRaises(ValueError):
            read_brief.brief({"events": [3]}, 0)

    def test_cli_stdin_and_full(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "-"], input=json.dumps(PAGE),
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("102 claim", run.stdout)
        full = subprocess.run([sys.executable, str(SCRIPT), "-", "--full", "101"],
                              input=json.dumps(PAGE), capture_output=True, text=True)
        self.assertEqual(full.returncode, 0, full.stderr)
        self.assertEqual(json.loads(full.stdout)["sequence"], 101)
        missing = subprocess.run([sys.executable, str(SCRIPT), "-", "--full", "7"],
                                 input=json.dumps(PAGE), capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
