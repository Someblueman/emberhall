import unittest
import numpy as np
from scipy.stats import spearmanr
from rank_attribution import attribution


class RankAttributionTests(unittest.TestCase):
    def test_all_permutations_and_ties_match_independent_score(self):
        import itertools
        target = [0, 1, 1, 3]
        old = [0, 2, 1, 3]
        for new in itertools.product(range(3), repeat=4):
            if len(set(new)) == 1:
                continue
            result = attribution(target, old, new)
            expected = spearmanr(target, new).statistic-spearmanr(target, old).statistic
            self.assertAlmostEqual(sum(r['contribution'] for r in result['comparisons']), expected)

    def test_rescaling_has_no_rank_change(self):
        before = np.random.default_rng(17).normal(size=15)
        result = attribution(np.arange(15), before, 3*before+10)
        self.assertEqual(result['changed_comparisons'], 0)
        self.assertAlmostEqual(result['score_change'], 0)

    def test_constant_rank_is_undefined(self):
        with self.assertRaisesRegex(ValueError, 'constant'):
            attribution([0, 1, 2], [0, 0, 0], [0, 1, 2])


if __name__ == '__main__':
    unittest.main()
