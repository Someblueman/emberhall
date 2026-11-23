#!/usr/bin/env python3
"""Milestone 3g: finite-record branch reports, general (non-isotropic) case.

Milestone 3 (s12-s17) finished the isotropic vortex.  This slice
carries the same programme to the general case of s7/s11
(general_tracks.py): arbitrary stable drift A and diffusion Dm,
where branch compatibility is tested by the symmetry residual
R(m) = (Sigma_m)01 - (Sigma_m)10 of the stationary covariance
implied by branch drift A_m.  Frozen general example:
A = [[-1.2, -2.0], [0.8, -0.7]], Dm = [[1, 0.3], [0.3, 0.6]],
Delta = 0.9, eps = 0.45, ell2 = 0.03; the true branch is m = 0.

Calibration mirrors s16.  The frame series is a zero-mean real
Gaussian stationary vector series with known population covariances
Gamma_h, so Isserlis gives, for the moment estimators
Ghat_k = (1/(N-k)) sum_n y_{n+k} y_n^T,

  N Cov(Ghat_k[i,j], Ghat_l[p,q]) ->
    sum_h [ Gamma_{k-l-h}[i,p] Gamma_{-h}[j,q]
          + Gamma_{k-h}[i,q]  Gamma_{-l-h}[j,p] ].

R(0) is a smooth function of the 11 distinct entries of
(Ghat_0, Ghat_1, Ghat_2) (Ghat_0 symmetric), so the delta method
(numeric gradient at the population point, through the branch
construction of verify_general.py) gives Var(R) = v_R / N and
tau(N) = 1.96 sqrt(v_R/N).  Sets keep branches whose |R| is within
tau of the best; |R_true| <= tau is sufficient for retention, so
asymptotic in-model coverage is at least 95%.

The second half (s19) derives delta-method slacks for the general
test's remaining population conditions (Sigma, Dm positive
definite; zero-lag off-diagonal; equal diagonal ell2) and measures
hard vs calibrated eligibility: hard sign-filters delete the true
branch in 9/24 films at N=1000, per-condition 95% slacks undercover
jointly (multiple conditions multiply), Bonferroni 99% slacks
nearly recover symmetry-only coverage while trimming set size.
Branches are searched in m in [-5, 5] (s11 gives completeness over
all m at population level; the window is a finite-record cost
choice).  Simulation is exact-transition substeps with trapezoid
frame averages, as elsewhere in milestone 3.  The delta-method sd
is Monte-Carlo checked on fresh seeds before coverage is measured
on seeded replicates (seed base 424242, same scheme as s8).
"""
from __future__ import annotations

import math
import random
import statistics
import sys

from general_tracks import (FROZEN_GENERAL, GeneralVortex, add,
                            branch_drifts, expm, int_exp, int_exp_weighted,
                            inverse2, matmul, scale, transpose)
from finite_record import FRAME_COUNTS, REPLICATES, SEED0

TRUE_M = 0
M_VALUES = range(-5, 6)
Z975 = 1.959963984540054
MC_SEED0 = 999000
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


# --- symmetry residual as a function of the three covariances --------------

def _min_eig_sym(M):
    a, b, d = M[0][0], 0.5 * (M[0][1] + M[1][0]), M[1][1]
    return 0.5 * (a + d) - math.sqrt((0.5 * (a - d)) ** 2 + b * b)


def branch_quantities_general(G0, G1, G2, Delta, eps, m):
    """All population-test quantities of branch m, or None if unavailable.

    Keys: R (symmetry residual), off (zero-lag off-diagonal residual),
    eq_ell (diagonal ell2 mismatch), ell (mean implied ell2),
    lam_S / lam_D (smallest eigenvalues of symmetrized Sigma and Dm).
    At the population true branch: R = off = eq_ell = 0, ell = ell2,
    lam_S, lam_D > 0.
    """
    try:
        Phi = matmul(G2, inverse2(G1))
        Am = dict(branch_drifts(Phi, Delta, [m]))[m]
        U = int_exp(Am, eps)
        W = int_exp(scale(Am, -1.0), eps)
        S = scale(matmul(inverse2(matmul(U, W)), matmul(inverse2(Phi), G1)),
                  eps ** 2)
    except ValueError:
        return None
    Ss = [[S[0][0], 0.5 * (S[0][1] + S[1][0])],
          [0.5 * (S[0][1] + S[1][0]), S[1][1]]]
    Dm = scale(add(matmul(Am, Ss), matmul(Ss, transpose(Am))), -0.5)
    U2S = matmul(int_exp_weighted(Am, eps), Ss)
    P0 = scale(add(U2S, transpose(U2S)), 1.0 / eps ** 2)
    ell_a, ell_b = G0[0][0] - P0[0][0], G0[1][1] - P0[1][1]
    return {"R": S[0][1] - S[1][0], "off": G0[0][1] - P0[0][1],
            "eq_ell": ell_a - ell_b, "ell": 0.5 * (ell_a + ell_b),
            "lam_S": _min_eig_sym(Ss), "lam_D": _min_eig_sym(Dm)}


