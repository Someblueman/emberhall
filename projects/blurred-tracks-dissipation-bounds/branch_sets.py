#!/usr/bin/env python3
"""Milestone 3a: set-valued branch reports for finite records.

The s8 pilot showed the plug-in winner is occasionally a rival branch at
N=1000, so a finite-record procedure should report a *set*: every branch
whose |phase residual| is within tolerance tau of the best residual.
Two eligibility variants are compared: phase-only, and the population
test's ell2 >= 0 filter (with a small slack variant), because the first
run of this script showed the hard filter discarding the true branch
whenever its *estimated* ell2 dipped below zero (true ell2 = 0.04 is
small): at N=4000 the true branch had the best phase residual in 24/24
replicates yet coverage with the hard filter was only 20/24.  Same
frozen design, seeds
and estimators as finite_record.py.  For an absolute tau grid and for
tau = c/sqrt(N), report per N: coverage (true branch m=1 in the set),
median set size, and median relative dissipation spread
(max sigma - min sigma)/sigma_true over the set.

This is a descriptive measurement of one frozen design: the tolerances
are not calibrated from a sampling theory, and no coverage guarantee is
claimed.  Its question is narrower -- how much honesty (set size, sigma
spread) a given tau buys at each N in this design.
"""
from __future__ import annotations

import math
import statistics

from blurred_tracks import FROZEN, branches_from_covariances
from finite_record import FRAME_COUNTS, REPLICATES, SEED0
from verify_blurred import empirical_gamma, simulate_frames

TRUE_M = 1
TAU_ABS = (0.01, 0.03, 0.10)
TAU_C = (1.0, 3.0)


def branch_set(bs, tau, ell_slack=None):
    elig = bs if ell_slack is None else [b for b in bs if b.ell2 >= -ell_slack]
    if not elig:
        return []
    best = min(abs(b.phase_residual) for b in elig)
    return [b for b in elig if abs(b.phase_residual) <= best + tau]


def main() -> None:
    v, cam = FROZEN["vortex"], FROZEN["camera"]
    sigma_true = v.dissipation()
    print(f"Frozen s8 design: R={REPLICATES}, N in {FRAME_COUNTS}, "
          f"seed base {SEED0}; true branch m={TRUE_M}, sigma={sigma_true:.2f}")
    taus = [(f"tau={t}", lambda n, t=t: t) for t in TAU_ABS] + \
           [(f"tau={c}/sqrt(N)", lambda n, c=c: c / math.sqrt(n)) for c in TAU_C]
    for n in FRAME_COUNTS:
        all_bs = []
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
                bs = []
            all_bs.append(bs)
        neg = sum(1 for bs in all_bs
                  if any(b.m == TRUE_M and b.ell2 < 0 for b in bs))
        print(f"N={n}: (true-branch estimated ell2 < 0 in {neg}/{REPLICATES})")
        variants = [("phase-only", None), ("ell2>=0", 0.0),
                    ("ell2>=-0.02", 0.02)]
        for vlabel, slack in variants:
          for label, tau_of in taus:
            tau = tau_of(n)
            cover, sizes, spreads = 0, [], []
            for bs in all_bs:
                s = branch_set(bs, tau, slack)
                sizes.append(len(s))
                if any(b.m == TRUE_M for b in s):
                    cover += 1
                if len(s) >= 2:
                    sig = [b.sigma for b in s]
                    spreads.append((max(sig) - min(sig)) / sigma_true)
                elif s:
                    spreads.append(0.0)
            med_spread = statistics.median(spreads) if spreads else float("nan")
            print(f"  [{vlabel}] {label:>14} (tau={tau:.4f} rad): coverage "
                  f"{cover:>2}/{REPLICATES}, median set size "
                  f"{statistics.median(sizes):.0f} (max {max(sizes)}), "
                  f"median rel. sigma spread {med_spread:.3f}")


if __name__ == "__main__":
    main()
