"""Independent tests for nonmatching_word_completion.py."""
from collections import Counter, deque
from itertools import combinations
import random
import unittest

import intermediate_shell_repair as repair
import nonmatching_word_completion as nwc


def graph_distances(lengths):
    graph = {(0, 0): []}
    for arm, n in enumerate(lengths, 1):
        previous = (0, 0)
        for d in range(1, n + 1):
            vertex = (arm, d)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    result = {}
    for source in graph:
        row, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for other in graph[vertex]:
                if other not in row:
                    row[other] = row[vertex] + 1
                    queue.append(other)
        result[source] = row
    return result


def bfs_counts(words, distances, centre=-1):
    vertices = {(i, d): v for i, w in enumerate(words, 1)
                for d, v in enumerate(w, 1) if v}
    vertices[0, 0] = centre
    profiles = []
    for sign in (1, -1):
        group = [v for v in vertices if vertices[v] == sign]
        profiles.append(Counter(distances[u][v] for u, v in combinations(group, 2)))
    return profiles


class NonmatchingWordCompletionTests(unittest.TestCase):
    def test_cyclotomic_lcm_identities(self):
        for periods in ((1, 1, 1), (2, 2, 2), (6, 10, 15), (17, 29, 23)):
            info = nwc.cyclotomic_lcm(periods)
            D = info['lcm_poly']
            self.assertLessEqual(info['degree'], sum(periods))
            for p, Q in zip(periods, info['quotients']):
                # Verify Q * (1 - z^p) == D exactly over Z[z]
                prod = nwc.poly_mul(Q, {0: 1, p: -1})
                self.assertEqual(prod, D)

    def test_multi_period_certificate_bounds_and_huge_scale(self):
        cases = (
            (10, (3, 5, 7), (4, 3, 3), (5, 4, 4)),
            (2661, (17, 29, 23), (200, 150, 180), (190, 210, 170)),
            (2660 * 10**12 + 1, (17, 29, 23), (200, 150, 180), (190, 210, 170)),
        )
        for t, periods, prefixes, suffixes in cases:
            cert = nwc.multi_period_certificate(
                t, periods, prefixes, suffixes, h=19,
            )
            self.assertTrue(cert['obstructed'])
            self.assertTrue(cert['bins_disjoint'])
            self.assertTrue(cert['escaping_local_repair'])
            self.assertFalse(cert['full_homometry_claimed'])
        # Exact boundary violation must raise ValueError
        with self.assertRaises(ValueError):
            # deg(lcm(1-z^3, 1-z^5, 1-z^7)) = 13; L=10, R=8 => 10+8+13 = 31 > 3*10
            nwc.multi_period_certificate(10, (3, 5, 7), (10, 4, 4), (8, 4, 4), h=19)
        with self.assertRaises(ValueError):
            # R_1 = 0 invalid because (1, 99t) is a hole
            nwc.multi_period_certificate(10, (2, 3, 2), (4, 4, 4), (0, 4, 4), h=19)
        with self.assertRaises(ValueError):
            # h >= 20t + 1 invalid
            nwc.multi_period_certificate(10, (2, 3, 2), (4, 4, 4), (4, 4, 4), h=201)

    def test_independent_bfs_and_patched_multi_period_at_t5(self):
        t = 5
        lengths = (99 * t, 79 * t, 23 * t)
        h = 11
        centre = 1
        periods = (2, 3, 2)  # deg(D) = 4
        L_lens = (3, 2, 2)
        R_lens = (3, 2, 3)  # max(1,L)+max(R)+degD = 3+3+4 = 10 <= 15 = 3*t
        rng = random.Random(20261124)
        a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
        blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
        # Absorb remainder into suffix so M_i is divisible by p_i
        c_patches = []
        actual_R = []
        for Ln, lp, rp, p in zip(lengths, L_lens, R_lens, periods):
            rem = (Ln - lp - rp) % p
            cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
            c_patches.append(cp)
            actual_R.append(len(cp))
        words = nwc.construct_patched_multi_period_words(
            t, periods, a_patches, blocks, c_patches, h=h,
        )
        verdict = nwc.audit_patched_multi_period(
            t, h, centre, words, periods, L_lens, actual_R,
        )
        self.assertTrue(verdict['obstructed'])
        self.assertFalse(verdict['homometric'])
        self.assertTrue(verdict['bins_disjoint'])

        # Independent BFS check on full tree + actual_upper_pair_counts check
        dists = graph_distances(lengths)
        pos, neg = bfs_counts(words, dists, centre=centre)
        self.assertNotEqual(pos, neg)
        for d in range(lengths[0] + 1, lengths[0] + lengths[1] + 1, 17):
            self.assertEqual(
                nwc.actual_upper_pair_counts(lengths, h, words, d),
                (pos[d], neg[d]),
            )

        # Altered-witness rejection on literal SEED and on patched words
        seed_words = [[0 if c == '0' else 1 if c == '+' else -1 for c in row] for row in repair.SEED]
        c_before = nwc.actual_upper_pair_counts((99, 79, 23), 19, seed_words, 177)
        self.assertEqual(c_before[0], c_before[1])
        seed_words[0][-2] *= -1
        c_after = nwc.actual_upper_pair_counts((99, 79, 23), 19, seed_words, 177)
        self.assertNotEqual(c_after[0], c_after[1])

        # Altered-witness rejection: flipping a periodic interior sign breaks periodicity audit
        bad_words = [list(w) for w in words]
        bad_words[2][L_lens[2] + 1] *= -1
        with self.assertRaises(ValueError):
            nwc.audit_patched_multi_period(
                t, h, centre, bad_words, periods, L_lens, actual_R,
            )

    def test_escaping_k1_unequal_nondividing_periods_and_patches(self):
        t = 2661
        h = 45  # arbitrary interior hole != 19
        centre = -1
        periods = (17, 29, 23)  # none divides 2660; distinct across arms
        L_lens = (200, 150, 180)
        R_lens = (190, 210, 170)
        rng = random.Random(314159)
        a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
        blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
        c_patches = []
        actual_R = []
        for base, lp, rp, p in zip((99, 79, 23), L_lens, R_lens, periods):
            rem = (base * t - lp - rp) % p
            cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
            c_patches.append(cp)
            actual_R.append(len(cp))
        words = nwc.construct_patched_multi_period_words(
            t, periods, a_patches, blocks, c_patches, h=h,
        )
        verdict = nwc.audit_patched_multi_period(
            t, h, centre, words, periods, L_lens, actual_R,
        )
        self.assertTrue(verdict['obstructed'])
        self.assertTrue(verdict['bins_disjoint'])
        self.assertFalse(verdict['homometric'])

    def test_aligned_period2_alternating_interiors_fail_upper_or_phase(self):
        t = 2661
        lengths = (99 * t, 79 * t, 23 * t)
        L_lens = (100, 100, 100)
        R_lens = (100, 100, 100)
        rng = random.Random(88)
        a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
        c_patches = []
        actual_R = []
        for base, lp, rp in zip((99, 79, 23), L_lens, R_lens):
            rem = (base * t - lp - rp) % 2
            cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
            c_patches.append(cp)
            actual_R.append(len(cp))
        # Aligned alternating blocks: y_r = z_r = (-1)^r, q_r = (-1)^{r+1}
        b1 = [(-1) ** ((lengths[0] - (L_lens[0] + d)) + 1) for d in range(1, 3)]
        b2 = [(-1) ** (lengths[1] - (L_lens[1] + d)) for d in range(1, 3)]
        b3 = [(-1) ** (lengths[2] - (L_lens[2] + d)) for d in range(1, 3)]
        words = nwc.construct_patched_multi_period_words(
            t, (2, 2, 2), a_patches, [b1, b2, b3], c_patches, h=19,
        )
        verdict = nwc.audit_patched_multi_period(
            t, 19, -1, words, (2, 2, 2), L_lens, actual_R,
        )
        self.assertTrue(verdict['obstructed'])
        self.assertFalse(verdict['homometric'])

    def test_h_inside_periodic_region_still_obstructed(self):
        t = 10
        h = 199  # h > L_1 = 5, still < 20*t + 1 = 201
        periods = (3, 5, 7)
        L_lens = (5, 4, 3)
        R_base = (4, 5, 4)
        rng = random.Random(55)
        a_patches = [[rng.choice((-1, 1)) for _ in range(lp)] for lp in L_lens]
        blocks = [[rng.choice((-1, 1)) for _ in range(p)] for p in periods]
        c_patches = []
        actual_R = []
        for base, lp, rp, p in zip((99, 79, 23), L_lens, R_base, periods):
            rem = (base * t - lp - rp) % p
            cp = [rng.choice((-1, 1)) for _ in range(rp + rem)]
            c_patches.append(cp)
            actual_R.append(len(cp))
        words = nwc.construct_patched_multi_period_words(
            t, periods, a_patches, blocks, c_patches, h=h,
        )
        verdict = nwc.audit_patched_multi_period(
            t, h, -1, words, periods, L_lens, actual_R,
        )
        self.assertTrue(verdict['obstructed'])
        self.assertTrue(verdict['bins_disjoint'])

    def test_fourteen_invariant_equations_across_all_256_choices(self):
        for j in nwc.INVARIANT_OFFSETS:
            expected_const = -2 if j <= 20 else 2
            eq = nwc.invariant_local_equation(1, 20, j=j)
            self.assertEqual(eq['constant'], expected_const)
            self.assertTrue(eq['choice_invariant'])
        # Non-dividing shift works for j=75 when 1 <= p <= 36
        eq75 = nwc.invariant_local_equation(1, 17, j=75)
        self.assertEqual(eq75['constant'], 2)

        # Verify against full_identity on arbitrary nonperiodic words across multiple choices
        rng = random.Random(12345)
        for k, p, choice in ((1, 20, 0), (1, 19, 173), (2, 7, 255)):
            words = repair.periodic_words(
                k,
                [[rng.choice((-1, 1)) for _ in range(p)] for _ in range(3)],
                choice,
            )
            # Break j=6 named positions so Hawthorn's j=6 equation passes,
            # while leaving j=65 matching!
            eq6 = nwc.invariant_local_equation(k, p, j=6)
            named65 = {(arm, d) for arm, d, _, _ in nwc.invariant_local_equation(k, p, j=65)['terms']}
            # Flip one term in j=6 with coeff -1 not in j=65's named set
            for arm, d, coeff, _ in eq6['terms']:
                if coeff == -1 and (arm, d) not in named65 and words[arm - 1][d - 1] == 1:
                    words[arm - 1][d - 1] = -1
                    break
            audit = nwc.audit_invariant_equations(k, p, words, offsets=(6, 65))
            self.assertFalse(audit['results']['6']['excluded'])
            self.assertTrue(audit['results']['65']['excluded'])
            self.assertTrue(audit['excluded_by_any'])

    def test_upper_forced_triples_against_complete_upper(self):
        rng = random.Random(9991)
        for k, choice in ((1, 0), (1, 173), (2, 255)):
            words = repair.periodic_words(k, [[1]*20, [-1]*20, [1]*20], choice)
            # Randomize all inserted signs on arms 2 and 3
            for i, base in ((1, 79), (2, 23)):
                for d in range(1, base * 2660 * k + 1):
                    words[i][d - 1] = rng.choice((-1, 1))
            res = nwc.audit_upper_forced_triples(k, words)
            up = repair.complete_upper(
                tuple(map(len, words)), 19, words[1], words[2],
            )
            # Every failed triple m must produce a non-sign in complete_upper at depth 23t - m
            t = 2660 * k + 1
            for row in res['triples']:
                m = row['m']
                depth1 = 23 * t - m
                suf_val = up['suffix'][depth1 - (20 * t + 1)]
                self.assertEqual(suf_val in (-1, 1), row['feasible'])


if __name__ == '__main__':
    unittest.main()
