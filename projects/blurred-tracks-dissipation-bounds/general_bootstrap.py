#!/usr/bin/env python3
"""Milestone 3i: parametric-bootstrap tolerances, general case.

Section 18 derived the symmetry-residual tolerance tau(N) for the
general (non-isotropic) test from Isserlis + delta method, but
evaluated the variance at the population parameters -- which a real
user does not know.  This slice is the general analogue of s17: it
removes that assumption with a parametric bootstrap from the film
itself, on the same frozen general example (true branch m = 0):

  1. from one film's Ghat_0..2, take the winning branch m*
     (smallest |R|) and its fitted motion (A*, Sigma*, Dm*, ell*),
     with Sigma* the symmetrized implied covariance and
     ell* = max(mean implied ell2, 0);
  2. simulate B bootstrap films of the same length from that fitted
     motion and record the bootstrap branch-m* residuals R*;
  3. tau_boot = 1.96 * sd(R*); report, on the original film, the set
     of branches within tau_boot of the best |R|.

Measured on the s18 seeds against s18's population calibration:
coverage of m = 0, set sizes, wrong-winner counts, and how tau_boot
compares with tau_population.  Known weaknesses, measured not
hidden: a wrong plug-in winner centres the bootstrap world on the
wrong motion (counted separately); a fit whose Sigma* or Dm* is not
positive definite cannot be simulated and the replicate is counted
unusable.  All claims stay inside the frozen general design and
model; the bootstrap inherits the trapezoid simulator of s18.
"""
from __future__ import annotations

import math
import statistics
import sys

from finite_record import FRAME_COUNTS, REPLICATES, SEED0
from general_finite_record import (M_VALUES, TRUE_M, delta_variance_R,
                                   empirical_Gamma,
                                   simulate_general_frames,
                                   symmetry_residual)
from general_tracks import (FROZEN_GENERAL, GeneralVortex, add,
                            branch_drifts, int_exp, int_exp_weighted,
                            inverse2, matmul, scale, transpose)

B_BOOT = 24
BOOT_SEED0 = 777000
Z975 = 1.959963984540054
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def _is_spd(M) -> bool:
    return M[0][0] > 0 and M[0][0] * M[1][1] - M[0][1] * M[1][0] > 0


def fit_from_covariances(G0, G1, G2, Delta, eps, m_values=M_VALUES):
    """Winning branch and its fitted motion, or None if unavailable.

    Returns (m_star, residuals, fitted) where residuals maps m -> R(m)
    for every available branch and fitted is a GeneralVortex carrying
    (A*, Dm*, Sigma*) plus the fitted ell2 under key "ell2" of a dict
    {"vortex": gv, "ell2": ell*}.  None when no branch is available
    or the winner's Sigma*/Dm* is not positive definite (the fitted
    motion then cannot be simulated).
    """
    try:
        Phi = matmul(G2, inverse2(G1))
        drifts = dict(branch_drifts(Phi, Delta, list(m_values)))
    except ValueError:
        return None
    residuals, cand = {}, {}
    for m, Am in drifts.items():
        U = int_exp(Am, eps)
        W = int_exp(scale(Am, -1.0), eps)
        try:
            S = scale(matmul(inverse2(matmul(U, W)),
                             matmul(inverse2(Phi), G1)), eps ** 2)
        except ValueError:
            continue
        residuals[m] = S[0][1] - S[1][0]
        cand[m] = (Am, S)
    if not residuals:
        return None
    m_star = min(residuals, key=lambda m: abs(residuals[m]))
    Am, S = cand[m_star]
    Ss = [[S[0][0], 0.5 * (S[0][1] + S[1][0])],
          [0.5 * (S[0][1] + S[1][0]), S[1][1]]]
    Dm = scale(add(matmul(Am, Ss), matmul(Ss, transpose(Am))), -0.5)
    if not (_is_spd(Ss) and _is_spd(Dm)):
        return None
    U2S = matmul(int_exp_weighted(Am, eps), Ss)
    P0 = scale(add(U2S, transpose(U2S)), 1.0 / eps ** 2)
    ell = max(0.5 * ((G0[0][0] - P0[0][0]) + (G0[1][1] - P0[1][1])), 0.0)
    gv = GeneralVortex.__new__(GeneralVortex)
    gv.A, gv.Dm, gv.Sigma = Am, Dm, Ss
    return m_star, residuals, {"vortex": gv, "ell2": ell}


def bootstrap_tau(fitted, Delta, eps, n_frames, m_star, seed0,
                  b_boot=B_BOOT):
    """tau_boot = 1.96 * sd of bootstrap branch-m* residuals, or None."""
    Rs = []
    for b in range(b_boot):
        frames = simulate_general_frames(fitted["vortex"], Delta, eps,
                                         fitted["ell2"], n_frames,
                                         seed0 + b)
        Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
        R = symmetry_residual(Gh[0], Gh[1], Gh[2], Delta, eps, m_star)
        if R is not None:
            Rs.append(R)
    if len(Rs) < 8:
        return None
    return Z975 * statistics.stdev(Rs)


def main() -> int:
    fg = FROZEN_GENERAL
    Delta, eps, ell2 = fg["Delta"], fg["eps"], fg["ell2"]
    g = GeneralVortex(fg["A"], fg["Dm"])
    vR = delta_variance_R(g, Delta, eps, ell2)
    print(f"Parametric bootstrap, general case (B={B_BOOT}) on s18 "
          f"seeds (R={REPLICATES}, seed base {SEED0}); bootstrap seed "
          f"base {BOOT_SEED0}; branches [-5, 5]; true m={TRUE_M}")
    for n in FRAME_COUNTS:
        tau_pop = Z975 * math.sqrt(vR / n)
        cover, sizes, tau_ratios = 0, [], []
        wrong_winner, usable, unfittable = 0, 0, 0
        for r in range(REPLICATES):
            frames = simulate_general_frames(g, Delta, eps, ell2, n,
                                             SEED0 + 1000 * n + r)
            Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
            fit = fit_from_covariances(Gh[0], Gh[1], Gh[2], Delta, eps)
            if fit is None:
                unfittable += 1
                sizes.append(0)
                continue
            m_star, residuals, fitted = fit
            if m_star != TRUE_M:
                wrong_winner += 1
            tau_boot = bootstrap_tau(fitted, Delta, eps, n, m_star,
                                     BOOT_SEED0 + 1000 * n + 100 * r)
            if tau_boot is None:
                sizes.append(0)
                continue
            usable += 1
            tau_ratios.append(tau_boot / tau_pop)
            best = min(abs(R) for R in residuals.values())
            s = [m for m, R in residuals.items()
                 if abs(R) <= best + tau_boot]
            sizes.append(len(s))
            cover += TRUE_M in s
        med_ratio = (statistics.median(tau_ratios) if tau_ratios
                     else float("nan"))
        print(f"  N={n:>5}: bootstrap coverage {cover}/{REPLICATES} "
              f"({usable} usable, {unfittable} unfittable, plug-in "
              f"winner wrong in {wrong_winner}); median set size "
              f"{statistics.median(sizes):.0f} (max {max(sizes)}); "
              f"median tau_boot/tau_population {med_ratio:.2f} "
              f"(tau_population {tau_pop:.4f}, s18 coverage 24/24)")
        check(f"N={n}: bootstrap tau tracks population tau (general)",
              0.6 <= med_ratio <= 1.6, f"(median ratio {med_ratio:.2f})")

    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\nFAILED: none -- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
