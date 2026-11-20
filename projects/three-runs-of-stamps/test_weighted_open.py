"""Check the outer-core bijection and independently enumerate its gap table."""
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from reconstruction import extend, legal
from weighted_open import (check_reduction, children, compress_core, expand_core,
                           exterior, inner_constructed, inner_open_frontiers, inner_prefix,
                           outer_constructed, outer_open_frontiers,
                           outer_prefix, region_boundary, stopped_prefixes, weights)


def actual_frontiers(stop):
    frontier = [outer_prefix(2, stop)]
    for depth in range(1, stop + 1):
        new = []
        for prefix in frontier:
            for child in children(prefix, "MM" + "V" * stop + "M" * depth):
                last = len(child) - 1
                if depth == 1 or abs(child.index(last) - child.index(last - 1)) != 1:
                    new.append(child)
        frontier = new
        yield set(frontier)


class WeightedOpenTests(unittest.TestCase):
    def test_core_maps_on_unequal_lengths_and_both_parities(self):
        cases = 0
        for a, stop in itertools.product(range(2, 10), range(2, 10)):
            for suffix in range(stop + 4):
                large, small = check_reduction(a, stop, suffix)
                self.assertEqual(large, small)
                cases += 1
        self.assertEqual(cases, 608)

    def test_core_maps_on_explicit_long_example(self):
        prefix = outer_prefix(8, 6)
        for order in extend(prefix, "M" * 8 + "V" * 6 + "M" * 6):
            small = compress_core(order, 8)
            self.assertTrue(legal(small, "MM" + "V" * 6 + "M" * 6))
            self.assertEqual(expand_core(small, 8), order)
        self.assertEqual(exterior(3), (3, 1, 0, 2))

    def test_symbolic_table_equals_every_open_prefix(self):
        for stop in range(7, 26):
            for depth, (actual, symbolic) in enumerate(zip(
                    actual_frontiers(stop), outer_open_frontiers(stop)), 1):
                self.assertEqual(set(symbolic.values()), actual, (stop, depth))
                if depth <= 3:
                    expected = 2
                elif depth < stop - 3:
                    expected = 3
                elif depth == stop - 3:
                    expected = 4
                elif depth == stop - 2:
                    expected = 3
                else:
                    expected = 2
                self.assertEqual(len(actual), expected)

    def test_constructive_inverse_covers_full_completion_set(self):
        for stop in range(7, 26):
            actual = set(extend(outer_prefix(2, stop), "MM" + "V" * stop + "M" * stop))
            constructive = outer_constructed(stop)
            self.assertEqual(constructive, actual, stop)
            self.assertEqual(len(actual), 3*stop - 4)

    def test_small_boundaries_have_separate_exact_certificates(self):
        for stop, vector in [(2, [1, 1]), (3, [2, 1, 1]), (4, [3, 2, 1, 2]),
                             (5, [2, 3, 2, 2, 2]), (6, [2, 2, 3, 3, 2, 2])]:
            frontier_sizes = [len(s) for s in actual_frontiers(stop)]
            self.assertEqual(frontier_sizes, vector)
            total = sum(1 for _ in extend(outer_prefix(2, stop), "MM" + "V"*stop + "M"*stop))
            self.assertEqual(total, sum(vector))
        # Extending 3r-4 down to r=3 would be a false statement.
        self.assertEqual(sum(1 for _ in extend(outer_prefix(2, 3), "MMVVVMMM")), 4)

    def test_two_exterior_weights_are_not_one_identical_family(self):
        self.assertEqual(sorted(n for _, n in weights(8, 5)), [8, 11])
        self.assertEqual(check_reduction(8, 5, 5), (11, 11))

    def test_inner_table_on_finite_unequal_cases(self):
        for stop in range(4, 14):
            for a in (stop + 1, stop + 2, stop + 5):
                prefix = inner_prefix(a, stop)
                actual = set(extend(prefix, "M"*a + "V"*stop + "M"*stop))
                self.assertEqual(inner_constructed(a, stop), actual)
                self.assertEqual(len(actual), 2*stop - 2)
                self.assertEqual([len(row) for row in inner_open_frontiers(a, stop)],
                                 [2]*(stop-2) + [1, 1])
        with self.assertRaises(ValueError):
            inner_prefix(5, 5)

    def test_inner_parent_and_child_indices(self):
        for stop in range(4, 15):
            for a in (stop + 1, stop + 2, stop + 5):
                prefix = inner_prefix(a, stop)
                self.assertEqual(region_boundary(prefix), (a+stop-2, (a-stop+2,)))
                states = list(inner_open_frontiers(a, stop))
                self.assertEqual(set(stopped_prefixes(a, stop)),
                                 {prefix, outer_prefix(a, stop)})
                for step in range(2, stop + 1):
                    for kind, order in states[step-2].items():
                        if step <= stop-2:
                            pair = ((a-stop+step+1, (a+stop-step+1,)) if kind == "first"
                                    else (a+stop-step-1, (a-stop+step+1,)))
                        elif kind == "first":
                            pair = (None, (a+stop-step+1,))
                        else:
                            pair = (a, ())
                        self.assertEqual(region_boundary(order), pair, (a, stop, step, kind))

    def test_invalid_maps_and_domain(self):
        for args in [(1, 5, 5), (5, 1, 5), (5, 5, -1)]:
            with self.assertRaises(ValueError):
                check_reduction(*args)
        with self.assertRaises(ValueError):
            list(outer_open_frontiers(6))
        with self.assertRaises(ValueError):
            compress_core((1, 4, 0, 2, 3), 4)
        with self.assertRaises(ValueError):
            expand_core((0, 0, 2), 4)

    def test_native_commands(self):
        path = str(Path(__file__).with_name("weighted_open.py"))
        result = subprocess.run([sys.executable, path, "--outer", "--stop", "8"],
                                capture_output=True, text=True, check=True)
        self.assertIn("8-mountain core: 20; two-mountain core: 20", result.stdout)
        result = subprocess.run([sys.executable, path, "--table", "--stop", "12"],
                                capture_output=True, text=True, check=True)
        self.assertIn("32 stacks", result.stdout)
        for flags in (["--inner", "--outer"], ["--table", "--suffix", "2"]):
            bad = subprocess.run([sys.executable, path, *flags], capture_output=True)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
