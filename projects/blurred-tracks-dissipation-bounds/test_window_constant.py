#!/usr/bin/env python3
"""Unit tests for window_constant.py (DERIVATION s25)."""
import math
import unittest
from fractions import Fraction

from window_constant import (ENG_FRAC, GOLDEN, SQRT2M1, Ctx, bound_for,
                             brute_min, convergents, from_cf,
                             homogeneous_min)


class TestDecomposition(unittest.TestCase):
    def test_exact_against_eigen_and_direct_routes(self):
        cx = Ctx(GOLDEN)
        for m in [1, 2, 3, 7, 50, 101, 1000]:
            ref = cx.er.R(m)
            self.assertLessEqual(abs(cx.decomp(m) - ref),
                                 1e-8 * max(1.0, abs(ref)))
        for m in [-3, 1, 2, 5]:
            self.assertAlmostEqual(cx.decomp(m),
                                   cx.er.sigma_direct_sym(m), places=8)

    def test_two_simple_zeros(self):
        for rho in (GOLDEN, SQRT2M1):
            cx = Ctx(rho)
            zs = cx.zeros()
            self.assertEqual(len(zs), 2)
            for z in zs:
                self.assertAlmostEqual(cx.h(z), 0.0, places=9)
                self.assertGreater(abs(cx.hp(z)), 1e-3)


class TestBound(unittest.TestCase):
    def test_bound_below_brute_golden(self):
        bd = bound_for(GOLDEN, M=30000, G=20000)
        brute = brute_min(bd["cx"], bd["M0"], 30000)
        self.assertGreater(bd["B"], 0.0)
        self.assertLessEqual(bd["B"], brute[0] * (1 + 1e-9))

    def test_s24_controls_at_reduced_range(self):
        # golden minimum over the full 200000 is 0.1553 (script check);
        # here just the ordering engineered << golden at 30000.
        g = brute_min(Ctx(GOLDEN), 1, 30000)[0]
        e = brute_min(Ctx(float(ENG_FRAC)), 1, 30000)[0]
        self.assertLess(e, g / 10)


class TestContinuedFractions(unittest.TestCase):
    def test_engineered_fraction(self):
        self.assertEqual(ENG_FRAC, Fraction(242055, 2200498))
        self.assertEqual(from_cf([0, 1, 1, 1]), Fraction(2, 3))

    def test_convergents_golden_are_fibonacci(self):
        frac = Fraction(GOLDEN).limit_denominator(10 ** 6)
        qs = [q for _p, q, _a in convergents(frac, 5000) if q <= 5000]
        self.assertEqual(qs[:6], [1, 1, 2, 3, 5, 8])

    def test_homogeneous_bound(self):
        self.assertGreaterEqual(homogeneous_min(GOLDEN, 5000),
                                1.0 / 3 - 1e-9)
        self.assertGreaterEqual(homogeneous_min(SQRT2M1, 5000),
                                1.0 / 4 - 1e-9)


if __name__ == "__main__":
    unittest.main()
