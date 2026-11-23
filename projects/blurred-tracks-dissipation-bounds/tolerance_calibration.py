#!/usr/bin/env python3
"""Milestone 3e: calibrate the branch-report tolerance from sampling theory.

Sections 12-15 used guessed tolerances (tau in {0.01, 0.03, 0.1} rad,
ell2 slack 0.02).  This slice derives them.  The frame series of the
frozen s8 design is a zero-mean proper complex Gaussian stationary
series with known population autocovariance gamma_h
(observed_cov_complex).  The estimators ghat_k = (1/(N-k)) sum_n
z_{n+k} conj(z_n), k = 0, 1, 2, then have exact asymptotic covariances
from Isserlis' theorem (only z-with-conj(z) pairings survive for a
proper series):

    N Cov(ghat_k, conj(ghat_l)) -> sum_h gamma_h gamma_{k-l-h},
    N Cov(ghat_k, ghat_l)       -> sum_h gamma_{k-h} gamma_{l+h},

both sums geometric (|gamma_h| ~ |phi|^|h| for |h| >= 1), evaluated
numerically at the population design.  The true branch's phase
residual R(ghat_1, ghat_2) and implied ell2(ghat_0, ghat_1, ghat_2)
are smooth functions of the five real estimator coordinates, so the
delta method (numeric gradient at the population point) gives
Var(R) = v_R / N and Var(ell2) = v_e / N.  The calibrated tolerance
is tau(N) = z_{0.975} sqrt(v_R / N): since the reported set keeps
every branch within tau of the best residual, and the best residual
is at most |R_true|, the event |R_true| <= tau is sufficient for the
true branch to be retained, so asymptotic coverage is at least 95%
inside the model.  The ell2 eligibility slack is calibrated the same
way, s_e(N) = z_{0.975} sqrt(v_e / N), replacing s12's guessed 0.02.

Two exposures: independent films give independent residuals, each
asymptotically N(0, v_j / N_j) at the true branch, so the derived
combination is the standardized quadratic form
Q_m = sum_j R_{j,m}^2 / (v_j / N_j), which is chi^2_2 at the true
branch.  The set {m : Q_m <= 5.991} (the 95% point of chi^2_2)
retains the true branch with asymptotic probability 95% -- a derived
rule, replacing s13's guessed max-residual ranking, and an empty set
is then a model rejection rather than an accident of two tolerances.

Everything is checked, not trusted: the delta-method standard
deviations are compared with Monte Carlo over fresh seeds, and
empirical coverage/set sizes are measured on the original s8 seeds.
Claims stay inside the frozen design and the stated model: the
calibration is asymptotic (first order in 1/sqrt(N)), the simulator's
trapezoid frame averages are an approximation of the exact shutter
integral shared by all of milestone 3, and no coverage is claimed
for data outside the model class.
"""
from __future__ import annotations

import cmath
import math
import statistics
import sys

from blurred_tracks import (FROZEN, Camera, blur_factor_F, blur_factor_Z,
                            branches_from_covariances, observed_cov_complex,
                            wrap_angle)
from branch_sets import branch_set
from finite_record import FRAME_COUNTS, REPLICATES, SEED0
from verify_blurred import empirical_gamma, simulate_frames

TRUE_M = 1
Z975 = 1.959963984540054
CHI2_2_95 = 5.991464547107979
MC_SEED0 = 999000          # fresh seeds for the delta-method check
MC_REPLICATES = 48
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def moment_covariances(v, cam, ks=(0, 1, 2), half_width=300):
    """Asymptotic N*Cov of (ghat_k): C[k,l] with conj(ghat_l), P[k,l] plain."""
    def gam(h):
        return observed_cov_complex(v, cam, h)
    C, P = {}, {}
    for k in ks:
        for l in ks:
            C[k, l] = sum(gam(h) * gam(k - l - h)
                          for h in range(-half_width, half_width + 1))
            P[k, l] = sum(gam(k - h) * gam(l + h)
                          for h in range(-half_width, half_width + 1))
    return C, P


def real_covariance(C, P):
    """5x5 asymptotic N*Cov for x = (g0, Re g1, Im g1, Re g2, Im g2)."""
    idx = {0: [0], 1: [1, 2], 2: [3, 4]}
    S = [[0.0] * 5 for _ in range(5)]
    for k, rows in idx.items():
        for l, cols in idx.items():
            c, p = C[k, l], P[k, l]
            block = [[0.5 * (c.real + p.real), 0.5 * (p.imag - c.imag)],
                     [0.5 * (p.imag + c.imag), 0.5 * (c.real - p.real)]]
            for i, ri in enumerate(rows):
                for j, cj in enumerate(cols):
                    S[ri][cj] = block[i][j]
    return S


