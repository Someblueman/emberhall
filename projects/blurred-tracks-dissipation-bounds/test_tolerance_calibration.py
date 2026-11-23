"""Tests for tolerance_calibration (DERIVATION s16).

Fast checks of the derivation's moving parts: the Isserlis moment
covariances against a direct Monte Carlo of the estimators, the
delta-method scaling tau ~ 1/sqrt(N), and consistency of
branch_quantities with branches_from_covariances at the population
point.  The full recorded run (coverage on the s8 seeds) lives in
tolerance_calibration.py itself and RECORDED_RUN.md.
"""
import math
import statistics

from blurred_tracks import FROZEN, branches_from_covariances, observed_cov_complex
from tolerance_calibration import (branch_quantities, delta_variances,
                                   moment_covariances, slack_of, tau_of)
from verify_blurred import empirical_gamma, simulate_frames

V, CAM = FROZEN["vortex"], FROZEN["camera"]


def test_population_point_matches_branch_enumeration():
    g0 = observed_cov_complex(V, CAM, 0).real
    g1, g2 = (observed_cov_complex(V, CAM, k) for k in (1, 2))
    R, ell2 = branch_quantities([g0, g1.real, g1.imag, g2.real, g2.imag],
                                CAM, 1)
    _, _, bs = branches_from_covariances(g0, g1, g2, CAM.Delta, CAM.eps, [1])
    assert abs(R - bs[0].phase_residual) < 1e-12
    assert abs(ell2 - bs[0].ell2) < 1e-12
    assert abs(R) < 1e-12 and abs(ell2 - 0.04) < 1e-12


def test_moment_covariance_matches_monte_carlo():
    C, _P = moment_covariances(V, CAM)
    # N * Var(ghat_1) from the Isserlis sum vs simulation at N=1000.
    # sub=60 (finer than the house sub=20): the formula describes the
    # exact shutter-averaged process, and the trapezoid simulator at
    # sub=20 measurably inflates raw moment variances (~25%, s16).
    ests = []
    for r in range(32):
        frames = simulate_frames(V, CAM, n_frames=1000, seed=777000 + r,
                                 sub=60)
        ests.append(empirical_gamma(frames, 1))
    var_mc = statistics.variance([e.real for e in ests]) \
        + statistics.variance([e.imag for e in ests])
    var_formula = C[1, 1].real / 1000
    assert C[1, 1].real > 0 and abs(C[1, 1].imag) < 1e-9 * C[1, 1].real
    assert 0.65 <= var_mc / var_formula <= 1.45


def test_tau_scales_as_inverse_sqrt_n_and_is_positive():
    vR, ve = delta_variances(V, CAM)
    assert vR > 0 and ve > 0
    assert math.isclose(tau_of(vR, 4000), tau_of(vR, 1000) / 2.0)
    assert math.isclose(slack_of(ve, 16000), slack_of(ve, 1000) / 4.0)
    # The calibrated slack replaces s12's guessed 0.02; at these N the
    # guess was smaller than the derived value (see DERIVATION s16).
    assert slack_of(ve, 1000) > 0.02
