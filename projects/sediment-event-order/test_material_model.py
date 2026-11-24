import json
import math
import random
import unittest

from baseline import mixed_fraction
from material_model import (covariance_check, draw_sample, layer_fraction,
                            material_age, zero_width_covariance, normal_log_survival,
                            date_density_and_young_fraction, sample_log_likelihood,
                            joint_calibration)


class MaterialTests(unittest.TestCase):
    def test_convolution_limits_and_closed_form(self):
        self.assertAlmostEqual(layer_fraction(0, 0, 1, 1), (1 + math.exp(-2)) / 2)
        self.assertEqual(layer_fraction(0, -2, 1, 1), 0)
        self.assertEqual(layer_fraction(0, 1000, 1, 1), 1)
        self.assertEqual(layer_fraction(0, 1e20, 1, 1), 1)
        self.assertAlmostEqual(layer_fraction(0, 0, 0, 1), .5)
        self.assertEqual(layer_fraction(0, -2, 0, 1), 0)
        self.assertEqual(layer_fraction(0, 2, 0, 1), 1)
        for event in (-2, -.5, 0, 2):
            self.assertEqual(layer_fraction(0, event, 1, 0), mixed_fraction(0, event, 1))
            self.assertAlmostEqual(layer_fraction(0, event, 1, 1e-10),
                                   mixed_fraction(0, event, 1), places=12)

    def test_cdf_derivative_matches_published_convolution_density(self):
        h, width = 2, 1
        for z in (-2, -.5, .5, 2, 5):
            event = z - h
            epsilon = 1e-5
            derivative = (layer_fraction(0, event + epsilon, h, width)
                          - layer_fraction(0, event - epsilon, h, width)) / (2 * epsilon)
            if z < -width:
                expected = 0
            elif z <= width:
                expected = (1 - math.exp(-(z + width) / h)) / (2 * width)
            else:
                expected = math.exp(-(z - width) / h) * (1 - math.exp(-2 * width / h)) / (2 * width)
            self.assertAlmostEqual(derivative, expected, places=8)

    def test_age_sampler_moments_and_integrated_cdf(self):
        rng = random.Random(93179)
        ages = [material_age(1000, 75, 30, rng) for _ in range(100000)]
        mean = math.fsum(ages) / len(ages)
        variance = math.fsum((age - 1000) ** 2 for age in ages) / len(ages)
        fraction = sum(age <= 1000 for age in ages) / len(ages)
        self.assertLess(abs(mean - 1000), 1)
        self.assertLess(abs(variance / (75 ** 2 + 30 ** 2 / 3) - 1), .03)
        self.assertLess(abs(fraction - layer_fraction(1000, 1000, 75, 30)), .006)

    def test_export_preserves_overlap_but_excludes_latent_parameters(self):
        for overlap in (0, 4, 8):
            sample = draw_sample(depth_cm=10, focal=1000, event=1025, mixing=75,
                                 half_width=30, proxy_count=8, date_count=8,
                                 overlap=overlap, dating_sigma=20,
                                 age_rng=random.Random(1), proxy_rng=random.Random(2),
                                 date_rng=random.Random(3), prefix='core-A:depth-10')
            observed = sample.observed()
            proxies = {s['specimen_id'] for s in observed['proxy_measurements']}
            dates = {s['specimen_id'] for s in observed['date_measurements']}
            self.assertEqual(len(proxies), 8)
            self.assertEqual(len(dates), 8)
            self.assertEqual(len(proxies & dates), overlap)
            self.assertEqual(len(sample.specimens), 16 - overlap)
            self.assertEqual(set(observed), {'depth_cm', 'dating_sigma_years',
                                            'proxy_measurements', 'date_measurements'})
            text = json.dumps(observed, allow_nan=False)
            for key in ('true_age', 'focal', 'event', 'mixing', 'half_width'):
                self.assertNotIn(key, text)

    def test_covariance_identity_and_controls(self):
        self.assertAlmostEqual(zero_width_covariance(1000, 1000, 75, 8, 8, 8), -7.5 / math.e)
        self.assertAlmostEqual(zero_width_covariance(1000, 1000, 75, 8, 8, 4), -3.75 / math.e)
        self.assertEqual(zero_width_covariance(1000, 1000, 75, 8, 8, 0), 0)
        self.assertEqual(zero_width_covariance(1000, 900, 75, 8, 8, 8), 0)
        self.assertEqual(zero_width_covariance(1000, 1000, 0, 8, 8, 8), 0)
        self.assertEqual(zero_width_covariance(0, 1e20, 1, 8, 8, 8), 0)
        result = covariance_check(trials=5000)
        for row in result['cases']:
            self.assertLess(abs(row['error_in_standard_errors']), 5)

    def test_invalid_inputs_rejected(self):
        for values in ((0, 0, -1, 0), (0, 0, 1, -1), (math.nan, 0, 1, 1)):
            with self.assertRaises(ValueError):
                layer_fraction(*values)
        args = dict(depth_cm=10, focal=1000, event=1000, mixing=75, half_width=0,
                    proxy_count=8, date_count=8, overlap=8, dating_sigma=20,
                    age_rng=random.Random(1), proxy_rng=random.Random(2), date_rng=random.Random(3))
        for changed in ({'overlap': 9}, {'proxy_count': 0}, {'date_count': True},
                        {'prefix': ''}, {'dating_sigma': -1}):
            with self.assertRaises(ValueError):
                draw_sample(**(args | changed))

    def test_normal_survival_tail_and_small_mixing_limit(self):
        for z in (8, 10, 20, 30):
            expected = math.log(.5 * math.erfc(z / math.sqrt(2)))
            self.assertAlmostEqual(normal_log_survival(z), expected, places=10)
        self.assertTrue(math.isfinite(normal_log_survival(40)))
        density, young = date_density_and_young_fraction(0, 0, 0, 1e-10, 20)
        self.assertAlmostEqual(density, -math.log(20 * math.sqrt(2 * math.pi)), places=10)
        self.assertAlmostEqual(young, 1 - math.exp(-1), places=10)
        self.assertEqual(date_density_and_young_fraction(0, 0, 0, 0, 20)[1], 1)
        self.assertTrue(math.isfinite(date_density_and_young_fraction(-1000,1000,1000,75,20)[0]))

    def test_joint_measurement_density_against_direct_age_integration(self):
        focal, event, h, sigma = 1000, 1000, 75, 20
        lower = focal - h
        for measured in (900, 1000, 1100):
            log_density, fraction = date_density_and_young_fraction(measured, focal, event, h, sigma)
            exact_positive = math.exp(log_density) * (.1 + .8 * fraction)

            def integrand(age):
                exponential = math.exp(-(age - lower) / h) / h
                gaussian = math.exp(-.5 * ((measured - age) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
                return exponential * gaussian

            # Independent probability-space Simpson integration. Split at the
            # climate boundary so no numerical panel crosses a binary jump.
            def integrate(a, b, response):
                n = 10000
                step = (b - a) / n
                total = integrand(a) + integrand(b)
                total += math.fsum((4 if i % 2 else 2) * integrand(a + step * i) for i in range(1, n))
                return response * total * step / 3

            numerical = integrate(lower, event, .9) + integrate(event, lower + 20 * h, .1)
            self.assertAlmostEqual(exact_positive / numerical, 1, places=8)
            obs = {'dating_sigma_years': sigma,
                   'proxy_measurements': [{'specimen_id':'same', 'positive':True}],
                   'date_measurements': [{'specimen_id':'same', 'measured_age':measured}]}
            joint = sample_log_likelihood(obs, focal=focal, event=event, mixing=h, half_width=0)
            self.assertAlmostEqual(math.exp(joint), exact_positive, places=12)
            # Re-labelling the date as another specimen intentionally removes
            # the conditional dependence and gives the product of marginals.
            obs['date_measurements'][0]['specimen_id'] = 'different'
            independent = sample_log_likelihood(obs, focal=focal, event=event, mixing=h, half_width=0)
            marginal = .1 + .8 * mixed_fraction(focal, event, h)
            self.assertAlmostEqual(math.exp(independent), math.exp(log_density) * marginal, places=12)
            if measured == 900:
                self.assertGreater(math.exp(joint - independent), 1.4)

    def test_joint_likelihood_rejects_unsupported_or_duplicate_data(self):
        obs = {'dating_sigma_years': 20,
               'proxy_measurements': [{'specimen_id':'p', 'positive':True}],
               'date_measurements': [{'specimen_id':'d', 'measured_age':1000}]}
        parameters = dict(focal=1000,event=1000,mixing=75,half_width=0)
        self.assertTrue(math.isfinite(sample_log_likelihood(obs, **parameters)))
        with self.assertRaises(ValueError):
            sample_log_likelihood(obs, **(parameters | {'half_width':1}))
        obs['proxy_measurements'] *= 2
        with self.assertRaises(ValueError):
            sample_log_likelihood(obs, **parameters)

    def test_joint_prior_predictive_check_and_weak_marginal_control(self):
        result = joint_calibration()
        self.assertTrue(result['calibration']['joint']['pit_within_band'])
        # The deliberately factorized model also passes this coarse diagnostic.
        # Preserve that negative result rather than claiming sensitivity it lacks.
        self.assertTrue(result['calibration']['ignore_shared_ids']['pit_within_band'])
        self.assertGreater(result['truth_log_score_gain_mean'], .3)


if __name__ == '__main__':
    unittest.main()
