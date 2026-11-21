"""Direct deletion tests for the shared-favorite bridge, with exact utilities."""

from fractions import Fraction
from itertools import combinations
from random import Random
import unittest

from swaps import allocation, favorites, picking_outcomes, rounds_for, validate_witness
from two_rounds import EXAMPLE, braid, path, tail_bridge


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(3)]
    return all(not goods or any(sum(row[g] for g in bundles[i]) >=
                                sum(row[g] for g in goods if g != removed)
                                for removed in goods)
               for i, row in enumerate(u) for goods in bundles)


def swap(a, x, y):
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


class TwoRoundTest(unittest.TestCase):
    def assert_path(self, u, wa, wb, states):
        rounds = rounds_for(3, len(u[0]), (0,))
        validate_witness(u, rounds, wa)
        validate_witness(u, rounds, wb)
        self.assertEqual(states[0], allocation(wa, len(u[0])))
        self.assertEqual(states[-1], allocation(wb, len(u[0])))
        self.assertTrue(all(fair(u, state) for state in states))
        for a, b in zip(states, states[1:]):
            neighbors = {swap(a, x, y) for x, y in combinations(range(len(a)), 2)
                         if a[x] != a[y]}
            self.assertIn(b, neighbors)

    def test_two_round_example_and_wrong_pivot(self):
        wa, wb, states = braid(EXAMPLE)
        self.assert_path(EXAMPLE, wa, wb, states)
        self.assertEqual(states, [(1, 0, 2, 1, 0, 2, 0), (1, 0, 2, 1, 2, 0, 0),
                                  (2, 0, 2, 1, 1, 0, 0), (2, 0, 2, 1, 0, 0, 1)])
        a, b = states[0], states[-1]
        self.assertFalse(fair(EXAMPLE, swap(a, 0, 5)))
        self.assertFalse(fair(EXAMPLE, swap(a, 6, 5)))
        with self.assertRaisesRegex(ValueError, "sum bounds"):
            tail_bridge(EXAMPLE, a, b, shared=0, pivot=1, x=6, y=5)
        wrong = swap(a, 1, 5)  # Borrowing the first common D good loses D's protection.
        self.assertFalse(fair(EXAMPLE, wrong))
        self.assertEqual(sum(EXAMPLE[0][g] for g, owner in enumerate(wrong) if owner == 0), 12)

    def test_random_braids_through_five_rounds_and_ties(self):
        rng = Random(2026112010)
        branches = set()
        for q in range(1, 6):
            for trial in range(300):
                m = 3 * q + 1
                rows = [[rng.randrange(8) for _ in range(m)] for _ in range(3)]
                for i in (1, 2):
                    rows[i][0] = max(rows[i]) + (trial % 2)
                u = tuple(tuple(Fraction(v, 3) for v in row) for row in rows)
                wa, wb, states = braid(u)
                self.assert_path(u, wa, wb, states)
                branches.add(len(states) - 1)
        self.assertEqual(branches, {1, 2, 3})

    def test_zero_and_invalid_inputs(self):
        for q in (1, 2, 3):
            u = ((0,) * (3 * q + 1),) * 3
            wa, wb, states = braid(u)
            self.assert_path(u, wa, wb, states)
        with self.assertRaisesRegex(ValueError, "maximize"):
            braid(((0, 0, 0, 0), (0, 1, 2, 3), (0, 1, 2, 3)))
        with self.assertRaises(ValueError):
            braid(((0,) * 6,) * 3)

    def test_all_endpoints_on_small_two_round_profiles(self):
        rng = Random(2026112012)
        checked = 0
        for trial in range(24):
            u = tuple(tuple(rng.randrange(4) for _ in range(7)) for _ in range(3))
            outcomes = picking_outcomes(u, rounds_for(3, 7, (0,)))
            for wa, wb in combinations(outcomes.values(), 2):
                self.assert_path(u, wa, wb, path(u, wa, wb))
                checked += 1
        self.assertGreater(checked, 1000)

    def test_arbitrary_three_agent_endpoints_through_six_rounds(self):
        rng = Random(2026112013)
        checked = longest = 0

        def endpoint(u, q):
            pool = tuple(range(len(u[0])))
            result = []
            for _ in range(q):
                order = [0, 1, 2]
                rng.shuffle(order)
                for i in order:
                    g = rng.choice(favorites(u, i, pool))
                    result.append((i, g))
                    pool = tuple(h for h in pool if h != g)
            return tuple(result) + ((0, pool[0]),)

        for q in range(1, 7):
            for trial in range(50):
                u = tuple(tuple(0 if trial == 0 else rng.randrange(6) for _ in range(3*q + 1))
                          for _ in range(3))
                wa, wb = endpoint(u, q), endpoint(u, q)
                route = path(u, wa, wb)
                self.assert_path(u, wa, wb, route)
                checked += 1
                longest = max(longest, len(route) - 1)
        print(f"three-agent paths: {checked}, longest {longest} exchanges")


if __name__ == "__main__":
    unittest.main()
