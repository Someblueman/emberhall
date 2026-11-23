#!/usr/bin/env python3
"""Milestone 3c: unknown trap centre (DERIVATION s14).

Sections 8/12/13 estimated gamma_k by raw second moments, using the
model's known zero mean -- an experimenter does not know the trap
centre.  This script measures both directions on the s8 design
(24 seeded replicates, N in {1000, 4000, 16000}, branches m in [-5,5],
winner = smallest |phase residual| among ell2-slack-eligible branches):

(a) cost of demeaning when the centre really is zero: demeaning by the
    sample mean of *correlated* frames biases gamma_k downward (the
    sample mean is itself a blurred average of the track), shrinking
    |gamma_1|, |gamma_2| and distorting phi = gamma_2/gamma_1 mildly;
(b) cost of NOT demeaning when the centre is mu0 = 0.7 + 0.4i
    (stationary per-coordinate sd is sqrt(s)=1): raw moments then
    estimate gamma_k + |mu0|^2 at every lag, which corrupts phi
    completely, while demeaning behaves as in (a).

Reported: winner-is-true counts, median relative sigma error of the
winner, median kappa error.  Descriptive, one design, same caveats
as s8/s12/s13.
"""
from __future__ import annotations

import statistics

from blurred_tracks import FROZEN, branches_from_covariances
from finite_record import FRAME_COUNTS, REPLICATES, SEED0
from verify_blurred import empirical_gamma, simulate_frames

MU0 = 0.7 + 0.4j
SLACK = 0.02
TRUE_M = 1


def demean(frames):
    mu = sum(frames) / len(frames)
    return [f - mu for f in frames]


def winner_stats(frames, cam, sigma_true):
    try:
        kappa, _, bs = branches_from_covariances(
            empirical_gamma(frames, 0).real, empirical_gamma(frames, 1),
            empirical_gamma(frames, 2), cam.Delta, cam.eps, range(-5, 6))
    except ValueError:
        return None
    elig = [b for b in bs if b.ell2 >= -SLACK] or bs
    w = min(elig, key=lambda b: abs(b.phase_residual))
    return w.m == TRUE_M, abs(w.sigma - sigma_true) / sigma_true, kappa - 1.0


def run(offset):
    v, cam = FROZEN["vortex"], FROZEN["camera"]
    st = v.dissipation()
    label = f"centre offset {offset}" if offset else "true centre 0"
    print(f"{label}:")
    for n in FRAME_COUNTS:
        agg = {"raw (assumes 0)": [], "demeaned": []}
        for r in range(REPLICATES):
            frames = simulate_frames(v, cam, n_frames=n,
                                     seed=SEED0 + 1000 * n + r, sub=20)
            if offset:
                frames = [f + offset for f in frames]
            for name, fr in (("raw (assumes 0)", frames),
                             ("demeaned", demean(frames))):
                s = winner_stats(fr, cam, st)
                if s is not None:
                    agg[name].append(s)
        for name, rows in agg.items():
            if not rows:
                print(f"  N={n:>5} {name:>16}: estimator refused all "
                      f"{REPLICATES} replicates (|phi| outside (0,1))")
                continue
            wins = sum(r[0] for r in rows)
            print(f"  N={n:>5} {name:>16}: true wins {wins:>2}/{len(rows)}, "
                  f"median rel. sigma err "
                  f"{statistics.median(r[1] for r in rows):.3f}, "
                  f"median kappa err "
                  f"{statistics.median(r[2] for r in rows):+.3f}")


def main() -> None:
    run(0j)
    run(MU0)


if __name__ == "__main__":
    main()
