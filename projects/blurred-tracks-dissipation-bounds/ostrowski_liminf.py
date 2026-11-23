#!/usr/bin/env python3
"""Per-truth liminf via Ostrowski digits of gamma (DERIVATION s26).

s25 proved, on the frozen general truth at irrational rho = eps/Delta,
  liminf_{m->inf} |R(m)|/m = 2 pi * min_j |h'(psi*_j)| * dist(xi*_j, Xi_j),
Xi_j the finite limit points of xi_m = m*(m*rho - gamma_j - n_m), and
found D_j(M) = min_{m<=M} |xi_m - xi*_j| flat from M=2e5 to 1e6 at the
golden ratio and sqrt(2)-1 (search).  This slice decides what can be
decided about dist(xi*_j, Xi_j) at those two quadratic rho.

Proof part (checked here, mostly exactly).  rho = [0;a,a,...] (a=1
golden, a=2 for sqrt(2)-1), convergents p_k/q_k (q_0=1, q_1=a).
- delta_k := q_k*rho - p_k = (-1)^k rho^{k+1} exactly in Q(sqrt(d)).
- Every m >= 0 has unique legal Ostrowski digits b_k (0<=b_k<=a,
  b_k=a => b_{k-1}=0); gamma has digits c_k in the same system
  (predecessor digits) with gamma = e + sum_k c_k delta_k, e in {0,1}.
- With J(m) = first index where b and c differ,
  xi_m = m * S_m, S_m = sum_{k>=J} (b_k-c_k) delta_k, exactly (no
  integer wrap) once J >= J0 (4 golden, 3 for sqrt(2)-1): both tails
  are O(rho^J), so |S_m| < 1/2 and n_m is forced.
- Prefix integers A_K = sum_{k<K} c_k q_k give xi_{A_K} = -A_K R_K,
  R_K = sum_{k>=K} c_k delta_k: an exact subsequence probing Xi.
- |q_J delta_J| -> L = rho/(1+rho^2) (1/sqrt5 golden, 1/(2 sqrt2)),
  and limit points factor through the (past, future) digit windows
  of gamma at position J.  Over ALL legal windows the image is dense
  around both xi*_j (exhibited below), so no argument using only
  finite windows of gamma's digits can prove dist > 0: positivity,
  if true, is a property of gamma's whole digit orbit.

Computation part.  gamma_j, xi*_j are recomputed in 100-digit mpmath
from the frozen matrices (independent route; agrees with s25 floats
to 1e-11).  gamma's Ostrowski digits are extracted to k=380 by an
exact integer predecessor algorithm (verified against brute force).
Prefix values xi_{A_K} (K<=380) plus a digit-pattern DFS at J<=150
give certified upper bounds (explicit m, xi_m from the exact S-sum,
error < 1e-40):

  golden, active zero:   dist <= 0.007503  => liminf |R|/m <= 0.0789
  sqrt(2)-1, active:     dist <= 0.001558  => liminf |R|/m <= 0.00517

Record lows keep falling with K (golden: 0.01476 at K=25 - which is
exactly s25's scan minimum, m=92549 - then 0.00750 at K=363;
sqrt(2)-1: 0.0611 at K=12, again s25's value, then 0.0148, 0.00927,
0.00588, 0.00532, 0.00156).  So s25's "flat" D_j(M) was a finite-range
effect: the liminf is at most half (golden) resp. 39x smaller
(sqrt(2)-1) than the scan suggested, the decay is consistent with
dist = 0 (liminf = 0), and deciding dist = 0 versus dist > 0 is
equivalent to a digit-density property of this specific gamma,
which no finite computation settles.  That is the decision: positive
liminf at s25's level is refuted; exact positivity is the named
open core (DERIVATION s26).  Scope: frozen truth, two quadratic rho;
the DFS/prefix parts are a search (upper bounds are rigorous for the
exhibited m); the window-density point is an exhibit plus the
tiling/P-surjectivity lemma of s26.
"""
from __future__ import annotations

import math
import random
import sys
from fractions import Fraction

import mpmath
from mpmath import mp, mpf, mpc, matrix

import window_constant as wc

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


# ---------------------------------------------------------------- Q(sqrt d)
def qadd(u, v):
    return (u[0] + v[0], u[1] + v[1])


def qmul(u, v, d):
    return (u[0] * v[0] + d * u[1] * v[1], u[0] * v[1] + u[1] * v[0])


