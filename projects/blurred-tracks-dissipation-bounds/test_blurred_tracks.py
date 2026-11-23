#!/usr/bin/env python3
"""Unit tests: python3 -m pytest test_blurred_tracks.py  (or unittest)."""
import cmath
import math
import unittest

from fractions import Fraction

from blurred_tracks import (Camera, Vortex, all_branch_candidates,
                            blur_factor_F, blur_factor_Z,
                            branches_from_covariances, observed_cov_complex,
                            observed_cov_matrix)

V = Vortex(kappa=1.3, omega=-2.1, D=0.7)
CAM = Camera(Delta=0.8, eps=0.3, ell2=0.02)


class TestCovariances(unittest.TestCase):
    def test_zero_lag_real_isotropic(self):
        G = observed_cov_matrix(V, CAM, 0)
        self.assertAlmostEqual(G[0][1], 0.0)
        self.assertAlmostEqual(G[0][0], G[1][1])
        self.assertGreater(G[0][0], CAM.ell2)

    def test_negative_lag_is_transpose(self):
        for k in (1, 2, 5):
            Gp = observed_cov_matrix(V, CAM, k)
            Gm = observed_cov_matrix(V, CAM, -k)
            self.assertAlmostEqual(Gm[0][1], Gp[1][0])
            self.assertAlmostEqual(Gm[1][0], Gp[0][1])
            self.assertAlmostEqual(Gm[0][0], Gp[0][0])

    def test_ratio_is_phi(self):
        phi = cmath.exp(-V.lam * CAM.Delta)
        for k in (1, 2, 3):
            r = observed_cov_complex(V, CAM, k + 1) / observed_cov_complex(V, CAM, k)
            self.assertAlmostEqual(r, phi, places=12)

    def test_vanishing_exposure_limit(self):
        tiny = Camera(Delta=CAM.Delta, eps=1e-6, ell2=CAM.ell2)
        g1 = observed_cov_complex(V, tiny, 1)
        latent = V.latent_cov_complex(CAM.Delta)
        self.assertAlmostEqual(g1, latent, delta=1e-5)
        g0 = observed_cov_complex(V, tiny, 0)
        self.assertAlmostEqual(g0.real, 2 * V.s + 2 * CAM.ell2, delta=1e-5)

    def test_blur_factors_bounds(self):
        Z = blur_factor_Z(V.lam, CAM.eps)
        self.assertTrue(0.0 < Z <= 1.0)
        self.assertGreater(abs(blur_factor_F(V.lam, CAM.eps)), 0.0)

    def test_full_exposure_allowed(self):
        full = Camera(Delta=1.0, eps=1.0, ell2=0.0)
        self.assertTrue(math.isfinite(observed_cov_complex(V, full, 1).real))

    def test_invalid_camera(self):
        with self.assertRaises(ValueError):
            Camera(Delta=1.0, eps=1.5, ell2=0.0)
        with self.assertRaises(ValueError):
            Camera(Delta=1.0, eps=0.0, ell2=0.0)


class TestBranches(unittest.TestCase):
    def test_recovers_true_branch(self):
        cam = Camera(Delta=1.0, eps=0.5, ell2=0.04)
        v = Vortex(kappa=1.0, omega=3.9, D=1.0)
        gs = [observed_cov_complex(v, cam, k) for k in range(3)]
        kappa, _phi, bs = branches_from_covariances(gs[0].real, gs[1], gs[2],
                                                    1.0, 0.5, range(-30, 31))
        self.assertAlmostEqual(kappa, 1.0, places=9)
        ok = [b for b in bs if b.compatible()]
        self.assertEqual([b.m for b in ok], [1])
        self.assertAlmostEqual(ok[0].sigma, 30.42, places=6)
        self.assertAlmostEqual(ok[0].ell2, 0.04, places=9)

    def test_equilibrium_zero_dissipation(self):
        v = Vortex(kappa=2.0, omega=0.0, D=1.0)
        self.assertEqual(v.dissipation(), 0.0)
        g1 = observed_cov_complex(v, CAM, 1)
        self.assertAlmostEqual(g1.imag, 0.0)  # no rotation: real covariances

    def test_dissipation_formula(self):
        self.assertAlmostEqual(Vortex(0.5, 3.0, 9.9).dissipation(), 36.0)

    def test_all_candidates_cover_window_scan(self):
        v = Vortex(kappa=1.0, omega=3.9, D=1.0)
        for ratio in (Fraction(1, 3), Fraction(2, 5), Fraction(1, 2),
                      Fraction(1, 1)):
            eps = float(ratio)
            cam = Camera(Delta=1.0, eps=eps, ell2=0.04)
            gs = [observed_cov_complex(v, cam, k) for k in range(3)]
            cands = set(all_branch_candidates(gs[1], gs[2], 1.0, eps, ratio))
            _, _, bs = branches_from_covariances(
                gs[0].real, gs[1], gs[2], 1.0, eps, range(-300, 301))
            ok_window = {b.m for b in bs if b.compatible()}
            self.assertTrue(ok_window <= cands)
            _, _, bc = branches_from_covariances(
                gs[0].real, gs[1], gs[2], 1.0, eps, sorted(cands))
            self.assertEqual([b.m for b in bc if b.compatible()], [1])


if __name__ == "__main__":
    unittest.main()
