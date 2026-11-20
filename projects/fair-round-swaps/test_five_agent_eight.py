"""Independent deletion, pick and owner-change checks for the new construction."""

from fractions import Fraction
import random
import unittest

from five_agent_eight import (EXAMPLE, LEFT, RIGHT, anchor_bridge, path,
                              singleton_reduction)


def fair(u, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
    return all(any(sum(u[i][g] for g in bundles[i]) >=
                       sum(u[i][g] for g in bundles[j] if g != removed)
                       for removed in [None] + bundles[j])
               for i in range(len(u)) for j in range(len(u)))


def owners(witness, m):
    result = [-1] * m
    for i, g in witness:
        if result[g] != -1:
            raise AssertionError("repeated good")
        result[g] = i
    return tuple(result)


def greedy(u, witness, final):
    n, m = len(u), len(u[0])
    assert len(witness) == m
    assert {i for i, _ in witness[:n]} == set(range(n))
    assert sorted(i for i, _ in witness[n:]) == sorted(final)
    remaining = set(range(m))
    for i, g in witness:
        assert g in remaining and all(u[i][g] >= u[i][h] for h in remaining)
        remaining.remove(g)


def witness(u, final, rng):
    early, late = list(range(len(u))), list(final)
    rng.shuffle(early)
    rng.shuffle(late)
    remaining = set(range(len(u[0])))
    result = []
    for i in early + late:
        best = max(u[i][g] for g in remaining)
        g = rng.choice(sorted(g for g in remaining if u[i][g] == best))
        remaining.remove(g)
        result.append((i, g))
    return tuple(result)


class EightGoodTests(unittest.TestCase):
    def route(self, u, result, start=None, target=None):
        if start is not None:
            self.assertEqual(result[0], owners(start, len(u[0])))
        if target is not None:
            self.assertEqual(result[-1], owners(target, len(u[0])))
        sizes = sorted(result[0])
        for a in result:
            self.assertEqual(sorted(a), sizes)
            self.assertTrue(fair(u, a), (u, a))
        for a, b in zip(result, result[1:]):
            changed = [g for g in range(len(a)) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_recorded_example(self):
        greedy(EXAMPLE, LEFT, (0, 1, 2))
        greedy(EXAMPLE, RIGHT, (0, 1, 2))
        result = path(EXAMPLE, LEFT, RIGHT)
        self.route(EXAMPLE, result, LEFT, RIGHT)
        self.assertEqual(len(result) - 1, 5)

    def test_three_bridge_branches_and_free_finals(self):
        rng = random.Random(2026112051)
        branches = set()
        for r in range(1, 7):
            n, m = r + 2, 2 * r + 2
            for _ in range(100):
                u = [list(rng.choices(range(12), k=m)) for _ in range(n)]
                for i in (r, r + 1):
                    u[i][0] = max(u[i])
                pool = set(range(1, m))
                anchors = []
                for i in range(r):
                    g = max(sorted(pool), key=lambda h: u[i][h])
                    anchors.append(g)
                    pool.remove(g)
                x = max(sorted(pool), key=lambda h: u[r][h])
                y = max(sorted(pool), key=lambda h: u[r + 1][h])
                if x == y:
                    continue
                rest = list(pool - {x, y})
                rng.shuffle(rest)  # arbitrary final assignments, not greedy ones
                tails = (x,) + tuple(rest)
                c = anchors[-1]
                branches.add(0 if u[r][c] >= u[r][x] else
                             1 if u[r + 1][c] >= u[r + 1][y] else 2)
                result = anchor_bridge(tuple(map(tuple, u)), tuple(anchors), tails, 0, x, y)
                self.route(u, result)
                self.assertLessEqual(len(result) - 1, 2 * r + 2)
                for a in result:
                    self.assertTrue(all(a[g] == i for i, g in enumerate(anchors[:-1])))
        self.assertEqual(branches, {0, 1, 2})

    def test_reduction_all_remainders(self):
        rng = random.Random(2026112052)
        moved = 0
        for n in range(3, 8):
            for r in range(1, n):
                for _ in range(20):
                    final = tuple(rng.sample(range(n), r))
                    u = tuple(tuple(Fraction(rng.randrange(12), rng.choice((1, 2, 7)))
                                    for _ in range(n + r)) for _ in range(n))
                    a = witness(u, final, rng)
                    result, b = singleton_reduction(u, a, final)
                    self.route(u, result, a, b)
                    greedy(u, b, final)
                    self.assertNotIn(b[0][0], final)
                    moved += len(result) > 1
        self.assertGreater(moved, 0)

    def test_complete_constructor_rationals_ties_and_labels(self):
        rng = random.Random(2026112053)
        for n, count in ((3, 30), (4, 30), (5, 220), (6, 12), (7, 6)):
            m = 2 * n - 2
            for trial in range(count):
                final = tuple(rng.sample(range(n), n - 2))
                u = tuple(tuple(Fraction(rng.randrange(8), rng.choice((1, 3, 11)))
                                if trial else Fraction(0) for _ in range(m))
                          for _ in range(n))
                a, b = witness(u, final, rng), witness(u, final, rng)
                greedy(u, a, final)
                greedy(u, b, final)
                self.route(u, path(u, a, b, final), a, b)

    def test_no_automatic_common_prefix_lift(self):
        rows = [list(row) + [0] * 5 for row in EXAMPLE]
        for i in range(5):
            rows[i][8 + i] = 2000
        for i in (3, 4):
            rows[i][0] = rows[i][10] = 1000
            rows[i][11] = rows[i][12] = 90
        u = tuple(map(tuple, rows))
        prefix = (0, 1, 2, 3, 4)
        a = ((3, 0), (0, 8), (1, 9), (2, 10), (4, 12),
             (3, 11), (0, 1), (1, 2), (2, 3), (4, 5), (0, 4), (1, 6), (2, 7))
        b = ((4, 0), (0, 8), (1, 9), (2, 10), (3, 11),
             (4, 12), (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (1, 6), (2, 7))
        for w in (a, b):
            remaining = set(range(13))
            for i, g in w:
                self.assertEqual(u[i][g], max(u[i][h] for h in remaining))
                remaining.remove(g)
        local = tuple(tuple(row[:8]) for row in u)
        route = anchor_bridge(local, (1, 2, 3), (4, 6, 7), 0, 4, 5)
        self.assertTrue(fair(u, route[0] + prefix))
        self.assertTrue(fair(u, route[-1] + prefix))
        self.assertTrue(any(not fair(u, state + prefix) for state in route))

    def test_refuse_wrong_domains(self):
        with self.assertRaises(ValueError):
            path(EXAMPLE, LEFT[:-1], RIGHT)
        with self.assertRaises(ValueError):
            path(EXAMPLE, LEFT, RIGHT, (0, 1))
        bad = list(EXAMPLE)
        bad[3] = (0,) * 8
        bad[4] = (0,) * 8
        bad[0] = (0,) * 7 + (-1,)
        with self.assertRaises(ValueError):
            anchor_bridge(tuple(bad), (1, 2, 3), (4, 6, 7), 0, 4, 5)


if __name__ == "__main__":
    unittest.main()
