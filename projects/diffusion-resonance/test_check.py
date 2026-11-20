"""Cross-check the proof certificates with small spectra and exact path arithmetic."""

import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

import check


class DiffusionTest(unittest.TestCase):
    def test_reduction_preserves_known_cyclotomics(self):
        for order, coefficients in {
            1: (-1, 1), 6: (1, -1, 1), 8: (1, 0, 0, 0, 1), 10: (1, -1, 1, -1, 1),
            12: (1, 0, -1, 0, 1), 18: (1, 0, 0, -1, 0, 0, 1),
        }.items():
            with self.subTest(order=order):
                self.assertEqual(check.cyclotomic(order), coefficients)

    def test_grid_stability_for_rational_thresholds(self):
        for p, largest_admitted, first_excluded in (
            (2, "499/1000", "1/2"), (3, "249/1000", "1/4"),
            (4, "146/1000", "147/1000"), (5, "95/1000", "96/1000"),
            (6, "66/1000", "67/1000"),
        ):
            with self.subTest(p=p):
                self.assertTrue(check.stable(p, Fraction(largest_admitted)))
                self.assertFalse(check.stable(p, Fraction(first_excluded)))

    def test_two_points_integer_spectrum_at_each_cutoff(self):
        r = Fraction(1, 12)
        base = {1, 4}
        for m in range(2, 7):
            expected = {m + 3 * t for t in range(m + 1)}
            observed = {6 * check.rational_value(check.rate_sum(3, r, {1: m - t, 2: t}))
                        for t in range(m + 1)}
            self.assertEqual(observed, expected)
            self.assertEqual(base & observed, {4} if m == 4 else set())

    def test_two_point_shift_family_and_neighbors(self):
        for m in (4, 5, 6, 17, 1000):
            r = Fraction(m - 3, 4 * (m - 1))
            self.assertEqual(check.base_witness(3, r), (2, 1, m))
            self.assertEqual(check.rate_sum(3, r, {2: 1}), check.rate_sum(3, r, {1: m}))
        self.assertIsNone(check.base_witness(3, Fraction(1, 20)))

    def test_unshifted_witness_with_repeated_modes(self):
        for p in range(2, 25):
            answer = check.base_witness(p, Fraction(0))
            if p % 3:
                self.assertIsNone(answer)
            else:
                self.assertEqual(answer, (2 * p // 3, p // 3, 3))
                self.assertEqual(check.rate_sum(p, Fraction(0), {2 * p // 3: 1}),
                                 check.rate_sum(p, Fraction(0), {p // 3: 3}))

    def test_prime_orbit_certificates_on_composite_grids(self):
        for p, q in ((5, 5), (10, 5), (15, 3), (25, 5), (28, 7), (49, 7)):
            # sin(x) > 2x/pi for 0 < x < pi/2 implies s1 > 1/p².
            r = Fraction(1, 2 * p * p)
            self.assertTrue(check.stable(p, r))
            left, right = check.orbit_witness(p, r)
            h = (q - 1) // 2
            a, b = Fraction(q - 2, 4) - h * r, Fraction(q, 4) - h * r
            ratio = b / a
            self.assertEqual(sum(left.values()), ratio.numerator * h)
            self.assertEqual(sum(right.values()), ratio.denominator * h)
            self.assertEqual(check.rational_value(check.rate_sum(p, r, left)), ratio.numerator * a)
            self.assertEqual(check.rate_sum(p, r, left), check.rate_sum(p, r, right))
            left[p // q] -= 1
            self.assertNotEqual(check.rate_sum(p, r, left), check.rate_sum(p, r, right))
        for p in (2, 4, 8, 16, 32):
            self.assertIsNone(check.orbit_witness(p, Fraction(0)))

    def test_denominator_five_irrational_control_via_characteristic_polynomial(self):
        # For a path on four vertices, the eigenvalues of its adjacency matrix
        # satisfy (x² - x - 1)(x² + x - 1) = 0. Write x=(a+b sqrt(5))/2.
        # The two largest roots give the two slowest unshifted diffusion modes.
        for a, b, sign in ((1, 1, -1), (-1, 1, 1)):
            self.assertEqual((a*a + 5*b*b + 2*sign*a - 4, 2*a*b + 2*sign*b), (0, 0))
            # 24(s-r) = 6(2-x) - (7-3 sqrt(5)).
            self.assertEqual((12 - 3*a - 7, -3*b + 3), (2 if a == 1 else 8, 0))

    def test_public_commands(self):
        program = Path(__file__).with_name("check.py")
        def run(*args):
            return subprocess.run([sys.executable, "-O", str(program), *args],
                                  capture_output=True, text=True)
        examples = run()
        self.assertEqual(examples.returncode, 0, examples.stderr)
        self.assertIn("first overlap at 4", examples.stdout)
        self.assertIn("142 and 242 share 8591/100", examples.stdout)
        for p, r, text in (("3", "1/12", "b2 = 4 b1"), ("5", "1/50", "8591/100"),
                           ("8", "0", "All distinct levels are disjoint")):
            answer = run(p, r)
            self.assertEqual(answer.returncode, 0, answer.stderr)
            self.assertIn(text, answer.stdout)
        for args in (("2", "1/2"), ("3", "-1/6"), ("1", "0"), ("5",), ("5", "1/0")):
            self.assertEqual(run(*args).returncode, 2)


if __name__ == "__main__":
    unittest.main()
