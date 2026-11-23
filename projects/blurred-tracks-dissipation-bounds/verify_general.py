#!/usr/bin/env python3
"""Independent verification of general_tracks.py (milestone 2).

Routes: (1) quadrature of the defining double integrals using only the
latent covariance; (2) exact recovery of the milestone-1 isotropic formulas;
(3) branch test in the frozen non-isotropic example: recover Phi from
Gamma_2 Gamma_1^{-1}, build every real logarithm branch in m in [-60, 60],
solve for the Sigma each branch would need, and test symmetry, positive
definiteness of Sigma and of the implied diffusion, and zero lag.
The tail |m| > 60 is NOT excluded here (see DERIVATION.md section 7).
"""
from __future__ import annotations

import sys

from blurred_tracks import Camera, Vortex, observed_cov_matrix
from general_tracks import (FROZEN_GENERAL, GeneralVortex, add, branch_drifts,
                            expm, int_exp, int_exp_weighted, inverse2, matmul,
                            scale, transpose)

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def quadrature(g: GeneralVortex, Delta, eps, ell2, k, n=600):
    h = eps / n
    acc = [[0.0, 0.0], [0.0, 0.0]]
    for i in range(n + 1):
        wi = 0.5 if i in (0, n) else 1.0
        for j in range(n + 1):
            wj = 0.5 if j in (0, n) else 1.0
            C = g.latent_cov_matrix(k * Delta + (i - j) * h)
            for a in (0, 1):
                for b in (0, 1):
                    acc[a][b] += wi * wj * C[a][b]
    out = scale(acc, h * h / eps ** 2)
    if k == 0:
        out[0][0] += ell2
        out[1][1] += ell2
    return out


def is_spd(S) -> bool:
    return S[0][0] > 0 and S[0][0] * S[1][1] - S[0][1] * S[1][0] > 0


def main() -> int:
    fg = FROZEN_GENERAL
    D_, e_, l_ = fg["Delta"], fg["eps"], fg["ell2"]
    g = GeneralVortex(fg["A"], fg["Dm"])

    max_err = 0.0
    for k in (0, 1, 2):
        Q = quadrature(g, D_, e_, l_, k)
        G = g.observed_cov_matrix(D_, e_, l_, k)
        max_err = max(max_err, max(abs(Q[a][b] - G[a][b])
                                   for a in (0, 1) for b in (0, 1)))
    check("quadrature vs augmented-exponential formulas", max_err < 1e-5,
          f"(max abs err {max_err:.2e})")

    iso = GeneralVortex([[-1.0, -3.9], [3.9, -1.0]], [[1.0, 0.0], [0.0, 1.0]])
    v = Vortex(1.0, 3.9, 1.0)
    cam = Camera(1.0, 0.5, 0.04)
    err = max(abs(iso.observed_cov_matrix(1.0, 0.5, 0.04, k)[a][b]
                  - observed_cov_matrix(v, cam, k)[a][b])
              for k in (0, 1, 2) for a in (0, 1) for b in (0, 1))
    check("isotropic special case matches milestone 1", err < 1e-12,
          f"(max abs err {err:.2e}; sigma {iso.dissipation():.6f} vs 30.42)")

    G0 = g.observed_cov_matrix(D_, e_, l_, 0)
    G1 = g.observed_cov_matrix(D_, e_, l_, 1)
    G2 = g.observed_cov_matrix(D_, e_, l_, 2)
    Phi = matmul(G2, inverse2(G1))
    Phi_true = expm(scale(fg["A"], D_))
    perr = max(abs(Phi[a][b] - Phi_true[a][b]) for a in (0, 1) for b in (0, 1))
    check("propagator recovered as Gamma_2 Gamma_1^{-1}", perr < 1e-12,
          f"(max abs err {perr:.2e})")

    compatible = []
    min_sym = (float("inf"), None)
    for m, Am in branch_drifts(Phi, D_, range(-60, 61)):
        U = int_exp(Am, e_)
        W = int_exp(scale(Am, -1.0), e_)
        try:
            S = scale(matmul(inverse2(matmul(U, W)),
                             matmul(inverse2(Phi), G1)), e_ ** 2)
        except ValueError:
            continue
        sym = abs(S[0][1] - S[1][0])
        if m != 0 and sym < min_sym[0]:
            min_sym = (sym, m)
        Ss = [[S[0][0], (S[0][1] + S[1][0]) / 2],
              [(S[0][1] + S[1][0]) / 2, S[1][1]]]
        Dm = scale(add(matmul(Am, Ss), matmul(Ss, transpose(Am))), -0.5)
        U2S = matmul(int_exp_weighted(Am, e_), Ss)
        P0 = scale(add(U2S, transpose(U2S)), 1.0 / e_ ** 2)
        ell_a, ell_b = G0[0][0] - P0[0][0], G0[1][1] - P0[1][1]
        if (sym < 1e-9 and is_spd(Ss) and is_spd(Dm)
                and abs(G0[0][1] - P0[0][1]) < 1e-9
                and abs(ell_a - ell_b) < 1e-9 and ell_a >= -1e-12):
            gv = GeneralVortex.__new__(GeneralVortex)
            gv.A, gv.Dm, gv.Sigma = Am, Dm, Ss
            compatible.append((m, ell_a, gv.dissipation()))
    print(f"  compatible branches in [-60, 60]: {compatible}")
    print(f"  smallest symmetry residual among excluded: {min_sym[0]:.3f} (m={min_sym[1]})")
    check("only true branch compatible in window",
          len(compatible) == 1 and compatible[0][0] == 0
          and abs(compatible[0][1] - l_) < 1e-9
          and abs(compatible[0][2] - g.dissipation()) < 1e-9)
    print("  NOTE: |m| > 60 tail and real-eigenvalue logarithms are open; "
          "see DERIVATION.md section 7.")
    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
