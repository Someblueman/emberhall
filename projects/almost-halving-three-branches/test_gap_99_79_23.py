"""Tests for gap_99_79_23: BFS distances are counted on an adjacency
graph built here, independently of every construction module."""

import json
from collections import Counter, deque
from itertools import combinations
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))

import gap_99_79_23 as gap
from ratio_51_33_10 import cell_identity, template


def bfs_profile(lengths, vertices):
    adjacency = {(0, 0): [(i, 1) for i in (1, 2, 3)]}
    for arm, length in enumerate(lengths, 1):
        for depth in range(1, length + 1):
            neighbours = [(0, 0) if depth == 1 else (arm, depth - 1)]
            if depth < length:
                neighbours.append((arm, depth + 1))
            adjacency[(arm, depth)] = neighbours
    wanted = set(vertices)
    counts = Counter()
    for source in vertices:
        seen = {source: 0}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1
                    queue.append(v)
        for other in wanted:
            if other > source:
                counts[seen[other]] += 1
    return counts


class WitnessRecount(unittest.TestCase):
    def check_scale(self, t):
        result = gap.witness(t)
        lengths = result["lengths"]
        left = [tuple(v) for v in result["left"]]
        right = [tuple(v) for v in result["right"]]
        self.assertFalse(set(left) & set(right))
        self.assertEqual(len(left), len(right))
        self.assertGreaterEqual(len(left), gap.target(t))
        self.assertEqual(bfs_profile(lengths, left),
                         bfs_profile(lengths, right))
        return result

    def test_named_triple_attains_100(self):
        result = self.check_scale(1)
        self.assertEqual(result["size"], 100)
        self.assertEqual(result["target"], 100)
        used = {tuple(v) for v in result["left"] + result["right"]}
        unused = ({(0, 0)} | {(i, d) for i, n in enumerate((99, 79, 23), 1)
                              for d in range(1, n + 1)}) - used
        # The t=1 pair needs its interior omission: no tip-only pair works.
        self.assertEqual(unused, {(1, 19), (1, 99)})

    def test_small_scales_recounted_by_bfs(self):
        for t in (2, 3, 4, 5, 6):
            with self.subTest(t=t):
                self.check_scale(t)

    def test_altered_pair_rejected(self):
        result = gap.witness(3)
        left = [tuple(v) for v in result["left"]]
        right = [tuple(v) for v in result["right"]]
        used = set(left) | set(right)
        spare = next(v for v in [(1, d) for d in range(1, 298)]
                     if v not in used)
        altered = left[:-1] + [spare]
        checked = gap.check_pair(result["lengths"], altered, right)
        self.assertFalse(checked["homometric"])
        self.assertNotEqual(checked["difference"], {})

    def test_overlap_and_duplicates_rejected(self):
        result = gap.witness(2)
        with self.assertRaises(ValueError):
            gap.check_pair(result["lengths"], result["left"], result["left"])
        with self.assertRaises(ValueError):
            gap.check_pair(result["lengths"],
                           result["left"] + [result["left"][0]],
                           result["right"])


class BranchArithmetic(unittest.TestCase):
    def test_each_branch_word_identity(self):
        # Large representatives are verified through the exact cell
        # identity; full pair recounts at these sizes would be slow.
        for t, branch in ((2, "even"), (3, "odd-19"), (39, "odd-7"),
                          (267, "odd-5"), (1331, "odd-4")):
            with self.subTest(t=t):
                got, deletions, cells = gap.choose_cells(t)
                self.assertEqual(got, branch)
                self.assertTrue(gap.cells_admissible(cells))
                certified = template(cells)
                self.assertEqual(certified["status"], "constructed")
                self.assertEqual(cell_identity(certified["words"]), {})
                self.assertTrue(all(w == w[::-1]
                                    for w in certified["words"]))

    def test_resistant_scales_refused_and_classified(self):
        for t in (2661, 5321):
            with self.subTest(t=t):
                with self.assertRaises(gap.OpenScale):
                    gap.witness(t)
                info = gap.classify(t)
                self.assertEqual(info["status"], "open-no-full-prefix")
                self.assertEqual(info["upper_bound"], gap.target(t))

    def test_resistant_obstruction_rows(self):
        for row in gap.obstruction_data(2661):
            self.assertGreater(row["r"], 0)
            self.assertTrue(row["h"] > 1 or row["r"] != row["g"] - 1
                            or row["Q"] % 2 == 0, row)

    def test_classify_matches_congruences(self):
        for t in range(2, 400):
            info = gap.classify(t)
            self.assertEqual(info["status"], "attained")
            self.assertGreaterEqual(info["size"], gap.target(t))
            if t % 2 == 1:
                self.assertEqual(info["size"], gap.target(t))
                self.assertTrue(info["optimal"])

    def test_prove_audit(self):
        self.assertEqual(len(gap.prove()), 3)


class Cli(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, str(Path(__file__).parent / "gap_99_79_23.py"),
             *args], capture_output=True, text=True, input=stdin)

    def test_check_round_trip_and_tamper(self):
        made = self.run_cli("--witness", "3")
        self.assertEqual(made.returncode, 0, made.stderr)
        pair = json.loads(made.stdout)
        saved = json.dumps({"lengths": pair["lengths"],
                            "left": pair["left"], "right": pair["right"]})
        ok = self.run_cli("--check", "-", stdin=saved)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        data = json.loads(saved)
        data["left"][0], data["left"][1] = data["left"][1], data["left"][0]
        data["left"][0] = [2, data["left"][0][1]]  # move a vertex across arms
        bad = self.run_cli("--check", "-", stdin=json.dumps(data))
        self.assertEqual(bad.returncode, 1)

    def test_cli_refuses_open_scale(self):
        refused = self.run_cli("--witness", "2661", "--summary")
        self.assertEqual(refused.returncode, 1)
        self.assertIn("1 mod 2660", refused.stderr)


if __name__ == "__main__":
    unittest.main()
