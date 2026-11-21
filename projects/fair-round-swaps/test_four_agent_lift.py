"""Finite falsification checks; FOUR_AGENT_LIFT.md carries the universal proof."""

from fractions import Fraction
from itertools import combinations, permutations
import random
import unittest

from four_agent_lift import (EXAMPLE, LEFT, PREFIX, RIGHT, TAIL, carrier_path,
                             five_path, padded_path, path)
from swaps import allocation, favorites, validate_witness, rounds_for
from two_final_extension import bridge


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(len(u))]
    return all(any(sum(u[i][g] for g in bundles[i]) >=
                       sum(u[i][g] for g in bundles[j] if g != deleted)
                       for deleted in bundles[j])
               for i in range(len(u)) for j in range(len(u)) if i != j)


def adjacent(a, b):
    changed = [g for g in range(len(a)) if a[g] != b[g]]
    return (len(changed) == 2 and a[changed[0]] == b[changed[1]]
            and a[changed[1]] == b[changed[0]])


def check_route(case, u, route, a, b):
    case.assertEqual((route[0], route[-1]), (a, b))
    sizes = tuple(a.count(i) for i in range(len(u)))
    for current in route:
        case.assertTrue(fair(u, current), (u, current))
        case.assertEqual(tuple(current.count(i) for i in range(len(u))), sizes)
    case.assertTrue(all(adjacent(x, y) for x, y in zip(route, route[1:])))


