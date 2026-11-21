"""Independent counters for all branches of the fixed-difference theorem."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import fixed_difference_family as family
from test_next_family import counts, distances


class FixedDifferenceTest(unittest.TestCase):
    def test_exact_identities_and_balanced_corruption(self):
        for base in family.FAMILIES:
            self.assertEqual(family.identity_residual(base), {})
        rows = [list(row) for row in family.FAMILIES[23]]
        self.assertEqual(rows[0][1][0], '+')
        self.assertEqual(rows[1][1][0], '-')
        rows[0][1] = '-'+rows[0][1][1:]
        rows[1][1] = '+'+rows[1][1][1:]
        self.assertTrue(family.identity_residual(23, rows))

    def test_fresh_original_graphs_all_branches(self):
        for c in (1, 2, 3, 7, 15, 79, 87, 151, 103, 167, 127):
            witness = family.construct(c)
            metric = distances(witness['lengths'])
            left, right = witness['left'], witness['right']
            self.assertFalse(set(left) & set(right))
            self.assertEqual(len(left), len(right))
            self.assertEqual(counts(left, metric), counts(right, metric))
            self.assertEqual(len(left), family.bound(c)['optimal_size'])
            self.assertGreaterEqual(len(left), witness['target'])
            if c in (79, 87, 151, 103, 167, 127):
                self.assertEqual(set(metric)-set(left)-set(right), {(1, 19), (1, c+76)})

    def test_prefix_and_seed_boundaries(self):
        for c in (1, 2, 3, 7, 63):
            self.assertEqual(family.construct(c)['construction'], 'Euler-cell prefix')
        self.assertEqual(family.construct(15)['construction'], 'Mallow finite c=15 control')
        self.assertIn('base 71, repeat 0', family.construct(71)['construction'])
        self.assertIn('base 71, repeat 1', family.construct(127)['construction'])
        self.assertEqual(family.bound(8*10**40+3)['optimal_size'],
                         (3*(8*10**40+3)+133)//2)
        self.assertEqual(family.bound(8*10**40+7)['optimal_size'],
                         (3*(8*10**40+7)+133)//2-1)

    def test_real_cli_and_altered_witness(self):
        script = str(Path(family.__file__))
        proof = subprocess.run([sys.executable, script, '--prove'],
                               capture_output=True, text=True, check=True)
        self.assertTrue(all(json.loads(proof.stdout)['affine_identities'].values()))
        valid = subprocess.run([sys.executable, script, '--frontier', '0'],
                               capture_output=True, text=True, check=True)
        accepted = subprocess.run([sys.executable, script, '--check', '-'],
                                  input=valid.stdout, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0)
        witness = json.loads(valid.stdout)
        witness['left'][0] = [1, 99]
        rejected = subprocess.run([sys.executable, script, '--check', '-'],
                                  input=json.dumps(witness), capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 1)
        self.assertFalse(json.loads(rejected.stdout)['homometric'])

    def test_input_boundaries(self):
        for value in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                family.construct(value)
        rows = [list(row) for row in family.FAMILIES[23]]
        rows[0][1] = '0'+rows[0][1][1:]
        with self.assertRaises(ValueError):
            family.identity_residual(23, rows)


if __name__ == '__main__':
    unittest.main()
