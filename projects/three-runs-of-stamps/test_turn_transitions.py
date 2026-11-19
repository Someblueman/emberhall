"""Independent matching-stack comparisons for the two transition rows."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from delayed_escape import adjacent, first_internal, nest
from reconstruction import extend, legal
from turn_transitions import (
    KINDS, basis, completion_records, expected_weight, open_frontiers,
    recover, transition_prefix, verify,
)
from weighted_open import exterior


def children(prefix, word):
    n = len(prefix)
    for i in range(n + 1):
        child = prefix[:i] + (n,) + prefix[i:]
        if legal(child, word):
            yield child


def stopped(mountain, a, r):
    frontier = {mountain}
    for j in range(1, r):
        frontier = {
            c for p in frontier for c in children(p, "M" * a + "V" * j)
            if j == 1 or c != adjacent(p, "V")
        }
    return {adjacent(p, "V") for p in frontier}


class TransitionTests(unittest.TestCase):
    def test_prefix_census(self):
        for r in range(5, 12):
            for offset in (3, 4):
                for extra in (1, 2, 5):
                    a = r + extra
                    mountain, *_ = basis(a, r, offset)
                    self.assertEqual(first_internal(mountain), a - r + offset)
                    self.assertEqual(stopped(mountain, a, r),
                                     {transition_prefix(a, r, offset, k) for k in KINDS})

    def test_every_open_frontier_against_full_matching(self):
        for r in range(5, 14):
            for offset in (3, 4):
                for extra in (1, 2, 4):
                    a = r + extra
                    for kind in KINDS:
                        previous = {transition_prefix(a, r, offset, kind)}
                        for j, frontier in enumerate(open_frontiers(a, r, offset, kind), 1):
                            direct = {
                                c for p in previous
                                for c in children(p, "M" * a + "V" * r + "M" * j)
                                if j == 1 or c != adjacent(p, "M")
                            }
                            self.assertEqual(set(frontier.values()), direct,
                                             (a, r, offset, kind, j))
                            self.assertEqual(len(frontier), len(direct))
                            previous = direct

    def test_complete_sets_and_recovered_parameters(self):
        for r in range(5, 13):
            for offset in (3, 4):
                for a in (r + 1, r + 2, r + 6):
                    for kind in KINDS:
                        self.assertEqual(verify(a, r, offset, kind),
                                         expected_weight(r, offset, kind))

    def test_long_constructed_cases(self):
        for offset in (3, 4):
            for kind in KINDS:
                records = list(completion_records(57, 40, offset, kind))
                self.assertEqual(len(records), expected_weight(40, offset, kind))
                for parameter, stack in records:
                    self.assertEqual(recover(stack, 57, 40, offset, kind), parameter)

    def test_small_stop_is_not_a_blind_extension(self):
        for r, offset, expected in ((3, 3, [5, 6]), (4, 3, [9, 9]), (4, 4, [8, 8])):
            a = r + 1
            turn = a - r + offset
            mountain = nest(exterior(turn - 1), a - turn + 1, "M")
            weights = sorted(sum(1 for _ in extend(p, "M" * a + "V" * r + "M" * r))
                             for p in stopped(mountain, a, r))
            self.assertEqual(weights, expected)
        self.assertNotEqual([8, 8], [4 * 4 - 9, 4 * 4 - 8])

    def test_domain_and_inverse_failures(self):
        for args in ((5, 5, 3), (8, 4, 4), (9, 7, 5)):
            with self.assertRaises(ValueError):
                basis(*args)
        with self.assertRaises(ValueError):
            transition_prefix(9, 8, 3, "unknown")
        stack = next(completion_records(9, 8, 3, "core"))[1]
        with self.assertRaises(ValueError):
            recover(stack, 9, 8, 3, "wrap")
        with self.assertRaises(ValueError):
            recover(stack[:-1], 9, 8, 3, "core")

    def test_cli(self):
        script = str(Path(__file__).with_name("turn_transitions.py"))
        for offset, line in ((3, "core: 25 stacks; theorem 25"),
                             (4, "core: 23 stacks; theorem 23")):
            result = subprocess.run([sys.executable, script, "--offset", str(offset), "--verify"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(line, result.stdout)
        result = subprocess.run([sys.executable, script, "--stop", "4"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
