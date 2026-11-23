"""Tests for the squared-distance residue checker."""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from q_residue_check import analyse, find_equal_pair, q_mod4  # noqa: E402


class TestQResidueCheck(unittest.TestCase):
    def test_counts_and_q(self):
        r = analyse(45, 20, 8)
        self.assertEqual(r["counts"], [19, 19, 18, 18])
        self.assertEqual(r["K"], 36)
        self.assertTrue(r["pair"])
        self.assertIsNotNone(r["witness"])

    def test_q_formula(self):
        self.assertEqual(q_mod4([0, 2, 17, 17], 36), 3)
        self.assertEqual(q_mod4([19, 17, 0, 0], 36), 3)

    def test_no_obstruction_on_all_six(self):
        for triple in [(45, 20, 8), (55, 20, 5), (45, 30, 8),
                       (40, 30, 14), (55, 50, 35), (55, 50, 23)]:
            self.assertTrue(analyse(*triple)["pair"], triple)

    def test_too_few_vertices_refused(self):
        found, witness = find_equal_pair([2, 0, 0, 0], 2)
        self.assertFalse(found)
        self.assertIsNone(witness)

    def test_cli_single(self):
        r = subprocess.run(
            [sys.executable, str(HERE / "q_residue_check.py"), "45", "20", "8"],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pair True", r.stdout)

    def test_cli_resistant_default(self):
        r = subprocess.run(
            [sys.executable, str(HERE / "q_residue_check.py")],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count("pair True"), 6)


if __name__ == "__main__":
    unittest.main()
