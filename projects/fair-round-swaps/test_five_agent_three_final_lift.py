"""Independent deletion and exchange checks for the arbitrary-round constructor."""

from fractions import Fraction
import random
import unittest

from five_agent_three_final_lift import example, path
from five_agent_eight import EXAMPLE
from test_five_agent_protected import fair


def witness(u, final, rng, prefix=()):
    remaining = set(range(len(u[0])))
    result = list(prefix)
    for _, g in prefix:
        remaining.remove(g)
    rounds = len(u[0]) // 5
    for r in range(rounds):
        used = {i for i, _ in prefix[5 * r:5 * r + 5]}
        order = [i for i in range(5) if i not in used]
        rng.shuffle(order)
        for i in order:
            best = max(u[i][g] for g in remaining)
            g = rng.choice(sorted(g for g in remaining if u[i][g] == best))
            result.append((i, g))
            remaining.remove(g)
    order = list(final)
    rng.shuffle(order)
    for i in order:
        best = max(u[i][g] for g in remaining)
        g = rng.choice(sorted(g for g in remaining if u[i][g] == best))
        result.append((i, g))
        remaining.remove(g)
    return tuple(result)


def owners(w, m):
    a = [-1] * m
    for i, g in w:
        a[g] = i
    return tuple(a)


class ThreeFinalLiftTests(unittest.TestCase):
    def route(self, u, a, b, result):
        self.assertEqual(result[0], owners(a, len(u[0])))
        self.assertEqual(result[-1], owners(b, len(u[0])))
        sizes = tuple(result[0].count(i) for i in range(5))
        for state in result:
            self.assertEqual(tuple(state.count(i) for i in range(5)), sizes)
            self.assertTrue(fair(u, state))
        for s, t in zip(result, result[1:]):
            changed = [g for g in range(len(s)) if s[g] != t[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((s[x], s[y]), (t[y], t[x]))

    def test_uncancelled_braids_through_eight_rounds(self):
        for q in (1, 2, 3, 5, 8):
            u, a, b = example(q)
            result = path(u, a, b)
            self.route(u, a, b, result)
            if q > 1:  # The one-round base is deliberately ambient.
                self.assertTrue(all(state[0] in (3, 4) for state in result))

    def test_rational_endpoints_and_all_zero_ties(self):
        rng = random.Random(2026112059)
        for q in range(1, 6):
            for trial in range(12):
                u = tuple(tuple(Fraction(rng.randrange(9), rng.choice((1, 3, 7)))
                                if trial else Fraction(0) for _ in range(5 * q + 3))
                          for _ in range(5))
                final = tuple(rng.sample(range(5), 3))
                a, b = witness(u, final, rng), witness(u, final, rng)
                self.route(u, a, b, path(u, a, b, final))

    def test_fixed_first_round_and_partial_prefix(self):
        rng = random.Random(2026112060)
        for q in (2, 3, 4):
            for length in (1, 2, 4, 5):
                u = tuple(tuple(rng.randrange(8) for _ in range(5 * q + 3)) for _ in range(5))
                initial = witness(u, (0, 1, 2), rng)
                prefix = initial[:length]
                a = witness(u, (0, 1, 2), rng, prefix)
                b = witness(u, (0, 1, 2), rng, prefix)
                result = path(u, a, b)
                self.route(u, a, b, result)
                self.assertTrue(all(state[g] == i for state in result for i, g in prefix))

    def test_relabelled_uncancelled_braid(self):
        u, a, b = example(4)
        labels = (2, 4, 1, 0, 3)
        rows = [None] * 5
        for i, row in enumerate(u):
            rows[labels[i]] = row
        a = tuple((labels[i], g) for i, g in a)
        b = tuple((labels[i], g) for i, g in b)
        self.route(tuple(rows), a, b, path(tuple(rows), a, b, tuple(labels[:3])))

    def test_last_agent_tie_across_round_boundary(self):
        u = ((0,) * 13,) * 5
        prefix = tuple((i, i) for i in range(4))
        rest = ((0, 6), (1, 7), (2, 8), (3, 9), (0, 10), (1, 11), (2, 12))
        a = prefix + ((4, 4), (4, 5)) + rest
        b = prefix + ((4, 5), (4, 4)) + rest
        result = path(u, a, b)
        self.route(u, a, b, result)
        self.assertEqual(len(result), 1)

    def test_original_thirteen_good_padding_failure(self):
        u = [list(row) + [0] * 5 for row in EXAMPLE]
        for i in range(5):
            u[i][8 + i] = 2000
        for i in (3, 4):
            u[i][0] = u[i][10] = 1000
            u[i][11] = u[i][12] = 90
        common = ((0, 8), (1, 9), (2, 10))
        anchors = ((0, 1), (1, 2), (2, 3))
        a = ((3, 0),) + common + ((4, 12), (3, 11)) + anchors + ((4, 5), (0, 4), (1, 6), (2, 7))
        b = ((4, 0),) + common + ((3, 11), (4, 12)) + anchors + ((3, 4), (0, 5), (1, 6), (2, 7))
        u = tuple(map(tuple, u))
        self.route(u, a, b, path(u, a, b))

    def test_invalid_endpoints_and_remainders(self):
        u, a, b = example(2)
        with self.assertRaises(ValueError):
            path(u, a[:-1], b)
        with self.assertRaises(ValueError):
            path(u, a, b, (0, 1))
        with self.assertRaises(ValueError):
            path(tuple(row[:-1] for row in u), a, b)
        bad = ((a[0][0], a[-1][1]),) + a[1:-1] + ((a[-1][0], a[0][1]),)
        with self.assertRaises(ValueError):
            path(u, bad, b)


if __name__ == '__main__':
    unittest.main()
