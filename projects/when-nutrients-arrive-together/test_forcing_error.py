import unittest
import numpy as np
from forcing_error import relative_error, interpolation_error
from reference import ou


class InterpolationChecks(unittest.TestCase):
    def test_formula_against_covariance_matrix(self):
        for a in (.0001, .0625, 1, 10):
            for theta in np.linspace(0, 1, 11):
                points = np.array([theta, 0, 1])
                covariance = np.exp(-a*np.abs(points[:, None]-points[None, :]))
                weights = np.array([1, -(1-theta), -theta])
                self.assertAlmostEqual(relative_error(theta, a), weights@covariance@weights, places=13)
        self.assertEqual(relative_error(0, .1), 0)
        self.assertEqual(relative_error(1, .1), 0)

    def test_observed_stationary_midpoint_error(self):
        path = ou(321, 4096, spacing=.0625)
        error = path[1:-1:2] - (path[:-2:2]+path[2::2])/2
        expected = .005*relative_error(.5, .125)
        self.assertLess(abs(np.mean(error**2)/expected-1), .02)

    def test_small_mesh_asymptote_and_refinement(self):
        result = interpolation_error(1e-5)
        self.assertAlmostEqual(result['mean_square_input_error']/(.005*1e-5/3), 1, places=5)
        errors = [interpolation_error(h)['mean_square_input_error'] for h in (.25, .125, .0625)]
        self.assertTrue(errors[0] > errors[1] > errors[2] > 0)
        with self.assertRaises(ValueError):
            interpolation_error(0)