def symmetry_residual(G0, G1, G2, Delta, eps, m):
    """R(m) = (Sigma_m)01 - (Sigma_m)10; None if the branch is unavailable."""
    q = branch_quantities_general(G0, G1, G2, Delta, eps, m)
    return None if q is None else q["R"]


def delta_sds(g, Delta, eps, ell2, keys, m=TRUE_M):
    """Delta-method sd*sqrt(N) for each named branch quantity at branch m."""
    Gs = [g.observed_cov_matrix(Delta, eps, ell2, k) for k in (0, 1, 2)]
    x0 = pack(Gs)
    S = moment_covariance_real(g, Delta, eps, ell2)
    out = {}
    for key in keys:
        def f(x, key=key):
            G = unpack(x)
            return branch_quantities_general(G[0], G[1], G[2],
                                             Delta, eps, m)[key]
        grad = []
        for i in range(len(x0)):
            h = 1e-6 * max(1.0, abs(x0[i]))
            xp, xm = list(x0), list(x0)
            xp[i] += h
            xm[i] -= h
            grad.append((f(xp) - f(xm)) / (2.0 * h))
        var = sum(grad[a] * S[a][b] * grad[b]
                  for a in range(len(x0)) for b in range(len(x0)))
        out[key] = math.sqrt(var)
    return out


COORDS = [(0, 0, 0), (0, 0, 1), (0, 1, 1),
          (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1),
          (2, 0, 0), (2, 0, 1), (2, 1, 0), (2, 1, 1)]


def pack(Gs):
    return [Gs[k][i][j] for (k, i, j) in COORDS]


def unpack(x):
    Gs = [[[0.0, 0.0], [0.0, 0.0]] for _ in range(3)]
    for val, (k, i, j) in zip(x, COORDS):
        Gs[k][i][j] = val
        if k == 0:
            Gs[k][j][i] = val
    return Gs


def moment_covariance_real(g, Delta, eps, ell2, half_width=200):
    """11x11 asymptotic N*Cov of pack(Ghat_0..2) from Isserlis."""
    def Gam(h):
        return g.observed_cov_matrix(Delta, eps, ell2, h)
    cache = {h: Gam(h) for h in range(-2 * half_width - 3, 2 * half_width + 4)}
    S = [[0.0] * len(COORDS) for _ in COORDS]
    for a, (k, i, j) in enumerate(COORDS):
        for b, (l, p, q) in enumerate(COORDS):
            s = 0.0
            for h in range(-half_width, half_width + 1):
                s += cache[k - l - h][i][p] * cache[-h][j][q]
                s += cache[k - h][i][q] * cache[-l - h][j][p]
            S[a][b] = s
    return S


def delta_variance_R(g, Delta, eps, ell2, m=TRUE_M):
    Gs = [g.observed_cov_matrix(Delta, eps, ell2, k) for k in (0, 1, 2)]
    x0 = pack(Gs)
    S = moment_covariance_real(g, Delta, eps, ell2)

    def f(x):
        G = unpack(x)
        return symmetry_residual(G[0], G[1], G[2], Delta, eps, m)

    grad = []
    for i in range(len(x0)):
        h = 1e-6 * max(1.0, abs(x0[i]))
        xp, xm = list(x0), list(x0)
        xp[i] += h
        xm[i] -= h
        grad.append((f(xp) - f(xm)) / (2.0 * h))
    return sum(grad[a] * S[a][b] * grad[b]
               for a in range(len(x0)) for b in range(len(x0)))


# --- simulation ------------------------------------------------------------

def _chol2(M):
    """Lower Cholesky factor of a 2x2 SPD matrix."""
    l00 = math.sqrt(M[0][0])
    l10 = M[1][0] / l00
    l11 = math.sqrt(max(M[1][1] - l10 * l10, 0.0))
    return [[l00, 0.0], [l10, l11]]


def _step_mats(A, Sigma, h):
    E = expm(scale(A, h))
    Q = [[Sigma[i][j] - sum(E[i][t] * Sigma[t][u] * E[j][u]
                            for t in range(2) for u in range(2))
          for j in range(2)] for i in range(2)]
    return E, _chol2(Q)


