"""Literal paired equations check the corrected sixteen-field model."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
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

    def test_new_family_identity_and_changed_sign(self):
        self.assertFalse(any(fields.family_proof().values()))
        patterns = list(fields.FAMILY_EDGES)
        prefix, block, tail = patterns[0]
        patterns[0] = (("+" if prefix[0] == "-" else "-")+prefix[1:], block, tail)
        self.assertTrue(any(fields.family_proof(patterns).values()))
        for t in (9, 27, 36, 531):
            k = fields.family_parameter(t)
            self.assertEqual(36*(k+1), 1064*t)
        for bad in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                fields.family_pair(bad)
        for bad in (0, 6, 12, True):
            with self.assertRaises(ValueError):
                fields.family_parameter(bad)

    def test_new_family_original_tree_distances(self):
        from edge_dependent import graph_counts
        from paired_edge_five import distance_profile
        for k in (0, 1, 2):
            pair = fields.family_pair(k)
            lengths, left, right = pair["lengths"], pair["left"], pair["right"]
            self.assertFalse(set(left) & set(right))
            self.assertEqual(len(left), 358+270*k)
            self.assertEqual(len(left), len(right))
            self.assertEqual(set(pair["omitted"]), {(1, lengths[0]), (2, lengths[1])})
            a, b = graph_counts(lengths, left), graph_counts(lengths, right)
            self.assertEqual(a, b)
            packed = distance_profile(lengths, left)
            self.assertEqual(a, {d: n for d, n in enumerate(packed) if n})
            coarse, x, y = fields.family_rows(k)
            self.assertEqual(original_equations(tuple(map(len, coarse)),
                             [[1 if s == "+" else -1 for s in row] for row in x],
                             [[1 if s == "+" else -1 for s in row] for row in y]), [{}, {}])

    def test_new_family_real_cli_rejects_altered_pair(self):
        script = str(Path(fields.__file__))
        with TemporaryDirectory() as directory:
            saved = Path(directory)/"pair.json"
            run = subprocess.run([sys.executable, script, "--family-k", "0", "--witness", str(saved)],
                                 capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(run.stdout)["meets_target"])
            pair = json.loads(saved.read_text())
            pair["left"].remove([0, 0])
            pair["left"].append([1, pair["lengths"][0]])
            saved.write_text(json.dumps(pair))
            altered = subprocess.run([sys.executable, script, "--check", str(saved)],
                                     capture_output=True, text=True)
            self.assertEqual(altered.returncode, 1, altered.stderr)
            self.assertFalse(json.loads(altered.stdout)["homometric"])
            saved.write_text("{}")
            malformed = subprocess.run([sys.executable, script, "--check", str(saved)],
                                       capture_output=True, text=True)
            self.assertEqual(malformed.returncode, 2)
            invalid = subprocess.run([sys.executable, script, "--family-t", "12"],
                                     capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 2)

    def test_parity_certificates_and_corruption(self):
        self.assertEqual(fields.parity_proof(), {
            1: {"modulus": 3, "necessary_residues": [0]},
            3: {"modulus": 5, "necessary_residues": []},
            7: {"modulus": 5, "necessary_residues": [1]}})
        from copy import deepcopy
        for part in ("weights", "lift"):
            damaged = deepcopy(fields.PARITY_CERTIFICATES)
            if part == "weights":
                damaged[1][part] = ("",)+damaged[1][part][1:]
            else:
                damaged[1][part] = "0,0,1"
            with self.assertRaises(ArithmeticError):
                fields.parity_proof(damaged)
        run = subprocess.run([sys.executable, str(Path(fields.__file__)), "--prove-parity"],
                             capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(run.stdout)["3"]["necessary_residues"], [])

    def test_all_remaining_paired_rows_are_excluded(self):
        self.assertTrue(fields.constant_mask_proof())
        proof = fields.obstruction_proof()
        self.assertEqual(len(proof["excluded_residues_mod_495"]), 48)
        self.assertIn(15, proof["excluded_residues_mod_495"])
        self.assertNotIn(36, proof["excluded_residues_mod_495"])
        self.assertFalse(proof["original_target_ruled_out"])

    def test_interior_identity_and_new_affine_class(self):
        self.assertFalse(fields.interior_proof())
        changed = list(fields.INTERIOR_FAMILY)
        prefix, block, tail = changed[1]
        changed[1] = (prefix, ("-" if block[0] == "+" else "+")+block[1:], tail)
        self.assertTrue(fields.interior_proof(changed))
        residues = fields.obstruction_proof()["excluded_residues_mod_495"]
        for residue in residues:
            t = residue or 495
            k = fields.interior_parameter(t)
            self.assertEqual(203+56*k, 91+5320*t)
            self.assertEqual(183+56*k, 71+5320*t)
            self.assertEqual(127+56*k, 15+5320*t)
        self.assertEqual(fields.interior_parameter(1), 93)
        for bad in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                fields.interior_pair(bad)
        for bad in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                fields.interior_parameter(bad)

    def test_interior_family_uses_original_tree_distances(self):
        from edge_dependent import graph_counts
        from paired_edge_five import check_pair
        for k in (0, 1, 3):
            pair = fields.interior_pair(k)
            ns, left, right = pair["lengths"], pair["left"], pair["right"]
            self.assertEqual(set(pair["omitted"]), {(1, 19), (1, ns[0])})
            self.assertFalse(set(left) & set(right))
            self.assertEqual(len(left), 256+84*k)
            self.assertEqual(len(left), len(right))
            self.assertEqual(graph_counts(ns, left), graph_counts(ns, right))
            self.assertTrue(check_pair(pair)["meets_target"])
            changed = {**pair, "left": [v for v in left if v != (0, 0)]+[(1, 19)]}
            self.assertEqual(len(changed["left"]), len(left))
            self.assertFalse(set(changed["left"]) & set(right))
            self.assertFalse(check_pair(changed)["homometric"])
        run = subprocess.run([sys.executable, str(Path(fields.__file__)), "--prove-interior"],
                             capture_output=True, text=True, check=True)
        self.assertFalse(json.loads(run.stdout)["universal_milestone_solved"])
        with TemporaryDirectory() as directory:
            saved = Path(directory)/"interior.json"
            subprocess.run([sys.executable, str(Path(fields.__file__)), "--interior-k", "1",
                            "--witness", str(saved)], capture_output=True, text=True, check=True)
            checked = subprocess.run([sys.executable, str(Path(fields.__file__)), "--check", str(saved)],
                                     capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(checked.stdout)["homometric"])
            damaged = json.loads(saved.read_text())
            damaged["left"].remove([0, 0])
            damaged["left"].append([1, 19])
            saved.write_text(json.dumps(damaged))
            rejected = subprocess.run([sys.executable, str(Path(fields.__file__)), "--check", str(saved)],
                                      capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1)

    def test_bipartition_holes_have_only_five_even_offsets(self):
        result = fields.bipartition_hole_proof()
        self.assertTrue(result["all_even_offsets_exhausted"])
        self.assertTrue(result["affine_parity_colouring_excluded"])
        self.assertFalse(result["original_target_ruled_out"])
        self.assertEqual([case["offset"] for case in result["cases"]], [18, 22, 40, 60, 78])
        from edge_dependent import graph_counts
        from paired_edge_five import check_pair
        for case in result["cases"]:
            ns, holes = case["lengths"], set(case["omitted"])
            left = [(0, 0)]+[(i, d) for i, n in enumerate(ns, 1) for d in range(2, n+1, 2)]
            right = [(i, d) for i, n in enumerate(ns, 1)
                     for d in range(1, n+1, 2) if (i, d) not in holes]
            pair = {"lengths": ns, "left": left, "right": right}
            self.assertEqual(len(left), len(right))
            self.assertFalse(set(left) & set(right))
            self.assertEqual(graph_counts(ns, left), graph_counts(ns, right))
            self.assertTrue(check_pair(pair)["meets_target"])
            # Move an omitted odd vertex into B, taking a different odd vertex
            # out. Sizes, parity and disjointness survive; homometry does not.
            changed = list(right)
            changed.remove(changed[0])
            changed.append(next(iter(holes)))
            self.assertFalse(check_pair({**pair, "right": changed})["homometric"])
        run = subprocess.run([sys.executable, str(Path(fields.__file__)),
                              "--prove-bipartition-holes"],
                             capture_output=True, text=True, check=True)
        self.assertFalse(json.loads(run.stdout)["original_target_ruled_out"])

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
