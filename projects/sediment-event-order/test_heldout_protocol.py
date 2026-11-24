"""Registration and denominator tests; never draw held-out observations."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import heldout_protocol as held


class RegistrationTests(unittest.TestCase):
    def test_manifest_draws_nothing(self):
        with patch.object(held.paired, 'stream', side_effect=AssertionError('draw')):
            manifest = held.registration()
        self.assertEqual(manifest['indices'], [1000, 1127])
        self.assertEqual(len(manifest['cases']), 5)
        self.assertEqual(manifest['particles'], 50000)

    def test_changed_manifest_or_source_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory)/'protocol.md'
            manifest = held.registration()
            document.write_text('```json\n'+json.dumps(manifest)+'\n```')
            sha = held.digest(manifest)
            held.validate_registration(sha, document)
            with self.assertRaisesRegex(ValueError, 'drift'):
                held.validate_registration('0'*64, document)
            with patch.object(held, 'registration', return_value=dict(manifest, particles=1000)):
                with self.assertRaisesRegex(ValueError, 'drift'):
                    held.validate_registration(sha, document)
            document.write_text('not registered')
            with self.assertRaisesRegex(ValueError, 'missing'):
                held.validate_registration(sha, document)

    def test_unregistered_draw_refused_before_randomness(self):
        with patch.object(held, 'validate_registration'), patch.object(held.paired, 'stream') as stream:
            for index in (999, 1128, True):
                with self.assertRaisesRegex(ValueError, 'unregistered'):
                    held.generate('sha', 'baseline', index=index)
            with self.assertRaises(ValueError):
                held.generate('sha', 'baseline', namespace='development', index=1000)
        stream.assert_not_called()

    def test_drift_blocks_generation_and_execution(self):
        with patch.object(held, 'validate_registration', side_effect=ValueError('drift')), \
             patch.object(held.paired, 'stream') as stream:
            with self.assertRaisesRegex(ValueError, 'drift'):
                held.generate('bad', 'baseline')
            with self.assertRaisesRegex(ValueError, 'drift'):
                held.execute_index(1000, 'bad')
        stream.assert_not_called()

    def test_failed_missing_and_duplicate_denominators(self):
        def row(index, status):
            return dict(index=index, case='baseline', scenario='balanced',
                method=held.METHODS[0], status=status, covered=True, wrong_order=False,
                squared_error=4., interval_width=5.)
        records = [row(1000, 'PASS_DIAGNOSTICS'), row(1001, 'FAILED_TIME_BUDGET'),
                   row(1002, 'MISSING_TIME_BUDGET')]
        result = held.summarize(records, (1000, 1001, 1002))
        self.assertEqual([result[k] for k in ('requested','attempted','passed','failed','missing')],
                         [90, 2, 1, 1, 88])
        s = result['strata']['baseline/balanced/paired-exponential']
        self.assertEqual(s['requested_coverage_identification_bounds'], [1/3, 1.])
        self.assertEqual(s['requested_wrong_declaration_bounds'], [0., 2/3])
        with self.assertRaises(ValueError):
            held.summarize(records+records[2:], (1000,1001,1002))
        with self.assertRaises(ValueError):
            held.summarize(records, (1000,))

    def test_pairing_uses_complete_passes_and_signed_differences(self):
        records = []
        for design, error, width in [('proxy-rich', 9., 50.), ('date-rich', 4., 30.)]:
            records.append(dict(index=1000, case='simultaneous', scenario=design,
                method=held.METHODS[0], status='PASS_DIAGNOSTICS', squared_error=error,
                interval_width=width, covered=True, wrong_order=None))
        result = held.summarize(records, (1000,1001))
        pair = result['comparisons']['simultaneous/paired-exponential/proxy-minus-date']
        self.assertEqual((pair['complete_pairs'], pair['incomplete_pairs']), (1,1))
        self.assertEqual(pair['squared_error']['mean'], 5.)
        self.assertEqual(pair['wrong_order']['mean'], 0.)
        self.assertEqual(pair['squared_error']['interval_95'], [-360000.,360000.])

    def test_uncertainty_empty_and_zero_errors(self):
        self.assertIsNone(held.wilson(0,0))
        self.assertAlmostEqual(held.wilson(0,1)[1], .7934506856)
        self.assertIsNone(held.bounded_mean([], -1,1)['mean'])
        with self.assertRaises(ValueError):
            held.bounded_mean([601], -600,600)

    def test_exclusive_reservation_survives_interruption(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(held, 'validate_registration'), \
             patch.object(held, 'execute_index', side_effect=RuntimeError('interrupted')) as execute:
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                held.run_once(1000, 'sha', directory)
            with self.assertRaises(FileExistsError):
                held.run_once(1000, 'sha', directory)
            self.assertEqual(execute.call_count, 1)
            saved = json.loads(next(Path(directory).glob('*.json')).read_text())
            self.assertEqual(saved['accounting']['missing'], 30)
            self.assertEqual(saved['accounting']['attempted'], 0)

    def test_fixed_particles_and_no_retry(self):
        with patch.object(held, 'validate_registration'):
            with self.assertRaises(ValueError):
                held.infer_gaussian('sha', held.paired.PublicObservation, particles=1000)
        failure = {'status':'FAILED_TIME_BUDGET','posterior':None}
        with patch.object(held, 'validate_registration'), \
             patch.object(held, 'generate', return_value=(object(), object())), \
             patch.object(held.paired, 'infer', return_value=failure) as primary, \
             patch.object(held, 'infer_gaussian', return_value=failure) as comparator, \
             patch.object(held.paired, 'evaluate', return_value={'covered':None}):
            report = held.execute_index(1000, 'sha')
        self.assertEqual((primary.call_count, comparator.call_count), (15,15))
        self.assertEqual(report['accounting']['failed'],30)
        self.assertEqual(report['accounting']['missing'],0)

    def test_aggregate_keeps_all_unexecuted_indices(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(held, 'validate_registration'):
            result = held.aggregate(directory, 'sha')
        self.assertEqual(result['accounting']['requested'], 3840)
        self.assertEqual(result['accounting']['missing'], 3840)
        self.assertEqual(result['accounting']['passed'], 0)

    def test_actual_file_hash_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'source.py').write_text('original')
            with patch.object(held, 'DIRECTORY', root), patch.object(held, 'PIN_FILES', ('source.py',)):
                manifest = held.registration()
                document = root/'protocol.md'
                document.write_text('```json\n'+json.dumps(manifest)+'\n```')
                (root/'source.py').write_text('changed')
                with self.assertRaisesRegex(ValueError, 'drift'):
                    held.validate_registration(held.digest(manifest), document)

    def test_simultaneous_false_declarations_both_signs(self):
        # No draw: construct a labelled oracle with equal latent event times.
        from types import SimpleNamespace
        oracle = held.paired.OracleEvaluation('ORACLE ONLY', SimpleNamespace(events=(900.,900.)), ())
        for probability in (.01,.99):
            result = {'posterior': {'delta_interval_90':[-5.,5.], 'delta_mean':0.,
                'probability_tau_b_older_than_a':probability}}
            self.assertTrue(held.paired.evaluate(result,oracle)['wrong_order'])


if __name__ == '__main__':
    unittest.main()
