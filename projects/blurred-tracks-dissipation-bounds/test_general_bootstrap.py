"""Tests for general_bootstrap (DERIVATION s20)."""
import math

from general_bootstrap import bootstrap_tau, fit_from_covariances
from general_finite_record import empirical_Gamma, simulate_general_frames
from general_tracks import FROZEN_GENERAL, GeneralVortex

FG = FROZEN_GENERAL
G = GeneralVortex(FG["A"], FG["Dm"])
D_, E_, L_ = FG["Delta"], FG["eps"], FG["ell2"]


def test_population_fit_recovers_true_motion():
    Gs = [G.observed_cov_matrix(D_, E_, L_, k) for k in (0, 1, 2)]
    m_star, residuals, fitted = fit_from_covariances(*Gs, D_, E_)
    assert m_star == 0
    assert abs(residuals[0]) < 1e-12
    gv = fitted["vortex"]
    err_A = max(abs(gv.A[i][j] - FG["A"][i][j])
                for i in range(2) for j in range(2))
    err_S = max(abs(gv.Sigma[i][j] - G.Sigma[i][j])
                for i in range(2) for j in range(2))
    assert err_A < 1e-9 and err_S < 1e-9
    assert abs(fitted["ell2"] - L_) < 1e-9
    assert abs(gv.dissipation() - G.dissipation()) < 1e-9


def test_film_fit_and_bootstrap_tau_positive():
    frames = simulate_general_frames(G, D_, E_, L_, 2000, seed=4242)
    Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
    fit = fit_from_covariances(*Gh, D_, E_)
    assert fit is not None
    m_star, _residuals, fitted = fit
    tau = bootstrap_tau(fitted, D_, E_, 500, m_star, seed0=99000,
                        b_boot=10)
    assert tau is not None and tau > 0
    # tau_boot shrinks with N for a fixed fit (same bootstrap design).
    tau_big = bootstrap_tau(fitted, D_, E_, 2000, m_star, seed0=99000,
                            b_boot=10)
    assert 0 < tau_big < 1.5 * tau / math.sqrt(2.0)
