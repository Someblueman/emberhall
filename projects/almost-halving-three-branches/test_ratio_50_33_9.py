"""Independent original-tree checks for the terminal-shell theorem and controls."""
from collections import Counter, deque
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import ratio_50_33_9 as ratio


def original_distances(lengths):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        parent = (0, 0)
        for depth in range(1, length+1):
            vertex = (arm, depth)
            graph[vertex] = [parent]
            graph[parent].append(vertex)
            parent = vertex
    metric = {}
    for start in graph:
        distance, queue = {start: 0}, deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in graph[current]:
                if neighbor not in distance:
                    distance[neighbor] = distance[current]+1
                    queue.append(neighbor)
        metric[start] = distance
    return metric


def counts(vertices, metric):
    return Counter(metric[u][v] for u, v in combinations(vertices, 2))


class RatioTest(unittest.TestCase):
    def test_actual_controls_independently(self):
        for t in (1, 2):
            witness = ratio.finite_witness(t)
            left, right = [list(map(tuple, witness[key])) for key in ("left", "right")]
            metric = original_distances(witness["lengths"])
            self.assertFalse(set(left) & set(right))
            self.assertEqual(len(left), 46*t-1)
            self.assertEqual(len(right), len(left))
            self.assertEqual(counts(left, metric), counts(right, metric))
            certificate = ratio.terminal_certificate(witness["lengths"], left, right)
            self.assertTrue(certificate["necessary_condition_passes"])
            self.assertEqual(certificate["cutoff"], 24*t+1)
            self.assertEqual(certificate["long_holes"], [])
            self.assertEqual(certificate["middle_holes"], [])

    def test_t1_is_outside_reflection_template(self):
        witness = ratio.finite_witness(1)
        signs = dict.fromkeys(map(tuple, witness["left"]), 1)
        signs.update(dict.fromkeys(map(tuple, witness["right"]), -1))
        central = [signs[(1, 16-j)] if j < 16 else signs[(0, 0)] if j == 16
                   else signs[(3, j-16)] for j in range(1, 25)]
        self.assertTrue(any(a != -b for a, b in zip(central, reversed(central))))

    def test_terminal_equivalence_all_balanced_colourings(self):
        # This audits arbitrary signs and interior/tip omissions, not just positives.
        for lengths, holes in (((5, 3, 1), set()),
                               ((6, 4, 2), {(1, 6)}),
                               ((7, 5, 3), {(1, 6), (2, 3)})):
            metric = original_distances(lengths)
            retained = sorted(set(metric)-holes)
            if len(retained) % 2:
                retained.pop()
            for left in combinations(retained, len(retained)//2):
                right = set(retained)-set(left)
                cert = ratio.terminal_certificate(lengths, left, sorted(right))
                high_start = sum(cert["retained_tips"][::2])
                lp, rp = counts(left, metric), counts(right, metric)
                high_equal = all(lp[d] == rp[d] for d in lp.keys() | rp.keys()
                                 if d > high_start)
                self.assertEqual(cert["necessary_condition_passes"], high_equal)

    def test_family_bound_arbitrary_holes_at_fresh_scales(self):
        rng = random.Random(935)
        for t in (3, 7, 11):
            lengths = [50*t, 33*t, 9*t]
            vertices = [(0, 0)]+[(i, d) for i, n in enumerate(lengths, 1)
                                    for d in range(1, n+1)]
            for holes in ({(2, 33*t-j) for j in range(3)},
                          {(1, 50*t), (2, 2), (3, 9*t)},
                          set(rng.sample(vertices, 3))):
                retained = [v for v in vertices if v not in holes]
                rng.shuffle(retained)
                half = len(retained)//2
                cert = ratio.terminal_certificate(lengths, retained[:half], retained[half:])
                self.assertGreaterEqual(cert["cutoff"], 24*t-3)
                self.assertEqual(cert["arms_long_middle_short"], [1, 2, 3])
        self.assertEqual(ratio.family_bound(10**30)["minimum_reconstructed_tip_levels"],
                         24*10**30-3)

    def test_hole_recurrence_can_force_an_impossible_sign(self):
        # Check gaps on either side, including forced non-sign coefficients.
        self.assertEqual(ratio.reconstruct_tail([1, 0, -1], [1], []), [-1, -1, 1])
        self.assertEqual(ratio.reconstruct_tail([1, 0, 1], [1], []), [-1, -1, -1])
        # A hole in the other tail can force zero where no hole was proposed.
        self.assertEqual(ratio.reconstruct_tail([1, -1, 1], [], [1]), [-1, 2, -3])

    def test_real_cli_and_size_preserving_corruption(self):
        script = str(Path(ratio.__file__))
        valid = subprocess.run([sys.executable, script, "--witness", "1"],
                               text=True, capture_output=True, check=True)
        witness = json.loads(valid.stdout)
        accepted = subprocess.run([sys.executable, script, "--check", "-"],
                                  input=valid.stdout, text=True, capture_output=True)
        self.assertEqual(accepted.returncode, 0)
        # Replace one selected vertex by an unused vertex, retaining size/disjointness.
        witness["left"][0] = [1, 50]
        rejected = subprocess.run([sys.executable, script, "--check", "-"],
                                  input=json.dumps(witness), text=True, capture_output=True)
        self.assertEqual(rejected.returncode, 1)
        self.assertFalse(json.loads(rejected.stdout)["homometric"])
        unsupported = subprocess.run([sys.executable, script, "--witness", "3"],
                                     text=True, capture_output=True)
        self.assertNotEqual(unsupported.returncode, 0)
        self.assertIn("remain open", unsupported.stderr)

    def test_validation(self):
        for value in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                ratio.family_bound(value)
        for holes in ([0], [2, 2], [3]):
            with self.assertRaises(ValueError):
                ratio.reconstruct_tail([1, 0, -1], holes, [])


if __name__ == "__main__":
    unittest.main()
