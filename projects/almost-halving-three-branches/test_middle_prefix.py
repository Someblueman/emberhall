"""Independent graph checks of the all-parameter middle-tip construction."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import middle_prefix as mp
import published_cases as pc
from test_next_family import counts, distances


class MiddlePrefixTest(unittest.TestCase):
    def check_witness(self, b, d):
        result = mp.construct(b, d)
        metric = distances(result["lengths"])
        left, right = result["left"], result["right"]
        self.assertFalse(set(left) & set(right))
        self.assertEqual(len(left), len(right))
        self.assertEqual(len(left), (3 * b - 1) // 2)
        self.assertEqual(counts(left, metric), counts(right, metric))
        self.assertEqual(set(metric) - set(left) - set(right), {(2, b - 1), (2, b)})
        return result

    def test_universal_formal_identity(self):
        self.assertEqual(mp.formal_identity(), {})

    def test_small_odd_parameters_by_independent_graph_distances(self):
        for b in range(3, 32, 2):
            for d in range(1, b, 2):
                with self.subTest(b=b, d=d):
                    self.check_witness(b, d)

    def test_fresh_large_and_short_arm_boundaries(self):
        for b, d in ((47, 7), (57, 9), (87, 13), (87, 33), (121, 51),
                     (151, 99), (101, 99), (103, 1)):
            with self.subTest(b=b, d=d):
                self.check_witness(b, d)

    def test_reflections_and_negative_index_extension(self):
        for b, d in ((3, 1), (5, 3), (47, 7), (87, 33), (101, 99)):
            word = mp.reflection_word(b, d)
            period, m, c = d + 2, b - 2, b - d
            self.assertEqual(word[0], -1)
            self.assertTrue(all(type(s) is int and s in (-1, 1) for s in word))
            for j in range(period):
                self.assertEqual(word[(m - j) % period], word[j])
                self.assertEqual(word[(c - j) % period],
                                 mp.parity_sign((c - j) // period) * word[j])
            for p in range(-2 * period, c + 2 * period):
                self.assertEqual(mp.short_sign(c - p, period, word),
                                 mp.short_sign(p, period, word))
                self.assertEqual(mp.short_sign(p + period, period, word),
                                 -mp.short_sign(p, period, word))

    def test_altered_pair_and_incomplete_colouring_rejected(self):
        result = mp.construct(87, 33)
        left = list(result["left"])
        left[left.index((0, 0))] = (2, 87)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])
        signs = {v: 1 for v in result["left"]} | {v: -1 for v in result["right"]}
        signs[(0, 0)] = -1
        with self.assertRaises(ValueError):
            mp.checked_witness(87, 33, signs)
        del signs[(0, 0)]
        with self.assertRaises(ValueError):
            mp.checked_witness(87, 33, signs)

    def test_invalid_parameters(self):
        for b, d in ((True, 1), (3, True), (1, 1), (4, 1), (7, 2),
                     (7, 7), (7, 0), (7, -1), (7.0, 3)):
            with self.subTest(b=b, d=d), self.assertRaises(ValueError):
                mp.construct(b, d)

    def test_cli_round_trip_and_proof(self):
        script = str(Path(mp.__file__))
        run = subprocess.run([sys.executable, script, "121", "51"],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(run.stdout)["size"], 181)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)


if __name__ == "__main__":
    unittest.main()
