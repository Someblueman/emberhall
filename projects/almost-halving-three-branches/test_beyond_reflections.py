"""Original-tree counters and bounded exhaustive controls for the new proof."""
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path
import subprocess
import sys
import unittest

import beyond_reflections as br
from unequal_spacing import full_partition
from test_next_family import counts, distances


class BeyondReflectionsTest(unittest.TestCase):
    def test_exact_elimination(self):
        self.assertFalse(any(br.root_elimination_residuals()))

    def test_obstructions_against_every_small_partition(self):
        checked = 0
        candidates = [lengths for lengths in combinations_with_replacement(range(1, 10), 3)
                      if (1 + sum(lengths)) <= 12]
        candidates.append((3, 3, 9))  # Nontrivial gcd branch, with 16 vertices.
        for lengths in candidates:
            order = 1 + sum(lengths)
            if order % 2:
                continue
            certificate = br.full_partition_obstruction(lengths)
            if not certificate["full_partition_ruled_out"]:
                continue
            metric = distances(lengths)
            vertices = list(metric)
            # Complementary labellings have identical validity: fix the centre.
            for chosen in combinations(vertices[1:], order // 2 - 1):
                left = {vertices[0], *chosen}
                right = set(vertices) - left
                self.assertNotEqual(counts(sorted(left), metric), counts(sorted(right), metric),
                                    (lengths, left))
            checked += 1
        self.assertGreater(checked, 0)

    def test_condition_does_not_assert_existence(self):
        for lengths in ((90, 70, 15), (91, 70, 14), (12, 9, 6)):
            certificate = br.full_partition_obstruction(lengths)
            self.assertFalse(certificate["full_partition_ruled_out"])
            self.assertFalse(certificate["existence_certified"])
        self.assertTrue(br.full_partition_obstruction((91, 71, 15))[
            "full_partition_ruled_out"])

    def test_family_certificates_at_fresh_and_large_parameters(self):
        for t in (0, 1, 2, 7, 19, 10**30):
            result = br.family_certificate(t)
            self.assertEqual(result["upper_bound_over_all_pairs"], 88 + 7980*t)
            self.assertEqual(result["prefixes_not_ruled_out"],
                             [(0, 1, 1), (1, 1, 0)])
            self.assertEqual(len(result["prefixes"]), 7)
            # Compute residue population parity directly from each arm length.
            for row in result["prefixes"]:
                if not row["full_partition_ruled_out"]:
                    continue
                g = row["modulus"]
                populations = [int(j == 0) + sum(
                    (n-j)//g + 1 if 1 <= j <= n else n//g if j == 0 else 0
                    for n in row["lengths"]) for j in range(g)]
                self.assertEqual(row["residue_gcd"], 1)
                self.assertTrue(any(n % 2 for n in populations))

    def test_seed_with_independent_original_tree_counter(self):
        result = br.seed_witness()
        metric = distances(result["lengths"])
        left, right = set(result["left"]), set(result["right"])
        self.assertFalse(left & right)
        self.assertEqual(len(left), 88)
        self.assertEqual(len(right), 88)
        self.assertEqual(counts(sorted(left), metric), counts(sorted(right), metric))
        self.assertEqual(set(metric) - left - right, {(1, 91), (2, 71)})

    def test_nearest_subdivision_has_exact_distance_two_defect(self):
        for lengths in ((13, 10, 2), (8, 5, 2), (14, 5, 8)):
            base = full_partition(*lengths)
            positive = set(base["left"])
            for scale in (3, 5, 7):
                expanded = tuple(scale*n for n in lengths)
                metric = distances(expanded)
                left, right = [(0, 0)], []
                for arm, length in enumerate(expanded, 1):
                    for depth in range(1, length+1):
                        nearest = (depth + scale//2)//scale
                        old = (arm, nearest) if nearest else (0, 0)
                        (left if old in positive else right).append((arm, depth))
                lp, rp = counts(left, metric), counts(right, metric)
                self.assertEqual(len(left), len(right))
                self.assertEqual(lp[1], rp[1])
                self.assertEqual(lp[2]-rp[2], 1)

    def test_real_cli_and_altered_witness(self):
        script = str(Path(br.__file__))
        valid = subprocess.run([sys.executable, script, "0", "--witness"],
                               capture_output=True, text=True, check=True)
        pair = json.loads(valid.stdout)
        pair["left"][0] = [1, 91]
        checker = str(Path(script).with_name("published_cases.py"))
        bad = subprocess.run([sys.executable, checker, "--check", "-"],
                             input=json.dumps(pair), capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertFalse(json.loads(bad.stdout)["homometric"])
        unavailable = subprocess.run([sys.executable, script, "1", "--witness"],
                                     capture_output=True, text=True)
        self.assertEqual(unavailable.returncode, 2)
        self.assertIn("only for t=0", unavailable.stderr)

    def test_reject_invalid_domain(self):
        for t in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                br.family_certificate(t)


if __name__ == "__main__":
    unittest.main()
