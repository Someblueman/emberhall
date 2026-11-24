"""Tests for universal_tip_multi_period.py."""
import random
import unittest

import bfs_verify
import general_hole_multi_period as ghmp
import universal_tip_multi_period as utmp


class UniversalTipMultiPeriodTests(unittest.TestCase):
    def test_bin_matrix_determinant_all_eight_tip_vectors(self):
        for s1 in (0, 1):
            for s2 in (0, 1):
                for s3 in (0, 1):
                    det = utmp.bin_matrix_determinant((s1, s2, s3))
                    self.assertEqual(det, {3 - s1 - s2 - s3: 2})

    def test_closes_tip13_phi4_and_tip1_restricted_overlap(self):
        # Previously refused in general_hole_certificate: tip1+tip3 with 4 | p_i
        cert13 = utmp.universal_tip_certificate(
            10, [[1, 990], [3, 230]], (4, 4, 4), (4, 4, 4), (4, 4, 4),
        )
        self.assertTrue(cert13['obstructed'])
        self.assertTrue(cert13['bins_disjoint'])
        self.assertEqual(cert13['tip_arms'], [1, 3])
        self.assertEqual(cert13['bin_det_exponent'], 1)
        self.assertFalse(cert13['full_homometry_claimed'])

        # t=2661 with unequal 4-divisible periods (4, 8, 12) on tip1+tip3
        cert13_big = utmp.universal_tip_certificate(
            2661, [[1, 99 * 2661], [3, 23 * 2661]], (4, 8, 12), (200, 150, 180), (190, 210, 170),
        )
        self.assertTrue(cert13_big['obstructed'])
        self.assertTrue(cert13_big['bins_disjoint'])

        # tip1 with periods=(2, 2, 2) even when all m in [m_lo, m_hi] lack hole-free upper overlap check
        cert1 = utmp.universal_tip_certificate(
            2661, [[1, 99 * 2661], [2, 10]], (2, 2, 2), (200, 150, 180), (190, 210, 170),
        )
        self.assertTrue(cert1['obstructed'])
        self.assertEqual(cert1['bin_det_exponent'], 2)

    def test_audit_tip13_phi4_and_tip1_period1_2_with_bfs(self):
        t = 7
        lengths = (99 * t, 79 * t, 23 * t)
        A, B, C = lengths
        rng = random.Random(2026112403)
        cases = (
            ([(1, A), (3, C)], (4, 4, 4), (3, 3, 3), (3, 3, 3), 1),
            ([(1, A), (3, C)], (4, 8, 4), (2, 1, 2), (2, 2, 2), -1),
            ([(1, A)], (1, 1, 1), (4, 4, 4), (4, 4, 4), 1),
            ([(1, A)], (2, 2, 2), (4, 4, 4), (4, 4, 4), -1),
            ([(0, 0), (1, 17)], (2, 4, 6), (2, 2, 2), (2, 2, 2), 1),
        )
        for holes, periods, L_lens, R_base, centre in cases:
            a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
            blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
            c_patches = []
            actual_R = []
            for Ln, lp, rp, p in zip(lengths, L_lens, R_base, periods):
                rem = (Ln - lp - rp) % p
                cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
                c_patches.append(cp)
                actual_R.append(len(cp))
            words = []
            hole_set = set(holes)
            for i, (Ln, ap, blk, cp, p) in enumerate(zip(lengths, a_patches, blocks, c_patches, periods), 1):
                w = list(ap) + list(blk) * ((Ln - len(ap) - len(cp)) // p) + list(cp)
                for ha, hd in hole_set:
                    if ha == i:
                        w[hd - 1] = 0
                words.append(w)

            verdict = utmp.audit_universal_tip_multi_period(
                t, holes, centre, words, periods, L_lens, actual_R,
            )
            self.assertTrue(verdict['obstructed'])
            self.assertTrue(verdict['bins_disjoint'])
            self.assertIsNotNone(verdict['cyclotomic_witness'])
            self.assertFalse(verdict['homometric'])

            left, right = [], []
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
                self.assertNotEqual(
                    bfs_verify.recount(lengths, left),
                    bfs_verify.recount(lengths, right),
                )

    def test_t2661_tip13_periods_4_8_12_audit(self):
        t = 2661
        lengths = (99 * t, 79 * t, 23 * t)
        holes = [[1, lengths[0]], [3, lengths[2]]]
        periods = (4, 8, 12)
        L_lens = (50, 50, 50)
        R_base = (50, 50, 50)
        rng = random.Random(7733)
        a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
        blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
        c_patches = []
        actual_R = []
        for Ln, lp, rp, p in zip(lengths, L_lens, R_base, periods):
            rem = (Ln - lp - rp) % p
            cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
            c_patches.append(cp)
            actual_R.append(len(cp))
        words = []
        for i, (Ln, ap, blk, cp, p) in enumerate(zip(lengths, a_patches, blocks, c_patches, periods), 1):
            w = list(ap) + list(blk) * ((Ln - len(ap) - len(cp)) // p) + list(cp)
            if i in (1, 3):
                w[-1] = 0
            words.append(w)
        verdict = utmp.audit_universal_tip_multi_period(
            t, holes, 1, words, periods, L_lens, actual_R,
        )
        self.assertTrue(verdict['obstructed'])
        self.assertTrue(verdict['bins_disjoint'])
        self.assertIsNotNone(verdict['cyclotomic_witness'])

        # Rejects non-periodic perturbation
        bad = [list(w) for w in words]
        bad[0][L_lens[0] + 1] *= -1
        with self.assertRaises(ValueError):
            utmp.audit_universal_tip_multi_period(t, holes, 1, bad, periods, L_lens, actual_R)


if __name__ == '__main__':
    unittest.main()
