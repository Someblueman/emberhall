"""Independent analytic/numerical checks for the development robustness extension."""
from dataclasses import replace
import math
import unittest
from unittest.mock import patch

import paired_experiment as paired
import robustness as robust
from chronology_model import AgeDepthPath


def normal_density(x, mean, sd):
    return math.exp(-.5*((x-mean)/sd)**2)/(sd*math.sqrt(2*math.pi))


def integrate(function, lo, hi, n=40000):
    step = (hi-lo)/n
    return step/3*(function(lo)+function(hi)+math.fsum(
        (4 if j % 2 else 2)*function(lo+j*step) for j in range(1, n)))


class Generators(unittest.TestCase):
    def test_baseline_exact_and_reproducible(self):
        for scenario in paired.SCENARIOS:
            actual = robust.generate('baseline', 'contract-test', 7, scenario)
            expected = paired.generate('contract-test', 7, scenario)
            self.assertEqual(actual[0].to_dict(), expected[0].to_dict())
            self.assertEqual(actual[1].latent_draw, expected[1].latent_draw)
            self.assertEqual(actual[1].specimen_ages, expected[1].specimen_ages)

    def test_simultaneity_and_paired_designs(self):
        for case in robust.CASES:
            draws = [robust.generate(case, 'contract-test', 9, s)[1].latent_draw
                     for s in paired.SCENARIOS]
            self.assertTrue(all(d == draws[0] for d in draws))
            if case == 'simultaneous':
                self.assertEqual(draws[0].events[0], draws[0].events[1])

    def test_misspecification_is_explicit_and_ancestry_valid(self):
        baseline, oracle = robust.generate('baseline', 'contract-test', 2)
        for case in robust.CASES[2:]:
            observation, changed = robust.generate(case, 'contract-test', 2)
            paired.validate_public(observation.to_dict())
            self.assertEqual(changed.latent_draw.paths, oracle.latent_draw.paths)
            self.assertEqual(changed.latent_draw.events, oracle.latent_draw.events)
            if case == 'mixing-x2':
                self.assertEqual(changed.latent_draw.mixing, tuple(2*h for h in oracle.latent_draw.mixing))
            if case == 'differential-offset-75':
                self.assertEqual(changed.specimen_ages, oracle.specimen_ages)
                for a in range(2):
                    for old, new in zip(baseline.archives[a], observation.archives[a]):
                        self.assertEqual(old['proxy_measurements'], new['proxy_measurements'])
                        for x, y in zip(old['date_measurements'], new['date_measurements']):
                            self.assertAlmostEqual(y['measured_age']-x['measured_age'], -75 if a == 0 else 75)
            self.assertNotEqual(baseline.to_dict(), observation.to_dict())

    def test_held_out_and_oracle_refused(self):
        for namespace, index in [('held-out', 1000), ('held-out', 0), ('development', 1000)]:
            with self.assertRaises(ValueError):
                robust.generate('baseline', namespace, index)
            with self.assertRaises(ValueError):
                robust.infer_gaussian(None, namespace, index)
        _, oracle = robust.generate('baseline')
        with self.assertRaises(ValueError):
            robust.infer_gaussian(oracle)
        with self.assertRaises(ValueError):
            robust.benchmark((1000,))


