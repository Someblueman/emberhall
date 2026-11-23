"""A paged task reply reads as short lines, not raw JSON."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.task_brief import brief

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "task_brief.py"


def page():
    return {
        "tasks": {
            "ready-one": {"status": "open", "generation": 0, "plain": "Build the next piece."},
            "held-one": {"status": "claimed", "generation": 1, "owner": "fern", "plain": "Hold this one."},
        },
        "page": {"total": 2, "shown": 2, "next_offset": None},
    }


class TaskBriefTests(unittest.TestCase):
    def test_one_line_per_task_with_footer(self):
        out = brief(page())
        self.assertIn("ready-one [open gen 0]: Build the next piece.", out)
        self.assertIn("held-one [claimed gen 1 owner fern]: Hold this one.", out)
        self.assertIn("total 2 shown 2 next_offset none", out)

    def test_empty_page(self):
        out = brief({"tasks": {}, "page": {"total": 0, "shown": 0, "next_offset": None}})
        self.assertIn("no queued tasks", out)
        self.assertIn("total 0 shown 0", out)

    def test_bad_input_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "bad.json"
            f.write_text("not json", encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(f)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn("task_brief:", p.stderr)

    def test_missing_tasks_exits_two(self):
        p = subprocess.run(
            [sys.executable, str(SCRIPT), "-"],
            input=json.dumps({"page": {}}), capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
