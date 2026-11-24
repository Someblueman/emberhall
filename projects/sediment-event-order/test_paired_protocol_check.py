"""Failure controls for the development-only protocol freeze."""
import copy
import io
import json
import subprocess
import unittest
from unittest.mock import patch

import paired_experiment as model
import paired_protocol_check as freeze


class FreezeTests(unittest.TestCase):
    def test_every_changed_frozen_input_refuses_acceptance(self):
        for name in freeze.PINS:
            hashes = dict(freeze.PINS, **{name: 'changed'})
            with patch.object(freeze, 'source_hashes', return_value=hashes):
                with self.assertRaisesRegex(ValueError, name.replace('.', r'\.')):
                    freeze.validate_freeze()

    def test_unlisted_protocol_change_is_also_rejected(self):
        protocol = model.protocol()
        protocol['event_prior'] = 'different law'
        with patch.object(model, 'protocol', return_value=protocol):
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                freeze.validate_freeze()

    def test_held_out_guard_prevents_generation_and_restores_stream(self):
        original = model.stream
        with freeze.development_only():
            with self.assertRaisesRegex(ValueError, 'forbids held-out'):
                model.generate('held-out', 1000)
            self.assertEqual(model.generate('development', 0)[0], model.generate('development', 0)[0])
        self.assertIs(model.stream, original)

    def test_paired_scenarios_share_truth_but_have_exact_declared_specimens(self):
        common = None
        for scenario, (proxies, dates, overlap) in model.SCENARIOS.items():
            public, oracle = model.generate('contract-test', 7, scenario)
            if common is not None:
                self.assertEqual(oracle.latent_draw, common)
            common = oracle.latent_draw
            for archive in public.archives:
                for layer in archive:
                    p = {r['specimen_id'] for r in layer['proxy_measurements']}
                    d = {r['specimen_id'] for r in layer['date_measurements']}
                    self.assertEqual((len(p), len(d), len(p & d)), (proxies, dates, overlap))
                    self.assertEqual(len(p | d), proxies+dates-overlap)
            for path in common.paths:
                self.assertTrue(all(a < b for a, b in zip(path.node_ages, path.node_ages[1:])))

    def test_failed_checks_skip_fitting_and_withhold_review_readiness(self):
        with patch.object(freeze, 'analytic_checks', return_value={'passed': False}), \
                patch.object(freeze, 'development_cases') as cases:
            report = freeze.preflight()
        cases.assert_not_called()
        self.assertEqual(report['status'], 'PREFLIGHT_FAILED')
        self.assertFalse(report['held_out_executed'])
        self.assertFalse(report['milestone_complete'])

    def test_numerical_failure_or_source_change_withholds_readiness(self):
        good = {s: {'diagnostic_passes': 1, 'source_changed_during_batch': False}
                for s in model.SCENARIOS}
        for change in ({'diagnostic_passes': 0}, {'source_changed_during_batch': True}):
            cases = copy.deepcopy(good)
            cases['date-rich'].update(change)
            with patch.object(freeze, 'analytic_checks', return_value={'passed': True}), \
                    patch.object(freeze, 'development_cases', return_value=cases):
                self.assertEqual(freeze.preflight()['status'], 'PREFLIGHT_FAILED')

    def test_requested_scenarios_retained_after_a_failed_fit(self):
        def batch(namespace, index, replicates, scenario, **settings):
            self.assertEqual((namespace, index, replicates, settings['particles']), ('development', 0, 1, 50000))
            return {'attempted': 1, 'diagnostic_passes': 0,
                    'records': [{'status': 'FAILED_TIME_BUDGET'}],
                    'source_changed_during_batch': False, 'elapsed_seconds': 0.}
        with patch.object(model, 'benchmark', side_effect=batch):
            result = freeze.development_cases()
        self.assertEqual(set(result), set(model.SCENARIOS))
        self.assertTrue(all(x['requested'] == 1 and x['diagnostic_passes'] == 0 for x in result.values()))

    def test_outer_timeout_returns_machine_readable_failure(self):
        output = io.StringIO()
        with patch('sys.argv', ['preflight']), patch('sys.stdout', output), \
                patch.object(freeze.subprocess, 'run', side_effect=subprocess.TimeoutExpired('worker', 180)):
            code = freeze.main()
        self.assertEqual(code, 1)
        result = json.loads(output.getvalue())
        self.assertEqual(result['status'], 'PREFLIGHT_FAILED')
        self.assertFalse(result['milestone_complete'])

    def test_outer_process_preserves_failed_worker_evidence(self):
        evidence = {'status': 'PREFLIGHT_FAILED', 'held_out_executed': False,
                    'development': {'balanced': {'diagnostic_passes': 0}}}
        child = subprocess.CompletedProcess([], 1, json.dumps(evidence), '')
        output = io.StringIO()
        with patch('sys.argv', ['preflight']), patch('sys.stdout', output), \
                patch.object(freeze.subprocess, 'run', return_value=child):
            self.assertEqual(freeze.main(), 1)
        self.assertEqual(json.loads(output.getvalue()), evidence)

    def test_manifest_does_not_draw_randomness_or_overstate_precision(self):
        with patch.object(model, 'stream', side_effect=AssertionError('no draws')):
            plan = freeze.validate_freeze()
        precision = plan['precision_and_denominators']
        self.assertEqual(precision['independent_latent_replicates'], 128)
        self.assertAlmostEqual(precision['coverage_se_at_0_90'], .02651650429)
        self.assertGreater(precision['zero_errors_upper_one_sided_95_if_128_declarations'], .02)
        self.assertFalse(plan['held_out']['executed_by_this_command'])
        self.assertEqual(len(plan['remaining_gaps']), 4)


if __name__ == '__main__':
    unittest.main()
