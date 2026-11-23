#!/usr/bin/env python3
"""Milestone 3d: equal-frames light budget (DERIVATION s15).

Section 13 left the design question open: at equal total frames, do two
films at two exposures beat one long film at the better exposure?
Budget T = 2N frames spent three ways on the frozen vortex:
  (a) 2N frames at eps/Delta = 1/2,
  (b) 2N frames at eps/Delta = 1/3,
  (c) N at 1/3 + N at 1/2, combined by joint max-residual ranking (s13).
All estimators demeaned (s14), ell2 slack 0.02 (s12), branches
m in [-15, 15], winner = best (joint) phase score; 24 seeded
replicates, N in {500, 2000, 8000}.  Winner sigma for (c) is taken
from the 1/2 film's branch entry.  Descriptive, one design.
"""
from __future__ import annotations

import statistics

from blurred_tracks import Camera, branches_from_covariances
from finite_record import REPLICATES, SEED0
from two_exposures import DELTA, ELL2, M_VALUES, SLACK, TRUE_M, V
from unknown_mean import demean
from verify_blurred import empirical_gamma, simulate_frames

HALVES = (500, 2000, 8000)


def branches(ratio, n, seed):
    cam = Camera(Delta=DELTA, eps=ratio * DELTA, ell2=ELL2)
    frames = demean(simulate_frames(V, cam, n_frames=n, seed=seed, sub=20))
    try:
        _, _, bs = branches_from_covariances(
            empirical_gamma(frames, 0).real, empirical_gamma(frames, 1),
            empirical_gamma(frames, 2), DELTA, cam.eps, M_VALUES)
    except ValueError:
        return []
    return [b for b in bs if b.ell2 >= -SLACK] or bs


def winner_single(bs):
    return min(bs, key=lambda b: abs(b.phase_residual)) if bs else None


def winner_joint(bs_a, bs_b):
    da, db = {b.m: b for b in bs_a}, {b.m: b for b in bs_b}
    common = set(da) & set(db)
    if not common:
        return None
    m = min(common, key=lambda m: max(abs(da[m].phase_residual),
                                      abs(db[m].phase_residual)))
    return db[m]  # sigma from the 1/2 film


def main() -> None:
    st = V.dissipation()
    print(f"Equal total frames T=2N; R={REPLICATES}; true m={TRUE_M}, "
          f"sigma={st:.2f}")
    for n in HALVES:
        rows = {"2N @ 1/2": [], "2N @ 1/3": [], "N @ 1/3 + N @ 1/2": []}
        for r in range(REPLICATES):
            seed = SEED0 + 31337 * n + r
            w = winner_single(branches(0.5, 2 * n, seed))
            rows["2N @ 1/2"].append(w)
            w = winner_single(branches(1 / 3, 2 * n, seed + 500000))
            rows["2N @ 1/3"].append(w)
            w = winner_joint(branches(1 / 3, n, seed + 900000),
                             branches(0.5, n, seed + 700000))
            rows["N @ 1/3 + N @ 1/2"].append(w)
        print(f"T={2 * n}:")
        for name, ws in rows.items():
            ok = [w for w in ws if w is not None]
            wins = sum(w.m == TRUE_M for w in ok)
            err = (statistics.median(abs(w.sigma - st) / st for w in ok)
                   if ok else float("nan"))
            print(f"  {name:>18}: true wins {wins:>2}/{REPLICATES} "
                  f"({len(ok)} usable), median rel. sigma err {err:.3f}")


if __name__ == "__main__":
    main()
