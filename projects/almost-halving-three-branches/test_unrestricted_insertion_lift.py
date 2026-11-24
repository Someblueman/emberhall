import itertools
import unittest
from collections import Counter

import unrestricted_insertion_lift as lift


def literal(lengths, h, centre, words):
    vertices = [((0, 0), centre)]
    vertices += [((i, d), s) for i, w in enumerate(words, 1)
                 for d, s in enumerate(w, 1) if s]
    difference = Counter()
    for (u, s), (v, t) in itertools.combinations(vertices, 2):
        distance = abs(u[1]-v[1]) if u[0] == v[0] else u[1]+v[1]
        difference[distance] += (s+t)//2
    return {d: n for d, n in difference.items() if n}


class UnrestrictedInsertionTests(unittest.TestCase):
    def test_every_balanced_small_colouring_against_literal_pairs(self):
        # Every assignment, not just prospective solutions or generated prefixes.
        for lengths, h in (((5, 4, 2), 2), ((6, 3, 2), 1), ((6, 4, 1), 5)):
            occupied = [(i, d) for i, n in enumerate(lengths)
                        for d in range(1, n+1) if (i, d) not in ((0, h), (0, lengths[0]))]
            for negative in itertools.combinations(range(len(occupied)), (len(occupied)-1)//2):
                words = [[0]*n for n in lengths]
                minus = set(negative)
                for j, (i, d) in enumerate(occupied):
                    words[i][d-1] = -1 if j in minus else 1
                # Centre -1 makes the two class sizes equal.
                expected = literal(lengths, h, -1, words)
                shell = {d: 2*n for d, n in expected.items()}
                derivative = lift.add(shell, lift.shift(shell, 1, -1))
                self.assertEqual(lift.identity(lengths, h, -1, words), derivative)
                for d in range(1, lengths[0]+lengths[1]+1):
                    self.assertEqual(lift.distance_difference(lengths, h, -1, words, d), expected.get(d, 0))
                result = lift.complete(lengths, h, -1, words[0][:h-1], words[1], words[2])
                if result['valid']:
                    self.assertFalse(literal(lengths, h, -1, [result['arm1'], words[1], words[2]]))
                if not expected:
                    self.assertTrue(result['valid'])
                    self.assertEqual(result['arm1'], words[0])

    def test_seed_completion_and_altered_witness(self):
        words = [[0 if c == '0' else 1 if c == '+' else -1 for c in w]
                 for w in lift.FRONTIER]
        self.assertFalse(literal(lift.BASE, 19, -1, words))
        result = lift.complete(lift.BASE, 19, -1, words[0][:18], words[1], words[2])
        self.assertTrue(result['valid'])
        self.assertEqual(result['arm1'], words[0])
        # Swap opposite signs, retaining balance, holes and the fixed first-arm prefix.
        altered = [w[:] for w in words]
        altered[2][0], altered[2][1] = altered[2][1], altered[2][0]
        self.assertTrue(literal(lift.BASE, 19, -1, altered))
        self.assertTrue(lift.identity(lift.BASE, 19, -1, altered))

    def test_prefix_allocation_preserves_seeds_and_joint_totals(self):
        for k in (1, 2, 3):
            words = lift.prefix_realization(k)
            self.assertEqual(-1+sum(map(sum, words)), 0)
            for i, (base, seed) in enumerate(zip(lift.BASE, lift.FRONTIER)):
                cut = 19 if i == 0 else 0
                added = 2660*k*base
                for depth, char in enumerate(seed, 1):
                    new_depth = depth if depth <= cut else depth+added
                    self.assertEqual(words[i][new_depth-1], 0 if char == '0' else 1 if char == '+' else -1)
                counts = Counter((d % 2660) for d in range(cut+1, cut+added+1) if words[i][d-1] < 0)
                self.assertTrue(all(counts[r] == (k*base+(k % 2)*(-1)**r)//2 for r in range(2660)))
            lengths = tuple(map(len, words))
            self.assertEqual(lift.distance_difference(lengths, 19, -1, words, 1), 0)
            self.assertEqual(lift.distance_difference(lengths, 19, -1, words, 2), -1)

    def test_validation(self):
        for bad in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                lift.prefix_realization(bad)

    def test_tail_obstruction_at_fresh_scales_and_altered_seed(self):
        for k in (1, 3, 7):
            report = lift.all_word_obstruction(k)
            words = lift.prefix_realization(k)
            self.assertEqual(lift.distance_difference(tuple(report['lengths']), 19, -1,
                                                     words, report['distance']), 1)
        # The obstruction depends on the actual seed, so changing that seed
        # must not be certified by the hard-coded theorem counter.
        old = lift.FRONTIER
        changed = list(old)
        changed[0] = old[0][:37]+'-'+old[0][38:]
        try:
            lift.FRONTIER = tuple(changed)
            with self.assertRaises(AssertionError):
                lift.all_word_obstruction(1)
        finally:
            lift.FRONTIER = old


if __name__ == '__main__':
    unittest.main()
