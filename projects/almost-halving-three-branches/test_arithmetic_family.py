"""Graph-distance and command-line checks of the second ratio family."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import arithmetic_family as af
import published_cases as pc
from test_next_family import counts, distances


class ArithmeticFamilyTest(unittest.TestCase):
    def test_exact_symbolic_identities(self):
        for parity in (0, 1):
            self.assertEqual(af.symbolic_residual(parity), ({}, (0, 0)))

    def test_fresh_unequal_triples_with_graph_distances(self):
        for t in (1, 2, 14, 17, 22, 31):
            with self.subTest(t=t):
                witness = af.family_witness(t)
                metric = distances(witness["lengths"])
                left, right = witness["left"], witness["right"]
                self.assertEqual(len(left), 12 * t)
                self.assertEqual(len(right), 12 * t)
                self.assertFalse(set(left) & set(right))
                self.assertEqual(set(metric) - set(left) - set(right), {(1, 11 * t)})
                lp, rp = counts(left, metric), counts(right, metric)
                self.assertEqual(lp, rp)
                self.assertEqual(lp, witness["left_profile"])
                self.assertEqual(sum(lp.values()), (12 * t) * (12 * t - 1) // 2)
                self.assertTrue(witness["attains_bound"])

    def test_size_preserving_perturbation_rejected(self):
        for t in (14, 17):
            witness = af.family_witness(t)
            left = list(witness["left"])
            left[left.index((0, 0))] = (1, 11 * t)
            checked = pc.check_pair(witness["lengths"], left, witness["right"])
            self.assertFalse(checked["homometric"])

    def test_invalid_parameters(self):
        for t in (0, -1, True, 1.0, "2"):
            with self.subTest(t=t), self.assertRaises(ValueError):
                af.family_witness(t)

    def test_real_cli_round_trip_and_proof(self):
        script = str(Path(af.__file__))
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)
        run = subprocess.run([sys.executable, script, "17"],
                             text=True, capture_output=True, check=True)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(run.stdout)["size"], 204)


if __name__ == "__main__":
    unittest.main()
