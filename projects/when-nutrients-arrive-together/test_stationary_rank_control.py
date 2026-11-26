import unittest
from scipy.stats import binom
from stationary_rank_control import binomial_interval


class ExactIntervalTests(unittest.TestCase):
    def test_exact_binomial_coverage_including_boundaries(self):
        intervals = [binomial_interval(k, 20) for k in range(21)]
        for p in (0., .01, .1, .3, .5, .8, .99, 1.):
            coverage = sum(binom.pmf(k, 20, p) for k, (a, b) in enumerate(intervals) if a <= p <= b)
            self.assertGreaterEqual(coverage, .95-1e-12)
        self.assertEqual(intervals[0][0], 0.)
        self.assertGreater(intervals[0][1], 0.)
        self.assertLess(intervals[-1][0], 1.)
        self.assertEqual(intervals[-1][1], 1.)


if __name__ == '__main__':
    unittest.main()
