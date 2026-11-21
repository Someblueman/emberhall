"""Independent graph distances check the general tail-transfer identity."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from edge_dependent import graph_counts
from paired_edge_five import check_pair
import interior_transfer as transfer
from unrestricted_odd_fields import INTERIOR_FAMILY, interior_pair


class InteriorTransferTests(unittest.TestCase):
    def test_positive_control_preserves_every_chosen_word(self):
        pair = {"lengths": (2, 2, 1), "left": [(1, 1), (1, 2)],
                "right": [(2, 1), (2, 2)]}
        for word in ((1,), (1, 1, -1), (-1, 1, -1, -1, 1)):
            self.assertFalse(transfer.transfer_residual(pair, (1, 2), word))
            extended = transfer.append_words(pair, (1, 2), (word, [-s for s in word]))
            self.assertTrue(check_pair(extended)["homometric"])
            self.assertEqual(graph_counts(extended["lengths"], extended["left"]),
                             graph_counts(extended["lengths"], extended["right"]))

    def test_residual_is_twice_the_literal_new_profile_difference(self):
        for k in (0, 1):
            pair = interior_pair(k)
            for arms in ((1, 2), (1, 3), (2, 3)):
                word = (1, -1, 1)
                extended = transfer.append_words(pair, arms, (word, [-s for s in word]))
                left = graph_counts(extended["lengths"], extended["left"])
                right = graph_counts(extended["lengths"], extended["right"])
                expected = Counter(left)
                expected.subtract(right)
                expected = {d: 2*c for d, c in expected.items() if c}
                self.assertEqual(transfer.transfer_residual(pair, arms, word), expected)
                self.assertEqual(len(extended["left"]), len(extended["right"]))
                self.assertFalse(set(map(tuple, extended["left"]))
                                 & set(map(tuple, extended["right"])))
                self.assertFalse(check_pair(extended)["homometric"])

    def test_high_distances_force_opposite_new_words(self):
        pair = interior_pair(0)
        a, b, _ = pair["lengths"]
        words = ((1, 1, -1), (-1, 1, -1))
        extended = transfer.append_words(pair, (1, 2), words)
        left = graph_counts(extended["lengths"], extended["left"])
        right = graph_counts(extended["lengths"], extended["right"])
        h = len(words[0])
        totals = [x+y for x, y in zip(*words)]
        # Above a+b+h only pairs crossing the two new tails can occur.
        high = [2*(left.get(a+b+h+j, 0)-right.get(a+b+h+j, 0))
                for j in range(1, h+1)]
        self.assertEqual(high, [sum(totals[j-1:]) for j in range(1, h+1)])
        recovered = [high[j]-(high[j+1] if j+1<h else 0) for j in range(h)]
        self.assertEqual(recovered, totals)
        self.assertFalse(check_pair(extended)["homometric"])
        self.assertTrue(transfer.prove_tip_obstruction()["long_middle_arbitrary_tail_words_excluded"])
        with self.assertRaises(ValueError):
            transfer.append_words(pair, (1, 2), ((1,), (1, -1)))

    def test_local_profiles_are_independent_of_parameter(self):
        expected = None
        for k in (0, 2, 5):
            pair = interior_pair(k)
            local = []
            for arm in (1, 2, 3):
                unsigned, signed = transfer.rooted_profiles(pair, arm)
                local.append(([unsigned.get(d, 0) for d in range(64)],
                              [signed.get(d, 0) for d in range(64)]))
                self.assertEqual(local[-1][0], [int(arm != 1)]+[1]*63)
            if expected is None:
                expected = local
            self.assertEqual(local, expected)

    def test_all_lengths_certificate_and_altered_tail(self):
        proof = transfer.prove_tip_obstruction()
        self.assertEqual(proof["proof"], "PASS")
        self.assertEqual([r.get("first_forbidden_position") for r in proof["tip_pairs"]],
                         [62, 6, None])
        self.assertEqual(proof["tip_pairs"][0]["short_lengths_excluded"], 61)
        self.assertFalse(proof["arbitrary_two_parameter_construction_excluded"])
        tails = [row[2] for row in INTERIOR_FAMILY]
        tails[2] = tails[2][:-1]+("-" if tails[2][-1] == "+" else "+")
        with self.assertRaises(ArithmeticError):
            transfer.prove_tip_obstruction(tails)
        with self.assertRaises(ValueError):
            transfer.prove_tip_obstruction(["+"]*3)

    def test_path_transfer_family_and_original_distances(self):
        self.assertFalse(any(transfer.path_family_identity().values()))
        self.assertTrue(transfer.path_family_identity(orientation=1)["transfer"])
        for r, m, c in ((1, 1, 1), (2, 3, 4), (2, 3, 1), (4, 2, 6),
                        (3, 2, 9), (5, 2, 2), (19, 4, 31),
                        (19, 6, 37), (19, 4, 141), (19, 4, 32)):
            pair = transfer.path_transfer_pair((m+1)*r+1, m*r, c)
            self.assertEqual(pair["lengths"], ((m+1)*r+1, m*r, c))
            holes = {(1, r), (1, (m+1)*r+1)}
            if (r+c) % 2:
                holes.add((3, c))
            self.assertEqual(set(pair["omitted"]), holes)
            self.assertEqual(len(pair["left"]), r*m+(r+c)//2)
            self.assertEqual(len(pair["left"]), len(pair["right"]))
            self.assertFalse(set(pair["left"]) & set(pair["right"]))
            self.assertEqual(graph_counts(pair["lengths"], pair["left"]),
                             graph_counts(pair["lengths"], pair["right"]))
            self.assertTrue(check_pair(pair)["meets_target"])
            changed = {**pair, "left": pair["left"][:-1]+[(1, r)]}
            if (r, m, c) == (19, 4, 31):
                self.assertFalse(check_pair(changed)["homometric"])
        for args in ((0, 1, 1), (1, 0, 1), (1, 1, 0), (True, 1, 1), (1, 2.5, 1), (95, 75, 31)):
            with self.assertRaises(ValueError):
                transfer.path_transfer_pair(*args)

    def test_short_multiple_extensions_without_long_divisibility(self):
        for lengths in ((120, 100, 57), (120, 100, 58), (24, 20, 9), (10, 7, 6),
                        (47, 40, 12), (23, 14, 16), (23, 14, 17), (11, 4, 1)):
            pair = transfer.path_transfer_pair(*lengths)
            self.assertEqual(graph_counts(lengths, pair["left"]),
                             graph_counts(lengths, pair["right"]))
            self.assertTrue(check_pair(pair)["meets_target"])

    def test_domain_against_independent_block_reflections(self):
        from itertools import product
        from math import gcd
        for r in range(1, 7):
            for b in range(1, 9):
                for c in range(1, 10):
                    retained = c-((r+c) % 2)
                    M, g = r+retained, gcd(r, b)
                    possible = False
                    for block in product((-1, 1), repeat=g):
                        path = [(-1 if (j//r) % 2 else 1)*block[j % g]
                                for j in range(M)]
                        if path == [-v for v in path[::-1]]:
                            possible = True
                            break
                    if possible:
                        pair = transfer.path_transfer_pair(b+r+1, b, c)
                        self.assertTrue(check_pair(pair)["homometric"], (r, b, c))
                    else:
                        with self.assertRaises(ValueError, msg=str((r, b, c))):
                            transfer.path_transfer_pair(b+r+1, b, c)

    def test_constructive_family_cli(self):
        from tempfile import TemporaryDirectory
        command = [sys.executable, str(Path(transfer.__file__))]
        proof = subprocess.run(command+["--prove-family"], capture_output=True,
                               text=True, check=True)
        self.assertFalse(json.loads(proof.stdout)["universal_milestone_solved"])
        with TemporaryDirectory() as directory:
            target = Path(directory)/"family.json"
            run = subprocess.run(command+["--family", "96", "76", "31", "--witness", str(target)],
                                 capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(run.stdout)["size"], 101)
            self.assertTrue(check_pair(json.loads(target.read_text()))["homometric"])

    def test_input_boundaries_and_cli(self):
        pair = interior_pair(0)
        for arms, word in (((1, 1), (1,)), ((0, 3), (1,)), ((1, 2), ()),
                           ((1, 2), (True,)), ((1, 2), (0,))):
            with self.assertRaises(ValueError):
                transfer.transfer_residual(pair, arms, word)
        broken = deepcopy(pair)
        broken["left"].remove((0, 0))
        broken["left"].append((1, 19))
        with self.assertRaises(ValueError):
            transfer.transfer_residual(broken, (1, 2), (1,))
        command = [sys.executable, str(Path(transfer.__file__))]
        proof = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(proof.stdout)["proof"], "PASS")
        example = subprocess.run(command+["--example", "--k", "1", "--word=+-"],
                                 capture_output=True, text=True, check=True)
        self.assertFalse(json.loads(example.stdout)["homometric"])
        bad = subprocess.run(command+["--example", "--word=x"],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
