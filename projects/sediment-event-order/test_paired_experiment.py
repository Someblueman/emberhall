"""Independent checks of the paired experiment's scientific boundaries."""
import copy
from dataclasses import replace
import math
import random
import tracemalloc
import unittest
from unittest.mock import patch

import paired_experiment as paired
from chronology_model import AgeDepthPath


def integrate(function, left=-500., right=500., cells=2000):
    step = (right-left)/cells
    return step/3 * math.fsum((1 if i in (0, cells) else 4 if i % 2 else 2)
                              * function(left+i*step) for i in range(cells+1))


def gaussian_rank_one(residuals, sigma, shared_sd):
    """Independent determinant-lemma / Sherman-Morrison normal density."""
    n = len(residuals)
    v, c = sigma*sigma, shared_sd*shared_sd
    logdet = (n-1)*math.log(v)+math.log(v+n*c)
    quadratic = math.fsum(r*r for r in residuals)/v - c*sum(residuals)**2/(v*(v+n*c))
    return math.exp(-.5*(n*math.log(2*math.pi)+logdet+quadratic))


class PairedTests(unittest.TestCase):
    def setUp(self):
        self.public, self.oracle = paired.generate()

    def test_reproducible_namespaces_and_monotone_paths(self):
        public, oracle = paired.generate()
        self.assertEqual(public.to_dict(), self.public.to_dict())
        self.assertEqual(oracle, self.oracle)
        self.assertNotEqual(paired.generate('contract-test')[0].to_dict(), public.to_dict())
        for path in oracle.latent_draw.paths:
            self.assertTrue(all(x < y for x, y in zip(path.node_ages, path.node_ages[1:])))
        for namespace, index in [('other', 0), ('development', -1), ('held-out', True), ('held-out', 0)]:
            with self.assertRaises(ValueError):
                paired.generate(namespace, index)

    def test_truth_allowlist_at_every_level(self):
        for where, key in [('top', 'tau'), ('layer', 'true_age'), ('row', 'true_age')]:
            value = self.public.to_dict()
            target = value if where == 'top' else value['archives'][0][0]
            if where == 'row':
                target = target['date_measurements'][0]
            target[key] = 1000.
            with self.assertRaises(ValueError):
                paired.PublicObservation.from_dict(value)
        for invalid in (self.oracle, self.oracle.latent_draw, self.public.to_dict()):
            with self.assertRaises(ValueError):
                paired.infer(invalid, particles=1000)
        # Even bypassing the parser with the constructor cannot inject truth.
        bad = copy.deepcopy(self.public)
        bad.archives[0][0]['tau'] = 1000.
        with self.assertRaises(ValueError):
            paired.infer(bad, particles=1000)

    def test_ancestry_cannot_be_changed_or_moved_between_archives(self):
        for mutation in ('detach_shared', 'swap_archive', 'duplicate', 'rename_both'):
            value = self.public.to_dict()
            layer = value['archives'][0][0]
            dates = layer['date_measurements']
            if mutation == 'detach_shared':
                dates[0]['specimen_id'] += ':detached'
            elif mutation == 'swap_archive':
                value['archives'] = tuple(reversed(value['archives']))
            elif mutation == 'duplicate':
                dates[0]['specimen_id'] = dates[1]['specimen_id']
            else:
                dates[0]['specimen_id'] = 'forged'
                layer['proxy_measurements'][0]['specimen_id'] = 'forged'
            with self.assertRaises(ValueError, msg=mutation):
                paired.PublicObservation.from_dict(value)

    def test_observation_export_is_defensive(self):
        value = self.public.to_dict()
        value['archives'][0][0]['date_measurements'][0]['measured_age'] += 900.
        self.assertNotEqual(value, self.public.to_dict())
        self.assertNotIn('true_age', str(self.public.to_dict()))
        self.assertNotIn('calibration', str(self.public.to_dict()))

    def test_joint_likelihood_against_analytic_integrated_shared_offset(self):
        # Zero-mixing limit: all specimen ages are fixed. Every date shares c,
        # so after integrating c the covariance is sigma² I + CAL_SD² 11'.
        # This checks the actual paired likelihood, not its normal helpers.
        paths = (AgeDepthPath(paired.DEPTHS, (800., 930., 1060., 1190.)),)*2
        candidate = paired.JointDraw(paths, (1000., 1000.), 0., (0., 0.))
        value = self.public.to_dict()
        residuals, proxy_likelihood = [], 1.
        by_archive = []
        for a, layers in enumerate(value['archives']):
            local = []
            for z, layer in enumerate(layers):
                age = paths[a].node_ages[z]
                for row in layer['date_measurements']:
                    residual = 35.+(z-1.5)*12.+a*7.
                    row['measured_age'] = age+residual
                    residuals.append(residual)
                    local.append(residual)
                p = .9 if age <= 1000. else .1
                for row in layer['proxy_measurements']:
                    proxy_likelihood *= p if row['positive'] else 1-p
            by_archive.append(local)
        observation = paired.PublicObservation.from_dict(value)
        exact = gaussian_rank_one(residuals, paired.DATE_SD, paired.CAL_SD)*proxy_likelihood
        prior = lambda c: math.exp(-.5*(c/paired.CAL_SD)**2)/(paired.CAL_SD*math.sqrt(2*math.pi))
        numerical = integrate(lambda c: prior(c)*math.exp(paired.joint_log_likelihood(
            observation, replace(candidate, calibration=c))))
        self.assertAlmostEqual(numerical/exact, 1., places=10)
        # Destroying shared pairing preserves each archive's marginal covariance,
        # but replaces one common offset with independent offsets. It must fail
        # the same joint oracle, rather than silently pass as paired inference.
        unpaired = math.prod(gaussian_rank_one(rs, paired.DATE_SD, paired.CAL_SD)
                             for rs in by_archive)*proxy_likelihood
        self.assertGreater(abs(unpaired/exact-1), .1)

    def test_nonzero_mixing_shared_specimen_likelihood_independent_quadrature(self):
        # One shared specimen per layer, all other observations retain their law.
        # Independently integrate its exponentially distributed material age.
        layer = self.public.archives[0][1]
        key = layer['date_measurements'][0]['specimen_id']
        proxy = next(r['positive'] for r in layer['proxy_measurements'] if r['specimen_id'] == key)
        date = layer['date_measurements'][0]['measured_age']
        focal, event, h, offset = 950., 1000., 45., 25.
        from material_model import sample_log_likelihood
        one = dict(layer, proxy_measurements=[{'specimen_id': key, 'positive': proxy}],
                   date_measurements=[{'specimen_id': key, 'measured_age': date-offset}])
        actual = math.exp(sample_log_likelihood(one, focal=focal, event=event, mixing=h, half_width=0))
        def density(age, young):
            p = .9 if young else .1
            return math.exp(-(age-focal+h)/h)/h * (p if proxy else 1-p) * math.exp(
                -.5*((date-offset-age)/paired.DATE_SD)**2)/(paired.DATE_SD*math.sqrt(2*math.pi))
        lower = focal-h
        reference = integrate(lambda age: density(age, True), lower, event, 1000)
        reference += integrate(lambda age: density(age, False), event, lower+40*h, 4000)
        self.assertAlmostEqual(actual/reference, 1., places=8)

    def test_ordering_uses_joint_weights_not_product_of_marginals(self):
        rows = [(0., 10., 0.), (100., 110., 0.), (200., 210., 0.)]
        summary = paired.weighted_summary(rows)
        self.assertEqual(summary['delta_mean'], 10.)
        self.assertEqual(summary['delta_sd'], 0.)
        self.assertEqual(summary['probability_tau_b_after_a'], 1.)
        shuffled = [(a, b, 0.) for a, b in zip((0., 100., 200.), (110., 210., 10.))]
        # Identical A and B marginals, different event ordering distribution.
        broken = paired.weighted_summary(shuffled)
        self.assertEqual(summary['tau_means'], broken['tau_means'])
        self.assertGreater(broken['delta_sd'], 100.)
        self.assertLess(broken['probability_tau_b_after_a'], 1.)

    def test_importance_correction_against_independent_event_integration(self):
        # Fixed-nuisance small case: independently integrate each event over
        # physical time. Both proposal algorithms must recover this same law.
        fixed = self.oracle.latent_draw
        from material_model import sample_log_likelihood
        exact_means = []
        for a, layers in enumerate(self.public.archives):
            def likelihood(tau):
                total = 0.
                for layer in layers:
                    shifted = dict(layer, date_measurements=[dict(r,
                        measured_age=r['measured_age']-fixed.calibration)
                        for r in layer['date_measurements']])
                    total += sample_log_likelihood(shifted,
                        focal=fixed.paths[a].age_at(layer['depth_cm']), event=tau,
                        mixing=fixed.mixing[a], half_width=0.)
                return math.exp(total)
            evidence = integrate(likelihood, 850., 1150., 1000)
            exact_means.append(integrate(lambda t: t*likelihood(t), 850., 1150., 1000)/evidence)
        def fixed_nuisance(rng):
            return replace(fixed, events=(rng.uniform(850., 1150.), rng.uniform(850., 1150.)))
        with patch.object(paired, 'prior_draw', side_effect=fixed_nuisance):
            for proposal in ('prior', 'proxy-grid'):
                result = paired.infer(self.public, particles=4000, proposal=proposal)
                self.assertEqual(result['status'], 'PASS_DIAGNOSTICS')
                posterior = result['posterior']
                self.assertLess(abs(posterior['delta_mean']-(exact_means[1]-exact_means[0])),
                                5*posterior['delta_mcse'])
                for actual, exact in zip(posterior['tau_means'], exact_means):
                    self.assertLess(abs(actual-exact), 5.)

    def test_joint_chronology_proposal_density_by_collapsing_surface_ages(self):
        candidate = self.oracle.latent_draw
        proposed, correction = paired.propose_chronology(self.public, candidate, random.Random(21))
        # Independent scalar-normal derivation: collapse each surface age,
        # infer common c, then condition each surface on c. No matrix helper.
        residuals, variances = [], []
        for a, layers in enumerate(self.public.archives):
            weights, values = [], []
            for layer in layers:
                dates = layer['date_measurements']
                weights.append(len(dates)/(paired.DATE_SD**2+candidate.mixing[a]**2))
                increment = candidate.paths[a].age_at(layer['depth_cm'])-candidate.paths[a].node_ages[0]
                values.append(sum(d['measured_age'] for d in dates)/len(dates)-increment-800.)
            variances.append(1/sum(weights))
            residuals.append(sum(w*v for w, v in zip(weights, values))/sum(weights))
        cvar = 1/(1/paired.CAL_SD**2+sum(1/(35.**2+v) for v in variances))
        cmean = cvar*sum(r/(35.**2+v) for r, v in zip(residuals, variances))
        def lognormal(x, mean, variance):
            return -.5*(math.log(2*math.pi*variance)+(x-mean)**2/variance)
        c = proposed.calibration
        logq = lognormal(c, cmean, cvar)
        logp = lognormal(c, 0., paired.CAL_SD**2)
        for a in range(2):
            var = 1/(1/35.**2+1/variances[a])
            mean = 800.+var*(residuals[a]-c)/variances[a]
            age = proposed.paths[a].node_ages[0]
            logq += lognormal(age, mean, var)
            logp += lognormal(age, 800., 35.**2)
            before = candidate.paths[a].node_ages
            after = proposed.paths[a].node_ages
            for b, d in zip(before, after):
                self.assertAlmostEqual(b-before[0], d-after[0])
        self.assertAlmostEqual(correction, logp-logq, places=11)

    def test_configured_particle_storage_fits_memory_budget(self):
        tracemalloc.start()
        try:
            rows = [(850.+i % 300, 850.+(i*7) % 300, -float(i % 10))
                    for i in range(paired.MAX_PARTICLES)]
            paired.weighted_summary(rows)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 32*1024*1024)

    def test_calibration_harness_keeps_failed_cases(self):
        failed = {'status': 'FAILED_IMPORTANCE_DIAGNOSTICS', 'posterior': None}
        with patch.object(paired, 'infer', return_value=failed):
            report = paired.benchmark('contract-test', 0, 3, 'balanced', particles=1000)
        self.assertEqual(report['requested'], 3)
        self.assertEqual(report['attempted'], 3)
        self.assertEqual(report['diagnostic_passes'], 0)
        self.assertIsNone(report['coverage_among_passes'])
        self.assertEqual(report['covered_fraction_all_requested'], 0.)
        self.assertTrue(all(r['covered'] is None for r in report['records']))
        with self.assertRaises(ValueError):
            paired.benchmark('contract-test', 0, 17, 'balanced')

    def test_prior_only_negative_control_ignores_observed_information(self):
        altered = self.public.to_dict()
        for a, layers in enumerate(altered['archives']):
            for layer in layers:
                for row in layer['proxy_measurements']:
                    row['positive'] = (a == 0)
        other = paired.PublicObservation.from_dict(altered)
        self.assertEqual(paired.observed_group(other), 'A_more_positive')
        left = paired.prior_only_control(self.public, 'contract-test', 0, 2000)
        right = paired.prior_only_control(other, 'contract-test', 0, 2000)
        self.assertEqual(left, right)
        self.assertEqual(paired.evaluate(left, self.oracle)['order'], 'unresolved')
        self.assertIsNotNone(paired.evaluate(left, self.oracle)['approximate_pit'])

    def test_optional_ensemble_contains_paired_candidates_and_prospective_contract(self):
        result = paired.infer(self.public, particles=4000, retain_ensemble=True)
        self.assertEqual(result['status'], 'PASS_DIAGNOSTICS')
        self.assertEqual(len(result['ensemble']), 4000)
        for a, b, logweight in result['ensemble']:
            self.assertTrue(850. <= a <= 1150. and 850. <= b <= 1150.)
            self.assertTrue(math.isfinite(logweight))
        order = 1-paired.weighted_cdf(result['ensemble'], 0.)
        self.assertAlmostEqual(order, result['posterior']['probability_tau_b_after_a'])
        self.assertEqual(paired.protocol()['held_out_indices'], [1000, 1127])
        # Reject altered held-out budgets before drawing any held-out case.
        with self.assertRaises(ValueError):
            paired.infer(self.public, 'held-out', 1000, particles=4000)
        with self.assertRaises(ValueError):
            paired.stream('held-out', 1128, 'truth')

    def registered_fixture(self):
        # Synthetic accounting fixture ONLY, not execution on held-out seeds.
        failed = {'status': 'FAILED_IMPORTANCE_DIAGNOSTICS', 'posterior': None}
        with patch.object(paired, 'infer', return_value=failed):
            report = paired.benchmark('contract-test', 0, 3, 'balanced',
                                      particles=paired.REGISTERED_PARTICLES)
        report.update(namespace='held-out', first_index=1000)
        for i, row in enumerate(report['records']):
            row['index'] = 1000+i
        return report

    def test_registered_accounting_preserves_missing_and_failed_cases(self):
        report = self.registered_fixture()
        summary = paired.aggregate_registered([report])
        self.assertEqual(summary['status'], 'INCOMPLETE')
        self.assertEqual(summary['scenarios']['balanced']['numerical_failures'], 3)
        self.assertEqual(summary['scenarios']['balanced']['missing_indices'], list(range(1003, 1128)))
        self.assertEqual(len(summary['scenarios']['proxy-rich']['missing_indices']), 128)
        self.assertIsNone(summary['scenarios']['balanced']['coverage_among_passes'])

    def test_registered_accounting_rejects_duplicates_and_changed_contracts(self):
        report = self.registered_fixture()
        with self.assertRaises(ValueError):
            paired.aggregate_registered([report, report])
        mutations = ({'namespace': 'development'}, {'particles': 12000},
                     {'source_changed_during_batch': True}, {'control': 'prior-only'},
                     {'provenance': {}}, {'attempted': 2})
        for changes in mutations:
            bad = copy.deepcopy(report)
            bad.update(changes)
            with self.assertRaises(ValueError, msg=str(changes)):
                paired.aggregate_registered([bad])
        bad = copy.deepcopy(report)
        bad['records'][0]['covered'] = True
        with self.assertRaises(ValueError):
            paired.aggregate_registered([bad])

    def test_registered_total_budget_cannot_be_hidden_by_partial_results(self):
        report = self.registered_fixture()
        report['elapsed_seconds'] = paired.REGISTERED_TOTAL_SECONDS+1
        self.assertEqual(paired.aggregate_registered([report])['status'], 'FAILED_TOTAL_BUDGET')

    def test_complete_accounting_never_means_failed_inference_is_calibrated(self):
        template = self.registered_fixture()
        reports = []
        for scenario in paired.SCENARIOS:
            for first in range(1000, 1128, 16):
                report = copy.deepcopy(template)
                report.update(scenario=scenario, first_index=first, requested=16, attempted=16)
                row = report['records'][0]
                report['records'] = [dict(row, index=i) for i in range(first, first+16)]
                reports.append(report)
        summary = paired.aggregate_registered(reports)
        self.assertEqual(summary['status'], 'COMPLETE_ACCOUNTING')
        self.assertFalse(summary['numerically_complete'])
        for result in summary['scenarios'].values():
            self.assertEqual(result['numerical_failures'], 128)
            self.assertEqual(result['missing_indices'], [])
            self.assertIsNone(result['coverage_among_passes'])

    def test_batch_detects_source_change_without_pooling_it(self):
        signature = paired.provenance()
        changed = dict(signature, python='changed-during-test')
        failed = {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
        with patch.object(paired, 'provenance', side_effect=[signature, changed]), \
                patch.object(paired, 'infer', return_value=failed):
            report = paired.benchmark('contract-test', 0, 2, 'balanced')
        self.assertTrue(report['source_changed_during_batch'])

    def test_budget_and_diagnostic_failures_withhold_posterior(self):
        for n in (999, 50001, True):
            with self.assertRaises(ValueError):
                paired.infer(self.public, particles=n)
        with self.assertRaises(ValueError):
            paired.infer(self.public, seconds=21)
        result = paired.infer(self.public, particles=1000, seconds=1e-12)
        self.assertEqual(result['status'], 'FAILED_TIME_BUDGET')
        self.assertIsNone(result['posterior'])
        with patch.object(paired, 'joint_log_likelihood', return_value=math.nan):
            self.assertEqual(paired.infer(self.public, particles=1000)['status'], 'FAILED_NONFINITE')
        # An extremely concentrated importance sample cannot be reported as fit.
        with patch.object(paired, 'joint_log_likelihood', side_effect=lambda o, c: c.events[0]*1000):
            result = paired.infer(self.public, particles=1000)
        self.assertEqual(result['status'], 'FAILED_IMPORTANCE_DIAGNOSTICS')
        self.assertIsNone(result['posterior'])

    def test_runnable_inference_and_controls(self):
        result = paired.infer(self.public, particles=4000)
        self.assertEqual(result['status'], 'PASS_DIAGNOSTICS')
        self.assertGreater(result['posterior']['ess'], 200)
        self.assertEqual(len(paired.gaussian_control(self.public)['archives']), 2)
        control = paired.fixed_chronology_control(self.public)
        self.assertTrue(all(a['numerical_status'] == 'PASS' for a in control['archives']))

    def test_all_frozen_count_scenarios_generate_and_score(self):
        for scenario, (p, d, overlap) in paired.SCENARIOS.items():
            observation, oracle = paired.generate(scenario=scenario)
            layer = observation.archives[0][0]
            self.assertEqual(len(layer['proxy_measurements']), p)
            self.assertEqual(len(layer['date_measurements']), d)
            self.assertEqual(len(oracle.specimen_ages), 8*(p+d-overlap))
            self.assertTrue(math.isfinite(paired.joint_log_likelihood(observation, oracle.latent_draw)))


if __name__ == '__main__':
    unittest.main()
