import random
import subprocess
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

import native
from arithmetic import Binary, ONE, ZERO, family, matrix_trace, power
from check import check_family, check_matrix, check_native


class ArithmeticTests(unittest.TestCase):
    def test_ties_carry_and_gradual_underflow(self):
        fmt = Binary(3, -4, 4)
        for value, expected in ((F(9, 8), F(1)), (F(11, 8), F(3, 2)),
                                (F(15, 8), F(2)), (power(-7), F(0)),
                                (3 * power(-7), power(-5))):
            self.assertEqual(fmt.round(value), expected)
            self.assertEqual(fmt.round(-value), -expected)
        with self.assertRaises(OverflowError):
            fmt.round(F(32))

    def test_small_format_against_enumerated_nearest_values(self):
        fmt = Binary(3, -4, 3)
        positive = {F(k, 64) for k in range(4)}
        positive.update(m * power(e-2) for e in range(-4, 4) for m in range(4, 8))
        candidates = sorted(positive | {-value for value in positive})
        for k in range(-1792, 1793):
            value = F(k, 128)
            distances = [abs(value - candidate) for candidate in candidates]
            self.assertEqual(abs(value - fmt.round(value)), min(distances))

    def test_native_rounding_independent_sample(self):
        native.require_binary64()
        fmt = Binary(53, -1022, 1023)
        rng = random.Random(20261120)
        for _ in range(500):
            value = rng.randrange(-2**64, 2**64) * power(rng.randrange(-1100, 900))
            self.assertEqual(fmt.round(value), F.from_float(float(value)))

    def test_exact_transform_residuals(self):
        fmt = Binary(53, -1022, 1023)
        rng = random.Random(731)
        for _ in range(250):
            a = rng.randrange(-100000, 100000) * power(rng.randrange(-100, 50))
            b = rng.randrange(-100000, 100000) * power(rng.randrange(-100, 50))
            self.assertEqual(fmt.two_sum(a, b), native.exact(native.two_sum(float(a), float(b))))
            self.assertEqual(fmt.two_product(a, b),
                             native.exact(native.two_product(float(a), float(b))))

    def test_invalid_family_and_insufficient_range(self):
        for p, j in ((2, 0), (3, -1), (3, 8)):
            with self.assertRaises(ValueError):
                family(p, j)
        small, _ = family(53, 1)
        self.assertFalse(Binary(53, -100, 1023).valid(small))
        with self.assertRaises(ArithmeticError):
            Binary(3, -4, 4).two_product(power(-6), F(1, 2))

    def test_all_small_family_inputs_and_boundaries(self):
        self.assertEqual(sum(check_family(Binary(p, -3*p-4, 2), range(2**p))
                             for p in range(3, 9)), 504)
        fmt = Binary(53, -1022, 1023)
        self.assertTrue(fmt.valid(ONE))
        self.assertFalse(fmt.valid((F(1), power(-52))))

    def test_full_trace_exact_control_and_native_execution(self):
        fmt = Binary(53, -1022, 1023)
        trace = check_matrix(fmt, 1)
        self.assertEqual(len(trace), 16)
        self.assertEqual(sum(r['direction'] == 'reverse' for r in trace), 8)
        check_native([0, 1, 2**53-1], trace)
        zero_trace, result = matrix_trace(fmt, 0)
        self.assertEqual(result, [[ZERO, ZERO], [ZERO, ZERO]])
        self.assertTrue(all(r['after'] == r['expected'] for r in zero_trace))

    def test_documented_command(self):
        script = Path(__file__).with_name('check.py')
        result = subprocess.run([sys.executable, str(script)], text=True,
                                capture_output=True, check=True)
        self.assertIn('Final Z[0,0]=(-2^-163,0)', result.stdout)
        self.assertEqual(sum(line.startswith(('forward ', 'reverse '))
                             for line in result.stdout.splitlines()), 16)


if __name__ == '__main__':
    unittest.main()