def simulate_general_frames(g, Delta, eps, ell2, n_frames, seed, sub=20):
    rng = random.Random(seed)
    A, Sigma = g.A, g.Sigma
    h = eps / sub
    E_sub, L_sub = _step_mats(A, Sigma, h)
    E_gap, L_gap = _step_mats(A, Sigma, Delta - eps)
    L0 = _chol2(Sigma)
    noise_sd = math.sqrt(ell2)

    def mv(M, x):
        return [M[0][0] * x[0] + M[0][1] * x[1],
                M[1][0] * x[0] + M[1][1] * x[1]]

    def innov(L):
        z1, z2 = rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)
        return [L[0][0] * z1, L[1][0] * z1 + L[1][1] * z2]

    x = innov(L0)
    frames = []
    for _ in range(n_frames):
        acc = [0.5 * x[0], 0.5 * x[1]]
        for _i in range(sub):
            xn = mv(E_sub, x)
            iv = innov(L_sub)
            x = [xn[0] + iv[0], xn[1] + iv[1]]
            acc[0] += x[0]
            acc[1] += x[1]
        acc[0] -= 0.5 * x[0]
        acc[1] -= 0.5 * x[1]
        frames.append([acc[0] / sub + rng.gauss(0.0, noise_sd),
                       acc[1] / sub + rng.gauss(0.0, noise_sd)])
        xn = mv(E_gap, x)
        iv = innov(L_gap)
        x = [xn[0] + iv[0], xn[1] + iv[1]]
    return frames


def empirical_Gamma(frames, k):
    n = len(frames) - k
    G = [[0.0, 0.0], [0.0, 0.0]]
    for t in range(n):
        a, b = frames[t + k], frames[t]
        G[0][0] += a[0] * b[0]
        G[0][1] += a[0] * b[1]
        G[1][0] += a[1] * b[0]
        G[1][1] += a[1] * b[1]
    return [[G[i][j] / n for j in range(2)] for i in range(2)]


