"""Original-tree checks of the coprime theorem, including every small word."""
from itertools import product
import json
from math import gcd
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import published_cases as pc
import unrestricted_path_transfer as up
from test_next_family import counts, distances


class UnrestrictedPathTransferTest(unittest.TestCase):
    def test_formal_identity_and_wrong_sign(self):
        self.assertEqual(up.constant_tail_identity(), {})
        self.assertTrue(up.constant_tail_identity(-1))
        self.assertEqual(up.elimination_identity(), {})
        self.assertTrue(up.elimination_identity(1))

    def test_all_small_unrestricted_words_by_graph_distances(self):
        checked = 0
        for r, b, c in product(range(1, 5), range(1, 4), range(1, 7)):
            cp, m = up.parameters(r, b, c)
            rigid = gcd(b, r) == gcd(b, cp+1) == 1
            metric = distances((b+r+1, b, c))
            found = 0
            for half in product("+-", repeat=m//2):
                central = "".join(half) + "".join("-" if s == "+" else "+" for s in half[::-1])
                for tail in map("".join, product("+-", repeat=b)):
                    pair = up.word_pair(r, b, c, central, tail)
                    self.assertEqual(up.reflection_transfer_identity(r, central, tail), {})
                    lp, rp = counts(pair["left"], metric), counts(pair["right"], metric)
                    self.assertEqual(pair["homometric"], lp == rp)
                    self.assertEqual(pair["transfer_residual"],
                                     {d: 2*(lp[d]-rp[d]) for d in lp.keys() | rp.keys()
                                      if lp[d] != rp[d]})
                    if lp == rp:
                        found += 1
                        if rigid:
                            self.assertEqual(len(set(tail)), 1)
                            self.assertTrue(pair["anti_periodic"])
                    checked += 1
            feasible = b % r == 0 or (cp % r == 0 and (cp//r % 2 == 1 or b % 2 == 0))
            self.assertEqual(found > 0, feasible, (r, b, c))
            if rigid:
                self.assertEqual(found, 2 if feasible else 0, (r, b, c))
        self.assertGreater(checked, 500)

    def test_fresh_positive_parameters_and_original_omissions(self):
        for r, b, c in ((3, 7, 9), (5, 11, 25), (4, 13, 20),
                        (2, 11, 6), (3, 11, 10), (1, 7, 2),
                        (3, 6, 1), (4, 6, 8), (4, 2, 1)):
            pair = up.construct_pair(r, b, c)
            metric = distances(pair["lengths"])
            self.assertEqual(counts(pair["left"], metric), counts(pair["right"], metric))
            self.assertFalse(set(pair["left"]) & set(pair["right"]))
            self.assertEqual(set(metric)-set(pair["left"])-set(pair["right"]), set(pair["omitted"]))
            self.assertEqual(pair["size"], pair["target"])

    def test_infinite_obstruction_classes_and_scope(self):
        for t in range(15):
            for b in (6*t+1, 6*t+5):
                result = up.classify(3, b, 1)
                self.assertEqual(result["status"], "obstructed")
                self.assertFalse(result["old_template_admitted"])
                self.assertFalse(result["universal_tripod_obstruction"])
            # This even b is outside the rigid class but inside the root class.
            result = up.classify(3, 6*t+2, 1)
            self.assertEqual(result["status"], "obstructed")
            self.assertFalse(result["constant_tails_proved_necessary"])
        # The unchanged default supplies target sets even on this obstruction.
        left, right = pc.path_pair((9, 5, 1))
        self.assertTrue(pc.check_pair((9, 5, 1), left, right)["meets_target"])

    def test_non_antiperiodic_solution_outside_rigidity_hypothesis(self):
        pair = up.word_pair(2, 7, 6, "+--+-++-", "-+--+-+")
        self.assertTrue(pair["homometric"])
        self.assertFalse(pair["anti_periodic"])
        self.assertEqual(up.classify(2, 7, 6)["status"], "constructible")
        self.assertFalse(up.classify(2, 7, 6)["constant_tails_proved_necessary"])
        self.assertEqual(up.classify(3, 2, 5)["status"], "obstructed")
        self.assertTrue(up.old_admission(2, 7, 6))  # New word, no new triple coverage.
        metric = distances(pair["lengths"])
        self.assertEqual(counts(pair["left"], metric), counts(pair["right"], metric))

    def test_changed_tail_preserves_sizes_but_fails(self):
        pair = up.word_pair(2, 7, 6, "+--+-++-", "++--+-+")
        self.assertFalse(pair["homometric"])
        self.assertTrue(pair["transfer_residual"])
        self.assertEqual(pair["size"], pair["target"])
        self.assertFalse(set(pair["left"]) & set(pair["right"]))

    def test_input_boundaries(self):
        for triple in ((True, 1, 1), (1, 0, 1), (2, 1, -1), (2, 1.0, 2)):
            with self.assertRaises(ValueError):
                up.classify(*triple)
        for central, tail in (("++++", "+"), ("++--", "0"), ("+-", "+")):
            with self.assertRaises(ValueError):
                up.word_pair(3, 1, 1, central, tail)

    def test_real_commands_and_independent_checker_rejection(self):
        script = str(Path(up.__file__))
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory)/"pair.json")
            run = subprocess.run([sys.executable, script, "3", "7", "9", "--witness", path],
                                 text=True, capture_output=True, check=True)
            self.assertTrue(json.loads(run.stdout)["homometric"])
            checker = [sys.executable, str(Path(pc.__file__)), "--check", path]
            self.assertEqual(subprocess.run(checker, capture_output=True).returncode, 0)
            data = json.loads(Path(path).read_text())
            data["left"][0] = data["omitted"][0]
            Path(path).write_text(json.dumps(data))
            self.assertEqual(subprocess.run(checker, capture_output=True).returncode, 1)
        proof = subprocess.run([sys.executable, script, "--prove"], capture_output=True, check=True)
        self.assertIn(b"PASS", proof.stdout)
        invalid = subprocess.run([sys.executable, script, "3", "5", "1",
                                  "--central=++--", "--tail=+++++"], capture_output=True)
        self.assertEqual(invalid.returncode, 1)
        self.assertEqual(subprocess.run([sys.executable, script, "--prove", "1"],
                                       capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
