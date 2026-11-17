"""Focused tests for the exact window and periodic search.

Run: python3 -m pytest projects/five-marks/test_counterexample.py -q
  or: python3 -m unittest projects.five-marks.test_counterexample
Finite computation is supporting evidence, never an infinite-family proof.
"""
import unittest
from itertools import combinations

try:
    from counterexample import (
        anchored_maximum,
        differences,
        legal,
        max_independent_set,
        periodic_maximum,
        shape,
    )
except ModuleNotFoundError:  # allow package-style discovery
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from counterexample import (
        anchored_maximum,
        differences,
        legal,
        max_independent_set,
        periodic_maximum,
        shape,
    )


class SolverTests(unittest.TestCase):
    def test_matches_brute_force_on_tiny_graphs(self) -> None:
        import random
        rng = random.Random(20261117)
        for n in (8, 10, 12):
            for _ in range(6):
                adj = [0] * n
                for i in range(n):
                    for j in range(i + 1, n):
                        if rng.random() < 0.3:
                            adj[i] |= 1 << j
                            adj[j] |= 1 << i
                got = max_independent_set(adj, n)
                # the returned set is independent
                for i, j in combinations(got, 2):
                    self.assertFalse((adj[i] >> j) & 1)
                best = 0
                for mask in range(1 << n):
                    idx = [i for i in range(n) if mask >> i & 1]
                    if all(not (adj[i] >> j) & 1 for i, j in combinations(idx, 2)):
                        best = max(best, len(idx))
                self.assertEqual(len(got), best)

    def test_conflict_graph_is_symmetric(self) -> None:
        for parameter in (1, 3, 5):
            m = differences(shape(parameter))
            n = 5 * parameter + 4
            for period in (n, 2 * n):
                _, residues = periodic_maximum(parameter, period)
                residue_set = set(residues)
                for x in residues:
                    for d in m:
                        self.assertNotIn((x + d) % period, residue_set)
                        self.assertNotIn((x - d) % period, residue_set)


class AnchoredWindowTests(unittest.TestCase):
    def test_overlap_with_check_py(self) -> None:
        for parameter, expected in ((1, 1), (3, 3), (5, 5), (7, 7)):
            size, points = anchored_maximum(parameter)
            self.assertEqual(size, expected)
            self.assertIn(0, points)
            self.assertTrue(legal(points, differences(shape(parameter))))

    def test_extension_beyond_check_py(self) -> None:
        for parameter in (9, 11):
            size, points = anchored_maximum(parameter)
            self.assertEqual(size, parameter)
            self.assertIn(0, points)
            self.assertTrue(legal(points, differences(shape(parameter))))


def expanded_translates_legal(residues, period, forbidden) -> bool:
    """Independent oracle: expand residues to integer starts and check pairs.

    A periodic set is residues + period*Z. Two distinct starts collide when
    their difference lies in the forbidden set. A residue whose own translate
    collides is therefore illegal whenever some forbidden distance is a
    multiple of the period.
    """
    lifts = sorted({r + k * period for r in residues for k in (-2, -1, 0, 1, 2)})
    for x, y in combinations(lifts, 2):
        if y - x in forbidden:
            return False
    return True


class SelfCollisionPeriodTests(unittest.TestCase):
    def test_period_dividing_a_forbidden_distance_is_empty(self) -> None:
        # b=1 forbids 1, so period 1 self-collides; b=3 forbids 3, so period 3 does
        self.assertEqual(periodic_maximum(1, 1), (0, ()))
        self.assertEqual(periodic_maximum(3, 3), (0, ()))

    def test_reported_witnesses_check_across_repeats(self) -> None:
        cases = [(1, 1), (3, 3), (5, 5)]
        cases += [(b, k * (5 * b + 4)) for b in (1, 3, 5) for k in (1, 2)]
        cases += [(1, 9), (3, 19), (5, 10)]
        for parameter, period in cases:
            size, residues = periodic_maximum(parameter, period)
            forbidden = differences(shape(parameter))
            self.assertEqual(len(residues), size)
            self.assertTrue(
                expanded_translates_legal(residues, period, forbidden),
                (parameter, period, residues),
            )
            if any(d % period == 0 for d in forbidden):
                self.assertEqual(residues, ())

    def test_noncolliding_period_gives_nonempty_witness(self) -> None:
        size, residues = periodic_maximum(1, 9)
        self.assertGreater(size, 0)
        self.assertTrue(expanded_translates_legal(residues, 9, differences(shape(1))))


class PeriodicDensityTests(unittest.TestCase):
    def test_no_density_beats_the_bound(self) -> None:
        for parameter in (1, 3, 5, 7, 9, 11):
            n = 5 * parameter + 4
            for period in (n, 2 * n):
                size, residues = periodic_maximum(parameter, period)
                self.assertEqual(size * n, parameter * period)
                self.assertEqual(len(residues), size)


if __name__ == '__main__':
    unittest.main()
