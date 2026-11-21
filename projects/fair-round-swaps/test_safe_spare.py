"""Independent checks for the safe-spare constructive component lemma."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from safe_spare import cycle_example, normalize, path, safe_spares
from single_extra import isolated_family
from swaps import picking_outcomes, rounds_for, states_with_sizes


def fair_by_deletion(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                       sum(row[g] for g in bundle if g != removed)
                       for removed in [None] + bundle)
               for i, row in enumerate(u) for bundle in bundles)


def check_route(test, u, route):
    sizes = tuple(route[0].count(i) for i in range(len(u)))
    for a in route:
        test.assertTrue(fair_by_deletion(u, a))
        test.assertEqual(tuple(a.count(i) for i in range(len(u))), sizes)
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(len(a)) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((a[x], a[y]), (b[y], b[x]))


def check_witness(test, u, a, witness):
    n = len(u)
    test.assertEqual(set(i for i, _ in witness[:n]), set(range(n)))
    remaining = set(range(n + 1))
    for i, g in witness:
        test.assertIn(g, remaining)
        test.assertEqual(a[g], i)
        test.assertEqual(u[i][g], max(u[i][h] for h in remaining))
        remaining.remove(g)
    test.assertFalse(remaining)
    test.assertEqual(a.count(witness[-1][0]), 2)


class SafeSpareTests(unittest.TestCase):
    def test_binary_singletons_exhaustively(self):
        count = 0
        for values in product((0, 1), repeat=8):
            u = ((2, 0, 3, 1), values[:4], values[4:])
            for a in states_with_sizes((2, 1, 1)):
                if safe_spares(u, a):
                    route, witness = normalize(u, a)
                    check_route(self, u, route)
                    check_witness(self, u, route[-1], witness)
                    count += 1
        # Per allocation: either spare safe gives 12^2 profiles; both give 10^2.
        self.assertEqual(count, 12 * (2 * 12**2 - 10**2))

    def test_long_cycles_and_nonzero_double_recipient(self):
        for n in (3, 4, 6, 12, 30):
            u, a = cycle_example(n)
            # Move the double recipient from 0 to the last agent.
            roles = tuple(range(1, n)) + (0,)
            inverse = {old: new for new, old in enumerate(roles)}
            u = tuple(u[i] for i in roles)
            a = tuple(inverse[i] for i in a)
            route, witness = normalize(u, a)
            self.assertEqual(len(route) - 1, n)
            check_route(self, u, route)
            check_witness(self, u, route[-1], witness)
            if n <= 4:
                self.assertNotIn(a, picking_outcomes(u, rounds_for(n, n + 1, (n - 1,))))

    def test_variable_spare_improvement_chain(self):
        n = 9
        rows = [tuple(range(n + 1))]
        for i in range(1, n):
            rows.append(tuple(10 if g == i else 0 for g in range(n + 1)))
        u, a = tuple(rows), (0, 0) + tuple(range(1, n))
        route, witness = normalize(u, a)
        self.assertEqual(len(route) - 1, n - 1)
        self.assertTrue(all(state[0] == 0 for state in route))
        check_route(self, u, route)
        check_witness(self, u, route[-1], witness)

    def test_rational_paths_and_bound(self):
        rng = random.Random(2026112023)
        for n in range(2, 11):
            for _ in range(25):
                rows = [tuple(Fraction(rng.randrange(13), 7) for _ in range(n + 1))]
                rows += [(Fraction(0),) + tuple(Fraction(rng.randrange(13), 7)
                                               for _ in range(n)) for _ in range(n - 1)]
                u, a = tuple(rows), (0, 0) + tuple(range(1, n))
                route, witness = normalize(u, a)
                self.assertLessEqual(len(route) - 1, 2 * n * (n - 1))
                check_route(self, u, route)
                check_witness(self, u, route[-1], witness)
                if n <= 6:
                    joined = path(u, a, route[-1])
                    self.assertEqual((joined[0], joined[-1]), (a, route[-1]))
                    check_route(self, u, joined)

    def test_sufficient_condition_is_not_necessity(self):
        u = ((0, 0, 0, 0), (4, 1, 2, 0), (1, 4, 0, 2))
        a, neighbor = (0, 0, 1, 2), (1, 0, 0, 2)
        self.assertEqual(safe_spares(u, a), ())
        check_route(self, u, [a, neighbor])
        with self.assertRaisesRegex(ValueError, 'requires a safe spare'):
            normalize(u, a)
        self.assertTrue(safe_spares(u, neighbor))
        for n in (5, 6, 10):
            for strict in (False, True):
                u, a, _ = isolated_family(n, strict=strict)
                self.assertEqual(safe_spares(u, a), ())
                with self.assertRaisesRegex(ValueError, 'requires a safe spare'):
                    normalize(u, a)

    def test_real_command(self):
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('safe_spare.py'))],
                             capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(result['exchanges'], 6)
        self.assertEqual(result['initial_safe_spares'], [0, 1])


if __name__ == '__main__':
    unittest.main()
