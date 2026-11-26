import itertools
import unittest

import numpy as np

from resolution_precision import (path_envelopes, community_envelopes,
                                  envelope_interval, paired_population,
                                  zero_sample_necessary_count, nonnegative_upper)


class ResolutionPrecisionTests(unittest.TestCase):
    def test_failure_envelopes_contain_every_completion(self):
        for a, b in itertools.product((None, -.8, .3, 1.), repeat=2):
            score, delta = path_envelopes(a, b, (-1., 1.))
            xs = np.linspace(-1, 1, 21) if a is None else [a]
            ys = np.linspace(-1, 1, 21) if b is None else [b]
            for x, y in itertools.product(xs, ys):
                self.assertLessEqual(score[0], x+1e-15)
                self.assertGreaterEqual(score[1], x-1e-15)
                self.assertLessEqual(delta[0], abs(x-y)+1e-15)
                self.assertGreaterEqual(delta[1], abs(x-y)-1e-15)

    def test_partial_failure_is_not_whole_community_deletion(self):
        score, delta = community_envelopes([(.8, .7), (None, .2)], (0., 1.), 2)
        np.testing.assert_allclose(score, (.4, .9))
        np.testing.assert_allclose(delta, (.05, .45))

    def test_paths_stay_nested(self):
        one = paired_population([[(.8, .7)] for _ in range(12)], (0., 1.), 1, family_size=48)
        two = paired_population([[(.8, .7), (.8, .7)] for _ in range(12)], (0., 1.), 2, family_size=48)
        self.assertEqual(one['communities'], two['communities'])
        np.testing.assert_allclose(one['score_mean'], two['score_mean'])
        np.testing.assert_allclose(one['mean_absolute_difference'], two['mean_absolute_difference'])

    def test_no_failures_still_have_positive_uncertainty(self):
        result = paired_population([[(1., 1.)]]*24, (0., 1.), 1, family_size=48)
        self.assertLess(result['score_mean'][0], 1.)
        self.assertGreater(result['mean_absolute_difference'][1], 0.)

    def test_failures_widen_and_empty_data_are_uninformative(self):
        exact = envelope_interval([(.4, .4)]*24, (0., 1.), .05)
        failed = envelope_interval([(.4, .4)]*23+[(0., 1.)], (0., 1.), .05)
        self.assertLessEqual(failed[0], exact[0])
        self.assertGreaterEqual(failed[1], exact[1])
        self.assertEqual(envelope_interval([], (-1., 1.), .05), [-1., 1.])

    def test_invalid_inputs_do_not_silently_change_design(self):
        for value in (np.nan, np.inf, 1.1, True, '0.5'):
            with self.assertRaises(ValueError):
                path_envelopes(value, .5, (0., 1.))
        with self.assertRaises(ValueError):
            community_envelopes([(.5, .5)], (0., 1.), 2)
        for family in (1, True, 2.5):
            with self.assertRaises(ValueError):
                paired_population([], (0., 1.), 1, family_size=family)

    def test_triangle_bound_does_not_allow_signed_cancellation(self):
        paths = [(1., 0.), (0., 1.)]
        score, delta = community_envelopes(paths, (0., 1.), 2)
        self.assertEqual(score, (.5, .5))
        self.assertEqual(delta, (1., 1.))

    def test_necessary_count_matches_adversarial_coverage_boundary(self):
        for radius in (1., 2.):
            for alpha in (.05, .05/48, .05/96):
                n = zero_sample_necessary_count(radius, .005, alpha)
                probability = 1-.005/radius
                self.assertLessEqual(probability**n, alpha)
                self.assertGreater(probability**(n-1), alpha)

    def test_zero_upper_attains_necessary_boundary(self):
        alpha, epsilon = .05/48, .005
        n = zero_sample_necessary_count(2., epsilon, alpha)
        self.assertLessEqual(nonnegative_upper([0.]*n, 2., alpha), epsilon)
        self.assertGreater(nonnegative_upper([0.]*(n-1), 2., alpha), epsilon)
        self.assertEqual(nonnegative_upper([0., 2., 0.], 2., alpha), 2.)

    def test_one_sided_anytime_coverage_by_exact_bernoulli_recursion(self):
        # A success takes the maximum value, so the bet then stays zero.
        # Only the all-zero prefix can cross; compute its exact probability.
        alpha = .05
        for mean in (.01, .1, .4, .9):
            surviving_zero_probability = 1.
            crossed = 0.
            already_crossed = False
            for n in range(1, 501):
                surviving_zero_probability *= 1-mean
                if not already_crossed and nonnegative_upper([0.]*n, 1., alpha) < mean:
                    crossed += surviving_zero_probability
                    already_crossed = True
            self.assertLessEqual(crossed, alpha+1e-14)

    def test_interior_atom_exact_path_crossing_probability(self):
        atoms, weights, alpha = (0., .25, 1.), (.3, .4, .3), .2
        mean = sum(x*p for x, p in zip(atoms, weights))
        active = [(1., 1.)]  # probability, wealth; absorb first crossings
        crossed = 0.
        for _ in range(8):
            remaining = []
            for probability, wealth in active:
                for x, weight in zip(atoms, weights):
                    p, w = probability*weight, wealth*(1-x)/(1-mean)
                    if w >= 1/alpha:
                        crossed += p
                    else:
                        remaining.append((p, w))
            active = remaining
        self.assertLessEqual(crossed, alpha+1e-14)
        self.assertAlmostEqual(crossed+sum(p for p, w in active), 1.)


if __name__ == '__main__':
    unittest.main()
