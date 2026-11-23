#!/usr/bin/env python3
"""Second covreduce importing program: sharpened spectral fit.

Distinct from run_demo.py / covreduce.cli (a positive-weight mean fit):
this program applies an overlapping moving-window stencil with negative
side lobes in mode="same", then a peak-fit weight vector that is
negative away from the centre.  The fit covariance is checked against
the dense J C J^T oracle, the ESSreduce-style upper bound and a seeded
Monte Carlo.  Standard library only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from covreduce import moving_window, rebin, source
from covreduce.baselines import essreduce_upper_bound, monte_carlo_covariance
from covreduce.oracle import max_covariance_difference

# Overlapping stencil: negative side lobes, mode keeps all 5 outputs.
STENCIL = (-0.25, 0.5, 1.0, 0.5, -0.25)
# Peak fit: negative flanks, weights sum to one.
FIT_WEIGHTS = (-0.1, 0.3, 0.6, 0.3, -0.1)
NEW_EDGES = (0.0, 2.0, 5.0)


def build_program():
    monitor = source(1000.0, 25.0)
    counts = source([120.0, 95.0, 60.0, 30.0, 15.0],
                    [12.0, 9.0, 8.0, 10.0, 7.0], dims=("bin",),
                    coords={"bin": (0.5, 1.5, 2.5, 3.5, 4.5)})
    rates = counts / monitor
    smooth = moving_window(rates, "bin", STENCIL, mode="same")
    return monitor, counts, rates, smooth


def fit_value(smooth):
    return sum(w * v for w, v in zip(FIT_WEIGHTS, smooth.values))


def flat_smooth(values):
    """Seeded-sample twin of the same-mode stencil (independent code)."""
    n, width, left = len(values), len(STENCIL), len(STENCIL) // 2
    out = []
    for j in range(n):
        start = j - left
        out.append(sum(STENCIL[k] * values[start + k]
                       for k in range(width) if 0 <= start + k < n))
    return out


def flat_program(flats):
    mon, cnt = flats[0][0], flats[1]
    return tuple(flat_smooth([c / mon for c in cnt]))


def main(argv=None):
    monitor, counts, rates, smooth = build_program()

    def oracle_program(parts):
        return (parts[1] / parts[0]).moving_window("bin", STENCIL,
                                                    mode="same")

    diff = max_covariance_difference(smooth, [monitor, counts],
                                     oracle_program)
    fit = fit_value(smooth)
    fit_var = smooth.quadratic_form(FIT_WEIGHTS)
    bound = essreduce_upper_bound(smooth, FIT_WEIGHTS)
    draws = 8000
    mc = monte_carlo_covariance([monitor, counts], flat_program,
                                draws=draws, seed=20261123)
    mc_fit = sum(FIT_WEIGHTS[i] * mc[i][j] * FIT_WEIGHTS[j]
                 for i in range(5) for j in range(5))
    rebinned_counts = rebin(counts, "bin", NEW_EDGES)
    rebinned_rates = rebin(rates, "bin", NEW_EDGES, intensive=True)

    if diff > 1e-12:
        print(f"FAIL oracle parity {diff:.3e} > 1e-12", file=sys.stderr)
        return 1
    if fit_var > bound + 1e-12:
        print("FAIL ESS bound does not cover fit variance", file=sys.stderr)
        return 1
    if abs(mc_fit - fit_var) > 0.15 * fit_var:
        print(f"FAIL MC {mc_fit:.3e} vs fit {fit_var:.3e} > 15%",
              file=sys.stderr)
        return 1
    if abs(sum(rebinned_counts.values) - sum(counts.values)) > 1e-9:
        print("FAIL rebinned counts do not conserve the sum",
              file=sys.stderr)
        return 1

    print("covreduce weighted-fit program: sharpened spectrum + peak fit")
    print(f"smoothed rates  = {[round(v, 6) for v in smooth.values]}")
    print(f"oracle parity   = max |cov diff| {diff:.3e}")
    print(f"peak fit        = {fit:.6f} +- {fit_var ** 0.5:.6f} "
          f"(negative flanks, overlapping windows)")
    print(f"  Monte Carlo   = sigma {mc_fit ** 0.5:.6f} "
          f"({draws} seeded draws)")
    print(f"  ESSreduce ub  = variance <= {bound:.3e} (upper bound only)")
    print(f"rebinned counts = {[round(v, 3) for v in rebinned_counts.values]}"
          f" (sum conserved: {sum(rebinned_counts.values):.3f})")
    print(f"rebinned rates  = "
          f"{[round(v, 6) for v in rebinned_rates.values]} (intensive)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
