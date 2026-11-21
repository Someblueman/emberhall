"""Graph-distance checks for the all-quotients divisible subfamily."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import progression_target as pt
import published_cases as pc
from test_next_family import counts, distances


class ProgressionTargetTest(unittest.TestCase):
    def test_three_variable_identities(self):
        self.assertEqual(pt.even_divisor_residual(0), {})
        self.assertEqual(pt.even_divisor_residual(1), {})

    def test_all_construction_branches_with_graph_distances(self):
        for q, d in ((2, 1), (4, 5), (3, 3), (9, 5),
                     (3, 2), (5, 4), (7, 6), (11, 10), (9, 12)):
            with self.subTest(q=q, d=d):
                result = pt.divisible_witness(q, d)
                left, right = result["left"], result["right"]
                metric = distances(result["lengths"])
                self.assertEqual(len(left), (3 * q * d + 1) // 2)
                self.assertEqual(len(left), len(right))
                self.assertFalse(set(left) & set(right))
                omitted = set() if q * d % 2 else {(1, (q + 1) * d)}
                self.assertEqual(set(metric) - set(left) - set(right), omitted)
                self.assertEqual(counts(left, metric), counts(right, metric))
                self.assertEqual(counts(left, metric), result["left_profile"])
                self.assertTrue(result["attains_bound"])

    def test_changed_pair_rejected(self):
        result = pt.divisible_witness(7, 6)
        left = list(result["left"])
        left[left.index((0, 0))] = (1, 48)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_parameter_validation(self):
        for q, d in ((1, 3), (0, 3), (3, 0), (True, 3), (3, 2.0)):
            with self.subTest(q=q, d=d), self.assertRaises(ValueError):
                pt.divisible_witness(q, d)

    def test_real_commands(self):
        script = str(Path(pt.__file__))
        run = subprocess.run([sys.executable, script, "7", "10"],
                             text=True, capture_output=True, check=True)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(run.stdout)["size"], 105)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)


if __name__ == "__main__":
    unittest.main()
