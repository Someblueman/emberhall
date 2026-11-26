import unittest
import numpy as np
from covariance_diagnostic import decompose, rank


class TotalCovariance(unittest.TestCase):
    def test_constant_halves_have_only_between_covariance(self):
        x = np.array([[0., 0.], [0., 0.], [2., 4.], [2., 4.]])
        full, within, between, delta = decompose(x)
        np.testing.assert_array_equal(within, np.zeros((2, 2)))
        np.testing.assert_array_equal(full, [[1., 2.], [2., 4.]])
        np.testing.assert_array_equal(between, full)
        np.testing.assert_array_equal(delta, [-2., -4.])

    def test_unequal_halves_use_observation_weights(self):
        x = np.array([[1., 3.], [4., 2.], [-1., 5.], [2., -3.], [7., 4.]])
        full, within, between, _ = decompose(x)
        np.testing.assert_allclose(full, np.cov(x.T, bias=True), atol=1e-14)
        np.testing.assert_allclose(full, within+between, atol=1e-14)

    def test_matching_halves_have_no_between_term(self):
        x = np.array([[0., 1.], [2., 3.], [0., 1.], [2., 3.]])
        full, within, between, _ = decompose(x)
        np.testing.assert_array_equal(between, np.zeros((2, 2)))
        np.testing.assert_array_equal(full, within)

    def test_undefined_rank_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'nonconstant'):
            rank(np.eye(6), np.arange(15))
        with self.assertRaisesRegex(ValueError, 'finite'):
            rank(np.eye(6), np.full(15, np.nan))


if __name__ == '__main__':
    unittest.main()
