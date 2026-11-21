"""Independent coefficient and original-tree checks of the paired-edge result."""
from collections import Counter, deque
from itertools import combinations
from pathlib import Path
import subprocess
import sys
import unittest

import mixed_edge_seven as mes
from unequal_spacing import full_partition


def direct_equations(lengths, x, y):
    """Expand the two definitions independently as lists of integer coefficients."""
    limit = sum(sorted(lengths)[-2:])
    answers = []
    for left, right in ((x, y), (y, x)):
        row = [0] * limit
        for arm in range(3):
            for depth in range(lengths[arm]):
                row[depth] += left[arm][depth]
                for other in range(3):
                    if other != arm:
                        row[depth + lengths[other]] -= left[arm][depth]
                row[lengths[arm] - depth - 1] -= right[arm][depth]
        answers.append(row)
    return answers


def graph_profiles(lengths, left, right):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    distances = {}
    for source in graph:
        distances[source] = {source: 0}
        queue = deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbour in graph[vertex]:
                if neighbour not in distances[source]:
                    distances[source][neighbour] = distances[source][vertex] + 1
                    queue.append(neighbour)
    return tuple(Counter(distances[u][v] for u, v in combinations(side, 2))
                 for side in (left, right))


class MixedEdgeSevenTests(unittest.TestCase):
    def test_formal_eliminations(self):
        self.assertTrue(all(not r for r in mes.proof_residuals().values()))

    def test_uncovered_infinite_progression(self):
        # Values are checks of the arithmetic implementation; the document proves all n.
        for n in (0, 1, 2, 7, 100003):
            result = mes.affine_obstruction(165 * n)
            self.assertTrue(result["in_previously_missing_classes"])
            self.assertTrue(result["paired_edge_assignment_excluded"])
            self.assertFalse(result["arbitrary_vertex_pairs_excluded"])
            self.assertEqual(result["retained_prefix_upper_bound"],
                             result["original_target"] - 1)

    def test_every_previously_missing_residue_is_excluded(self):
        missing = [t for t in range(165) if t % 3 == 0 and t % 15 != 3
                   and t % 11 not in (1, 6, 9)]
        self.assertEqual(len(missing), 32)
        for t in missing:
            self.assertTrue(mes.affine_obstruction(t)["paired_edge_assignment_excluded"])

    def test_does_not_exclude_available_or_unproved_cases(self):
        self.assertFalse(mes.affine_obstruction(1)["paired_edge_assignment_excluded"])
        self.assertFalse(mes.obstruction((19, 16, 8))["hypotheses_hold"])
        for t in (-1, True, 0.5):
            with self.assertRaises(ValueError):
                mes.affine_obstruction(t)

    def test_positive_control_and_corrupted_edge(self):
        lengths = (25, 22, 14)
        x = ([1] * 25, [1] * 11 + [-1] * 11, [-1] * 14)
        y = tuple([-s for s in arm] for arm in x)
        self.assertEqual(mes.paired_residual(lengths, x, y), ({}, {}))
        self.assertTrue(all(not any(row) for row in direct_equations(lengths, x, y)))
        altered = [list(arm) for arm in y]
        altered[1][3] *= -1
        self.assertTrue(any(mes.paired_residual(lengths, x, altered)))
        self.assertTrue(any(any(row) for row in direct_equations(lengths, x, altered)))
        with self.assertRaises(ValueError):
            mes.paired_residual(lengths, x, ([], [], []))

    def test_positive_control_in_the_original_tree(self):
        coarse = (25, 22, 14)
        old = full_partition(*coarse)
        signs = {v: 1 for v in old["left"]}
        signs.update({v: -1 for v in old["right"]})
        x = ([1] * 25, [1] * 11 + [-1] * 11, [-1] * 14)
        y = tuple([-s for s in arm] for arm in x)
        factor = 7
        lifted = {(arm, factor * depth): sign for (arm, depth), sign in signs.items()}
        for arm, length in enumerate(coarse, 1):
            for edge in range(length):
                for offset in (1, 2, 3):
                    lifted[arm, factor * edge + offset] = x[arm - 1][edge]
                    lifted[arm, factor * edge + factor - offset] = y[arm - 1][edge]
        left = {v for v, sign in lifted.items() if sign == 1}
        right = set(lifted) - left
        original = (175, 155, 99)  # Append the omitted middle and short tips.
        self.assertFalse(left & right)
        self.assertEqual(len(left), len(right))
        self.assertEqual(len(left), (1 + sum(original)) // 2 - 1)
        p, q = graph_profiles(original, left, right)
        self.assertEqual(p, q)
        # Exchange opposite signs: cardinality and disjointness survive, distances do not.
        u, v = (1, 1), (1, 6)
        self.assertIn(u, left)
        self.assertIn(v, right)
        changed_left, changed_right = left - {u} | {v}, right - {v} | {u}
        p, q = graph_profiles(original, changed_left, changed_right)
        self.assertNotEqual(p, q)

    def test_real_command(self):
        command = [sys.executable, str(Path(mes.__file__)), "--prove"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertIn("PASS: exact reflection eliminations", result.stdout)


if __name__ == "__main__":
    unittest.main()