CASES = [
    # name, a (CF period), d (Q(sqrt d)), rho as Q(sqrt d) pair
    ("golden", 1, 5, (Fraction(-1, 2), Fraction(1, 2))),
    ("sqrt2-1", 2, 2, (Fraction(-1), Fraction(1))),
]


def convergents(a, K):
    """p_k, q_k for rho=[0;a,a,...]: q_0=1, q_1=a, same recurrence."""
    p, q = [0, 1], [1, a]
    while len(q) <= K:
        p.append(a * p[-1] + p[-2])
        q.append(a * q[-1] + q[-2])
    return p, q


def greedy_digits(m, q):
    """Ostrowski digits of integer m (greedy from the top)."""
    if m == 0:
        return [0]
    kk = max(k for k, x in enumerate(q) if x <= m)
    b = [0] * (kk + 1)
    r = m
    for k in range(kk, -1, -1):
        b[k] = r // q[k]
        r -= b[k] * q[k]
    return b


def legal(digs, a):
    return all(0 <= digs[k] <= a and (digs[k] < a or k == 0 or digs[k - 1] == 0)
               for k in range(len(digs)))


# ------------------------------------------------- high-precision gamma, xi*
def _m2(a, b, c, d):
    m = matrix(2, 2)
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = a, b, c, d
    return m


def _inv2(m):
    det = m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0]
    return _m2(m[1, 1] / det, -m[0, 1] / det, -m[1, 0] / det, m[0, 0] / det)


def gamma_xi_star(rho, dps=185):
    """Recompute (psi*_j, gamma_j, xi*_j, 2 pi |h'_j|) in mpmath.

    Replicates window_constant.Ctx from the frozen matrices, with the
    zeros of h in closed form: Re(alpha c2 / D(phi)) = 0 iff D(phi)
    is a real multiple of -i*alpha*c2 (ellipse meet line: quadratic).
    """
    with mpmath.workdps(dps):
        A = _m2(mpf("-1.2"), mpf(-2), mpf("0.8"), mpf("-0.7"))
        Dm = _m2(mpf(1), mpf("0.3"), mpf("0.3"), mpf("0.6"))
        Delta = mpf("0.9")
        K = matrix(4, 4)
        for i in range(2):
            for j in range(2):
                for p_ in range(2):
                    for q_ in range(2):
                        K[j * 2 + i, q_ * 2 + p_] += (
                            A[i, p_] * (1 if j == q_ else 0)
                            + (1 if i == p_ else 0) * A[j, q_])
        rhs = matrix([-2 * Dm[0, 0], -2 * Dm[1, 0], -2 * Dm[0, 1], -2 * Dm[1, 1]])
        xv = mp.lu_solve(K, rhs)
        Sigma = _m2(xv[0], xv[2], xv[1], xv[3])

        def int_exp(M, eps):
            Mx = matrix(4, 4)
            for i in range(2):
                for j in range(2):
                    Mx[i, j] = M[i, j] * eps
                Mx[i, 2 + i] = eps
            E = mp.expm(Mx)
            return _m2(E[0, 2], E[0, 3], E[1, 2], E[1, 3])

        eps = rho * Delta

        def observed(k):
            G = int_exp(A, eps) * int_exp(-A, eps) * Sigma
            return mp.expm(A * (k * Delta)) * G / eps ** 2

        G1, G2 = observed(1), observed(2)
        Phi = G2 * _inv2(G1)
        a_, b_, c_, d_ = Phi[0, 0], Phi[0, 1], Phi[1, 0], Phi[1, 1]
        tr, det = a_ + d_, a_ * d_ - b_ * c_
        lam1 = tr / 2 + mp.sqrt(mpc(tr * tr / 4 - det, 0))
        r, theta = abs(lam1), mp.arg(lam1)
        v1 = (mpc(b_), lam1 - a_) if abs(b_) > abs(c_) else (lam1 - d_, mpc(c_))
        v2 = (mp.conj(v1[0]), mp.conj(v1[1]))
        P = _m2(v1[0], v2[0], v1[1], v2[1])
        detP = v1[0] * v2[1] - v2[0] * v1[1]
        Pinv = _m2(v2[1] / detP, -v2[0] / detP, -v1[1] / detP, v1[0] / detP)
        PhiInvG1 = _inv2(Phi) * G1
        Gc = _m2(mpc(PhiInvG1[0, 0]), mpc(PhiInvG1[0, 1]),
                 mpc(PhiInvG1[1, 0]), mpc(PhiInvG1[1, 1]))
        Ghat = Pinv * Gc * P

        def form(dd):
            Dg = _m2(dd, mpc(0), mpc(0), mp.conj(dd))
            S = P * Dg * Ghat * Pinv
            return mp.re(S[0, 1] - S[1, 0])

        alpha = mpc(form(mpc(1)), -form(mpc(0, 1)))
        aa = r ** rho
        Aell, Bell = aa + 1 / aa, aa - 1 / aa
        s = mp.log(r)
        c2 = -(2 * mp.pi / Delta) ** 2
        c1 = (4 * mp.pi / Delta ** 2) * (mpc(0, 1) * s - theta)
        w = -mpc(0, 1) * alpha * c2
        u, v = mp.re(w), mp.im(w)
        qa = u * u / Aell ** 2 + v * v / Bell ** 2
        qb = 4 * u / Aell ** 2
        qc = 4 / Aell ** 2 - 1
        disc = mp.sqrt(qb * qb - 4 * qa * qc)
        out = []
        for lam in ((-qb + disc) / (2 * qa), (-qb - disc) / (2 * qa)):
            cosphi, sinphi = (2 + lam * u) / Aell, lam * v / Bell
            psi = mp.atan2(sinphi, cosphi) % (2 * mp.pi)
            D = mpc(Aell * cosphi - 2, Bell * sinphi)
            Dp = mpc(-Aell * sinphi, Bell * cosphi)
            hp = eps ** 2 * mp.re(alpha * c2 * (-Dp) / D ** 2)
            h1 = eps ** 2 * mp.re(alpha * c1 / D)
            xi_star = -h1 / (2 * mp.pi * hp)
            gam = (psi / (2 * mp.pi) - rho * theta / (2 * mp.pi)) % 1
            out.append((+psi, +gam, +xi_star, +(2 * mp.pi * abs(hp))))
        return out  # [active-ish?, ...] sorted by 2pi|h'| at call site


