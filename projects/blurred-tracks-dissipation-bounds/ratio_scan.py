#!/usr/bin/env python3
"""How the branch margin depends on the exposure ratio eps/Delta.

Same latent vortex as milestone 1 at several rational ratios.  Candidate
branches over ALL integers come from blurred_tracks.all_branch_candidates
(complete per residue class); compatibility then also needs ell^2 >= 0.
Reports the compatible set and the smallest |phase residual| among rival
candidates -- the margin a finite record must beat.  Note the margin is
not monotone in eps: some ratios nearly re-alias at a far branch.
"""
from fractions import Fraction

from blurred_tracks import (Camera, Vortex, all_branch_candidates,
                            branches_from_covariances, observed_cov_complex)


def main() -> None:
    v = Vortex(kappa=1.0, omega=3.9, D=1.0)
    print(f"{'eps/Delta':>10} {'compatible (all m)':>20} "
          f"{'nearest rival |residual|':>26}")
    for ratio in (Fraction(1, 4), Fraction(1, 3), Fraction(2, 5),
                  Fraction(1, 2), Fraction(3, 4), Fraction(1, 1)):
        eps = float(ratio)
        cam = Camera(Delta=1.0, eps=eps, ell2=0.04)
        g = [observed_cov_complex(v, cam, k) for k in range(3)]
        cands = all_branch_candidates(g[1], g[2], 1.0, eps, ratio)
        _, _, bs = branches_from_covariances(g[0].real, g[1], g[2],
                                             1.0, eps, cands)
        ok = [b.m for b in bs if b.compatible()]
        rival = min((abs(b.phase_residual) for b in bs if b.m != 1),
                    default=float("nan"))
        print(f"{str(ratio):>10} {str(ok):>20} {rival:>26.4f}")


if __name__ == "__main__":
    main()
