#!/usr/bin/env python3
"""Milestone 3j: what kind of bias leans on the general residuals?

Sections 18-19 reported non-shrinking means -- symmetry residual
mean +0.036 at N=1000 (0.18 sd) and zero-lag off-diagonal mean
-0.011 -- and attributed them to the trapezoid frame average
(sub=20) shared by all of milestone 3, without sizing the effect.
Two candidate mechanisms scale differently, and this script
separates them on the frozen general example:

  * trapezoid quadrature bias: R is evaluated on Ghat whose mean
    differs from Gamma by the quadrature error; that error is
    O(1/sub^2) and independent of N, so mean R stays constant as
    N grows while sd(R) falls -- bias/sd grows like sqrt(N);
  * finite-N estimator bias: R is a nonlinear function of Ghat, so
    E[R(Ghat)] - R(Gamma) = O(1/N) at any fixed sub -- bias/sd
    falls like 1/sqrt(N).

Arm A sweeps sub in {10, 20, 40, 80} at N=2000 (R=24, descriptive,
with standard errors).  Arm B sweeps N at sub=20 (N=1000 R=96,
N=4000 R=48, N=16000 R=48): quadrature predicts mean R unchanged
from N=1000 to 16000, estimator bias predicts a factor 1/16.
What matters for s18/s20's calibrated sets is bias/sd at the N
where they are used.
"""
from __future__ import annotations

import math
import statistics
import sys

from general_finite_record import (branch_quantities_general,
                                   delta_variance_R, empirical_Gamma,
                                   simulate_general_frames)
from general_tracks import FROZEN_GENERAL, GeneralVortex

SEED0 = 246000
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def measure(g, Delta, eps, ell2, sub, n, reps, seed0):
    """(max mean |Ghat-Gamma| entry error, mean R, se of mean R)."""
    Gp = [g.observed_cov_matrix(Delta, eps, ell2, k) for k in (0, 1, 2)]
    errs = [[[0.0, 0.0], [0.0, 0.0]] for _ in range(3)]
    Rs = []
    for r in range(reps):
        frames = simulate_general_frames(g, Delta, eps, ell2, n,
                                         seed0 + r, sub=sub)
        Gh = [empirical_Gamma(frames, k) for k in (0, 1, 2)]
        for k in range(3):
            for i in range(2):
                for j in range(2):
                    errs[k][i][j] += (Gh[k][i][j] - Gp[k][i][j]) / reps
        q = branch_quantities_general(Gh[0], Gh[1], Gh[2], Delta, eps, 0)
        if q is not None:
            Rs.append(q["R"])
    max_err = max(abs(errs[k][i][j]) for k in range(3)
                  for i in range(2) for j in range(2))
    se = statistics.stdev(Rs) / math.sqrt(len(Rs))
    return max_err, statistics.mean(Rs), se


def main() -> int:
    fg = FROZEN_GENERAL
    Delta, eps, ell2 = fg["Delta"], fg["eps"], fg["ell2"]
    g = GeneralVortex(fg["A"], fg["Dm"])
    vR = delta_variance_R(g, Delta, eps, ell2)
    print(f"Bias anatomy, frozen general example (seed base {SEED0})")
    print("Arm A: sub sweep at N=2000, R=24")
    sdR = math.sqrt(vR / 2000)
    for sub in (10, 20, 40, 80):
        max_err, meanR, se = measure(g, Delta, eps, ell2, sub, 2000, 24,
                                      SEED0 + sub * 1000)
        print(f"  sub={sub:>3}: max mean Gamma entry error "
              f"{max_err:+.5f}, mean R {meanR:+.4f} +- {se:.4f} "
              f"({meanR / sdR:+.2f} sd)")
    print("Arm B: N sweep at sub=20")
    means = {}
    for n, reps in ((1000, 96), (4000, 48), (16000, 48)):
        max_err, meanR, se = measure(g, Delta, eps, ell2, 20, n, reps,
                                      SEED0 + n)
        means[n] = (meanR, se)
        print(f"  N={n:>5} R={reps}: max mean Gamma entry error "
              f"{max_err:+.5f}, mean R {meanR:+.4f} +- {se:.4f} "
              f"({meanR / math.sqrt(vR / n):+.2f} sd)")
    m16, se16 = means[16000]
    print(f"  N-independent bias of s18's apparent size (+0.036) "
          f"would sit {(0.036 - m16) / se16:.1f} standard errors "
          f"from the N=16000 mean")
    check("no N-independent bias of s18's apparent size at N=16000",
          abs(m16) + 2 * se16 < 0.036,
          f"(|mean| + 2se = {abs(m16) + 2 * se16:.4f} < 0.036)")
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\nFAILED: none -- all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
