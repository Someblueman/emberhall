#!/usr/bin/env python3
"""General-case completeness at rational eps/Delta, and the irrational
obstruction (DERIVATION s11).

Rational rho = eps/Delta = p/q: in the eigenbasis of Phi (as in
completeness_general.py) Sigma_m = eps^2 P diag(d_m, conj d_m) Ghat P^{-1}
with d_m = mu_m^2/(e^{mu_m eps} + e^{-mu_m eps} - 2),
mu_m = (ln r + i(theta + 2 pi m))/Delta.  Now
e^{mu_m eps} = r^rho e^{i (theta + 2 pi m) rho} is periodic in m with
period q/gcd(p, q), so the denominator of d_m takes only that many values
while mu_m^2 is quadratic in m.  The symmetry residual R(m) -- a fixed
real linear form in (d_m, conj d_m) -- is therefore an exact quadratic
polynomial in m on each residue class, and finitely many quadratics
enumerate every integer root: completeness over all m, for any rational
ratio.  Demonstrated on the frozen general example at eps/Delta = 1/3
(Delta = 0.9, eps = 0.3).

Irrational rho: no such reduction exists.  Write d_m's denominator as
D(phi) = a e^{i phi} + a^{-1} e^{-i phi} - 2 with a = r^rho in (0,1) and
phi_m = (theta + 2 pi m) rho.  As phi runs over the circle, D traces an
ellipse centred at -2 with semi-axes a + a^{-1} > 2 and a^{-1} - a, which
encloses the origin; hence 1/D winds once around 0 and the normalized
limit function h(phi) = Re(alpha * (-(2 pi/Delta)^2) / D(phi)) (alpha the
fixed complex coefficient of R, nonzero in these examples) takes both
signs.  For irrational rho the phases phi_m are dense mod 2 pi, so
R(m)/m^2 has a dense set of limit points containing 0 in its interior:
R changes sign at arbitrarily large m and |R(m)|/m^2 is arbitrarily small
infinitely often.  No finite window and no uniform margin can come from
the symmetry condition there.  Exact zeros R(m) = 0 at large m remain
codimension-one coincidences (absent generically), but they cannot be
excluded by any finite computation from symmetry alone.  Exhibited
numerically at rho = (sqrt(5)-1)/2.
"""
from __future__ import annotations

import cmath
import math
import sys
from fractions import Fraction

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


class EigenResidual:
    """Symmetry residual R(m) for the frozen general A, Dm at given eps."""

    def __init__(self, Delta, eps, ell2=0.03):
        fg = FROZEN_GENERAL
        self.Delta, self.eps = Delta, eps
        g = GeneralVortex(fg["A"], fg["Dm"])
        self.g = g
        self.G1 = g.observed_cov_matrix(Delta, eps, ell2, 1)
        G2 = g.observed_cov_matrix(Delta, eps, ell2, 2)
        self.Phi = matmul(G2, inverse2(self.G1))
        (a, b), (c_, d_) = self.Phi
        tr, det = a + d_, a * d_ - b * c_
        lam1 = tr / 2 + cmath.sqrt(complex(tr * tr / 4 - det))
        self.r, self.theta = abs(lam1), cmath.phase(lam1)
        v1 = (complex(b), lam1 - a) if abs(b) > abs(c_) else (lam1 - d_, complex(c_))
        v2 = (v1[0].conjugate(), v1[1].conjugate())
        self.P = [[v1[0], v2[0]], [v1[1], v2[1]]]
        detP = v1[0] * v2[1] - v2[0] * v1[1]
        self.Pinv = [[v2[1] / detP, -v2[0] / detP], [-v1[1] / detP, v1[0] / detP]]
        PhiInvG1 = matmul(inverse2(self.Phi), self.G1)
        self.Ghat = cmul(cmul(self.Pinv,
                              [[complex(x) for x in row] for row in PhiInvG1]),
                         self.P)

    def R(self, m: int) -> float:
        mu = (math.log(self.r) + 1j * (self.theta + 2 * math.pi * m)) / self.Delta
        z = mu * self.eps
        dm = mu ** 2 / (cmath.exp(z) + cmath.exp(-z) - 2.0)
        Dg = [[dm, 0j], [0j, dm.conjugate()]]
        S = cmul(cmul(self.P, cmul(Dg, self.Ghat)), self.Pinv)
        return (self.eps ** 2 * (S[0][1] - S[1][0])).real

    def sigma_direct_sym(self, m: int) -> float:
        Am = dict(branch_drifts(self.Phi, self.Delta, [m]))[m]
        U = int_exp(Am, self.eps)
        W = int_exp(scale(Am, -1.0), self.eps)
        S = scale(matmul(inverse2(matmul(U, W)),
                         matmul(inverse2(self.Phi), self.G1)), self.eps ** 2)
        return S[0][1] - S[1][0]


