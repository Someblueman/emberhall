"""Check the construction against literal deletion, including nongreedy inputs."""
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

import binary_one_pair as subject
from single_extra import greedy_witness


def literal_fair(u, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in bundle if g != removed) for removed in bundle)
               for i, row in enumerate(u) for bundle in bundles if bundle)


def assert_route(test, u, route):
    sizes = sorted(route[0]).copy()
    for state in route:
        test.assertEqual(sorted(state), sizes)
        test.assertTrue(literal_fair(u, state))
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(len(a)) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((a[x], a[y]), (b[y], b[x]))


class BinaryOnePairTests(unittest.TestCase):
    def check_normalization(self, u, start):
        route = subject.normalize(u, start)
        assert_route(self, u, route)
        bits = subject.reduced_profile(u)
        initial = sum(bits[i][start.index(i)] for i in range(1, len(u)))
        self.assertLessEqual(len(route) - 1, len(u) - 1 - initial)
        for a, b in zip(route, route[1:]):
            before = [bits[i][a.index(i)] for i in range(1, len(u))]
            after = [bits[i][b.index(i)] for i in range(1, len(u))]
            self.assertTrue(all(x <= y for x, y in zip(before, after)))
            self.assertGreater(sum(after), sum(before))
        witness = subject.normal_witness(u, route[-1])
        remaining = set(range(len(start)))
        owners = [-1] * len(start)
        for i, g in witness:
            self.assertIn(g, remaining)
            self.assertEqual(bits[i][g], max(bits[i][h] for h in remaining))
            remaining.remove(g)
            owners[g] = i
        self.assertFalse(remaining)
        self.assertEqual(tuple(owners), route[-1])
        return route

    def test_every_four_good_binary_profile_and_fair_start(self):
        states = sorted(set(permutations((0, 0, 1, 2))))
        checked = 0
        for a, b in product(product((0, 1), repeat=4), repeat=2):
            u = ((17, 2, 9, 0), a, b)
            fair = [state for state in states if literal_fair(u, state)]
            for start in fair:
                self.check_normalization(u, start)
                route = subject.path(u, start, fair[0])
                self.assertEqual((route[0], route[-1]), (start, fair[0]))
                assert_route(self, u, route)
                checked += 1
        self.assertEqual(checked, 2352)

    def test_large_rational_and_constant_rows(self):
        rng = Random(20261120127)
        for k in (3, 5, 8, 15, 30):
            m = k + 2
            start = tuple(range(1, k + 1)) + (0, 0)
            u = [tuple(rng.randrange(20) for _ in range(m))]
            for i in range(k):
                bits = [rng.randrange(2) for _ in range(m)]
                bits[i] = 0
                if bits[k] and bits[k + 1]:
                    bits[k + rng.randrange(2)] = 0
                low = Fraction(i % 4, 7)
                high = low + Fraction(i + 1, 3)
                u.append(tuple(high if bit else low for bit in bits))
            self.check_normalization(tuple(u), start)
        u = ((5,) * 6, (0,) * 6, (7,) * 6, (0,) * 6, (1,) * 6)
        self.check_normalization(u, (0, 1, 2, 0, 3, 4))
        # Both pair goods are already safe; only low-to-low improvements remain.
        u = ((9,) * 5, (0, 1, 0, 0, 0), (0, 0, 1, 0, 0), (1, 0, 0, 0, 0))
        route = self.check_normalization(u, (1, 2, 3, 0, 0))
        self.assertEqual(len(route) - 1, 2)
        self.assertTrue(all(state[-2:] == (0, 0) for state in route))

    def test_arbitrary_nongreedy_endpoints(self):
        rng = Random(127)
        checked = 0
        for k in (3, 4, 5, 6):
            m = k + 2
            for _ in range(12):
                u = [tuple(rng.randrange(10) for _ in range(m))]
                u.extend(tuple(rng.randrange(2) for _ in range(m)) for _ in range(k))
                starts = []
                for _ in range(300):
                    state = [0, 0] + list(range(1, k + 1))
                    rng.shuffle(state)
                    state = tuple(state)
                    if literal_fair(u, state):
                        starts.append(state)
                    if len(starts) == 2:
                        break
                self.assertEqual(len(starts), 2)
                route = subject.path(u, *starts)
                assert_route(self, u, route)
                self.assertEqual((route[0], route[-1]), tuple(starts))
                checked += 1
        self.assertEqual(checked, 48)

    def test_nongreedy_examples_and_actual_command(self):
        for k in (2, 4, 6, 8):
            u, start, target = subject.example(k)
            self.assertIsNone(greedy_witness(u, start))
            route = self.check_normalization(u, start)
            self.assertLessEqual(len(route) - 1, k)
            assert_route(self, u, subject.path(u, start, target))
        result = subprocess.run([sys.executable, '-S', str(Path(subject.__file__))],
                                capture_output=True, text=True, check=True)
        self.assertIn('"start_normalization_swaps": 6', result.stdout)
        self.assertIn('"verified":', result.stdout)

    def test_reject_wrong_domain(self):
        u, start, _ = subject.example(4)
        bad = list(u)
        bad[1] = (0, 1, 2, 0, 1, 2)
        with self.assertRaisesRegex(ValueError, 'at most two'):
            subject.normalize(bad, start)
        with self.assertRaisesRegex(ValueError, 'exact nonnegative'):
            subject.normalize([[float(v) for v in row] for row in u], start)
        with self.assertRaises(ValueError):
            subject.normalize(u, (0,) * len(start))
        changed = tuple(1 if x == 0 else 0 if x == 1 else x for x in start)
        with self.assertRaisesRegex(ValueError, 'recipient zero'):
            subject.normalize(u, changed)
        with self.assertRaisesRegex(ValueError, 'start must be EF1'):
            subject.normalize(((0,) * 4, (0, 0, 1, 1), (0,) * 4), (1, 2, 0, 0))


if __name__ == '__main__':
    unittest.main()
