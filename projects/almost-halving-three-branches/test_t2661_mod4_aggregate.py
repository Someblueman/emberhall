"""The formulas are tested by actual vertex-pair bins, not their own equations."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import t2661_mod4_aggregate as m


class AggregateTests(unittest.TestCase):
    def test_actual_large_trees_both_parities_and_scales(self):
        for k in (1, 2):
            for parity in ('odd', 'even'):
                result = m.allocation(k, parity)
                checked = m.check(result)
                self.assertTrue(checked['valid_mod4'])
                self.assertEqual(checked['positive_size'], (201*(2660*k+1)-1)//2)
                self.assertEqual(sum(checked['left_bins']), checked['target']*(checked['target']-1)//2)
                self.assertNotEqual(checked['distance_one_left_minus_right'], 0)
                self.assertEqual({d % 2 for _, d in result['holes']}, {1 if parity == 'odd' else 0})
                self.assertFalse(checked['full_homometry_claimed'])

    def test_altered_allocation_preserves_sizes_but_is_rejected(self):
        for parity in ('odd', 'even'):
            result = m.allocation(1, parity)
            bad = copy.deepcopy(result)
            groups, x, A = result['groups'], result['negative_counts'], result['normalized_matrix']
            pair = next((i, j) for i, g in enumerate(groups) for j, h in enumerate(groups)
                        if i != j and x[i] < g['count'] and x[j] > 0
                        and any(row[i] != row[j] for row in A))
            i, j = pair
            bad['negative_counts'][i] += 1
            bad['negative_counts'][j] -= 1
            checked = m.check(bad)
            self.assertFalse(checked['valid_mod4'])
            self.assertEqual(checked['positive_size'], checked['target'])
            self.assertEqual(checked['negative_size'], checked['target'])

    def test_exact_affine_extension_and_large_symbolic_scales(self):
        records = m.parity_extension()
        self.assertEqual(len(records), 4)
        for parity in ('odd', 'even'):
            for k in (1, 2, 3, 4, 11, 20, 101, 1001, 10**12):
                r = m.allocation(k, parity)
                ref = m.allocation(1 if k % 2 else 2, parity)
                self.assertEqual(r['normalized_matrix'], ref['normalized_matrix'])
                self.assertEqual(r['corrections'], ref['corrections'])
                self.assertEqual(sum(g['count'] for g in r['groups']), sum(r['lengths'])-1)
                self.assertEqual(sum(r['negative_counts']), (sum(r['lengths'])-1)//2)
                for g, x in zip(r['groups'], r['negative_counts']):
                    self.assertLessEqual(0, x)
                    self.assertLessEqual(x, g['count'])

    def test_cli_recounts_and_exposes_scope(self):
        script = Path(m.__file__)
        p = subprocess.run([sys.executable, str(script), '--prove'], capture_output=True, text=True, check=True)
        r = json.loads(p.stdout)
        self.assertEqual(r['scope'], 'modular distance equality only')
        self.assertTrue(all(x['valid_mod4'] for x in r['records']))
        self.assertEqual(r['records'][0]['holes'], [[1, 19], [1, 263439]])
        self.assertEqual(r['records'][1]['holes'], [[1, 18], [1, 263438]])

    def test_invalid_scale_and_parity(self):
        for k in (0, -1, True):
            with self.assertRaises(ValueError):
                m.allocation(k, 'odd')
        with self.assertRaises(ValueError):
            m.allocation(1, 'opposite')


if __name__ == '__main__':
    unittest.main()
