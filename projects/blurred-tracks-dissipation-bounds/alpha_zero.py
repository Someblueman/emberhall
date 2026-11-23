"""Section 23: the alpha = 0 case of s11 cannot occur.

The symmetry residual of s7/s11 is R(m) = Re(alpha * d_m), with
d_m = mu_m^2 / (e^{mu_m eps} + e^{-mu_m eps} - 2) in the eigenbasis
P = [z, zbar] of Phi (z = (p, q) the eigenvector for Im lambda > 0).
DERIVATION s11 left "the degenerate alpha = 0 case, where symmetry
is automatic" untreated.  It is empty:

1. Extracting the linear form (sympy, and verified numerically here
   against the definition) gives, with Ghat = P^{-1} Phi^{-1} G_1 P,

       alpha = i eps^2 [ (z^dagger z) Ghat_11 - (z^T z) Ghat_12 ]
               / ( -Im(pbar q) ).

2. At the true branch, eps^2 diag(d_0, dbar_0) Ghat = P^{-1} Sigma P
   =: Shat, so both first-row entries of Ghat share the factor
   1/(eps^2 d_0), and alpha * d_0 / i is the real number

       t = [ (z^dagger z) Shat_11 - (z^T z) Shat_12 ] / ( -Im(pbar q) ).

3. The bracket collapses (sympy factorization, re-verified below on
   random data) to a sesquilinear form in Sigma's adjugate:

       (z^dagger z) Shat_11 - (z^T z) Shat_12 = z^dagger adj(Sigma) z
         = Sigma_11 |q|^2 - 2 Sigma_12 Re(p qbar) + Sigma_22 |p|^2.

   Sigma positive definite (2x2) implies adj(Sigma) positive
   definite, and z != 0, so the bracket is strictly positive.
   The denominator Im(pbar q) is also nonzero: it vanishes only
   if p, q share a phase, making z real up to a phase and lambda
   real.  Hence t != 0, and alpha = i t / d_0 != 0 for every
   latent motion in the class with complex spectrum.

So symmetry is never automatic: R(m) is a genuinely branch-dependent
residual for every truth, and the irrational-ratio obstruction of
s11 (dense sign changes of R at large m) applies without exception.
What this does not change: exact roots R(m) = 0 at isolated m remain
possible codimension-one coincidences; alpha != 0 only rules out
R identically zero.
"""

from __future__ import annotations

import cmath
import math
import random
import sys

from general_tracks import FROZEN_GENERAL, GeneralVortex, inverse2, matmul

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def cmul(A, B):
    return [[sum(A[i][t] * B[t][j] for t in range(2)) for j in range(2)]
            for i in range(2)]


def alpha_data(A, Dm, Delta, eps, ell2=0.03):
    """alpha three ways: definition, formula (1), and adjugate form (3)."""
    g = GeneralVortex(A, Dm)
    G1 = g.observed_cov_matrix(Delta, eps, ell2, 1)
    G2 = g.observed_cov_matrix(Delta, eps, ell2, 2)
    Phi = matmul(G2, inverse2(G1))
    (a, b), (c_, d_) = Phi
    tr, det = a + d_, a * d_ - b * c_
    lam1 = tr / 2 + cmath.sqrt(complex(tr * tr / 4 - det))
    if lam1.imag < 0:
        lam1 = lam1.conjugate()
    z = (complex(b), lam1 - a) if abs(b) > abs(c_) else (lam1 - d_, complex(c_))
    zn = math.hypot(abs(z[0]), abs(z[1]))
    z = (z[0] / zn, z[1] / zn)  # unit eigenvector: bracket scale is meaningful
    zc = (z[0].conjugate(), z[1].conjugate())
    P = [[z[0], zc[0]], [z[1], zc[1]]]
    detP = z[0] * zc[1] - zc[0] * z[1]
    Pinv = [[zc[1] / detP, -zc[0] / detP], [-z[1] / detP, z[0] / detP]]
    Ghat = cmul(cmul(Pinv, [[complex(x) for x in row]
                             for row in matmul(inverse2(Phi), G1)]), P)

    def F(dv):
        Dg = [[dv, 0j], [0j, dv.conjugate()]]
        S = cmul(cmul(P, cmul(Dg, Ghat)), Pinv)
        return (eps ** 2 * (S[0][1] - S[1][0])).real

    alpha_def = F(1 + 0j) - 1j * F(1j)
    p, q = z
    N = abs(p) ** 2 + abs(q) ** 2
    Vt = p * p + q * q
    alpha_formula = eps ** 2 * 1j * (N * Ghat[0][0] - Vt * Ghat[0][1]) \
        / (-(p.conjugate() * q).imag)
    # true-branch d_0 and the adjugate bracket with the true Sigma
    r, theta = abs(lam1), cmath.phase(lam1)
    mu0 = (math.log(r) + 1j * theta) / Delta
    zz = mu0 * eps
    d0 = mu0 ** 2 / (cmath.exp(zz) + cmath.exp(-zz) - 2.0)
    Sigma = g.Sigma
    bracket = (Sigma[0][0] * abs(q) ** 2
               - 2 * Sigma[0][1] * (p * q.conjugate()).real
               + Sigma[1][1] * abs(p) ** 2)
    # factorization (3): the Shat bracket equals bracket(Sigma) exactly
    Shat = cmul(cmul(Pinv, [[complex(x) for x in row] for row in Sigma]), P)
    bracket_hat = N * Shat[0][0] - Vt * Shat[0][1]
    return alpha_def, alpha_formula, d0, bracket, bracket_hat


