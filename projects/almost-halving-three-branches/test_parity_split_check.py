"""Tests for the even/odd parity-split checker."""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from parity_split_check import analyse  # noqa: E402


class TestParitySplitCheck(unittest.TestCase):
    def test_resistant_triple(self):
        r = analyse(45, 20, 8)
        self.assertEqual((r["K"], r["Ne"], r["No"]), (36, 37, 37))
        self.assertEqual(r["same"], [18])
        self.assertTrue(r["pair"])

    def test_second_triple(self):
        r = analyse(55, 20, 5)
        self.assertEqual((r["K"], r["Ne"], r["No"]), (39, 40, 41))
        self.assertEqual(r["same"], [19, 20])
        self.assertTrue(r["pair"])

    def test_no_parity_obstruction_on_all_six(self):
        for triple in [(45, 20, 8), (55, 20, 5), (45, 30, 8),
                       (40, 30, 14), (55, 50, 35), (55, 50, 23)]:
            self.assertTrue(analyse(*triple)["pair"], triple)

    def test_cli_single(self):
        r = subprocess.run(
            [sys.executable, str(HERE / "parity_split_check.py"), "45", "20", "8"],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pair True", r.stdout)
        self.assertIn("same [18]", r.stdout)

    def test_cli_resistant_default(self):
        r = subprocess.run(
            [sys.executable, str(HERE / "parity_split_check.py")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count("pair True"), 6)


if __name__ == "__main__":
    unittest.main()
