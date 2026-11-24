"""Tests for general_hole_multi_period.py."""
import random
import unittest

import bfs_verify
import general_hole_multi_period as ghmp
import nonmatching_word_completion as nwc


class GeneralHoleMultiPeriodTests(unittest.TestCase):
    def test_certificate_all_hole_regimes_and_t2661(self):
        cases = (
            (10, [[0, 0], [1, 15]], (3, 5, 7), (4, 3, 3), (4, 4, 4)),
            (10, [[2, 3], [3, 2]], (2, 4, 2), (4, 4, 4), (4, 4, 4)),
            (10, [[2, 790], [1, 15]], (3, 5, 7), (4, 3, 3), (4, 4, 4)),
            (10, [[3, 230], [1, 15]], (3, 5, 7), (4, 3, 3), (4, 4, 4)),
            (10, [[1, 990], [2, 790]], (4, 4, 2), (4, 4, 4), (4, 4, 4)),
            (10, [[2, 790], [3, 230]], (4, 4, 4), (4, 4, 4), (4, 4, 4)),
            (10, [[1, 990], [2, 5]], (3, 5, 7), (4, 5, 3), (4, 4, 4)),
            (10, [[1, 990], [3, 230]], (3, 5, 7), (4, 4, 4), (4, 4, 4)),
            (2661, [[0, 0], [1, 45]], (17, 29, 23), (200, 150, 180), (190, 210, 170)),
            (2661, [[1, 263439], [2, 75]], (17, 29, 23), (200, 150, 180), (190, 210, 170)),
            (2661, [[2, 210219], [3, 61203]], (4, 6, 8), (200, 150, 180), (190, 210, 170)),
        )
        for t, holes, periods, prefixes, suffixes in cases:
            cert = ghmp.general_hole_certificate(t, holes, periods, prefixes, suffixes)
            self.assertTrue(cert['obstructed'])
            self.assertTrue(cert['bins_disjoint'])
            self.assertFalse(cert['full_homometry_claimed'])

        # tip1+tip3 with period 4 on all arms leaves Phi_4 unkilled -> refused
        with self.assertRaises(ValueError):
            ghmp.general_hole_certificate(10, [[1, 990], [3, 230]], (4, 4, 4), (4, 4, 4), (4, 4, 4))

    def test_matches_tip1_arm1_certificate(self):
        c1 = nwc.multi_period_certificate(2661, (17, 29, 23), (200, 150, 180), (190, 210, 170), h=45)
        c2 = ghmp.general_hole_certificate(2661, [[1, 45], [1, 99 * 2661]], (17, 29, 23), (200, 150, 180), (190, 210, 170))
        self.assertEqual(c1['intervals'], c2['intervals'])
        self.assertEqual(c1['obstructed'], c2['obstructed'])

    def test_audit_and_standalone_bfs_across_hole_regimes_at_t5(self):
        t = 5
        lengths = [99 * t, 79 * t, 23 * t]
        A, B, C = lengths
        periods = (2, 3, 2)  # deg(D) = 4
        L_lens = (3, 3, 3)
        R_base = (2, 2, 2)
        rng = random.Random(2026112402)
        regimes = (
            ([[0, 0], [1, 10]], 1),
            ([[2, B], [1, 10]], -1),
            ([[3, C], [1, 10]], -1),
            ([[1, A], [2, B]], -1),
            ([[2, B], [3, C]], -1),
            ([[1, A], [3, C]], -1),
            ([[1, A], [2, 2]], -1),
            ([[1, A], [3, 2]], -1),
        )
        for holes, centre in regimes:
            a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
            blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
            c_patches = []
            actual_R = []
            for Ln, lp, rp, p in zip(lengths, L_lens, R_base, periods):
                rem = (Ln - lp - rp) % p
                cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
                c_patches.append(cp)
                actual_R.append(len(cp))
            words = ghmp.construct_general_hole_words(t, holes, periods, a_patches, blocks, c_patches)
            verdict = ghmp.audit_general_hole_multi_period(
                t, holes, centre, words, periods, L_lens, actual_R,
            )
            self.assertTrue(verdict['obstructed'])
            self.assertTrue(verdict['bins_disjoint'])
            self.assertFalse(verdict['homometric'])

            # Independent BFS check on the constructed vertex sets
            left = []
            right = []
            hole_set = {(ha, hd) for ha, hd in holes}
            if (0, 0) not in hole_set:
                (left if centre == 1 else right).append([0, 0])
            for arm, w in enumerate(words, 1):
                for d, s in enumerate(w, 1):
                    if s == 1:
                        left.append([arm, d])
                    elif s == -1:
                        right.append([arm, d])
            if len(left) == len(right):
                bfs = bfs_verify.verify({'lengths': lengths, 'left': left, 'right': right})
                self.assertFalse(bfs['ok'])
                self.assertTrue(bfs['difference'])
            else:
                lp_cnt = bfs_verify.recount(lengths, left)
                rp_cnt = bfs_verify.recount(lengths, right)
                self.assertNotEqual(lp_cnt, rp_cnt)

    def test_t2661_audit_and_altered_rejection(self):
        t = 2661
        lengths = (99 * t, 79 * t, 23 * t)
        holes = [[2, lengths[1]], [3, lengths[2]]]
        periods = (4, 6, 8)
        L_lens = (100, 100, 100)
        R_base = (100, 100, 100)
        rng = random.Random(5511)
        a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
        blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
        c_patches = []
        actual_R = []
        for Ln, lp, rp, p in zip(lengths, L_lens, R_base, periods):
            rem = (Ln - lp - rp) % p
            cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
            c_patches.append(cp)
            actual_R.append(len(cp))
        words = ghmp.construct_general_hole_words(t, holes, periods, a_patches, blocks, c_patches)
        verdict = ghmp.audit_general_hole_multi_period(
            t, holes, -1, words, periods, L_lens, actual_R,
        )
        self.assertTrue(verdict['obstructed'])
        self.assertTrue(verdict['bins_disjoint'])

        # Altered periodicity breaks audit
        bad = [list(w) for w in words]
        bad[1][L_lens[1] + 2] *= -1
        with self.assertRaises(ValueError):
            ghmp.audit_general_hole_multi_period(t, holes, -1, bad, periods, L_lens, actual_R)


if __name__ == '__main__':
    unittest.main()
