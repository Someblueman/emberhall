"""The independent check agrees with the project's classification, case by case.

These tests run the command as a subprocess, so the command line a reader is
told to use is the one the house's suite exercises.
"""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import progression_check


class ProgressionCheckTest(unittest.TestCase):
    def test_the_classification_is_read_as_the_project_states_it(self):
        self.assertTrue(progression_check.predicts_full_partition(3, 1))   # d divides b
        self.assertTrue(progression_check.predicts_full_partition(3, 2))   # 2d divides b+1
        self.assertTrue(progression_check.predicts_full_partition(5, 3))   # 2d divides b+1
        self.assertFalse(progression_check.predicts_full_partition(5, 2))  # neither holds
        self.assertFalse(progression_check.predicts_full_partition(5, 4))  # neither holds
        self.assertFalse(progression_check.predicts_full_partition(4, 1))  # b is even
        self.assertFalse(progression_check.predicts_full_partition(2, 1))  # b is even

    def test_every_case_agrees(self):
        for b, d in progression_check.cases(5):
            row = progression_check.case(b, d)
            passed, detail = progression_check.check_case(row)
            self.assertTrue(passed, (b, d, detail))

    def test_the_negative_cases_are_exactly_the_two_the_classification_names(self):
        negative = [(b, d) for b, d in progression_check.cases(5)
                    if b % 2 == 1 and not progression_check.predicts_full_partition(b, d)]
        self.assertEqual(negative, [(5, 2), (5, 4)])
        for b, d in negative:
            row = progression_check.case(b, d)
            self.assertEqual(row["optimum"], row["target"])
            self.assertEqual(row["optimum"], row["full_size"] - 1)

    def test_an_odd_b_case_has_a_full_partition_when_the_classification_says_so(self):
        for b, d in progression_check.cases(5):
            row = progression_check.case(b, d)
            if row["predicted"]:
                self.assertEqual(row["optimum"], row["full_size"], (b, d))
                self.assertEqual(2 * row["optimum"], 3 * b + 1, (b, d))

    def test_the_command_passes(self):
        result = subprocess.run([sys.executable, str(HERE / "progression_check.py"),
                                 "--middle", "5"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHECK PASSED over 10 cases", result.stdout)
        self.assertNotIn("FAIL:", result.stdout)


if __name__ == "__main__":
    unittest.main()
