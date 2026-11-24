import itertools
import math
import random
import unittest

from baseline import (Design, Observation, calibration, event_marginal,
                      mixed_fraction, poisson_change_point, posterior,
                      quantile, response, simulate)


class MixingTests(unittest.TestCase):
    def test_support_mass_and_midpoint(self):
        self.assertEqual(mixed_fraction(1000, 799, 200), 0)
        self.assertEqual(mixed_fraction(1000, 800, 200), 0)
        self.assertAlmostEqual(mixed_fraction(1000, 1000, 200), 1 - math.exp(-1))
        self.assertAlmostEqual(mixed_fraction(1000, 1000 - 200 + 200 * math.log(2), 200), .5)
        # At three mixing depths older, retained mass is 1-exp(-4), not 1-exp(-3).
        self.assertAlmostEqual(mixed_fraction(1000, 1600, 200), 1 - math.exp(-4))
        self.assertAlmostEqual(mixed_fraction(1000, 100000, 200), 1)

    def test_unmixed_limit_and_age_orientation(self):
        self.assertEqual(mixed_fraction(-2, 0, 0), 1)
        self.assertEqual(mixed_fraction(2, 0, 0), 0)
        self.assertEqual(mixed_fraction(2, 0, .00001), 0)
        self.assertEqual(mixed_fraction(-2, 0, .00001), 1)
        for focal in (-100, 0, 100):
            vals = [mixed_fraction(focal, t, 25) for t in range(-200, 201)]
            self.assertEqual(vals, sorted(vals))

    def test_actual_particle_generator_matches_analytic_law(self):
        # Independent age draws test the sign and shift of the analytic CDF.
        design = Design(events=(0,), mixing_times=(75,), focal_ages=(0,), specimens=100000)
        obs = simulate(design, 0, 75, random.Random(7124))
        expected = .1 + .8 * (1 - math.exp(-1))
        self.assertLess(abs(obs.positive_counts[0] / design.specimens - expected), .006)


class InferenceTests(unittest.TestCase):
    def test_poisson_example_against_rational_integration(self):
        # For D=(2,0), exp(1) priors: s1 evidence=2/27, s2=1/8.
        p = poisson_change_point((2, 0))
        self.assertAlmostEqual(p[0], 16 / 43)
        self.assertAlmostEqual(p[1], 27 / 43)
        self.assertEqual(poisson_change_point((3,)), (1,))

    def test_direct_binomial_enumeration_and_calibration_identity(self):
        design = Design(events=(-1, 0, 1), mixing_times=(0, 1),
                        focal_ages=(-1, 1), specimens=2)
        states = design.states()
        recovered_prior = [0.0] * len(states)
        coverage = 0.0
        expected_mass = 0.0
        predictive_total = 0.0
        for counts in itertools.product(range(3), repeat=2):
            # Independent probability-space product incl. binomial factors.
            likelihoods = []
            for event, mixing in states:
                terms = []
                for focal, k in zip(design.focal_ages, counts):
                    p = response(design, focal, event, mixing)
                    terms.append(math.comb(2, k) * p ** k * (1 - p) ** (2 - k))
                likelihoods.append(math.prod(terms))
            predictive = sum(likelihoods) / len(states)
            predictive_total += predictive
            obs = Observation(design.focal_ages, 2, counts)
            weights = posterior(design, obs)
            for i, (weight, likelihood) in enumerate(zip(weights, likelihoods)):
                self.assertAlmostEqual(weight, likelihood / sum(likelihoods), places=13)
                recovered_prior[i] += predictive * weight
            marginal = event_marginal(design, weights)
            lo = quantile(design.events, marginal, .05)
            hi = quantile(design.events, marginal, .95)
            mass = sum(w for t, w in zip(design.events, marginal) if lo <= t <= hi)
            expected_mass += predictive * mass
            coverage += sum(likelihood / len(states) for (t, _), likelihood in zip(states, likelihoods)
                            if lo <= t <= hi)
        self.assertAlmostEqual(predictive_total, 1)
        for value in recovered_prior:
            self.assertAlmostEqual(value, 1 / len(states))
        self.assertAlmostEqual(coverage, expected_mass)

    def test_missing_information_recovers_prior(self):
        design = Design(focal_ages=(1000,), specimens=1)
        weights = posterior(design, Observation((1000,), 1, (0,)))
        # Every state's younger support ends below focal=1000.
        for value in weights:
            self.assertAlmostEqual(value, 1 / len(weights))

    def test_large_counts_remain_normalized(self):
        design = Design(specimens=10000)
        obs = Observation(design.focal_ages, 10000, (10000,) * len(design.focal_ages))
        weights = posterior(design, obs)
        self.assertAlmostEqual(sum(weights), 1)
        self.assertTrue(all(math.isfinite(w) and w >= 0 for w in weights))

    def test_invalid_data_fail_explicitly(self):
        for kwargs in ({"events": ()}, {"events": (1, 0)}, {"mixing_times": (-1,)},
                       {"specimens": 0}, {"young_probability": 1}):
            with self.assertRaises(ValueError):
                Design(**kwargs)
        design = Design()
        for obs in (Observation((0,), 1, (0,)),
                    Observation(design.focal_ages, 16, (0,)),
                    Observation(design.focal_ages, 16, (17,) * len(design.focal_ages))):
            with self.assertRaises(ValueError):
                posterior(design, obs)
        for vals in ((0, 0, -1), (math.nan, 0, 1)):
            with self.assertRaises(ValueError):
                mixed_fraction(*vals)
        with self.assertRaises(ValueError):
            poisson_change_point((1, -1))

    def test_declared_run_distinguishes_mixing_control(self):
        correct = calibration()
        wrong = calibration(ignore_mixing=True)
        self.assertTrue(correct['pit_within_band'])
        self.assertFalse(wrong['pit_within_band'])
        self.assertLess(abs(correct['coverage_minus_mass']), .02)
        self.assertLess(wrong['coverage_minus_mass'], -.1)

    def test_prior_only_can_pass_marginal_check_but_not_conditional_check(self):
        prior = calibration(prior_only=True)
        self.assertTrue(prior['pit_within_band'])
        self.assertAlmostEqual(prior['event_information_mean_nats'], 0)
        self.assertEqual(prior['interval_width_mean_years'], 200)
        for result in prior['data_conditional_pit'].values():
            self.assertFalse(result['pit_within_band'])
        correct = calibration()
        self.assertGreater(correct['event_information_mean_nats'], 1)
        for result in correct['data_conditional_pit'].values():
            self.assertTrue(result['pit_within_band'])

    def test_continuous_truth_is_not_validated_by_finite_prior_success(self):
        wrong = calibration(continuous_truth=True)
        self.assertFalse(wrong['pit_within_band'])
        self.assertLess(wrong['interval_coverage'], .5)


if __name__ == "__main__":
    unittest.main()
