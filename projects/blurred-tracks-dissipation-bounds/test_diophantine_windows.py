"""Tests for diophantine_windows (DERIVATION s24)."""
from fractions import Fraction

from completeness_rational import EigenResidual
from diophantine_windows import cf_value, min_scaled


def test_cf_value():
    assert cf_value([0, 9, 11]) == Fraction(11, 100)


def test_true_branch_residual_zero():
    er = EigenResidual(0.9, 0.45)
    assert abs(er.R(0)) < 1e-9


def test_golden_scaled_minimum_bounded_below_small_range():
    _, (v, _m) = min_scaled((5 ** 0.5 - 1) / 2, lo=100, hi=5000)
    assert v > 0.1
