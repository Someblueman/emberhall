"""Original-tree checks of the whole-family polynomial, including damaged input."""
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import coupled_word_completion as coupled
from test_word_frontier import graph_data, profile


class CoupledWordTests(unittest.TestCase):
    def test_every_symbolic_coefficient_against_original_tree(self):
        rng = random.Random(614)
        for segments in (
            [[("literal", 3), ("repeat", 2), ("literal", 2)],
             [("literal", 2), ("repeat", 2)], [("literal", 1)]],
            [[("literal", 2), ("repeat", 2), ("literal", 1), ("repeat", 2)],
             [("literal", 1), ("repeat", 2), ("literal", 1)],
             [("repeat", 2), ("literal", 1)]],
        ):
            for _ in range(4):
                saved = {"format": coupled.FORMAT, "centre": rng.choice((-1, 1)),
                         "period": 2, "arms": [
                             [{kind: "".join(rng.choice("+-") for _ in range(size))}
                              for kind, size in arm] for arm in segments]}
                rows, _, base, growth, values = coupled.parse_word(saved)
                for n in (0, 1, 3):
                    lengths = tuple(a + 2 * r * n for a, r in zip(base, growth))
                    vertices, pairs = graph_data(lengths)
                    words = coupled.expand_word(saved, n)
                    signs = {(0, 0): saved["centre"]}
                    for arm, word in enumerate(words, 1):
                        signs.update({(arm, d): 1 if ch == "+" else -1
                                      for d, ch in enumerate(word, 2 if arm < 3 else 1)})
                    literal = [signs[v] for v in vertices]
                    delta = profile(literal, pairs)
                    shell = {d: 2 * (delta[d + 1] - delta[d])
                             - (2 * sum(literal) if d == 0 else 0)
                             for d in range(sum(lengths[:2]) + 1)}
                    expected = {}
                    for d, value in shell.items():
                        expected[d] = expected.get(d, 0) + value
                        expected[d + 2] = expected.get(d + 2, 0) - value
                    actual = {}
                    for (z, v), row in rows.items():
                        d = z + 2 * n * v
                        actual[d] = actual.get(d, 0) + sum(a * values[i] for i, a in row.items())
                    self.assertEqual({d: a for d, a in actual.items() if a},
                                     {d: a for d, a in expected.items() if a})

    def test_known_infinite_family_and_independent_distances(self):
        saved = coupled.control()
        report = coupled.verify_word(saved)
        self.assertEqual(report["growth_per_repeat"], [4, 0, 0])
        for n in (0, 1, 7, 23):
            audit = coupled.audit_word(saved, n)
            self.assertEqual(audit["lengths"], [5 + 4 * n, 4, 2])
            self.assertEqual(audit["size"], 5 + 2 * n)
            self.assertEqual(audit["pairs_per_set"], (5 + 2 * n) * (4 + 2 * n) // 2)
        for n in (-1, True):
            with self.assertRaises(ValueError):
                coupled.audit_word(saved, n)
        with self.assertRaises(ValueError):
            coupled.audit_word(saved, 1000000)

    def test_valid_base_word_is_not_a_family_certificate(self):
        saved = coupled.control()
        saved["arms"][0][0]["repeat"] = "++++"
        self.assertTrue(coupled.audit_word(saved, 0)["equal_distance_multisets"])
        with self.assertRaisesRegex(ValueError, "family coefficient"):
            coupled.verify_word(saved)
        with self.assertRaises(ValueError):
            coupled.audit_word(saved, 1)

    def test_global_contradiction_replays_without_a_search(self):
        saved = coupled.target_probe()
        self.assertEqual(saved["sign_variables"], 736)
        self.assertEqual(len(saved["contradiction"]["xor_rows"]), 364)
        self.assertFalse(saved["target_existence_decided"])
        lengths, cuts = saved["base_lengths"], saved["prefix_lengths"]
        shapes = [[("literal", k), ("repeat", 24), ("literal", a - (i < 2) - k)]
                  for i, (a, k) in enumerate(zip(lengths, cuts))]
        rows = list(coupled.compile_shape(24, shapes)[0].values())
        parity, rhs = set(), 0
        for i in saved["contradiction"]["xor_rows"]:
            parity.symmetric_difference_update(j for j, a in rows[i].items() if a % 2)
            rhs ^= (sum(rows[i].values()) // 2) % 2
        self.assertEqual((parity, rhs), (set(), 1))

    def test_strict_input_and_altered_sign_rejection(self):
        for change in (lambda x: x.update(extra=True), lambda x: x.update(centre=True),
                       lambda x: x.update(period=0), lambda x: x["arms"][0][0].update(repeat="+x++"),
                       lambda x: x["arms"][0][0].update(repeat="+")):
            saved = coupled.control()
            change(saved)
            with self.assertRaises(ValueError):
                coupled.verify_word(saved)
        saved = coupled.control()
        saved["arms"][0][1]["literal"] = "+--+"  # swap signs, preserving both sizes
        with self.assertRaises(ValueError):
            coupled.verify_word(saved)
        with self.assertRaises(ValueError):
            coupled.audit_word(saved, 0)

    def test_real_cli_and_altered_obstruction_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certificate.json"
            script = str(Path(coupled.__file__))
            for option in ("--control", "--target-template"):
                result = subprocess.run([sys.executable, script, option, "--write", str(path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run([sys.executable, script, "--verify", str(path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            saved = json.loads(path.read_text())
            saved["contradiction"]["xor_rows"].pop()
            path.write_text(json.dumps(saved))
            result = subprocess.run([sys.executable, script, "--verify", str(path)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("altered", result.stderr)


if __name__ == "__main__":
    unittest.main()
