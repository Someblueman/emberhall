"""Literal paired equations check the corrected sixteen-field model."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import unittest

import unrestricted_odd_fields as fields


def original_equations(ns, x, y):
    answer = []
    for first, second in ((x, y), (y, x)):
        row = Counter()
        for arm, n in enumerate(ns):
            for j in range(n):
                row[j] += first[arm][j]
                for other in range(3):
                    if other != arm:
                        row[j+ns[other]] -= first[arm][j]
                row[n-1-j] -= second[arm][j]
        answer.append({j: v for j, v in row.items() if v})
    return answer


class UnrestrictedOddTests(unittest.TestCase):
    def test_root_elimination_does_not_force_whole_odd_row(self):
        self.assertFalse(any(fields.root_identity()))
        self.assertEqual(len(fields.masks()), 12)
        for p, q in fields.masks():
            columns, matrix, rhs = fields.corrected_system(p, q)
            self.assertEqual(len(columns), 16)
            self.assertEqual(len(matrix), 12)
            self.assertTrue(all(len(row) == 16 for row in matrix))
            self.assertEqual(sum(arm == 2 for arm, r in columns), 4)
            self.assertEqual(len(rhs), 12)

    def test_every_mask_against_literal_edge_equations(self):
        for h in (0, 3, 8):
            ns = fields.lengths(h)
            for p, q in fields.masks():
                phase = p.index(-1)
                for known_sign in (-1, 1):
                    x = [[1 if (j*j+3*j+arm) % 7 < 3 else -1 for j in range(n)]
                         for arm, n in enumerate(ns)]
                    for j in range(phase, ns[2], 3):
                        x[2][j] = known_sign
                    eps = ([p[j % 3]*q[j % 2] for j in range(ns[0])],
                           [q[j % 2] for j in range(ns[1])],
                           [p[j % 3] for j in range(ns[2])])
                    y = [list(reversed([a*b for a, b in zip(row, mask)]))
                         for row, mask in zip(x, eps)]
                    first, second = original_equations(ns, x, y)
                    reversed_second = {sum(ns)-1-j-6*h: v for j, v in second.items()}
                    actual = fields.field_residuals(h, p, q, x)
                    for row, polynomial in enumerate(actual):
                        literal = first if row < 6 else reversed_second
                        before = {(j//6, 0): v for j, v in literal.items() if j % 6 == row % 6}
                        expected = fields.multiply(before, {(0, 0): 1, (1, 0): -1})
                        self.assertEqual(polynomial, expected, (h, p, q, known_sign, row))

    def test_actual_affine_nonperiodic_counterexample_is_admitted(self):
        result = fields.counterexample_check(850)
        self.assertEqual(result["lengths"], (25554, 25550, 25539))
        self.assertEqual(result["residual_coefficients"], 0)
        self.assertFalse(result["whole_odd_row_has_period_three"])
        self.assertFalse(result["remaining_24_classes_solved"])

    def test_invalid_masks_and_fixed_component(self):
        with self.assertRaises(ValueError):
            fields.corrected_system((-1, -1, -1), (1, 1))
        for h in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                fields.lengths(h)
        x, _ = fields.nonperiodic_rows(0)
        x = [[1 if c == "+" else -1 for c in row] for row in x]
        x[2][1] *= -1
        with self.assertRaises(ValueError):
            fields.field_residuals(6, (1, -1, 1), (1, 1), x)

    def test_mask_certificates_and_corruption(self):
        self.assertEqual(fields.prove_seven_masks(), (0, 2, 4, 5, 6, 8, 9))
        for p, q in fields.masks():
            if q != (-1, -1):
                continue
            _, rows = fields.endpoint_system(p, q)
            steps, terminal = fields.endpoint_certificate(rows)
            self.assertTrue(fields.verify_endpoint_certificate(rows, (steps, terminal)))
            altered = list(steps)
            row, key, value = altered[0]
            altered[0] = (row, key, -value)
            self.assertFalse(fields.verify_endpoint_certificate(rows, (altered, terminal)))
        _, rows = fields.endpoint_system((1, -1, 1), (1, 1))
        self.assertIsNone(fields.endpoint_certificate(rows))

    def test_linear_combination_certificates_reject_corruption(self):
        _, rows = fields.endpoint_system(*fields.masks()[2])
        derived, weights = fields.linear_consequences(rows)
        self.assertTrue(fields.verify_linear_consequences(rows, derived, weights))
        damaged = list(derived)
        a, b, c, row, target = damaged[0]
        damaged[0] = (a, b, c, row, target+1)
        self.assertFalse(fields.verify_linear_consequences(rows, damaged, weights))

    def test_endpoint_rows_match_original_equations(self):
        p, q = (1, -1, 1), (-1, -1)
        columns, rows = fields.endpoint_system(p, q)
        for h in (100, 131):
            ns = fields.lengths(h)
            x = [[1 if (j*j+arm) % 7 < 3 else -1 for j in range(n)]
                 for arm, n in enumerate(ns)]
            for j in range(1, ns[2], 3):
                x[2][j] = 1
            eps = ([p[j % 3]*q[j % 2] for j in range(ns[0])],
                   [q[j % 2] for j in range(ns[1])],
                   [p[j % 3] for j in range(ns[2])])
            y = [list(reversed([a*b for a, b in zip(row, mask)]))
                 for row, mask in zip(x, eps)]
            first, second = original_equations(ns, x, y)
            reversed_second = {sum(ns)-1-j-6*h: v for j, v in second.items()}
            for equation, alpha, beta, row, target in rows:
                actual = sum(c*x[columns[column][0]][6*(power*h+offset)+columns[column][1]]
                             for (column, power, offset), c in row.items())-target
                expected = (first if equation < 6 else reversed_second).get(
                    6*(alpha*h+beta)+equation % 6, 0)
                self.assertEqual(actual, expected)

    def test_real_cli(self):
        script = str(Path(fields.__file__))
        result = subprocess.run([sys.executable, script, "--counterexample-k", "850"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["residual_coefficients"], 0)
        invalid = subprocess.run([sys.executable, script, "--h", "-1"],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)


if __name__ == "__main__":
    unittest.main()
