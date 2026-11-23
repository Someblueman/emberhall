"""Tests for scalar_phi_search (DERIVATION s22)."""
import math

from general_tracks import GeneralVortex, inverse2, matmul
from real_logs import compatibility, family_drift
from scalar_phi_search import joint_residual, minimize_branch


def _setup():
    Delta, eps, ell2 = 1.0, 0.5, 0.03
    A = family_drift(-1.0, math.pi, 0.0, 0.0, Delta)
    g = GeneralVortex(A, [[1.0, 0.3], [0.3, 0.6]])
    G0 = g.observed_cov_matrix(Delta, eps, ell2, 0)
    G1 = g.observed_cov_matrix(Delta, eps, ell2, 1)
    G2 = g.observed_cov_matrix(Delta, eps, ell2, 2)
    Phi = matmul(G2, inverse2(G1))
    s = max(1.0, max(abs(G0[i][j]) for i in range(2) for j in range(2)))
    return A, G0, G1, Phi, Delta, eps, s


def test_truth_joint_residual_is_zero():
    A, G0, G1, Phi, Delta, eps, s = _setup()
    assert joint_residual(compatibility(A, G0, G1, Phi, Delta, eps), s) < 1e-16


def test_other_branch_rival_stays_separated():
    A, G0, G1, Phi, Delta, eps, s = _setup()
    v, *_ = minimize_branch(3 * math.pi, -1.0, G0, G1, Phi, Delta, eps, s)
    assert v > 1e-2
