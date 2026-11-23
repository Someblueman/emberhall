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

    def test_background_is_one_shared_level(self):
        # Hand value for the 2x2 field (counts 100..103, var 2.0..2.3;
        # monitor 5000 var 100; ONE background level 3.0 var 0.05):
        # Var(mean rate) = (8.6/16 + 0.05)/5000^2 + (98.5/5000^2)^2 * 100.
        # The background variance enters whole (not /4) because the same
        # level is subtracted from every bin.
        _, _, background, rates, _ = build_field(rows=2, cols=2)
        self.assertEqual(background.size, 1)
        hand = 0.5875 / 25e6 + (98.5 / 25e6) ** 2 * 100
        self.assertAlmostEqual(rates.quadratic_form((0.25,) * 4), hand,
                               delta=1e-13)

    def test_field_shape(self):
        _, _, _, rates, weights = build_field()
        self.assertEqual(rates.size, 2000)
        self.assertAlmostEqual(sum(weights), 1.0)


if __name__ == "__main__":
    unittest.main()
