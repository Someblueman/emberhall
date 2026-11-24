import itertools
import unittest

import tail_boundary_repair as repair
from unrestricted_insertion_lift import distance_difference


class TailBoundaryRepairTests(unittest.TestCase):
    def test_local_language_count_against_exhaustion(self):
        constants = repair.local_constants()
        self.assertEqual(constants, [-1, -1, -1, -1, 1, 1, 3, 3, 5, 5, 7, 7, 9, 9, 11, 11, 13, 13])
        for shells in range(1, 7):
            count = 0
            for signs in itertools.product((-1, 1), repeat=2*(shells-1)):
                running = 0
                valid = True
                for j in range(shells-1):
                    running += signs[2*j]+signs[2*j+1]
                    valid &= constants[j+1]+running in (-1, 1)
                count += valid
            self.assertEqual(repair.boundary_count(shells), count)
        self.assertEqual(repair.boundary_count(), 4373919)

    def test_all_minimum_tail_choices(self):
        for choice in range(256):
            x = list(repair.FRONTIER[0])
            y = list(repair.FRONTIER[1])
            changes = 0
            for i, r in enumerate(repair.CONFLICTS):
                word, depth = (y, 80-r) if choice >> i & 1 else (x, 99-r)
                self.assertEqual(word[depth-1], '+')
                word[depth-1] = '-'
                changes += 1
            self.assertEqual(changes, 8)
            self.assertTrue(all(x[98-r] != y[79-r] for r in range(1, 80)))

    def test_actual_fresh_scales_and_both_seed_edit_extremes(self):
        for k, choice in ((1, 0), (2, 85), (3, 255)):
            words, evidence = repair.construct(k, choice)
            self.assertEqual(len(evidence['retained_seed_changes']), 8)
            self.assertFalse(repair.top_differences(words))
            lengths = tuple(map(len, words))
            for d in range(1, 19):
                self.assertEqual(distance_difference(lengths, 19, -1, words, d), 0)
            self.assertEqual(distance_difference(lengths, 19, -1, words, 20), -1)
            for r in (1, 60, 61, 75, 79):
                self.assertEqual(distance_difference(lengths, 19, -1, words, lengths[0]+lengths[1]-r), 0)

    def test_residue_preserving_altered_witness_rejected(self):
        words, evidence = repair.construct()
        before = repair.class_totals(words)
        arm, depth, donor = evidence['exchanges'][0]
        words[arm-1][depth-1], words[arm-1][donor-1] = words[arm-1][donor-1], words[arm-1][depth-1]
        self.assertEqual(repair.class_totals(words), before)
        self.assertEqual(-1+sum(map(sum, words)), 0)
        self.assertTrue(repair.top_differences(words))

    def test_input_validation(self):
        for choice in (-1, 256, True, 1.5):
            with self.assertRaises(ValueError):
                repair.construct(1, choice)


if __name__ == '__main__':
    unittest.main()
