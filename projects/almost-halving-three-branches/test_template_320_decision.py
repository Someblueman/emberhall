"""Independent checks for the 320 template decision."""
import copy
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import coupled_word_completion as coupled
import integer_template_decision as prior
import template_320_decision as decision
from test_word_frontier import graph_data, profile


class Template320Tests(unittest.TestCase):
    def test_engine_matches_exhaustive_on_small_systems(self):
        self.assertFalse(
            decision.run_exact(prior.IntegerSearch({0: {0: 1}}, 1), None))
        self.assertFalse(
            decision.run_exact(
                prior.IntegerSearch({0: {0: 1, 1: 3}}, 2), None))
        import random
        rng = random.Random(320427)
        for _ in range(60):
            size = rng.randrange(2, 8)
            rows = {k: {i: a for i in range(size)
                        if (a := rng.randrange(-3, 4))}
                    for k in range(rng.randrange(1, 7))}
            for row in rows.values():
                if sum(row.values()) % 2:
                    row[0] = row.get(0, 0) + 1
                    if not row[0]:
                        del row[0]
            expected = any(
                all(sum(row.get(i, 0) * sign for i, sign in enumerate(signs))
                    == 0 for row in rows.values())
                for tail in product((-1, 1), repeat=size - 1)
                for signs in [(1,) + tail])
            engine = prior.IntegerSearch(rows, size)
            self.assertEqual(decision.run_exact(engine, None), expected, rows)
            if expected:
                self.assertTrue(all(
                    sum(a * -engine.values[i + 1] for i, a in row.items())
                    == 0 for row in rows.values()))

    def test_original_tree_census_for_fresh_unequal_triples(self):
        for lengths in ((4, 2, 1), (5, 3, 1), (7, 4, 2)):
            shapes = [[("literal", a - (i < 2))]
                      for i, a in enumerate(lengths)]
            rows, variables, _, _ = coupled.compile_shape(1, shapes)
            engine = prior.IntegerSearch(rows, len(variables))
            result = decision.run_exact(engine, None)
            vertices, pairs = graph_data(lengths)
            expected = any(
                sum(signs) == 0 and not any(
                    profile(signs, pairs).values())
                for tail in product((-1, 1), repeat=len(vertices) - 1)
                for signs in [(1,) + tail])
            self.assertEqual(result, expected)
            if result:
                values = {(0, 0): 1}
                for index, (arm, _, letter) in enumerate(variables[1:], 2):
                    values[arm, letter + (2 if arm < 3 else 1)] = (
                        -engine.values[index])
                signs = [values[v] for v in vertices]
                self.assertEqual(sum(signs), 0)
                self.assertFalse(any(profile(signs, pairs).values()))

    def test_control_word_audit_and_damage(self):
        original = coupled.control()
        report = coupled.verify_word(original)
        self.assertTrue(report["all_nonnegative_repetitions"])
        for count in (0, 1, 4):
            audit = coupled.audit_word(original, count)
            self.assertTrue(audit["equal_distance_multisets"])
            self.assertEqual(audit["target"], audit["size"])
        damaged = coupled.control()
        damaged["arms"][0][1]["literal"] = "+--+"
        with self.assertRaises(ValueError):
            coupled.verify_word(damaged)
        with self.assertRaises(ValueError):
            coupled.audit_word(damaged, 0)

    def test_limit_receipt_and_tampered_fields(self):
        receipt = decision.solve_exact(1)
        self.assertEqual(receipt["status"], "resource_limit")
        self.assertFalse(receipt["template_existence_decided"])
        self.assertNotIn("exists", receipt)
        self.assertFalse(
            decision.verify(receipt)["template_existence_decided"])
        self.assertEqual(receipt["coefficient_rows"], 1981)
        self.assertEqual(receipt["sign_variables"], 1864)
        for key, value in (("status", "exact"), ("exists", False),
                           ("period", 319),
                           ("prefix_lengths", [212, 133, 105]),
                           ("general_target_decided", True),
                           ("conflicts", 0)):
            damaged = dict(receipt, **{key: value})
            with self.assertRaises(ValueError):
                decision.verify(damaged)

    def test_rows_are_unmodified(self):
        rows, variables, base, growth = decision.rows_for_template()
        other, other_vars, other_base, other_growth = (
            coupled.compile_shape(prior.PERIOD, prior.SHAPES))
        self.assertEqual(rows, other)
        self.assertEqual(variables, other_vars)
        self.assertEqual(base, other_base)
        self.assertEqual(growth, other_growth)
        self.assertEqual(len(rows), 1981)
        self.assertEqual(decision.separating_repeat_count(rows), 4)

    def test_real_cli_keeps_limit_inconclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            command = [sys.executable, str(Path(decision.__file__))]
            result = subprocess.run(
                command + ["--solve", "--max-conflicts", "1",
                           "--write", str(path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            result = subprocess.run(
                command + ["--verify", str(path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            saved = json.loads(path.read_text())
            saved["exists"] = False
            path.write_text(json.dumps(saved))
            result = subprocess.run(
                command + ["--verify", str(path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
