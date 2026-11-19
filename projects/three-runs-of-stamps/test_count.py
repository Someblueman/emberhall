"""Run with: python3 -m unittest discover -s projects/three-runs-of-stamps -v."""
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from count import (crosses, extensions, family_prefix, first_inward, insertions,
                   nested_family, nested_prefix, stacks, violations)


def direct_legal(order, assignment):
    """Independent permutation oracle: directed pairs and interval membership."""
    at = {label: rank for rank, label in enumerate(order)}
    for i, symbol in enumerate(assignment):
        left, right = (i + 1, i) if (symbol == "M") == (i % 2 == 0) else (i, i + 1)
        if at[left] >= at[right]:
            return False
    for i in range(len(assignment)):
        a, b = sorted((at[i], at[i + 1]))
        for j in range(i + 2, len(assignment), 2):
            if (a < at[j] < b) != (a < at[j + 1] < b):
                return False
    return True


class CountingTests(unittest.TestCase):
    def test_all_assignments_through_six_faces(self):
        for n in range(1, 7):
            permutations = list(itertools.permutations(range(n)))
            for bits in itertools.product("MV", repeat=n - 1):
                assignment = "".join(bits)
                expected = {p for p in permutations if direct_legal(p, assignment)}
                actual = list(stacks(assignment))
                self.assertEqual(len(actual), len(set(actual)))
                self.assertEqual(set(actual), expected, assignment)

    def test_ten_stacks_against_full_seven_face_universe(self):
        expected = {
            (5, 6, 4, 1, 2, 3, 0), (5, 4, 1, 2, 3, 6, 0),
            (5, 4, 1, 2, 3, 0, 6), (1, 2, 5, 6, 4, 3, 0),
            (1, 2, 5, 4, 3, 6, 0), (1, 2, 5, 4, 3, 0, 6),
            (5, 6, 4, 1, 0, 2, 3), (5, 4, 1, 0, 2, 3, 6),
            (1, 0, 2, 5, 6, 4, 3), (1, 0, 2, 5, 4, 3, 6),
        }
        self.assertEqual(set(stacks("MMVVMM")), expected)
        self.assertEqual({p for p in itertools.permutations(range(7))
                          if direct_legal(p, "MMVVMM")}, expected)

    def test_proven_controls(self):
        for k in range(2, 9):
            self.assertEqual(len(list(stacks("M" * k))), k)
            self.assertEqual(len(list(stacks("M" * k + "V" * k))), 2*k*k - 3*k + 2)
        self.assertEqual(len(list(stacks("MV" * 6))), 1)

    def test_family_prefix_and_every_shorter_third_run(self):
        for k in range(2, 13):
            prefix = family_prefix(k)
            self.assertEqual(violations(prefix, "M" * k + "V" * k), [])
            for length in range(1, k + 1):
                found = list(extensions(prefix, "M" * length))
                self.assertEqual(len(found), length, (k, length))
                for order in found:
                    self.assertTrue(direct_legal(order, "M"*k + "V"*k + "M"*length))

    def test_growing_nested_family_and_its_exception(self):
        for k in range(2, 11):
            total = 0
            prefixes = list(nested_family(k))
            self.assertEqual(len(prefixes), k)
            self.assertEqual({turn for turn, _ in prefixes}, {None, *range(2, k + 1)})
            for turn, prefix in prefixes:
                self.assertFalse(violations(prefix, "M"*k + "V"*k))
                found = list(extensions(prefix, "M"*k))
                self.assertEqual(len(found), k + (turn == k), (k, turn))
                total += len(found)
            self.assertEqual(total, k*k + 1)
        # A regression against claiming every tightly nested prefix gives k.
        self.assertEqual(first_inward((1, 0, 3, 2)), 3)
        self.assertEqual(nested_prefix((1, 0, 3, 2), 3), (1, 0, 4, 6, 5, 3, 2))

    def test_crossing_and_orientation_boundaries(self):
        self.assertTrue(crosses(0, 2, 1, 3))
        self.assertTrue(crosses(2, 0, 3, 1))
        self.assertFalse(crosses(0, 3, 1, 2))  # nested
        self.assertFalse(crosses(0, 1, 2, 3))  # disjoint
        self.assertEqual(list(stacks("M")), [(1, 0)])
        self.assertEqual(list(stacks("V")), [(0, 1)])
        for p in stacks("MMVVMM"):
            self.assertTrue(violations(p[::-1], "MMVVMM"))
            self.assertFalse(violations(p[::-1], "VVMMVV"))
        crossing = (1, 0, 2, 5, 4, 6, 3)
        self.assertEqual(violations(crossing, "MMVVMM"),
                         ["bottom crossing: 3-4 with 5-6"])

    def test_invalid_input(self):
        for order in ((), (0, 0), (1, 2)):
            with self.assertRaises(ValueError):
                violations(order, "M")
        with self.assertRaises(ValueError):
            list(stacks("MX"))
        with self.assertRaises(ValueError):
            list(insertions((0,), ""))
        with self.assertRaises(ValueError):
            violations((0, 1), "")

    def test_native_command(self):
        command = [sys.executable, str(Path(__file__).with_name("count.py"))]
        result = subprocess.run(command + ["--list"], capture_output=True, text=True, check=True)
        self.assertIn("10: 1 0 2 5 4 3 6", result.stdout)
        self.assertIn("MMVVMM: 10 legal labeled stacks", result.stdout)
        result = subprocess.run(command + ["--assignment", "MX"], capture_output=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
