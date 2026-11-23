#!/usr/bin/env python3
"""Explicit window constant for irrational eps/Delta (DERIVATION s25).

s24 exhibited min_m |R(m)|/m on the frozen general truth as Diophantine
in rho = eps/Delta and left the explicit constant open.  This slice
settles what form that constant can take.

Exact decomposition (proof).  With mu_m = (ln r + i(theta + 2 pi m))/Delta,
eps = rho*Delta, a = r^rho and psi_m = (theta + 2 pi m)*rho mod 2 pi, the
s11 residual is R(m) = eps^2 Re(alpha * mu_m^2 / D(psi_m)) where alpha is a
fixed complex number read off the eigenbasis formula, D(phi) = a e^{i phi}
+ a^{-1} e^{-i phi} - 2, and mu_m^2 is exactly quadratic in m:
mu_m^2 = c2 m^2 + c1 m + c0 with
  c2 = -(2 pi/Delta)^2,  c1 = (4 pi/Delta^2)(i ln r - theta),
  c0 = (ln r + i theta)^2 / Delta^2.
Hence, with h_j(phi) = eps^2 Re(alpha c_j / D(phi)) (write h for h_2),
  R(m) = m^2 h(psi_m) + m h_1(psi_m) + h_0(psi_m)      exactly, all m.
D traces an ellipse centred at -2 enclosing the origin (a in (0,1)), so
the polar angle of D(phi) is strictly monotone and h has exactly two
zeros psi*_j on the circle, simple iff h'(psi*_j) != 0 (checked here).
Near psi*_j, writing gamma_j = psi*_j/(2 pi) - rho*theta/(2 pi) and
xi_m^(j) = m * (m*rho - gamma_j - n_m) (n_m the nearest integer):
  R(m)/m = 2 pi h'(psi*_j) (xi_m - xi*_j) + o(1)   as psi_m -> psi*_j,
with xi*_j = -h_1(psi*_j) / (2 pi h'(psi*_j)).  Therefore (proof in
DERIVATION s25)
  liminf_{m->inf} |R(m)|/m
      = 2 pi * min_j |h'(psi*_j)| * dist(xi*_j, Xi_j),
Xi_j the finite limit points of xi_m^(j) (nonempty by the inhomogeneous
Dirichlet theorem).  The constant depends on the truth through exactly
(C, psi*) = (h'(psi*_j), and xi*_j, gamma_j built from psi*_j, theta).

No truth-uniform c(rho) exists (proof at the level of the residual's
parameters: at any fixed m0, R(m0) as a function of arg alpha is a
sinusoid, hence has an exact zero; a genuine in-model family exhibiting
the same phenomenon is bisected below).  Nor is the finite-range minimum
a closed monotone function of rho's partial quotients: replacing the
engineered quotient 1000 by 1s *lowers* the minimum, inserting 1000 into
the golden ratio *raises* it (search, below).  What continued fractions
give in closed form is the homogeneous bound m*||m*rho|| >= 1/(A+2)
(A = max partial quotient); the inhomogeneous target gamma_j is set by
the truth, and its Ostrowski position relative to the quotients -- not
the quotients alone -- decides the arithmetic factor dist(xi*_j, Xi_j).

Effective finite bound.  For 1 <= M0 <= m <= M this script computes
  B(rho, truth, M) = min(B_far, min_j B_near_j) <= min |R(m)|/m,
B_far from |h| away from the zeros, B_near_j = 2 pi b_j D_j - E_j
- H0/M0 with b_j a lower bound for |h'| near psi*_j, E_j the variation
of the near-zero expansion, and D_j = min |xi_m^(j) - xi*_j| over the
range (the arithmetic factor, computed by a xi-scan organised by
convergent blocks).  Analytic constants are grid extrema with explicit
Lipschitz padding (computed bounds in float arithmetic, not interval
proof).  Branches m < M0 remain a finite enumeration, as in s11.
Checked against brute force over m <= 200000 for the golden ratio,
sqrt(2)-1 and the engineered [0;9,11,1000,7,3] ratio, reproducing the
s24 control minima 0.1553 / 0.2024 / 0.0049.
"""
from __future__ import annotations

import cmath
import math
import sys
from fractions import Fraction

import completeness_rational as cr
from completeness_rational import EigenResidual, cmul

