"""Independent graph-distance controls for the short-arm-four family."""
import json
from itertools import combinations
from pathlib import Path
import subprocess
import sys
import unittest

import odd_spacing as os
import published_cases as pc
from test_next_family import counts, distances


class OddSpacingTest(unittest.TestCase):
    def test_exact_identity(self):
        self.assertEqual(os.symbolic_residual(), {})
        self.assertEqual(os.template_obstruction_identity(), {})

    def test_fresh_graphs(self):
        for b in (5, 7, 9, 13, 17, 23, 31, 47, 65):
            with self.subTest(b=b):
                result = os.four_short_witness(b)
                metric = distances(result["lengths"])
                left, right = result["left"], result["right"]
                self.assertEqual(len(left), (3 * b - 1) // 2)
                self.assertEqual(len(right), len(left))
                self.assertFalse(set(left) & set(right))
                self.assertEqual(set(metric) - set(left) - set(right), {(2,b-1),(2,b)})
                self.assertEqual(counts(left, metric), counts(right, metric))
                self.assertEqual(counts(left, metric), result["left_profile"])
        self.assertFalse(os.four_short_witness(5)["attains_bound"])
        self.assertFalse(os.four_short_witness(9)["attains_bound"])
        self.assertTrue(os.four_short_witness(13)["attains_bound"])

    def test_altered_pair(self):
        result = os.four_short_witness(17)
        left = list(result["left"])
        left[left.index((0, 0))] = (2, 16)
        self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_invalid_inputs(self):
        for b in (True, 0, 3, 6, 7.0, "7"):
            with self.subTest(b=b), self.assertRaises(ValueError):
                os.four_short_witness(b)

    def test_finite_search_and_its_failure_boundaries(self):
        for b, d in ((3, 1), (17, 5), (21, 13)):
            with self.subTest(b=b, d=d):
                result = os.search_prefix(b, d)
                self.assertEqual(result["search_status"], "found")
                metric = distances(result["lengths"])
                self.assertEqual(counts(result["left"], metric), counts(result["right"], metric))
                self.assertEqual(set(metric) - set(result["left"]) - set(result["right"]),
                                 {(2, b-1), (2, b)})
        limited = os.search_prefix(17, 5, max_nodes=1)
        self.assertEqual(limited["search_status"], "node-limit")
        self.assertEqual(limited["nodes"], 1)
        self.assertNotIn("homometric", limited)
        # No full partition of this retained prefix; no claim about other omissions.
        absent = os.search_prefix(7, 4)
        self.assertEqual(absent["search_status"], "no-prefix-pair")
        self.assertNotIn("meets_target", absent)
        for b, d, nodes in ((69, 1, 10), (5, 5, 10), (5, 1, 0), (True, 1, 10)):
            with self.subTest(b=b, d=d), self.assertRaises(ValueError):
                os.search_prefix(b, d, max_nodes=nodes)

    def test_search_agrees_with_exhaustive_small_colourings(self):
        for b in (3, 5):
            for d in range(1, b):
                metric = distances((b+d, b, b-d))
                vertices = set(metric) - {(2, b-1), (2, b)}
                others = sorted(vertices - {(0, 0)})
                size = len(vertices)//2
                exists = any(counts([(0, 0), *rest], metric)
                             == counts(list(vertices-set(rest)-{(0, 0)}), metric)
                             for rest in combinations(others, size-1))
                with self.subTest(b=b, d=d):
                    self.assertEqual(os.search_prefix(b, d)["search_status"] == "found", exists)

    def test_cli_round_trip(self):
        script = str(Path(os.__file__))
        run = subprocess.run([sys.executable, script, "13"],
                             capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(run.stdout)["size"], 19)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        proof = subprocess.run([sys.executable, script, "--prove"],
                               capture_output=True, text=True, check=True)
        self.assertIn("PASS", proof.stdout)
        invalid = subprocess.run([sys.executable, script, "4"],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        search = subprocess.run([sys.executable, script, "17", "--search-spacing", "5"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(search.stdout)["search_status"], "found")
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=search.stdout, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)


if __name__ == "__main__":
    unittest.main()
