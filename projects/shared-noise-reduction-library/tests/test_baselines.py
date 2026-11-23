"""Hand-derived checks for covreduce.baselines.

Every expected value below is derived by hand from first-order propagation
(J C J^T with the Jacobian written out), not by running the package first.

Scenario A: monitor m ~ (100, var 4); counts c = [100, 50], diag var [10, 5],
all independent.  Rates r_i = c_i / m, so dr_i = dc_i/100 - c_i/m^2 dm:
  Var(r0) = 10/10^4 + (100/10^4)^2 * 4 = 1.4e-3
  Var(r1) =  5/10^4 +  (50/10^4)^2 * 4 = 6.0e-4
  Cov(r0, r1) = (100 * 50 / 10^8) * 4  = 2.0e-4   (monitor term only)

Scenario B: x = [1, 2] with primitive covariance [[1, 0.5], [0.5, 2]].
  Var(0.6 x0 + 0.4 x1) = 0.36*1 + 0.16*2 + 2*0.24*0.5 = 0.92
  Var(x0 + x1) = 1 + 2 + 2*0.5 = 4
"""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import source
from covreduce.baselines import (essreduce_upper_bound,
                                 gvar_equivalent_variance,
                                 independent_variance_covariance,
                                 monte_carlo_covariance,
                                 rme_ellipse_attribution)


def bins(values, cov):
    return source(values, cov, dims=("bin",),
                  coords={"bin": tuple(i + 0.5 for i in range(len(values)))})


def scenario_a():
    monitor = source(100.0, 4.0)
    counts = bins([100.0, 50.0], [10.0, 5.0])
    return monitor, counts, counts / monitor


class TestBaselinesHandCheck(unittest.TestCase):
    def test_full_covariance_matches_hand_jcjt(self):
        _, _, rates = scenario_a()
        cov = rates.covariance()
        self.assertAlmostEqual(cov[0][0], 1.4e-3, places=12)
        self.assertAlmostEqual(cov[0][1], 2.0e-4, places=12)
        self.assertAlmostEqual(cov[1][1], 6.0e-4, places=12)

    def test_independent_variance_keeps_shared_monitor_term(self):
        # The monitor is ONE primitive element shared by both outputs, so
        # the independent-element baseline cannot remove its cross term.
        _, _, rates = scenario_a()
        indep = independent_variance_covariance(rates)
        self.assertAlmostEqual(indep[0][1], 2.0e-4, places=12)
        self.assertAlmostEqual(indep[0][0], 1.4e-3, places=12)

    def test_independent_variance_drops_primitive_correlation(self):
        x = bins([1.0, 2.0], [[1.0, 0.5], [0.5, 2.0]])
        indep = independent_variance_covariance(x)
        self.assertAlmostEqual(indep[0][1], 0.0, places=12)
        self.assertAlmostEqual(x.covariance()[0][1], 0.5, places=12)

    def test_gvar_equivalent_matches_hand_dense(self):
        x = bins([1.0, 2.0], [[1.0, 0.5], [0.5, 2.0]])
        got = gvar_equivalent_variance([(0.6, x[0]), (0.4, x[1])])
        self.assertAlmostEqual(got, 0.92, places=12)
        self.assertAlmostEqual(got, x.quadratic_form((0.6, 0.4)), places=12)

    def test_essreduce_bound_hand_value_and_covers_truth(self):
        # One block: radius = max|C| = 2, contracted = [1, 1] for w = (1, 1),
        # bound = 2 * (1 + 1)^2 = 8, true w^T C w = 4.
        x = bins([1.0, 2.0], [[1.0, 0.5], [0.5, 2.0]])
        bound = essreduce_upper_bound(x, (1.0, 1.0))
        self.assertAlmostEqual(bound, 8.0, places=12)
        self.assertGreaterEqual(bound, x.quadratic_form((1.0, 1.0)))

    def test_rme_ellipse_hand_values(self):
        x = bins([1.0, 2.0], [[1.0, 0.5], [0.5, 2.0]])
        out = rme_ellipse_attribution(x)
        self.assertAlmostEqual(out["ellipse_area"], math.pi * math.sqrt(1.75))
        self.assertAlmostEqual(out["independent_ellipse_area"],
                               math.pi * math.sqrt(2.0))
        self.assertAlmostEqual(out["correlation"], 0.5 / math.sqrt(2.0))
        self.assertEqual(out["source_trace_shares"], [(0, 1.0)])

    def test_monte_carlo_agrees_with_hand_covariance(self):
        monitor, counts, _ = scenario_a()

        def flat_program(flats):
            mon, cnt = flats[1][0], flats[0]
            return tuple(c / mon for c in cnt)

        mc = monte_carlo_covariance([counts, monitor], flat_program,
                                    draws=8000, seed=20261123)
        self.assertAlmostEqual(mc[0][0], 1.4e-3, delta=1.4e-4)
        self.assertAlmostEqual(mc[0][1], 2.0e-4, delta=6.0e-5)
        self.assertAlmostEqual(mc[1][1], 6.0e-4, delta=8.0e-5)


if __name__ == "__main__":
    unittest.main()
