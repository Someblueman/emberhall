"""Definition-level tests of the turn-boundary construction and inverse."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from delayed_escape import adjacent, first_internal, nest
from reconstruction import extend, legal
from weighted_open import exterior
from turn_boundary import (
    KINDS, boundary_prefix, completion_records, expected_weight, mountain_core,
    open_frontiers, recover, verify, compress_core, expand_core,
)


def children(prefix, word):
    label = len(prefix)
    for gap in range(label + 1):
        child = prefix[:gap] + (label,) + prefix[gap:]
        if legal(child, word):
            yield child


def open_valleys(mountain, a, r):
    frontier = {mountain}
    for step in range(1, r):
        frontier = {
            child for p in frontier for child in children(p, "M" * a + "V" * step)
            if step == 1 or child != adjacent(p, "V")
        }
    return {adjacent(p, "V") for p in frontier}


class TurnBoundaryTests(unittest.TestCase):
    def test_prefixes_are_the_complete_stopped_bucket(self):
        for r in range(3, 11):
            for extra in range(1, 7):
                a = r + extra
                mountain, *_ = mountain_core(a, r)
                self.assertEqual(first_internal(mountain), a - r + 2)
                self.assertEqual(open_valleys(mountain, a, r),
                                 {boundary_prefix(a, r, k) for k in KINDS})

    def test_each_named_gap_table_is_exhaustive(self):
        # Check every frontier, not only a final numerical identity.
        for r in range(3, 14):
            for extra in (1, 2, 5):
                a = r + extra
                for kind in KINDS:
                    previous = {boundary_prefix(a, r, kind)}
                    for step, frontier in enumerate(open_frontiers(a, r, kind), 1):
                        direct = {
                            child for p in previous
                            for child in children(p, "M" * a + "V" * r + "M" * step)
                            if step == 1 or child != adjacent(p, "M")
                        }
                        self.assertEqual(set(frontier.values()), direct, (a, r, kind, step))
                        self.assertEqual(len(frontier), len(direct))
                        previous = direct

    def test_complete_sets_and_inverse(self):
        for r in range(3, 12):
            for extra in (1, 2, 4):
                for kind in KINDS:
                    self.assertEqual(verify(r + extra, r, kind), expected_weight(r, kind))

    def test_large_constructive_inverses(self):
        for a, r in ((32, 30), (67, 50)):
            for kind in KINDS:
                records = list(completion_records(a, r, kind))
                self.assertEqual(len(records), expected_weight(r, kind))
                for parameter, stack in records:
                    self.assertEqual(recover(stack, a, r, kind), parameter)

    def test_core_maps_preserve_complete_sets(self):
        for r in range(3, 9):
            for extra in (1, 2, 3, 6):
                a = r + extra
                for kind in KINDS:
                    large = {s for _, s in completion_records(a, r, kind)}
                    small = {s for _, s in completion_records(r + 1, r, kind)}
                    self.assertEqual({compress_core(s, a, r) for s in large}, small)
                    self.assertEqual({expand_core(s, a, r) for s in small}, large)
                    for s in large:
                        self.assertEqual(expand_core(compress_core(s, a, r), a, r), s)

    def test_small_stops_have_their_actual_frontiers(self):
        expected = {
            3: {"inside": [3, 2, 2], "outside": [2, 2, 2]},
            4: {"inside": [3, 3, 2, 3], "outside": [2, 3, 2, 3]},
            5: {"inside": [3, 3, 3, 3, 3], "outside": [2, 3, 3, 3, 3]},
        }
        for r, kinds in expected.items():
            for kind, values in kinds.items():
                self.assertEqual([len(f) for f in open_frontiers(r + 1, r, kind)], values)

    def test_one_shallower_turn_is_not_this_family(self):
        for r in (5, 6, 7):
            a = r + 1
            # Build the next shallower mountain directly: first inward at 4.
            mountain = nest(exterior(3), a - 3, "M")
            prefixes = open_valleys(mountain, a, r)
            weights = sorted(sum(1 for _ in extend(p, "M" * a + "V" * r + "M" * r))
                             for p in prefixes)
            self.assertEqual(weights, [4 * r - 7, 4 * r - 7])
            self.assertNotEqual(weights, sorted(expected_weight(r, k) for k in KINDS))

    def test_invalid_domain_and_inverse(self):
        for a, r in ((4, 4), (4, 2), (-1, 5)):
            with self.assertRaises(ValueError):
                mountain_core(a, r)
        with self.assertRaises(ValueError):
            boundary_prefix(8, 7, "unknown")
        stack = next(completion_records(8, 7, "inside"))[1]
        with self.assertRaises(ValueError):
            recover(stack, 8, 7, "outside")
        with self.assertRaises(ValueError):
            recover(stack[:-1], 8, 7, "inside")

    def test_native_command(self):
        script = str(Path(__file__).with_name("turn_boundary.py"))
        result = subprocess.run([sys.executable, script, "--verify"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("inside: 23 stacks; theorem 23", result.stdout)
        self.assertIn("outside: 22 stacks; theorem 22", result.stdout)
        bad = subprocess.run([sys.executable, script, "--stop", "2"], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertIn("require r >= 3", bad.stderr)


if __name__ == "__main__":
    unittest.main()
