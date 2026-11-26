import copy
import unittest
import numpy as np
from scipy.stats import t
from paired_refinement import summarize, validate
from convergence import METRICS, TARGETS


def row(seed, drive, value):
    table = {m: {k: value for k in TARGETS} for m in METRICS}
    return dict(community=seed, drive=drive, status='success',
                scores=copy.deepcopy(table), forcing_delta=copy.deepcopy(table),
                length_delta=copy.deepcopy(table), segment_delta={'16': copy.deepcopy(table)},
                protocol_sha256='frozen', input_seed=80000+100*seed+drive,
                bridge_seed=90000+100*seed+drive, endpoints_exact=True)


class PairedRefinementChecks(unittest.TestCase):
    def test_community_uncertainty_and_cancellation_are_separate(self):
        rows = [row(4, 0, -1), row(4, 1, 1), row(5, 0, .4), row(5, 1, .6)]
        result = summarize(rows, dict(communities=[4, 5], drives=[0, 1]))
        stat = result['summaries']['forcing_delta']['correlation']['overlap_spearman']
        self.assertEqual(stat['n'], 2)
        self.assertEqual(stat['mean'], .25)
        self.assertAlmostEqual(stat['ci95'][1], .25+t.ppf(.975, 1)*.25)
        self.assertEqual(stat['maximum_individual_absolute_value'], 1)
        self.assertEqual(stat['communities_with_any_margin_exceedance'], 2)
        # Differences have range four, rather than the score's range two.
        self.assertAlmostEqual(stat['hoeffding_marginal_radius95'],
                               4*np.sqrt(np.log(40)/4))

    def test_missing_and_failed_drives_do_not_bias_community_weights(self):
        failed = row(5, 1, 0)
        failed.update(status='failure', error='witnessed')
        rows = [row(4, 0, 0), row(4, 1, 1), row(5, 0, 1), failed, row(6, 0, 1)]
        result = summarize(rows, dict(communities=[4, 5, 6], drives=[0, 1]))
        self.assertFalse(result['complete'])
        self.assertEqual(result['complete_communities'], 1)
        self.assertEqual(len(result['failures']), 1)
        self.assertEqual(result['summaries']['scores']['coherence']['same_diet_pair_auc']['mean'], .5)

    def test_duplicate_unplanned_and_tampered_evidence_rejected(self):
        good = row(4, 0, .5)
        with self.assertRaises(ValueError):
            summarize([good, good], dict(communities=[4], drives=[0, 1]))
        with self.assertRaises(ValueError):
            summarize([row(99, 0, .5)], dict(communities=[4], drives=[0, 1]))
        for key, value in [('input_seed', 1), ('protocol_sha256', 'other'), ('endpoints_exact', False)]:
            changed = copy.deepcopy(good)
            changed[key] = value
            with self.assertRaises(ValueError):
                validate(changed, 4, 0, 'frozen')
        good['scores']['coherence']['overlap_spearman'] = float('nan')
        with self.assertRaises(ValueError):
            validate(good, 4, 0, 'frozen')


if __name__ == '__main__':
    unittest.main()
