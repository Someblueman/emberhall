"""Independent literal pair/neighbor oracles for the sparse reduction."""
from itertools import combinations, product
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import t2661_joint_residue as m


def vertices(lengths, holes):
    return [(None, 0)]+[(a, d) for a, L in enumerate(lengths) for d in range(1, L+1) if (a, d) not in holes]


def distance(u, v):
    a, d = u
    b, e = v
    return abs(d-e) if a == b else d+e


def bins(verts, p):
    result = [0]*p
    for u, v in combinations(verts, 2):
        result[distance(u, v) % p] += 1
    return result


def allocations(system, negative):
    counts = []
    for g in system['groups']:
        counts.append(sum((g['arm'], g['first']+j*system['modulus']) in negative
                          for j in range(g['population'])))
    return counts


class JointTests(unittest.TestCase):
    def test_sparse_columns_against_literal_occupied_neighbours(self):
        lengths, holes = (7, 4, 2), ((0, 2), (1, 1))
        vs = vertices(lengths, holes)
        for p in (1, 2, 3, 4, 5, 7):
            for a, d in vs:
                hist = [0]*p
                for u in vs:
                    if u != (a, d):
                        hist[distance((a, d), u) % p] += 1
                expected = {r: hist[r]-hist[(r-1) % p] for r in range(p)
                            if hist[r] != hist[(r-1) % p]}
                self.assertEqual(m.anchor_coefficient(lengths, holes, a, d, p),
                                 hist[0]-sum(L//p for L in lengths))
                self.assertEqual(m.derivative_column(lengths, holes, a, d, p), expected)

    def test_exact_equivalence_over_every_small_balanced_colouring(self):
        cases = (((5, 3, 1), ((0, 1), (1, 1))),
                 ((6, 4, 1), ((0, 2), (1, 2))),
                 ((7, 4, 2), ((0, 2), (1, 1))))
        for lengths, holes in cases:
            vs = vertices(lengths, holes)
            for p in (2, 3, 4, 5):
                system = m.reduction(lengths, holes, p)
                for choice in combinations(vs, len(vs)//2):
                    negative = set(choice)
                    positive = [v for v in vs if v not in negative]
                    expected = bins(positive, p) == bins(choice, p)
                    self.assertEqual(m.bounded_allocation(system, allocations(system, negative)), expected)

    def test_parity_elimination_matches_exhaustive_small_system(self):
        for p in (2, 3, 4):
            system = m.reduction((3, 1, 1), ((0, 3), (2, 1)), p)
            result = m.parity_test(system)
            feasible = any(all((a-b) % 2 == 0 for a, b in zip(m.lhs(system, x), system['rhs']))
                           for x in product((0, 1), repeat=len(system['groups'])))
            self.assertEqual(result['consistent_mod2'], feasible)

    def test_large_cases_and_known_opposite_parity_control(self):
        for parity in ('odd', 'even'):
            a, b, c = (m.family(k, parity) for k in (1, 2, 3))
            self.assertEqual(a['columns'], b['columns'])
            self.assertEqual([y-x for x, y in zip(a['population'], b['population'])],
                             [z-y for y, z in zip(b['population'], c['population'])])
            for system in (a, b):
                self.assertEqual(len(system['groups']), 7999)
                self.assertLessEqual(max(map(len, system['columns'])), 10)
                result = m.parity_test(system)
                self.assertTrue(result['consistent_mod2'])
                self.assertEqual(result['rank'], 2658)
                self.assertFalse(m.bounded_allocation(system, result['solution_bits']))
        self.assertFalse(m.parity_test(m.family(1, 'opposite'))['consistent_mod2'])

    def test_lift_preserves_every_equation_and_bound(self):
        system = m.reduction((5, 3, 1), ((0, 1), (1, 1)), 3)
        vs = vertices(system['lengths'], system['holes'])
        for choice in combinations(vs, len(vs)//2):
            x = allocations(system, set(choice))
            if m.bounded_allocation(system, x):
                bits = [n % 2 for n in x]
                lifted = m.lift_problem(system, bits)
                y = [(n-u)//2 for n, u in zip(x, bits)]
                self.assertTrue(m.bounded_allocation(lifted, y))
                self.assertEqual([u+2*n for u, n in zip(bits, y)], x)
                return
        self.fail('small positive control missing')

    def test_bounds_are_part_of_the_problem(self):
        system = m.reduction((3, 1, 1), ((0, 3), (2, 1)), 2)
        self.assertFalse(m.bounded_allocation(system, [-1]*len(system['groups'])))
        self.assertFalse(m.bounded_allocation(system, [n+1 for n in system['population']]))
        with self.assertRaises(ValueError):
            m.family(0, 'odd')


if __name__ == '__main__':
    unittest.main()
