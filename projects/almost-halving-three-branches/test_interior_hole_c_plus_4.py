"""Tests for interior_hole_c_plus_4: c=r+4 and period-7 c=15 families."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter, deque
from pathlib import Path

from interior_hole_c_plus_4 import (
    check_pair,
    construct_c_plus_4,
    construct_period7_c15,
    prove_c_plus_4_laurent,
    prove_period7_laurent,
    solve_tree,
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


class CPlusFourInteriorHoleTest(unittest.TestCase):
    def test_validation(self):
        for bad in [(3, 0), (6, 0), (5, -1), (4, 1)]:
            with self.assertRaises(ValueError):
                construct_c_plus_4(*bad)
        with self.assertRaises(ValueError):
            construct_period7_c15(-1)

    def test_symbolic_laurent_proofs_and_corruptions(self):
        res1 = prove_c_plus_4_laurent()
        self.assertEqual(res1["proof"], "PASS")
        self.assertEqual(res1["residual_terms"], 0)
        self.assertGreater(res1["corrupt_s0_terms"], 0)
        self.assertGreater(res1["corrupt_hole_terms"], 0)
        self.assertGreater(res1["corrupt_block_terms"], 0)

        res2 = prove_period7_laurent()
        self.assertEqual(res2["proof"], "PASS")
        self.assertEqual(res2["residual_terms"], 0)
        self.assertGreater(res2["corrupt_s0_terms"], 0)
        self.assertGreater(res2["corrupt_hole_terms"], 0)

    def test_c_plus_4_witnesses_and_bfs(self):
        cases = [(5, 0), (5, 2), (7, 0), (7, 3), (11, 0), (11, 18), (23, 0), (23, 6)]
        for r, k in cases:
            w = construct_c_plus_4(r, k)
            self.assertEqual(w["lengths"], [r * (k + 3) + 4, r * (k + 2) + 3, r + 4])
            self.assertTrue(w["homometric"])
            self.assertTrue(w["meets_target"])
            self.assertEqual(w["omitted"], [[1, r], [1, r * (k + 3) + 4]])
            lp = _bfs_profile(w["lengths"], w["left"])
            rp = _bfs_profile(w["lengths"], w["right"])
            self.assertEqual(lp, rp, (r, k))

    def test_period7_c15_witnesses_and_bfs(self):
        for k in (0, 1, 2, 5):
            w = construct_period7_c15(k)
            self.assertEqual(w["lengths"], [22 + 7 * k, 14 + 7 * k, 15])
            self.assertTrue(w["homometric"])
            self.assertTrue(w["meets_target"])
            lp = _bfs_profile(w["lengths"], w["left"])
            rp = _bfs_profile(w["lengths"], w["right"])
            self.assertEqual(lp, rp, k)

    def test_solve_tree_permutations_and_cli_rejection(self):
        w = solve_tree([15, 235, 223])
        self.assertEqual(w["lengths"], [15, 235, 223])
        self.assertTrue(w["homometric"])
        self.assertTrue(w["meets_target"])
        lp = _bfs_profile(w["lengths"], w["left"])
        rp = _bfs_profile(w["lengths"], w["right"])
        self.assertEqual(lp, rp)

        w99 = solve_tree([99, 79, 23])
        self.assertEqual((w99["r"], w99["k"]), (19, 2))
        self.assertTrue(w99["homometric"])
        self.assertEqual(_bfs_profile(w99["lengths"], w99["left"]),
                         _bfs_profile(w99["lengths"], w99["right"]))

        with self.assertRaises(ValueError):
            solve_tree([195, 139, 19])

        small = construct_c_plus_4(5, 0)
        bad_right = list(small["right"])
        idx = bad_right.index([0, 0])
        bad_right[idx] = [1, 5]
        bad = check_pair(small["lengths"], small["left"], bad_right)
        self.assertFalse(bad["homometric"])

        script = Path(__file__).with_name("interior_hole_c_plus_4.py")
        payload = json.dumps({
            "lengths": small["lengths"],
            "left": small["left"],
            "right": bad_right,
        })
        proc = subprocess.run(
            [sys.executable, str(script), "--check", "-"],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(json.loads(proc.stdout)["homometric"])


if __name__ == "__main__":
    unittest.main()
