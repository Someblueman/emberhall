import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from convergence import aggregate, run, perfect_recovery, METRICS, KEYS


def scores(value):
    return {m: {k: value for k in KEYS} for m in METRICS}


class ConvergenceChecks(unittest.TestCase):
    def test_perfect_observations_do_not_imply_population_certainty(self):
        rows = [dict(community=c, scores=scores(1.)) for c in range(12) for _ in range(2)]
        result = perfect_recovery(rows)['coherence']
        self.assertEqual(result['communities'], 12)
        self.assertEqual(result['successes'], 12)
        self.assertAlmostEqual(result['exact_ci95'][0], .025**(1/12))
        self.assertEqual(result['exact_ci95'][1], 1.)
        rows[0]['scores']['coherence']['single_linkage_guild_auc'] = .99
        result = perfect_recovery(rows)['coherence']
        self.assertEqual(result['successes'], 11)
        self.assertLess(result['exact_ci95'][1], 1.)

    def test_uncertainty_unit_is_community_not_drive(self):
        records = [dict(community=c, scores=scores(v))
                   for c, v in [(0, 0), (0, 2), (1, 5), (1, 7)]]
        result = aggregate(records, 'scores')['coherence']['overlap_spearman']
        self.assertEqual(result['n'], 2)
        self.assertEqual(result['mean'], 3.5)
        # Paired drives give community means 1 and 6, hence SE = 2.5.
        from scipy.stats import t
        self.assertAlmostEqual(result['ci95'][1], 3.5 + t.ppf(.975, 1)*2.5)

    def test_failures_retained_and_incomplete_communities_excluded(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / 'experiment'
            # One failed drive makes its otherwise successful community incomplete.
            rng = np.random.default_rng(7)
            x = rng.normal(size=(480, 6))
            calls = [(x, .1)] * 3 + [ValueError('witnessed failure')] + [(x, .1)] * 6
            with patch('convergence.simulate', side_effect=calls):
                report = run(target, communities=2, drives=2, duration=512, burn=32)
            self.assertEqual(report['attempted'], 4)
            self.assertEqual(report['successful'], 3)
            self.assertEqual(report['complete_communities'], 1)
            self.assertEqual(report['failures'][0]['community'], 0)
            self.assertIn('witnessed failure', (target / 'failures.json').read_text())
            self.assertEqual(report['summaries']['scores']['cpsd']['same_diet_pair_auc']['n'], 1)
            self.assertIsNone(report['summaries']['scores']['cpsd']['same_diet_pair_auc']['ci95'])
            with self.assertRaises(ValueError):
                run(target)
            with patch('convergence.simulate', side_effect=AssertionError('must not rerun')):
                resumed = run(target, communities=2, drives=2, duration=512, burn=32, resume=True)
            self.assertTrue(resumed['complete'])
            self.assertEqual(resumed['completed_attempts'], 4)
            with self.assertRaisesRegex(ValueError, 'configuration differs'):
                run(target, communities=3, drives=2, duration=512, burn=32, resume=True)

    def test_bounded_resume_keeps_original_seed_schedule(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / 'experiment'
            x = np.random.default_rng(9).normal(size=(480, 6))
            with patch('convergence.simulate', return_value=(x, .1)):
                first = run(target, communities=2, duration=512, burn=32, max_attempts=1)
                second = run(target, communities=2, duration=512, burn=32, max_attempts=1, resume=True)
            self.assertFalse(first['complete'])
            self.assertEqual(first['complete_communities'], 0)
            self.assertEqual(second['completed_attempts'], 2)
            self.assertFalse(second['candidate_stable'])
            with patch('convergence.simulate', side_effect=AssertionError('report must not simulate')):
                snapshot = run(target, communities=2, duration=512, burn=32, resume=True, report_only=True)
            self.assertEqual(snapshot['completed_attempts'], 2)
            import json
            rows = [json.loads(line) for line in (target/'records.jsonl').read_text().splitlines()]
            self.assertEqual([r['input_seed'] for r in rows], [200000, 200001])


if __name__ == '__main__':
    unittest.main()
