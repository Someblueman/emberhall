import copy
from collections import defaultdict
import unittest
import literal_fibre as full
import reduced_folded_fibre as reduced


class ReducedFoldedTests(unittest.TestCase):
    def test_exact_stencils_against_every_reduced_matrix_coefficient(self):
        left,right = reduced.boundaries()
        interior = reduced.interior()
        for t in (163,201):
            half,r = t//2,40
            vertices,equations,_ = full.system(t,None,1)
            actual_left = defaultdict(lambda:defaultdict(int))
            actual_right = defaultdict(lambda:defaultdict(int))
            actual_interior = defaultdict(lambda:defaultdict(int))
            for e,row,rhs in equations:
                level = full.folded_level(t,e)
                tau = 1 if e%t <= half else -1
                quotient = (e-tau*level)//t
                for i,c in row.items():
                    arm,d = vertices[i]
                    vlevel = full.folded_level(t,d)
                    s = 1 if d%t <= half else -1
                    q = (d-s*vlevel)//t
                    if level <= 20:
                        actual_left[quotient,tau*level][arm,q,s*vlevel] += c
                    if level >= half-20:
                        actual_right[quotient,tau,level-half][arm,q,s,vlevel-half] += c
                    if level == r:
                        actual_interior[quotient,tau][arm,q,s,vlevel-r] += c
                if rhs:
                    self.assertLessEqual(level,20)
                    actual_left[quotient,tau*level][0,0,0] -= rhs
            self.assertEqual(left,reduced.trim(actual_left))
            self.assertEqual(right,reduced.trim(actual_right))
            self.assertEqual(interior,reduced.trim(actual_interior))

    def test_random_original_shell_reconstruction(self):
        for t in (163,201):
            report = reduced.audit(t)
            self.assertTrue(report['all_coefficients_reconstructed'])
            self.assertFalse(report['homometry_claimed'])
            self.assertEqual(report['reduced_unknowns'],145*t-2)

    def test_altered_interior_is_rejected_by_original_coefficients(self):
        coordinates,expected = reduced.control(163)
        damaged = copy.deepcopy(reduced.interior())
        row = next(iter(damaged))
        variable = next(iter(damaged[row]))
        damaged[row][variable] += 1
        self.assertNotEqual(reduced.residual(163,coordinates,damaged),expected)

    def test_tail_threshold_and_endpoints(self):
        t = 163
        lengths,holes = full.geometry(t)
        for arm,d in [(0,0),(1,18),(1,20),(1,43*t-1),(2,23*t-1),
                      (2,23*t),(2,23*t+1),(2,79*t),(3,23*t)]:
            q,beta = divmod(d,t)
            formal = defaultdict(int)
            for Q,alpha,c,coefficient in reduced.column(arm,q,0,beta,arm == 1 and d < 19):
                self.assertEqual(alpha,0)
                formal[Q*t+c] += coefficient
            expected = defaultdict(int,full.shell.shell_column(lengths,holes,(arm,d)))
            if arm == 2 and d >= 23*t+1:
                for e,c in full.shell.shell_column(lengths,holes,(1,d+20*t-1)).items():
                    expected[e] -= c
            self.assertEqual({e:c for e,c in formal.items() if c},
                             {e:c for e,c in expected.items() if c})

    def test_bound_and_invalid_scale(self):
        self.assertEqual(len(set(reduced.labels())),290)
        self.assertEqual(len(reduced.interior()),244)
        self.assertEqual(max(abs(v[3]) for row in reduced.interior().values() for v in row),20)
        self.assertEqual(reduced.theorem()['stored_sign_bound'],11600)
        self.assertFalse(reduced.theorem()['resistant_scales_decided'])
        for t in (0,True,161,164):
            with self.assertRaises(ValueError):
                reduced.audit(t)


if __name__ == '__main__':
    unittest.main()
