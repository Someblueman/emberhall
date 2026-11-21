"""Independent graph distances and exhaustive small template controls."""
from itertools import product
import json
from math import gcd
from pathlib import Path
import subprocess
import sys
import unittest

import ratio_51_33_10 as ratio
from test_next_family import counts, distances


class CellGraphTest(unittest.TestCase):
    def test_scaled_family_with_original_tree_distances(self):
        for t in (1, 2, 5, 11):
            witness = ratio.construct(t)
            left, right = witness['left'], witness['right']
            metric = distances(witness['lengths'])
            self.assertEqual(len(left), 47*t-1)
            self.assertEqual(len(right), len(left))
            self.assertFalse(set(left) & set(right))
            self.assertEqual(counts(left, metric), counts(right, metric))
            self.assertEqual(set(metric)-set(left)-set(right),
                             {(i, n) for i, n in enumerate(witness['lengths'], 1)})

    def test_gcd_one_theorem_and_fresh_bases(self):
        checked = 0
        for a in range(3, 13):
            for b in range(2, a):
                for c in range(1, b):
                    if (a+b+c) % 2 or gcd(a-b, b-c) != 1:
                        continue
                    result = ratio.template((a, b, c))
                    self.assertEqual(result['status'], 'constructed')
                    self.assertEqual(len(result['components']), 1)
                    self.assertTrue(result['components'][0]['has_boundary'])
                    self.assertTrue(ratio.verify_template(result['words']))
                    checked += 1
        self.assertGreater(checked, 50)
        for base, t in (((19, 12, 7), 3), ((23, 14, 9), 2), ((6, 4, 2), 2)):
            witness = ratio.construct(t, base)
            metric = distances(witness['lengths'])
            self.assertEqual(counts(witness['left'], metric), counts(witness['right'], metric))

    def test_graph_criterion_against_all_small_palindromic_words(self):
        for lengths in ((5, 4, 3), (7, 4, 1), (6, 4, 2), (8, 4, 2)):
            half_lengths = [(n+1)//2 for n in lengths]
            exists = False
            for bits in product('+-', repeat=sum(half_lengths)):
                words, start = [], 0
                for n, half in zip(lengths, half_lengths):
                    prefix = ''.join(bits[start:start+half])
                    words.append(prefix+prefix[:n//2][::-1])
                    start += half
                if ratio.verify_template(words):
                    exists = True
                    break
            result = ratio.template(lengths)
            self.assertEqual(result['status'] == 'constructed', exists)
            if not exists:
                self.assertFalse(result['general_tripod_obstruction'])
                self.assertTrue(any(not row['has_boundary'] and row['edge_count'] % 2
                                    for row in result['components']))

    def test_arithmetic_classification_matches_graph(self):
        for a in range(1, 10):
            for b in range(1, a+1):
                for c in range(1, b+1):
                    if (a+b+c) % 2 == 0:
                        result = ratio.template((a, b, c))
                        self.assertEqual(ratio.classify((a, b, c))['admitted'],
                                         result['status'] == 'constructed')
        self.assertTrue(ratio.classify((50*10**20, 33*10**20, 9*10**20))['admitted'])
        self.assertFalse(ratio.classify((91, 71, 16))['admitted'])
        self.assertFalse(ratio.classify((3, 3, 3))['admitted'])

    def test_full_partition_and_half_minus_one(self):
        for lengths in ((6, 3, 2), (11, 6, 4), (13, 8, 4), (8, 5, 3), (10, 7, 4), (1, 1, 1)):
            witness = ratio.original_tree(lengths)
            metric = distances(lengths)
            self.assertEqual(counts(witness['left'], metric), counts(witness['right'], metric))
            self.assertGreaterEqual(witness['size'], (sum(lengths)+1)//2-1)
            if sum(lengths) % 2 and gcd(lengths[0]-lengths[1], lengths[1]-lengths[2]) == 1:
                self.assertEqual(witness['size'], (sum(lengths)+1)//2)
        with self.assertRaisesRegex(ValueError, 'not ruled out'):
            ratio.original_tree((91, 71, 15))

    def test_template_corruption_preserves_symmetry_but_fails_identity(self):
        words = ratio.template()['words']
        row = list(words[0])
        plus = next(i for i in range(1, len(row)//2) if row[i] == '+')
        minus = next(i for i in range(1, len(row)//2) if row[i] == '-')
        row[plus], row[minus] = row[minus], row[plus]
        row[-1-plus], row[-1-minus] = row[-1-minus], row[-1-plus]
        changed = [''.join(row), *words[1:]]
        self.assertEqual(changed[0], changed[0][::-1])
        self.assertEqual(changed[0].count('+'), words[0].count('+'))
        self.assertTrue(ratio.cell_identity(changed))
        self.assertFalse(ratio.verify_template(changed))

    def test_interior_seed_is_not_a_cell_obstruction_counterexample(self):
        witness = ratio.frontier_seed()
        metric = distances(witness['lengths'])
        self.assertEqual(counts(witness['left'], metric), counts(witness['right'], metric))
        self.assertEqual(set(metric)-set(witness['left'])-set(witness['right']),
                         {(1, 19), (1, 99)})
        with self.assertRaisesRegex(ValueError, 'not ruled out'):
            ratio.original_tree(witness['lengths'])

    def test_real_cli_and_altered_witness(self):
        script = str(Path(ratio.__file__))
        valid = subprocess.run([sys.executable, script, '--witness', '3'],
                               capture_output=True, text=True, check=True)
        accepted = subprocess.run([sys.executable, script, '--check', '-'],
                                  input=valid.stdout, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0)
        witness = json.loads(valid.stdout)
        witness['left'][0] = [1, 153]
        rejected = subprocess.run([sys.executable, script, '--check', '-'],
                                  input=json.dumps(witness), capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 1)
        self.assertFalse(json.loads(rejected.stdout)['homometric'])
        negative = subprocess.run([sys.executable, script, '--prove', '--base', '7', '4', '1'],
                                  capture_output=True, text=True)
        self.assertEqual(negative.returncode, 1)
        self.assertFalse(json.loads(negative.stdout)['general_tripod_obstruction'])

    def test_input_boundaries(self):
        for scale in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                ratio.construct(scale)
        for lengths in ((1, 1, 1), (0, 3, 5)):
            with self.assertRaises(ValueError):
                ratio.template(lengths)
        for words in (('', '+', '-'), ('x', '+', '-')):
            with self.assertRaises(ValueError):
                ratio.cell_identity(words)


if __name__ == '__main__':
    unittest.main()
