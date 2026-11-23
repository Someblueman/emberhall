#!/usr/bin/env python3
"""Scalar-Phi rivals: from search to determinant exclusion (s27).

s22 excluded scalar-Phi rival drifts by continuous search over an
8-truth family and left a parameter-free proof open.  This slice
takes the first proof step: it turns the rival equations into a
one-variable determinant whose roots can be isolated completely,
and carries the exclusion through for the closest truth of the s22
sweep (2pi/short shutter, whose nearest rival sat at J = 1.08e-3).

The general reduction (proof).  For a rival branch beta != 0 the
candidate drift is Ac(t, phi) = R(phi) Ac(t, 0) R(phi)^T (the scalar
part commutes), and every ingredient of real_logs.compatibility is
conjugation-covariant (augmented matrix exponentials), while Phi is
scalar.  Hence the three signed residuals (symmetry, zero-lag
off-diagonal, ell^2 split) are, at fixed t, trigonometric
polynomials of degree one in 2*phi:

    f_i(t, phi) = A_i(t) + B_i(t) cos(2 phi) + C_i(t) sin(2 phi).

A compatible rival needs a common zero, so with M(t) the 3x3
coefficient matrix, det M(t) = 0 is necessary (for t != 0; at t = 0
the phi-family collapses to one drift per branch, checked
directly).  Numerically (70-digit mpmath, exact interpolation) det
factors as

    det M(t) = (w - 2) * S(w),   w = e^{2t} + e^{-2t} = 2 cosh(2t),

with S a quadratic polynomial having the universal root w = -2,
i.e. det M = (w^2 - 4)(c2 w - c2 w*) for one remaining number w*
per branch.  Real t != 0 has w > 2, so a rival on the branch can
exist only if w* > 2.

For the 2pi/short-shutter truth: w* = 1.029 (beta = 4 pi) and
w* = 0.625 (beta = 6 pi) - no admissible t at all; beta = 0 is a
single drift with J = 1.084e-3 > 0; and on the same branch
beta = 2 pi, w* = 2.162 gives t = +-0.2, whose null vector
recovers exactly the true drift (and its (t, phi) twin).  So for
this truth the film admits no scalar-Phi rival on any branch
beta in {0, 2pi, 4pi, 6pi}, over the whole (t, phi) cylinder -
s22's search result for this truth, upgraded to a complete
exclusion modulo the stated high-precision arithmetic.

Scope, plainly: the trig/determinant reduction is general, but the
coefficients (hence w*) are truth-specific transcendentals computed
at 70 digits with root margins reported; this is a verified
exclusion for ONE truth (the sweep's closest), not yet the
parameter-free theorem.  Positivity at candidate roots is checked
where a root is admissible.
"""
from __future__ import annotations

import sys

from mpmath import mp, mpf, matrix

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def M2(a, b, c, d):
    m = matrix(2, 2)
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = a, b, c, d
    return m


def inv2(m):
    det = m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0]
    return M2(m[1, 1] / det, -m[0, 1] / det, -m[1, 0] / det, m[0, 0] / det)


def int_exp(A, eps):
    Mx = matrix(4, 4)
    for i in range(2):
        for j in range(2):
            Mx[i, j] = A[i, j] * eps
        Mx[i, 2 + i] = eps
    E = mp.expm(Mx)
    return M2(E[0, 2], E[0, 3], E[1, 2], E[1, 3])


def int_exp_w(A, eps):
    Mx = matrix(6, 6)
    for i in range(2):
        for j in range(2):
            Mx[i, j] = A[i, j] * eps
        Mx[i, 2 + i] = eps
        Mx[2 + i, 4 + i] = eps
    E = mp.expm(Mx)
    return M2(E[0, 4], E[0, 5], E[1, 4], E[1, 5])


def family_drift(alpha, beta, t, phi, Delta):
    if beta == 0:
        return M2(alpha / Delta, mpf(0), mpf(0), alpha / Delta)
    Nt = M2(mpf(0), -beta * mp.exp(2 * t), beta * mp.exp(-2 * t), mpf(0))
    cp, sp = mp.cos(phi), mp.sin(phi)
    R = M2(cp, -sp, sp, cp)
    N = R * Nt * R.T
    return M2((alpha + N[0, 0]) / Delta, N[0, 1] / Delta,
              N[1, 0] / Delta, (alpha + N[1, 1]) / Delta)


