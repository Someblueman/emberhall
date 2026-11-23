#!/usr/bin/env python3
import unittest

from general_tracks import (GeneralVortex, expm, int_exp, matmul, scale,
                            stationary_covariance, transpose)


class TestGeneral(unittest.TestCase):
    def setUp(self):
        self.A = [[-1.2, -2.0], [0.8, -0.7]]
        self.Dm = [[1.0, 0.3], [0.3, 0.6]]
        self.g = GeneralVortex(self.A, self.Dm)

    def test_lyapunov_residual(self):
        S = self.g.Sigma
        R = matmul(self.A, S)
        R = [[R[i][j] + matmul(S, transpose(self.A))[i][j] + 2 * self.Dm[i][j]
              for j in range(2)] for i in range(2)]
        self.assertLess(max(abs(x) for r in R for x in r), 1e-12)
        self.assertAlmostEqual(S[0][1], S[1][0], places=12)

    def test_expm_rotation(self):
        E = expm([[0.0, -1.0], [1.0, 0.0]])
        import math
        self.assertAlmostEqual(E[0][0], math.cos(1.0), places=12)
        self.assertAlmostEqual(E[1][0], math.sin(1.0), places=12)

    def test_int_exp_scalar_limit(self):
        U = int_exp([[-2.0, 0.0], [0.0, -2.0]], 0.5)
        import math
        self.assertAlmostEqual(U[0][0], (1 - math.exp(-1.0)) / 2.0, places=12)

    def test_negative_lag_transpose(self):
        Gp = self.g.observed_cov_matrix(0.9, 0.45, 0.03, 2)
        Gm = self.g.observed_cov_matrix(0.9, 0.45, 0.03, -2)
        self.assertAlmostEqual(Gm[0][1], Gp[1][0], places=12)

    def test_zero_lag_symmetric(self):
        G0 = self.g.observed_cov_matrix(0.9, 0.45, 0.03, 0)
        self.assertAlmostEqual(G0[0][1], G0[1][0], places=12)

    def test_equilibrium_of_symmetric_drift(self):
        # A = -Dm @ K with K SPD gives detailed balance: sigma = 0 and
        # Sigma = K^{-1}.
        K = [[2.0, 0.4], [0.4, 1.0]]
        Dm = [[1.0, 0.2], [0.2, 0.8]]
        A = scale(matmul(Dm, K), -1.0)
        g = GeneralVortex(A, Dm)
        self.assertAlmostEqual(g.dissipation(), 0.0, delta=1e-10)


class TestRealLogs(unittest.TestCase):
    def test_no_real_log_negative_spectrum(self):
        from real_logs import real_log_candidates
        for P in ([[-0.5, 0.1], [0.0, 0.3]], [[-0.5, 0.1], [0.0, -0.25]],
                  [[-0.5, 1.0], [0.0, -0.5]]):
            self.assertEqual(real_log_candidates(P, 1.0)[0], "none")

    def test_family_members_are_real_logs(self):
        import math
        from real_logs import family_drift
        from general_tracks import expm, scale
        lam = -math.exp(-1.0)
        for beta in (math.pi, 3 * math.pi):
            A = family_drift(-1.0, beta, 0.4, 0.7, 1.0)
            E = expm(scale(A, 1.0))
            self.assertAlmostEqual(E[0][0], lam, places=10)
            self.assertAlmostEqual(E[0][1], 0.0, places=10)

    def test_defective_unique_log(self):
        from real_logs import real_log_candidates
        from general_tracks import expm, scale
        Phi = expm(scale([[-1.0, 1.0], [0.0, -1.0]], 0.9))
        kind, cands = real_log_candidates(Phi, 0.9)
        self.assertEqual(kind, "unique")
        self.assertAlmostEqual(cands[0][0][1], 1.0, places=10)


