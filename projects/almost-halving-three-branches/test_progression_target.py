"""Graph-distance checks for every even-middle construction branch."""
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
        self.assertEqual(pt.even_middle_residual(), {})
        self.assertEqual(pt.odd_class_residual(), {})

    def test_all_construction_branches_with_graph_distances(self):
        for b, d in ((2, 1), (4, 1), (14, 4), (28, 10), (70, 10),
                     (22, 20), (14, 5), (40, 17), (20, 19)):
            with self.subTest(b=b, d=d):
                result = pt.even_middle_witness(b, d)
                left, right = result["left"], result["right"]
                metric = distances(result["lengths"])
                self.assertEqual(len(left), 3 * b // 2)
                self.assertEqual(len(left), len(right))
                self.assertFalse(set(left) & set(right))
                omitted = {(1, b + d)} if d % 2 == 0 else {(3, b - d)}
                self.assertEqual(set(metric) - set(left) - set(right), omitted)
                self.assertEqual(counts(left, metric), counts(right, metric))
                self.assertEqual(counts(left, metric), result["left_profile"])
                self.assertTrue(result["attains_bound"])

    def test_odd_congruence_class_with_independent_distances(self):
        for b, d in ((5, 3), (13, 3), (17, 7), (25, 11), (33, 15)):
            with self.subTest(b=b, d=d):
                result = pt.odd_class_witness(b, d)
                left, right = result["left"], result["right"]
                metric = distances(result["lengths"])
                self.assertFalse(set(left) & set(right))
                self.assertEqual(set(metric) - set(left) - set(right), {(1, b + d), (3, b - d)})
                self.assertEqual(len(left), (3 * b - 1) // 2)
                self.assertEqual(len(right), len(left))
                self.assertEqual(counts(left, metric), counts(right, metric))
        # The target construction must not claim maximality when a full pair exists.
        self.assertFalse(pt.odd_class_witness(5, 3)["attains_bound"])

    def test_changed_pair_rejected(self):
        result = pt.even_middle_witness(42, 6)
        left = list(result["left"])
        left[left.index((0, 0))] = (1, 48)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_parameter_validation(self):
        for b, d in ((1, 3), (0, 3), (3, 1), (4, 4), (4, 0), (True, 3), (4, 2.0)):
            with self.subTest(b=b, d=d), self.assertRaises(ValueError):
                pt.even_middle_witness(b, d)

    def test_real_commands(self):
        script = str(Path(pt.__file__))
        run = subprocess.run([sys.executable, script, "70", "10"],
                             text=True, capture_output=True, check=True)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(run.stdout)["size"], 105)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)
        odd = subprocess.run([sys.executable, script, "13", "3", "--summary"],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(odd.stdout)["size"], 19)
        unknown = subprocess.run([sys.executable, script, "7", "6"],
                                 text=True, capture_output=True)
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("not covered", unknown.stderr)


if __name__ == "__main__":
    unittest.main()
