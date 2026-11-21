"""Independent one-round witness, deletion and exchange validation."""

from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from arbitrary_single_round import path
from five_agent_eight import EXAMPLE, LEFT, RIGHT


def greedy(u, final, rng):
    order = rng.sample(range(len(u)), len(u)) + rng.sample(final, len(final))
    remaining, result = set(range(len(u[0]))), []
    for i in order:
        best = max(u[i][g] for g in remaining)
        g = rng.choice([g for g in sorted(remaining) if u[i][g] == best])
        result.append((i, g))
        remaining.remove(g)
    return tuple(result)


def check(test, u, final, left, right, route):
    n, m = len(u), len(u[0])
    endpoints = []
    for w in (left, right):
        test.assertEqual({i for i, _ in w[:n]}, set(range(n)))
        test.assertEqual({i for i, _ in w[n:]}, set(final))
        remaining, a = set(range(m)), [-1] * m
        for i, g in w:
            test.assertIn(g, remaining)
            test.assertEqual(u[i][g], max(u[i][h] for h in remaining))
            remaining.remove(g)
            a[g] = i
        endpoints.append(tuple(a))
    test.assertEqual((route[0], route[-1]), tuple(endpoints))
    for a in route:
        test.assertEqual(tuple(a.count(i) for i in range(n)),
                         tuple(2 if i in final else 1 for i in range(n)))
        bundles = [[g for g in range(m) if a[g] == i] for i in range(n)]
        for i, row in enumerate(u):
            own = sum(row[g] for g in bundles[i])
            for b in bundles:
                test.assertTrue(any(own >= sum(row[g] for g in b if g != h)
                                    for h in [None] + b))
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(m) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((a[x], a[y]), (b[y], b[x]))


class SingleRoundTests(unittest.TestCase):
    def test_every_remainder_through_ten_agents(self):
        rng = random.Random(2026112037)
        count = 0
        for n in range(2, 11):
            for r in range(1, n):
                for trial in range(5):
                    final = tuple(sorted(rng.sample(range(n), r)))
                    u = tuple(tuple(Fraction(rng.randrange(9) if trial else 0, 11)
                                    for _ in range(n+r)) for _ in range(n))
                    left, right = greedy(u, final, rng), greedy(u, final, rng)
                    check(self, u, final, left, right, path(u, left, right, final))
                    count += 1
        self.assertEqual(count, 225)

    def test_loan_bridge_with_extra_singleton_observers(self):
        # Each new singleton values g above its own good, and every other
        # residual good below it. The bridge really lends g to a double.
        for extra in (1, 2, 4):
            n = 5 + extra
            u = tuple(row + (0,) * extra for row in EXAMPLE)
            u += tuple((1000,) + (0,) * 7 + tuple(500 if j == k else 0 for j in range(extra))
                       for k in range(extra))
            fixed = tuple((5+k, 8+k) for k in range(extra))
            left = (LEFT[0],) + fixed + LEFT[1:]
            right = (RIGHT[0],) + fixed + RIGHT[1:]
            route = path(u, left, right, (0, 1, 2))
            check(self, u, (0, 1, 2), left, right, route)
            self.assertTrue(any(a[0] in (0, 1, 2) for a in route))
            self.assertEqual(len(u), n)

    def test_non_greedy_and_multiple_complete_rounds_rejected(self):
        with self.assertRaisesRegex(ValueError, 'maximizer'):
            path(EXAMPLE, ((LEFT[0][0], 1), (LEFT[1][0], 0)) + LEFT[2:], RIGHT, (0, 1, 2))
        with self.assertRaisesRegex(ValueError, 'one complete'):
            path(((0,) * 13,) * 5, (), (), (0, 1, 2))
        with self.assertRaisesRegex(ValueError, 'final round'):
            path(EXAMPLE, LEFT, RIGHT, (0, 1))

    def test_real_command(self):
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('arbitrary_single_round.py'))],
                             capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual((result['agents'], result['goods']), (6, 8))
        self.assertEqual(result['exchanges'], 6)


if __name__ == '__main__':
    unittest.main()
