"""Tests for the standalone BFS witness recount (independent oracle)."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from bfs_verify import verify  # noqa: E402
from published_cases import alternating_pair, witness  # noqa: E402


class TestBfsVerify(unittest.TestCase):
    def test_real_witness_passes(self):
        w = witness((11, 7, 3), "block")
        result = verify({"lengths": [11, 7, 3], "left": w["left"],
                         "right": w["right"]})
        self.assertTrue(result["ok"])
        self.assertEqual(result["size"], 11)

    def test_altered_pair_rejected(self):
        left, right = alternating_pair((10, 7, 5), (1, 2, 3))
        left = [list(v) for v in left]
        i = left.index([0, 0])
        left[i] = [1, 10]
        result = verify({"lengths": [10, 7, 5], "left": left,
                         "right": [list(v) for v in right]})
        self.assertFalse(result["ok"])
        self.assertTrue(result["difference"])

    def test_overlap_rejected(self):
        w = witness((9, 7, 4), "alternating")
        result = verify({"lengths": [9, 7, 4], "left": w["left"],
                         "right": [w["left"][0]] + w["right"][1:]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "overlap")

    def test_cli_roundtrip(self):
        w = witness((13, 7, 3), "block")
        payload = json.dumps({"lengths": [13, 7, 3], "left": w["left"],
                              "right": w["right"]})
        proc = subprocess.run(
            [sys.executable, str(HERE / "bfs_verify.py"), "-"],
            input=payload, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertTrue(out["ok"])


if __name__ == "__main__":
    unittest.main()
