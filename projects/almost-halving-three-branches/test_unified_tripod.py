"""Tests for unified_tripod: unified dispatcher, proof runner, and a<=300 audit."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter, deque
from pathlib import Path

from unified_tripod import (
    audit_coverage,
    check_pair,
    construct_best,
    prove_all_families,
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


class UnifiedTripodTest(unittest.TestCase):
    def test_construct_best_across_all_families_and_bfs(self):
        # Covers published_cases, ratio_51_33_10, fixed_difference_family,
        # corrected_subdivision, three_param, two_row_subdivision, c_plus_4, and c=1,2.
        samples = [
            (11, 7, 3),      # published_cases / block
            (45, 20, 8),     # ratio_51_33_10 (previously grid energy-2)
            (55, 20, 5),     # ratio_51_33_10 (previously grid energy-2)
            (40, 30, 14),    # ratio_51_33_10 (previously grid energy-2)
            (50, 33, 9),     # ratio_50_33_9 / ratio_51_33_10
            (99, 79, 23),    # fixed_difference_family / c_plus_4
            (21, 12, 6),     # two_row_subdivision lift 3*(7,4,2)
            (131, 111, 55),  # corrected_subdivision 5*(26,22,11) + (1,1,0)
            (187, 163, 3),   # interior_hole_three_param
            (203, 179, 19),  # interior_hole_three_param
            (211, 187, 27),  # interior_hole_c_plus_4
            (235, 223, 15),  # interior_hole_c_plus_4
            (227, 215, 7),   # interior_hole_three_param
            (37, 25, 15),    # two_row_subdivision k=0
            (29, 21, 15),    # period-7 c=15
        ]
        for lengths in samples:
            w = construct_best(lengths)
            self.assertEqual(w["lengths"], list(lengths))
            self.assertTrue(w["homometric"], lengths)
            self.assertTrue(w["meets_target"], lengths)
            lp = _bfs_profile(lengths, w["left"])
            rp = _bfs_profile(lengths, w["right"])
            self.assertEqual(lp, rp, lengths)

    def test_arm_permutation_invariance(self):
        w = construct_best((27, 211, 187))
        self.assertTrue(w["homometric"])
        self.assertTrue(w["meets_target"])
        self.assertEqual(_bfs_profile((27, 211, 187), w["left"]),
                         _bfs_profile((27, 211, 187), w["right"]))

    def test_prove_all_families_and_small_audit(self):
        proofs = prove_all_families()
        self.assertEqual(proofs["proof"], "PASS")
        self.assertTrue(all(v == "PASS" for k, v in proofs["families"].items()))

        audit = audit_coverage(max_a=120)
        self.assertEqual(audit["grid_total"], 346)
        self.assertEqual(audit["grid_settled"], 346)
        self.assertEqual(audit["settled"], audit["total_triples"] - audit["open_count"])

    def test_cli_altered_pair_rejected(self):
        w = construct_best((45, 20, 8))
        bad_right = list(w["right"])
        # Replace one right vertex with an unchosen vertex (or swap with left to break homometry while disjoint):
        # (45, 20, 8) is a full partition, so swap one element from left with one from right?
        # Even simpler: use (187, 163, 3) and replace [0, 0] with omitted [1, 23]!
        w2 = construct_best((187, 163, 3))
        bad_r = list(w2["right"])
        idx = bad_r.index([0, 0])
        bad_r[idx] = [1, 23]
        bad = check_pair(w2["lengths"], w2["left"], bad_r)
        self.assertFalse(bad["homometric"])

        script = Path(__file__).with_name("unified_tripod.py")
        payload = json.dumps({"lengths": w2["lengths"], "left": w2["left"], "right": bad_r})
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
