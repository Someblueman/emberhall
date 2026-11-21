"""Graph and finite exhaustive controls for the odd-middle construction."""
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import unittest

import next_odd_family as nf
import published_cases as pc
from test_next_family import counts, distances


class NextOddFamilyTest(unittest.TestCase):
    def test_independent_variable_identity(self):
        self.assertEqual(nf.symbolic_residual(), {})

    def test_graph_distances_and_boundary(self):
        for b, d in ((3, 2), (5, 2), (5, 4), (11, 8), (15, 2),
                     (19, 4), (25, 24), (39, 14), (51, 32)):
            with self.subTest(b=b, d=d):
                result = nf.family_witness(b, d)
                left, right = result["left"], result["right"]
                metric = distances(result["lengths"])
                self.assertEqual(len(left), (3 * b - 1) // 2)
                self.assertEqual(len(right), len(left))
                self.assertFalse(set(left) & set(right))
                self.assertEqual(set(metric) - set(left) - set(right), {(2, b), (3, b-d)})
                self.assertEqual(counts(left, metric), counts(right, metric))
                self.assertEqual(counts(left, metric), result["left_profile"])
        # A full partition exists here: the new pair is not always optimal.
        self.assertFalse(nf.family_witness(15, 2)["attains_bound"])
        self.assertTrue(nf.family_witness(11, 8)["attains_bound"])

    def test_small_full_partition_obstruction_exhaustively(self):
        metric = distances((7, 5, 3))
        vertices = list(metric)
        # Fix the centre on one side to remove complementary duplicates.
        for rest in combinations(vertices[1:], 7):
            left = [(0, 0), *rest]
            right = list(set(vertices) - set(left))
            self.assertNotEqual(counts(left, metric), counts(right, metric))
        self.assertEqual(nf.family_witness(5, 2)["size"], 7)

    def test_altered_pair_is_rejected(self):
        result = nf.family_witness(11, 8)
        left = list(result["left"])
        left[left.index((0, 0))] = (2, 11)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_invalid_parameters(self):
        for b, d in ((1, 0), (4, 2), (7, 3), (5, 6), (5, 0), (True, 2), (5, 2.0)):
            with self.subTest(b=b, d=d), self.assertRaises(ValueError):
                nf.family_witness(b, d)

    def test_real_commands_and_existing_checker(self):
        script = str(Path(nf.__file__))
        run = subprocess.run([sys.executable, script, "11", "8"],
                             text=True, capture_output=True, check=True)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(run.stdout)["size"], 16)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)
        invalid = subprocess.run([sys.executable, script, "11", "3"],
                                 text=True, capture_output=True)
        self.assertEqual(invalid.returncode, 2)


if __name__ == "__main__":
    unittest.main()