FAILURES: list[str] = []
DELTA = 0.9
M_DEFAULT = 200000


def check(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def alpha_of(er) -> complex:
    """R(m) = eps^2 Re(alpha * d_m): read alpha off d = 1 and d = i."""
    def form(d):
        Dg = [[d, 0j], [0j, d.conjugate()]]
        S = cmul(cmul(er.P, cmul(Dg, er.Ghat)), er.Pinv)
        return (S[0][1] - S[1][0]).real
    return complex(form(1 + 0j), -form(0 + 1j))


class Ctx:
    def __init__(self, rho: float):
        self.rho = rho
        self.er = EigenResidual(DELTA, rho * DELTA)
        self.eps = self.er.eps
        self.al = alpha_of(self.er)
        a = self.er.r ** rho
        s = math.log(self.er.r)
        self.th = self.er.theta
        self.c2 = -(2 * math.pi / DELTA) ** 2
        self.c1 = (4 * math.pi / DELTA ** 2) * (1j * s - self.th)
        self.c0 = (s + 1j * self.th) ** 2 / DELTA ** 2
        self.A = a + 1 / a          # ellipse semi-axis (real), > 2
        self.B = a - 1 / a          # ellipse semi-axis (imag)
        self.a = a

    def D(self, phi):
        return complex(self.A * math.cos(phi) - 2, self.B * math.sin(phi))

    def Dp(self, phi):
        return complex(-self.A * math.sin(phi), self.B * math.cos(phi))

    def h(self, phi):
        return self.eps ** 2 * (self.al * self.c2 / self.D(phi)).real

    def hj(self, c, phi):
        return self.eps ** 2 * (self.al * c / self.D(phi)).real

    def hp(self, phi):
        return self.eps ** 2 * (self.al * self.c2 * (-self.Dp(phi))
                                / self.D(phi) ** 2).real

    def psi(self, m):
        return ((self.th + 2 * math.pi * m) * self.rho) % (2 * math.pi)

    def decomp(self, m):
        p = self.psi(m)
        return (m * m * self.h(p) + m * self.hj(self.c1, p)
                + self.hj(self.c0, p))

    def zeros(self):
        N, zs, prev = 8000, [], self.h(0.0)
        for i in range(1, N + 1):
            phi = 2 * math.pi * i / N
            v = self.h(phi)
            if v * prev < 0:
                lo, hi = 2 * math.pi * (i - 1) / N, phi
                vlo = self.h(lo)
                for _ in range(90):
                    mid = (lo + hi) / 2
                    if self.h(mid) * vlo > 0:
                        lo = mid
                    else:
                        hi = mid
                zs.append((lo + hi) / 2)
            prev = v
        return zs

    # -- analytic derivative bounds, |D'| <= A, |D''| <= A -------------
    def lip_hj(self, c, dmin):
        return self.eps ** 2 * abs(self.al) * abs(c) * self.A / dmin ** 2

    def lip_hp(self, dmin):
        return (self.eps ** 2 * abs(self.al) * abs(self.c2)
                * (2 * self.A ** 2 / dmin ** 3 + self.A / dmin ** 2))


def wrap_dist(phi, z):
    return min((phi - z) % (2 * math.pi), (z - phi) % (2 * math.pi))


def bound_for(rho, M=M_DEFAULT, G=60000):
    """Computed lower bound B for min_{M0<=m<=M} |R(m)|/m (see docstring)."""
    cx = Ctx(rho)
    zs = cx.zeros()
    deltas = [0.01 if abs(cx.hp(z)) > 50 else 0.05 for z in zs]
    step = 2 * math.pi / G
    hfar, H1far, H0 = math.inf, 0.0, 0.0
    for i in range(G):
        phi = step * i
        dloc = abs(cx.D(phi)) - cx.A * step / 2
        dloc = max(dloc, 1e-9)
        H0 = max(H0, abs(cx.hj(cx.c0, phi))
                 + cx.lip_hj(cx.c0, dloc) * step / 2)
        if all(wrap_dist(phi, z) > d for z, d in zip(zs, deltas)):
            hfar = min(hfar, abs(cx.h(phi))
                       - cx.lip_hj(cx.c2, dloc) * step / 2)
            H1far = max(H1far, abs(cx.hj(cx.c1, phi))
                        + cx.lip_hj(cx.c1, dloc) * step / 2)
    M0 = max(1000, int(math.ceil((H1far + 2.0) / hfar)))
    B = M0 * hfar - H1far - H0 / M0
    rows = []
    K = 8000
    for z, d in zip(zs, deltas):
        hpz, h1z = cx.hp(z), cx.hj(cx.c1, z)
        xi_star = -h1z / (2 * math.pi * hpz)
        gam = (z / (2 * math.pi) - rho * cx.th / (2 * math.pi)) % 1.0
        istep = 2 * d / K
        dmin = min(abs(cx.D(z + istep * i - d)) for i in range(K + 1)) \
            - cx.A * istep / 2
        bmin, sign_ok, E = math.inf, True, 0.0
        lipE = (cx.lip_hj(cx.c1, dmin)
                + abs(h1z) * cx.lip_hp(dmin) / (2 * abs(hpz)))
        for i in range(K + 1):
            dd = -d + istep * i
            hpv = cx.hp(z + dd)
            sign_ok = sign_ok and hpv * hpz > 0
            bmin = min(bmin, abs(hpv) - cx.lip_hp(dmin) * istep / 2)
            if dd != 0.0:
                beta = cx.h(z + dd) / dd
                E = max(E, abs(cx.hj(cx.c1, z + dd) - (beta / hpz) * h1z))
        E += lipE * istep / 2
        Dj, argm = math.inf, None
        for m in range(M0, M + 1):
            x = m * rho - gam
            xi = m * (x - round(x))
            if abs(2 * math.pi * xi / m) <= d and abs(xi - xi_star) < Dj:
                Dj, argm = abs(xi - xi_star), m
        Bnear = 2 * math.pi * bmin * Dj - E - H0 / M0
        rows.append(dict(z=z, d=d, hp=hpz, xi_star=xi_star, gam=gam,
                         bmin=bmin, sign_ok=sign_ok, E=E, Dj=Dj, argm=argm,
                         Bnear=Bnear))
        B = min(B, Bnear)
    return dict(cx=cx, zs=zs, M0=M0, B=B, rows=rows,
                hfar=hfar, H1far=H1far, H0=H0)


def brute_min(cx, lo, hi):
    best = (math.inf, None)
    for m in range(lo, hi + 1):
        v = abs(cx.er.R(m)) / m
        if v < best[0]:
            best = (v, m)
    return best


def from_cf(cf):
    f = Fraction(cf[-1])
    for a in reversed(cf[:-1]):
        f = a + Fraction(1, f)
    return f


def convergents(rho_frac: Fraction, qmax):
    """(p_k, q_k, a_{k+1}-style list) via Fraction CF; floats via limit."""
    n, d = rho_frac.numerator, rho_frac.denominator
    cf = []
    while d:
        cf.append(n // d)
        n, d = d, n - (n // d) * d
    p0, p1, q0, q1 = 0, 1, 1, 0
    out = []
    for a in cf:
        p0, p1 = p1, a * p1 + p0
        q0, q1 = q1, a * q1 + q0
        out.append((p1, q1, a))
        if q1 > qmax and len(out) > 2:
            break
    return out


def homogeneous_min(rho, M):
    best = math.inf
    for m in range(1, M + 1):
        x = m * rho
        best = min(best, m * abs(x - round(x)))
    return best


GOLDEN = (math.sqrt(5) - 1) / 2
SQRT2M1 = math.sqrt(2) - 1
ENG_FRAC = from_cf([0, 9, 11, 1000, 7, 3])
ENG = float(ENG_FRAC)
CASES = [("golden [0;1,1,...]", GOLDEN, 0.1553, Fraction(GOLDEN).limit_denominator(10 ** 7)),
         ("sqrt2-1 [0;2,2,...]", SQRT2M1, 0.2024, Fraction(SQRT2M1).limit_denominator(10 ** 7)),
         ("engineered [0;9,11,1000,7,3]", ENG, 0.0049, ENG_FRAC)]


def main() -> int:
    M = M_DEFAULT
    # 1. exact decomposition + alpha formula, against two other routes
    for name, rho, _ctl, _fr in CASES:
        cx = Ctx(rho)
        ms = [1, 2, 3, 7, 50, 101, 1000]
        err = max(abs(cx.decomp(m) - cx.er.R(m)) / max(1.0, abs(cx.er.R(m)))
                  for m in ms)
        # at m ~ 1e5 both routes reduce a phase ~1e6 rad in doubles, so
        # compare at h-level: |decomp - R| / m^2 (phase error ~1e-10 rad
        # times |h'| accounts for the observed size)
        errb = max(abs(cx.decomp(m) - cx.er.R(m)) / (m * m)
                   for m in [92549, 169777, 200000])
        errd = max(abs(cx.decomp(m) - cx.er.sigma_direct_sym(m))
                   for m in [-3, 1, 2, 5])
        check(f"{name}: R = m^2 h + m h1 + h0 exact",
              err < 1e-9 and errb < 1e-6 and errd < 1e-8,
              f"(rel err vs eigen {err:.1e} for m<=1000, h-level err "
              f"{errb:.1e} at m~1e5, abs err vs direct {errd:.1e}; "
              f"alpha={cx.al:.4f}, a=r^rho={cx.a:.4f})")
        zs = cx.zeros()
        check(f"{name}: h has exactly two zeros, both simple",
              len(zs) == 2 and all(abs(cx.hp(z)) > 1e-3 for z in zs),
              f"(psi* = {['%.5f' % z for z in zs]}, "
              f"h' = {['%.4f' % cx.hp(z) for z in zs]})")

    # 2. derived bound vs brute force; s24 controls
    act = {}
    for name, rho, ctl, frac in CASES:
        bd = bound_for(rho, M)
        cx, M0, B = bd["cx"], bd["M0"], bd["B"]
        b_out = brute_min(cx, M0, M)
        b_in = brute_min(cx, 1, M0 - 1)
        b_all = min(b_in, b_out)
        check(f"{name}: s24 control min|R(m)|/m over m<={M}",
              abs(b_all[0] - ctl) < 5e-4,
              f"(got {b_all[0]:.4f} at m={b_all[1]}, s24 {ctl})")
        check(f"{name}: derived bound B <= brute min on [M0,M], B > 0",
              0 < B <= b_out[0] * (1 + 1e-9),
              f"(M0={M0}, B={B:.5f}, brute={b_out[0]:.5f} at m={b_out[1]}, "
              f"ratio {b_out[0] / B:.2f}; brute below M0: {b_in[0]:.5f} "
              f"at m={b_in[1]})")
        for row in bd["rows"]:
            pred = 2 * math.pi * abs(row["hp"]) * row["Dj"]
            print(f"    psi*={row['z']:.4f} gamma={row['gam']:.5f} "
                  f"xi*={row['xi_star']:.4f} 2pi|h'|={2 * math.pi * abs(row['hp']):.4f} "
                  f"(per eps^2: {2 * math.pi * abs(row['hp']) / cx.eps ** 2:.2f}) "
                  f"D_j={row['Dj']:.5f} at m={row['argm']} "
                  f"B_near={row['Bnear']:.5f} pred~{pred:.5f}")
        act[name] = min(bd["rows"], key=lambda r: r["Bnear"])
        conv = convergents(frac, 10 * M)
        blk = [q for _p, q, _a in conv if q <= M]
        k = max(i for i, q in enumerate(blk) if q <= b_out[1])
        print(f"    convergents q_k<={M}: {len(blk)}; argmin m={b_out[1]} "
              f"in block [q_k={blk[k]}, q_next={conv[k + 1][1] if k + 1 < len(conv) else '>'})"
              f" (next partial quotient {conv[k + 1][2] if k + 1 < len(conv) else '-'})")

    # 3. arithmetic factor saturation (search): D_j(M) to 10^6, active zero
    for name, rho, _ctl, _fr in CASES:
        row = act[name]
        best, at = math.inf, {}
        gam, xs = row["gam"], row["xi_star"]
        for m in range(1, 1000001):
            x = m * rho - gam
            d = abs(m * (x - round(x)) - xs)
            if d < best:
                best = d
            if m in (10000, 200000, 1000000):
                at[m] = best
        print(f"  {name}: D_j(M) search: "
              + ", ".join(f"M={m}: {v:.5f}" for m, v in at.items())
              + "  (saturation would mean xi* off the limit set Xi_j)")

    # 4. closed-form CF content: homogeneous bound; quotient swaps
    for name, rho, A in [("golden", GOLDEN, 1), ("sqrt2-1", SQRT2M1, 2)]:
        hm = homogeneous_min(rho, M)
        check(f"{name}: homogeneous CF bound m||m rho|| >= 1/(A+2)",
              hm >= 1.0 / (A + 2) - 1e-9,
              f"(min over m<={M} is {hm:.4f}, bound {1.0 / (A + 2):.4f}, A={A})")
    alt = float(from_cf([0, 9, 11] + [1] * 25))
    g1000 = float(from_cf([0] + [1] * 6 + [1000] + [1] * 20))
    m_alt = brute_min(Ctx(alt), 1, M)
    m_g1k = brute_min(Ctx(g1000), 1, M)
    m_eng = brute_min(Ctx(ENG), 1, M)
    m_gld = brute_min(Ctx(GOLDEN), 1, M)
    check("quotient swap: engineered 1000 -> 1s lowers the minimum",
          m_alt[0] < m_eng[0],
          f"([0;9,11,1,...] {m_alt[0]:.5f} at {m_alt[1]} < engineered "
          f"{m_eng[0]:.5f} at {m_eng[1]})")
    check("quotient swap: inserting 1000 into golden raises the minimum",
          m_g1k[0] > m_gld[0],
          f"([0;1x6,1000,1...] {m_g1k[0]:.5f} at {m_g1k[1]} > golden "
          f"{m_gld[0]:.5f} at {m_gld[1]})")
    print("  reading: no closed c(partial quotients) orders these minima;")
    print("  the arithmetic factor is dist(xi*, Xi) for the truth's own")
    print("  gamma (its Ostrowski position), times eps^2 geometry in h'.")

    # 5. no truth-uniform constant: parameter-level zero + in-model family
    cx = Ctx(GOLDEN)
    m0 = 1000
    mu = (math.log(cx.er.r) + 1j * (cx.th + 2 * math.pi * m0)) / DELTA
    dm = mu ** 2 / cx.D(cx.psi(m0))
    t_star = math.pi / 2 - cmath.phase(cx.al * dm)
    val = (cx.eps ** 2 * (cx.al * cmath.exp(1j * t_star) * dm).real)
    check("parameter level: rotating arg alpha zeroes R(m0) exactly",
          abs(val) < 1e-10 * max(1.0, abs(cx.er.R(m0))),
          f"(m0={m0}, t*={t_star:.4f}, R={val:.2e}; so no c(rho) uniform "
          f"over (alpha, theta, r) exists)")
    fg0 = cr.FROZEN_GENERAL

    def R_family(w, m):
        cr.FROZEN_GENERAL = {"A": [[-0.6, -w], [w, -1.2]], "Dm": fg0["Dm"]}
        return EigenResidual(DELTA, GOLDEN * DELTA).R(m)

    m_fam, w_lo = 96, None
    ws = [2.80 + 0.01 * i for i in range(21)]
    vs = [R_family(w, m_fam) for w in ws]
    for (wa, va), (wb, vb) in zip(zip(ws, vs), zip(ws[1:], vs[1:])):
        if va * vb < 0:
            lo, hi, vlo = wa, wb, va
            for _ in range(100):
                mid = (lo + hi) / 2
                if R_family(mid, m_fam) * vlo > 0:
                    lo = mid
                else:
                    hi = mid
            w_lo = (lo + hi) / 2
            break
    if w_lo is not None:
        cr.FROZEN_GENERAL = {"A": [[-0.6, -w_lo], [w_lo, -1.2]],
                             "Dm": fg0["Dm"]}
        er = EigenResidual(DELTA, GOLDEN * DELTA)
        resid = abs(er.R(m_fam)) / m_fam
        # A(w): trace -1.8, det 0.72 + w^2 > (trace/2)^2 for w > 0.3,
        # so eigenvalues are -0.9 +- i*sqrt(w^2-0.09): stable, genuine.
        check("in-model family: a genuine truth with |R(m)|/m ~ 0 at golden rho",
              resid < 1e-7 and er.r < 1,
              f"(A=[[-0.6,-w],[w,-1.2]], w*={w_lo:.8f}, m={m_fam}, "
              f"|R|/m={resid:.2e}, r={er.r:.4f}<1, theta={er.theta:.4f})")
    else:
        check("in-model family: sign change located", False, "(none found)")
    cr.FROZEN_GENERAL = fg0

    print("FAILED:", FAILURES if FAILURES else "none -- all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
