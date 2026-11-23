"""Pin the sparse-vs-dense scale claim at a suite-sized field.

At 600 elements (20x30, one shared monitor, one shared background level)
the sparse quadratic form must equal the dense-covariance value, while
the dense route's tracemalloc peak must exceed the sparse peak by a
wide, measurement-backed margin (observed ~290x and ~410x at 600 and
1000 elements on the verifying machine; pinned at 20x so the test
tracks the algorithmic gap, not one machine).  Seeded Monte Carlo must
land within 25% of the dense value (observed ~6%).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce.scale import run_comparison


class TestScaleVerify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_comparison(rows=20, cols=30, draws=300, seed=7)

    def test_sparse_equals_dense_value(self):
        sparse, dense = self.result["sparse"][0], self.result["dense"][0]
        self.assertAlmostEqual(sparse, dense, delta=dense * 1e-9)

    def test_dense_peak_far_exceeds_sparse_peak(self):
        sparse_peak = self.result["sparse"][2]
        dense_peak = self.result["dense"][2]
        self.assertLess(sparse_peak, 2 ** 20)  # sparse stays under 1 MiB
        self.assertGreaterEqual(dense_peak, 20 * sparse_peak)

    def test_monte_carlo_within_tolerance_of_dense(self):
        dense, mc = self.result["dense"][0], self.result["monte_carlo"][0]
        self.assertAlmostEqual(mc, dense, delta=dense * 0.25)


if __name__ == "__main__":
    unittest.main()
