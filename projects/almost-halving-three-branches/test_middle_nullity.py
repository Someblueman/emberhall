import random
import unittest
from fractions import Fraction
import full_shorter_coupling as fc
import middle_nullity as mn
from test_aperiodic_completion import bfs_shells


def full_matrix(t, h):
    n = 5 * t
    return [
        [fc.middle_operator(t, h, 13 * t + i).get(13 * t + j, 0) for j in range(1, n + 1)]
        for i in range(1, n + 1)
    ]


def rational_rank(rows):
    if not rows:
        return 0
    mat = [[Fraction(v) for v in row] for row in rows]
    r = 0
    cols = len(mat[0])
    for col in range(cols):
        pivot = next((i for i in range(r, len(mat)) if mat[i][col] != 0), None)
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        scale = mat[r][col]
        mat[r] = [v / scale for v in mat[r]]
        for i in range(r + 1, len(mat)):
            factor = mat[i][col]
            if factor != 0:
                mat[i] = [v - factor * w for v, w in zip(mat[i], mat[r])]
        r += 1
        if r == len(mat):
            break
    return r


class MiddleNullityTests(unittest.TestCase):
    def test_closed_form_nullity_and_basis_against_full_matrix(self):
        """Compare closed-form nullity, right basis, and left basis against full 5t x 5t matrices."""
        for t in range(1, 9):
            for h in range(0, 2 * t - 1):
                n = 5 * t
                M = full_matrix(t, h)
                expected_rank = rational_rank(M)
                expected_nullity = n - expected_rank
                cls = mn.nullity_classification(t, h)
                self.assertEqual(cls['rank'], expected_rank, f't={t}, h={h}')
                self.assertEqual(cls['nullity'], expected_nullity, f't={t}, h={h}')
                self.assertEqual(cls['seed_rank'], (2 * h + 2) - expected_nullity, f't={t}, h={h}')

                rbasis = mn.kernel_basis(t, h)
                lbasis = mn.left_kernel_basis(t, h)
                self.assertEqual(len(rbasis), expected_nullity)
                self.assertEqual(len(lbasis), expected_nullity)

                for item in rbasis:
                    z = item['vector']
                    self.assertTrue(all(v in (-1, 0, 1) for v in z.values()))
                    for i, row in enumerate(M, 1):
                        self.assertEqual(sum(a * z[j] for j, a in enumerate(row, 1)), 0)

                for item in lbasis:
                    w = item['weights']
                    for j in range(1, n + 1):
                        self.assertEqual(sum(w[i] * M[i - 1][j - 1] for i in range(1, n + 1)), 0)

                if expected_nullity > 0:
                    r_rows = [[item['vector'][j] for j in range(1, n + 1)] for item in rbasis]
                    l_rows = [[item['weights'][i] for i in range(1, n + 1)] for item in lbasis]
                    self.assertEqual(rational_rank(r_rows), expected_nullity)
                    self.assertEqual(rational_rank(l_rows), expected_nullity)

    def test_global_symmetry_of_intertwiner_LTM(self):
        """Verify L_{t,h}^T M(t, h) = M(t, h)^T L_{t,h} on full matrices for t=1..7, 0<=h<=2t-2."""
        for t in range(1, 8):
            for h in range(0, 2 * t - 1):
                n = 5 * t
                M = full_matrix(t, h)
                L = [[0] * n for _ in range(n)]
                lo = 2 * t - h - 1
                L[lo - 1][5 * t - 1] = 1
                for r in range(h):
                    L[2 * t - h + r - 1][5 * t - 1 - r - 1] += 1
                    L[2 * t - h + r - 1][5 * t - r - 1] -= 1
                for i in range(2 * t, 5 * t + 1):
                    L[i - 1][i - 1] = 1
                LTM = [[sum(L[k][a] * M[k][b] for k in range(n)) for b in range(n)] for a in range(n)]
                for a in range(n):
                    for b in range(a + 1, n):
                        self.assertEqual(LTM[a][b], LTM[b][a], f't={t}, h={h}, ({a+1},{b+1})')

    def test_psi_seed_parametrization_and_xi_eta_identities(self):
        """Verify X = Psi_h Y and closed-form kappa, xi, eta formulas across t and h."""
        for t in range(2, 8):
            for h in range(1, 2 * t - 1):
                lo = 2 * t - h - 1
                for col in range(h + 1):
                    Y = [int(q == col) for q in range(h + 1)]
                    X = [0] * (2 * h + 2)
                    X[0] = Y[0] + 2 * Y[h]
                    for p in range(1, h + 1):
                        X[p] = Y[p] + Y[h - p] - Y[h - p + 1]
                    for r in range(h + 1):
                        X[h + 1 + r] = -Y[h - r] - X[r + 1] + X[r]
                    z = {lo + p: X[p] for p in range(2 * h + 2)}
                    kappa = z[2 * t + h] + z[2 * t] - z[2 * t - 1] - z[2 * t - h - 1]
                    self.assertEqual(kappa, -2 * (Y[0] + Y[h]))
                    self.assertEqual(z[2 * t] + z[2 * t - h], Y[0] + Y[h])
                    for r in range(1, h + 1):
                        self.assertEqual(z[2 * t + r] + z[2 * t + r - h], Y[r] - Y[h + 1 - r])
                    for s in range(h):
                        self.assertEqual(z[2 * t + s] - z[2 * t + s - h - 1], -(Y[s + 1] + Y[h - 1 - s]))

    def test_compatibility_necessary_and_sufficient_against_augmented_rank(self):
        """Verify w^T b = 0 is necessary and sufficient for M z = b consistency."""
        rng = random.Random(20261124)
        for t in range(1, 7):
            for h in range(0, 2 * t - 1):
                n = 5 * t
                M = full_matrix(t, h)
                rk_M = rational_rank(M)
                for _ in range(4):
                    b = {i: Fraction(rng.randrange(-4, 5), 2) for i in range(1, n + 1)}
                    aug_rk = rational_rank([row + [b[i]] for i, row in enumerate(M, 1)])
                    comp = mn.compatibility_residuals(t, h, b)
                    self.assertEqual(comp['compatible'], rk_M == aug_rk)
                    solved = mn.solve_middle(t, h, b)
                    self.assertEqual(solved['consistent'], rk_M == aug_rk)
                # Guaranteed consistent vector b = M * target
                target = [Fraction(rng.randrange(-3, 4)) for _ in range(n)]
                b_ok = {i: sum(a * x for a, x in zip(row, target)) for i, row in enumerate(M, 1)}
                solved_ok = mn.solve_middle(t, h, b_ok)
                self.assertTrue(solved_ok['consistent'])
                self.assertTrue(solved_ok['compatibility']['compatible'])

    def test_type2_discrimination_beyond_reflected_rectangle_and_type1(self):
        """Verify literal second words that pass reflected, rectangle, and Type-I tests but fail Type-II."""
        cases = [
            (2, 2, 4, [0], [2]),
            (6, 5, 442, [0, 0, 0], [0, -2]),
            (6, 10, 11, [], [2, 0, 0, 0, 0]),
            (12, 19, 871, [0, 0], [0, -2, -2, 0, 0, 0, 0, 0, 0]),
        ]
        for t, h, neg_depth, exp_t1, exp_t2 in cases:
            word = ['+'] * (79 * t)
            word[neg_depth - 1] = '-'
            report = mn.audit_word(t, h, 1, ''.join(word))
            self.assertFalse(report['consistent'])
            self.assertTrue(report['literal_middle_excluded'])
            self.assertEqual(report['exclusion_reason'], 'failed_left_kernel_compatibility')
            self.assertEqual(report['type1_residuals'], exp_t1)
            self.assertEqual(report['type2_residuals'], exp_t2)
            self.assertEqual(report['first_failure']['kind'], 'type2_antiperiodic')

    def test_resistant_scales_at_h19_are_invertible(self):
        """Verify h=19 classification across resistant scales t=2660k+1 and parity/divisor families."""
        for k in (1, 2, 5, 10):
            t = 2660 * k + 1
            cls = mn.nullity_classification(t, 19)
            self.assertTrue(cls['invertible'])
            self.assertEqual(cls['nullity'], 0)
            self.assertEqual(cls['type1_nullity'], 0)
            self.assertEqual(cls['type2_nullity'], 0)
            self.assertEqual(cls['seed_rank'], 40)
        # Divisible by 5 (odd): d1=2, d2=0
        cls15 = mn.nullity_classification(15, 19)
        self.assertEqual((cls15['type1_nullity'], cls15['type2_nullity'], cls15['nullity']), (2, 0, 2))
        # t = 12 (even and 3t+2 = 38 divisible by 19): d1=2, d2=9, total=11
        cls12 = mn.nullity_classification(12, 19)
        self.assertEqual((cls12['type1_nullity'], cls12['type2_nullity'], cls12['nullity']), (2, 9, 11))
        # t = 31 (odd and 3t+2 = 95 divisible by 19, but v2(95)=0 == v2(19)): d1=0, d2=0
        cls31 = mn.nullity_classification(31, 19)
        self.assertEqual((cls31['type1_nullity'], cls31['type2_nullity'], cls31['nullity']), (0, 0, 0))

    def test_independent_bfs_on_type1_and_type2_kernel_vectors(self):
        """Verify via independent adjacency BFS that both Type-I and Type-II kernel vectors preserve all 5t middle shells."""
        for t, h in [(2, 1), (2, 2), (3, 2)]:
            L, _ = fc.geometry(t, h)
            y = {d: 1 for d in range(1, 79 * t + 1)}
            zero = {d: 0 for d in range(13 * t + 1, 18 * t + 1)}
            base_signs = fc.linear_completion(t, h, 1, y, zero)
            F0, _ = bfs_shells(L, base_signs)
            for item in mn.kernel_basis(t, h):
                z = {13 * t + i: val for i, val in item['vector'].items()}
                shifted_signs = fc.linear_completion(t, h, 1, y, z)
                F1, _ = bfs_shells(L, shifted_signs)
                for i in range(1, 5 * t + 1):
                    e = 92 * t + 1 + i
                    self.assertEqual(F1[e] - F1[e - 1], F0[e] - F0[e - 1])

    def test_validation_and_honesty_flags(self):
        for t, h in [(0, 0), (1, 1), (2, 3), (3, -1), (True, 0)]:
            with self.assertRaises(ValueError):
                mn.validate(t, h)
        # At a singular scale with compatible forcing (all-positive word at t=2, h=2),
        # literal feasibility of the affine solution space must remain unchecked/unexcluded.
        rep = mn.audit_word(2, 2, 1, '+' * (79 * 2))
        self.assertTrue(rep['consistent'])
        self.assertEqual(rep['nullity'], 2)
        self.assertFalse(rep['unique_middle'])
        self.assertFalse(rep['literal_middle_checked'])
        self.assertFalse(rep['literal_middle_excluded'])
        self.assertFalse(rep['universal_existence_proved'])


if __name__ == '__main__':
    unittest.main()
