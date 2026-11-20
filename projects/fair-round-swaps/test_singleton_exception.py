"""Original-deletion checks for arbitrary-singleton favorite acquisition."""
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

import singleton_exception as subject


def fair(u, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in other if g != removed) for removed in other)
               for i, row in enumerate(u) for other in bundles if other)


def check_route(test, u, route):
    for state in route:
        test.assertTrue(fair(u, state))
        test.assertEqual([state.count(i) for i in range(len(u))], [2] + [1] * (len(u) - 1))
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(len(a)) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((a[x], a[y]), (b[y], b[x]))


class SingletonExceptionTests(unittest.TestCase):
    def test_all_four_good_weak_binary_profiles(self):
        orders = [r for r in product(range(4), repeat=4)
                  if set(r) == set(range(max(r) + 1))]
        states = sorted(set(permutations((0, 0, 1, 2))))
        count = 0
        for a in orders:
            for b in product((0, 1), repeat=4):
                u = ((11, 0, 5, 1), a, b)
                live = [state for state in states if fair(u, state)]
                for state in live:
                    route = subject.favorite_path(u, state)
                    check_route(self, u, route)
                    h = max(range(4), key=lambda g: (a[g], -g))
                    self.assertEqual(route[-1][h], 1)
                    self.assertLessEqual(len(route) - 1, 3)
                    complete = subject.path(u, state, live[0])
                    self.assertEqual((complete[0], complete[-1]), (state, live[0]))
                    check_route(self, u, complete)
                    count += 1
        self.assertGreater(count, 9000)
        print(f"complete weak/binary four-good fair starts: {count}")

    def test_arbitrary_rows_and_both_favorite_locations(self):
        rng = Random(1731)
        locations, decreases, checked = set(), 0, 0
        for k in range(2, 10):
            m = k + 2
            for _ in range(80):
                a = rng.randrange(1, k + 1)
                u = [tuple(rng.randrange(11) for _ in range(m))]
                for i in range(1, k + 1):
                    if i == a:
                        u.append(tuple(Fraction(rng.randrange(20), rng.choice((1, 3))) for _ in range(m)))
                    else:
                        low = Fraction(rng.randrange(3), 7)
                        high = low + Fraction(rng.randrange(1, 9), 3)
                        u.append(tuple(rng.choice((low, high)) for _ in range(m)))
                live = []
                for _ in range(400):
                    state = [0, 0] + list(range(1, k + 1))
                    rng.shuffle(state)
                    state = tuple(state)
                    if fair(u, state):
                        live.append(state)
                    if len(live) == 2:
                        break
                self.assertEqual(len(live), 2)
                h = max(range(m), key=lambda g: (u[a][g], -g))
                locations.add('pair' if live[0][h] == 0 else 'self' if live[0][h] == a else 'binary')
                route = subject.favorite_path(u, live[0], a)
                self.assertEqual(route[-1][h], a)
                self.assertLessEqual(len(route) - 1, k + 1)
                values = [u[a][state.index(a)] for state in route]
                decreases += any(x > y for x, y in zip(values, values[1:]))
                check_route(self, u, route)
                complete = subject.path(u, *live, a)
                self.assertEqual((complete[0], complete[-1]), tuple(live))
                check_route(self, u, complete)
                checked += 1
        self.assertEqual(locations, {'pair', 'self', 'binary'})
        self.assertGreater(decreases, 0)
        print(f"arbitrary-size rational profiles: {checked}; nonmonotone favorite paths: {decreases}")

    def test_no_binary_recipient_and_tied_favorite(self):
        for row in ((0, 0, 0), (2, 7, 7), (7, 2, 7)):
            u = ((91, 1, 7), row)
            states = [state for state in set(permutations((0, 0, 1))) if fair(u, state)]
            for a, b in product(states, repeat=2):
                route = subject.path(u, a, b)
                check_route(self, u, route)
                self.assertEqual((route[0], route[-1]), (a, b))

    def test_nonmonotone_and_binary_donor_repairs(self):
        u = ((0,) * 4, (4, 3, 5, 2), (1, 0, 0, 1))
        route = subject.favorite_path(u, (1, 2, 0, 0))
        self.assertEqual([u[1][s.index(1)] for s in route], [4, 3, 5])
        for x in (0, 1):
            u = ((0,) * 5, (4, 5, 3, 2, 1), (0, 1, x, 1, 1), (0, 1, 0, 0, 1))
            route = subject.favorite_path(u, (1, 2, 3, 0, 0))
            check_route(self, u, route)
            self.assertEqual(route[-1][1], 1)
        u = ((0,) * 6, (5, 6, 4, 3, 2, 1), (0, 1, 0, 0, 1, 1),
             (0, 1, 0, 0, 0, 1), (0, 0, 1, 0, 0, 1))
        route = subject.favorite_path(u, (1, 2, 3, 4, 0, 0))
        check_route(self, u, route)
        self.assertEqual(route[-1][1], 1)

    def test_wrong_domain_and_actual_command(self):
        u = ((0,) * 5, (0, 1, 2, 3, 4), (0, 0, 1, 0, 1), (0,) * 5)
        state = (1, 2, 3, 0, 0)
        with self.assertRaisesRegex(ValueError, 'exceptional singleton'):
            subject.favorite_path(u, state, 0)
        with self.assertRaisesRegex(ValueError, 'at most two'):
            subject.favorite_path(u, state, 2)
        with self.assertRaises(ValueError):
            subject.favorite_path(u, (0,) * 5)
        with self.assertRaisesRegex(ValueError, 'exact nonnegative'):
            subject.favorite_path([[float(v) for v in row] for row in u], state)
        result = subprocess.run([sys.executable, '-S', str(Path(subject.__file__))],
                                capture_output=True, text=True, check=True)
        self.assertIn('"verified":', result.stdout)


if __name__ == '__main__':
    unittest.main()
