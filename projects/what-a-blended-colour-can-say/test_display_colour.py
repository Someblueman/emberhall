"""Transfer/rounding boundaries checked without floating-point reference code."""
from fractions import Fraction as F
import unittest

import display_colour as dc


class DisplayTests(unittest.TestCase):
    def test_black_white_and_known_srgb_midpoint(self):
        for mode in dc.MODES:
            self.assertEqual(dc.encode_rgb((F(0), F(1), F(0)), mode), (0, 255, 0))
        self.assertEqual(dc.encode_channel(F(1, 2), 'srgb8'), 188)
        self.assertEqual(dc.encode_channel(F(1, 2), 'linear8'), 128)

    def test_all_linear_half_ties_round_up_and_adjacent_values(self):
        for q in range(255):
            tie = F(2 * q + 1, 510)
            self.assertEqual(dc.encode_channel(tie, 'linear8'), q + 1)
            self.assertEqual(dc.encode_channel(tie - F(1, 10**9), 'linear8'), q)
            self.assertEqual(dc.encode_channel(tie + F(1, 10**9), 'linear8'), q + 1)

    def test_srgb_linear_branch_half_tie_and_nonlinear_exact_power(self):
        tie = F(3, 510) / F(323, 25)
        self.assertEqual(dc.encode_channel(tie), 2)
        self.assertEqual(dc.encode_channel(tie - F(1, 10**10)), 1)
        # x = t**12 gives an exact rational nonlinear encoding 1.055*t**5-.055.
        t = F(9, 10)
        encoded = F(211, 200) * t**5 - F(11, 200)
        expected = (encoded * 255 + F(1, 2)).numerator // (encoded * 255 + F(1, 2)).denominator
        self.assertEqual(dc.encode_channel(t**12), expected)
        for x in (dc.LINEAR_CUTOFF - F(1, 10**10), dc.LINEAR_CUTOFF, dc.LINEAR_CUTOFF + F(1, 10**10)):
            self.assertEqual(dc.encode_channel(x), 10)

    def test_all_byte_enclosures_have_rigorous_inverse_endpoints(self):
        for q in range(256):
            lo, hi = dc.channel_box(q)
            for encoded, lower in ((max(F(0), F(2*q-1, 510)), True),
                                   (min(F(1), F(2*q+1, 510)), False)):
                bound = lo if lower else hi
                if encoded <= F(809, 20000):
                    self.assertEqual(bound, encoded / F(323, 25))
                else:
                    target = ((200 * encoded + 11) / 211)**12
                    epsilon = F(1, 2**64)
                    if lower:
                        self.assertLessEqual(bound**5, target)
                        self.assertGreaterEqual((bound + epsilon)**5, target)
                    else:
                        self.assertGreaterEqual(bound**5, target)
                        self.assertLessEqual((bound - epsilon)**5, target)

    def test_rational_samples_are_inside_their_observation_boxes(self):
        for mode in dc.MODES:
            for numerator in range(1001):
                x = F(numerator, 1000)
                lo, hi = dc.channel_box(dc.encode_channel(x, mode), mode)
                self.assertLessEqual(lo, x)
                self.assertLessEqual(x, hi)

    def test_unsupported_or_invalid_inputs_fail(self):
        for mode in ('gamma22', 'display-p3', '', None):
            with self.assertRaises(ValueError):
                dc.encode_channel(F(1, 2), mode)
        for value in (-1, 256, True, F(1), 1.2):
            with self.assertRaises(ValueError):
                dc.channel_box(value)
        for value in (-F(1, 9), F(10, 9)):
            with self.assertRaises(ValueError):
                dc.encode_channel(value)
        with self.assertRaises(ValueError):
            dc.observation_box((128, 128))


if __name__ == '__main__':
    unittest.main()
