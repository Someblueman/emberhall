"""Independent deletion checks for the four-agent six-good constructions."""

from fractions import Fraction
from itertools import combinations, permutations
import random
import unittest

from swaps import picking_outcomes, rounds_for
from two_final_extension import EXAMPLE, LEFT, RIGHT, bridge, path, residual_path


def fair(u, a):
    bundles = [[g for g in range(6) if a[g] == i] for i in range(4)]
    return all(any(sum(u[i][g] for g in bundles[i]) >=
                       sum(u[i][g] for g in bundles[j] if g != removed)
                       for removed in bundles[j])
               for i in range(4) for j in range(4) if i != j)


def check_route(case, u, route, start, target):
    case.assertEqual(route[0], start)
    case.assertEqual(route[-1], target)
    for a in route:
        case.assertTrue(fair(u, a), (u, a))
        case.assertEqual(tuple(a.count(i) for i in range(4)), (2, 2, 1, 1))
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(6) if a[g] != b[g]]
        case.assertEqual(len(changed), 2)
        x, y = changed
        case.assertEqual((a[x], a[y]), (b[y], b[x]))


class ExtensionTests(unittest.TestCase):
    def test_braid_outside_old_guard_and_all_loan_branches(self):
        self.assertLess(EXAMPLE[2][5], min(EXAMPLE[2][1], EXAMPLE[2][3]))
        route = bridge(EXAMPLE)
        check_route(self, EXAMPLE, route, LEFT, RIGHT)
        self.assertLessEqual(len(route) - 1, 6)
        rng = random.Random(2026112021)
        branches = set()
        for _ in range(600):
            rows = [[Fraction(rng.randrange(30), rng.randrange(1, 5))
                     for _ in range(6)] for _ in range(4)]
            rows[0][1] = max(rows[0][1:])
            rows[1][2] = max(rows[1][2:])
            for i, x in ((2, 3), (3, 4)):
                rows[i][0] = max(rows[i])
                rows[i][x] = max(rows[i][3:])
            u = tuple(map(tuple, rows))
            branches.add('left' if u[2][2] >= u[2][3] else
                         'right' if u[3][2] >= u[3][4] else 'small')
            result = bridge(u)
            check_route(self, u, result, LEFT, RIGHT)
            self.assertLessEqual(len(result) - 1, 6)
            self.assertTrue(all(a[1] == 0 for a in result))
        self.assertEqual(branches, {'left', 'right', 'small'})
        zero = ((0,) * 6,) * 4
        check_route(self, zero, bridge(zero), LEFT, RIGHT)

    def test_residual_first_upgrade_fails_but_second_repairs_it(self):
        u = ((0, 20, 1, 1, 1, 1), (0, 10, 5, 6, 0, 1),
             (20, 0, 1, 1, 1, 1), (0, 0, 4, 3, 0, 1))
        start = (2, 0, 0, 1, 1, 3)
        target = (2, 0, 3, 1, 0, 1)
        bad = list(start)
        bad[5], bad[3] = bad[3], bad[5]
        self.assertTrue(fair(u, start))
        self.assertFalse(fair(u, tuple(bad)))
        result = residual_path(u, start, target, double=0, anchor=1,
                               single=2, favorite=0)
        check_route(self, u, result, start, target)
        self.assertEqual(len(result) - 1, 2)

    def test_shared_favorite_can_be_below_already_fixed_anchor(self):
        rows = list(map(list, EXAMPLE))
        rows[2][1] = rows[3][1] = 1000
        u = tuple(map(tuple, rows))
        check_route(self, u, bridge(u), LEFT, RIGHT)
        a = ((0, 1), (2, 0), (1, 2), (3, 4), (0, 3), (1, 5))
        b = ((0, 1), (3, 0), (1, 2), (2, 3), (0, 4), (1, 5))
        check_route(self, u, path(u, a, b), LEFT, RIGHT)

    def test_every_fair_residual_pair_for_fresh_cardinal_profiles(self):
        states = sorted(set((2, 0) + a for a in permutations((0, 1, 1, 3))))
        rng = random.Random(2026112022)
        checked = 0
        for _ in range(120):
            rows = [[Fraction(rng.randrange(40), rng.randrange(1, 4))
                     for _ in range(6)] for _ in range(4)]
            rows[0][1] = 40
            rows[2][0] = 40
            u = tuple(map(tuple, rows))
            allowed = [a for a in states if fair(u, a)]
            for a in allowed:
                for b in allowed:
                    result = residual_path(u, a, b, double=0, anchor=1,
                                           single=2, favorite=0)
                    check_route(self, u, result, a, b)
                    self.assertLessEqual(len(result) - 1, 8)
                    self.assertTrue(all(c[0] == 2 and c[1] == 0 for c in result))
                    checked += 1
        self.assertGreater(checked, 3000)

    def test_greedy_endpoints_through_the_entire_graph(self):
        rng = random.Random(2026112023)
        count = 0
        for _ in range(32):
            u = tuple(tuple(rng.randrange(4) for _ in range(6)) for _ in range(4))
            endpoints = picking_outcomes(u, rounds_for(4, 6, (0, 1)))
            pairs = list(combinations(endpoints, 2))
            rng.shuffle(pairs)
            for a, b in pairs[:12]:
                result = path(u, endpoints[a], endpoints[b])
                check_route(self, u, result, a, b)
                count += 1
        self.assertGreater(count, 250)

    def test_invalid_boundaries(self):
        with self.assertRaisesRegex(ValueError, 'four agents'):
            bridge(((0, 0), (0, 0)))
        bad = list(map(list, EXAMPLE))
        bad[2][0] = 0
        with self.assertRaisesRegex(ValueError, 'braid inequalities'):
            bridge(tuple(map(tuple, bad)))
        with self.assertRaisesRegex(ValueError, 'dominate'):
            residual_path(EXAMPLE, LEFT, RIGHT, double=0, anchor=1,
                          single=2, favorite=5)
        with self.assertRaises(ValueError):
            residual_path(EXAMPLE, LEFT, RIGHT, double=0, anchor=True,
                          single=2, favorite=0)
        witness = ((2, 0), (0, 1), (1, 2), (3, 4), (0, 3), (1, 5))
        with self.assertRaisesRegex(ValueError, 'maximizer'):
            path(EXAMPLE, ((2, 5),) + witness[1:], witness)


if __name__ == '__main__':
    unittest.main()
