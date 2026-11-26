import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from paired_refinement import configuration, digest, evaluate, write_json
from refinement_report import audit, cohort_envelopes


class RefinementAuditChecks(unittest.TestCase):
    def test_fixed_cohort_envelopes_cover_binomial_control_and_retain_failures(self):
        from scipy.stats import binom
        from test_paired_refinement import row
        config = dict(communities=list(range(4, 16)), drives=[0, 1])
        intervals = []
        for successes in range(25):
            rows = [row(4+i//2, i%2, float(i < successes)) for i in range(24)]
            bound = cohort_envelopes(rows, config)['envelopes']['scores']['correlation']['same_diet_pair_auc']
            intervals.append(bound['marginal95'])
        # Exact enumeration of all binomial counts, independent of the bound's
        # implementation; a perfect observed sample must retain uncertainty.
        for probability in np.linspace(0, 1, 101):
            coverage = sum(binom.pmf(k, 24, probability) for k, (low, high) in enumerate(intervals)
                           if low <= probability <= high)
            self.assertGreaterEqual(coverage, .95-1e-12)
        self.assertLess(intervals[-1][0], 1)
        rows[0]['status'] = 'failure'
        bounds = cohort_envelopes(rows, config)['envelopes']['scores']['correlation']['same_diet_pair_auc']
        self.assertAlmostEqual(bounds['empirical_completion_range'][1]-bounds['empirical_completion_range'][0], 1/24)
        self.assertEqual(cohort_envelopes(rows[:-1], config)['status'], 'incomplete; no bound reported')

    def test_score_replay_rejects_plausible_but_false_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            study = Path(root)
            config = configuration()
            config.update(communities=[4], drives=[0], duration=512, burn=32, lengths=[240, 480])
            write_json(study/'protocol.json', config)
            x = np.random.default_rng(5).normal(size=(480, 6))*.01
            with patch('paired_refinement.simulate', return_value=(x, .1)):
                row = evaluate(4, 0, config, digest(study/'protocol.json'), study)
            self.assertEqual(row['status'], 'success')
            receipt = study/'community-4-drive-0.json'
            write_json(receipt, row)
            with patch('refinement_report.configuration', return_value=config):
                self.assertEqual(len(audit(study)[1]), 1)
                row['scores']['correlation']['overlap_spearman'] += .001
                write_json(receipt, row)
                with self.assertRaisesRegex(ValueError, 'differ from trajectories'):
                    audit(study)

    def test_missing_realization_cannot_be_exported_as_complete(self):
        with tempfile.TemporaryDirectory() as root:
            study = Path(root)
            config = configuration()
            config.update(communities=[4], drives=[0])
            write_json(study/'protocol.json', config)
            with patch('refinement_report.configuration', return_value=config):
                with self.assertRaises(FileNotFoundError):
                    audit(study)


if __name__ == '__main__':
    unittest.main()
