"""Tests for general_trapezoid_bias (DERIVATION s21)."""
from general_trapezoid_bias import measure
from general_tracks import FROZEN_GENERAL, GeneralVortex

FG = FROZEN_GENERAL
G = GeneralVortex(FG["A"], FG["Dm"])
D_, E_, L_ = FG["Delta"], FG["eps"], FG["ell2"]


def test_measure_sanity_at_fine_substeps():
    # Loose stochastic sanity: the recorded run carries the numbers.
    max_err, meanR, se = measure(G, D_, E_, L_, 40, n=1000, reps=12,
                                 seed0=135000)
    assert max_err < 0.05
    assert abs(meanR) < 6 * se + 0.05
