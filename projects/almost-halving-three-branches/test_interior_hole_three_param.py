"""Tests for interior_hole_three_param: three-parameter family & escape taxonomy."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter, deque
from pathlib import Path

from interior_hole_three_param import (
    classify_euler_escapes,
    check_pair,
    construct_three_param,
    prove_symbolic_identity,
    solve_tree,
    target_size,
    validate_parameters,
)


def _bfs_profile(lengths, vertices):
    """Independent BFS pairwise distance counter on the original tripod."""
    adj = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        prev = (0, 0)
        for d in range(1, length + 1):
            v = (arm, d)
            adj.setdefault(v, [])
            adj[prev].append(v)
            adj[v].append(prev)
            prev = v
    verts = [tuple(v) for v in vertices]
    dists = {}
    for src in verts:
        dist = {src: 0}
        q = deque([src])
        while q:
            u = q.popleft()
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        dists[src] = dist
    counts = Counter()
    for i, u in enumerate(verts):
        for w in verts[i + 1 :]:
            counts[dists[u][w]] += 1
    return counts


class ThreeParamInteriorHoleTest(unittest.TestCase):
    def test_parameter_validation(self):
        self.assertEqual(validate_parameters(1, 1, 0), (1, 1, 0))
        self.assertEqual(validate_parameters(23, 3, 6), (23, 3, 6))
        for bad in [(4, 1, 0), (5, 2, 0), (5, 7, 0), (5, 1, -1), (0, 1, 0)]:
            with self.assertRaises(ValueError):
                validate_parameters(*bad)

    def test_symbolic_laurent_identity_and_corruptions(self):
        res = prove_symbolic_identity()
        self.assertEqual(res["proof"], "PASS")
        self.assertEqual(res["residual_terms"], 0)
        self.assertGreater(res["corrupt_s0_terms"], 0)
        self.assertGreater(res["corrupt_hole_terms"], 0)
        self.assertGreater(res["corrupt_block_terms"], 0)
        self.assertTrue(res["specialization_matches_difference"])

    def test_small_and_frontier_cases_bfs(self):
        cases = [
            (1, 1, 0),
            (3, 1, 0),
            (3, 3, 2),
            (7, 3, 0),
            (7, 3, 1),
            (11, 7, 0),
            (11, 7, 18),   # (227, 215, 7)
            (15, 7, 1),
            (23, 3, 6),    # (187, 163, 3)
            (23, 19, 6),   # (203, 179, 19)
        ]
        for r, c, k in cases:
            w = construct_three_param(r, c, k)
            lengths = w["lengths"]
            self.assertTrue(w["homometric"], (r, c, k))
            self.assertTrue(w["meets_target"], (r, c, k))
            self.assertEqual(w["size"], target_size(lengths))
            self.assertEqual(len(w["left"]), len(w["right"]))
            self.assertFalse(set(map(tuple, w["left"])) & set(map(tuple, w["right"])))
            lp = _bfs_profile(lengths, w["left"])
            rp = _bfs_profile(lengths, w["right"])
            self.assertEqual(lp, rp, (r, c, k))
            self.assertEqual({str(d): cnt for d, cnt in sorted(lp.items())},
                             {str(d): cnt for d, cnt in w["left_profile"].items()})

    def test_solve_tree_arm_permutations_and_rejections(self):
        w = solve_tree([19, 203, 179])
        self.assertEqual(w["lengths"], [19, 203, 179])
        self.assertTrue(w["homometric"])
        self.assertTrue(w["meets_target"])
        lp = _bfs_profile(w["lengths"], w["left"])
        rp = _bfs_profile(w["lengths"], w["right"])
        self.assertEqual(lp, rp)
        with self.assertRaises(ValueError):
            solve_tree([99, 79, 23])

    def test_altered_pair_rejected_by_check_and_cli(self):
        w = construct_three_param(7, 3, 0)
        altered_right = list(w["right"])
        # Replace centre [0, 0] with omitted interior hole [1, 7].
        idx = altered_right.index([0, 0])
        altered_right[idx] = [1, 7]
        bad = check_pair(w["lengths"], w["left"], altered_right)
        self.assertFalse(bad["homometric"])
        self.assertEqual(bad["size"], w["size"])

        script = Path(__file__).with_name("interior_hole_three_param.py")
        payload = json.dumps({
            "lengths": w["lengths"],
            "left": w["left"],
            "right": altered_right,
        })
        proc = subprocess.run(
            [sys.executable, str(script), "--check", "-"],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertFalse(out["homometric"])

    def test_euler_escape_taxonomy_small(self):
        tax = classify_euler_escapes(max_a=120)
        self.assertEqual(tax["even_sum_euler_escapes"], 0)
        self.assertGreater(tax["odd_sum_euler_escapes"], 0)
        self.assertEqual(tax["grid_total"], 346)
        self.assertEqual(tax["grid_settled"], 346)


if __name__ == "__main__":
    unittest.main()
