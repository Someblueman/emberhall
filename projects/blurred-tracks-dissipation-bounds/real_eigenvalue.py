#!/usr/bin/env python3
"""Real-eigenvalue propagators: the primary-logarithm subcase.

If Phi = exp(A Delta) has distinct positive real eigenvalues lam1 != lam2,
its primary real logarithm is given by Sylvester's formula

    log Phi = [ln(lam1)(Phi - lam2 I) - ln(lam2)(Phi - lam1 I)]/(lam1-lam2)

and A = log(Phi)/Delta recovers the true drift when A itself is the
primary branch.  Frozen example: symmetric drift (real eigenvalues, no
rotation in A) with non-commuting diffusion, which still dissipates
(sigma > 0) -- a Brownian-gyrator-flavoured case.  Checks: Phi recovery,
primary-log recovery of A, full Sigma/Dm/ell^2/sigma reconstruction, and
that a negative-eigenvalue Phi is refused.

NOT claimed: non-primary real logarithms for positive spectrum (they need
not be polynomials in Phi) and any real logarithm for negative spectrum.
Those families remain open (DERIVATION.md section 7).
"""
from __future__ import annotations

import math
import sys

from general_tracks import (GeneralVortex, add, expm, eye, int_exp,
                            int_exp_weighted, inverse2, matmul, scale,
                            transpose)

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def primary_log(Phi):
    (a, b), (c, d) = Phi
    tr, det = a + d, a * d - b * c
    disc = tr * tr / 4 - det
    if disc <= 0:
        raise ValueError("need distinct real eigenvalues")
    lam1 = tr / 2 + math.sqrt(disc)
    lam2 = tr / 2 - math.sqrt(disc)
    if lam1 <= 0 or lam2 <= 0:
        raise ValueError("primary real log here needs positive eigenvalues")
    I2 = eye(2)
    num = add(scale(add(Phi, I2, -lam2), math.log(lam1)),
              scale(add(Phi, I2, -lam1), math.log(lam2)), -1.0)
    return scale(num, 1.0 / (lam1 - lam2)), (lam1, lam2)


def main() -> int:
    A = [[-1.5, 0.4], [0.4, -0.8]]
    Dm = [[1.0, 0.5], [0.5, 1.0]]
    Delta, eps, ell2 = 0.9, 0.45, 0.03
    g = GeneralVortex(A, Dm)
    print(f"frozen real-eigenvalue example: sigma = {g.dissipation():.6f}")
    check("dissipates despite symmetric drift", g.dissipation() > 0.01)

    G0 = g.observed_cov_matrix(Delta, eps, ell2, 0)
    G1 = g.observed_cov_matrix(Delta, eps, ell2, 1)
    G2 = g.observed_cov_matrix(Delta, eps, ell2, 2)
    Phi = matmul(G2, inverse2(G1))
    L, lams = primary_log(Phi)
    A_rec = scale(L, 1.0 / Delta)
    err = max(abs(A_rec[i][j] - A[i][j]) for i in range(2) for j in range(2))
    check("primary log recovers A", err < 1e-10,
          f"(eigenvalues {lams[0]:.4f}, {lams[1]:.4f}; max err {err:.2e})")
    back = expm(scale(A_rec, Delta))
    errb = max(abs(back[i][j] - Phi[i][j]) for i in range(2) for j in range(2))
    check("exp(log Phi) = Phi", errb < 1e-12, f"(max err {errb:.2e})")

    U = int_exp(A_rec, eps)
    W = int_exp(scale(A_rec, -1.0), eps)
    S = scale(matmul(inverse2(matmul(U, W)), matmul(inverse2(Phi), G1)),
              eps ** 2)
    Dm_rec = scale(add(matmul(A_rec, S), matmul(S, transpose(A_rec))), -0.5)
    U2S = matmul(int_exp_weighted(A_rec, eps), S)
    P0 = scale(add(U2S, transpose(U2S)), 1.0 / eps ** 2)
    gv = GeneralVortex.__new__(GeneralVortex)
    gv.A, gv.Dm, gv.Sigma = A_rec, Dm_rec, S
    ok = (max(abs(S[i][j] - g.Sigma[i][j]) for i in range(2) for j in range(2)) < 1e-9
          and max(abs(Dm_rec[i][j] - Dm[i][j]) for i in range(2) for j in range(2)) < 1e-9
          and abs((G0[0][0] - P0[0][0]) - ell2) < 1e-9
          and abs(gv.dissipation() - g.dissipation()) < 1e-9)
    check("Sigma, Dm, ell^2, sigma all reconstructed", ok,
          f"(sigma_rec {gv.dissipation():.6f})")

    try:
        primary_log([[-0.5, 0.0], [0.0, 0.25]])
        refused = False
    except ValueError:
        refused = True
    check("negative eigenvalue refused, not silently logged", refused)
    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
