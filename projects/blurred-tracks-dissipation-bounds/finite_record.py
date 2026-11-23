#!/usr/bin/env python3
"""Milestone-3 pilot: does the milestone-1 branch separation survive noise?

Frozen design: milestone-1 example (kappa=1, omega=3.9, D=1, Delta=1,
eps=0.5, ell^2=0.04; true branch m=1, sigma=30.42, population phase margin
to nearest rival 0.274 rad).  For each frame count N, simulate R tracks
(exact-transition substeps, 20 per exposure; trapezoid frame averages),
estimate gamma_0..gamma_2 by raw second moments (model mean is known 0),
and run the branch enumeration of blurred_tracks on the estimates.

Reported per N: fraction of replicates where branch m=1 has the strictly
smallest |phase residual| among m in [-5, 5] (the plug-in winner), median
gap between the best rival residual and the true-branch residual, and
median |sigma_hat - sigma| / sigma for the winner.  This measures the
simulated design only; it is not a coverage guarantee.
"""
from __future__ import annotations

import statistics

from blurred_tracks import FROZEN, branches_from_covariances
from verify_blurred import empirical_gamma, simulate_frames

REPLICATES = 24
FRAME_COUNTS = (1000, 4000, 16000)
SEED0 = 424242


def main() -> None:
    v, cam = FROZEN["vortex"], FROZEN["camera"]
    print(f"Frozen: R={REPLICATES} tracks x N in {FRAME_COUNTS}, "
          f"seed base {SEED0}, substeps=20/exposure")
    print(f"{'N':>7} {'true wins':>10} {'median gap (rad)':>17} "
          f"{'median rel. sigma err':>22}")
    for n in FRAME_COUNTS:
        wins, gaps, rel_errs = 0, [], []
        for r in range(REPLICATES):
            frames = simulate_frames(v, cam, n_frames=n,
                                     seed=SEED0 + 1000 * n + r, sub=20)
            g0 = empirical_gamma(frames, 0).real
            g1 = empirical_gamma(frames, 1)
            g2 = empirical_gamma(frames, 2)
            try:
                _, _, bs = branches_from_covariances(
                    g0, g1, g2, cam.Delta, cam.eps, range(-5, 6))
            except ValueError:
                gaps.append(0.0)
                rel_errs.append(1.0)
                continue
            ranked = sorted(bs, key=lambda b: abs(b.phase_residual))
            winner = ranked[0]
            true_res = next(abs(b.phase_residual) for b in bs if b.m == 1)
            rival_res = min(abs(b.phase_residual) for b in bs if b.m != 1)
            gaps.append(rival_res - true_res)
            if winner.m == 1:
                wins += 1
            rel_errs.append(abs(winner.sigma - v.dissipation())
                            / v.dissipation())
        print(f"{n:>7} {wins:>4}/{REPLICATES:<5} "
              f"{statistics.median(gaps):>17.3f} "
              f"{statistics.median(rel_errs):>22.3f}")


if __name__ == "__main__":
    main()
