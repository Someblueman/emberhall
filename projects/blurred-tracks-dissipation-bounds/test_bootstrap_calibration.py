"""Tests for bootstrap_calibration (DERIVATION s17).

The recorded coverage run lives in bootstrap_calibration.py itself;
these are fast structural checks: the winner fit recovers the fitted
motion's parameters in the right parametrization, and bootstrap
tolerances from the true parameters land near s16's population tau.
"""
from blurred_tracks import FROZEN
from bootstrap_calibration import bootstrap_tolerances, fit_winner
from tolerance_calibration import delta_variances, tau_of
from verify_blurred import simulate_frames

V, CAM = FROZEN["vortex"], FROZEN["camera"]


def test_fit_winner_parametrization():
    frames = simulate_frames(V, CAM, n_frames=4000, seed=424242 + 4000000,
                             sub=20)
    fit = fit_winner(frames, CAM)
    assert fit is not None
    win, _bs, v_fit, cam_fit = fit
    # s = D/kappa must reproduce the branch's stationary variance.
    assert abs(v_fit.s - win.s) < 1e-12
    assert v_fit.omega == win.omega
    assert cam_fit.ell2 >= 0.0


def test_bootstrap_tau_near_population_tau_at_truth():
    vR, _ve = delta_variances(V, CAM)
    tol = bootstrap_tolerances(V, CAM, 1000, m_star=1, seed0=888000,
                               b_boot=12)
    assert tol is not None
    tau_boot, slack_boot = tol
    assert tau_boot > 0 and slack_boot >= 0
    assert 0.4 <= tau_boot / tau_of(vR, 1000) <= 2.5
