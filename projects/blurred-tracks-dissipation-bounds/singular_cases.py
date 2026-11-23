#!/usr/bin/env python3
"""Singular Gamma_1 / singular U_m W_m cannot occur in the declared class.

U = int_0^eps e^{Au}du and W = int_0^eps e^{-Av}dv are both functions of A,
so UW = f(A) with scalar symbol, for each eigenvalue mu of A,

    f(mu) = (e^{mu eps} - 1)(1 - e^{-mu eps}) / mu^2
          = (e^{z} + e^{-z} - 2) / mu^2,   z = mu eps = x + i y.

|e^z + e^-z - 2| = 2 cosh(x) - 2 cos(y)  (square both sides), hence

    |f(mu)| = (2 cosh(x) - 2 cos(y)) / |mu|^2 >= (2 cosh(x) - 2)/|mu|^2 > 0

whenever x = Re(mu) eps != 0.  Every drift in the declared class is stable
(Re mu < 0), and so is every branch candidate A_m (Re mu_m = ln r / Delta
< 0 since |eig Phi| < 1).  Therefore UW, and with it
Gamma_1 = Phi U W Sigma / eps^2 (Phi and Sigma invertible: Sigma is SPD
because Dm is), is nonsingular for every latent motion and every branch
in the class -- no singular handling is needed, and an observed singular
Gamma_1 certifies data outside the declared class (or finite-sample noise).

What *can* happen is ill-conditioning: |f| is small when kappa*eps is
small and omega*eps is near a multiple of 2 pi (weak damping, rotation
completing whole turns inside one exposure).  This script verifies the
symbol formula, sweeps seeded random stable drifts, exhibits the
ill-conditioned regime honestly, and checks the refusal path for a
manufactured singular Gamma_1.
"""
from __future__ import annotations

import cmath
import math
import random
import sys

from general_tracks import (FROZEN_GENERAL, GeneralVortex, branch_drifts,
                            int_exp, inverse2, matmul, scale)

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def det2(M):
    return M[0][0] * M[1][1] - M[0][1] * M[1][0]


def symbol_f(mu, eps):
    z = mu * eps
    return (cmath.exp(z) + cmath.exp(-z) - 2.0) / mu ** 2


def eigenpair(A):
    (a, b), (c, d) = A
    tr, det = a + d, a * d - b * c
    sq = cmath.sqrt(complex(tr * tr / 4.0 - det))
    return tr / 2 + sq, tr / 2 - sq


def propagator_from_covariances(G1, G2):
    """Phi = G2 G1^{-1}, refusing (near-)singular G1 instead of dividing."""
    n1 = max(abs(x) for row in G1 for x in row)
    if n1 == 0.0 or abs(det2(G1)) <= 1e-12 * n1 * n1:
        raise ValueError("Gamma_1 singular: outside the declared class "
                         "(stable A, SPD Dm, eps > 0 give det Gamma_1 != 0)")
    return matmul(G2, inverse2(G1))


def main() -> int:
    eps = 0.45
    cases = [
        FROZEN_GENERAL["A"],
        [[-1.5, 0.4], [0.4, -0.8]],
        [[-1.0, 1.0], [0.0, -1.0]],          # defective
        [[-0.7, -3.0], [3.0, -0.7]],
        [[-2.0, 0.0], [0.0, -0.5]],
    ]
    err = 0.0
    for A in cases:
        UW = matmul(int_exp(A, eps), int_exp(scale(A, -1.0), eps))
        m1, m2 = eigenpair(A)
        err = max(err, abs(det2(UW) - (symbol_f(m1, eps) * symbol_f(m2, eps)).real))
        for mu in (m1, m2):
            z = mu * eps
            bound = (2 * math.cosh(z.real) - 2 * math.cos(z.imag)) / abs(mu) ** 2
            err = max(err, abs(abs(symbol_f(mu, eps)) - bound))
    check("det(UW) = f(mu1) f(mu2) and |f| closed form", err < 1e-10,
          f"(max err {err:.1e}, incl. a defective A)")

    # every branch candidate of the frozen general example: |f(mu_m)| > 0
    fg = FROZEN_GENERAL
    g = GeneralVortex(fg["A"], fg["Dm"])
    G1 = g.observed_cov_matrix(fg["Delta"], fg["eps"], fg["ell2"], 1)
    G2 = g.observed_cov_matrix(fg["Delta"], fg["eps"], fg["ell2"], 2)
    Phi = propagator_from_covariances(G1, G2)
    worst = 1e9
    for _, Am in branch_drifts(Phi, fg["Delta"], range(-60, 61)):
        mu, _ = eigenpair(Am)
        worst = min(worst, abs(symbol_f(mu, fg["eps"])))
        UW = matmul(int_exp(Am, fg["eps"]), int_exp(scale(Am, -1.0), fg["eps"]))
        assert det2(UW) != 0.0
    check("all branch candidates m in [-60,60] have nonsingular U_m W_m",
          worst > 0, f"(min |f(mu_m)| {worst:.3e}; > 0 for all m by Re mu < 0)")

    rng = random.Random(20261123)
    min_det = 1e9
    for _ in range(200):
        A = [[rng.uniform(-3, 0.2), rng.uniform(-3, 3)],
             [rng.uniform(-3, 3), rng.uniform(-3, 0.2)]]
        m1, m2 = eigenpair(A)
        if m1.real >= -0.05 or m2.real >= -0.05:
            continue
        Dm = [[1.0, 0.2], [0.2, 0.8]]
        gv = GeneralVortex(A, Dm)
        d1 = det2(gv.observed_cov_matrix(0.9, 0.45, 0.03, 1))
        assert d1 != 0.0
        min_det = min(min_det, abs(d1))
    check("seeded sweep of stable drifts: det Gamma_1 never 0",
          min_det > 0, f"(min |det Gamma_1| {min_det:.3e} over the sweep)")

    # honest ill-conditioning: kappa eps small, omega eps = 2 pi
    A_bad = [[-0.05, -2 * math.pi / 0.45], [2 * math.pi / 0.45, -0.05]]
    mu, _ = eigenpair(A_bad)
    f_bad = abs(symbol_f(mu, 0.45))
    gv = GeneralVortex(A_bad, [[1.0, 0.0], [0.0, 1.0]])
    d_bad = abs(det2(gv.observed_cov_matrix(0.9, 0.45, 0.03, 1)))
    check("near-singular regime is conditioning, not singularity",
          0 < f_bad < 1e-3 and d_bad > 0,
          f"(|f| {f_bad:.2e} at kappa*eps=0.0225, omega*eps=2pi; "
          f"|det Gamma_1| {d_bad:.2e} > 0)")

    try:
        propagator_from_covariances([[1.0, 2.0], [0.5, 1.0]],
                                    [[0.3, 0.1], [0.0, 0.2]])
        refused = False
    except ValueError:
        refused = True
    check("manufactured singular Gamma_1 is refused with a reason", refused)

    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
