import json
from pathlib import Path
import tempfile
import unittest

from convergence import METRICS, TARGETS
from repeated_paths import analyze_repeats


class ReplicationChecks(unittest.TestCase):
    def test_communities_remain_replicates_and_negative_variance_is_retained(self):
        with tempfile.TemporaryDirectory() as temporary:
            study = Path(temporary)/'first'
            second = Path(temporary)/'second'
            study.mkdir(); second.mkdir()
            (study/'protocol.json').write_text(json.dumps(dict(seeds=[0,1,2])))
            for seed in range(3):
                a = {m: {k: float(seed % 2) for k in TARGETS} for m in METRICS}
                b = {m: {k: float(1-seed % 2) for k in TARGETS} for m in METRICS}
                (study/f'seed-{seed}.json').write_text(json.dumps(dict(seed=seed, status='success', scores={'0.0625': {'30': a}})))
                r = dict(seed=seed, status='success', scores=b) if seed != 2 else dict(seed=seed, status='failure', error='retained')
                (second/f'seed-{seed}.json').write_text(json.dumps(r))
            result = analyze_repeats(study, second)
            self.assertEqual(result['complete_communities'], 2)
            self.assertEqual(len(result['failures']), 1)
            s = result['summaries']['coherence']['single_linkage_guild_auc']
            self.assertEqual(s['community_mean_interval']['n'], 2)
            self.assertEqual(s['community_mean_interval']['mean'], .5)
            self.assertEqual(s['within_path_variance'], .5)
            self.assertEqual(s['between_community_variance_raw'], -.25)
            self.assertEqual(s['maximum_path_score_change'], 1)