class LiftTests(unittest.TestCase):
    def test_five_good_both_direct_upgrades_can_fail(self):
        u = ((1, 0, 1, 2, 0), (1, 2, 1, 0, 0), (1, 0, 2, 0, 0))
        a, b = (0, 0, 1, 1, 2), (2, 1, 1, 0, 0)
        self.assertTrue(fair(u, a))
        self.assertFalse(fair(u, (2, 0, 1, 1, 0)))
        self.assertFalse(fair(u, (0, 0, 2, 1, 1)))
        self.assertTrue(fair(u, (0, 1, 1, 0, 2)))
        check_route(self, u, five_path(u, a, b), a, b)

    def test_entire_five_good_graphs_include_non_picking_states(self):
        states = tuple(sorted(set(permutations((0, 0, 1, 1, 2)))))
        rng = random.Random(2026112025)
        for _ in range(120):
            u = tuple(tuple(Fraction(rng.randrange(16), rng.randrange(1, 5))
                            for _ in range(5)) for _ in range(3))
            allowed = [a for a in states if fair(u, a)]
            reached = {allowed[0]}
            while True:
                new = {b for b in allowed if any(adjacent(a, b) for a in reached)}
                if new <= reached:
                    break
                reached |= new
            self.assertEqual(reached, set(allowed))
            for a, b in ((allowed[0], allowed[-1]), (rng.choice(allowed), rng.choice(allowed))):
                result = five_path(u, a, b)
                check_route(self, u, result, a, b)
                self.assertLessEqual(len(result) - 1, 9)

    def test_protected_six_good_graphs(self):
        states = tuple(a for a in sorted(set(permutations((0, 0, 1, 1, 2, 3))))
                       if a[0] in (2, 3))
        rng = random.Random(2026112026)
        for _ in range(100):
            rows = [[rng.randrange(10) for _ in range(6)] for _ in range(4)]
            rows[2][0] = rows[3][0] = 10
            u = tuple(map(tuple, rows))
            allowed = [a for a in states if fair(u, a)]
            for a, b in ((allowed[0], allowed[-1]), (rng.choice(allowed), rng.choice(allowed))):
                result = carrier_path(u, a, b)
                check_route(self, u, result, a, b)
                self.assertTrue(all(c[0] in (2, 3) for c in result))

    def test_failed_unrestricted_lift_and_actual_greedy_endpoints(self):
        small = tuple(tuple(row[g] for g in TAIL) for row in EXAMPLE)
        wrong = list(allocation(PREFIX, 10))
        for g, owner in zip(TAIL, bridge(small)[1]):
            wrong[g] = owner
        self.assertFalse(fair(EXAMPLE, tuple(wrong)))
        left = ((2, 4), (0, 3), (1, 1), (3, 7), (2, 5), (0, 8), (1, 9), (3, 2), (0, 6), (1, 0))
        right = ((3, 4), (0, 3), (1, 1), (2, 5), (3, 7), (0, 8), (1, 9), (2, 6), (0, 2), (1, 0))
        a, b = allocation(left, 10), allocation(right, 10)
        check_route(self, EXAMPLE, padded_path(EXAMPLE, PREFIX, TAIL, LEFT, RIGHT), a, b)
        check_route(self, EXAMPLE, path(EXAMPLE, left, right), a, b)

    def test_greedy_padding_through_seven_complete_rounds(self):
        rng = random.Random(2026112027)
        checked = 0
        for q in range(2, 8):
            for _ in range(80):
                m = 4 * q + 2
                rows = [[rng.randrange(100) for _ in range(m)] for _ in range(4)]
                rows[2][0] = rows[3][0] = 100
                u = tuple(map(tuple, rows))
                remaining, prefix = tuple(range(1, m)), []
                for _ in range(q - 1):
                    for i in (0, 1):
                        h = favorites(u, i, remaining)[0]
                        prefix.append((i, h))
                        remaining = tuple(g for g in remaining if g != h)
                    x, y = favorites(u, 2, remaining)[0], favorites(u, 3, remaining)[0]
                    if x == y:
                        break
                    prefix.extend(((2, x), (3, y)))
                    remaining = tuple(g for g in remaining if g not in (x, y))
                if len(prefix) != 4 * (q - 1):
                    continue
                k = favorites(u, 0, remaining)[0]
                remaining = tuple(g for g in remaining if g != k)
                l = favorites(u, 1, remaining)[0]
                remaining = tuple(g for g in remaining if g != l)
                x, y = favorites(u, 2, remaining)[0], favorites(u, 3, remaining)[0]
                if x == y:
                    continue
                z = next(g for g in remaining if g not in (x, y))
                tail = (0, k, l, x, y, z)
                result = padded_path(u, tuple(prefix), tail, LEFT, RIGHT)
                self.assertTrue(all(fair(u, a) for a in result))
                self.assertTrue(all(adjacent(a, b) for a, b in zip(result, result[1:])))
                self.assertTrue(all(a[0] in (2, 3) for a in result))
                self.assertTrue(all(a[g] == i for a in result for i, g in prefix))
                checked += 1
        self.assertGreater(checked, 60)

    def test_recursive_constructor_preserves_each_fixed_prefix(self):
        first_a = ((2, 4), (0, 3), (1, 1), (3, 7))
        first_b = ((3, 4), (0, 3), (1, 1), (2, 5))
        rest_a = ((2, 5), (0, 8), (1, 9), (3, 2), (0, 6), (1, 0))
        rest_b = ((3, 7), (0, 8), (1, 9), (2, 6), (0, 2), (1, 0))
        for fixed in ((), (0,), (1,), (0, 1), (1, 0)):
            def reorder(first):
                common = tuple(next(p for p in first if p[0] == i) for i in fixed)
                return common + tuple(p for p in first if p[0] not in fixed)
            a, b = reorder(first_a) + rest_a, reorder(first_b) + rest_b
            validate_witness(EXAMPLE, rounds_for(4, 10, (0, 1)), a)
            validate_witness(EXAMPLE, rounds_for(4, 10, (0, 1)), b)
            result = path(EXAMPLE, a, b)
            check_route(self, EXAMPLE, result, allocation(a, 10), allocation(b, 10))
            self.assertTrue(all(state[g] == i for state in result for i, g in a[:len(fixed)]))

    def test_recursive_constructor_longer_greedy_endpoints_and_ties(self):
        rng = random.Random(2026112028)
        def witness(u):
            remaining, result = tuple(range(len(u[0]))), []
            for round_agents in rounds_for(4, len(u[0]), (0, 1)):
                order = list(round_agents)
                rng.shuffle(order)
                for i in order:
                    g = rng.choice(favorites(u, i, remaining))
                    result.append((i, g))
                    remaining = tuple(h for h in remaining if h != g)
            return tuple(result)
        for q in range(2, 7):
            for sample in range(8):
                m = 4 * q + 2
                u = (tuple((0 for _ in range(m))) for _ in range(4)) if sample == 0 else (
                    tuple(Fraction(rng.randrange(10), 3) for _ in range(m)) for _ in range(4))
                u = tuple(u)
                a, b = witness(u), witness(u)
                check_route(self, u, path(u, a, b), allocation(a, m), allocation(b, m))

    def test_invalid_lifts_are_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError, 'prefix is not greedy'):
            padded_path(EXAMPLE, ((0, 0),) + PREFIX[1:], TAIL, LEFT, RIGHT)
        with self.assertRaisesRegex(ValueError, 'six distinct'):
            padded_path(EXAMPLE, PREFIX, (4, 8, 9, 6, 2, 2), LEFT, RIGHT)
        bad = list(map(list, EXAMPLE))
        bad[0][3] = 0
        with self.assertRaises(ValueError):
            padded_path(tuple(map(tuple, bad)), PREFIX, TAIL, LEFT, RIGHT)


if __name__ == '__main__':
    unittest.main()
