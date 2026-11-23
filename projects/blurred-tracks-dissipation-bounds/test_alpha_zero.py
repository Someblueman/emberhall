"""Tests for alpha_zero (DERIVATION s23): alpha != 0 always."""
from alpha_zero import alpha_data
from general_tracks import FROZEN_GENERAL


def test_alpha_formula_and_adjugate_bracket():
    adef, aform, d0, bracket, bracket_hat = alpha_data(
        FROZEN_GENERAL["A"], FROZEN_GENERAL["Dm"], 0.9, 0.45)
    assert abs(adef - aform) < 1e-9
    assert abs(bracket_hat - bracket) < 1e-9
    assert bracket > 0
    t = adef * d0 / 1j
    assert abs(t.imag) < 1e-9 and abs(t.real) > 0.1


def test_alpha_nonzero_isotropic():
    adef, *_ = alpha_data([[-1.0, -2.0], [2.0, -1.0]],
                          [[1.0, 0.0], [0.0, 1.0]], 0.9, 0.45)
    assert abs(adef) > 0.1
