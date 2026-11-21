import unittest

from mixed_edge_seven import paired_residual
from paired_edge_five import alternating_taylor_certificate, observed_mask, reduction, reflection_cases


class FiveReductionTests(unittest.TestCase):
    def test_exact_cubic_certificate(self):
        self.assertTrue(alternating_taylor_certificate())

    def test_mask_list_is_complete_and_distinct(self):
        cases = reflection_cases()
        self.assertEqual(len(cases), 16)
        self.assertEqual(len({(c["odd"], c["middle"]) for c in cases}), 16)
        for case in cases:
            p, q = case["odd"], case["middle"]
            self.assertEqual(p[0] * p[1] * p[2], -1)
            self.assertEqual(case["long"], tuple(p[k % 3] * q[k % 2] for k in range(6)))

    def test_partial_status_on_every_missing_class(self):
        parameters = [t for t in range(165) if t % 3 == 0 and t % 15 != 3
                      and t % 11 not in (1, 6, 9)]
        self.assertEqual(len(parameters), 32)
        for t in parameters + [165 * 100003]:
            result = reduction(t)
            self.assertEqual(result["remaining_mask_word_combinations"], 48)
            self.assertFalse(result["paired_edge_assignment_excluded"])
            self.assertEqual(len(result["remaining_reflection_masks"]), 12)

    def test_real_base_pair_survives_the_reduction(self):
        # Independently found finite control; this is not a construction for t>0.
        words = (
            ("+-+-+++-+-+---+---", "-+++-+-+++-+++", "+--"),
            ("--+-+--++-+++++-++", "-+---+-----+--", "+-+"),
        )
        x, y = (tuple(tuple(1 if s == "+" else -1 for s in word) for word in row)
                for row in words)
        self.assertEqual(paired_residual((18, 14, 3), x, y), ({}, {}))
        mask = observed_mask(x, y)
        self.assertIn(mask, reduction(0)["remaining_reflection_masks"])
        self.assertEqual(x[2], (1, -1, -1))
        bad = [list(word) for word in y]
        bad[0][0] *= -1
        self.assertTrue(any(paired_residual((18, 14, 3), x, bad)))

    def test_domain_rejections(self):
        for t in (-1, True, 0.5, 1, 3, 6, 9):
            with self.assertRaises(ValueError):
                reduction(t)


if __name__ == "__main__":
    unittest.main()
