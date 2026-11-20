"""Literal deletion and maximizing-pick checks for the terminal-anchor proof."""

from fractions import Fraction
from itertools import product
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

from reserved_completion import (acquire_best_tail, normalize_guarded,
                                 normalize_with_favorite, terminal_buffer)
from reserved_singleton import LOSS_ANCHORS, LOSS_START, LOSS_STRICT_PROFILE


def fair(u, state):
    bundles = [[g for g, a in enumerate(state) if a == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in own) >= sum(row[g] for g in other if g != t)
                   for t in other) for row, own in zip(u, bundles) for other in bundles)


def check(test, u, start, singleton, anchors):
    route, witness = normalize_guarded(u, start, singleton, anchors)
    test.assertEqual(route[0], start)
    test.assertLessEqual(len(route) - 1, 2 * len(anchors) + 1)
    sizes = tuple(start.count(i) for i in range(len(u)))
    values = []
    for state in route:
        test.assertTrue(fair(u, state))
        test.assertEqual(tuple(state.count(i) for i in range(len(u))), sizes)
        values.append(u[singleton][state.index(singleton)])
    test.assertEqual(values, sorted(values))
    for left, right in zip(route, route[1:]):
        changed = [g for g in range(len(start)) if left[g] != right[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((left[x], left[y]), (right[y], right[x]))
    remaining, final = set(range(len(start))), [-1] * len(start)
    for offset in (0, len(u)):
        group = witness[offset:offset + (len(u) if offset == 0 else len(anchors))]
        expected = set(range(len(u))) if offset == 0 else set(range(len(u))) - {singleton}
        test.assertEqual({i for i, _ in group}, expected)
    for i, g in witness:
        test.assertIn(g, remaining)
        test.assertTrue(all(u[i][g] >= u[i][h] for h in remaining))
        remaining.remove(g)
        final[g] = i
    test.assertFalse(remaining)
    test.assertEqual(tuple(final), route[-1])
    return route, witness


class ReservedCompletionTests(unittest.TestCase):
    def test_best_tail_chain_can_decrease_between_improvements(self):
        u = ((10, 0, 0, 0, 0, 0, 0), (10, 1, 0, 0, 0, 0, 10),
             (10, 10, 1, 0, 0, 0, 0), (0, 9, 7, 10, 0, 0, 5))
        start, anchors = (0, 1, 2, 0, 1, 2, 3), ((0, 0), (1, 1), (2, 2))
        route, chain = acquire_best_tail(u, start, 3, anchors)
        self.assertEqual(chain, (1, 2))
        self.assertEqual([u[3][a.index(3)] for a in route], [5, 9, 7, 10])
        self.assertTrue(all(fair(u, a) for a in route))

    def test_unrestricted_best_tail_chains(self):
        rng = Random(20261120097)
        blocked, changed = 0, 0
        for n in range(2, 17):
            for _ in range(30):
                m = 2 * n - 1
                u = [[Fraction(rng.randrange(16), rng.choice((1, 2, 5)))
                      for _ in range(m)] for _ in range(n)]
                order = list(range(n - 1))
                rng.shuffle(order)
                remaining, start, anchors = set(range(1, m)), [n - 1] + [-1] * (m - 1), []
                for a in order:
                    p = max(remaining, key=lambda g: (u[a][g], g))
                    start[p] = a
                    anchors.append((a, p))
                    remaining.remove(p)
                tails = sorted(remaining)
                rng.shuffle(tails)
                u[-1][0] = 2
                for (a, p), t in zip(anchors, tails):
                    start[t] = a
                    if u[-1][t] > 2:
                        u[-1][p] = Fraction(rng.randrange(5), 2)
                u, start, anchors = tuple(map(tuple, u)), tuple(start), tuple(anchors)
                route, chain = acquire_best_tail(u, start, n - 1, anchors)
                indices = [order.index(a) for a in chain]
                self.assertEqual(indices, sorted(set(indices)))
                self.assertLessEqual(len(route) - 1, n)
                self.assertTrue(all(fair(u, state) for state in route))
                self.assertTrue(all(u[-1][state.index(n - 1)] >= 2 for state in route))
                target = max(u[-1][t] for t in tails)
                self.assertEqual(u[-1][route[-1].index(n - 1)], max(2, target))
                for a in chain:
                    value = lambda state: sum(u[a][g] for g, b in enumerate(state) if b == a)
                    self.assertGreater(value(route[-1]), value(start))
                for left, right in zip(route, route[1:]):
                    delta = [g for g in range(m) if left[g] != right[g]]
                    self.assertEqual(len(delta), 2)
                    x, y = delta
                    self.assertEqual((left[x], left[y]), (right[y], right[x]))
                blocked += bool(chain)
                changed += len(route) > 1
        print(f"unrestricted best-tail chains: 450; changed: {changed}; blocked: {blocked}")

    def test_strict_lost_certificate_example_now_normalizes(self):
        self.assertEqual(terminal_buffer(LOSS_STRICT_PROFILE, LOSS_START, 3, LOSS_ANCHORS),
                         (2, 5, 6, "anchor"))
        route, witness = check(self, LOSS_STRICT_PROFILE, LOSS_START, 3, LOSS_ANCHORS)
        self.assertEqual(route[1], (1, 0, 1, 0, 2, 2, 3))
        self.assertEqual(witness[:4], ((0, 3), (1, 4), (3, 6), (2, 5)))

    def test_all_three_good_integer_inputs(self):
        tested = 0
        for flat in product(range(3), repeat=6):
            u = (flat[:3], flat[3:])
            for z in range(3):
                start = tuple(int(g != z) for g in range(3))
                if not fair(u, start):
                    continue
                for p in range(3):
                    if p == z or any(u[1][g] > u[1][p] for g in range(3) if g != z):
                        continue
                    anchors = ((1, p),)
                    if (terminal_buffer(u, start, 0, anchors) is not None
                            or max(u[0][g] for g in range(3) if g not in (z, p)) <= u[0][z]):
                        check(self, u, start, 0, anchors)
                        tested += 1
        print(f"complete three-good admitted inputs: {tested}")
        self.assertEqual(tested, 2376)

    def test_all_binary_five_good_reserved_inputs(self):
        rows = tuple(product(range(2), repeat=5))
        tested, branches = 0, set()
        start, anchors = (2, 0, 0, 1, 1), ((0, 1), (1, 3))
        for a in rows:
            if a[1] < max(a[1:]):
                continue
            for b in rows:
                if b[3] < max(b[2], b[4]):
                    continue
                for s in rows:
                    u = (a, b, s)
                    if not fair(u, start):
                        continue
                    plan = terminal_buffer(u, start, 2, anchors)
                    safe = s[0] >= max(s[2], s[4])
                    if plan is not None or safe:
                        check(self, u, start, 2, anchors)
                        tested += 1
                        branches.add("safe" if safe else plan[-1])
        self.assertEqual(branches, {"safe", "anchor", "tail"})
        print(f"complete binary five-good admitted inputs: {tested}")

    def test_seeded_exact_profiles_and_relabellings(self):
        rng = Random(20261120093)
        tested = unsafe = twice_improved = 0
        for n in range(3, 15):
            for case in range(40):
                m, singleton = 2 * n - 1, rng.randrange(n)
                rows = [[Fraction(rng.randrange(15), rng.choice((1, 2, 7)))
                         for _ in range(m)] for _ in range(n)]
                order = [i for i in range(n) if i != singleton]
                rng.shuffle(order)
                z = rng.randrange(m)
                remaining, owners, anchors = set(range(m)) - {z}, [-1] * m, []
                owners[z] = singleton
                for a in order:
                    p = max(remaining, key=lambda g: (rows[a][g], g))
                    anchors.append((a, p))
                    owners[p] = a
                    remaining.remove(p)
                tails = sorted(remaining)
                rng.shuffle(tails)
                rows[singleton][z] = 2
                for (a, p), t in zip(anchors, tails):
                    owners[t] = a
                    if rows[singleton][t] > 2 or a == order[-1]:
                        rows[singleton][p] = Fraction(rng.randrange(5), 2)
                u, start, anchors = tuple(map(tuple, rows)), tuple(owners), tuple(anchors)
                route, _ = check(self, u, start, singleton, anchors)
                vals = [u[singleton][a.index(singleton)] for a in route]
                unsafe += max(u[singleton][t] for t in tails) > 2
                twice_improved += len(set(vals)) > 2
                tested += 1
        self.assertEqual(tested, 480)
        self.assertGreater(unsafe, 400)
        self.assertGreater(twice_improved, 0)
        print(f"terminal-anchor routes: {tested}; unsafe: {unsafe}; twice improved: {twice_improved}")

    def test_seeded_tail_buffers(self):
        rng = Random(20261120095)
        for n in range(3, 15):
            for _ in range(20):
                m = 2 * n - 1
                u = [[Fraction(rng.randrange(17), rng.choice((1, 3))) for _ in range(m)]
                     for _ in range(n)]
                remaining, start, anchors = set(range(1, m)), [n - 1] + [-1] * (m - 1), []
                for a in range(n - 1):
                    p = max(remaining, key=lambda g: (u[a][g], g))
                    start[p] = a
                    remaining.remove(p)
                    anchors.append((a, p))
                tails = sorted(remaining)
                rng.shuffle(tails)
                q = max(tails, key=lambda t: u[-2][t])
                if n == 3 and q != tails[-1]:
                    tails.reverse()
                for (a, p), t in zip(anchors, tails):
                    start[t] = a
                    u[-1][p] = 0
                u[-1][0] = u[-1][q] = u[-1][tails[-1]] = 0
                h = next(t for t in tails if t not in (q, tails[-1]))
                u[-1][h] = 1
                u[-1][anchors[-1][1]] = max(u[-1][t] for t in tails) + 1
                u, start, anchors = tuple(map(tuple, u)), tuple(start), tuple(anchors)
                self.assertEqual(terminal_buffer(u, start, n - 1, anchors)[-1], "tail")
                check(self, u, start, n - 1, anchors)

    def test_two_value_doubles_with_singleton_gap(self):
        rng = Random(20261120096)
        branches = set()
        for n in range(2, 22):
            for _ in range(20):
                m, singleton = 2 * n - 1, rng.randrange(n)
                u = []
                for a in range(n):
                    low = Fraction(rng.randrange(5), 7)
                    high = low + Fraction(rng.randrange(1, 11), 3)
                    u.append([rng.choice((low, high)) for _ in range(m)])
                order = [a for a in range(n) if a != singleton]
                rng.shuffle(order)
                z = rng.randrange(m)
                remaining, start, anchors = set(range(m)) - {z}, [-1] * m, []
                start[z] = singleton
                for a in order:
                    p = max(remaining, key=lambda g: (u[a][g], g))
                    start[p] = a
                    anchors.append((a, p))
                    remaining.remove(p)
                tails = sorted(remaining)
                rng.shuffle(tails)
                u[singleton][z] = 1
                h_value = max(u[singleton][t] for t in tails)
                for (a, p), t in zip(anchors, tails):
                    start[t] = a
                    u[singleton][p] = (0 if u[singleton][t] > 1
                                       else rng.choice((0, max(1, h_value))))
                u, start, anchors = tuple(map(tuple, u)), tuple(start), tuple(anchors)
                plan = terminal_buffer(u, start, singleton, anchors)
                safe = max(u[singleton][t] for t in tails) <= 1
                self.assertTrue(safe or plan is not None)
                branches.add("safe" if safe else plan[-1])
                check(self, u, start, singleton, anchors)
        self.assertEqual(branches, {"safe", "anchor", "tail"})

    def test_commuting_pivot_ties_and_outside_domain(self):
        u = ((0, 3, 1, 3, 1), (0, 3, 1, 3, 1), (2, 1, 5, 4, 0))
        start, anchors = (2, 0, 0, 1, 1), ((0, 1), (1, 3))
        self.assertEqual(terminal_buffer(u, start, 2, anchors), (0, 1, 2, "anchor"))
        check(self, u, start, 2, anchors)
        check(self, ((0,) * 5,) * 3, start, 2, anchors)
        with self.assertRaises(ValueError):
            normalize_guarded(u, start[:-1], 2, anchors)

    def test_safe_favorite_tail_with_high_terminal_anchor(self):
        start, anchors = (2, 0, 0, 1, 1), ((0, 1), (1, 3))
        for tied in (False, True):
            u = ((8, 10, 1, 7, 2), (3, 11, 8 if tied else 2, 9, 8), (2, 1, 5, 7, 1))
            self.assertEqual(terminal_buffer(u, start, 2, anchors), (1, 4, 3, "tail"))
            check(self, u, start, 2, anchors)
        outside = ((8, 10, 1, 7, 2), (3, 11, 8, 9, 2), (2, 1, 5, 7, 1))
        self.assertIsNone(terminal_buffer(outside, start, 2, anchors))
        with self.assertRaisesRegex(ValueError, "terminal buffer"):
            normalize_guarded(outside, start, 2, anchors)

    def test_fixed_favorite_lift(self):
        rng = Random(20261120094)
        for fixed in range(5):
            agents = tuple(a for a in range(5) if a != fixed)
            goods = list(range(8))
            rng.shuffle(goods)
            u = [[0] * 8 for _ in range(5)]
            start = [fixed] * 8
            for a, row in enumerate(LOSS_STRICT_PROFILE):
                for g, v in enumerate(row):
                    u[agents[a]][goods[g]] = v
                    start[goods[g]] = agents[LOSS_START[g]]
            u[fixed][goods[7]] = 100
            u = tuple(map(tuple, u))
            anchors = tuple((agents[a], goods[g]) for a, g in LOSS_ANCHORS)
            route, witness = normalize_with_favorite(u, tuple(start), fixed, agents[3], anchors)
            self.assertTrue(all(fair(u, state) and state[goods[7]] == fixed for state in route))
            self.assertEqual(witness[0], (fixed, goods[7]))
            remaining = set(range(8))
            for a, g in witness:
                self.assertTrue(all(u[a][g] >= u[a][h] for h in remaining))
                remaining.remove(g)
            expected = [-1] * 8
            for a, g in witness:
                expected[g] = a
            self.assertEqual(tuple(expected), route[-1])
            with self.assertRaises(ValueError):
                normalize_with_favorite(u, tuple(start), fixed, fixed, anchors)
            bad = [list(row) for row in u]
            bad[fixed][goods[0]] = 101
            with self.assertRaisesRegex(ValueError, "global favorite"):
                normalize_with_favorite(tuple(map(tuple, bad)), tuple(start), fixed, agents[3], anchors)

    def test_real_command(self):
        result = subprocess.run([sys.executable, "-S", str(Path(__file__).with_name("reserved_completion.py"))],
                                check=True, text=True, capture_output=True)
        self.assertIn("Verified 4 EF1 exchanges; bound 7", result.stdout)


if __name__ == "__main__":
    unittest.main()
