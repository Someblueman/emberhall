"""Independent deletion, picking and exchange checks for the seven-good braid."""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from five_agent_seven import EXAMPLE, LEFT, RIGHT, bridge, path, singleton_reduction, swap
from swaps import allocation, ef1, states_with_sizes


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(5)]
    for i, row in enumerate(u):
        own = sum(row[g] for g in bundles[i])
        for bundle in bundles:
            if not any(own >= sum(row[g] for g in bundle if g != removed)
                       for removed in [None] + bundle):
                return False
    return True


def profile(rng):
    u = [[Fraction(rng.randrange(21), rng.randrange(1, 8)) for _ in range(7)]
         for _ in range(5)]
    u[0][4] = max(u[0][4], u[0][6])
    u[0][5] = max(u[0][5], u[0][6])
    u[0][1] = max(u[0][1:])
    u[1][2] = max(u[1][2:])
    for i, own in ((2, 4), (3, 5)):
        u[i][own] = max(u[i][4:])
        u[i][0] = max(u[i])
    u[4][3] = max(u[4][3:])
    return tuple(tuple(row) for row in u)


class SevenGoodTests(unittest.TestCase):
    def check_general_route(self, u, route, final=(0, 1)):
        for a in route:
            self.assertEqual(tuple(a.count(i) for i in range(5)),
                             tuple(1 + (i in final) for i in range(5)))
            self.assertTrue(fair(u, a), a)
        for a, b in zip(route, route[1:]):
            changed = [g for g in range(7) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))
            self.assertNotEqual(a[x], a[y])

    def check_route(self, u):
        for witness in (LEFT, RIGHT):
            self.assertEqual(sorted(i for i, _ in witness[:5]), list(range(5)))
            self.assertEqual(sorted(i for i, _ in witness[5:]), [0, 1])
            remaining = set(range(7))
            for i, g in witness:
                self.assertIn(g, remaining)
                self.assertEqual(u[i][g], max(u[i][h] for h in remaining))
                remaining.remove(g)
        route = bridge(u)
        self.assertEqual(route[0], allocation(LEFT, 7))
        self.assertEqual(route[-1], allocation(RIGHT, 7))
        self.check_general_route(u, route)
        if u[4][2] <= u[4][3]:
            self.assertLessEqual(len(route) - 1, 6)
            self.assertTrue(all(a[3] == 4 and a[1] == 0 for a in route))
        else:
            self.assertLessEqual(len(route) - 1, 63)
            borrowed = [a for a in route if a[2] == 4]
            self.assertTrue(borrowed)
            self.assertTrue(all(a[0] in (2, 3) for a in borrowed))
        return route

    def test_loan_repairs_extra_observer_failure(self):
        self.check_route(EXAMPLE)
        a = allocation(LEFT, 7)
        for x, y in ((4, 6), (0, 4)):
            a = swap(a, x, y)
        self.assertFalse(fair(EXAMPLE, a))
        # E has {g,l}: h's own t=40 loses to even the best remainder 90.
        self.assertEqual({g for g in range(7) if a[g] == 1}, {0, 2})
        self.assertEqual(min(EXAMPLE[4][0], EXAMPLE[4][2]), 90)

    def test_direct_braid_all_three_comparison_branches(self):
        for carrier in (None, 2, 3):
            rows = [list(row) for row in EXAMPLE]
            rows[4][2] = 30
            if carrier is not None:
                rows[carrier][2] = 60
            self.check_route(tuple(tuple(row) for row in rows))
        self.check_route(((0,) * 7,) * 5)

    def test_fresh_exact_profiles_and_ties(self):
        rng = random.Random(23749)
        branches = [0, 0]
        for _ in range(600):
            u = profile(rng)
            branches[u[4][2] > u[4][3]] += 1
            self.check_route(u)
        self.assertTrue(all(count > 30 for count in branches), branches)

    def test_complete_fixed_size_graph_predicate(self):
        states = states_with_sizes((2, 2, 1, 1, 1))
        self.assertEqual(len(states), 1260)
        self.assertEqual(len(set(states)), 1260)
        for a in states:
            self.assertEqual(ef1(EXAMPLE, a), fair(EXAMPLE, a))
        # Independently close the full fair component, including nongreedy states.
        unseen = {a for a in states if fair(EXAMPLE, a)}
        reached = {allocation(LEFT, 7)}
        todo = list(reached)
        unseen -= reached
        while todo:
            a = todo.pop()
            for x, y in combinations(range(7), 2):
                b = swap(a, x, y)
                if b in unseen:
                    unseen.remove(b)
                    reached.add(b)
                    todo.append(b)
        self.assertIn(allocation(RIGHT, 7), reached)

    def test_invalid_inputs(self):
        for u in (EXAMPLE[:4], tuple(row[:6] for row in EXAMPLE),
                  ((-1,) * 7,) * 5, ((0.0,) * 7,) * 5):
            with self.assertRaises(ValueError):
                bridge(u)
        rows = [list(row) for row in EXAMPLE]
        rows[2][0] = 0
        with self.assertRaisesRegex(ValueError, 'maximizer'):
            bridge(tuple(tuple(row) for row in rows))

    def test_arbitrary_greedy_endpoints_and_singleton_reduction(self):
        rng = random.Random(23758)
        nontrivial = 0
        for _ in range(180):
            u = tuple(tuple(Fraction(rng.randrange(12), rng.randrange(1, 6))
                            for _ in range(7)) for _ in range(5))
            final = tuple(rng.sample(range(5), 2))
            witnesses = []
            for _ in range(2):
                remaining = set(range(7))
                w = []
                for i in rng.sample(range(5), 5) + list(final):
                    best = max(u[i][g] for g in remaining)
                    g = rng.choice([g for g in sorted(remaining) if u[i][g] == best])
                    w.append((i, g))
                    remaining.remove(g)
                w = tuple(w)
                witnesses.append(w)
                route, target = singleton_reduction(u, w, final)
                self.assertEqual(route[0], allocation(w, 7))
                self.assertEqual(route[-1], allocation(target, 7))
                self.assertNotIn(target[0][0], final)
                self.check_general_route(u, route, final)
                remaining = set(range(7))
                for i, g in target:
                    self.assertEqual(u[i][g], max(u[i][h] for h in remaining))
                    remaining.remove(g)
                nontrivial += len(route) > 1
            route = path(u, *witnesses, final)
            self.check_general_route(u, route, final)
            self.assertEqual(route[0], allocation(witnesses[0], 7))
            self.assertEqual(route[-1], allocation(witnesses[1], 7))
        self.assertGreater(nontrivial, 0)

    def test_nontrivial_reduction_fibers(self):
        fixtures = (
            (((5, 6, 1, 0, 6, 2, 4), (5, 6, 7, 2, 3, 2, 0),
              (3, 5, 3, 4, 2, 1, 3), (5, 3, 0, 0, 5, 0, 0),
              (2, 0, 6, 4, 7, 3, 2)),
             ((0, 1), (2, 3), (4, 4), (1, 2), (3, 0), (0, 6), (1, 5)), False),
            (((2, 3, 4, 0, 5, 1, 6), (7, 4, 3, 1, 7, 3, 4),
              (1, 1, 0, 1, 2, 2, 5), (7, 5, 5, 3, 0, 3, 3),
              (7, 6, 1, 3, 2, 4, 0)),
             ((1, 0), (3, 1), (0, 6), (2, 4), (4, 5), (0, 2), (1, 3)), True),
            (((2, 3, 6, 4, 3, 0, 0), (4, 0, 1, 7, 7, 5, 5),
              (2, 1, 6, 0, 3, 3, 2), (4, 2, 7, 1, 5, 3, 0),
              (6, 1, 1, 4, 3, 3, 2)),
             ((0, 2), (1, 3), (3, 4), (2, 5), (4, 0), (0, 1), (1, 6)), True),
        )
        for u, w, has_anchor in fixtures:
            route, target = singleton_reduction(u, w)
            self.assertGreater(len(route), 1)
            self.check_general_route(u, route)
            self.assertEqual(target[1][0] in (0, 1), has_anchor)

    def test_actual_commands(self):
        script = Path(__file__).with_name('five_agent_seven.py')
        for flags in ([], ['--general']):
            run = subprocess.run([sys.executable, str(script), *flags], check=True,
                                 capture_output=True, text=True)
            data = json.loads(run.stdout)
            route = [tuple(map(int, a)) for a in data['path']]
            self.check_general_route(EXAMPLE, route)
            self.assertEqual(data['exchanges'], len(route) - 1)
            for label, state in (('start', route[0]), ('target', route[-1])):
                self.assertEqual(allocation(data['witnesses'][label], 7), state)

    def test_general_zero_ties_and_invalid_witnesses(self):
        zeros = ((0,) * 7,) * 5
        a = ((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (3, 5), (4, 6))
        b = ((4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (4, 5), (3, 6))
        self.check_general_route(zeros, path(zeros, a, b, (3, 4)), (3, 4))
        for final in ((0,), (0, 0), (0, 7)):
            with self.assertRaises(ValueError):
                path(EXAMPLE, LEFT, RIGHT, final)
        for bad in (LEFT[:-1], ((2, 7),) + LEFT[1:], (LEFT[0],) + LEFT):
            with self.assertRaises(ValueError):
                singleton_reduction(EXAMPLE, bad)


if __name__ == '__main__':
    unittest.main()