def quad_coeffs(ms, ys):
    # exact quadratic A2 x^2 + A1 x + A0 through three points (via Lagrange
    # values at 0, 1, 2 of the interpolant)
    def lag(x):
        tot = 0.0
        for i in range(3):
            term = ys[i]
            for j in range(3):
                if i != j:
                    term *= (x - ms[j]) / (ms[i] - ms[j])
            tot += term
        return tot
    A2 = (lag(2) - 2 * lag(1) + lag(0)) / 2
    return A2, lag(1) - lag(0) - A2, lag(0)


def rational_case():
    Delta, eps = 0.9, 0.3
    rho = Fraction(eps).limit_denominator(1000) / Fraction(Delta).limit_denominator(1000)
    period = rho.denominator // math.gcd(rho.numerator, rho.denominator)
    er = EigenResidual(Delta, eps)
    err = max(abs(er.R(m) - er.sigma_direct_sym(m)) for m in range(-5, 6))
    check(f"eps/Delta={rho}: eigenbasis R matches direct route", err < 1e-9,
          f"(max err {err:.1e}, period {period} residue classes)")
    int_roots = []
    for cls in range(period):
        ms = [cls, cls + period, cls + 2 * period]
        A2, A1, A0 = quad_coeffs(ms, [er.R(m) for m in ms])
        probe = [cls + 3 * period, cls - 4 * period, cls + 1000 * period]
        ver = max(abs(A2 * m * m + A1 * m + A0 - er.R(m)) / max(1.0, abs(er.R(m)))
                  for m in probe)
        check(f"class {cls} mod {period}: R quadratic, A2 != 0",
              ver < 1e-9 and abs(A2) > 1e-8, f"(rel err {ver:.1e}, A2={A2:.5f})")
        disc = A1 * A1 - 4 * A2 * A0
        if disc >= 0:
            for sgn in (-1, 1):
                x = (-A1 + sgn * math.sqrt(disc)) / (2 * A2)
                for cand in {math.floor(x), math.ceil(x)}:
                    if cand % period == cls % period and abs(er.R(cand)) < 1e-9:
                        int_roots.append(cand)
    check("eps/Delta=1/3: only integer root of R over all m is the truth",
          sorted(set(int_roots)) == [0], f"(integer roots {sorted(set(int_roots))})")


def irrational_case():
    Delta = 0.9
    rho = (math.sqrt(5) - 1) / 2
    er = EigenResidual(Delta, rho * Delta)
    N = 20000
    vals = [(m, er.R(m)) for m in range(1, N + 1)]
    signs = [m for (m, v), (_, w) in zip(vals, vals[1:]) if v * w < 0]
    small = min(abs(v) / m ** 2 for m, v in vals if m > 10000)
    big_m, big_v = min(((m, abs(v) / m ** 2) for m, v in vals if m > 10000),
                       key=lambda t: t[1])
    check("irrational rho: R changes sign at arbitrarily large m",
          len(signs) > 20 and signs[-1] > 15000,
          f"({len(signs)} sign changes up to m={N}, last at m={signs[-1]})")
    check("irrational rho: |R(m)|/m^2 arbitrarily small for large m",
          small < 1e-3,
          f"(min over m>10000 is {small:.2e} at m={big_m}; no finite window)")
    absmin = {w: min(abs(er.R(m)) for m in range(*w))
              for w in ((1, 100), (100, 1000), (1000, 5000))}
    print(f"  absolute min |R| by window: "
          + ", ".join(f"{lo}-{hi}: {v:.1f}" for (lo, hi), v in absmin.items()))
    print("  reading: symmetry alone admits no finite candidate list and no")
    print("  uniform (relative) margin at irrational eps/Delta; absolute")
    print("  residuals here still grow (~m), because the golden ratio is")
    print("  badly approximable -- the finite-window question at fixed")
    print("  absolute tolerance is Diophantine in rho, not settled here;")


def main() -> int:
    rational_case()
    irrational_case()
    print("  exact large-m roots would be codimension-one coincidences, not")
    print("  excluded by finiteness -- recorded as the honest remainder.")
    print("FAILED:", FAILURES if FAILURES else "none — all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
