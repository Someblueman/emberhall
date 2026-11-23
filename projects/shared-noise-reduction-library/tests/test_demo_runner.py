"""Subprocess check that one command runs both importing programs."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestDemoRunner(unittest.TestCase):
    def test_one_command_runs_both_programs(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "run_all_demos.py")],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("importing program: shared monitor", proc.stdout)
        self.assertIn("weighted-fit program", proc.stdout)
        self.assertIn("both covreduce importing programs passed",
                      proc.stdout)


if __name__ == "__main__":
    unittest.main()