def main() -> int:
    fg = FROZEN_GENERAL
    Delta, eps, ell2 = fg["Delta"], fg["eps"], fg["ell2"]
    g = GeneralVortex(fg["A"], fg["Dm"])
    Gs = [g.observed_cov_matrix(Delta, eps, ell2, k) for k in (0, 1, 2)]
    pop_R = {m: symmetry_residual(Gs[0], Gs[1], Gs[2], Delta, eps, m)
             for m in M_VALUES}
    rival = min(abs(pop_R[m]) for m in M_VALUES if m != TRUE_M)
    print(f"Frozen general example: true m={TRUE_M}, population R(0) = "
          f"{pop_R[TRUE_M]:.2e}, nearest rival |R| = {rival:.4f} in "
          f"m in [-5, 5]; sigma = {g.dissipation():.4f}")
    vR = delta_variance_R(g, Delta, eps, ell2)
    print(f"Delta method: sd(R)*sqrt(N) = {math.sqrt(vR):.4f}")
    for n in FRAME_COUNTS:
        print(f"  N={n:>5}: tau_95 = {Z975 * math.sqrt(vR / n):.4f}")

    # Monte Carlo check of sd(R) at N=1000 on fresh seeds.
    Rs = []
    for r in range(48):
        frames = simulate_general_frames(g, Delta, eps, ell2, 1000,
                                         MC_SEED0 + r)
        Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
        R = symmetry_residual(Gh[0], Gh[1], Gh[2], Delta, eps, TRUE_M)
        if R is not None:
            Rs.append(R)
    sd_mc = statistics.stdev(Rs)
    sd_d = math.sqrt(vR / 1000)
    check("delta-method sd(R) matches Monte Carlo (general case)",
          0.75 <= sd_mc / sd_d <= 1.3,
          f"(MC {sd_mc:.4f} vs delta {sd_d:.4f}, {len(Rs)}/48 usable, "
          f"MC mean R {statistics.mean(Rs):+.4f})")

    # Coverage of calibrated sets on seeded replicates.
    print(f"\nCalibrated symmetry-residual sets (R={REPLICATES}, "
          f"seed base {SEED0}, branches [-5, 5]):")
    for n in FRAME_COUNTS:
        tau = Z975 * math.sqrt(vR / n)
        cover, wins, sizes, usable = 0, 0, [], 0
        for r in range(REPLICATES):
            frames = simulate_general_frames(g, Delta, eps, ell2, n,
                                             SEED0 + 1000 * n + r)
            Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
            res = {}
            for m in M_VALUES:
                R = symmetry_residual(Gh[0], Gh[1], Gh[2], Delta, eps, m)
                if R is not None:
                    res[m] = R
            if TRUE_M not in res or not res:
                sizes.append(0)
                continue
            usable += 1
            best = min(abs(R) for R in res.values())
            s = [m for m, R in res.items() if abs(R) <= best + tau]
            sizes.append(len(s))
            cover += TRUE_M in s
            wins += min(res, key=lambda m: abs(res[m])) == TRUE_M
        print(f"  N={n:>5} tau={tau:.4f}: coverage {cover}/{REPLICATES} "
              f"({usable} usable), true branch wins {wins}/{REPLICATES}, "
              f"median set size {statistics.median(sizes):.0f} "
              f"(max {max(sizes)})")

    # s19: derived slacks for the remaining population conditions.
    keys = ("off", "eq_ell", "ell", "lam_S", "lam_D")
    sds = delta_sds(g, Delta, eps, ell2, keys)
    pop_q = branch_quantities_general(Gs[0], Gs[1], Gs[2], Delta, eps, TRUE_M)
    print("\nEligibility slacks (delta method at true branch):")
    for key in keys:
        print(f"  {key}: population {pop_q[key]:+.4f}, "
              f"sd*sqrt(N) = {sds[key]:.4f}")
    # Monte Carlo check on fresh seeds at N=1000 (same films as above
    # would couple the checks; use the MC_SEED0 films' quantities).
    mc = {key: [] for key in keys}
    for r in range(48):
        frames = simulate_general_frames(g, Delta, eps, ell2, 1000,
                                         MC_SEED0 + r)
        Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
        q = branch_quantities_general(Gh[0], Gh[1], Gh[2], Delta, eps, TRUE_M)
        if q is not None:
            for key in keys:
                mc[key].append(q[key])
    for key in keys:
        sd_mc_k = statistics.stdev(mc[key])
        sd_d_k = sds[key] / math.sqrt(1000)
        # lam_min is a concave, nonlinear function of the matrix, so
        # its first-order sd overestimates the true sd (conservative
        # for a slack); allow that direction a wider band.
        lo = 0.55 if key.startswith("lam") else 0.7
        check(f"delta sd({key}) matches Monte Carlo",
              lo <= sd_mc_k / sd_d_k <= 1.4,
              f"(MC {sd_mc_k:.4f} vs delta {sd_d_k:.4f}; MC mean "
              f"{statistics.mean(mc[key]):+.4f} vs population "
              f"{pop_q[key]:+.4f})")

    print("\nHard eligibility vs calibrated slacks (same replicates):")
    Z_BONF = 2.5758293035489004  # per-condition 99%: union bound over 5
    for n in FRAME_COUNTS:
        tau = Z975 * math.sqrt(vR / n)
        sl = {key: Z975 * sds[key] / math.sqrt(n) for key in keys}
        sl_b = {key: Z_BONF * sds[key] / math.sqrt(n) for key in keys}
        cov_hard, cov_cal, cov_bonf, hard_deletes, sizes_cal = 0, 0, 0, 0, []
        for r in range(REPLICATES):
            frames = simulate_general_frames(g, Delta, eps, ell2, n,
                                             SEED0 + 1000 * n + r)
            Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
            qs = {}
            for m in M_VALUES:
                q = branch_quantities_general(Gh[0], Gh[1], Gh[2],
                                              Delta, eps, m)
                if q is not None:
                    qs[m] = q
            if TRUE_M not in qs:
                sizes_cal.append(0)
                continue

            def sym_set(elig):
                cand = [m for m in qs if elig(qs[m])]
                if not cand:
                    return []
                best = min(abs(qs[m]["R"]) for m in cand)
                return [m for m in cand if abs(qs[m]["R"]) <= best + tau]

            hard = lambda q: (q["lam_S"] > 0 and q["lam_D"] > 0  # noqa: E731
                              and q["ell"] >= 0)
            def cal_with(sl_):
                return lambda q: (q["lam_S"] >= -sl_["lam_S"]
                                  and q["lam_D"] >= -sl_["lam_D"]
                                  and q["ell"] >= -sl_["ell"]
                                  and abs(q["off"]) <= sl_["off"]
                                  and abs(q["eq_ell"]) <= sl_["eq_ell"])
            if not hard(qs[TRUE_M]):
                hard_deletes += 1
            cov_hard += TRUE_M in sym_set(hard)
            s_cal = sym_set(cal_with(sl))
            cov_cal += TRUE_M in s_cal
            cov_bonf += TRUE_M in sym_set(cal_with(sl_b))
            sizes_cal.append(len(s_cal))
        print(f"  N={n:>5}: hard sign-filters delete the true branch in "
              f"{hard_deletes}/{REPLICATES} replicates; coverage hard "
              f"{cov_hard}/{REPLICATES}, per-condition 95% slacks "
              f"{cov_cal}/{REPLICATES}, Bonferroni 99% slacks "
              f"{cov_bonf}/{REPLICATES} (symmetry-only 24/24; "
              f"median set size {statistics.median(sizes_cal):.0f})")

    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\nFAILED: none -- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
