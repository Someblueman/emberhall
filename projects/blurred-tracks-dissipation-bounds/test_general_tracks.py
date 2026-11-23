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


if __name__ == "__main__":
    unittest.main()
