"""Independent graph and real-command controls for the periodic construction."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import general_odd_spacing as gos
import published_cases as pc
from test_next_family import counts, distances


class GeneralOddSpacingTest(unittest.TestCase):
    def test_exact_identity(self):
        for phase in (0, 1):
            self.assertEqual(gos.symbolic_residual(phase), {})

    def test_independent_graph_distances(self):
        for c, t in ((4,0), (4,3), (6,0), (6,1), (6,2), (8,1), (8,3),
                     (10,2), (12,1), (14,4), (18,2), (24,0), (10,5), (12,7)):
            with self.subTest(c=c, t=t):
                result = gos.periodic_witness(c, t)
                b = 2*c-1+4*t
                self.assertEqual(result["lengths"], (3*c-2+8*t, b, c))
                metric = distances(result["lengths"])
                left, right = result["left"], result["right"]
                self.assertEqual(len(left), (3*b-1)//2)
                self.assertEqual(len(right), len(left))
                self.assertFalse(set(left)&set(right))
                self.assertEqual(set(metric)-set(left)-set(right), {(2,b-1),(2,b)})
                self.assertEqual(counts(left, metric), counts(right, metric))
                self.assertEqual(counts(left, metric), result["left_profile"])
                self.assertTrue(result["attains_bound"])

    def test_altered_witness(self):
        result = gos.periodic_witness(8, 1)
        left = list(result["left"])
        left[left.index((0, 0))] = (2, result["b"]-1)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_domain_is_explicit(self):
        for c, t in ((True,0), (2,0), (5,0), (6.0,1), (6,True), (6,-1), (6,1.0)):
            with self.subTest(c=c, t=t), self.assertRaises(ValueError):
                gos.periodic_witness(c, t)

    def test_actual_command_and_checker(self):
        script = str(Path(gos.__file__))
        run = subprocess.run([sys.executable, script, "6", "3"],
                             capture_output=True, text=True, check=True)
        data = json.loads(run.stdout)
        self.assertEqual(data["lengths"], [40, 23, 6])
        self.assertEqual(data["size"], 34)
        check = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                               input=run.stdout, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        data["left"][0] = [2, 22]
        corrupted = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                   input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(corrupted.returncode, 1)
        self.assertFalse(json.loads(corrupted.stdout)["homometric"])
        proof = subprocess.run([sys.executable, script, "--prove"],
                               capture_output=True, text=True, check=True)
        self.assertIn("PASS", proof.stdout)
        for args in (("5","1"), ("8","-1"), ("8",), ("8","1","--prove")):
            invalid = subprocess.run([sys.executable, script, *args],
                                     capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 2)


if __name__ == "__main__":
    unittest.main()
