#!/usr/bin/env python3
"""All real logarithms of a 2x2 propagator Phi, classified (DERIVATION s11).

Elementary classification used here.  Any logarithm L of Phi commutes with
Phi = exp(L).  Unless Phi = lam*I is scalar, Phi is non-derogatory and its
centralizer is the polynomials {aI + b Phi}; hence every logarithm is a
polynomial in Phi and is determined by scalar log branches on the
eigenvalues.  A real L needs its spectrum closed under conjugation:

- distinct real lam1 != lam2, both > 0: the only conjugation-closed branch
  choice is k1 = k2 = 0 -> unique real log (the primary one).  Pairing
  ln lam1 + 2 pi i k with its conjugate would need lam1 = lam2.
- distinct real with a negative eigenvalue: its log has imaginary part an
  odd multiple of pi, never real and never the conjugate of the other
  branch (magnitudes / parity mismatch) -> no real logarithm, even when
  both eigenvalues are negative.
- defective (one Jordan block) lam: a log exists (polynomial) with scalar
  branch on lam; real iff lam > 0 with branch 0 -> unique real log
  ln(lam) I + (Phi - lam I)/lam; none for lam < 0.
- Phi = lam I scalar: the centralizer is everything, and there is a
  continuous family: L = ln|lam| I + N with N^2 = -beta^2 I, beta =
  2 pi k (lam > 0, k >= 1; k = 0 gives the scalar drift) or
  beta = pi (2k+1) (lam < 0).  N = [[a, b], [c, -a]], a^2 + bc = -beta^2.

So outside the scalar case the branch candidate list for real spectrum is
either a single drift or empty -- there are no hidden non-primary real
logarithms for distinct positive eigenvalues.  In the scalar case this
script exhibits the family and runs the full compatibility test on frozen
examples: the extra motions are real logarithms of the same Phi but (in
these examples) do not fit the same film.
"""
from __future__ import annotations

import cmath
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


def classify_phi(Phi):
    """Return (kind, eigenvalues). kind in {complex_pair, distinct_real,
    scalar, defective}."""
    (a, b), (c, d) = Phi
    tr, det = a + d, a * d - b * c
    disc = tr * tr / 4.0 - det
    if disc < -1e-14:
        sq = cmath.sqrt(complex(disc))
        return "complex_pair", (tr / 2 + sq, tr / 2 - sq)
    if disc > 1e-14:
        sq = math.sqrt(disc)
        return "distinct_real", (tr / 2 + sq, tr / 2 - sq)
    lam = tr / 2.0
    off = max(abs(b), abs(c), abs(a - lam), abs(d - lam))
    return ("scalar" if off < 1e-12 else "defective"), (lam, lam)


def real_log_candidates(Phi, Delta):
    """('unique', [A]) | ('none', reason) | ('family', (alpha, betas)) |
    ('complex', None) for the complex-eigenvalue branches of s7.
    For 'family', candidate drifts are (alpha I + N)/Delta with
    N = [[a,b],[c,-a]], a^2+bc = -beta^2 for beta in betas."""
    kind, lams = classify_phi(Phi)
    if kind == "complex_pair":
        return "complex", None
    if kind == "distinct_real":
        lam1, lam2 = lams
        if lam1 <= 0 or lam2 <= 0:
            return "none", "a negative eigenvalue has no conjugation-closed branch"
        I2 = eye(2)
        num = add(scale(add(Phi, I2, -lam2), math.log(lam1)),
                  scale(add(Phi, I2, -lam1), math.log(lam2)), -1.0)
        return "unique", [scale(scale(num, 1.0 / (lam1 - lam2)), 1.0 / Delta)]
    if kind == "defective":
        lam = lams[0]
        if lam <= 0:
            return "none", "single Jordan block on a negative eigenvalue"
        L = add(scale(eye(2), math.log(lam)), add(Phi, eye(2), -lam), 1.0 / lam)
        return "unique", [scale(L, 1.0 / Delta)]
    lam = lams[0]  # scalar
    if lam == 0:
        return "none", "singular Phi is not an exponential"
    if lam > 0:
        return "family", (math.log(lam), [2 * math.pi * k for k in range(0, 4)])
    return "family", (math.log(-lam), [math.pi * (2 * k + 1) for k in range(0, 3)])


def family_drift(alpha, beta, t, phi, Delta):
    """Drift (alpha I + N)/Delta, N similar to beta*J via stretch t and
    rotation phi: N = R(phi) diag-stretch(beta J) R(-phi)."""
    if beta == 0.0:
        return scale(eye(2), alpha / Delta)
    Nt = [[0.0, -beta * math.exp(2 * t)], [beta * math.exp(-2 * t), 0.0]]
    cp, sp = math.cos(phi), math.sin(phi)
    R = [[cp, -sp], [sp, cp]]
    N = matmul(matmul(R, Nt), transpose(R))
    return scale(add(scale(eye(2), alpha), N), 1.0 / Delta)


