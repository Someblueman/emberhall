import itertools
import unittest
from t2661_joint_lift import actual_pair_bins, vertices, verify, sparse_rows, divisibility_refinement, divided_equation, parity_analysis, branch_probe, refinement_report, even_scale_allocation, joint_allocation, alternating_kernel
from t2661_joint_residue import reduction, bounded_allocation


def literal_bins(selected, p):
    out = [0]*p
    for (a, d), (b, e) in itertools.combinations(selected, 2):
        distance = abs(d-e) if a == b else d+e
        out[distance % p] += 1
    return out


class JointLiftTests(unittest.TestCase):
    def test_all_subsets_against_literal_pairs(self):
        lengths = (3, 2, 1)
        vs = [(None, 0)]+[(a, d) for a, n in enumerate(lengths) for d in range(1, n+1)]
        for mask in range(1 << len(vs)):
            chosen = [v for i, v in enumerate(vs) if mask >> i & 1]
            for p in (1, 2, 4, 7):
                self.assertEqual(actual_pair_bins(lengths, chosen, p), literal_bins(chosen, p))

    def test_longer_carry_and_lag_orientation(self):
        lengths = (280, 279, 3)
        chosen = [(None, 0)]+[(a, d) for a, n in enumerate(lengths)
                            for d in range(1, n+1) if (d+a) % 3]
        for p in (3, 19, 2660):
            self.assertEqual(actual_pair_bins(lengths, chosen, p), literal_bins(chosen, p))

    def test_every_bounded_allocation(self):
        for lengths, holes, p in [((4, 3, 2), ((0, 1), (0, 4)), 2),
                                   ((3, 2, 2), ((0, 2), (1, 1)), 3)]:
            s = reduction(lengths, holes, p)
            for x in itertools.product(*(range(n+1) for n in s['population'])):
                a, b = vertices(s, x)
                expected = len(a) == len(b) and literal_bins(a, p) == literal_bins(b, p)
                self.assertEqual(bounded_allocation(s, x), expected)
                self.assertEqual(verify(s, x)['valid'], expected)

    def test_altered_allocation_rejected(self):
        s = reduction((4, 3, 2), ((0, 1), (0, 4)), 3)
        good = [0, 0, 0, 1, 1, 0, 1, 1]
        altered = [0, 1, 0, 0, 1, 0, 1, 1]
        self.assertTrue(verify(s, good)['valid'])
        self.assertEqual(sum(good), sum(altered))
        self.assertFalse(verify(s, altered)['valid'])
        a, b = vertices(s, altered)
        self.assertNotEqual(actual_pair_bins(s['lengths'], a, 3),
                            actual_pair_bins(s['lengths'], b, 3))

    def test_mod4_extendability_exhaustive(self):
        # Every parity branch, including all choices of the free variables.
        for p in (2, 3, 4):
            s = reduction((2, 2, 1), ((0, 1), (1, 2)), p)
            rr = sparse_rows(s)
            r = divisibility_refinement(s)
            n = len(s['population'])
            extendable = set()
            for x in itertools.product(range(4), repeat=n):
                if all((sum(a*x[j] for j, a in row.items())-b) % 4 == 0
                       for row, b in zip(rr, s['rhs'])):
                    extendable.add(tuple(v % 2 for v in x))
            for u in itertools.product(range(2), repeat=n):
                allowed = all((sum(a*u[j] for j, a in row.items())-b) % 2 == 0
                              for row, b in zip(r['rows'], r['rhs']))
                self.assertEqual(allowed, u in extendable)

    def test_divided_equation_provenance(self):
        rows = [{0: 1, 1: 1}, {0: 1, 1: -1}]
        self.assertEqual(divided_equation(rows, [2, 0], 3), ({0: 1}, 1))
        with self.assertRaises(ValueError):
            divided_equation(rows, [2, 1], 3)  # altered right side
        with self.assertRaises(ValueError):
            divided_equation(rows, [2, 0], 1)  # altered provenance
        self.assertFalse(parity_analysis([{0: 2}], [1], 1)['consistent'])

    def test_rejected_prefix_is_not_global_failure(self):
        s = reduction((4, 3, 2), ((0, 1), (0, 4)), 2)
        self.assertTrue(verify(s, [0, 0, 0, 0, 2, 1, 1])['valid'])
        rejected = branch_probe(s, initial_bits=[0]*7)
        self.assertEqual(rejected['status'], 'chosen_prefix_rejected')
        self.assertFalse(rejected['all_parity_branches_examined'])
        self.assertGreater(rejected['levels'][-1]['verified_dual_rows'], 0)
        with self.assertRaises(ValueError):
            branch_probe(s, initial_bits=[2]*7)

    def test_parity_solver_against_exhaustive(self):
        import random
        rng = random.Random(837)
        for _ in range(24):
            rows = [{j: rng.randrange(-2, 3) for j in range(5)} for _ in range(6)]
            rhs = [rng.randrange(-3, 4) for _ in rows]
            solutions = [u for u in itertools.product(range(2), repeat=5)
                         if all((sum(a*u[j] for j, a in row.items())-b) % 2 == 0
                                for row, b in zip(rows, rhs))]
            tested = parity_analysis(rows, rhs, 5)
            self.assertEqual(tested['consistent'], bool(solutions))
            if solutions:
                self.assertIn(tuple(tested['bits']), solutions)
                self.assertEqual(len(solutions), 2**(5-tested['rank']))
            else:
                source = tested['contradiction']
                self.assertTrue(sum(rhs[i] for i in range(6) if source >> i & 1) % 2)
                for j in range(5):
                    self.assertEqual(sum(rows[i][j] for i in range(6)
                                         if source >> i & 1) % 2, 0)

    def test_inherited_even_scale_positive_control(self):
        for k in (2, 4, 10):
            system, counts = even_scale_allocation(k)
            self.assertTrue(bounded_allocation(system, counts))
            self.assertEqual(sum(counts), (201*(2660*k+1)-1)//2)
        for k in (0, 1, 3, True):
            with self.assertRaises(ValueError):
                even_scale_allocation(k)

    def test_all_scale_construction_and_arm_kernels(self):
        from t2661_joint_residue import lhs
        for k in (1, 2, 3, 4, 7, 31):
            system, counts = joint_allocation(k)
            self.assertTrue(bounded_allocation(system, counts))
            self.assertEqual(sum(counts), (201*(2660*k+1)-1)//2)
            for arm in (None, 0, 1, 2):
                self.assertEqual(lhs(system, alternating_kernel(system, arm)),
                                 [0]*len(system['rhs']))

    def test_actual_joint_witness_and_full_distance_boundary(self):
        system, counts = joint_allocation(1)
        result = verify(system, counts, full=True)
        self.assertTrue(result['valid'])
        self.assertTrue(result['actual_counter'])
        self.assertEqual(result['size_each'], 267430)
        self.assertEqual(result['full_distance_check']['first_difference'], (1, -1))
        self.assertFalse(result['full_distance_check']['equal'])
        altered = list(counts)
        altered[0] -= 1
        altered[19] += 1
        self.assertEqual(sum(altered), sum(counts))
        self.assertFalse(verify(system, altered)['valid'])

    def test_large_divisibility_frontier(self):
        from t2661_joint_residue import family
        for parity, previous_violations in [('odd', 4), ('even', 0)]:
            r = refinement_report(family(1, parity))
            self.assertEqual((r['initial_rank'], r['refined_rank']), (2658, 2659))
            self.assertEqual(r['derived_equations'], 4)
            self.assertTrue(r['consistent'])
            self.assertEqual(r['predecessor_bit_vector_violations'], previous_violations)
            self.assertEqual(r['bounded_integer_feasibility'], 'unresolved')

    def test_input_validation(self):
        for chosen in [[(0, 1), (0, 1)], [(None, 1)], [(3, 1)], [(0, 4)]]:
            with self.assertRaises(ValueError):
                actual_pair_bins((3, 2, 1), chosen, 4)


if __name__ == '__main__':
    unittest.main()
