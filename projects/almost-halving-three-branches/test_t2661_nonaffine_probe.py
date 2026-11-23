"""Tests for t2661_nonaffine_probe: all-pairs mod-2 hole-parity exclusions."""
from itertools import combinations
import json
import subprocess
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from t2661_nonaffine_probe import (
    classify_hole_parities,
    mod2_counts,
    odd_distance_count_from_pair,
)
import residue_2660 as r2660


class AllPairsMod2Tests(unittest.TestCase):
    def test_opposite_parity_holes_impossible_for_t_1_mod_4(self):
        for t in (1, 5, 9, 2661, 5321):
            r = classify_hole_parities(t, 0, 1)
            self.assertTrue(r["excluded"])
            self.assertEqual(r["even_remaining"] % 2, 1)

    def test_exhaustively_on_small_analog_t1_mod4_tree(self):
        # Small analog T(5, 3, 1): order 10, target m=4 (even), E_tot=4, O_tot=6.
        # Verify by brute force over ALL 2^8 colourings that NO opposite-parity
        # 2-hole choice yields a homometric pair of size 4!
        lengths = (5, 3, 1)
        all_verts = [(0, 0)] + [(a, d) for a, L in enumerate(lengths, 1) for d in range(1, L + 1)]
        def dist(u, v):
            return abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]
        for i in range(len(all_verts)):
            for j in range(i + 1, len(all_verts)):
                h1, h2 = all_verts[i], all_verts[j]
                if h1[1] % 2 == h2[1] % 2:
                    continue
                rem = [v for v in all_verts if v not in (h1, h2)]
                for mask in range(1 << len(rem)):
                    if mask.bit_count() != 4:
                        continue
                    left = [rem[k] for k in range(8) if (mask >> k) & 1]
                    right = [rem[k] for k in range(8) if not ((mask >> k) & 1)]
                    lp = sorted(dist(u, v) for u, v in combinations(left, 2))
                    rp = sorted(dist(u, v) for u, v in combinations(right, 2))
                    self.assertNotEqual(lp, rp, (h1, h2))

    def test_t1_witness_odd_distance_identity(self):
        w1 = r2660.t1_witness()
        ol, or_ = odd_distance_count_from_pair(w1["left"], w1["right"])
        self.assertEqual(ol, or_)
        info = mod2_counts(1)
        self.assertEqual(info["even_total"], 100)
        self.assertEqual(info["odd_total"], 102)

    def test_cli_prove_and_classify(self):
        script = str(HERE / "t2661_nonaffine_probe.py")
        p1 = subprocess.run([sys.executable, script, "--prove"], capture_output=True, text=True, check=True)
        self.assertIn("PASS: t=2661", p1.stdout)
        p2 = subprocess.run(
            [sys.executable, script, "--classify", "2661", "0", "19"],
            capture_output=True, text=True, check=True,
        )
        self.assertTrue(json.loads(p2.stdout)["excluded"])


if __name__ == "__main__":
    unittest.main()