class TestSingularCases(unittest.TestCase):
    def test_symbol_never_zero_for_stable(self):
        from singular_cases import symbol_f
        for mu in (-1 + 3j, -0.1 + 40j, -2.0, -0.05 + 13.963j):
            self.assertGreater(abs(symbol_f(mu, 0.45)), 0.0)

    def test_singular_gamma1_refused(self):
        from singular_cases import propagator_from_covariances
        with self.assertRaises(ValueError):
            propagator_from_covariances([[1.0, 2.0], [0.5, 1.0]],
                                        [[0.3, 0.1], [0.0, 0.2]])


class TestRationalCompleteness(unittest.TestCase):
    def test_residual_roots_at_one_third(self):
        from completeness_rational import EigenResidual
        er = EigenResidual(0.9, 0.3)
        self.assertAlmostEqual(er.R(0), 0.0, delta=1e-9)
        self.assertGreater(abs(er.R(1)), 1e-3)
        self.assertGreater(abs(er.R(-2)), 1e-3)


class TestBranchSets(unittest.TestCase):
    def _bs(self):
        from types import SimpleNamespace as B
        return [B(m=1, phase_residual=0.02, ell2=-0.005, sigma=30.0),
                B(m=0, phase_residual=-0.05, ell2=0.05, sigma=11.0),
                B(m=2, phase_residual=0.40, ell2=0.01, sigma=90.0)]

    def test_hard_ell2_filter_discards_best_phase(self):
        from branch_sets import branch_set
        self.assertEqual([b.m for b in branch_set(self._bs(), 0.01, 0.0)], [0])
        self.assertEqual([b.m for b in branch_set(self._bs(), 0.01, 0.02)], [1])
        self.assertEqual([b.m for b in branch_set(self._bs(), 0.01)], [1])

    def test_tolerance_admits_near_rival(self):
        from branch_sets import branch_set
        self.assertEqual(sorted(b.m for b in branch_set(self._bs(), 0.05)),
                         [0, 1])


class TestTwoExposures(unittest.TestCase):
    def test_population_near_alias_and_combined_margin(self):
        from two_exposures import RATIOS, TRUE_M, pop_branches
        per = [{b.m: b for b in pop_branches(r)} for r in RATIOS]
        self.assertLess(abs(per[0][11].phase_residual), 0.01)
        self.assertLess(per[0][11].ell2, -0.02)
        combined = min(max(abs(per[0][m].phase_residual),
                           abs(per[1][m].phase_residual))
                       for m in per[0] if m != TRUE_M)
        self.assertGreater(combined, 0.27)


class TestUnknownMean(unittest.TestCase):
    def test_demean_removes_centre(self):
        from unknown_mean import demean
        frames = demean([1 + 2j, 3 + 0j, -1 + 1j])
        self.assertAlmostEqual(abs(sum(frames)), 0.0, places=12)

    def test_offset_invariance_of_demeaned_gamma(self):
        from unknown_mean import demean
        from verify_blurred import empirical_gamma
        base = [complex(i, -i) for i in range(10)]
        off = [f + (0.7 + 0.4j) for f in base]
        for k in (0, 1, 2):
            self.assertAlmostEqual(
                abs(empirical_gamma(demean(base), k)
                    - empirical_gamma(demean(off), k)), 0.0, places=9)


class TestEqualFrames(unittest.TestCase):
    def test_joint_winner_uses_max_residual(self):
        from types import SimpleNamespace as B
        from equal_frames import winner_joint
        a = [B(m=1, phase_residual=0.30, sigma=30.0),
             B(m=0, phase_residual=0.01, sigma=11.0)]
        b = [B(m=1, phase_residual=0.02, sigma=31.0),
             B(m=0, phase_residual=0.28, sigma=12.0)]
        # max-residual scores: m=1 -> 0.30, m=0 -> 0.28, so m=0 wins jointly
        # although each film alone prefers a different branch.
        self.assertEqual(winner_joint(a, b).m, 0)


if __name__ == "__main__":
    unittest.main()