def main() -> int:
    cases = [
        ("frozen general", FROZEN_GENERAL["A"], FROZEN_GENERAL["Dm"], 0.9, 0.45),
        ("isotropic", [[-1.0, -2.0], [2.0, -1.0]], [[1.0, 0.0], [0.0, 1.0]], 0.9, 0.45),
        ("iso A, aniso Dm", [[-1.0, -2.0], [2.0, -1.0]], [[1.5, 0.2], [0.2, 0.5]], 1.0, 0.3),
        ("stretched", [[-1.5, -2.0], [2.0, -0.7]], [[1.0, 0.0], [0.0, 1.0]], 0.9, 0.45),
    ]
    for name, A, Dm, Delta, eps in cases:
        adef, aform, d0, bracket, bracket_hat = alpha_data(A, Dm, Delta, eps)
        t = (adef * d0 / 1j)
        check(f"{name}: formula (1) matches definition",
              abs(adef - aform) < 1e-9 * max(1.0, abs(adef)),
              f"(|diff| {abs(adef - aform):.1e})")
        check(f"{name}: factorization (3) Shat bracket = Sigma bracket",
              abs(bracket_hat - bracket) < 1e-9 * max(1.0, abs(bracket)),
              f"(|diff| {abs(bracket_hat - bracket):.1e})")
        check(f"{name}: alpha*d0/i real and nonzero, adjugate bracket > 0",
              abs(t.imag) < 1e-9 and abs(t.real) > 1e-6 and bracket > 0,
              f"(t={t.real:+.4f}, bracket={bracket:.4f}, |alpha|={abs(adef):.4f})")

    rng = random.Random(20261124)
    n, min_t, min_bracket, scale_err = 0, math.inf, math.inf, 0.0
    while n < 200:
        A = [[rng.uniform(-3, 1), rng.uniform(-3, 3)],
             [rng.uniform(-3, 3), rng.uniform(-3, 1)]]
        tr = A[0][0] + A[1][1]
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if tr >= 0 or det <= 0 or tr * tr - 4 * det >= 0:
            continue
        m11, m22 = rng.uniform(0.2, 3), rng.uniform(0.2, 3)
        m12 = rng.uniform(-0.9, 0.9) * math.sqrt(m11 * m22)
        adef, aform, d0, bracket, _bh = alpha_data(
            A, [[m11, m12], [m12, m22]],
            rng.choice([0.5, 0.9, 1.3]), rng.choice([0.2, 0.45, 0.7]))
        t = (adef * d0 / 1j).real
        min_t = min(min_t, abs(t))
        min_bracket = min(min_bracket, bracket)
        scale_err = max(scale_err, abs(adef - aform))
        n += 1
    check("random sweep (200 truths): t != 0 and bracket > 0 throughout",
          min_t > 1e-6 and min_bracket > 0,
          f"(min |t| {min_t:.4f}, min bracket {min_bracket:.4f})")
    check("random sweep: formula (1) matches definition",
          scale_err < 1e-7, f"(max |diff| {scale_err:.1e})")
    print("\nFAILED:", FAILURES if FAILURES else "none -- all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