class Truth:
    """The s22 sweep's closest truth: 2pi / short shutter / mixed Dm."""

    def __init__(self):
        self.alpha = mpf("-1.5")
        self.beta_true = 2 * mp.pi
        self.t_true, self.phi_true = mpf("0.2"), mpf("0.3")
        self.Delta, self.eps, self.ell2 = mpf(1), mpf("0.15"), mpf("0.03")
        self.A = family_drift(self.alpha, self.beta_true,
                              self.t_true, self.phi_true, self.Delta)
        Dm = M2(mpf(1), mpf("0.3"), mpf("0.3"), mpf("0.6"))
        A = self.A
        K = matrix(4, 4)
        for i in range(2):
            for j in range(2):
                for pp in range(2):
                    for qq in range(2):
                        K[j * 2 + i, qq * 2 + pp] += (
                            A[i, pp] * (1 if j == qq else 0)
                            + (1 if i == pp else 0) * A[j, qq])
        xv = mp.lu_solve(K, matrix([-2 * Dm[0, 0], -2 * Dm[1, 0],
                                    -2 * Dm[0, 1], -2 * Dm[1, 1]]))
        self.Sigma = M2(xv[0], xv[2], xv[1], xv[3])
        self.G0 = self._observed(0)
        self.G1 = self._observed(1)
        G2 = self._observed(2)
        self.Phi = G2 * inv2(self.G1)
        self.a_rec = mp.log(self.Phi[0, 0])
        self.scale = max([mpf(1)] + [abs(self.G0[i, j])
                                     for i in range(2) for j in range(2)])

    def _observed(self, k):
        A, eps = self.A, self.eps
        if k == 0:
            U2S = int_exp_w(A, eps) * self.Sigma
            G = (U2S + U2S.T) / eps ** 2
            G[0, 0] += self.ell2
            G[1, 1] += self.ell2
            return G
        G = int_exp(A, eps) * int_exp(-A, eps) * self.Sigma
        return mp.expm(A * (k * self.Delta)) * G / eps ** 2

    def compat(self, Ac):
        """Signed residuals + positivity data (real_logs.compatibility)."""
        eps = self.eps
        U, W = int_exp(Ac, eps), int_exp(-Ac, eps)
        S = inv2(U * W) * inv2(self.Phi) * self.G1 * eps ** 2
        U2S = int_exp_w(Ac, eps) * S
        P0 = (U2S + U2S.T) / eps ** 2
        Dmr = -(Ac * S + S * Ac.T) / 2
        resid = (S[0, 1] - S[1, 0],
                 self.G0[0, 1] - P0[0, 1],
                 (self.G0[0, 0] - P0[0, 0]) - (self.G0[1, 1] - P0[1, 1]))
        pos = dict(detS=S[0, 0] * S[1, 1] - S[0, 1] * S[1, 0], s00=S[0, 0],
                   detDm=Dmr[0, 0] * Dmr[1, 1] - Dmr[0, 1] * Dmr[1, 0],
                   dm00=Dmr[0, 0],
                   ell2=((self.G0[0, 0] - P0[0, 0])
                         + (self.G0[1, 1] - P0[1, 1])) / 2)
        return resid, pos

    def coeffs(self, beta, t):
        fs = [self.compat(family_drift(self.a_rec, beta, t, phi, self.Delta))[0]
              for phi in (mpf(0), mp.pi / 4, mp.pi / 2)]
        M = []
        for i in range(3):
            f0, f1, f2 = fs[0][i], fs[1][i], fs[2][i]
            M.append(((f0 + f2) / 2, (f0 - f2) / 2, f1 - (f0 + f2) / 2))
        return M

    def detM(self, beta, t):
        M = self.coeffs(beta, t)
        return mp.det(matrix([[M[i][j] for j in range(3)] for i in range(3)]))


def fit_S(truth, beta, ts_fit, ts_test):
    """Fit detM = (w-2) * S(w), S quadratic; return (coef, max rel err)."""
    def pt(t):
        u = mp.exp(2 * t)
        w = u + 1 / u
        return w, truth.detM(beta, t) / (w - 2)

    pts = [pt(t) for t in ts_fit]
    Vn = matrix(3, 3)
    for i in range(3):
        for j in range(3):
            Vn[i, j] = pts[i][0] ** j
    coef = mp.lu_solve(Vn, matrix([p[1] for p in pts]))
    err = mpf(0)
    for t in ts_test:
        w, y = pt(t)
        err = max(err, abs(sum(coef[j] * w ** j for j in range(3)) - y)
                  / max(abs(y), mpf("1e-300")))
    return coef, err