class GaussianLikelihood(unittest.TestCase):
    def layer(self, shared=True, positive=True):
        return {'dating_sigma_years': 30.,
                'proxy_measurements': [{'specimen_id': 'p', 'positive': positive}],
                'date_measurements': [{'specimen_id': 'p' if shared else 'd', 'measured_age': 1050.}]}

    def test_shared_specimen_integral_against_direct_quadrature(self):
        # Integrate the original latent A density, splitting at the binary step.
        for positive in (True, False):
            for offset in (-25., 35.):
                layer = self.layer(positive=positive)
                def density(age):
                    return normal_density(age, 1000., 50.)*normal_density(1050., age+offset, 30.)
                below = integrate(density, 500., 1010.)
                above = integrate(density, 1010., 1500.)
                expected = (.9*below+.1*above) if positive else (.1*below+.9*above)
                actual = robust.gaussian_layer_log_likelihood(layer,
                    focal=1000., event=1010., mixing=50., calibration=offset)
                self.assertAlmostEqual(math.exp(actual), expected, places=12)

    def test_unshared_factorization_and_ancestry_matters(self):
        layer = self.layer(shared=False)
        expected = normal_density(1050., 1000., math.hypot(50, 30))*.5
        actual = robust.gaussian_layer_log_likelihood(layer,
            focal=1000., event=1000., mixing=50., calibration=0.)
        self.assertAlmostEqual(math.exp(actual), expected, places=14)
        shared = robust.gaussian_layer_log_likelihood(self.layer(),
            focal=1000., event=1000., mixing=50., calibration=0.)
        self.assertGreater(abs(actual-shared), .2)

    def test_proxy_complements_sum_to_date_density(self):
        values = [math.exp(robust.gaussian_layer_log_likelihood(self.layer(positive=b),
            focal=1000., event=1010., mixing=50., calibration=20.)) for b in (False, True)]
        self.assertAlmostEqual(sum(values), normal_density(1050., 1020., math.hypot(50, 30)), places=14)

    def test_zero_mixing_and_common_offset(self):
        result = robust.gaussian_layer_log_likelihood(self.layer(),
            focal=1000., event=1000., mixing=0., calibration=50.)
        self.assertAlmostEqual(math.exp(result), .9*normal_density(1050., 1050., 30.), places=14)
        observation, oracle = robust.generate('baseline', 'contract-test', 3)
        draw = oracle.latent_draw
        # Shift all dates and the candidate COMMON offset by the same amount.
        moved = observation.to_dict()
        for archive in moved['archives']:
            for layer in archive:
                for date in layer['date_measurements']:
                    date['measured_age'] += 70.
        self.assertAlmostEqual(robust.gaussian_log_likelihood(observation, draw),
            robust.gaussian_log_likelihood(paired.PublicObservation.from_dict(moved),
                replace(draw, calibration=draw.calibration+70.)), places=10)

    def test_public_boundary_revalidates_mutated_ancestry(self):
        observation, _ = robust.generate('baseline')
        observation.archives[0][0]['date_measurements'][0]['specimen_id'] = 'foreign'
        with self.assertRaises(ValueError):
            robust.infer_gaussian(observation, particles=1000)

    def test_common_offset_marginal_matches_bivariate_normal(self):
        # Dates only, so the offset integral has an independent analytic answer.
        layers = [{'dating_sigma_years': 30., 'proxy_measurements': [],
                   'date_measurements': [{'specimen_id': 'd', 'measured_age': d}]}
                  for d in (1050., 950.)]
        def conditional(offset):
            return normal_density(offset, 0., 50.)*math.exp(math.fsum(
                robust.gaussian_layer_log_likelihood(layer, focal=1000.,
                    event=1000., mixing=40., calibration=offset) for layer in layers))
        actual = integrate(conditional, -500., 500.)
        variance, covariance = 5000., 2500.
        determinant = variance**2-covariance**2
        x, y = 50., -50.
        quadratic = (variance*(x*x+y*y)-2*covariance*x*y)/determinant
        expected = math.exp(-quadratic/2)/(2*math.pi*math.sqrt(determinant))
        self.assertAlmostEqual(actual, expected, places=14)
        independent = normal_density(x, 0., math.sqrt(variance))*normal_density(y, 0., math.sqrt(variance))
        self.assertGreater(abs(actual-independent), 1e-6)


