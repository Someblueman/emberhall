import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import (moving_window, rebin, reorder_dims, source,
                       UnsupportedOperationError)
from covreduce.baselines import (essreduce_upper_bound,
                                 gvar_equivalent_variance,
                                 monte_carlo_covariance,
                                 rme_ellipse_attribution)
from covreduce.oracle import dense_jcjt_oracle, max_covariance_difference


def bins(values, cov):
    return source(values, cov, dims=("bin",),
                  coords={"bin": tuple(i + 0.5 for i in range(len(values)))})


class TestCore(unittest.TestCase):
    def test_same_source_cancels(self):
        x = bins([10.0, 20.0], [[1.0, 0.2], [0.2, 4.0]])
        self.assertEqual((x - x).variance, [0.0, 0.0])

    def test_equal_valued_independent_sources_do_not_cancel(self):
        x = bins([10.0], [2.0])
        y = bins([10.0], [2.0])
        self.assertAlmostEqual((x - y).variance, 4.0)

    def test_shared_monitor_cross_terms(self):
        monitor = source(100.0, 4.0)
        counts = bins([100.0, 50.0], [10.0, 5.0])
        rates = counts / monitor
        cov = rates.covariance()
        self.assertGreater(cov[0][1], 0.0)  # shared monitor correlates bins

    def test_covariance_symmetric_and_psd(self):
        x = bins([1.0, 2.0, 3.0], [[2.0, 0.3, 0.0], [0.3, 1.0, 0.1],
                                   [0.0, 0.1, 3.0]])
        y = (x * 2.0 - x)
        cov = y.covariance()
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(cov[i][j], cov[j][i], places=12)
        for w in ((1, 0, 0), (0.2, -0.5, 0.9), (-1, -2, 0.3)):
            self.assertGreaterEqual(y.quadratic_form(w), -1e-12)

    def test_negative_weights_moving_window(self):
        x = bins([1.0, 2.0, 4.0, 8.0], [0.1, 0.2, 0.3, 0.4])
        out = moving_window(x, "bin", (-1.0, 1.0))
        self.assertEqual(out.values, (1.0, 2.0, 4.0))

    def test_mask_select_list(self):
        x = bins([1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        kept = x.select("bin", [0, 2])
        self.assertEqual(kept.values, (1.0, 3.0))
        self.assertEqual(kept.variance, [1.0, 1.0])

    def test_rebin_conserves_counts(self):
        x = bins([10.0, 20.0, 30.0], [1.0, 1.0, 1.0])
        out = rebin(x, "bin", (0.0, 2.0, 3.0))
        self.assertAlmostEqual(sum(out.values), 60.0)

    def test_unsupported_operations_rejected(self):
        x = bins([10.0], [1.0])
        with self.assertRaises(UnsupportedOperationError):
            x // 2
        with self.assertRaises(UnsupportedOperationError):
            x % 2
        with self.assertRaises(UnsupportedOperationError):
            x.apply_discontinuous()

    def test_dimension_reorder_values(self):
        x = source([[1.0, 2.0], [3.0, 4.0]], [1.0] * 4,
                   dims=("row", "col"))
        out = reorder_dims(x, "col", "row")
        self.assertEqual(out.values, (1.0, 3.0, 2.0, 4.0))

    def test_quadratic_form_matches_dense(self):
        x = bins([1.0, 2.0], [[2.0, 0.5], [0.5, 3.0]])
        w = (0.7, -0.4)
        cov = x.covariance()
        dense = sum(w[i] * cov[i][j] * w[j] for i in range(2)
                    for j in range(2))
        self.assertAlmostEqual(x.quadratic_form(w), dense, places=12)


class TestOracle(unittest.TestCase):
    def test_oracle_parity_monitor_program(self):
        monitor = source(100.0, 4.0)
        counts = bins([100.0, 50.0], [[10.0, 1.0], [1.0, 5.0]])
        bkg = bins([5.0, 5.0], [[0.3, 0.25], [0.25, 0.3]])
        rates = counts / monitor - bkg / monitor
        diff = max_covariance_difference(
            rates, [monitor, counts, bkg],
            lambda p: p[1] / p[0] - p[2] / p[0])
        self.assertLess(diff, 1e-12)

    def test_oracle_repeated_source_is_zero(self):
        x = bins([10.0], [3.0])
        values, cov = dense_jcjt_oracle([x, x], lambda a: a[0] - a[1])
        self.assertEqual(values, (0.0,))
        self.assertAlmostEqual(cov[0][0], 0.0, places=15)

    def test_oracle_rejects_derived_input(self):
        x = bins([10.0], [3.0])
        derived = x * 2.0
        with self.assertRaises(ValueError):
            dense_jcjt_oracle([derived], lambda a: a[0] + 1.0)

    def test_oracle_reorder_parity(self):
        x = source([[1.0, 2.0], [3.0, 4.0]],
                   [[1.0, 0.1, 0.0, 0.0], [0.1, 2.0, 0.2, 0.0],
                    [0.0, 0.2, 3.0, 0.3], [0.0, 0.0, 0.3, 4.0]],
                   dims=("row", "col"))
        out = reorder_dims(x, "col", "row") * 1.5
        diff = max_covariance_difference(
            out, [x], lambda a: a[0].reorder_dims("col", "row") * 1.5)
        self.assertLess(diff, 1e-12)

    def test_oracle_moving_window_negative_weights(self):
        x = bins([1.0, 2.0, 4.0, 8.0], [[0.4, 0.1, 0.0, 0.0],
                                         [0.1, 0.5, 0.1, 0.0],
                                         [0.0, 0.1, 0.6, 0.1],
                                         [0.0, 0.0, 0.1, 0.7]])
        out = moving_window(x, "bin", (-0.5, 1.0, -0.25))
        diff = max_covariance_difference(
            out, [x],
            lambda a: a[0].moving_window("bin", (-0.5, 1.0, -0.25)))
        self.assertLess(diff, 1e-12)


class TestBaselines(unittest.TestCase):
    def test_monte_carlo_agrees_within_tolerance(self):
        monitor = source(100.0, 4.0)
        counts = bins([100.0, 50.0], [10.0, 5.0])
        mc = monte_carlo_covariance(
            [monitor, counts],
            lambda f: tuple(c / f[0][0] for c in f[1]), draws=8000)
        exact = (counts / monitor).covariance()
        self.assertAlmostEqual(mc[0][0], exact[0][0], delta=0.0015)
        self.assertAlmostEqual(mc[0][1], exact[0][1], delta=0.0015)

    def test_essreduce_bound_is_above(self):
        x = bins([1.0, 2.0], [[2.0, 0.5], [0.5, 3.0]])
        bound = essreduce_upper_bound(x, (1.0, 1.0))
        self.assertGreaterEqual(bound + 1e-12, x.quadratic_form((1.0, 1.0)))

    def test_gvar_equivalent_matches_library(self):
        monitor = source(100.0, 4.0)
        counts = bins([100.0, 50.0], [10.0, 5.0])
        rates = counts / monitor
        dense = gvar_equivalent_variance([(0.6, rates[0]), (0.4, rates[1])])
        self.assertAlmostEqual(dense, rates.quadratic_form((0.6, 0.4)),
                               places=12)

    def test_rme_ellipse_independent_expected_value(self):
        # Independent hand check: two independent outputs with variances
        # 4 and 9 have ellipse area pi*sqrt(det)=pi*6.
        import math
        x = bins([1.0, 2.0], [[4.0, 0.0], [0.0, 9.0]])
        result = rme_ellipse_attribution(x)
        self.assertAlmostEqual(result["ellipse_area"], math.pi * 6.0,
                               places=10)
        self.assertAlmostEqual(result["correlation"], 0.0, places=12)
        shares = dict(result["source_trace_shares"])
        self.assertAlmostEqual(sum(shares.values()), 1.0, places=10)


if __name__ == "__main__":
    unittest.main()
