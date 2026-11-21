"""Independently check the obstruction and compare endpoint recognition exhaustively."""

from fractions import Fraction
from itertools import combinations, permutations
import random
import unittest

from five_agent_frontier import (EXAMPLE, ISOLATED, TWO_STATE_COMPONENT,
                                 TWO_STATE_PROFILE, certificate, greedy_witness)
from swaps import picking_outcomes, rounds_for


def fair(u, a):
    n = len(u)
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(n)]
    return all(any(sum(u[i][g] for g in bundles[i]) >=
                       sum(u[i][g] for g in bundles[j] if g != deleted)
                       for deleted in bundles[j])
               for i in range(n) for j in range(n) if i != j)


def valid_witness(case, u, a, witness):
    n, m = len(u), len(u[0])
    remaining = set(range(m))
    case.assertEqual({i for i, _ in witness[:n]}, set(range(n)))
    case.assertEqual({i for i, _ in witness[n:]}, {i for i in range(n) if a.count(i) == 2})
    case.assertEqual(len(witness), m)
    for i, g in witness:
        case.assertEqual(a[g], i)
        case.assertIn(g, remaining)
        case.assertEqual(u[i][g], max(u[i][h] for h in remaining))
        remaining.remove(g)
    case.assertFalse(remaining)


class FrontierTests(unittest.TestCase):
    def test_all_nineteen_isolated_neighbors_with_independent_deletions(self):
        self.assertTrue(fair(EXAMPLE, ISOLATED))
        count = 0
        for x, y in combinations(range(7), 2):
            if ISOLATED[x] == ISOLATED[y]:
                continue
            b = list(ISOLATED)
            b[x], b[y] = b[y], b[x]
            self.assertFalse(fair(EXAMPLE, b))
            count += 1
        self.assertEqual(count, 19)
        self.assertIsNone(greedy_witness(EXAMPLE, ISOLATED))
        report = certificate()
        self.assertEqual(report['component_sizes'], [1, 227])
        self.assertEqual(report['protected_component_sizes'], [1, 89])
        self.assertEqual(report['greedy_states'], 50)
        self.assertEqual(report['greedy_per_component'], [0, 50])

    def test_recognizer_matches_all_greedy_outcomes_on_fresh_profiles(self):
        rng = random.Random(2026112033)
        cases = [(n, r) for n in range(2, 5) for r in range(n)] + [(5, 2)]
        for n, r in cases:
            sizes = (2,) * r + (1,) * (n - r)
            labels = tuple(i for i, size in enumerate(sizes) for _ in range(size))
            states = set(permutations(labels))
            m = len(labels)
            for sample in range(6):
                u = tuple(tuple(Fraction(rng.randrange(6), rng.randrange(1, 4))
                                for _ in range(m)) for _ in range(n))
                if sample == 0:
                    u = ((0,) * m,) * n
                expected = set(picking_outcomes(u, rounds_for(n, m, tuple(range(r)))))
                found = set()
                for a in states:
                    w = greedy_witness(u, a)
                    if w is not None:
                        valid_witness(self, u, a, w)
                        found.add(a)
                self.assertEqual(found, expected, (n, r, u))

    def test_both_precedence_graphs_are_necessary(self):
        first_cycle = ((1, 2, 0, 0), (0, 1, 2, 0), (2, 0, 1, 0))
        self.assertTrue(fair(first_cycle, (0, 1, 2, 0)))
        self.assertIsNone(greedy_witness(first_cycle, (0, 1, 2, 0)))
        last_cycle = ((100, 100, 100, 100, 1, 2),
                      (100, 100, 100, 100, 2, 1),
                      (100, 100, 100, 100, 0, 0),
                      (100, 100, 100, 100, 0, 0))
        self.assertTrue(fair(last_cycle, (0, 1, 2, 3, 0, 1)))
        self.assertIsNone(greedy_witness(last_cycle, (0, 1, 2, 3, 0, 1)))

    def test_deleting_isolated_vertices_does_not_restore_connectivity(self):
        a, b = TWO_STATE_COMPONENT
        self.assertTrue(fair(TWO_STATE_PROFILE, a))
        self.assertTrue(fair(TWO_STATE_PROFILE, b))
        for current in (a, b):
            self.assertIsNone(greedy_witness(TWO_STATE_PROFILE, current))
            allowed_neighbors = []
            for x, y in combinations(range(6), 2):
                if current[x] == current[y]:
                    continue
                candidate = list(current)
                candidate[x], candidate[y] = candidate[y], candidate[x]
                if fair(TWO_STATE_PROFILE, candidate):
                    allowed_neighbors.append(tuple(candidate))
            self.assertEqual(allowed_neighbors, [b if current == a else a])
        result = certificate()['nonisolated_boundary']
        self.assertEqual(result['component_sizes'], [2, 41])
        self.assertEqual(result['greedy_per_component'], [0, 7])

    def test_invalid_shape_and_values(self):
        with self.assertRaises(ValueError):
            greedy_witness(EXAMPLE, (0,) * 7)
        with self.assertRaises(ValueError):
            greedy_witness(EXAMPLE, ISOLATED[:-1] + (True,))
        with self.assertRaises(ValueError):
            greedy_witness(((0, 0), (0, 0)), (0, 7))


if __name__ == '__main__':
    unittest.main()