# ------------------------------------------------------------- gamma digits
def predecessor_j(gam, rho, p, q, K):
    """j < q_K maximizing {j*rho} <= gamma, exactly.

    {j*rho} = (s_j + j*delta_K)/q_K with s_j = (j p_K) mod q_K and
    delta_K = (-1)^K rho^{K+1}; candidates s near floor(gamma q_K)
    via p_K^{-1} == (-1)^{K-1} q_{K-1} (mod q_K).  All comparisons in
    the scaled form, which keeps full precision for huge q_K.
    """
    qK = q[K]
    gq = gam * qK
    s_star = int(mp.floor(gq))
    pinv = (((-1) ** (K - 1)) * q[K - 1]) % qK if K >= 1 else 0
    dK = ((-1) ** K) * rho ** (K + 1)
    best_j, best_d = None, None
    for s in (s_star - 2, s_star - 1, s_star, s_star + 1, s_star + 2):
        j = (s * pinv) % qK
        val = mpf(s % qK) + mpf(j) * dK
        if val < 0:
            val += qK
        if val >= qK:
            val -= qK
        d = val / qK - gam
        if d <= 0 and (best_d is None or d > best_d):
            best_d, best_j = d, j
    return best_j


def gamma_digits(gam, rho, a, K):
    """Predecessor Ostrowski digits of gamma to length K, and e."""
    p, q = convergents(a, K + 2)
    j = predecessor_j(gam, rho, p, q, K)
    cs = greedy_digits(j, q)
    cs = cs + [0] * (K - len(cs))
    dfl = [((-1) ** k) * rho ** (k + 1) for k in range(K)]
    ssum = sum(mpf(cs[k]) * dfl[k] for k in range(K))
    frac = (mpf(j) * rho) % 1 if j < 10 ** 30 else None
    if frac is not None:
        e = int(mp.nint(frac - ssum))
    else:
        e = int(mp.nint(gam - ssum))  # tail beyond K is < rho^K, negligible
    return cs, e, q


