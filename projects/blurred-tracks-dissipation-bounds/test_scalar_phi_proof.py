#!/usr/bin/env python3
"""Unit tests for scalar_phi_proof.py (DERIVATION s27)."""
import unittest

from mpmath import mp, mpf

import scalar_phi_proof as sp



class TestDeterminantExclusion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mp.dps = 50
        cls.tr = sp.Truth()

    def test_truth_scalar_phi_and_control(self):
        tr = self.tr
        ea = mp.exp(tr.alpha)
        self.assertLess(abs(tr.Phi[0, 0] - ea) + abs(tr.Phi[0, 1]),
                        mpf("1e-40"))
        resid, _ = tr.compat(tr.A)
        self.assertLess(max(abs(v) for v in resid), mpf("1e-40"))

    def test_trig_form(self):
        tr = self.tr
        beta, t, phi = 4 * mp.pi, mpf("0.42"), mpf("2.1")
        M = tr.coeffs(beta, t)
        got, _ = tr.compat(sp.family_drift(tr.a_rec, beta, t, phi, tr.Delta))
        for i in range(3):
            pred = M[i][0] + M[i][1] * mp.cos(2 * phi) + M[i][2] * mp.sin(2 * phi)
            self.assertLess(abs(pred - got[i]), mpf("1e-35"))

    def test_beta0_single_drift(self):
        tr = self.tr
        r0, _ = tr.compat(sp.family_drift(tr.a_rec, mpf(0), mpf(0),
                                          mpf(0), tr.Delta))
        J0 = sum((v / tr.scale) ** 2 for v in r0)
        self.assertGreater(J0, mpf("1e-3"))

    def test_S_quadratic_and_roots(self):
        tr = self.tr
        ts_fit = [mpf("0.35"), mpf("0.9"), mpf("1.6")]
        ts_test = [mpf("0.55"), mpf("1.2")]
        expect = {2: (2.16, 2.17), 4: (1.02, 1.04), 6: (0.62, 0.63)}
        for k, (lo, hi) in expect.items():
            beta = 2 * mp.pi * (k // 2)
            coef, err = sp.fit_S(tr, beta, ts_fit, ts_test)
            self.assertLess(err, mpf("1e-30"))
            w_star = -coef[0] / (2 * coef[2])
            self.assertTrue(mpf(lo) < w_star < mpf(hi),
                            f"beta={k}pi w*={w_star}")

    def test_same_branch_recovers_truth(self):
        tr = self.tr
        coef, _err = sp.fit_S(tr, 2 * mp.pi,
                              [mpf("0.35"), mpf("0.9"), mpf("1.6")],
                              [mpf("0.55")])
        w_star = -coef[0] / (2 * coef[2])
        t_star = mp.acosh(w_star / 2) / 2
        self.assertLess(abs(t_star - tr.t_true), mpf("1e-25"))


if __name__ == "__main__":
    unittest.main()
