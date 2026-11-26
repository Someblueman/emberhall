import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from convergence import METRICS, TARGETS, protocol, run, summarize
from reference import ou


class ConvergenceChecks(unittest.TestCase):
    def test_subsampled_ou_has_correct_coarse_stationary_transition(self):
        q = ou(887, 8192, spacing=.0625)[::4] - np.r_[np.ones(24), np.full(6, 3)]
        innovation = q[1:] - np.exp(-.25) * q[:-1]
        expected = .005 * (1-np.exp(-.5))
        np.testing.assert_allclose(innovation.var(0), expected, rtol=.05)
        self.assertLess(np.max(np.abs(np.corrcoef(innovation.T)-np.eye(30))), .03)

    def test_perfect_observed_scores_do_not_imply_population_certainty(self):
        values = {m: {k: 1.0 for k in TARGETS} for m in METRICS}
        zero = {m: {k: 0.0 for k in TARGETS} for m in METRICS}
        records = [dict(seed=i, status='success', scores={'0.0625': {'30': values}},
                        finest_forcing_delta=zero, length_delta=zero, solver_delta=zero)
                   for i in range(12)]
        result = summarize(records, protocol(range(12), 4608, 512))
        s = result['summaries']['coherence']['single_linkage_guild_auc']
        self.assertEqual(s['ci95'], [1, 1])
        self.assertLess(s['hoeffding_ci95'][0], .7)
        self.assertFalse(result['gates']['precision'])
        records.append(dict(seed=12, status='failure', error='retained failure'))
        self.assertFalse(summarize(records, protocol(range(13), 4608, 512))['gates']['no_failures'])

    def test_failed_seed_is_preserved_and_not_retried_on_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch('convergence.simulate', side_effect=ValueError('witnessed failure')) as simulation:
                first = run(output, range(2), duration=480, burn=0)
                self.assertEqual(simulation.call_count, 2)
                self.assertEqual(len(first['failures']), 2)
                self.assertTrue((output/'protocol.json').exists())
                second = run(output, range(2), duration=480, burn=0)
                self.assertEqual(simulation.call_count, 2)
                self.assertEqual(first, second)
            with self.assertRaisesRegex(ValueError, 'different protocol'):
                run(output, range(3), duration=480, burn=0)

    def test_distinct_scientific_targets_have_distinct_gates(self):
        values = {m: {k: .8 for k in TARGETS} for m in METRICS}
        delta = {m: {k: 0.0 for k in TARGETS} for m in METRICS}
        delta['coherence']['single_linkage_guild_auc'] = .04
        records = [dict(seed=i, status='success', scores={'0.0625': {'30': values}},
                        finest_forcing_delta=delta, length_delta=delta, solver_delta=delta)
                   for i in range(2)]
        result = summarize(records, protocol(range(2), 4608, 512))
        self.assertFalse(result['gates']['forcing'])
        self.assertTrue(result['gates']['length'])
        self.assertFalse(result['gates']['solver'])


if __name__ == '__main__':
    unittest.main()
