"""Independent pair enumeration tests for modular lifting and exact shells."""
from collections import Counter
from itertools import product
from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import t2661_same_parity as m


class SameParityTests(unittest.TestCase):
    def test_frontier_is_exact(self):
        self.assertEqual(m.brute_difference(m.frontier(), -1), {})
        self.assertEqual([len(w) for w in m.frontier()], [99, 79, 23])

    def test_modular_counter_against_pairs(self):
        rng = random.Random(2661)
        for _ in range(20):
            signs = [1]*5 + [-1]*5 + [0]*2
            rng.shuffle(signs)
            words, centre = [signs[1:5], signs[5:9], signs[9:]], signs[0]
            difference = m.brute_difference(words, centre)
            for p in (1, 2, 3, 5, 7, 19):
                left, right = m.modular_profiles(words, centre, p)
                expected = [0]*p
                for d, n in difference.items():
                    expected[d % p] += n
                self.assertEqual([a-b for a, b in zip(left, right)], expected)
                self.assertEqual(sum(left), 10)
                self.assertEqual(sum(right), 10)

    def test_exact_shell_matches_every_distance(self):
        # Includes a missing centre, holes on different arms, endpoint and
        # internal cuts, coincident arm ends, non-alternating patterns, P=3.
        rng = random.Random(19)
        for period in (1, 2, 3):
            for _ in range(20):
                signs = [1]*4 + [-1]*4 + [0]*2
                rng.shuffle(signs)
                words, centre = [signs[1:4], signs[4:7], signs[7:]], signs[0]
                halves = (period, 2*period, 3*period)
                cuts = tuple(rng.randrange(len(w)+1) for w in words)
                patterns = tuple(tuple(rng.choice((-1, 1)) for _ in range(period)) for _ in words)
                lifted = m.lift(words, centre, halves, cuts, patterns)
                expected = m.mul(m.scale(m.brute_difference(lifted, centre), 2),
                                 m.mul({0: 1, 1: -1}, {0: 1, period: -1}))
                self.assertEqual(m.exact_numerator(words, centre, halves, cuts, patterns), expected)

    def test_modular_lifting_all_small_cuts_and_patterns(self):
        # T(3,1,1): pairs {centre,arm2-tip} and {arm1-depth1,depth2}
        # both have distance 1. Two odd holes: arm1-depth3 and arm3-tip.
        words, centre = [[-1, -1, 0], [1], [0]], 1
        self.assertEqual(m.brute_difference(words, centre), {})
        for cuts in product(range(4), range(2), range(2)):
            for flat in product((-1, 1), repeat=3):
                lifted = m.lift(words, centre, (6, 12, 6), cuts,
                                tuple((s,) for s in flat))
                for p in (2, 3, 6):
                    left, right = m.modular_profiles(lifted, centre, p)
                    self.assertEqual(left, right)

    def test_t2661_independent_modular_counts_and_exact_failure(self):
        r = m.run()
        self.assertEqual(r['lengths'], [263439, 210219, 61203])
        self.assertEqual(r['size'], 267430)
        self.assertEqual(r['holes'], [[1, 19], [1, 263439]])
        self.assertTrue(all(v['equal'] for v in r['modular_profiles'].values()))
        self.assertFalse(r['homometric'])
        self.assertGreater(r['first_distance_discrepancy'], 0)

    def test_altered_pair_rejected_by_modular_counter(self):
        w = m.frontier()
        # Swap a plus and minus at different residues; cardinalities survive.
        w[0][0], w[0][1] = w[0][1], w[0][0]
        self.assertNotEqual(*m.modular_profiles(w, -1, 19))

    def test_unbalanced_shell_oracle(self):
        words, centre = [[1, 0, 1], [1], [0]], 1
        halves, cuts, patterns = (2, 4, 2), (1, 0, 1), ((1, -1),)*3
        # Construct directly because lift intentionally requires balance.
        out = []
        for w, h, c, pattern in zip(words, halves, cuts, patterns):
            block = list(pattern)*(h//2)
            out.append(w[:c]+block+[-x for x in block]+w[c:])
        expected = m.mul(m.scale(m.brute_difference(out, centre), 2),
                         m.mul({0: 1, 1: -1}, {0: 1, 2: -1}))
        self.assertEqual(m.exact_numerator(words, centre, halves, cuts, patterns,
                                           require_balance=False), expected)

    def test_free_base_hensel_against_exhaustive_mod4(self):
        # Exhaust every actual sign variable, and compare *necessary mod-4*
        # feasibility with elimination, not only full homometry feasibility.
        for cuts in ((0, 0, 0), (1, 0, 0), (3, 1, 1)):
            seed = [[1, 1, 0], [1], [0]]
            halves, period = (2, 2, 2), 1
            r = m.hensel_obstruction(seed, 1, halves, cuts, period, free_base=True)
            feasible = False
            for signs in product((-1, 1), repeat=7):
                centre = signs[0]
                words = [[signs[1], signs[2], 0], [signs[3]], [0]]
                if (centre+sum(map(sum, words))) % 4:
                    continue
                patterns = tuple((signs[4+j],) for j in range(3))
                N = m.exact_numerator(words, centre, halves, cuts, patterns,
                                      require_balance=False)
                if all(c % 4 == 0 for c in N.values()):
                    feasible = True
                    break
            self.assertEqual(r['excluded'], not feasible)
            if r['excluded']:
                self.assertTrue(m.verify_obstruction_by_shells(
                    seed, 1, halves, cuts, period, r['xor_exponents'], free_base=True)['verified'])

    def test_free_base_large_certificate_independently(self):
        halves = tuple(1330*b for b in m.BASE)
        r = m.hensel_obstruction(m.frontier(), -1, halves, (19, 0, 0), 1330,
                                 free_base=True)
        self.assertTrue(r['excluded'])
        self.assertEqual(r['variables'], 4190)
        self.assertEqual(r['xor_exponents'], [30592])
        self.assertTrue(m.verify_obstruction_by_shells(
            m.frontier(), -1, halves, (19, 0, 0), 1330,
            r['xor_exponents'], free_base=True)['verified'])
        # A made-up coefficient is not accepted as this obstruction.
        self.assertFalse(m.verify_obstruction_by_shells(
            m.frontier(), -1, halves, (19, 0, 0), 1330, [1], free_base=True)['verified'])

    def test_nonperiodic_half_words_escape_the_simple_certificate(self):
        halves = tuple(1330*b for b in m.BASE)
        v = m.verify_obstruction_by_shells(m.frontier(), -1, halves, (19, 0, 0),
                                          1330, [30592], free_base=True, full_words=True)
        self.assertFalse(v['verified'])
        self.assertEqual(v['odd_variable_coefficients'], 24)

    def test_defect_refinement_matches_literal_sign_assignments(self):
        seed, centre, halves, cuts = [[1, 1, 0], [1], [0]], 1, (2, 2, 2), (1, 0, 0)
        defects = ((0, 0), (2, 1))
        result = m.hensel_obstruction(seed, centre, halves, cuts, 1, True, defects)
        feasible = False
        # Four base signs, three residue signs, two independently split sites.
        for signs in product((-1, 1), repeat=9):
            base = [[signs[1], signs[2], 0], [signs[3]], [0]]
            if (signs[0]+sum(map(sum, base))) % 4:
                continue
            lifted = []
            for a, (w, h, c) in enumerate(zip(base, halves, cuts)):
                block = [signs[4+a]]*h
                for j, (arm, offset) in enumerate(defects):
                    if arm == a:
                        block[offset] = signs[7+j]
                lifted.append(w[:c]+block+[-x for x in block]+w[c:])
            N = m.mul(m.scale(m.brute_difference(lifted, signs[0]), 2),
                      m.mul({0: 1, 1: -1}, {0: 1, 1: -1}))
            if all(c % 4 == 0 for c in N.values()):
                feasible = True
                break
        self.assertEqual(result['excluded'], not feasible)
        if result['excluded']:
            self.assertTrue(m.verify_obstruction_by_shells(
                seed, centre, halves, cuts, 1, result['xor_exponents'],
                free_base=True, defects=defects)['verified'])

    def test_modular_shell_against_literal_neighbours(self):
        rng = random.Random(1330)
        lengths = (9, 7, 3)
        vertices = [(a, d) for a, L in enumerate(lengths) for d in range(1, L+1)]
        for _ in range(12):
            holes = set(rng.sample(vertices, 2))
            centre_present = rng.choice((True, False))
            for a, d in vertices:
                if (a, d) in holes:
                    continue
                distances = [abs(d-e) if a == b else d+e
                             for b, e in vertices if (b, e) not in holes and (b, e) != (a, d)]
                if centre_present:
                    distances.append(d)
                for p in (1, 2, 4, 7):
                    expected = [sum(x % p == r for x in distances) for r in range(p)]
                    self.assertEqual(m.modular_shell(lengths, holes, centre_present, a, d, p), expected)

    def test_mod4_arbitrary_word_obstruction_and_even_scale_boundary(self):
        for k in (1, 3, 5, 101):
            self.assertTrue(m.mod4_halfword_obstruction(k)['excluded_for_fixed_frontier'])
            self.assertEqual(m.audit_mod4_cut_classes(k)['cut_residue_classes'], 64)
        for k in (2, 4, 100):
            self.assertFalse(m.mod4_halfword_obstruction(k)['excluded_for_fixed_frontier'])
        for k, expected in ((1, False), (2, True)):
            halves = tuple(1330*k*b for b in m.BASE)
            lifted = m.lift(m.frontier(), -1, halves, (19, 0, 0), ((1, -1),)*3)
            left, right = m.modular_profiles(lifted, -1, 4)
            self.assertEqual(left == right, expected)

    def test_arbitrary_nonperiodic_halfwords_preserve_modular_counts(self):
        rng = random.Random(665)
        base, centre, halves = [[-1, -1, 0], [1], [0]], 1, (6, 12, 6)
        for _ in range(20):
            cuts = tuple(rng.randrange(len(w)+1) for w in base)
            lifted = []
            for w, h, c in zip(base, halves, cuts):
                block = [rng.choice((-1, 1)) for _ in range(h)]
                lifted.append(w[:c]+block+[-s for s in block]+w[c:])
            for p in (2, 3, 6):
                self.assertEqual(*m.modular_profiles(lifted, centre, p))

    def test_validation(self):
        with self.assertRaises(ValueError):
            m.run(0)
        with self.assertRaises(ValueError):
            m.lift(m.frontier(), -1, (1, 2, 2), (0, 0, 0), ((1, -1),)*3)
        with self.assertRaises(ValueError):
            m.modular_profiles(m.frontier(), -1, 0)
        with self.assertRaises(ValueError):
            m.lift(m.frontier(), -1, (2, 2, 2), (100, 0, 0), ((1, -1),)*3)


if __name__ == '__main__':
    unittest.main()