class AccountingAndNumerics(unittest.TestCase):
    def test_exponential_event_proposal_corrects_to_gaussian_target(self):
        # Fix nuisance parameters. Direct event quadrature is independent of q.
        observation, _ = robust.generate('baseline', 'contract-test', 42)
        path = AgeDepthPath((0., 1., 2., 3.), (800., 930., 1060., 1190.))
        candidate = paired.JointDraw((path, path), (1000., 1000.), 0., (45., 65.))
        def grid(n):
            ages = [850+(i+.5)*300/n for i in range(n)]
            margins = []
            for a in range(2):
                logw = [sum(robust.gaussian_layer_log_likelihood(layer,
                    focal=path.age_at(layer['depth_cm']), event=tau,
                    mixing=candidate.mixing[a], calibration=0.)
                    for layer in observation.archives[a]) for tau in ages]
                peak = max(logw)
                weights = [math.exp(w-peak) for w in logw]
                norm = sum(weights)
                margins.append([w/norm for w in weights])
            means = [sum(x*w for x, w in zip(ages, weights)) for weights in margins]
            cdf, probability = 0., 0.
            for wa, wb in zip(*margins):
                probability += wb*cdf
                cdf += wa
            return means[1]-means[0], probability
        coarse, fine = grid(2000), grid(4000)
        self.assertLess(abs(coarse[0]-fine[0]), .001)
        self.assertLess(abs(coarse[1]-fine[1]), .001)
        rows = []
        for batch in range(2):
            rng = paired.stream('contract-test', 42, f'conditional-gaussian-check/{batch}')
            for _ in range(10000):
                draw, correction = paired.propose_events(observation, candidate, rng)
                rows.append((*draw.events, robust.gaussian_log_likelihood(observation, draw)+correction))
        summary = paired.weighted_summary(rows)
        self.assertLess(abs(summary['delta_mean']-fine[0]), 5*summary['delta_mcse'])
        self.assertLess(abs(summary['probability_tau_b_older_than_a']-fine[1]),
                        5*summary['order_probability_mcse'])

    def test_failures_missing_and_paired_indices(self):
        records = [dict(index=0, case='baseline', scenario=s, method=m,
                        status='PASS_DIAGNOSTICS' if s == 'proxy-rich' else 'FAILED_TIME_BUDGET')
                   for s in ('proxy-rich', 'date-rich') for m in robust.METHODS]
        result = robust.accounting(records, (0, 1), ('baseline',))
        self.assertEqual((result['requested'], result['attempted'], result['passed'],
                          result['failed'], result['missing']), (12, 4, 2, 2, 8))
        self.assertEqual(result['paired_budget_designs']['baseline/gaussian-material']['complete_indices'], [])
        self.assertEqual(result['paired_methods']['baseline/proxy-rich']['complete_indices'], [0])
        self.assertEqual(result['paired_methods']['baseline/date-rich']['incomplete'], 2)
        self.assertEqual(result['strata']['baseline/balanced/gaussian-material']['missing'], 2)
        with self.assertRaises(ValueError):
            robust.accounting(records+records[:1], (0, 1), ('baseline',))
        with self.assertRaises(ValueError):
            robust.accounting(records, (1,), ('baseline',))

    def test_simultaneous_declaration_is_false_either_direction(self):
        _, oracle = robust.generate('simultaneous')
        for probability in (.99, .01):
            result = {'posterior': {'delta_interval_90': [-10., 10.],
                'delta_mean': 0., 'probability_tau_b_older_than_a': probability}}
            self.assertTrue(paired.evaluate(result, oracle)['wrong_order'])
        result['posterior']['probability_tau_b_older_than_a'] = .5
        self.assertIsNone(paired.evaluate(result, oracle)['wrong_order'])

    def test_joint_rows_preserve_delta_dependence(self):
        # Perfectly coupled event times imply delta=0, even with broad marginals.
        rows = [(850.+i, 850.+i, 0.) for i in range(200)]
        result = robust.summarize_batches([rows, rows])
        self.assertEqual(result['status'], 'PASS_DIAGNOSTICS')
        self.assertEqual(result['posterior']['delta_interval_90'], [0., 0.])
        self.assertEqual(result['posterior']['tau_covariance'], (200**2-1)/12)

    def test_tiny_budget_reports_failure(self):
        observation, _ = robust.generate('baseline')
        result = robust.infer_gaussian(observation, particles=1000, seconds=1e-12)
        self.assertEqual(result['status'], 'FAILED_TIME_BUDGET')
        self.assertIsNone(result['posterior'])
        for particles in (999, 1001, 50002):
            with self.assertRaises(ValueError):
                robust.infer_gaussian(observation, particles=particles)

    def test_no_hidden_retry_and_requested_denominator(self):
        failure = {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
        with patch.object(paired, 'infer', return_value=failure) as primary, \
             patch.object(robust, 'infer_gaussian', return_value=failure) as comparator:
            report = robust.benchmark((0,), ('simultaneous',), particles=1000)
        self.assertEqual(primary.call_count, 3)
        self.assertEqual(comparator.call_count, 3)
        self.assertEqual(report['accounting']['failed'], 6)
        self.assertEqual(report['accounting']['missing'], 0)
        self.assertTrue(all(r['covered'] is None for r in report['records']))

    def test_frozen_drift_refused_before_generation(self):
        with patch.object(robust.frozen, 'validate_freeze', side_effect=ValueError('drift')), \
             patch.object(robust, 'generate') as generate:
            with self.assertRaisesRegex(ValueError, 'drift'):
                robust.benchmark()
        generate.assert_not_called()

    def test_comparator_executes_only_contract_streams(self):
        observation, _ = robust.generate('baseline', 'contract-test', 12)
        original = paired.stream
        roles = []
        def fenced_stream(namespace, index, role):
            self.assertEqual((namespace, index), ('contract-test', 12))
            roles.append(role)
            return original(namespace, index, role)
        with patch.object(paired, 'stream', side_effect=fenced_stream):
            result = robust.infer_gaussian(observation, 'contract-test', 12, particles=1000)
        self.assertEqual(len(roles), 2)
        self.assertIn(result['status'], ('PASS_DIAGNOSTICS', 'FAILED_IMPORTANCE_DIAGNOSTICS'))
        self.assertEqual(result['particles'], 1000)


if __name__ == '__main__':
    unittest.main()
