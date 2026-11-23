#!/usr/bin/env python3
"""Unit tests for ostrowski_liminf.py (DERIVATION s26)."""
import math
import unittest
from fractions import Fraction

from mpmath import mp, mpf

import ostrowski_liminf as ol
import window_constant as wc

mp.dps = 80


class TestExactIdentities(unittest.TestCase):
    def test_delta_identity_in_quadratic_field(self):
        for _name, a, d, rhoq in ol.CASES:
            p, q = ol.convergents(a, 30)
            pw = rhoq
            for k in range(20):
                dk = ol.qadd(
                    ol.qmul((Fraction(q[k]), Fraction(0)), rhoq, d),
                    (Fraction(-p[k]), Fraction(0)))
                want = pw if k % 2 == 0 else (-pw[0], -pw[1])
                self.assertEqual(dk, want)
                pw = ol.qmul(pw, rhoq, d)

    def test_greedy_digits_legal_and_reconstruct(self):
        for _name, a, _d, _rq in ol.CASES:
            _p, q = ol.convergents(a, 14)
            for m in range(q[9]):
                b = ol.greedy_digits(m, q)
                self.assertTrue(ol.legal(b, a))
                self.assertEqual(sum(b[k] * q[k] for k in range(len(b))), m)


class TestGammaAndDigits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {}
        for name, a, _d, _rq in ol.CASES:
            rho = (mp.sqrt(5) - 1) / 2 if name == "golden" else mp.sqrt(2) - 1
            zeros = sorted(ol.gamma_xi_star(rho, dps=60), key=lambda t: t[3])
            cls.cases[name] = (rho, a, zeros)

    def test_gamma_xi_star_vs_float_route(self):
        for name, (rho, _a, zeros) in self.cases.items():
            cx = wc.Ctx(float(rho))
            fz = []
            for z in cx.zeros():
                hp = cx.hp(z)
                fz.append((2 * math.pi * abs(hp),
                           -cx.hj(cx.c1, z) / (2 * math.pi * hp),
                           (z / (2 * math.pi)
                            - float(rho) * cx.th / (2 * math.pi)) % 1.0))
            fz.sort()
            for i in range(2):
                self.assertAlmostEqual(float(zeros[i][3]), fz[i][0],
                                       delta=1e-6 * fz[i][0])
                self.assertAlmostEqual(float(zeros[i][2]), fz[i][1], delta=1e-9)
                self.assertAlmostEqual(float(zeros[i][1]), fz[i][2], delta=1e-11)

    def test_predecessor_vs_brute(self):
        for name, (rho, a, zeros) in self.cases.items():
            gam = zeros[0][1]
            p, q = ol.convergents(a, 14)
            bj = ol.predecessor_j(gam, rho, p, q, 11)
            gf, rf = float(gam), float(rho)
            expect = max(range(q[11]),
                         key=lambda j: (j * rf) % 1.0 if (j * rf) % 1.0 <= gf else -1)
            self.assertEqual(bj, expect)

    def test_digits_series_and_xi_machine(self):
        for name, (rho, a, zeros) in self.cases.items():
            _psi, gam, xi_star, _tpi = zeros[0]
            xm = ol.XiMachine(rho, a, gam, K=150)
            self.assertTrue(ol.legal(xm.cs, a))
            self.assertLess(abs(gam - xm.e - xm.R[0]), mpf("1e-25"))
            for m in (3, 12345, 92549):
                self.assertLess(abs(xm.xi_of_m(m)[0] - xm.xi_direct(m)),
                                mpf("1e-24"))
            for K in (12, 25, 40):
                if xm.A[K] > 0:
                    self.assertLess(
                        abs(xm.xi_prefix(K) - xm.xi_of_m(xm.A[K])[0]),
                        mpf("1e-25"))
            J0 = 4 if a == 1 else 3
            self.assertLess(2 * xm.tail_abs_bound(J0), 0.5)

    def test_golden_prefix25_is_s25_argmin(self):
        rho, a, zeros = self.cases["golden"]
        _psi, gam, xi_star, _tpi = zeros[0]
        xm = ol.XiMachine(rho, a, gam, K=150)
        self.assertEqual(xm.A[25], 92549)
        dd = float(abs(xm.xi_prefix(25) - xi_star))
        self.assertAlmostEqual(dd, 0.014756, delta=2e-6)


if __name__ == "__main__":
    unittest.main()
