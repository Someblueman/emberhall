"""Tests for general_finite_record (DERIVATION s18)."""
import math
import statistics

from general_finite_record import (branch_quantities_general, delta_sds,
                                   delta_variance_R, empirical_Gamma,
                                   simulate_general_frames,
                                   symmetry_residual)
from general_tracks import FROZEN_GENERAL, GeneralVortex

FG = FROZEN_GENERAL
G = GeneralVortex(FG["A"], FG["Dm"])
D_, E_, L_ = FG["Delta"], FG["eps"], FG["ell2"]


def test_population_residual_zero_only_at_true_branch():
    Gs = [G.observed_cov_matrix(D_, E_, L_, k) for k in (0, 1, 2)]
    assert abs(symmetry_residual(*Gs, D_, E_, 0)) < 1e-12
    for m in (-2, -1, 1, 2):
        assert abs(symmetry_residual(*Gs, D_, E_, m)) > 0.1


def test_simulator_recovers_population_covariances():
    frames = simulate_general_frames(G, D_, E_, L_, 16000, seed=31337)
    for k in (0, 1):
        Gh = empirical_Gamma(frames, k)
        Gp = G.observed_cov_matrix(D_, E_, L_, k)
        err = max(abs(Gh[i][j] - Gp[i][j]) for i in range(2)
                  for j in range(2))
        scale = max(abs(Gp[i][j]) for i in range(2) for j in range(2))
        assert err < 0.08 * scale


def test_population_eligibility_quantities():
    Gs = [G.observed_cov_matrix(D_, E_, L_, k) for k in (0, 1, 2)]
    q = branch_quantities_general(*Gs, D_, E_, 0)
    assert abs(q["R"]) < 1e-12 and abs(q["off"]) < 1e-9
    assert abs(q["eq_ell"]) < 1e-9 and abs(q["ell"] - L_) < 1e-9
    assert q["lam_S"] > 0 and q["lam_D"] > 0
    sds = delta_sds(G, D_, E_, L_, ("off", "ell", "lam_S"))
    assert all(s > 0 for s in sds.values())


def test_delta_variance_positive_and_mc_consistent():
    vR = delta_variance_R(G, D_, E_, L_)
    assert vR > 0
    Rs = []
    for r in range(16):
        frames = simulate_general_frames(G, D_, E_, L_, 1000,
                                         seed=606000 + r)
        Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
        Rs.append(symmetry_residual(*Gh, D_, E_, 0))
    ratio = statistics.stdev(Rs) / math.sqrt(vR / 1000)
    assert 0.55 <= ratio <= 1.7
