"""Independent graph and exhaustive sign-word checks for unequal spacings."""
from itertools import product
import json
from math import gcd
from pathlib import Path
import subprocess
import sys
import unittest

import published_cases as pc
import unequal_spacing as us
from test_next_family import counts, distances


class UnequalSpacingTest(unittest.TestCase):
    def check_pair(self, result):
        metric = distances(result["lengths"])
        left, right = result["left"], result["right"]
        self.assertFalse(set(left) & set(right))
        self.assertEqual(len(left), len(right))
        self.assertEqual(counts(left, metric), counts(right, metric))
        self.assertTrue(result["homometric"])
        return set(metric) - set(left) - set(right)

    def test_free_laurent_identity(self):
        self.assertEqual(us.formal_identity(), {})

    def test_gcd_criterion_against_exhaustive_sign_words(self):
        for m in range(1, 8):
            for period in (1, 3, 5, 7):
                for c in (2, 4, 6, 8):
                    exists = False
                    for tail in product((-1, 1), repeat=period - 1):
                        word = (-1,) + tail
                        if all(word[(m-j) % period] == word[j]
                               and word[(c-j) % period]
                               == (-1 if ((c-j)//period) % 2 else 1) * word[j]
                               for j in range(period)):
                            exists = True
                            break
                    self.assertEqual(exists, (m+1) % gcd(period, c-m) == 0,
                                     (m, period, c))

    def test_full_partitions_with_independent_graph_counts(self):
        for lengths in ((8, 1, 4), (10, 7, 2), (14, 5, 8), (24, 9, 4), (5, 2, 2),
                        (8, 5, 20), (50, 33, 8), (70, 43, 12), (54, 31, 16)):
            with self.subTest(lengths=lengths):
                result = us.full_partition(*lengths)
                self.assertEqual(self.check_pair(result), set())
                self.assertEqual(2 * result["size"], 1 + sum(lengths))
                self.assertTrue(result["attains_bound"])

    def test_all_components_and_negative_index_reflections(self):
        for a, m, c in ((14, 5, 8), (24, 9, 4), (8, 5, 20)):
            word = us.reflection_word(a, m, c)
            period = a-m
            self.assertGreater(gcd(period, c-m), 1)
            self.assertTrue(all(s in (-1, 1) for s in word))
            for j in range(period):
                self.assertEqual(word[(m-j) % period], word[j])
                self.assertEqual(word[(c-j) % period],
                                 (-1 if ((c-j)//period) % 2 else 1) * word[j])
            def short_sign(p):
                return (1 if (p//period) % 2 else -1) * word[p % period]
            for j in range(-2*period, 2*period):
                self.assertEqual(short_sign(c-j), short_sign(j))
                self.assertEqual(short_sign(j+period), -short_sign(j))

    def test_prefixes_permutations_and_new_optimum(self):
        for lengths in ((50, 33, 9), (9, 50, 33), (51, 33, 9), (50, 34, 10)):
            with self.subTest(lengths=lengths):
                result = us.prefix_witness(lengths)
                self.assertEqual(self.check_pair(result), set(result["omitted"]))
                self.assertLessEqual(len(result["omitted"]), 3)
                self.assertTrue(result["meets_target"])
        result = us.prefix_witness((50, 33, 9))
        self.assertEqual(result["size"], 46)
        self.assertTrue(result["attains_bound"])
        self.assertEqual(result["omitted"], [(3, 9)])
        self.assertEqual(pc.witness((50, 33, 9))["size"], 43)

    def test_refusal_is_only_a_template_limitation(self):
        with self.assertRaisesRegex(ValueError, "no word in this reflection template"):
            us.full_partition(12, 3, 6)
        with self.assertRaisesRegex(ValueError, "not a bound on other pairs"):
            us.prefix_witness((1, 1, 1))
        self.assertTrue(pc.witness((1, 1, 1))["meets_target"])
        for b in (11, 221, 431):
            with self.assertRaisesRegex(ValueError, "not a bound on other pairs"):
                us.prefix_witness((b+50, b, b-6))
        # Another constructor succeeds on a member of the excluded family.
        result = pc.witness((271, 221, 215))
        self.assertTrue(result["meets_target"])
        self.check_pair(result)
        for lengths in ((True, 3, 2), (4, 2, 2), (3, 3, 2), (8, 3, 0), (8, 3, 3)):
            with self.assertRaises(ValueError):
                us.full_partition(*lengths)

    def test_fifty_thirty_three_nine_all_scale_formulas(self):
        for t in (1, 2, 5, 12):
            if t % 2:
                lengths = ((50*t-2, 9*t, 33*t-1) if t % 7 != 5
                           else (50*t, 9*t-2, 33*t-1))
            else:
                lengths = ((50*t-2, 33*t-1, 9*t) if t % 7 != 5
                           else (50*t, 33*t-1, 9*t-2))
            result = us.full_partition(*lengths)
            self.assertEqual(result["size"], 46*t-1)
            if t <= 5:
                self.check_pair(result)

    def test_cli_round_trip_mutation_and_proof(self):
        script = str(Path(us.__file__))
        run = subprocess.run([sys.executable, script, "50", "33", "9"],
                             text=True, capture_output=True, check=True)
        result = json.loads(run.stdout)
        checker = [sys.executable, str(Path(pc.__file__)), "--check", "-"]
        checked = subprocess.run(checker, input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        result["left"][result["left"].index([0, 0])] = [3, 9]
        rejected = subprocess.run(checker, input=json.dumps(result),
                                  text=True, capture_output=True)
        self.assertEqual(rejected.returncode, 1)
        self.assertFalse(json.loads(rejected.stdout)["homometric"])
        failed = subprocess.run([sys.executable, script, "1", "1", "1"],
                                text=True, capture_output=True)
        self.assertEqual(failed.returncode, 2)
        self.assertIn("not a bound", failed.stderr)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)


if __name__ == "__main__":
    unittest.main()
