"""Independent graph counts and exhaustive checks of bounded sign search."""
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import middle_prefix as mp
import published_cases as pc
from test_next_family import counts, distances


class MiddlePrefixTest(unittest.TestCase):
    def check_witness(self, result):
        metric = distances(result["lengths"])
        left, right = result["left"], result["right"]
        self.assertFalse(set(left) & set(right))
        self.assertEqual(len(left), len(right))
        self.assertEqual(len(left), result["target"])
        self.assertEqual(counts(left, metric), counts(right, metric))
        self.assertEqual(set(metric) - set(left) - set(right), set(result["omitted"]))
        self.assertEqual(set(result["omitted"]),
                         {(2, result["lengths"][1] - 1), (2, result["lengths"][1])})

    def test_all_four_symbolic_classes(self):
        for m in range(4):
            self.assertEqual(mp.symbolic_residual(m), ({}, (0, 0)))

    def test_bases_boundaries_and_fresh_family_parameters(self):
        for d in (1, 3, 5, 7, 9, 11, 13, 15, 17, 23, 31, 37, 59):
            with self.subTest(d=d):
                result = mp.checked_witness(2 * d + 3, d, mp.family_signs(d))
                self.check_witness(result)
                self.assertEqual(result["size"], 3 * d + 4)
                if d >= 5:
                    self.assertTrue(result["attains_bound"])

    def test_search_previously_limited_cases(self):
        for b, d in ((47, 7), (57, 9)):
            with self.subTest(b=b, d=d):
                result = mp.search(b, d)
                self.assertEqual(result["status"], "partition")
                self.check_witness(result)

    def test_exact_search_against_exhaustive_sign_oracle(self):
        rng = random.Random(620527)
        for n in range(1, 6):
            for _ in range(12):
                rows = [tuple((i, c) for i in range(n)
                              if (c := rng.randrange(-2, 3))) for _ in range(3)]
                targets = [rng.randrange(1, 4) for _ in rows]
                expected = any(all(abs(sum(c * signs[i] for i, c in row)) == target
                                   for row, target in zip(rows, targets))
                               for signs in product((-1, 1), repeat=n))
                actual, _, exhausted = mp.sign_search(rows, targets, n, 1000)
                self.assertTrue(exhausted)
                self.assertEqual(actual is not None, expected)
                if actual is not None:
                    self.assertTrue(all(abs(sum(c * actual[i] for i, c in row)) == target
                                        for row, target in zip(rows, targets)))

    def test_zero_constraint_and_node_limit_are_distinct(self):
        self.assertEqual(mp.sign_search([()], [1], 0, 10), (None, 1, True))
        result, _, exhausted = mp.sign_search([((0, 1), (1, 1), (2, 1))], [1], 3, 1)
        self.assertIsNone(result)
        self.assertFalse(exhausted)
        self.assertEqual(mp.search(47, 7, 1)["status"], "node-limit")

    def test_altered_pair_and_incomplete_colouring_rejected(self):
        d = 37
        signs = mp.family_signs(d)
        result = mp.checked_witness(2 * d + 3, d, signs)
        left = list(result["left"])
        left[left.index((0, 0))] = (2, 2 * d + 3)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])
        signs[(0, 0)] = -1
        with self.assertRaises(ValueError):
            mp.checked_witness(2 * d + 3, d, signs)
        del signs[(0, 0)]
        with self.assertRaises(ValueError):
            mp.checked_witness(2 * d + 3, d, signs)

    def test_invalid_parameters(self):
        for b, d in ((True, 1), (3, True), (1, 1), (4, 1), (7, 2), (7, 7), (7, 0)):
            with self.subTest(b=b, d=d), self.assertRaises(ValueError):
                mp.search(b, d)

    def test_cli_round_trip_and_proof(self):
        script = str(Path(mp.__file__))
        run = subprocess.run([sys.executable, script, "--family", "37"],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(run.stdout)["size"], 115)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)


if __name__ == "__main__":
    unittest.main()