def main() -> int:
    mp.dps = 70
    tr = Truth()
    ea = mp.exp(tr.alpha)
    perr = (abs(tr.Phi[0, 0] - ea) + abs(tr.Phi[0, 1])
            + abs(tr.Phi[1, 0]) + abs(tr.Phi[1, 1] - ea))
    check("truth setup: Phi = e^alpha I (scalar), alpha recovered",
          perr < mpf("1e-50") and abs(tr.a_rec - tr.alpha) < mpf("1e-50"),
          f"(err {mp.nstr(perr, 2)})")
    r_true, _ = tr.compat(tr.A)
    check("truth control: residuals vanish at the true drift",
          max(abs(v) for v in r_true) < mpf("1e-50"),
          f"(max {mp.nstr(max(abs(v) for v in r_true), 2)})")

    # trig form in phi, verified against direct evaluation
    worst = mpf(0)
    samples = [(mpf("-1.3"), mpf("0.77")), (mpf("0.42"), mpf("2.1")),
               (mpf("1.8"), mpf("-0.5"))]
    for beta in (2 * mp.pi, 4 * mp.pi, 6 * mp.pi):
        for t, phi in samples:
            M = tr.coeffs(beta, t)
            got, _ = tr.compat(family_drift(tr.a_rec, beta, t, phi, tr.Delta))
            for i in range(3):
                pred = M[i][0] + M[i][1] * mp.cos(2 * phi) + M[i][2] * mp.sin(2 * phi)
                worst = max(worst, abs(pred - got[i]))
    check("signed residuals are A + B cos(2phi) + C sin(2phi) exactly",
          worst < mpf("1e-50"), f"(worst fit err {mp.nstr(worst, 2)})")

    # beta = 0: one drift
    r0, _p0 = tr.compat(family_drift(tr.a_rec, mpf(0), mpf(0), mpf(0), tr.Delta))
    J0 = sum((v / tr.scale) ** 2 for v in r0)
    check("beta=0 rival: single drift with J = 1.084e-3 > 0",
          J0 > mpf("1e-3"), f"(J = {mp.nstr(J0, 6)}, s22 search value)")

    ts_fit = [mpf("0.35"), mpf("0.9"), mpf("1.6")]
    ts_test = [mpf("0.55"), mpf("1.2"), mpf("2.0"), mpf("-0.7")]
    for beta, tag in ((2 * mp.pi, "same branch 2pi"),
                      (4 * mp.pi, "rival 4pi"), (6 * mp.pi, "rival 6pi")):
        # t = 0 collapse: phi-independent drift must not be compatible
        r_t0, _ = tr.compat(family_drift(tr.a_rec, beta, mpf(0), mpf(0), tr.Delta))
        m_t0 = max(abs(v) for v in r_t0)
        coef, ferr = fit_S(tr, beta, ts_fit, ts_test)
        c0, c1, c2 = coef[0], coef[1], coef[2]
        sm2 = c0 - 2 * c1 + 4 * c2  # S(-2)
        disc = c1 * c1 - 4 * c2 * c0
        check(f"{tag}: det M = (w-2) S(w), S quadratic, S(-2)=0",
              ferr < mpf("1e-40") and abs(sm2) < abs(c0) * mpf("1e-30")
              and m_t0 > mpf("1e-3"),
              f"(fit rel err {mp.nstr(ferr, 2)}, max|resid| at t=0 "
              f"{mp.nstr(m_t0, 3)})")
        # remaining root w* from product of roots c0/c2 = (-2) * w*
        w_star = -c0 / (2 * c2)
        if beta == tr.beta_true:
            # admissible root: must recover the truth alone
            t_star = mp.acosh(w_star / 2) / 2
            M = tr.coeffs(beta, t_star)
            # solve rows 0,1 for (c,s): B c + C s = -A
            det2 = M[0][1] * M[1][2] - M[0][2] * M[1][1]
            cc = (-M[0][0] * M[1][2] + M[0][2] * M[1][0]) / det2
            ss = (-M[0][1] * M[1][0] + M[0][0] * M[1][1]) / det2
            phi_star = mp.atan2(ss, cc) / 2 % mp.pi
            Ac = family_drift(tr.a_rec, beta, t_star, phi_star, tr.Delta)
            drift_err = max(abs(Ac[i, j] - tr.A[i, j])
                            for i in range(2) for j in range(2))
            resid, pos = tr.compat(Ac)
            check(f"{tag}: only admissible root w*={mp.nstr(w_star, 8)} "
                  f"gives t=+-0.2 and recovers the true drift",
                  abs(t_star - tr.t_true) < mpf("1e-30")
                  and abs(cc * cc + ss * ss - 1) < mpf("1e-40")
                  and drift_err < mpf("1e-30")
                  and max(abs(v) for v in resid) < mpf("1e-40")
                  and pos["detS"] > 0 and pos["detDm"] > 0,
                  f"(drift err {mp.nstr(drift_err, 2)}, phi* "
                  f"{mp.nstr(phi_star, 6)} vs true 0.3 mod pi/2 twin)")
        else:
            check(f"{tag}: w* = {mp.nstr(w_star, 8)} < 2, so det M(t) != 0 "
                  f"for all real t != 0: no rival on this branch",
                  w_star < 2 - mpf("0.5"),
                  f"(discriminant {mp.nstr(disc, 3)}; other root w=-2)")

    print("\nFAILED:", FAILURES if FAILURES else "none -- all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
