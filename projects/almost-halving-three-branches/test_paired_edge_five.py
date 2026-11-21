import unittest

from mixed_edge_seven import _add, _mon, _mul, _scale, paired_residual
from paired_edge_five import (alternating_taylor_certificate, observed_mask, reduction,
                              reflection_cases, residue_system)


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

    def test_symbolic_residue_system_against_literal_edge_equations(self):
        p, q, odd = (1, 1, -1), (1, -1), (1, -1, -1)
        matrix, rhs = residue_system(p, q, odd)
        for h in (0, 1, 4):
            lengths = (6*h + 18, 6*h + 14, 6*h + 3)
            x = ([1 if k % 5 < 2 else -1 for k in range(lengths[0])],
                 [-1 if k % 7 < 3 else 1 for k in range(lengths[1])],
                 [odd[k % 3] for k in range(lengths[2])])
            eps = ([p[k % 3] * q[k % 2] for k in range(lengths[0])],
                   [q[k % 2] for k in range(lengths[1])],
                   [p[k % 3] for k in range(lengths[2])])
            y = [list(reversed([s*e for s, e in zip(arm, mask)]))
                 for arm, mask in zip(x, eps)]

            def specialize(poly):
                return _add(*(_scale(_mon(a=a+h*b), c)
                              for (a, b, _, _), c in poly.items()))

            numerators = []
            for arm in x[:2]:
                for r in range(6):
                    field = _add(*(_scale(_mon(a=k//6), s) for k, s in enumerate(arm)
                                   if k % 6 == r))
                    numerators.append(_mul(_add(_mon(), _scale(_mon(a=1), -1)), field))
            first, second = paired_residual(lengths, x, y)
            reversed_second = {sum(lengths) - 1 - k - 6*h: value
                               for k, value in second.items()}
            for row in range(12):
                r = row % 6
                literal = first if row < 6 else reversed_second
                actual = _add(*(_mul(specialize(coefficient), field)
                               for coefficient, field in zip(matrix[row], numerators)),
                              _scale(specialize(rhs[row]), -1))
                expected = _add(*(_scale(_mon(a=k//6), value)
                                  for k, value in literal.items() if k % 6 == r))
                expected = _mul(_add(_mon(), _scale(_mon(a=1), -1)), expected)
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
