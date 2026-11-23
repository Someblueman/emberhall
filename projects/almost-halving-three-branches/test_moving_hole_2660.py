"""Tests for moving_hole_2660: moving-hole obstructions and 3-param transfer."""
from collections import Counter, deque
import json
import subprocess
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fixed_difference_family import FAMILIES, identity_residual
from moving_hole_2660 import (
    BASE,
    DIVISORS_2660,
    PERIOD,
    MovingHoleAuditor,
    make_moving_identity,
    make_split_identity,
    split_level01_obstruction,
    three_param_pair,
    verify_finite_identities,
    verify_three_param_symbolic,
)
from published_cases import check_pair as pc_check_pair
import residue_2660 as r2660


def _bfs_profile(lengths, vertices):
    """Independent BFS distance-profile counter (imports nothing from solvers)."""
    adj = {(0, 0): []}
    for arm, L in enumerate(lengths, 1):
        prev = (0, 0)
        for d in range(1, L + 1):
            v = (arm, d)
            adj.setdefault(v, [])
            adj[prev].append(v)
            adj[v].append(prev)
            prev = v
    dists = {}
    for src in vertices:
        dist = {src: 0}
        q = deque([src])
        while q:
            u = q.popleft()
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        dists[src] = dist
    count = Counter()
    vlist = list(vertices)
    for i, u in enumerate(vlist):
        for w in vlist[i + 1:]:
            count[dists[u][w]] += 1
    return count


class MovingHoleAndTransferTests(unittest.TestCase):
    def test_matches_fixed_difference_and_residue_2660(self):
        rows = FAMILIES[23]
        P = [r[0] for r in rows]
        T = [r[2] for r in rows]
        B = [r[1] for r in rows]
        mine = make_moving_identity(
            56, (1, 1, 1), BASE, P, T, B, ((0, "P", 18), (0, "tip", None)), sigma=-1)
        self.assertEqual(mine, identity_residual(23, rows))
        self.assertEqual(mine, {})
        self.assertEqual(
            mine,
            r2660.make_identity(56, (1, 1, 1), BASE, P, T, B, holes=((0, 19), (0, "tip"))),
        )

    def test_finite_moving_centre_and_split_identities(self):
        lines = verify_finite_identities()
        self.assertEqual(len(lines), 5)

    def test_auditor_matches_residue_2660_and_obstructs_moving_holes(self):
        for delta in (1, 4, 5, 7, 19, 20):
            aud = MovingHoleAuditor(delta)
            # Fixed-hole check matches residue_2660:
            v1, _ = aud.check_holes((0, "P", 18), (0, "tip", None), -1)
            v2, _ = r2660.level01_obstruction(delta)
            self.assertEqual(v1, "obstructed")
            self.assertEqual(v2, "obstructed")
            # Moving tail holes and centre holes also obstructed:
            for h1, h2, sig in [
                ((0, "T", 9), (0, "tip", None), -1),
                ((0, "T", 9), "centre", 0),
                ((0, "P", 18), "centre", 0),
                ((0, "T", 0), (1, "T", 0), -1),
            ]:
                verdict, _ = aud.check_holes(h1, h2, sig)
                self.assertEqual(verdict, "obstructed", (delta, h1, h2, sig))

    def test_flagship_period_moving_centre_and_split_obstructed(self):
        aud = MovingHoleAuditor(PERIOD)
        for h1, h2, sig in [
            ((0, "T", 9), (0, "tip", None), -1),
            ((0, "T", 9), "centre", 0),
            ((0, "P", 18), "centre", 0),
        ]:
            verdict, _ = aud.check_holes(h1, h2, sig)
            self.assertEqual(verdict, "obstructed")
        verdict, _ = split_level01_obstruction(PERIOD, 0, 20, 18, (0, "tip", None), sigma=-1)
        self.assertEqual(verdict, "obstructed")
        verdict_c, _ = split_level01_obstruction(PERIOD, 0, 20, 18, "centre", sigma=0)
        self.assertEqual(verdict_c, "obstructed")

    def test_three_param_symbolic_identity_vanishes(self):
        sym = verify_three_param_symbolic()
        self.assertEqual(sym["cell_residual"], {})
        self.assertEqual(sym["transfer_residual"], {})

    def test_three_param_witnesses_via_independent_bfs(self):
        for k, r, h in ((1, 1, 1), (1, 2, 1), (1, 3, 2), (2, 2, 3), (2, 3, 4), (3, 2, 5)):
            w = three_param_pair(k, r, h)
            L = w["lengths"]
            left = [tuple(v) for v in w["left"]]
            right = [tuple(v) for v in w["right"]]
            self.assertEqual(len(left), len(right))
            self.assertEqual(len(left), w["target"])
            self.assertEqual(set(left) & set(right), set())
            lp = _bfs_profile(L, left)
            rp = _bfs_profile(L, right)
            self.assertEqual(lp, rp)
            res = pc_check_pair(L, left, right)
            self.assertTrue(res["homometric"])
            self.assertTrue(res["meets_target"])

    def test_three_param_rejects_bad_inputs_and_altered_pair(self):
        with self.assertRaises(ValueError):
            three_param_pair(0, 2, 1)
        with self.assertRaises(ValueError):
            three_param_pair(1, 2, 0)
        w = three_param_pair(1, 3, 2)
        # Move one vertex into an omitted hole: breaks homometry!
        corrupted = dict(w)
        corrupted["left"] = [list(v) for v in w["left"][:-1]] + [w["holes"][0]]
        res = pc_check_pair(corrupted["lengths"], corrupted["left"], corrupted["right"])
        self.assertFalse(res["homometric"])

    def test_cli_prove_witness_and_check_roundtrip(self):
        script = str(HERE / "moving_hole_2660.py")
        p1 = subprocess.run(
            [sys.executable, script, "--prove"],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("PASS: 3-parameter transfer", p1.stdout)
        p2 = subprocess.run(
            [sys.executable, script, "--witness", "1", "3", "2"],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(p2.stdout)
        p3 = subprocess.run(
            [sys.executable, script, "--check", "-"],
            input=json.dumps(data), capture_output=True, text=True, check=True,
        )
        self.assertTrue(json.loads(p3.stdout)["homometric"])
        # Altered CLI payload fails closed with exit code 1:
        data["left"][0] = data["holes"][0]
        p4 = subprocess.run(
            [sys.executable, script, "--check", "-"],
            input=json.dumps(data), capture_output=True, text=True,
        )
        self.assertEqual(p4.returncode, 1)
        self.assertFalse(json.loads(p4.stdout)["homometric"])


if __name__ == "__main__":
    unittest.main()