def branch_quantities(x, cam, m):
    """(phase residual, ell2) of branch m as functions of estimator coords x."""
    g0, g1, g2 = x[0], complex(x[1], x[2]), complex(x[3], x[4])
    phi = g2 / g1
    kappa = -math.log(abs(phi)) / cam.Delta
    theta = cmath.phase(phi)
    omega = (theta + 2.0 * math.pi * m) / cam.Delta
    lam = complex(kappa, -omega)
    F = blur_factor_F(lam, cam.eps)
    R = wrap_angle(cmath.phase(F) - cmath.phase(g1 / phi))
    s = abs(g1) / (2.0 * abs(F) * abs(phi))
    ell2 = g0 / 2.0 - s * blur_factor_Z(lam, cam.eps)
    return R, ell2


def _gradient(f, x):
    g = []
    for i in range(len(x)):
        h = 1e-6 * max(1.0, abs(x[i]))
        xp, xm = list(x), list(x)
        xp[i] += h
        xm[i] -= h
        g.append((f(xp) - f(xm)) / (2.0 * h))
    return g


def delta_variances(v, cam, m=TRUE_M):
    """Return (v_R, v_e): Var(R) ~ v_R/N, Var(ell2) ~ v_e/N at branch m."""
    C, P = moment_covariances(v, cam)
    S = real_covariance(C, P)
    g1, g2 = (observed_cov_complex(v, cam, k) for k in (1, 2))
    x0 = [observed_cov_complex(v, cam, 0).real, g1.real, g1.imag,
          g2.real, g2.imag]

    def quad(g):
        return sum(g[i] * S[i][j] * g[j] for i in range(5) for j in range(5))

    vR = quad(_gradient(lambda x: branch_quantities(x, cam, m)[0], x0))
    ve = quad(_gradient(lambda x: branch_quantities(x, cam, m)[1], x0))
    return vR, ve


def tau_of(vR, n):
    return Z975 * math.sqrt(vR / n)


def slack_of(ve, n):
    return Z975 * math.sqrt(ve / n)


def estimate_branches(frames, cam, m_range):
    g0 = empirical_gamma(frames, 0).real
    g1 = empirical_gamma(frames, 1)
    g2 = empirical_gamma(frames, 2)
    try:
        _, _, bs = branches_from_covariances(g0, g1, g2, cam.Delta, cam.eps,
                                             m_range)
        return bs
    except ValueError:
        return []


