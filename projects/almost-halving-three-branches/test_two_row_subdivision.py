"""Tests for two_row_subdivision: unrestricted k=0 family, E1=E2=0 lifts, and obstructions."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter, deque
from pathlib import Path

from two_row_subdivision import (
    LIFT_FAMILIES,
    all_odd_parity_obstruction,
    check_pair,
    construct_k0,
    construct_lifted_tree,
    gf2_obstruction_check,
    prove_k0_laurent,
    prove_two_row_lift,
    q_nullspace_exhaustion,
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


class TwoRowSubdivisionTest(unittest.TestCase):
    def test_k0_symbolic_and_c_gt_r_bfs(self):
        proof = prove_k0_laurent()
        self.assertEqual(proof["proof"], "PASS")
        self.assertEqual(proof["residual_terms"], 0)
        self.assertGreater(proof["corrupt_s0_terms"], 0)
        self.assertGreater(proof["corrupt_hole_terms"], 0)

        for r, c in [(1, 1), (3, 5), (7, 11), (11, 15), (23, 27)]:
            w = construct_k0(r, c)
            self.assertEqual(w["lengths"], [2 * r + c, r + c - 1, c])
            self.assertTrue(w["homometric"])
            self.assertTrue(w["meets_target"])
            lp = _bfs_profile(w["lengths"], w["left"])
            rp = _bfs_profile(w["lengths"], w["right"])
            self.assertEqual(lp, rp, (r, c))

    def test_two_row_symbolic_lifts_and_bfs(self):
        for base in ((4, 2, 1), (6, 3, 2), (6, 4, 1), (7, 4, 2)):
            res = prove_two_row_lift(base)
            self.assertEqual(res["proof"], "PASS")
            self.assertEqual(res["e1_terms"], 0)
            self.assertEqual(res["e2_terms"], 0)
            self.assertEqual(res["lifted_q_terms"], 0)
            for g in (3, 5, 7):
                if sum(base) * g > 100:
                    continue
                w = construct_lifted_tree(base, g)
                self.assertTrue(w["homometric"])
                self.assertEqual(w["size"], (1 + g * sum(base)) // 2)
                lp = _bfs_profile(w["lengths"], w["left"])
                rp = _bfs_profile(w["lengths"], w["right"])
                self.assertEqual(lp, rp, (base, g))

    def test_7_4_2_has_no_single_row_H0_solution(self):
        # Exhaustively verify that Aster's single-row H=0 (Y_i = -X_i) has 0 solutions on (7, 4, 2).
        L1, L2, L3 = 7, 4, 2
        Ls = (L1, L2, L3)
        N = L1 + L2 + L3  # 13 vars -> 2^12 up to sign symmetry
        D = max(L1 + L2, L2 + L3, L1 + L3)
        var_terms = []
        for i in range(3):
            Li, Lj, Ll = Ls[i], Ls[(i + 1) % 3], Ls[(i + 2) % 3]
            for k in range(Li):
                terms = {}
                for deg, sgn in ((k, 1), (k + Lj, -1), (k + Ll, -1), (Li - 1 - k, 1)):
                    terms[deg] = terms.get(deg, 0) + sgn
                var_terms.append([(d, s) for d, s in terms.items() if s])
        found = 0
        for mask in range(1 << (N - 1)):
            bits = (mask << 1) | 1
            vec = [0] * (D + 1)
            for idx, vt in enumerate(var_terms):
                val = 1 if (bits >> idx) & 1 else -1
                for d, s in vt:
                    vec[d] += val * s
            if not any(vec):
                found += 1
        self.assertEqual(found, 0)
        self.assertIn((7, 4, 2), LIFT_FAMILIES)

    def test_obstructions_all_odd_gf2_and_q_nullspace(self):
        for base in ((5, 3, 1), (9, 5, 1), (11, 7, 3)):
            obs = all_odd_parity_obstruction(base)
            self.assertEqual(obs["status"], "obstructed")
            self.assertEqual(obs["gf2_status"], "inconsistent_mod_4")

        for base in ((8, 5, 2), (10, 7, 4)):
            res = gf2_obstruction_check(base)
            self.assertEqual(res["gf2_status"], "inconsistent_mod_4")

        res_62 = q_nullspace_exhaustion((62, 54, 1))
        self.assertEqual(res_62["nullity"], 5)
        self.assertEqual(res_62["solutions_up_to_sign"], 0)

        res_65 = q_nullspace_exhaustion((65, 46, 6))
        self.assertEqual(res_65["nullity"], 15)
        self.assertEqual(res_65["solutions_up_to_sign"], 0)

    def test_altered_pair_rejected_by_cli(self):
        w = construct_lifted_tree((7, 4, 2), 3)
        altered_right = list(w["right"])
        # Swap [0, 0] or first right vertex with first left vertex? Move [1, 1] -> [2, 1] by swapping or shifting:
        # Take a vertex from left and move a vertex from right: wait, replace first right [arm, d] with a vertex
        # Wait: (7*3, 4*3, 2*3) is a full partition, so swap one element between left and right? No, keep disjointness:
        # use k0 witness (3, 5) -> omit (1,3) and (1,11), move [0,0] in right to [1,3]!
        wk0 = construct_k0(3, 5)
        bad_right = list(wk0["right"])
        idx = bad_right.index([0, 0])
        bad_right[idx] = [1, 3]
        bad = check_pair(wk0["lengths"], wk0["left"], bad_right)
        self.assertFalse(bad["homometric"])

        script = Path(__file__).with_name("two_row_subdivision.py")
        payload = json.dumps({"lengths": wk0["lengths"], "left": wk0["left"], "right": bad_right})
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
