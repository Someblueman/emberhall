"""Hand-derived checks for the weighted-fit importing program.

Expected values are computed here from first-order propagation written
out explicitly (J C J^T with the Jacobian derived in this file), not by
running the package first.

Rates r_i = c_i / m with independent diagonal counts and one shared
monitor m:
  Cov(r_i, r_j) = delta_ij * var(c_i) / m^2
                  + c_i * c_j / m^4 * var(m)
The same-mode stencil is replicated below from STENCIL alone.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import rebin
from covreduce.baselines import essreduce_upper_bound, monte_carlo_covariance
from weighted_fit_demo import (FIT_WEIGHTS, NEW_EDGES, STENCIL,
                               build_program, flat_program, fit_value)

M = 1000.0
VAR_M = 25.0
C = [120.0, 95.0, 60.0, 30.0, 15.0]
VAR_C = [12.0, 9.0, 8.0, 10.0, 7.0]


def hand_rates_cov():
    return [[(VAR_C[i] / M ** 2 if i == j else 0.0)
             + C[i] * C[j] / M ** 4 * VAR_M
             for j in range(5)] for i in range(5)]


def hand_stencil():
    n, width, left = 5, len(STENCIL), len(STENCIL) // 2
    return [[STENCIL[k - (j - left)] if 0 <= k - (j - left) < width else 0.0
             for k in range(n)] for j in range(n)]


def hand_smooth_cov():
    cr, s = hand_rates_cov(), hand_stencil()
    return [[sum(s[i][a] * cr[a][b] * s[j][b]
                 for a in range(5) for b in range(5))
             for j in range(5)] for i in range(5)]


class TestWeightedFitHandCheck(unittest.TestCase):
    def test_fit_weights_have_negative_flanks(self):
        self.assertLess(min(FIT_WEIGHTS), 0.0)
        self.assertAlmostEqual(sum(FIT_WEIGHTS), 1.0, places=12)

    def test_smooth_covariance_matches_hand_jcjt(self):
        _, _, _, smooth = build_program()
        got, want = smooth.covariance(), hand_smooth_cov()
        for i in range(5):
            for j in range(5):
                self.assertAlmostEqual(got[i][j], want[i][j], places=12)

    def test_fit_variance_matches_hand_jcjt(self):
        _, _, _, smooth = build_program()
        want = sum(FIT_WEIGHTS[i] * hand_smooth_cov()[i][j] * FIT_WEIGHTS[j]
                   for i in range(5) for j in range(5))
        self.assertAlmostEqual(smooth.quadratic_form(FIT_WEIGHTS), want,
                               places=12)

    def test_overlapping_windows_share_covariance(self):
        _, _, _, smooth = build_program()
        want = hand_smooth_cov()
        self.assertGreater(abs(smooth.covariance()[0][1]), 0.0)
        self.assertAlmostEqual(smooth.covariance()[0][1], want[0][1],
                               places=12)

    def test_ess_bound_covers_truth(self):
        _, _, _, smooth = build_program()
        truth = smooth.quadratic_form(FIT_WEIGHTS)
        self.assertLessEqual(truth, essreduce_upper_bound(
            smooth, FIT_WEIGHTS) + 1e-12)

    def test_monte_carlo_agrees_within_tolerance(self):
        monitor, counts, _, smooth = build_program()
        mc = monte_carlo_covariance([monitor, counts], flat_program,
                                    draws=8000, seed=20261123)
        mc_fit = sum(FIT_WEIGHTS[i] * mc[i][j] * FIT_WEIGHTS[j]
                     for i in range(5) for j in range(5))
        truth = smooth.quadratic_form(FIT_WEIGHTS)
        self.assertLessEqual(abs(mc_fit - truth), 0.15 * truth)

    def test_rebin_conserves_extensive_and_intensive(self):
        _, counts, rates, _ = build_program()
        rc = rebin(counts, "bin", NEW_EDGES)
        rr = rebin(rates, "bin", NEW_EDGES, intensive=True)
        self.assertEqual([round(v, 9) for v in rc.values], [215.0, 105.0])
        self.assertAlmostEqual(sum(rc.values), sum(counts.values), places=9)
        # Intensive: width-weighted average is conserved (widths 2 and 3).
        self.assertAlmostEqual(2.0 * rr.values[0] + 3.0 * rr.values[1],
                               sum(rates.values), places=9)

    def test_fit_value_matches_manual_sum(self):
        _, _, _, smooth = build_program()
        manual = sum(w * v for w, v in zip(FIT_WEIGHTS, smooth.values))
        self.assertAlmostEqual(fit_value(smooth), manual, places=12)


if __name__ == "__main__":
    unittest.main()
