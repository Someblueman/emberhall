import unittest
import numpy as np
from bounded_precision import confidence_sequence, completion_interval, log_wealth


class BoundedPrecisionTests(unittest.TestCase):
    def test_exact_bernoulli_anytime_crossing_probability(self):
        # Exact probability recursion, not Monte Carlo or a fixed-time check.
        # States retain only paths that have not crossed the rejection boundary.
        alpha = .05
        for p in (.01, .1, .3, .5, .8, .99):
            live = {0: 1.}
            crossed = 0.
            for n in range(1, 41):
                next_live = {}
                for k, mass in live.items():
                    for success, chance in ((0, 1-p), (1, p)):
                        count = k+success
                        values = [1.]*count+[0.]*(n-count)
                        weight = mass*chance
                        if log_wealth(p, values) >= -np.log(alpha):
                            crossed += weight
                        else:
                            next_live[count] = next_live.get(count, 0.)+weight
                live = next_live
            self.assertLessEqual(crossed, alpha+1e-12)
            self.assertAlmostEqual(crossed+sum(live.values()), 1.)

    def test_general_bounded_mean_wealth_has_unit_expectation(self):
        # A non-Bernoulli distribution with an atom inside the interval.
        import itertools
        support = np.array([0., .4, 1.]); probabilities = np.array([.2, .5, .3])
        mean = support@probabilities
        expectation = sum(np.exp(log_wealth(mean, support[list(indices)]))
                          * np.prod(probabilities[list(indices)])
                          for indices in itertools.product(range(3), repeat=4))
        self.assertAlmostEqual(expectation, 1.)

    def test_intervals_retain_uncertainty_and_failures(self):
        self.assertEqual(confidence_sequence([]), [0., 1.])
        good = completion_interval([1.]*24, (0, 1))
        self.assertLess(good[0], 1.)
        self.assertEqual(good[1], 1.)
        failed = completion_interval([1.]*23+[None], (0, 1))
        self.assertLess(failed[0], good[0])
        self.assertEqual(completion_interval([None]*24, (-1, 1)), [-1., 1.])
        for values in ([float('nan')], [-.1], [1.1]):
            with self.assertRaises(ValueError):
                confidence_sequence(values)

    def test_confidence_set_matches_dense_wealth_grid(self):
        values = [.1, .4, .7, .2, .9]*8
        low, high = confidence_sequence(values)
        for mean in np.linspace(.001, .999, 101):
            self.assertEqual(low <= mean <= high, log_wealth(mean, values) < -np.log(.05))


if __name__ == '__main__':
    unittest.main()
