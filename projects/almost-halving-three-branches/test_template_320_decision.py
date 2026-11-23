"""Independent checks for the 320 template decision."""
import copy
from itertools import product
import json
import random
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


# Core-certificate tests ported from preserved contribution 47252b6 and
# rebased onto the 372-row core of preserved contribution 1425cabb
# (commit 51525046). They are unittest methods on purpose: the house
# gate discovers this project with unittest, so module-level pytest
# functions would never be executed by the gate.


class CoreCertificateTests(unittest.TestCase):
    def test_template_shape_and_rows(self):
        rows, variables = decision.compiled_rows()
        self.assertEqual(decision.PERIOD, 320)
        self.assertEqual(decision.BASE, (427, 267, 211))
        self.assertEqual(decision.CUTS, (213, 133, 105))
        self.assertEqual(len(rows), 1981)
        self.assertEqual(len(variables), 1864)
        self.assertEqual(decision.rows_sha256(rows), decision.ROWS_SHA256)
        self.assertTrue(0 < len(decision.CORE_ROWS) < len(rows))
        self.assertEqual(list(decision.CORE_ROWS),
                         sorted(set(decision.CORE_ROWS)))


    def test_certificate_fields(self):
        cert = decision.certificate()
        self.assertIn("no signing", cert["external_exact_decision"])
        self.assertFalse(cert["template_existence_decided"])
        self.assertFalse(cert["general_target_decided"])
        self.assertEqual(cert["core_row_count"], len(decision.CORE_ROWS))
        self.assertEqual(cert["core_row_count"], 372)
        self.assertEqual(cert["core_variables"], 763)
        self.assertIn("468-row core", cert["core_provenance"])

    def test_random_signings_violate_core_rows_directly(self):
        # Independent of IntegerSearch: evaluate the integer rows by hand.
        rows, variables = decision.compiled_rows()
        ordered = list(rows.values())
        rng = random.Random(320)
        for _ in range(25):
            signs = [rng.choice((-1, 1)) for _ in variables]
            self.assertTrue(any(
                sum(a * signs[i] for i, a in ordered[j].items())
                for j in decision.CORE_ROWS))

    def test_original_tree_audit_rejects_fabricated_word(self):
        # A made-up word for this shape must fail coupled_word_completion's
        # independent original-tree distance audit, not only the row system.
        arms = []
        for length, cut in zip(decision.BASE, decision.CUTS):
            rest = length - cut
            arms.append([{"literal": "+" * cut}, {"repeat": "+" * decision.PERIOD},
                         {"literal": "+" * (rest - 1)}])
        # Match SHAPES segment sizes exactly: rebuild from SHAPES.
        arms = [[{kind: "+" * size} for kind, size in arm]
                for arm in decision.SHAPES]
        word = {"format": coupled.FORMAT, "centre": 1,
                "period": decision.PERIOD, "arms": arms}
        with self.assertRaises(ValueError):
            coupled.verify_word(word)
        with self.assertRaises(ValueError):
            coupled.audit_word(word, 0)
        # The known control word still passes the same machinery.
        self.assertIs(coupled.verify_word(coupled.control())["valid"], True)
        self.assertTrue(coupled.audit_word(coupled.control(), 1)
                        ["equal_distance_multisets"])

    def test_tampered_certificates_rejected(self):
        cert = decision.certificate()
        tampers = []
        bad = copy.deepcopy(cert); bad["template_existence_decided"] = True
        tampers.append(bad)
        bad = copy.deepcopy(cert); bad["rows_sha256"] = "0" * 64; tampers.append(bad)
        bad = copy.deepcopy(cert); bad["core_rows"] = bad["core_rows"][:-1]
        bad["core_row_count"] -= 1; tampers.append(bad)
        bad = copy.deepcopy(cert); bad["general_target_decided"] = True
        tampers.append(bad)
        bad = copy.deepcopy(cert); bad["period"] = 321; tampers.append(bad)
        bad = copy.deepcopy(cert); bad["replay"]["conflicts"] += 1; tampers.append(bad)
        for bad in tampers:
            with self.assertRaises(ValueError):
                decision.verify_certificate(bad)

    def test_full_replay_matches_recorded_cap(self):
        result = decision.verify_certificate(decision.certificate())
        self.assertIs(result["valid"], True)
        self.assertEqual(result["status"], "resource_limit")
        self.assertFalse(result["template_existence_decided"])
        self.assertFalse(result["general_target_decided"])

    # The 372-row core and its exact replay anchor, rebased from the
    # preserved contribution 1425cabb (commit 51525046).

    def test_core_rows_are_sorted_unique_subset(self):
        self.assertEqual(len(decision.CORE_ROWS), 372)
        self.assertEqual(tuple(sorted(set(decision.CORE_ROWS))),
                         decision.CORE_ROWS)
        declared = decision.core_rows_declared()
        rows, _, _, _ = decision.rows_for_template()
        keys = list(rows)
        self.assertEqual(declared, [keys[j] for j in decision.CORE_ROWS])
        core_vars = {i for d in declared for i in rows[d]}
        self.assertEqual(len(core_vars), 763)

    def test_core_replay_anchor_is_deterministic(self):
        report = decision.certificate()
        self.assertEqual(report["format"], decision.CORE_FORMAT)
        self.assertEqual(report["core_row_count"], 372)
        self.assertEqual(report["core_variables"], 763)
        self.assertEqual(report["replay"], decision.REPLAY)
        self.assertEqual(report["replay"]["max_conflicts"], 20000)
        self.assertEqual(report["replay"]["conflicts"], 20000)
        self.assertEqual(report["replay"]["decisions"], 28144)
        self.assertEqual(report["replay"]["maximum_depth"], 46)
        self.assertEqual(report["replay"]["integer_reasons"], 461782)
        self.assertFalse(report["template_existence_decided"])
        self.assertFalse(report["general_target_decided"])
        self.assertEqual(decision.certificate(), report)

    def test_core_reject_tampered_fields(self):
        report = decision.certificate()
        for key, value in (("core_row_count", 467),
                           ("core_variables", 1101),
                           ("base_lengths", [427, 267, 212]),
                           ("rows_sha256", "0" * 64),
                           ("core_provenance", "edited")):
            damaged = dict(report, **{key: value})
            with self.assertRaises(ValueError):
                decision.verify_certificate(damaged)

    def test_real_cli_core_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "core.json"
            command = [sys.executable, str(Path(decision.__file__))]
            result = subprocess.run(
                command + ["--core", "--write", str(path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            saved = json.loads(path.read_text())
            self.assertEqual(saved["replay"], decision.REPLAY)
            self.assertEqual(saved["core_row_count"], 372)
            result = subprocess.run(
                command + ["--verify-core", str(path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            saved["replay"]["conflicts"] = 0
            path.write_text(json.dumps(saved))
            result = subprocess.run(
                command + ["--verify-core", str(path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
