"""Reproduce CONTRACT.md's first-order validity bounds.

Products are checked against the exact independent-product variance;
the small-r quotient against seeded Monte Carlo. These tests pin the
numbers a user reads in the contract, not new library behaviour.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce import source
from covreduce.baselines import monte_carlo_covariance


def _product(r):
    a = source(100.0, (100.0 * r) ** 2)
    b = source(2.0, (2.0 * r) ** 2)
    exact = (100.0 ** 2 * (2.0 * r) ** 2 + 2.0 ** 2 * (100.0 * r) ** 2
             + (100.0 * r) ** 2 * (2.0 * r) ** 2)
    return (a * b).variance, exact


class TestFirstOrderBounds(unittest.TestCase):
    def test_product_error_small_at_r_0_1(self):
        fo, exact = _product(0.10)
        self.assertLess(abs(fo - exact) / exact, 0.01)

    def test_product_error_large_at_r_0_5(self):
        fo, exact = _product(0.50)
        self.assertLess(fo, exact)  # always an underestimate
        self.assertGreater((exact - fo) / exact, 0.10)

    def test_quotient_agrees_with_mc_at_r_0_01(self):
        a = source(100.0, 1.0 ** 2)
        b = source(50.0, 0.5 ** 2)
        fo = (a / b).variance
        mc = monte_carlo_covariance(
            [a, b], lambda f: (f[0][0] / f[1][0],),
            draws=8000, seed=7)[0][0]
        self.assertLess(abs(fo - mc) / mc, 0.05)

    def test_linear_ops_exact_at_large_r(self):
        a = source(100.0, 50.0 ** 2)
        b = source(2.0, 1.0 ** 2)
        self.assertAlmostEqual((a + b).variance, 50.0 ** 2 + 1.0 ** 2)


if __name__ == "__main__":
    unittest.main()
