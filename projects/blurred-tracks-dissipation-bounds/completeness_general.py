#!/usr/bin/env python3
"""All-branch completeness for the frozen general example (eps/Delta = 1/2).

Argument (DERIVATION.md section 7): every logarithm branch A_m shares the
eigenvectors of Phi.  In that eigenbasis, with mu_m = (ln r + i(theta +
2 pi m))/Delta the eigenvalue of A_m, the Sigma that branch m would need is

    Sigma_m = eps^2 P diag(d_m, conj d_m) Ghat P^{-1},
    d_m = mu_m^2 / (e^{mu_m eps} + e^{-mu_m eps} - 2),
    Ghat = P^{-1} Phi^{-1} Gamma_1 P        (fixed, m-independent).

For eps/Delta = 1/2, e^{mu_m eps} = (-1)^m c with c = sqrt(r) e^{i theta/2},
so the denominator of d_m depends only on the parity of m, while mu_m^2 is
quadratic in m.  The symmetry residual R(m) = (Sigma_m)_01 - (Sigma_m)_10
is a fixed real linear form in (d_m, conj d_m); hence per parity R is an
exact real quadratic polynomial in m.  A branch can be compatible only if
R(m) = 0.  This script: (1) cross-checks the eigenbasis Sigma_m against
general_tracks for small m; (2) fits each parity quadratic from three m
values and verifies it at further m, including |m| = 1000 evaluated in the
eigenbasis; (3) finds all real roots and confirms no integer m (other than
the true branch, already fully verified) is a root.
"""
from __future__ import annotations

import cmath
import math
import sys

from general_tracks import (FROZEN_GENERAL, GeneralVortex, branch_drifts,
                            int_exp, inverse2, matmul, scale)

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def cmul(A, B):
    return [[sum(A[i][t] * B[t][j] for t in range(2)) for j in range(2)]
            for i in range(2)]


def main() -> int:
    fg = FROZEN_GENERAL
    D_, e_, l_ = fg["Delta"], fg["eps"], fg["ell2"]
    g = GeneralVortex(fg["A"], fg["Dm"])
    G1 = g.observed_cov_matrix(D_, e_, l_, 1)
    G2 = g.observed_cov_matrix(D_, e_, l_, 2)
    Phi = matmul(G2, inverse2(G1))

    (a, b), (c_, d_) = Phi
    tr, det = a + d_, a * d_ - b * c_
    lam1 = tr / 2 + cmath.sqrt(complex(tr * tr / 4 - det))
    r, theta = abs(lam1), cmath.phase(lam1)
    if abs(b) > abs(c_):
        v1 = (complex(b), lam1 - a)
    else:
        v1 = (lam1 - d_, complex(c_))
    v2 = (v1[0].conjugate(), v1[1].conjugate())
    P = [[v1[0], v2[0]], [v1[1], v2[1]]]
    detP = v1[0] * v2[1] - v2[0] * v1[1]
    Pinv = [[v2[1] / detP, -v2[0] / detP], [-v1[1] / detP, v1[0] / detP]]
    PhiInvG1 = matmul(inverse2(Phi), G1)
    Ghat = cmul(cmul(Pinv, [[complex(x) for x in row] for row in PhiInvG1]), P)

    def sigma_eigen(m: int):
        mu = (math.log(r) + 1j * (theta + 2 * math.pi * m)) / D_
        z = mu * e_
        dm = mu ** 2 / (cmath.exp(z) + cmath.exp(-z) - 2.0)
        Dg = [[dm, 0j], [0j, dm.conjugate()]]
        S = cmul(cmul(P, cmul(Dg, Ghat)), Pinv)
        return [[(e_ ** 2 * S[i][j]).real for j in range(2)] for i in range(2)]

    def sigma_direct(m: int):
        Am = dict(branch_drifts(Phi, D_, [m]))[m]
        U = int_exp(Am, e_)
        W = int_exp(scale(Am, -1.0), e_)
        return scale(matmul(inverse2(matmul(U, W)), matmul(inverse2(Phi), G1)),
                     e_ ** 2)

    err = 0.0
    for m in range(-6, 7):
        Se, Sd = sigma_eigen(m), sigma_direct(m)
        err = max(err, max(abs(Se[i][j] - Sd[i][j])
                           for i in range(2) for j in range(2)))
    check("eigenbasis Sigma_m matches augmented-exponential route",
          err < 1e-8, f"(max abs err {err:.2e}, m in [-6,6])")

    def R(m: int) -> float:
        S = sigma_eigen(m)
        return S[0][1] - S[1][0]

    all_int_roots = []
    for parity, base in ((0, 0), (1, 1)):
        ms = [base, base + 2, base + 4]
        ys = [R(m) for m in ms]
        # quadratic through three points (Lagrange, evaluated stably)
        def quad(x, ms=ms, ys=ys):
            tot = 0.0
            for i in range(3):
                term = ys[i]
                for j in range(3):
                    if i != j:
                        term *= (x - ms[j]) / (ms[i] - ms[j])
                tot += term
            return tot
        # coefficients A2 x^2 + A1 x + A0 via values at 0,1,2 (shift-free fit)
        A2 = (quad(2) - 2 * quad(1) + quad(0)) / 2
        A1 = quad(1) - quad(0) - A2
        A0 = quad(0)
        ver = max(abs(quad(m) - R(m)) / max(1.0, abs(R(m)))
                  for m in (base + 6, base - 8, 1000 + parity, -1000 - parity))
        check(f"parity {parity}: R is quadratic in m", ver < 1e-9,
              f"(rel err {ver:.2e}; A2={A2:.6f})")
        check(f"parity {parity}: leading coefficient nonzero", abs(A2) > 1e-6)
        disc = A1 * A1 - 4 * A2 * A0
        roots = []
        if disc >= 0:
            for sgn in (-1, 1):
                x = (-A1 + sgn * math.sqrt(disc)) / (2 * A2)
                roots.append(x)
                for cand in {math.floor(x), math.ceil(x)}:
                    if cand % 2 == parity and abs(R(cand)) < 1e-9:
                        all_int_roots.append(cand)
        print(f"  parity {parity}: real roots "
              f"{[f'{x:.4f}' for x in roots] or 'none'}")
    print(f"  integer roots of R over all m: {sorted(set(all_int_roots))}")
    check("only the true branch m=0 has R(m)=0 over all integers",
          sorted(set(all_int_roots)) == [0])
    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
