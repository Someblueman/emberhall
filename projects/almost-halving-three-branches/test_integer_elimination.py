"""Exhaustive inverse checks and independent original-tree distance controls."""
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import coupled_word_completion as coupled
import integer_elimination as elimination
from test_word_frontier import graph_data, profile


class IntegerEliminationTests(unittest.TestCase):
    def assert_exact_sign_bijection(self, rows, size):
        reduction = elimination.Reduction(rows, size)
        self.assertTrue(reduction.validate())
        expected = {signs for signs in product((-1, 1), repeat=size)
                    if all(sum(a * signs[i] for i, a in row.items()) == 0 for row in rows)}
        actual = set()
        for free in product((-1, 1), repeat=len(reduction.parameters)):
            try:
                full = tuple(reduction.lift_parameters(list(free)))
            except ValueError:
                continue
            self.assertEqual([full[i] for i in reduction.parameters], list(free))
            actual.add(full)
        self.assertEqual(actual, expected)
        return reduction

    def test_exhaustive_small_integer_systems(self):
        rng = random.Random(18641981)
        controls = [([], 3), ([{}], 2), ([{0: 1}], 1),
                    ([{0: 3, 1: 2, 2: 2}], 3),
                    ([{0: 2, 1: 1, 2: 1}], 3),
                    ([{0: 5, 1: 2, 2: 2, 3: 1}], 4),
                    ([{0: 1, 1: 1}, {1: 1, 2: -1}, {0: 1, 2: -1}], 3)]
        for rows, size in controls:
            self.assert_exact_sign_bijection(rows, size)
        for _ in range(75):
            size = rng.randrange(2, 8)
            rows = [{i: a for i in range(size) if (a := rng.randrange(-3, 4))}
                    for _ in range(rng.randrange(1, 8))]
            self.assert_exact_sign_bijection(rows, size)

    def test_fresh_unequal_tripods_against_breadth_first_distances(self):
        for lengths in ((6, 3, 2), (7, 3, 1), (8, 4, 3)):
            shape = [[("literal", a - (i < 2))] for i, a in enumerate(lengths)]
            rows, variables, _, _ = coupled.compile_shape(1, shape)
            reduction = elimination.Reduction(list(rows.values()), len(variables))
            self.assertTrue(reduction.validate())
            vertices, pairs = graph_data(lengths)
            expected = set()
            for signs in product((-1, 1), repeat=len(vertices)):
                if not sum(signs) and not any(profile(signs, pairs).values()):
                    expected.add(signs)
            actual = set()
            for free in product((-1, 1), repeat=len(reduction.parameters)):
                try:
                    actual.add(tuple(reduction.lift_parameters(list(free))))
                except ValueError:
                    pass
            self.assertEqual(actual, expected)

    def test_repeated_control_and_size_preserving_damage(self):
        reduction, _ = elimination.build(control=True)
        _, _, _, _, original = coupled.parse_word(coupled.control())
        full = reduction.lift([original[i] for i in reduction.free])
        self.assertEqual(full, original)
        word = elimination.word_from_signs(full, control=True)
        for n in (0, 2, 9):
            lengths = (5 + 4 * n, 4, 2)
            vertices, pairs = graph_data(lengths)
            expanded = coupled.expand_word(word, n)
            signs = {(0, 0): word["centre"]}
            for arm, text in enumerate(expanded, 1):
                signs.update({(arm, d): 1 if s == "+" else -1
                              for d, s in enumerate(text, 2 if arm < 3 else 1)})
            values = [signs[v] for v in vertices]
            self.assertEqual(sum(values), 0)
            self.assertFalse(any(profile(values, pairs).values()))
        damaged = full[:]
        plus, minus = damaged.index(1), damaged.index(-1)
        damaged[plus], damaged[minus] = -1, 1
        with self.assertRaises(ValueError):
            elimination.word_from_signs(damaged, control=True)

    def test_invalid_free_signs_and_altered_reduction(self):
        reduction = self.assert_exact_sign_bijection([{0: 2, 1: 1, 2: 1}], 3)
        for values in ([1, -1], [True, 1], [1], [1, 0]):
            with self.assertRaises(ValueError):
                reduction.lift(values)
        reduction.equations[0][1] += 1
        with self.assertRaises(ValueError):
            reduction.validate()
        _, receipt = elimination.build(control=True)
        self.assertTrue(elimination.verify(receipt)["valid"])
        for key, value in (("rational_rank", 0), ("free_signs", []),
                           ("template_existence_decided", True), ("extra", 1)):
            with self.assertRaises(ValueError):
                elimination.verify(dict(receipt, **{key: value}))

    def test_target_exact_rank(self):
        reduction, report = elimination.build()
        self.assertEqual((report["sign_variables"], report["coefficient_rows"]), (1864, 1981))
        self.assertEqual(report["pair_identifications"], 115)
        self.assertEqual(report["rational_rank"], 1656)
        self.assertEqual(len(reduction.free), 208)
        self.assertEqual(len(reduction.parity), 5)
        self.assertEqual(reduction.congruence, (0, 541, 5))
        self.assertEqual(len(reduction.parameters), 202)
        self.assertFalse(report["template_existence_decided"])
        exported = reduction.export()
        self.assertEqual(len(exported["equations"]), 1541)
        damaged = json.loads(json.dumps(exported))
        damaged["equations"][0][1][0][1] += 1
        self.assertNotEqual(elimination.digest(damaged), report["equations_sha256"])

    def test_actual_cli_replay_lift_and_tampering(self):
        command = [sys.executable, str(Path(elimination.__file__))]
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.json"
            free = Path(directory) / "free.json"
            word = Path(directory) / "word.json"
            result = subprocess.run(command + ["--control", "--reduce", "--write", str(receipt)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run(command + ["--verify", str(receipt)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            free.write_text("[-1]\n")
            result = subprocess.run(command + ["--control", "--lift", str(free),
                                               "--audit-repeat", "9", "--write", str(word)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(word.read_text())["audit"]["equal_distance_multisets"])
            saved = json.loads(receipt.read_text())
            saved["equations_sha256"] = "0" * 64
            receipt.write_text(json.dumps(saved))
            result = subprocess.run(command + ["--verify", str(receipt)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
