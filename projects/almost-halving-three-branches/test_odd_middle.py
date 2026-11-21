"""Independent graph checks of the seven-five-three family."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import odd_middle as om
import published_cases as pc
from test_next_family import counts, distances


class OddMiddleTest(unittest.TestCase):
    def test_exact_four_class_identities(self):
        for m in range(4):
            self.assertEqual(om.symbolic_residual(m), ({}, (0, 0)))

    def test_fresh_scales_and_all_parity_classes(self):
        for t in (1, 2, 3, 5, 7, 9, 11, 17, 19, 22):
            with self.subTest(t=t):
                result = om.family_witness(t)
                metric = distances(result["lengths"])
                left, right = result["left"], result["right"]
                self.assertFalse(set(left) & set(right))
                self.assertEqual(len(left), len(right))
                self.assertEqual(len(left), 15 * t // 2)
                self.assertEqual(counts(left, metric), counts(right, metric))
                self.assertEqual(set(result["omitted"]), set(metric) - set(left) - set(right))
                self.assertTrue(result["attains_bound"])

    def test_altered_pair_rejected(self):
        result = om.family_witness(19)
        left = list(result["left"])
        left[left.index((0, 0))] = (1, 133)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_invalid_parameter(self):
        for t in (True, 0, -1, 2.0):
            with self.subTest(t=t), self.assertRaises(ValueError):
                om.family_witness(t)

    def test_cli_round_trip(self):
        script = str(Path(om.__file__))
        run = subprocess.run([sys.executable, script, "19"],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(run.stdout)["size"], 142)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)


if __name__ == "__main__":
    unittest.main()
