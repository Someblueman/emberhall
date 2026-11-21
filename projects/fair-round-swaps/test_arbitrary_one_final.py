"""Independent deletion, exchange, witness and fixed-prefix checks."""

from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from arbitrary_one_final import braid_example, padded_path, path, protected_path
from single_extra import isolated_family


def owners(w, m):
    a = [-1] * m
    for i, g in w:
        a[g] = i
    return tuple(a)


def witness(u, q, d, rng, prefix=()):
    n, m = len(u), len(u[0])
    result, goods = list(prefix), set(range(m)) - {g for _, g in prefix}
    order = rng.sample([i for i in range(n) if i not in {a for a, _ in prefix}], n-len(prefix))
    for _ in range(q-1):
        order += rng.sample(range(n), n)
    for i in order + [d]:
        best = max(u[i][g] for g in goods)
        g = rng.choice([g for g in sorted(goods) if u[i][g] == best])
        result.append((i, g))
        goods.remove(g)
    return tuple(result)


def check(test, u, left, right, route, prefix=()):
    n, m = len(u), len(u[0])
    for w in (left, right):
        remaining = set(range(m))
        for offset in range(0, m-1, n):
            test.assertEqual({i for i, _ in w[offset:offset+n]}, set(range(n)))
        for i, g in w:
            test.assertIn(g, remaining)
            test.assertEqual(u[i][g], max(u[i][h] for h in remaining))
            remaining.remove(g)
    test.assertEqual((route[0], route[-1]), (owners(left, m), owners(right, m)))
    sizes = tuple(route[0].count(i) for i in range(n))
    for a in route:
        test.assertEqual(tuple(a.count(i) for i in range(n)), sizes)
        for i, g in prefix:
            test.assertEqual(a[g], i)
        bundles = [[g for g in range(m) if a[g] == j] for j in range(n)]
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


class ArbitraryOneFinalTests(unittest.TestCase):
    def test_uncancelled_braids_and_fixed_prefixes(self):
        for n in (3, 4, 5, 6, 8, 12):
            for q in (2, 3, 4):
                u, left, right = braid_example(n, q)
                for count in sorted({0, 1, n-2}):
                    prefix = left[1:1+count]
                    ll = prefix + (left[0],) + left[1+count:]
                    rr = prefix + (right[0],) + right[1+count:]
                    check(self, u, ll, rr, path(u, ll, rr), prefix)

    def test_random_rational_and_zero_profiles_all_labels(self):
        rng = random.Random(2026112027)
        for n in range(2, 9):
            for q in (1, 2, 3):
                for case in range(6):
                    m, d = n*q+1, rng.randrange(n)
                    u = tuple(tuple(Fraction(rng.randrange(5) if case else 0, 7)
                                    for _ in range(m)) for _ in range(n))
                    left = witness(u, q, d, rng)
                    prefix = left[:case % (n+1)]
                    right = witness(u, q, d, rng, prefix)
                    # The accepted one-extra base is ambient, not prefix-preserving.
                    check(self, u, left, right, path(u, left, right, d), prefix if q > 1 else ())

    def test_protected_bridge_with_opposed_carrier_rankings(self):
        rng = random.Random(17)
        for n in range(3, 11):
            rows = [[rng.randrange(9) for _ in range(n+1)] for _ in range(n)]
            rows[-2] = [100] + list(range(1, n+1))
            rows[-1] = [100] + list(range(n, 0, -1))
            u = tuple(map(tuple, rows))
            left = witness(u, 1, 0, rng, ((n-2, 0),))
            right = witness(u, 1, 0, rng, ((n-1, 0),))
            route = protected_path(u, owners(left, n+1), owners(right, n+1), (n-2, n-1), 0)
            check(self, u, left, right, route)
            self.assertTrue(all(a[0] in (n-2, n-1) for a in route))

    def test_rejects_missing_padding_dominance(self):
        u = ((0, 0, 20, 0, 0, 0, 0), (10, 1, 0, 0, 0, 0, 0),
             (20, 0, 0, 5, 0, 0, 0))
        with self.assertRaisesRegex(ValueError, 'do not dominate'):
            padded_path(u, ((2, 0), (1, 1), (0, 2)), (3, 4, 5, 6),
                        (1, 0, 0, 2), (2, 0, 0, 1), (1, 2))

    def test_tied_last_pick_across_rounds(self):
        u = ((0,) * 9,) * 4
        prefix = ((0, 0), (1, 1), (2, 2))
        left = prefix + ((3, 3), (0, 4), (1, 5), (2, 6), (3, 7), (0, 8))
        right = prefix + ((3, 4), (3, 3), (0, 5), (1, 6), (2, 7), (0, 8))
        check(self, u, left, right, path(u, left, right), prefix)

    def test_protected_api_does_not_assume_all_fibers_connected(self):
        base, a, _ = isolated_family(5)
        u = tuple(row + (max(row) + 1,) for row in base) + ((0,) * 6 + (1,),)
        a = a + (5,)
        with self.assertRaisesRegex(ValueError, 'requires a safe spare'):
            protected_path(u, a, a, (1, 5), 6)

    def test_bad_endpoint_and_remainder(self):
        u, left, right = braid_example()
        with self.assertRaisesRegex(ValueError, 'maximizer'):
            path(u, ((left[0][0], 1), (left[1][0], 0)) + left[2:], right)
        with self.assertRaisesRegex(ValueError, 'n.q.1'):
            path(tuple(row[:-1] for row in u), left, right)

    def test_real_command(self):
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('arbitrary_one_final.py'))],
                             capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual((result['agents'], result['goods'], result['exchanges']), (6, 19, 3))


if __name__ == '__main__':
    unittest.main()
