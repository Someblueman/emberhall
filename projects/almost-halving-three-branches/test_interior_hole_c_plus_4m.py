"""Tests for the c = r + 4m three-parameter interior-hole family."""
import unittest

import bfs_verify
import interior_hole_c_plus_4 as cp4
import interior_hole_c_plus_4m as cp4m


class InteriorHoleCPlus4MTests(unittest.TestCase):
    def test_four_variable_laurent_proof_and_corruptions(self):
        proof = cp4m.prove_c_plus_4m_laurent()
        self.assertEqual(proof['residual_terms'], 0)
        self.assertGreater(proof['corrupt_s0_terms'], 0)
        self.assertGreater(proof['corrupt_hole_terms'], 0)
        self.assertGreater(proof['corrupt_block_terms'], 0)
        self.assertTrue(proof['specialization_matches_difference'])

    def test_matches_c_plus_4_at_m1(self):
        for r, k in ((5, 0), (7, 2), (11, 3)):
            w1 = cp4.construct_c_plus_4(r, k)
            w2 = cp4m.construct_c_plus_4m(r, 1, k)
            self.assertEqual(w1['left'], w2['left'])
            self.assertEqual(w1['right'], w2['right'])
            self.assertEqual(w1['lengths'], w2['lengths'])

    def test_independent_bfs_across_parameters_and_open_escapes(self):
        cases = (
            (5, 1, 0),
            (7, 2, 0),
            (7, 2, 1),
            (9, 2, 1),
            (11, 3, 1),
            (23, 2, 6),   # (215, 191, 31)
            (23, 5, 6),   # (227, 203, 43)
        )
        for r, m, k in cases:
            w = cp4m.construct_c_plus_4m(r, m, k)
            self.assertTrue(w['homometric'])
            self.assertTrue(w['meets_target'])
            self.assertEqual(w['omitted'], [[1, r], [1, w['lengths'][0]]])
            bfs = bfs_verify.verify({'lengths': w['lengths'], 'left': w['left'], 'right': w['right']})
            self.assertTrue(bfs['ok'])
            self.assertEqual(bfs['difference'], {})
            self.assertEqual(bfs['size'], w['size'])

    def test_solve_tree_permutations_and_altered_rejection(self):
        for lengths in ([215, 191, 31], [31, 215, 191], [227, 203, 43], [203, 43, 227]):
            w = cp4m.solve_tree(lengths)
            self.assertTrue(w['homometric'])
            self.assertTrue(w['meets_target'])
            bfs = bfs_verify.verify({'lengths': w['lengths'], 'left': w['left'], 'right': w['right']})
            self.assertTrue(bfs['ok'])

        # Altered-pair rejection via standalone bfs_verify
        base = cp4m.construct_c_plus_4m(7, 2, 0)
        bad_right = [list(v) for v in base['right']]
        bad_right[0] = [1, 7]  # move [0, 0] to omitted [1, 7]
        rejected = bfs_verify.verify({'lengths': base['lengths'], 'left': base['left'], 'right': bad_right})
        self.assertFalse(rejected['ok'])
        self.assertTrue(rejected['difference'])

    def test_validation(self):
        for bad in ((7, 0, 0), (6, 1, 0), (5, 2, 0), (7, 2, -1)):
            with self.assertRaises(ValueError):
                cp4m.construct_c_plus_4m(*bad)
        with self.assertRaises(ValueError):
            cp4m.solve_tree([195, 139, 19])


if __name__ == '__main__':
    unittest.main()
