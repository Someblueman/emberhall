"""Original-tree metric checks, independent of the shell derivation."""
from collections import Counter
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import edge_dependent as ed
from unequal_spacing import full_partition


def direct_profile(subset):
    return dict(Counter(abs(p-q) if i == j else p+q
                        for k, (i, p) in enumerate(subset)
                        for j, q in subset[k+1:]))


class EdgeDependentTests(unittest.TestCase):
    def test_arbitrary_holes_identity_exhaustively(self):
        lengths = (2, 2, 1)
        vv = ed.vertices(lengths)
        for values in product((-1, 0, 1), repeat=len(vv)):
            if sum(values):
                continue
            signs = {v: s for v, s in zip(vv, values) if s}
            left = [v for v, s in signs.items() if s == 1]
            right = [v for v, s in signs.items() if s == -1]
            delta = ed.add(direct_profile(left), ed.shift(direct_profile(right), 0, -1))
            expected = ed.add(ed.shift(delta, 0, 2), ed.shift(delta, 1, -2))
            self.assertEqual(ed.shell_numerator(lengths, signs), expected, values)

    def test_general_edge_layers_match_the_fine_shell(self):
        lengths = (3, 2, 2)
        vv = ed.vertices(lengths)
        base = dict(zip(vv, (1, -1, -1, -1, -1, 1, 1, 1)))
        rng = random.Random(731)
        for factor in (3, 5, 7):
            for _ in range(8):
                rows = [(rng.choice(("parent", "child")),
                         {v: rng.choice((-1, 1)) for v in vv})
                        for r in range(factor-1)]
                fine, signs = ed.lift(lengths, base, rows)
                expected = ed.add(*({factor*k+r: c for k, c in poly.items()}
                                    for r, poly in enumerate(
                                        ed.layer_residuals(lengths, rows), 1)))
                self.assertEqual(ed.full_shell(fine, signs), expected)

    def test_strict_extension_and_positive_control(self):
        lengths = (3, 2, 2)
        vv = ed.vertices(lengths)
        base = dict(zip(vv, (1, -1, -1, -1, -1, 1, 1, 1)))
        seed = dict(zip(vv, (1, -1, -1, -1, 1, 1, -1, 1)))
        parent = tuple(base[(i, p-1) if p > 1 else (0, 0)] for i, p in vv[1:])
        child = tuple(base[v] for v in vv[1:])
        new = tuple(seed[v] for v in vv[1:])
        self.assertNotIn(new, (parent, child, tuple(-s for s in parent),
                               tuple(-s for s in child)))
        for field in (base, seed):
            self.assertEqual(sum(field.values()), 0)
            self.assertEqual(ed.full_shell(lengths, field), {})
        for endpoint in ("parent", "child"):
            rows = [(endpoint, seed), (endpoint, {v: -s for v, s in seed.items()})]
            self.assertEqual(not any(ed.layer_residuals(lengths, rows)), endpoint == "child")
        result = ed.demo()
        self.assertEqual(result["size"], 11)
        self.assertEqual(result["left_profile"], direct_profile(result["left"]))
        self.assertEqual(result["right_profile"], direct_profile(result["right"]))
        self.assertTrue(result["altered_pair_rejected"])
        words = ("+++"+"-"*11+"++++", "---"+"+"*7+"----", "+++")
        extra = {(0, 0): 1} | {(i, p): 1 if s == "+" else -1
                              for i, w in enumerate(words, 1) for p, s in enumerate(w, 1)}
        pair = ed.check_pair((18, 14, 3), [v for v, s in extra.items() if s == 1],
                             [v for v, s in extra.items() if s == -1])
        self.assertTrue(pair["homometric"])

    def test_arithmetic_certificates_and_coarse_seeds(self):
        self.assertEqual(ed.prove()["proof"], "PASS")
        for t in ed.prove()["remaining_residues_mod_165"]:
            small = ed.parameter_certificate(t)
            large = ed.parameter_certificate(t + 165*10**30)
            self.assertEqual(small["five_gcds"], large["five_gcds"])
            self.assertEqual(small["seven_gcds"], large["seven_gcds"])
            self.assertFalse(large["target_ruled_out"])
        for lengths in ((18, 3, 14), (13, 10, 2)):
            result = full_partition(*lengths)
            field = {**dict.fromkeys(result["left"], 1),
                     **dict.fromkeys(result["right"], -1)}
            self.assertFalse(ed.full_shell(lengths, field))
            c, _, u, _, _ = ed.components(lengths, field)
            self.assertTrue(ed.add(u, ed.shift(u, 1), ed.shift(c, 0, -1)))
            self.assertGreaterEqual(sum(sorted(lengths)[:2]), max(lengths)-1)
        bound = ed.odd_common_factor_bound((15, 9, 3))
        self.assertEqual(bound["upper_bound"], 13)
        self.assertFalse(bound["target_ruled_out"])
        self.assertTrue(ed.odd_common_factor_bound((3*10**30+3,)*3)["full_partition_impossible"])
        vv = ed.vertices((3, 3, 3))
        for tail in product((-1, 1), repeat=len(vv)-1):
            field = dict(zip(vv, (1,)+tail))
            if not sum(field.values()):
                left = [v for v, s in field.items() if s == 1]
                right = [v for v, s in field.items() if s == -1]
                self.assertNotEqual(direct_profile(left), direct_profile(right))

    def test_mixed_edges_escape_homometric_seed_class(self):
        lengths, _, seeds = ed.mixed_rows()
        self.assertTrue(all(ed.full_shell(lengths, seed) for seed in seeds))
        self.assertFalse(any(ed.layer_residuals(lengths, [("child", s) for s in seeds])))
        self.assertTrue(any(seeds[0][v] == seeds[1][v] for v in seeds[0] if v[0]))
        self.assertTrue(any(seeds[0][v] != seeds[1][v] for v in seeds[0] if v[0]))
        for factor in (3, 5, 11):
            result = ed.mixed_control(factor)
            self.assertTrue(result["homometric"])
            self.assertEqual(result["size"], result["target"])
            self.assertEqual(result["left_profile"], direct_profile(result["left"]))
        self.assertEqual(ed.mixed_control(5)["lengths"], (91, 71, 15))

    def test_input_boundaries(self):
        for lengths in ((True, 2, 1), (0, 2, 1), (2, 1)):
            with self.assertRaises(ValueError):
                ed.vertices(lengths)
        for t in (-1, True, 0.5):
            with self.assertRaises(ValueError):
                ed.parameter_certificate(t)
        for lengths in ((5, 3, 1), (6, 3, 3)):
            with self.assertRaises(ValueError):
                ed.odd_common_factor_bound(lengths)
        with self.assertRaises(ValueError):
            ed.shell_numerator((1, 1, 1), {(0, 0): 1})
        for left, right in (([(0, 0)]*2, [(1, 1), (2, 1)]),
                            ([(0, 0)], [(0, 0)]),
                            ([(True, 1)], [(2, 1)])):
            with self.assertRaises(ValueError):
                ed.check_pair((1, 1, 1), left, right)

    def test_real_cli_accepts_and_rejects(self):
        command = [sys.executable, str(Path(ed.__file__))]
        result = subprocess.run(command + ["--mixed-control", "5"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        pair = json.loads(result.stdout)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pair.json"
            path.write_text(json.dumps(pair))
            self.assertEqual(subprocess.run(command + ["--check", str(path)],
                                           capture_output=True).returncode, 0)
            pair["left"].remove([0, 0]); pair["left"].append([1, 91])
            path.write_text(json.dumps(pair))
            altered = subprocess.run(command + ["--check", str(path)],
                                     capture_output=True, text=True)
            self.assertEqual(altered.returncode, 1, altered.stderr)
            self.assertFalse(json.loads(altered.stdout)["homometric"])


if __name__ == "__main__":
    unittest.main()
