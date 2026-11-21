"""Deletion and finite-graph checks independent of the construction predicates."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
import random
import unittest

from five_agent_eight import LEFT, RIGHT
from five_agent_protected import (BOUNDARY, START, TARGET, common_crossing,
                                  protected_path, separation_formula)


def fair(u, a):
    bundles = [[g for g, k in enumerate(a) if k == i] for i in range(len(u))]
    for i, row in enumerate(u):
        own = sum(row[g] for g in bundles[i])
        for bundle in bundles:
            if not any(own >= sum(row[g] for g in bundle if g != h)
                       for h in [None] + bundle):
                return False
    return True


def neighbors(a):
    for x, y in combinations(range(len(a)), 2):
        if a[x] != a[y]:
            b = list(a)
            b[x], b[y] = b[y], b[x]
            yield tuple(b)


class ProtectedTests(unittest.TestCase):
    def test_common_crossing_real_utility_cases(self):
        rng = random.Random(2026112055)
        for n in range(3, 13):
            m = 2 * n - 2
            for trial in range(40):
                u = [[Fraction(rng.randrange(10), rng.choice((1, 3, 7)))
                      for _ in range(m)] for _ in range(n)]
                carriers = tuple(rng.sample(range(n), 2))
                g = rng.randrange(m)
                for i in carriers:
                    u[i][g] = max(u[i])
                if trial == 0:
                    u = [[0] * m for _ in range(n)]
                a, b = common_crossing(tuple(map(tuple, u)), g, carriers)
                self.assertTrue(fair(u, a))
                self.assertTrue(fair(u, b))
                self.assertIn(b, set(neighbors(a)))
                for i in range(n):
                    self.assertEqual(a.count(i), 1 if i in carriers else 2)
                    self.assertEqual(b.count(i), a.count(i))
                self.assertEqual((a[g], b[g]), carriers)

    def test_boundary_endpoints_are_actual_greedy_outcomes(self):
        for witness, expected in ((LEFT, START), (RIGHT, TARGET)):
            remaining = set(range(8))
            owners = [-1] * 8
            self.assertEqual({i for i, _ in witness[:5]}, set(range(5)))
            self.assertEqual([i for i, _ in witness[5:]], [0, 1, 2])
            for i, g in witness:
                self.assertIn(g, remaining)
                self.assertEqual(BOUNDARY[i][g], max(BOUNDARY[i][h] for h in remaining))
                remaining.remove(g)
                owners[g] = i
            self.assertEqual(tuple(owners), expected)

    def test_all_fixed_states_and_no_crossing_edge(self):
        # Independent enumeration and deletion checks, including nongreedy states.
        states = set(permutations((0, 0, 1, 1, 2, 2, 3, 4)))
        self.assertEqual(len(states), 5040)
        full = {a for a in states if fair(BOUNDARY, a)}
        protected = {a for a in full if a[0] in (3, 4)}
        fixed = {a for a in protected if a[1] == 0 and a[2] == 1}
        self.assertEqual((len(full), len(protected), len(fixed)), (1054, 482, 20))
        self.assertEqual(Counter(a[0] for a in fixed), {3: 10, 4: 10})
        for a in fixed:
            self.assertTrue(all(b[0] == a[0] for b in neighbors(a) if b in fixed))
        # Every half is connected under a different reachability implementation.
        for start in (START, TARGET):
            reached = {start}
            while True:
                expanded = reached | {b for a in reached for b in neighbors(a) if b in fixed}
                if expanded == reached:
                    break
                reached = expanded
            self.assertEqual(reached, {a for a in fixed if a[0] == start[0]})
        self.assertIsNone(protected_path(BOUNDARY, START, TARGET, (1, 2)))

    def test_moving_second_anchor_restores_a_protected_route(self):
        route = protected_path(BOUNDARY, START, TARGET, (1,))
        self.assertIsNotNone(route)
        self.assertEqual((route[0], route[-1]), (START, TARGET))
        self.assertTrue(any(a[2] != 1 for a in route))
        for a in route:
            self.assertEqual(a[1], 0)
            self.assertIn(a[0], (3, 4))
            self.assertTrue(fair(BOUNDARY, a))
        self.assertTrue(all(b in set(neighbors(a)) for a, b in zip(route, route[1:])))

    def test_invalid_domains_and_symbolic_export(self):
        with self.assertRaises(ValueError):
            common_crossing(BOUNDARY, 3, (3, 4))
        with self.assertRaises(ValueError):
            common_crossing(BOUNDARY, 0, (3, 3))
        with self.assertRaises(ValueError):
            protected_path(BOUNDARY, START, TARGET, (8,))
        with self.assertRaises(ValueError):
            separation_formula((0,))
        formula = separation_formula((1, 2))
        self.assertIn('(set-logic QF_LRA)', formula)
        self.assertEqual(formula.count('(declare-const u'), 40)
        self.assertEqual(formula.count('(declare-const r'), 120)
        self.assertTrue(formula.endswith('(check-sat)\n'))


if __name__ == '__main__':
    unittest.main()