# ------------------------------------------------------------------- xi_m
class XiMachine:
    """xi_m via the exact S-decomposition for one (rho, gamma)."""

    def __init__(self, rho, a, gam, K=430):
        self.rho, self.a, self.gam = rho, a, gam
        self.cs, self.e, self.q = gamma_digits(gam, rho, a, K)
        self.K = K
        self.dfl = [((-1) ** k) * rho ** (k + 1) for k in range(K)]
        # prefix integers A_K and tails R_K
        self.A = [0] * (K + 1)
        for J in range(1, K + 1):
            self.A[J] = self.A[J - 1] + self.cs[J - 1] * self.q[J - 1]
        self.R = [mpf(0)] * (K + 1)
        for kk in range(K - 1, -1, -1):
            self.R[kk] = self.cs[kk] * self.dfl[kk] + self.R[kk + 1]

    def xi_of_m(self, m):
        """xi_m = m*(S - round(S)), S = sum_{k>=J(m)} (b_k-c_k) delta_k."""
        b = greedy_digits(m, self.q)
        cs = self.cs
        J = next(k for k in range(self.K)
                 if (b[k] if k < len(b) else 0) != cs[k])
        S = sum(mpf((b[k] if k < len(b) else 0) - cs[k]) * self.dfl[k]
                for k in range(J, self.K))
        return mpf(m) * (S - mp.nint(S)), J

    def xi_direct(self, m):
        v = mpf(m) * self.rho - self.gam
        return mpf(m) * (v - mp.nint(v))

    def xi_prefix(self, K):
        return -mpf(self.A[K]) * self.R[K]

    def tail_abs_bound(self, J):
        """max |sum_{k>=J} d_k delta_k| over legal d (DP, float)."""
        rho_f = float(self.rho)
        a = self.a
        KMAX = J + 60
        dfl = [((-1) ** k) * rho_f ** (k + 1) for k in range(KMAX + 2)]
        T = [[(0.0, 0.0), (0.0, 0.0)] for _ in range(KMAX + 3)]
        for kk in range(KMAX, -1, -1):
            for pn in (0, 1):
                cmax = a if pn == 0 else a - 1
                los, his = [], []
                for c in range(cmax + 1):
                    lo, hi = T[kk + 1][1 if c != 0 else 0]
                    los.append(c * dfl[kk] + lo)
                    his.append(c * dfl[kk] + hi)
                T[kk][pn] = (min(los), max(his))
        return max(abs(T[J][pn][i]) for pn in (0, 1) for i in (0, 1))


def dfs_best(xm, xi_star_f, Jmax=150, depth=24):
    """Digit-pattern search: min |xi_m - xi*| over patterns at J<=Jmax.

    Float approximation for filtering, exact S-evaluation of finalists.
    """
    rho_f = float(xm.rho)
    lam = 1.0 / rho_f
    x = -rho_f
    a = xm.a
    L = rho_f / (1 + rho_f * rho_f)
    cs, q, A = xm.cs, xm.q, xm.A
    best = [math.inf, None]
    for J in range(1, Jmax + 1):
        PJf = float(mpf(A[J]) / mpf(q[J]))
        qJdJ = (1 if J % 2 == 0 else -1) * L * (1 - ((-rho_f ** 2) ** (J + 1)))
        cands = []

        def dfs(j, pn, U, D, bd):
            if bd and bd[-1] != 0:
                Dt = D
                for i in range(j, min(j + 42, xm.K - J)):
                    Dt += (0 - cs[J + i]) * (x ** i)
                approx = (PJf + U) * qJdJ * Dt
                if abs(approx - xi_star_f) < 0.08:
                    cands.append(list(bd))
            if j >= depth:
                return
            rj = D / (x ** j) if j > 0 else D
            if abs(rj) > 45:
                return
            tau = a * rho_f ** (j + 1) / (1 - rho_f)
            if (PJf + U) * L * 0.99 * max(0.0, abs(D) - tau) > abs(xi_star_f) + 0.4:
                return
            cmax = a - 1 if pn else a
            for bdig in range(cmax + 1):
                if j == 0 and bdig == cs[J]:
                    continue
                dfs(j + 1, bdig != 0, U + bdig * lam ** j,
                    D + (bdig - cs[J + j]) * (x ** j), bd + [bdig])

        dfs(0, cs[J - 1] != 0, 0.0, 0.0, [])
        for bd in cands[:40]:
            m = A[J] + sum(bd[j] * q[J + j] for j in range(len(bd)))
            xv, _J = xm.xi_of_m(m)
            dd = float(abs(xv - mpf(xi_star_f)))
            if dd < best[0]:
                best[0], best[1] = dd, m
    return best


