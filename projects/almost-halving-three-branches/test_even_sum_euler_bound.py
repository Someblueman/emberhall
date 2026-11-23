"""Tests for even_sum_euler_bound: c=1,2 halving, 13-shift CRT bound, and T(1932211,1377448,7)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter, deque
from pathlib import Path

from even_sum_euler_bound import (
    SMALLEST_FOUND_ESCAPE,
    audit_small_range,
    check_pair,
    construct_c12_even_sum,
    prove_prime_shift_bound,
    verify_thirteen_trim_escape,
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


class EvenSumEulerBoundTest(unittest.TestCase):
    def test_c12_even_sum_validation_and_bfs(self):
        for bad in [(4, 4, 1), (4, 3, 2), (5, 4, 3), (0, 2, 1)]:
            with self.assertRaises(ValueError):
                construct_c12_even_sum(*bad)

        cases = [(1, 1, 2), (4, 3, 1), (7, 2, 1), (4, 2, 2), (5, 3, 2), (10, 8, 2), (17, 12, 1)]
        for a, b, c in cases:
            w = construct_c12_even_sum(a, b, c)
            self.assertTrue(w["homometric"])
            self.assertTrue(w["meets_target"])
            expected = (a + b + c) // 2 if c == 1 else (a + b + c) // 2 - 1
            self.assertEqual(w["size"], expected)
            self.assertGreaterEqual(w["size"], (1 + a + b + c) // 2 - 1)
            lp = _bfs_profile(w["lengths"], w["left"])
            rp = _bfs_profile(w["lengths"], w["right"])
            self.assertEqual(lp, rp, (a, b, c))

    def test_prime_shift_and_crt_bound(self):
        res = prove_prime_shift_bound()
        self.assertEqual(res["proof"], "PASS")
        self.assertEqual(res["max_shifts_covered_by_p2"], 4)
        self.assertEqual(res["max_shifts_covered_by_p3"], 4)
        self.assertEqual(res["max_shifts_covered_by_p_ge_5"], 1)
        self.assertEqual(res["min_uncovered_after_2_and_3"], 6)
        self.assertEqual(res["min_crt_modulus_6_primes"], 9699690)
        self.assertEqual(res["min_uv_sum_6_primes_5_to_19"], 1291695)

    def test_small_range_zero_escapes(self):
        small = audit_small_range(max_uv=300)
        self.assertEqual(small["escapes_found"], 0)

    def test_verify_smallest_found_escape(self):
        a, b, c = SMALLEST_FOUND_ESCAPE
        self.assertEqual((a, b, c), (1932211, 1377448, 7))
        res = verify_thirteen_trim_escape(a, b, c)
        self.assertEqual(res["status"], "all_13_trims_obstructed")
        self.assertEqual(len(res["trims"]), 13)
        self.assertTrue(all(not row["admitted"] for row in res["trims"]))

    def test_cli_altered_pair_rejection(self):
        w = construct_c12_even_sum(5, 3, 2)
        bad_right = list(w["right"])
        # Move one vertex from right to an omitted vertex [3, 1].
        bad_right[0] = [3, 1]
        bad = check_pair(w["lengths"], w["left"], bad_right)
        self.assertFalse(bad["homometric"])

        script = Path(__file__).with_name("even_sum_euler_bound.py")
        payload = json.dumps({"lengths": w["lengths"], "left": w["left"], "right": bad_right})
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