def compatibility(Ac, G0, G1, Phi, Delta, eps):
    """Residuals for candidate drift Ac against observed covariances."""
    U = int_exp(Ac, eps)
    W = int_exp(scale(Ac, -1.0), eps)
    S = scale(matmul(inverse2(matmul(U, W)), matmul(inverse2(Phi), G1)), eps ** 2)
    sym = abs(S[0][1] - S[1][0])
    Dm = scale(add(matmul(Ac, S), matmul(S, transpose(Ac))), -0.5)
    U2S = matmul(int_exp_weighted(Ac, eps), S)
    P0 = scale(add(U2S, transpose(U2S)), 1.0 / eps ** 2)
    ell_a, ell_b = G0[0][0] - P0[0][0], G0[1][1] - P0[1][1]
    detS = S[0][0] * S[1][1] - S[0][1] * S[1][0]
    detD = Dm[0][0] * Dm[1][1] - Dm[0][1] * Dm[1][0]
    return {
        "sym": sym, "detS": detS, "s00": S[0][0], "detDm": detD,
        "dm00": Dm[0][0], "ell_split": abs(ell_a - ell_b),
        "ell2": 0.5 * (ell_a + ell_b),
        "offdiag": abs(G0[0][1] - P0[0][1]),
    }


def passes(r):
    return (r["sym"] < 1e-8 and r["detS"] > 0 and r["s00"] > 0
            and r["detDm"] > 0 and r["dm00"] > 0 and r["ell2"] >= -1e-9
            and r["ell_split"] < 1e-8 and r["offdiag"] < 1e-8)


def _phi_and_cov(A, Dm, Delta, eps, ell2):
    g = GeneralVortex(A, Dm)
    G0 = g.observed_cov_matrix(Delta, eps, ell2, 0)
    G1 = g.observed_cov_matrix(Delta, eps, ell2, 1)
    G2 = g.observed_cov_matrix(Delta, eps, ell2, 2)
    return g, G0, G1, matmul(G2, inverse2(G1))


def scalar_example(name, A, Delta, true_beta):
    Dm = [[1.0, 0.3], [0.3, 0.6]]
    eps, ell2 = 0.5 * Delta, 0.03
    g, G0, G1, Phi = _phi_and_cov(A, Dm, Delta, eps, ell2)
    kind, payload = real_log_candidates(Phi, Delta)
    check(f"{name}: Phi is scalar", kind == "family",
          f"(Phi00={Phi[0][0]:+.4f}, offdiag {max(abs(Phi[0][1]), abs(Phi[1][0])):.1e})")
    alpha, betas = payload
    worst_rival = 1e9
    n_pass = 0
    for beta in betas:
        for i in range(-6, 7):
            for j in range(12):
                t, phi = 0.25 * i, math.pi * j / 12
                if beta == 0.0 and (i or j):
                    continue
                Ac = family_drift(alpha, beta, t, phi, Delta)
                E = expm(scale(Ac, Delta))
                err = max(abs(E[p][q] - Phi[p][q]) for p in range(2) for q in range(2))
                assert err < 1e-9, (name, beta, t, phi, err)
                r = compatibility(Ac, G0, G1, Phi, Delta, eps)
                if passes(r):
                    n_pass += 1
                near_truth = max(abs(Ac[p][q] - A[p][q])
                                 for p in range(2) for q in range(2)) < 1e-9
                if not near_truth:
                    worst_rival = min(worst_rival, r["sym"])
    r_true = compatibility(A, G0, G1, Phi, Delta, eps)
    check(f"{name}: true drift passes compatibility", passes(r_true),
          f"(sigma {g.dissipation():.4f})")
    check(f"{name}: every scanned family member is a real log of Phi", True,
          "(exp(A_c Delta) = Phi asserted on the grid)")
    check(f"{name}: only the true drift passes on grid", worst_rival > 1e-3,
          f"({n_pass} passes; min rival symmetry residual {worst_rival:.4f})")


def main() -> int:
    # distinct positive: unique real log, recovers s9 example
    g, G0, G1, Phi = _phi_and_cov([[-1.5, 0.4], [0.4, -0.8]],
                                  [[1.0, 0.5], [0.5, 1.0]], 0.9, 0.45, 0.03)
    kind, cands = real_log_candidates(Phi, 0.9)
    err = max(abs(cands[0][i][j] - g.A[i][j]) for i in range(2) for j in range(2))
    check("distinct positive: unique real log recovers A",
          kind == "unique" and err < 1e-10, f"(max err {err:.1e})")

    for label, P in (("mixed signs", [[-0.5, 0.1], [0.0, 0.3]]),
                     ("both negative distinct", [[-0.5, 0.1], [0.0, -0.25]]),
                     ("negative Jordan block", [[-0.5, 1.0], [0.0, -0.5]])):
        kind, why = real_log_candidates(P, 1.0)
        check(f"no real logarithm: {label}", kind == "none", f"({why})")

    # defective positive: unique real log via the derivative term
    A = [[-1.0, 1.0], [0.0, -1.0]]
    g, G0, G1, Phi = _phi_and_cov(A, [[1.0, 0.3], [0.3, 0.6]], 0.9, 0.45, 0.03)
    kind, cands = real_log_candidates(Phi, 0.9)
    err = max(abs(cands[0][i][j] - A[i][j]) for i in range(2) for j in range(2))
    r = compatibility(cands[0], G0, G1, Phi, 0.9, 0.45)
    check("defective positive: unique real log recovers A and fits",
          kind == "unique" and err < 1e-9 and passes(r), f"(max err {err:.1e})")

    # scalar Phi: continuous families of genuine extra logarithms
    scalar_example("scalar negative (beta=pi truth)",
                   [[-1.0, -math.pi], [math.pi, -1.0]], 1.0, math.pi)
    scalar_example("scalar positive (beta=2pi truth)",
                   [[-1.0, -2 * math.pi], [2 * math.pi, -1.0]], 1.0, 2 * math.pi)

    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
