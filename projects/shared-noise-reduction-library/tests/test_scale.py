import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from covreduce.scale import build_field, run_comparison


class TestScale(unittest.TestCase):
    def test_small_field_sparse_equals_dense(self):
        result = run_comparison(rows=6, cols=5, draws=400)
        sparse, dense, mc = (result["sparse"][0], result["dense"][0],
                             result["monte_carlo"][0])
        self.assertAlmostEqual(sparse, dense, delta=dense * 1e-9)
        self.assertAlmostEqual(mc, dense, delta=dense * 0.25)

    def test_sparse_uses_less_memory_than_dense_at_scale(self):
        result = run_comparison(rows=23, cols=20, draws=50)
        self.assertLess(result["sparse"][2], result["dense"][2])

    def test_field_shape(self):
        _, _, _, rates, weights = build_field()
        self.assertEqual(rates.size, 2000)
        self.assertAlmostEqual(sum(weights), 1.0)


if __name__ == "__main__":
    unittest.main()
