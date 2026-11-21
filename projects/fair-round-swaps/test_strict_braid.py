"""Check refinement against literal EF1 deletions on complete small domains."""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from strict_braid import (FRONTIER, balanced_report, bounded_profile, endpoints,
                          example, frontier_path, refinement_report, strict_braid)
from swaps import picking_outcomes, rounds_for, states_with_sizes


def fair(u, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
    return all(sum(row[g] for g in bundles[i]) >= min(
        sum(row[g] for g in bundle if g != removed) for removed in bundle)
        for i, row in enumerate(u) for bundle in bundles)


def independent_signs(row):
    # Different enumeration from the production form generator.
    result = []
    for target in range(len(row)):
        others = [g for g in range(len(row)) if g != target]
        for count in (1, 2):
            result.extend(sum(row[g] for g in own) - row[target]
                          for own in combinations(others, count))
    return result


class StrictBraidTests(unittest.TestCase):
    def test_balanced_graphs_and_greedy_witnesses_are_identical(self):
        rng = random.Random(2026112054)
        for sizes in ((1, 1, 1), (2, 2, 2), (3, 2, 2), (3, 3, 2), (5, 4)):
            n, m = len(sizes), sum(sizes)
            for trial in range(3):
                u = tuple(tuple(Fraction(rng.randrange(5), 10**40+7) if trial else 0
                                for _ in range(m)) for _ in range(n))
                v = bounded_profile(u, sizes)
                balanced_report(u, v, sizes)
                for a in states_with_sizes(sizes):
                    self.assertEqual(fair(u, a), fair(v, a), (sizes, a))
                for old, new in zip(u, v):
                    self.assertEqual([[a >= b for b in old] for a in old],
                                     [[a >= b for b in new] for a in new])
                if sizes == (3, 2, 2):
                    rs = rounds_for(n, m, (0,))
                    self.assertEqual(picking_outcomes(u, rs), picking_outcomes(v, rs))
        for sizes in ((4, 2, 1), (3, 3, 0), (3, 2)):
            with self.assertRaises(ValueError):
                bounded_profile(((0,)*7,)*3, sizes)
        with self.assertRaisesRegex(ValueError, 'comparison budget'):
            bounded_profile(((0,)*7,)*3, (3, 2, 2), max_forms=1)

    def test_retained_strict_frontier(self):
        route = frontier_path()
        self.assertEqual(len(route)-1, 7)
        self.assertEqual(max(map(max, FRONTIER)), 297)
        for u in (FRONTIER, strict_braid(FRONTIER)):
            for a in route:
                self.assertTrue(fair(u, a))
            for a, b in zip(route, route[1:]):
                changed = [g for g in range(12) if a[g] != b[g]]
                self.assertEqual(len(changed), 2)
                self.assertEqual(tuple(a[g] for g in changed), tuple(b[g] for g in reversed(changed)))

    def test_complete_small_graph_inclusion(self):
        total = lost = 0
        for r in (1, 2, 3):
            n, m = r+2, 2*r+2
            states = states_with_sizes((2,)*r+(1, 1))
            for u in (example(r), ((0,)*m,)*n, ((Fraction(1, 7),)*m,)*n):
                v = strict_braid(u)
                self.assertTrue(all(fair(u, a) and fair(v, a) for a in endpoints(r)))
                for a in states:
                    old, new = fair(u, a), fair(v, a)
                    self.assertFalse(new and not old, (r, a))
                    lost += old and not new
                    total += 1
        self.assertEqual(total, 15696)
        self.assertGreater(lost, 0)  # Refinement need not preserve every fair state.

    def test_large_rationals_and_strict_cell(self):
        rng = random.Random(2026112052)
        for r in range(1, 7):
            u = tuple(tuple(Fraction(v * (10**40+7), 10**50 + i+1) for v in row)
                      for i, row in enumerate(example(r)))
            v = strict_braid(u)
            report = refinement_report(u, v)
            self.assertEqual(report['integer_bound'], 2**len(u[0]))
            for old, new in zip(u, v):
                self.assertEqual(len(set(new)), len(new))
                self.assertTrue(all(type(x) is int and 1 <= x <= report['integer_bound'] for x in new))
                original, refined = independent_signs(old), independent_signs(new)
                self.assertTrue(all(b and (not a or (a > 0) == (b > 0))
                                    for a, b in zip(original, refined)))
                for _ in range(5):
                    nearby = tuple(x + Fraction(rng.choice((-1, 1)), 4) for x in new)
                    perturbed = independent_signs(nearby)
                    self.assertTrue(all((a > 0) == (b > 0) for a, b in zip(refined, perturbed)))

    def test_refinement_is_not_a_connectivity_verdict(self):
        u = ((0,)*6,)*4
        v = strict_braid(u)
        states = states_with_sizes((2, 2, 1, 1))
        self.assertTrue(all(fair(u, a) for a in states))
        self.assertFalse(all(fair(v, a) for a in states))
        changed = [list(row) for row in v]
        changed[0] = [1]*6
        with self.assertRaises(ValueError):
            refinement_report(u, tuple(map(tuple, changed)))

    def test_varied_sign_cells_and_forged_refinement(self):
        rng = random.Random(2026112053)
        for r in range(1, 6):
            m = 2*r+2
            for _ in range(10):
                u = [[Fraction(rng.randrange(30), rng.choice((1, 3, 17)))
                      for _ in range(m)] for _ in range(r+2)]
                for i in range(r):
                    u[i][i+1] = max(u[i][i+1:])
                for i, best in ((r, r+1), (r+1, r+2)):
                    u[i][best] = max(u[i][r+1:])
                    u[i][0] = max(u[i])
                u = tuple(map(tuple, u))
                v = strict_braid(u)
                for old, new in zip(u, v):
                    self.assertTrue(all(b and (not a or (a > 0) == (b > 0)) for a, b
                                        in zip(independent_signs(old), independent_signs(new))))
        u = example(2)
        bad = [list(row) for row in strict_braid(u)]
        bad[0][0] = 64  # Within the bound and free of anchor constraints; reverses signs.
        with self.assertRaises(ValueError):
            refinement_report(u, tuple(map(tuple, bad)))

    def test_input_boundaries_and_actual_command(self):
        with self.assertRaises(ValueError):
            strict_braid(((0,)*6,)*3)
        with self.assertRaises(ValueError):
            strict_braid(((0.0,)*6,)*4)
        with self.assertRaises(ValueError):
            strict_braid(((0,)*6, (0,)*5, (0,)*6, (0,)*6))
        for i, g in ((0, 5), (2, 1), (3, 1)):
            u = [list(row) for row in example(2)]
            u[i][g] = 100
            with self.assertRaises(ValueError):
                strict_braid(tuple(map(tuple, u)))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'profile.json'
            path.write_text(json.dumps([[str(Fraction(v, 3)) for v in row] for row in example(5)]))
            result = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name('strict_braid.py')),
                                     '--input', str(path)], check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
            self.assertEqual((data['goods'], data['integer_bound'], data['comparisons_checked']),
                             (12, 4096, 5082))
            self.assertIn('not decided', data['scope'])
            generic = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name('strict_braid.py')),
                                      '--input', str(path), '--sizes', '2,2,2,2,2,1,1'],
                                     check=True, capture_output=True, text=True)
            self.assertIn('same entire EF1 graph', json.loads(generic.stdout)['scope'])
            path.write_text('[[0.5]]')
            result = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name('strict_braid.py')),
                                     '--input', str(path)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('integers or rational strings', result.stderr)


if __name__ == '__main__':
    unittest.main()
