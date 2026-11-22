"""Independent finite censuses and replay boundaries for the integer search."""
import copy
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import coupled_word_completion as coupled
import integer_template_decision as decision
from test_word_frontier import graph_data, profile


class IntegerTemplateTests(unittest.TestCase):
    def test_every_integer_reason_is_implied_by_its_row(self):
        checked = []

        class AuditedSearch(decision.IntegerSearch):
            def integer_reason(self, number, forced=None):
                clause = super().integer_reason(number, forced)
                row = self.rows[number]
                columns = sorted(row)
                for bits in product((False, True), repeat=len(columns)):
                    values = dict(zip(columns, bits))
                    if sum(a * (1 - 2 * values[i]) for i, a in row.items()) == 0:
                        assert any(values[abs(lit) - 1] == (lit > 0) for lit in clause)
                checked.append(clause)
                return clause

        rng = random.Random(213)
        for _ in range(80):
            rows = {j: {i: weight * rng.choice((-1, 1))
                        for i, weight in enumerate((1, 1, 2, 2, 1, 1))}
                    for j in range(6)}
            AuditedSearch(rows, 6).solve(10000)
        self.assertGreater(len(checked), 30)

    def test_integer_solver_against_exhaustive_signs(self):
        self.assertFalse(decision.IntegerSearch({0: {0: 1}}, 1).solve(10))
        # Even total and consistent parity do not make the integer row feasible.
        self.assertFalse(decision.IntegerSearch({0: {0: 1, 1: 3}}, 2).solve(10))
        rng = random.Random(320427)
        for _ in range(120):
            size = rng.randrange(2, 9)
            rows = {k: {i: a for i in range(size)
                        if (a := rng.randrange(-3, 4))}
                    for k in range(rng.randrange(1, 9))}
            # Avoid making most negative controls trivial odd-total rows.
            for row in rows.values():
                if sum(row.values()) % 2:
                    row[0] = row.get(0, 0) + 1
                    if not row[0]:
                        del row[0]
            expected = any(all(sum(row.get(i, 0) * sign for i, sign in enumerate(signs)) == 0
                               for row in rows.values())
                           for tail in product((-1, 1), repeat=size - 1)
                           for signs in [(1,) + tail])
            engine = decision.IntegerSearch(rows, size)
            self.assertEqual(engine.solve(10000), expected, rows)
            if expected:
                self.assertTrue(all(sum(a * -engine.values[i + 1] for i, a in row.items()) == 0
                                    for row in rows.values()))

    def test_original_tree_census_for_fresh_unequal_triples(self):
        for lengths in ((4, 2, 1), (5, 3, 1), (7, 4, 2), (8, 5, 2)):
            shapes = [[("literal", a - (i < 2))] for i, a in enumerate(lengths)]
            rows, variables, _, _ = coupled.compile_shape(1, shapes)
            engine = decision.IntegerSearch(rows, len(variables))
            result = engine.solve(100000)
            vertices, pairs = graph_data(lengths)
            expected = any(sum(signs) == 0 and not any(profile(signs, pairs).values())
                           for tail in product((-1, 1), repeat=len(vertices) - 1)
                           for signs in [(1,) + tail])
            self.assertEqual(result, expected)
            if result:
                values = {(0, 0): 1}
                for index, (arm, _, letter) in enumerate(variables[1:], 2):
                    values[arm, letter + (2 if arm < 3 else 1)] = -engine.values[index]
                signs = [values[v] for v in vertices]
                self.assertEqual(sum(signs), 0)
                self.assertFalse(any(profile(signs, pairs).values()))

    def test_repeated_positive_and_size_preserving_damage(self):
        original = coupled.control()
        rows, variables, _, _, _ = coupled.parse_word(original)
        engine = decision.IntegerSearch(rows, len(variables))
        self.assertTrue(engine.solve(10000))
        saved = copy.deepcopy(original)
        for index, (arm, segment, letter) in enumerate(variables):
            if arm:
                item = saved["arms"][arm - 1][segment]
                kind, word = next(iter(item.items()))
                word = word[:letter] + ("+" if engine.values[index + 1] < 0 else "-") + word[letter + 1:]
                item[kind] = word
        self.assertTrue(coupled.verify_word(saved)["all_nonnegative_repetitions"])
        for repeat in (0, 1, 7):
            self.assertTrue(coupled.audit_word(saved, repeat)["equal_distance_multisets"])
        damaged = coupled.control()
        damaged["arms"][0][1]["literal"] = "+--+"
        with self.assertRaises(ValueError):
            coupled.verify_word(damaged)
        with self.assertRaises(ValueError):
            coupled.audit_word(damaged, 0)

    def test_limit_and_tampered_receipts(self):
        receipt = decision.solve(1)
        self.assertEqual(receipt["status"], "resource_limit")
        self.assertFalse(receipt["template_existence_decided"])
        self.assertNotIn("exists", receipt)
        self.assertFalse(decision.verify(receipt)["template_existence_decided"])
        for key, value in (("status", "exact"), ("prefix_lengths", [212, 133, 105]),
                           ("general_target_decided", True), ("conflicts", 0)):
            damaged = dict(receipt, **{key: value})
            with self.assertRaises(ValueError):
                decision.verify(damaged)
        for invalid in (0, -1, True, 1000001):
            with self.assertRaises(ValueError):
                decision.IntegerSearch({0: {0: 1, 1: 1}}, 2).solve(invalid)

    def test_pointwise_obstruction_and_changed_certificate(self):
        saved = decision.known_obstruction()
        self.assertEqual(saved["z_span"], 558)
        self.assertEqual(saved["separating_repeat_count"], 24)
        self.assertTrue(saved["signs_may_depend_on_repetition"])
        self.assertTrue(decision.verify(saved)["valid"])
        for target in (1, 2, 101):
            repeat = 315 * target - 5
            self.assertGreater(24 * repeat, saved["z_span"])
            self.assertEqual([a + 24 * repeat for a in saved["base_lengths"]],
                             [a + 7560 * target for a in (227, 67, 11)])
            self.assertEqual((sum(saved["base_lengths"]) + 72 * repeat - 1) // 2,
                             332 + 36 * repeat)
        for field in ("separating_repeat_count", "z_span"):
            damaged = dict(saved, **{field: saved[field] - 1})
            with self.assertRaises(ValueError):
                decision.verify(damaged)
        damaged = copy.deepcopy(saved)
        damaged["contradiction"]["xor_rows"].pop()
        with self.assertRaises(ValueError):
            decision.verify(damaged)

    def test_real_cli_keeps_limit_inconclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            command = [sys.executable, str(Path(decision.__file__))]
            result = subprocess.run(command + ["--solve", "--max-conflicts", "1", "--write", str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            result = subprocess.run(command + ["--verify", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            saved = json.loads(path.read_text())
            saved["exists"] = False
            path.write_text(json.dumps(saved))
            result = subprocess.run(command + ["--verify", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
