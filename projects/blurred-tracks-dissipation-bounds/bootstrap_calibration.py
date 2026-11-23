#!/usr/bin/env python3
"""Milestone 3f: parametric-bootstrap tolerances from a single film.

Section 16 derived tau(N) and the ell2 slack from sampling theory,
but evaluated the variances at the population parameters -- which a
real user does not know.  This slice removes that assumption with a
parametric bootstrap from the film itself:

  1. run the branch enumeration on the film; take the winning branch
     m* (smallest |phase residual|) and its implied parameters
     (kappa, omega*, s*, ell2*);
  2. simulate B bootstrap films of the same length from that fitted
     motion, re-estimate, and record the bootstrap true branch's
     (m*'s) phase residuals R* and implied ell2*;
  3. tau_boot = 1.96 * sd(R*), and the eligibility slack is
     ell2*_fit - (5th percentile of the bootstrap ell2 estimates),
     a one-sided 95% allowance for downward ell2 fluctuation;
  4. report, on the original film, the set of branches within
     tau_boot of the best residual (with the bootstrap slack).

Measured on the s8 seeds against s16's population calibration:
coverage, set sizes, and how tau_boot compares with tau_population.
Known weakness, measured not hidden: when the plug-in winner m* is
the wrong branch (it happens at N=1000), the bootstrap world is
centred on the wrong motion and its sets are calibrated for a film
that was not taken; those replicates are counted separately.  All
claims stay inside the frozen design and model; the bootstrap
inherits the trapezoid simulator shared by milestone 3.
"""
from __future__ import annotations

import math
import statistics
import sys

from blurred_tracks import FROZEN, Camera, Vortex, branches_from_covariances
from branch_sets import branch_set
from finite_record import FRAME_COUNTS, REPLICATES, SEED0
from tolerance_calibration import delta_variances, estimate_branches, tau_of
from verify_blurred import empirical_gamma, simulate_frames

TRUE_M = 1
B_BOOT = 24
BOOT_SEED0 = 555000
Z975 = 1.959963984540054
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def fit_winner(frames, cam, m_range=range(-5, 6)):
    """Winning branch and fitted (Vortex, Camera) for one film, or None."""
    g0 = empirical_gamma(frames, 0).real
    g1 = empirical_gamma(frames, 1)
    g2 = empirical_gamma(frames, 2)
    try:
        kappa, _phi, bs = branches_from_covariances(
            g0, g1, g2, cam.Delta, cam.eps, m_range)
    except ValueError:
        return None
    win = min(bs, key=lambda b: abs(b.phase_residual))
    v_fit = Vortex(kappa=kappa, omega=win.omega, D=win.s * kappa)
    cam_fit = Camera(Delta=cam.Delta, eps=cam.eps, ell2=max(win.ell2, 0.0))
    return win, bs, v_fit, cam_fit


def bootstrap_tolerances(v_fit, cam_fit, n_frames, m_star, seed0,
                         b_boot=B_BOOT):
    """(tau_boot, slack_boot) from B bootstrap films of the fitted motion."""
    Rs, ells = [], []
    for b in range(b_boot):
        frames = simulate_frames(v_fit, cam_fit, n_frames=n_frames,
                                 seed=seed0 + b, sub=20)
        bs = estimate_branches(frames, cam_fit, range(-5, 6))
        for br in bs:
            if br.m == m_star:
                Rs.append(br.phase_residual)
                ells.append(br.ell2)
    if len(Rs) < 8:
        return None
    tau_boot = Z975 * statistics.stdev(Rs)
    ells_sorted = sorted(ells)
    q05 = ells_sorted[max(0, int(0.05 * len(ells_sorted)) - 1)]
    slack_boot = max(cam_fit.ell2 - q05, 0.0)
    return tau_boot, slack_boot


def main() -> int:
    v, cam = FROZEN["vortex"], FROZEN["camera"]
    sigma_true = v.dissipation()
    vR, _ve = delta_variances(v, cam)
    print(f"Parametric bootstrap (B={B_BOOT}) on s8 seeds "
          f"(R={REPLICATES}, seed base {SEED0}); bootstrap seed base "
          f"{BOOT_SEED0}; branches [-5, 5]")
    for n in FRAME_COUNTS:
        tau_pop = tau_of(vR, n)
        cover, sizes, spreads, tau_ratios = 0, [], [], []
        wrong_winner = 0
        usable = 0
        for r in range(REPLICATES):
            frames = simulate_frames(v, cam, n_frames=n,
                                     seed=SEED0 + 1000 * n + r, sub=20)
            fit = fit_winner(frames, cam)
            if fit is None:
                sizes.append(0)
                continue
            win, bs, v_fit, cam_fit = fit
            if win.m != TRUE_M:
                wrong_winner += 1
            tol = bootstrap_tolerances(
                v_fit, cam_fit, n, win.m,
                seed0=BOOT_SEED0 + 1000 * n + 100 * r)
            if tol is None:
                sizes.append(0)
                continue
            usable += 1
            tau_boot, slack_boot = tol
            tau_ratios.append(tau_boot / tau_pop)
            s = branch_set(bs, tau_boot, slack_boot)
            sizes.append(len(s))
            if any(b.m == TRUE_M for b in s):
                cover += 1
            if len(s) >= 2:
                sig = [b.sigma for b in s]
                spreads.append((max(sig) - min(sig)) / sigma_true)
            elif s:
                spreads.append(0.0)
        med_spread = statistics.median(spreads) if spreads else float("nan")
        med_ratio = statistics.median(tau_ratios) if tau_ratios else float("nan")
        print(f"  N={n:>5}: bootstrap coverage {cover}/{REPLICATES} "
              f"({usable} usable, plug-in winner wrong in {wrong_winner}); "
              f"median set size {statistics.median(sizes):.0f} "
              f"(max {max(sizes)}), median rel. sigma spread "
              f"{med_spread:.3f}; median tau_boot/tau_population "
              f"{med_ratio:.2f} (tau_population {tau_pop:.4f} rad, "
              f"s16 coverage 24/24)")
        check(f"N={n}: bootstrap tau tracks population tau",
              0.6 <= med_ratio <= 1.6, f"(median ratio {med_ratio:.2f})")

    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\nFAILED: none -- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
