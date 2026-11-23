#!/usr/bin/env python3
"""Milestone 3b: two exposure times break the near-alias (DERIVATION s13).

Section 10 found the alias margin is ratio-dependent: at eps/Delta = 1/3
a far branch nearly re-aliases (phase residual 0.0023 rad), while at
1/2 the margin is 0.274 rad -- and the near-alias sits at a *different*
branch for each ratio.  So filming the same motion at two exposures and
intersecting the branch sets should restore a large combined margin:
for each rival m, max(|residual at 1/3|, |residual at 1/2|) is large
even when one term is tiny.

Population part: frozen vortex (kappa=1, omega=3.9, D=1), Delta=1,
ell2=0.04, branches m in [-15, 15] at eps in {1/3, 1/2}; tolerance sets
(s12: ell2 slack 0.02) and their intersection; combined margin.

Finite part: N in {1000, 4000, 16000}, 24 seeded replicates per
exposure (independent tracks, same estimator as s8), tau in {0.03, 0.1}
rad; coverage, set sizes and empty-intersection counts per exposure
alone vs intersected.  Descriptive, one design, uncalibrated tau.
"""
from __future__ import annotations

import statistics

from blurred_tracks import (Camera, Vortex, branches_from_covariances,
                            observed_cov_complex)
from branch_sets import branch_set
from finite_record import FRAME_COUNTS, REPLICATES, SEED0
from verify_blurred import empirical_gamma, simulate_frames

V = Vortex(kappa=1.0, omega=3.9, D=1.0)
DELTA, ELL2, TRUE_M = 1.0, 0.04, 1
RATIOS = (1.0 / 3.0, 0.5)
M_VALUES = range(-15, 16)
SLACK = 0.02


def pop_branches(eps):
    cam = Camera(Delta=DELTA, eps=eps, ell2=ELL2)
    g = [observed_cov_complex(V, cam, k) for k in (0, 1, 2)]
    _, _, bs = branches_from_covariances(g[0].real, g[1], g[2], DELTA, eps,
                                         M_VALUES)
    return bs


def population() -> None:
    per = {}
    for ratio in RATIOS:
        bs = pop_branches(ratio * DELTA)
        per[ratio] = {b.m: b for b in bs}
        rival = min((b for b in bs if b.m != TRUE_M),
                    key=lambda b: abs(b.phase_residual))
        s = branch_set(bs, 0.01, SLACK)
        print(f"eps/Delta={ratio:.3f}: nearest rival m={rival.m} "
              f"|residual|={abs(rival.phase_residual):.4f} rad; "
              f"tau=0.01 set = {[b.m for b in s]}")
    sets = [{b.m for b in branch_set(list(per[r].values()), 0.01, SLACK)}
            for r in RATIOS]
    print(f"intersection of tau=0.01 sets: {sorted(sets[0] & sets[1])}")
    combined = min(max(abs(per[RATIOS[0]][m].phase_residual),
                       abs(per[RATIOS[1]][m].phase_residual))
                   for m in M_VALUES if m != TRUE_M)
    print(f"combined margin (min over rivals of max residual): "
          f"{combined:.4f} rad")


def finite() -> None:
    for n in FRAME_COUNTS:
        per_ratio = []
        for ri, ratio in enumerate(RATIOS):
            cam = Camera(Delta=DELTA, eps=ratio * DELTA, ell2=ELL2)
            rows = []
            for r in range(REPLICATES):
                frames = simulate_frames(V, cam, n_frames=n,
                                         seed=SEED0 + 1000 * n + 977 * ri + r,
                                         sub=20)
                try:
                    _, _, bs = branches_from_covariances(
                        empirical_gamma(frames, 0).real,
                        empirical_gamma(frames, 1),
                        empirical_gamma(frames, 2), DELTA, cam.eps, M_VALUES)
                except ValueError:
                    bs = []
                rows.append(bs)
            per_ratio.append(rows)
        print(f"N={n}:")
        for tau in (0.03, 0.1):
            stats = []
            for ri in range(2):
                sets = [branch_set(bs, tau, SLACK) for bs in per_ratio[ri]]
                stats.append(sets)
            inter = [{b.m for b in a} & {b.m for b in b}
                     for a, b in zip(*stats)]
            joint = []
            for bs_a, bs_b in zip(*per_ratio):
                da = {b.m: b for b in bs_a if b.ell2 >= -SLACK}
                db = {b.m: b for b in bs_b if b.ell2 >= -SLACK}
                common = set(da) & set(db)
                if not common:
                    joint.append(set())
                    continue
                score = {m: max(abs(da[m].phase_residual),
                                abs(db[m].phase_residual)) for m in common}
                best = min(score.values())
                joint.append({m for m in common if score[m] <= best + tau})
            def summ(sets_ms):
                cov = sum(TRUE_M in s for s in sets_ms)
                sizes = [len(s) for s in sets_ms]
                return (f"coverage {cov}/{REPLICATES}, median size "
                        f"{statistics.median(sizes):.0f} (max {max(sizes)})")
            print(f"  tau={tau}: eps/Delta=1/3 [{summ([{b.m for b in s} for s in stats[0]])}]; "
                  f"1/2 [{summ([{b.m for b in s} for s in stats[1]])}]; "
                  f"intersection [{summ(inter)}], empty "
                  f"{sum(1 for s in inter if not s)}/{REPLICATES}; "
                  f"joint-max [{summ(joint)}], empty "
                  f"{sum(1 for s in joint if not s)}/{REPLICATES}")


def main() -> None:
    print("Population level:")
    population()
    print("Finite records:")
    finite()


if __name__ == "__main__":
    main()
