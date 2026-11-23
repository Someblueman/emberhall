"""The bench checker agrees with the reference construction and rejects alterations.

These tests are the recorded run the house's own suite will make of
``bench_check.py``: they run the command as a subprocess, so the command line a
reader is told to use is the one that is exercised.
"""
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import bench_check
import bfs_verify


class BenchCheckTest(unittest.TestCase):
    def test_recorded_runs_are_reproduced(self):
        """The two sizes the project recorded, with their pair counts."""
        one = bfs_verify.verify(bench_check.reference_payload(1))
        self.assertTrue(one["ok"])
        self.assertEqual(one["size"], 100)
        self.assertEqual(bench_check.gap.target(1), 100)
        self.assertEqual(bench_check.pairs(100), 4950)
        three = bfs_verify.verify(bench_check.reference_payload(3))
        self.assertTrue(three["ok"])
        self.assertEqual(three["size"], 301)
        self.assertEqual(bench_check.gap.target(3), 301)

    def test_the_reference_witness_passes_every_check(self):
        for scale in (1, 2, 3):
            checks = bench_check.check_payload(bench_check.reference_payload(scale), scale)
            self.assertTrue(all(ok for _, ok, _ in checks), (scale, checks))

    def test_altered_witnesses_are_rejected(self):
        payload = bench_check.reference_payload(1)
        moved = {"lengths": payload["lengths"], "left": payload["left"][:-1],
                 "right": payload["right"]}
        duplicated = {"lengths": payload["lengths"],
                      "left": payload["left"] + [payload["left"][0]],
                      "right": payload["right"]}
        recentred = {"lengths": payload["lengths"], "left": payload["left"],
                     "right": [[1, 19] if list(v) == [0, 0] else list(v)
                               for v in payload["right"]]}
        for candidate in (moved, duplicated, recentred):
            verdict = bfs_verify.verify(candidate)
            self.assertFalse(verdict.get("ok"), verdict)
            checks = bench_check.check_payload(candidate, 1)
            recount = [detail for name, ok, detail in checks
                       if name == "independent breadth-first recount"]
            self.assertEqual(len(recount), 1)
            self.assertTrue(any(not ok for _, ok, _ in checks), checks)

    def test_cli_self_test_passes(self):
        result = subprocess.run([sys.executable, str(HERE / "bench_check.py"), "--self-test"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SELF-TEST PASSED", result.stdout)
        self.assertNotIn("FAIL:", result.stdout)

    def test_cli_scale_prints_a_payload_the_checker_accepts(self):
        result = subprocess.run([sys.executable, str(HERE / "bench_check.py"), "--scale", "2"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["lengths"], [198, 158, 46])
        checks = bench_check.check_payload(payload, 2)
        self.assertTrue(all(ok for _, ok, _ in checks), checks)

    def test_cli_compare_accepts_the_reference_and_rejects_an_alteration(self):
        exported = subprocess.run([sys.executable, str(HERE / "bench_check.py"), "--scale", "2"],
                                  capture_output=True, text=True)
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
        accepted = subprocess.run([sys.executable, str(HERE / "bench_check.py"),
                                   "--compare", "-"],
                                  input=exported.stdout, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        self.assertIn("COMPARE PASSED", accepted.stdout)
        payload = json.loads(exported.stdout)
        payload["left"] = payload["left"][:-1]
        rejected = subprocess.run([sys.executable, str(HERE / "bench_check.py"),
                                   "--compare", "-"],
                                  input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
        self.assertIn("COMPARE FAILED", rejected.stdout)

    def test_scale_of_reads_the_shape(self):
        self.assertEqual(bench_check.scale_of([198, 158, 46]), 2)
        self.assertEqual(bench_check.scale_of([99, 79, 23]), 1)
        self.assertIsNone(bench_check.scale_of([10, 7, 4]))
        self.assertIsNone(bench_check.scale_of([198, 158, 45]))


if __name__ == "__main__":
    unittest.main()
