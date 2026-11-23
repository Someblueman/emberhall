"""Importing program: shared monitor + shared background, weighted fit.

This is the real consumer the milestone asks for: it imports covreduce,
normalises fixed bins by one shared monitor, subtracts one shared
background, fits a weighted mean downstream, and compares the sparse
result against the independent dense oracle and the baselines.
"""
from __future__ import annotations

from . import moving_window, rebin, source
from .baselines import (
    essreduce_upper_bound, gvar_equivalent_variance,
    independent_variance_covariance, monte_carlo_covariance,
    rme_ellipse_attribution,
)
from .events import benchmark_100k_events
from .oracle import max_covariance_difference


def build_program():
    monitor = source(1000.0, 25.0)
    counts = source([120.0, 80.0, 45.0], [[12.0, 1.0, 0.0],
                                          [1.0, 9.0, 0.5],
                                          [0.0, 0.5, 6.0]], dims=("bin",),
                    coords={"bin": (0.5, 1.5, 2.5)})
    background = source([5.0, 5.0, 5.0], [[0.30, 0.25, 0.25],
                                          [0.25, 0.30, 0.25],
                                          [0.25, 0.25, 0.30]], dims=("bin",),
                        coords={"bin": (0.5, 1.5, 2.5)})
    rates = counts / monitor - background / monitor
    return monitor, counts, background, rates


def main(argv=None):
    monitor, counts, background, rates = build_program()

    def program(parts):
        mon, cnt, bkg = parts
        return cnt / mon - bkg / mon

    diff = max_covariance_difference(rates, [monitor, counts, background],
                                     program)
    weights = (0.5, 0.3, 0.2)
    fit_value = sum(w * v for w, v in zip(weights, rates.values))
    fit_var = rates.quadratic_form(weights)
    indep = independent_variance_covariance(rates)
    indep_fit = sum(weights[i] * indep[i][j] * weights[j]
                    for i in range(3) for j in range(3))

    def flat_program(flats):
        mon, cnt, bkg = flats[0][0], flats[1], flats[2]
        return tuple(c / mon - b / mon for c, b in zip(cnt, bkg))

    mc = monte_carlo_covariance([monitor, counts, background], flat_program,
                                draws=6000)
    mc_fit = sum(weights[i] * mc[i][j] * weights[j]
                 for i in range(3) for j in range(3))
    bound = essreduce_upper_bound(rates, weights)
    gvar_var = gvar_equivalent_variance(
        [(weights[i], rates[i]) for i in range(3)])
    smoothed = moving_window(rates, "bin", (0.25, 0.5, 0.25))
    rebinned = rebin(counts, "bin", (0.0, 2.0, 3.0))
    ellipse = rme_ellipse_attribution(rates[0:2])
    bench = benchmark_100k_events()

    print("covreduce importing program: shared monitor + shared background")
    print(f"rates           = {[round(v, 6) for v in rates.values]}")
    print(f"rate variances  = {[round(v, 8) for v in rates.variance]}")
    print(f"oracle parity   = max |cov diff| {diff:.3e}")
    print(f"weighted fit    = {fit_value:.6f} +- {fit_var ** 0.5:.6f} "
          f"(covreduce, shared sources kept)")
    print(f"  independent   = sigma {indep_fit ** 0.5:.6f} "
          f"(baseline: shared sources wrongly split)")
    print(f"  Monte Carlo   = sigma {mc_fit ** 0.5:.6f} (6000 seeded draws)")
    print(f"  ESSreduce ub  = variance <= {bound:.3e} (upper bound only)")
    print(f"smoothed rates  = {[round(v, 6) for v in smoothed.values]}")
    print(f"rebinned counts = {[round(v, 3) for v in rebinned.values]} "
          f"(sum conserved: {sum(rebinned.values):.3f})")
    print(f"  gvar-equiv    = variance {gvar_var:.3e} (dense graph check)")
    print(f"RME ellipse     = area {ellipse['ellipse_area']:.3e} vs "
          f"independent {ellipse['independent_ellipse_area']:.3e}, "
          f"corr {ellipse['correlation']:.3f}")
    print(f"events bench    = {bench['events']} events -> {bench['bins']} "
          f"bins in {bench['seconds']:.2f}s, peak {bench['peak_bytes']} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