def main() -> int:
    v, cam = FROZEN["vortex"], FROZEN["camera"]
    sigma_true = v.dissipation()
    vR, ve = delta_variances(v, cam)
    print(f"Frozen s8 design (eps/Delta=1/2): delta method gives "
          f"sd(R)*sqrt(N) = {math.sqrt(vR):.4f} rad, "
          f"sd(ell2)*sqrt(N) = {math.sqrt(ve):.4f}")
    for n in FRAME_COUNTS:
        print(f"  N={n:>5}: tau_95 = {tau_of(vR, n):.4f} rad, "
              f"ell2 slack_95 = {slack_of(ve, n):.4f} "
              f"(s12 guessed slack 0.02 at every N)")

    # Monte Carlo check of the delta method on fresh seeds (N=1000).
    Rs, es = [], []
    for r in range(MC_REPLICATES):
        frames = simulate_frames(v, cam, n_frames=1000,
                                 seed=MC_SEED0 + r, sub=20)
        x = [empirical_gamma(frames, 0).real,
             empirical_gamma(frames, 1).real, empirical_gamma(frames, 1).imag,
             empirical_gamma(frames, 2).real, empirical_gamma(frames, 2).imag]
        R, e = branch_quantities(x, cam, TRUE_M)
        Rs.append(R)
        es.append(e)
    sdR_mc, sde_mc = statistics.stdev(Rs), statistics.stdev(es)
    sdR_d, sde_d = math.sqrt(vR / 1000), math.sqrt(ve / 1000)
    check("delta-method sd(R) matches Monte Carlo",
          0.8 <= sdR_mc / sdR_d <= 1.25,
          f"(MC {sdR_mc:.4f} vs delta {sdR_d:.4f}, {MC_REPLICATES} fresh "
          f"seeds at N=1000; MC mean R {statistics.mean(Rs):+.4f})")
    check("delta-method sd(ell2) matches Monte Carlo",
          0.8 <= sde_mc / sde_d <= 1.25,
          f"(MC {sde_mc:.4f} vs delta {sde_d:.4f}; MC mean ell2 "
          f"{statistics.mean(es):.4f} vs population 0.04 -- the trapezoid "
          f"simulator biases ell2 low, shared by all of milestone 3)")

    # Headline: calibrated sets on the original s8 seeds.
    print(f"\nCalibrated branch sets on s8 seeds (R={REPLICATES}, "
          f"seed base {SEED0}, branches [-5, 5]):")
    for n in FRAME_COUNTS:
        tau, slack = tau_of(vR, n), slack_of(ve, n)
        cover_p, cover_e, sizes, spreads = 0, 0, [], []
        for r in range(REPLICATES):
            frames = simulate_frames(v, cam, n_frames=n,
                                     seed=SEED0 + 1000 * n + r, sub=20)
            bs = estimate_branches(frames, cam, range(-5, 6))
            s_phase = branch_set(bs, tau, None)
            s_elig = branch_set(bs, tau, slack)
            if any(b.m == TRUE_M for b in s_phase):
                cover_p += 1
            if any(b.m == TRUE_M for b in s_elig):
                cover_e += 1
            sizes.append(len(s_elig))
            if len(s_elig) >= 2:
                sig = [b.sigma for b in s_elig]
                spreads.append((max(sig) - min(sig)) / sigma_true)
            elif s_elig:
                spreads.append(0.0)
        med_spread = statistics.median(spreads) if spreads else float("nan")
        print(f"  N={n:>5} tau={tau:.4f} slack={slack:.4f}: "
              f"coverage phase-only {cover_p}/{REPLICATES}, "
              f"with calibrated ell2 slack {cover_e}/{REPLICATES}; "
              f"median set size {statistics.median(sizes):.0f} "
              f"(max {max(sizes)}), median rel. sigma spread "
              f"{med_spread:.3f}")

    # Two exposures: derived chi^2 combination vs s13's joint-max rule.
    cams = [Camera(Delta=1.0, eps=1.0 / 3.0, ell2=cam.ell2), cam]
    variances = [delta_variances(v, c) for c in cams]
    print("\nTwo exposures (eps/Delta in {1/3, 1/2}, branches [-15, 15], "
          f"R={REPLICATES} independent pairs):")
    for (j, c), (vr_j, ve_j) in zip(enumerate(cams), variances):
        print(f"  exposure {j + 1} eps/Delta={c.eps:.3f}: "
              f"sd(R)*sqrt(N) = {math.sqrt(vr_j):.4f} rad")
    for n in FRAME_COUNTS:
        cov_q, cov_qr, cov_jm, empty_q, empty_jm, sizes_q = 0, 0, 0, 0, 0, []
        taus = [tau_of(vr_j, n) for vr_j, _ in variances]
        slacks = [slack_of(ve_j, n) for _, ve_j in variances]
        for r in range(REPLICATES):
            per_cam = []
            for j, c in enumerate(cams):
                # exact s13 seed scheme (two_exposures.py)
                frames = simulate_frames(
                    v, c, n_frames=n,
                    seed=SEED0 + 1000 * n + 977 * j + r, sub=20)
                per_cam.append(estimate_branches(frames, c, range(-15, 16)))
            R = [{b.m: b.phase_residual for b in bs} for bs in per_cam]
            # derived: standardized quadratic form, absolute chi^2_2 cutoff,
            # calibrated per-exposure ell2 slacks
            elig = [set(b.m for b in bs if b.ell2 >= -slacks[j])
                    for j, bs in enumerate(per_cam)]
            common = elig[0] & elig[1] if all(per_cam) else set()
            Q = {m: sum((R[j][m] / (math.sqrt(variances[j][0] / n))) ** 2
                        for j in (0, 1)) for m in common}
            set_q = [m for m in common if Q[m] <= CHI2_2_95]
            # relative variant: same statistic, cutoff relative to the
            # best branch -- robust to a bias common to all branches
            set_qr = [m for m in common
                      if Q[m] <= min(Q.values()) + CHI2_2_95] if Q else []
            # s13 guessed rule, reproduced with its original slack 0.02:
            # rank by max |residual|, keep within tau=0.03 of the best
            elig13 = [set(b.m for b in bs if b.ell2 >= -0.02)
                      for bs in per_cam]
            common13 = elig13[0] & elig13[1] if all(per_cam) else set()
            if common13:
                score = {m: max(abs(R[0][m]), abs(R[1][m])) for m in common13}
                best = min(score.values())
                set_jm = [m for m in common13 if score[m] <= best + 0.03]
            else:
                set_jm = []
            cov_q += TRUE_M in set_q
            cov_qr += TRUE_M in set_qr
            cov_jm += TRUE_M in set_jm
            empty_q += not set_q
            empty_jm += not set_jm
            sizes_q.append(len(set_q))
        print(f"  N={n:>5} per exposure: derived chi2 absolute coverage "
              f"{cov_q}/{REPLICATES} (empty {empty_q}, median size "
              f"{statistics.median(sizes_q):.0f}); chi2 relative-to-best "
              f"coverage {cov_qr}/{REPLICATES}; joint-max tau=0.03 "
              f"coverage {cov_jm}/{REPLICATES} (empty {empty_jm}); "
              f"per-exposure taus {taus[0]:.3f}/{taus[1]:.3f} rad")

    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\nFAILED: none -- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