def xi_max_density(rho_f, a, xi_star_f, trials=30000, seed=11):
    """Sample Xi over ALL legal windows (not gamma's): bracket width."""
    rng = random.Random(seed)
    lam = 1.0 / rho_f
    x = -rho_f
    L = rho_f / (1 + rho_f * rho_f)

    def rand_legal(n, pn=False):
        s = []
        for _ in range(n):
            c = rng.randint(0, a - 1 if pn else a)
            s.append(c)
            pn = c != 0
        return s

    below, above = -math.inf, math.inf
    for _ in range(trials):
        past = rand_legal(22)
        P = sum(past[i] * rho_f ** (i + 1) for i in range(len(past)))
        cfut = rand_legal(22)
        bf = rand_legal(rng.randint(1, 16))
        if bf[0] == cfut[0]:
            continue
        U = sum(bf[j] * lam ** j for j in range(len(bf)))
        D = sum(((bf[j] if j < len(bf) else 0) - cfut[j]) * x ** j
                for j in range(len(cfut)))
        for sgn in (1, -1):
            v = sgn * L * (P + U) * D
            if v < xi_star_f:
                below = max(below, v)
            elif v > xi_star_f:
                above = min(above, v)
    return below, above


def main() -> int:
    mp.dps = 190
    rho_of = {"golden": (mp.sqrt(5) - 1) / 2, "sqrt2-1": mp.sqrt(2) - 1}

    # 1. exact Q(sqrt d) identities
    for name, a, d, rhoq in CASES:
        p, q = convergents(a, 30)
        pw = rhoq
        ok = True
        for k in range(26):
            dk = qadd(qmul((Fraction(q[k]), Fraction(0)), rhoq, d),
                      (Fraction(-p[k]), Fraction(0)))
            want = pw if k % 2 == 0 else (-pw[0], -pw[1])
            ok = ok and dk == want
            pw = qmul(pw, rhoq, d)
        rel = qadd(qmul(rhoq, rhoq, d),
                   qmul((Fraction(a), Fraction(0)), rhoq, d))
        ok = ok and rel == (Fraction(1), Fraction(0))
        check(f"{name}: delta_k = (-1)^k rho^(k+1) exact in Q(sqrt{d}), "
              f"rho^2 + {a} rho = 1", ok)
        # greedy digit legality/reconstruction, brute
        ok2 = all(legal(greedy_digits(m, q), a)
                  and sum(b * q[k] for k, b in enumerate(greedy_digits(m, q))) == m
                  for m in range(q[10]))
        check(f"{name}: integer Ostrowski digits legal and reconstruct m<q_10", ok2)

    results = {}
    for name, a, d, _rq in CASES:
        rho = rho_of[name]
        rho_f = float(rho)
        zeros = sorted(gamma_xi_star(rho), key=lambda t: t[3])
        # cross-check against s25 float route
        cx = wc.Ctx(rho_f)
        fzeros = []
        for z in cx.zeros():
            hp = cx.hp(z)
            xs = -cx.hj(cx.c1, z) / (2 * math.pi * hp)
            gm = (z / (2 * math.pi) - rho_f * cx.th / (2 * math.pi)) % 1.0
            fzeros.append((z, gm, xs, 2 * math.pi * abs(hp)))
        fzeros.sort(key=lambda t: t[3])
        agree = all(abs(float(zeros[i][1]) - fzeros[i][1]) < 1e-11
                    and abs(float(zeros[i][2]) - fzeros[i][2]) < 1e-9
                    and abs(float(zeros[i][3]) - fzeros[i][3]) < 1e-6 * fzeros[i][3]
                    for i in range(2))
        check(f"{name}: mpmath gamma/xi*/2pi|h'| agree with s25 floats", agree,
              f"(active 2pi|h'| = {float(zeros[0][3]):.4f})")

        case_res = []
        for zi, (psi, gam, xi_star, tpi_hp) in enumerate(zeros):
            tag = "active" if zi == 0 else "inactive"
            xm = XiMachine(rho, a, gam, K=430)
            # digits: series + stabilization + predecessor brute check
            p12, q12 = convergents(a, 14)
            bj = predecessor_j(gam, rho, p12, q12, 12)
            gf = float(gam)
            bj2, bv = None, -1.0
            for j in range(q12[12]):
                v = (j * rho_f) % 1.0
                if v <= gf and v > bv:
                    bv, bj2 = v, j
            cs190, _e190, _q190 = gamma_digits(gam, rho, a, 190)
            stab = all(cs190[k] == xm.cs[k] for k in range(185))
            series_err = abs(gam - xm.e - xm.R[0])
            check(f"{name}/{tag}: gamma digits (pred vs brute, series, stable)",
                  bj == bj2 and stab and series_err < mpf("1e-60")
                  and legal(xm.cs, a),
                  f"(e={xm.e}, c[0:24]={''.join(map(str, xm.cs[:24]))})")
            # xi via S vs direct
            worst = max(abs(xm.xi_of_m(m)[0] - xm.xi_direct(m))
                        for m in (1, 17, 12345, 92549, 199999))
            check(f"{name}/{tag}: xi_m via S-decomposition = direct",
                  worst < mpf("1e-40"), f"(worst {mp.nstr(worst, 2)})")
            # N'=0 lemma range: |S| <= 2*tail_bound(J) < 1/2
            J0 = 4 if a == 1 else 3
            tb = xm.tail_abs_bound(J0)
            check(f"{name}/{tag}: |S_m| < 1/2 for J(m) >= {J0} (no wrap)",
                  2 * tb < 0.5, f"(2*tail bound = {2 * tb:.4f})")
            # prefix formula
            okp = all(abs(xm.xi_prefix(K) - xm.xi_of_m(xm.A[K])[0]) < mpf("1e-40")
                      for K in (10, 25, 40, 80) if xm.A[K] > 0)
            check(f"{name}/{tag}: xi_(A_K) = -A_K R_K", okp)
            # record lows over prefixes
            best = (math.inf, None)
            records = []
            for K in range(2, 381):
                if xm.A[K] == 0:
                    continue
                dd = float(abs(xm.xi_prefix(K) - xi_star))
                if dd < best[0]:
                    best = (dd, K)
                    records.append((K, dd))
            dbest = dfs_best(xm, float(xi_star))
            dist_ub = min(best[0], dbest[0])
            print(f"    {name}/{tag}: prefix record lows "
                  + ", ".join(f"K={K}:{v:.6f}" for K, v in records)
                  + (f" | DFS best {dbest[0]:.6f}" if dbest[1] is not None else " | DFS: none within filter"))
            case_res.append((tag, float(tpi_hp), dist_ub, best, dbest))
        results[name] = case_res

    # s25 consistency: prefix values at the scan argminima
    g_act = results["golden"][0]
    s_act = results["sqrt2-1"][0]
    check("golden active: dist upper bound (prefix K=25 is s25's 0.01476)",
          g_act[2] <= 0.00751, f"(dist <= {g_act[2]:.6f}, s25 scan 0.01476)")
    check("sqrt2-1 active: dist upper bound (s25 scan was 0.06056)",
          s_act[2] <= 0.0016, f"(dist <= {s_act[2]:.6f}, s25 scan 0.06056)")
    for name in ("golden", "sqrt2-1"):
        act = results[name][0]
        lim = act[1] * act[2]
        inact = results[name][1]
        print(f"    {name}: liminf |R(m)|/m <= {act[1]:.4f} * {act[2]:.6f} "
              f"= {lim:.6f} (active zero); inactive term <= "
              f"{inact[1] * inact[2]:.3f}")
    check("golden: liminf |R(m)|/m <= 0.0789 (s25 scan-level 0.1553 refuted)",
          results["golden"][0][1] * results["golden"][0][2] <= 0.079)
    check("sqrt2-1: liminf |R(m)|/m <= 0.00517 (s25 scan-level 0.2024 refuted)",
          results["sqrt2-1"][0][1] * results["sqrt2-1"][0][2] <= 0.0053)

    # Xi over all legal windows is dense at xi*: finite windows alone
    # cannot prove dist > 0 (exhibit, seeded search)
    for name, a, _d, _rq in CASES:
        rho_f = float(rho_of[name])
        xs = float(sorted(gamma_xi_star(rho_of[name]), key=lambda t: t[3])[0][2])
        below, above = xi_max_density(rho_f, a, xs)
        check(f"{name}: all-windows Xi brackets xi* within 0.005",
              below < xs < above and above - below < 0.005,
              f"(bracket width {above - below:.5f}; window-only positivity"
              f" proofs are impossible)")

    print("\nFAILED:", FAILURES if FAILURES else "none -- all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
