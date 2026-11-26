import unittest

import numpy as np
from scipy.stats import norm

from supply_guard import guard_bound


class SupplyGuardTests(unittest.TestCase):
    def test_union_contains_independent_control_without_assuming_independence(self):
        # Independent Gaussian nodes are a separate exact control, not OU data.
        for mean in (.2, 1., 2.):
            bound = guard_bound(1, .25, [mean]*3, amplitude=1.)
            p = norm.cdf(-mean*np.sqrt(2))
            exact = -np.expm1(15*np.log1p(-p))
            self.assertLessEqual(bound['probability_lower'], exact+1e-15)
            self.assertGreaterEqual(bound['probability_upper']+1e-15, exact)

    def test_union_formula_and_mesh_node_count(self):
        bound = guard_bound(1, .25, [1., 3.])
        self.assertEqual(bound['nodes'], 5)
        self.assertAlmostEqual(bound['probability_upper'],
            5*(norm.cdf(-np.sqrt(200))+norm.cdf(-3*np.sqrt(200))), delta=1e-56)
        self.assertGreater(guard_bound(1, .125, [1., 3.])['probability_upper'], bound['probability_upper'])

    def test_log_probability_retains_tiny_nonzero_model_risk(self):
        bound = guard_bound(1, .25, [3.])
        self.assertTrue(np.isfinite(bound['log_probability_upper']))
        self.assertLess(bound['log_probability_upper'], -700)
        # Float underflow in exp is not mathematical impossibility.

    def test_invalid_parameters(self):
        for duration, spacing, means, amplitude in ((1, .3, [1], .1), (0, .1, [1], .1),
                (1, .1, [], .1), (1, .1, [np.nan], .1), (1, .1, [1], 0)):
            with self.assertRaises(ValueError):
                guard_bound(duration, spacing, means, amplitude)


if __name__ == '__main__':
    unittest.main()
