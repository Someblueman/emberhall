"""Independent reconstruction, using the matching-stack legality predicate."""
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from reconstruction import (adjacent_valley, brute, census, collar_check, extend,
                            first_valley_census, inward_step, legal, nested_prefix)


class ReconstructionTests(unittest.TestCase):
    def test_oriented_single_creases(self):
        self.assertTrue(legal((1, 0), "M"))
        self.assertFalse(legal((0, 1), "M"))
        self.assertTrue(legal((0, 1), "V"))
        self.assertFalse(legal((1, 0), "V"))

    def test_matching_requires_no_crossings(self):
        # Every direction is right, but two bottom arcs interleave.
        self.assertFalse(legal((1, 0, 2, 5, 4, 6, 3), "MMVVMM"))
        self.assertTrue(legal((1, 0, 2, 5, 4, 3, 6), "MMVVMM"))
        for order in [(), (0, 0), (2, 1), (0, 1, 2)]:
            self.assertFalse(legal(order, "M"))
        self.assertFalse(legal((0, 1), "X"))

    def test_all_small_assignments_against_whole_permutations(self):
        for n in range(1, 7):
            for symbols in itertools.product("MV", repeat=n - 1):
                word = "".join(symbols)
                generated = list(extend((0,), word))
                self.assertEqual(len(generated), len(set(generated)))
                self.assertEqual(set(generated), brute(word), word)

    def test_complete_seven_face_control_and_family_partition(self):
        full = brute("MMVVMM")
        self.assertEqual(len(full), 10)
        self.assertEqual(set(extend((0,), "MMVVMM")), full)
        seen = set()
        for mountain in extend((0,), "MM"):
            prefix = nested_prefix(mountain, 2)
            completions = set(extend(prefix, "MMVVMM"))
            self.assertFalse(seen & completions)
            seen |= completions
        self.assertEqual(len(seen), 5)
        self.assertTrue(seen < full)

    def test_collar_bijection_across_all_short_prefix_types(self):
        cases = 0
        for length in range(1, 6):
            for symbols in itertools.product("MV", repeat=length - 1):
                word = "".join(symbols) + "V"
                for prefix in extend((0,), word):
                    if abs(prefix.index(length) - prefix.index(length - 1)) == 1:
                        for remaining in (1, 2, 3):
                            small, large = collar_check(prefix, word, remaining)
                            self.assertEqual(large, small + 1)
                            cases += 1
        self.assertEqual(cases, 225)

    def test_one_valley_base_and_unique_exception(self):
        for a in range(2, 17):
            rows = census(a, 1)
            self.assertEqual({t for t, _ in rows}, {None, *range(2, a + 1)})
            self.assertEqual(rows, [(None, 1)] + [(t, 1 + (t == a))
                                                    for t in range(2, a + 1)])

    def test_unequal_length_family_and_parity(self):
        for a, b in itertools.product(range(2, 11), range(1, 9)):
            with self.subTest(a=a, b=b):
                rows = census(a, b)
                self.assertEqual(sum(n for _, n in rows), a*b + 1)
                self.assertTrue(all(n == b + (t == a) for t, n in rows))
        self.assertEqual(census(4, 4), [(None, 4), (2, 4), (3, 4), (4, 5)])

    def test_skipped_first_valley_is_unique_and_has_four_base_completions(self):
        for a in range(2, 15):
            rows = first_valley_census(a, 2)
            skips = [row for row in rows if row[1]]
            self.assertEqual(len(skips), int(a >= 3))
            if skips:
                self.assertEqual(skips[0][2], 4)
            self.assertEqual(len(rows), a + int(a >= 3))

    def test_enlarged_family_unequal_lengths(self):
        for a, b in itertools.product(range(2, 9), range(2, 8)):
            rows = first_valley_census(a, b)
            prefixes = [row[0] for row in rows]
            self.assertEqual(len(prefixes), len(set(prefixes)))
            expected = 2*b + 1 if a == 2 else (a+1)*b + 3
            self.assertEqual(sum(row[2] for row in rows), expected)
            self.assertTrue(all(count == b + 2 for _, skip, count in rows if skip))

    def test_explicit_exception_and_reversal(self):
        mountain = (1, 0, 3, 2)
        self.assertEqual(inward_step(mountain), 3)
        self.assertEqual(nested_prefix(mountain, 3), (1, 0, 4, 6, 5, 3, 2))
        self.assertEqual(len(list(extend(nested_prefix(mountain, 3), "MMMVVVMMM"))), 4)
        for p in extend((0,), "MMVVMM"):
            self.assertTrue(legal(p[::-1], "VVMMVV"))
            self.assertFalse(legal(p[::-1], "MMVVMM"))

    def test_contract_errors(self):
        with self.assertRaises(ValueError):
            list(extend((0, 1), "M"))
        for a, b in [(1, 2), (2, 0)]:
            with self.assertRaises(ValueError):
                census(a, b)
        with self.assertRaises(ValueError):
            collar_check((0, 1), "V", 0)
        with self.assertRaises(ValueError):
            collar_check((1, 0, 2), "MM", 2)
        with self.assertRaises(ValueError):
            nested_prefix((0, 1), 1)

    def test_native_command(self):
        program = Path(__file__).with_name("reconstruction.py")
        result = subprocess.run([sys.executable, str(program), "--mountains", "5",
                                 "--valleys", "2"], text=True, capture_output=True, check=True)
        self.assertIn("nested family total: 11", result.stdout)
        self.assertIn("full three-run cubic is not proved", result.stdout)
        bad = subprocess.run([sys.executable, str(program), "--valleys", "0"],
                             text=True, capture_output=True)
        self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
