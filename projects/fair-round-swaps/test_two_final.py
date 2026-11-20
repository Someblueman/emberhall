"""Independent deletion checks for the guarded four-agent exchange path."""

from fractions import Fraction
from itertools import combinations
from random import Random
import unittest

from two_final import EXAMPLE, LEFT, RIGHT, bridge, core_path, swap
from swaps import allocation, rounds_for, validate_witness


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(4)]
    return all(not goods or any(sum(row[g] for g in bundles[i]) >=
                                sum(row[g] for g in goods if g != removed)
                                for removed in goods)
               for i, row in enumerate(u) for goods in bundles)


class TwoFinalTest(unittest.TestCase):
    def test_recorded_path_and_ignored_observer_failure(self):
        route = bridge(EXAMPLE)
        self.assertEqual(route[0], allocation(LEFT, 6))
        self.assertEqual(route[-1], allocation(RIGHT, 6))
        self.assertEqual(len(route), 5)
        self.assertTrue(all(fair(EXAMPLE, a) for a in route))
        bad = swap(route[0], 1, 4)
        # Ignore E=1: the three-agent subproblem is fair after deleting that observer.
        reduced_goods = (0, 1, 3, 4)
        reduced_u = tuple(tuple(EXAMPLE[i][g] for g in reduced_goods) for i in (0, 2, 3))
        renamed = {0: 0, 2: 1, 3: 2}
        reduced = tuple(renamed[bad[g]] for g in reduced_goods)
        from swaps import ef1
        self.assertTrue(ef1(reduced_u, reduced))
        self.assertFalse(fair(EXAMPLE, bad))

    def test_guarded_rational_profiles_and_all_ties(self):
        rng = Random(2026112014)
        profiles = [((0,) * 6,) * 4]
        for _ in range(300):
            profiles.append((
                (rng.randrange(120), 100, rng.randrange(100), rng.randrange(40, 80),
                 rng.randrange(40, 80), rng.randrange(20)),
                (rng.randrange(120), rng.randrange(120), 100, rng.randrange(80),
                 rng.randrange(80), rng.randrange(80)),
                (100, rng.randrange(61), rng.randrange(61), 80, rng.randrange(81), 60),
                (100, rng.randrange(61), rng.randrange(61), rng.randrange(81), 80, 60),
            ))
        for profile in profiles:
            u = tuple(tuple(Fraction(v, 7) for v in row) for row in profile)
            route = bridge(u)
            for w in (LEFT, RIGHT):
                validate_witness(u, rounds_for(4, 6, (0, 1)), w)
            self.assertTrue(all(fair(u, a) for a in route))
            for a, b in zip(route, route[1:]):
                self.assertIn(b, {swap(a, x, y) for x, y in combinations(range(6), 2)
                                  if a[x] != a[y]})

    def test_failed_guard_is_refused_without_a_nonconnectivity_claim(self):
        u = [list(row) for row in EXAMPLE]
        u[2][5] = 0  # Endpoints still pick greedily, but z is unsafe for i.
        with self.assertRaisesRegex(ValueError, "bridge guard"):
            bridge(tuple(tuple(row) for row in u))

    def test_safe_core_with_independent_fairness_and_neighbors(self):
        rng = Random(2026112016)
        for _ in range(100):
            u = (tuple(rng.randrange(20) for _ in range(6)),
                 tuple(rng.randrange(20) for _ in range(6)),
                 (20, 20, 1, 2, 3, 4), (20, 20, 4, 3, 2, 1))
            states = []
            for pair in combinations(range(2, 6), 2):
                a = (2, 3) + tuple(0 if g in pair else 1 for g in range(2, 6))
                if fair(u, a):
                    states.append(a)
            self.assertGreaterEqual(len(states), 4)
            for a, b in combinations(states, 2):
                route = core_path(u, a, b)
                self.assertLessEqual(len(route), 3)
                self.assertEqual((route[0], route[-1]), (a, b))
                self.assertTrue(all(fair(u, state) for state in route))
                for x, y in zip(route, route[1:]):
                    self.assertIn(y, {swap(x, g, h) for g, h in combinations(range(6), 2)
                                      if x[g] != x[h]})


if __name__ == "__main__":
    unittest.main()
