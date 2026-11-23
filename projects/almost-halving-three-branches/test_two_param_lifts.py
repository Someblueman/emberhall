"""Tests for two_param_lifts: infinite two-parameter E1=E2=0 subdivision families."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter, deque
from pathlib import Path

from two_param_lifts import (
    check_pair,
    family1_certificate,
    family2_certificate,
    prove_subdivision_symbolic,
    construct_family1,
    construct_family2,
    prove_family1_symbolic,
    prove_family2_symbolic,
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


class TwoParamLiftsTest(unittest.TestCase):
    def test_validation(self):
        for bad in [(1, 3), (2, 4), (2, 1)]:
            with self.assertRaises(ValueError):
                construct_family1(*bad)
        for bad in [(0, 3), (1, 4), (1, 1)]:
            with self.assertRaises(ValueError):
                construct_family2(*bad)

    def test_symbolic_two_variable_proofs(self):
        r1 = prove_family1_symbolic()
        self.assertEqual(r1["proof"], "PASS")
        self.assertEqual(r1["e1_terms"], 0)
        self.assertEqual(r1["e2_terms"], 0)
        self.assertGreater(r1["corrupt_x3_terms"], 0)

        r2 = prove_family2_symbolic()
        self.assertEqual(r2["proof"], "PASS")
        self.assertEqual(r2["e1_terms"], 0)
        self.assertEqual(r2["e2_terms"], 0)
        self.assertGreater(r2["corrupt_x3_terms"], 0)

    def test_universal_subdivision_identity(self):
        proof = prove_subdivision_symbolic()
        self.assertEqual(proof["reflection_terms"], [0, 0])
        self.assertGreater(proof["corrupt_reflection_terms"], 0)

    def test_parameter_certificates_match_edge_words(self):
        # Independent one-variable substitution and direct convolution.
        # This ties formal identities to the emitted word formulas.
        def specialize(poly, power):
            result = Counter()
            for (z, m), coeff in poly.items():
                result[z + power * m] += coeff
            return {k: v for k, v in result.items() if v}

        def cleared_word(word, degree):
            result = Counter()
            for k, ch in enumerate(word):
                sign = 1 if ch == "+" else -1
                result[k] += sign
                result[k + degree] -= sign
            return {k: v for k, v in result.items() if v}

        for m in (2, 3, 7, 20):
            A, NX, NY, degree = family1_certificate()
            xs = ("-" * (2*m), "+" * (2*m-2), "+")
            ys = ("+-" * m, "-+" * (m-1), "+")
            for i, (x, y) in enumerate(zip(xs, ys)):
                self.assertEqual(specialize(A[i], 2*m), {len(x): 1})
                self.assertEqual(specialize(NX[i], 2*m), cleared_word(x, degree))
                self.assertEqual(specialize(NY[i], 2*m), cleared_word(y, degree))
        for m in (1, 2, 7, 20):
            A, NX, NY, degree = family2_certificate()
            xs = ("--+" + "+--+" * m, "+-+-", "-+")
            ys = ("+--+" * m + "+--", "++++", "--")
            for i, (x, y) in enumerate(zip(xs, ys)):
                self.assertEqual(specialize(A[i], 4*m), {len(x): 1})
                self.assertEqual(specialize(NX[i], 4*m), cleared_word(x, degree))
                self.assertEqual(specialize(NY[i], 4*m), cleared_word(y, degree))

    def test_family1_and_family2_bfs(self):
        for m in (2, 3, 4):
            for g in (3, 5, 7):
                w = construct_family1(m, g)
                self.assertEqual(w["lengths"], [2 * m * g, (2 * m - 2) * g, g])
                self.assertTrue(w["homometric"])
                left, right = set(map(tuple, w["left"])), set(map(tuple, w["right"]))
                all_vertices = {(0, 0)} | {(arm, d)
                    for arm, length in enumerate(w["lengths"], 1)
                    for d in range(1, length+1)}
                self.assertFalse(left & right)
                self.assertEqual(left | right, all_vertices)
                self.assertEqual(len(left), len(right))
                self.assertEqual(w["size"], (1 + sum(w["lengths"])) // 2)
                self.assertEqual(_bfs_profile(w["lengths"], w["left"]),
                                 _bfs_profile(w["lengths"], w["right"]))
        for m in (1, 2, 3):
            for g in (3, 5, 7):
                w = construct_family2(m, g)
                self.assertEqual(w["lengths"], [(4 * m + 3) * g, 4 * g, 2 * g])
                self.assertTrue(w["homometric"])
                left, right = set(map(tuple, w["left"])), set(map(tuple, w["right"]))
                all_vertices = {(0, 0)} | {(arm, d)
                    for arm, length in enumerate(w["lengths"], 1)
                    for d in range(1, length+1)}
                self.assertFalse(left & right)
                self.assertEqual(left | right, all_vertices)
                self.assertEqual(len(left), len(right))
                self.assertEqual(w["size"], (1 + sum(w["lengths"])) // 2)
                self.assertEqual(_bfs_profile(w["lengths"], w["left"]),
                                 _bfs_profile(w["lengths"], w["right"]))

    def test_cli_altered_pair_rejected(self):
        w = construct_family1(2, 3)
        # Swap one element from left to right? Keep disjointness & same size by swapping
        # [1, 1] and [2, 1] if on opposite sides, or just move one vertex out and check check_pair!
        bad_right = list(w["right"])
        l0 = w["left"][0]
        r0 = bad_right[0]
        bad_left = [r0] + list(w["left"][1:])
        bad_right[0] = l0
        bad = check_pair(w["lengths"], bad_left, bad_right)
        self.assertFalse(bad["homometric"])

        script = Path(__file__).with_name("two_param_lifts.py")
        payload = json.dumps({"lengths": w["lengths"], "left": bad_left, "right": bad_right})
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
