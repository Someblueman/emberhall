"""Tests for split_block_2660: fast auditor & multi-arm split-block sweep."""
from collections import Counter, deque
import subprocess
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from moving_hole_2660 import make_split_identity, split_level01_obstruction
from split_block_2660 import BASE, PERIOD, SplitBlockAuditor


def _bfs_profile(lengths, vertices):
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


class SplitBlockSweepTests(unittest.TestCase):
    def test_arm2_and_arm3_split_identities_match_bfs(self):
        # Verify make_split_identity on arm 1 (0-based) and arm 2 (0-based) at k=0, 1!
        # Base (5, 3, 1), delta=2, repeats=(5, 3, 1)
        # Split arm 1 (length 3): P="+-", M="0", T="+", B1="+-", B2="-+" -> wait len(P+M+T)=3!
        # Wait: P=["+-", "+", "+"], M="0", T=["-", "+", ""], B1=["+-", "-+", "+-"], B2="+-":
        # Check k=0 balance with sigma=-1, holes: M[0] on arm 1 (2nd arm) and tip on arm 0 (wait no, tip on arm 0 requires T[0] ending in 0!).
        # Let's make split_arm=1, other_hole=(0, 'tip', None): P=["+-+", "+", ""], M="0", T=["-0", "+", "0"]? No, base=(5,3,1)!
        # Base (5,3,1): arm 0 len 5: P="+-+", T="-0" (len 3+2=5). arm 1 len 3: P="+", M="0", T="-" (1+1+1=3). arm 2 len 1: P="", T="+" (0+1=1).
        # Signs at k=0: arm0 (+-+ -0 -> 2+,2-), arm1 (+ 0 - -> 1+,1-), arm2 (+ -> 1+,0-), centre (-1) -> total 4+, 4-!
        P = ["+-+", "+", ""]
        M = "0"
        T = ["-0", "-", "+"]
        B1 = ["+-", "-+", "+-"]
        B2 = "+-"
        R_s = make_split_identity(
            2, (5, 3, 1), (5, 3, 1), P, T, B1, 1, 1, M, B2, 0, (0, "tip", None), sigma=-1)
        for k in (0, 1):
            w0 = P[0] + B1[0] * (5 * k) + T[0]
            w1 = P[1] + B1[1] * (1 * k) + M + B2 * (2 * k) + T[1]
            w2 = P[2] + B1[2] * (1 * k) + T[2]
            left, right = [], [(0, 0)]
            for arm, w in enumerate((w0, w1, w2), 1):
                for d, ch in enumerate(w, 1):
                    if ch == "+":
                        left.append((arm, d))
                    elif ch == "-":
                        right.append((arm, d))
            self.assertEqual(len(left), len(right))
            lp = _bfs_profile((5 * (1 + 2 * k), 3 * (1 + 2 * k), 1 * (1 + 2 * k)), left)
            rp = _bfs_profile((5 * (1 + 2 * k), 3 * (1 + 2 * k), 1 * (1 + 2 * k)), right)
            diff = {d: 2 * (lp[d] - rp[d]) for d in set(lp) | set(rp) if lp[d] != rp[d]}
            # Multiply by (1-z)(1-z^2)
            def mul1(a, b):
                o = Counter()
                for e1, c1 in a.items():
                    for e2, c2 in b.items():
                        o[e1 + e2] += c1 * c2
                return {e: c for e, c in o.items() if c}
            exp = mul1({0: 1, 1: -1}, mul1({0: 1, 2: -1}, diff))
            got = Counter()
            for (z, w_e), c in R_s.items():
                got[z + 2 * k * w_e] += c
            got = {e: c for e, c in got.items() if c}
            self.assertEqual(got, exp)

    def test_fast_auditor_matches_slow_split_check(self):
        aud = SplitBlockAuditor(4, plen=(18, 18, 5), m_len=5)
        for oh, sig in [((0, "tip", None), -1), ("centre", 0)]:
            v_fast, _ = aud.check_split(0, 20 * 2660 // 4, 18, oh, sigma=sig)
            v_slow, _ = split_level01_obstruction(4, 0, 20 * 2660 // 4, 18, oh, sigma=sig)
            self.assertEqual(v_fast, "obstructed")
            self.assertEqual(v_slow, "obstructed")

    def test_all_three_arms_sample_slopes_delta_20_and_2660(self):
        aud20 = SplitBlockAuditor(20)
        for arm, r1 in ((0, 133 * 49), (1, 133 * 39), (2, 133 * 11)):
            v, _ = aud20.check_split(arm, r1, 2, (0, "tip", None), sigma=-1)
            self.assertEqual(v, "obstructed")
        aud2660 = SplitBlockAuditor(PERIOD)
        for arm, r1 in ((0, 50), (1, 40), (2, 12)):
            v, _ = aud2660.check_split(arm, r1, 2, (arm, "tip", None), sigma=-1)
            self.assertEqual(v, "obstructed")

    def test_cli_sweep2660_subset(self):
        p = subprocess.run(
            [sys.executable, str(HERE / "split_block_2660.py"), "--sweep2660"],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("delta=2660 arm 3", p.stdout)


if __name__ == "__main__":
    unittest.main()
