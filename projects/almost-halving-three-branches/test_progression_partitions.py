"""Independent finite checks of the full-partition classification."""
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import unittest

import progression_partitions as pp
from test_next_family import counts, distances


def exhaustive_full_partition(b, d):
    """Literal profiles of every permitted pair; fix centre on the left."""
    metric = distances((b + d, b, b - d))
    vertices = list(metric)
    if len(vertices) % 2:
        return False
    for rest in combinations(vertices[1:], len(vertices) // 2 - 1):
        left = [vertices[0], *rest]
        remaining = set(vertices) - set(left)
        right = [v for v in vertices if v in remaining]
        if counts(left, metric) == counts(right, metric):
            return True
    return False


class ProgressionPartitionsTest(unittest.TestCase):
    def test_exact_elimination_and_construction_identities(self):
        self.assertEqual(pp.root_elimination_residuals(), ({}, {}, {}))
        self.assertEqual(pp.multiple_construction_residuals(), ({}, {}))

    def test_all_full_partitions_through_middle_length_five(self):
        for b in range(2, 6):
            for d in range(1, b):
                with self.subTest(b=b, d=d):
                    self.assertEqual(pp.classify(b, d)["full_partition"],
                                     exhaustive_full_partition(b, d))

    def test_constructed_pairs_on_fresh_unequal_triples(self):
        for b, d in ((9, 3), (15, 5), (35, 7), (23, 3), (31, 4), (39, 5)):
            result = pp.classify(b, d, include_witness=True)
            metric = distances(result["lengths"])
            left, right = result["left"], result["right"]
            self.assertFalse(set(left) & set(right))
            self.assertEqual(set(left) | set(right), set(metric))
            self.assertEqual(len(left), len(right))
            self.assertEqual(len(left), result["maximum"])
            self.assertEqual(counts(left, metric), counts(right, metric))

    def test_residue_certificates_against_enumerated_vertex_counts(self):
        for b in range(3, 60, 2):
            for d in range(1, b):
                result = pp.classify(b, d)
                if result["full_partition"]:
                    continue
                counts_by_residue = Counter([0] + [depth % d
                    for length in result["lengths"] for depth in range(1, length + 1)])
                certificate = result["certificate"]
                if "residues" in certificate:
                    u, v = certificate["residues"]
                    self.assertEqual(u % certificate["gcd"], v % certificate["gcd"])
                    self.assertNotEqual(counts_by_residue[u] % 2, counts_by_residue[v] % 2)
                    self.assertEqual(certificate["vertex_counts"],
                                     [counts_by_residue[u], counts_by_residue[v]])
                else:
                    self.assertEqual(certificate["gcd"], 1)
                    self.assertEqual(counts_by_residue[0] % 2, 1)
                self.assertEqual(result["upper_bound"], result["target"])
                self.assertFalse(result["target_ruled_out"])

    def test_real_cli_witness_and_invalid_input(self):
        script = str(Path(pp.__file__))
        run = subprocess.run([sys.executable, script, "9", "3", "--witness"],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(run.stdout)["maximum"], 14)
        for b, d in ((0, 1), (3, 0), (3, 3), (True, 1), (3, 1.0)):
            with self.subTest(b=b, d=d), self.assertRaises(ValueError):
                pp.classify(b, d)


if __name__ == "__main__":
    unittest.main()
