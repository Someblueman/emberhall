"""Independent original-tree checks for the all-colouring omission theorem."""
from collections import Counter, deque
from copy import deepcopy
from itertools import combinations, permutations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lifting_frontier import (audit_original_tree, certificate, frontier_lengths,
                              verify_certificate)


def graph_distances(lengths):
    """Integer-node BFS, independent of the checker's vertex graph and formulas."""
    labels = [(0, 0)]
    edges = []
    for arm, length in enumerate(lengths, 1):
        previous = 0
        for depth in range(1, length + 1):
            node = len(labels)
            labels.append((arm, depth))
            edges.append((previous, node))
            previous = node
    neighbors = [[] for _ in labels]
    for u, v in edges:
        neighbors[u].append(v)
        neighbors[v].append(u)
    distances = {}
    for source in range(len(labels)):
        row = {source: 0}
        queue = deque([source])
        while queue:
            node = queue.popleft()
            for other in neighbors[node]:
                if other not in row:
                    row[other] = row[node] + 1
                    queue.append(other)
        for target, value in row.items():
            distances[labels[source], labels[target]] = value
    return labels, distances


def histogram(vertices, distances):
    return Counter(distances[u, v] for u, v in combinations(vertices, 2))


class LiftingFrontierTests(unittest.TestCase):
    def test_all_small_holes_and_arm_relabelings(self):
        cases = 0
        for lengths in sorted(set(permutations((3, 7, 7)))
                              | set(permutations((3, 3, 11)))
                              | set(permutations((7, 7, 11)))):
            vertices, distances = graph_distances(lengths)
            holes = [v for v in vertices if v[1] % 4 == 0]
            for pair in combinations(holes, 2):
                result = certificate(lengths, pair)
                retained = [v for v in vertices if v not in pair]
                degrees = [sum(distances[u, v] % 4 == 2 for v in retained)
                           for u in retained]
                self.assertEqual(sum(degrees) // 2, result['selected_edges'])
                self.assertEqual({d % 4 for d in degrees},
                                 {result['common_degree_residue']})
                self.assertEqual(result['contradiction_residue'], 2)
                self.assertFalse(result['all_omissions_obstructed'])
                cases += 1
        self.assertEqual(cases, 48)

    def test_every_colouring_of_a_small_support(self):
        vertices, distances = graph_distances((3, 3, 11))
        retained = [v for v in vertices if v not in ((0, 0), (3, 4))]
        checked = 0
        # Exchange of the two colours lets us fix the first vertex in A.
        for rest in combinations(retained[1:], 7):
            left = [retained[0], *rest]
            right = [v for v in retained if v not in left]
            self.assertNotEqual(histogram(left, distances), histogram(right, distances))
            checked += 1
        self.assertEqual(checked, 6435)

    def test_odd_quotient_sum_has_a_real_positive_pair(self):
        lengths = (3, 3, 7)
        _, distances = graph_distances(lengths)
        left = [(3, d) for d in (1, 2, 3, 5, 6, 7)]
        right = [(a, d) for a in (1, 2) for d in (1, 2, 3)]
        self.assertEqual(histogram(left, distances), Counter({1: 4, 2: 3, 3: 2, 4: 3, 5: 2, 6: 1}))
        self.assertEqual(histogram(left, distances), histogram(right, distances))
        with self.assertRaisesRegex(ValueError, 'quotients must be even'):
            certificate(lengths, [(0, 0), (3, 4)])

    def test_mixed_even_holes_positive_boundary_and_forced_counts(self):
        _, distances = graph_distances((3, 7, 7))
        left = [(1, 2), (2, 1), (2, 3), (2, 5), (2, 6), (3, 3), (3, 4), (3, 7)]
        right = [(1, 1), (1, 3), (2, 4), (2, 7), (3, 1), (3, 2), (3, 5), (3, 6)]
        self.assertEqual(histogram(left, distances), histogram(right, distances))
        self.assertEqual(sum(d % 4 == 0 for _, d in left), 1)
        self.assertEqual(sum(d % 4 == 2 for _, d in left), 2)
        self.assertEqual(sum(d % 4 == 0 for _, d in right), 1)
        self.assertEqual(sum(d % 4 == 2 for _, d in right), 2)
        with self.assertRaisesRegex(ValueError, 'depths divisible by four'):
            certificate((3, 7, 7), [(0, 0), (2, 2)])

    def test_symbolic_frontier_and_real_audit(self):
        result = certificate(frontier_lengths(0), [(0, 0), (1, 4)])
        audit = audit_original_tree(result)
        self.assertEqual(audit['selected_edges'], 11550)
        self.assertEqual(audit['retained_vertices'], 304)
        t = 10**60
        huge = certificate(frontier_lengths(t), [(1, 4), (3, 7560*t+8)])
        self.assertEqual(huge['target_size'], 152+11340*t)
        self.assertEqual(verify_certificate(huge), huge)
        with self.assertRaisesRegex(ValueError, 'vertex limit'):
            audit_original_tree(huge)

    def test_invalid_domains_and_corrupt_certificates(self):
        for lengths, holes in [((3, 3, 10), [(0, 0), (3, 4)]),
                               ((3, 3, 11), [(0, 0), (3, 2)]),
                               ((3, 3, 11), [(3, 4), (3, 4)]),
                               ((3, 3, 11), [(3, 4), (3, 12)]),
                               ((True, 3, 11), [(0, 0), (3, 4)])]:
            with self.assertRaises(ValueError):
                certificate(lengths, holes)
        good = certificate((3, 3, 11), [(0, 0), (3, 4)])
        for field in ('selected_edges', 'common_degree_residue',
                      'all_omissions_obstructed', 'target_size'):
            broken = deepcopy(good)
            broken[field] = not broken[field] if isinstance(broken[field], bool) else broken[field]+1
            with self.assertRaises(ValueError):
                verify_certificate(broken)
        with self.assertRaises(ValueError):
            frontier_lengths(True)

    def test_cli_saved_certificate_rejects_corruption(self):
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'certificate.json'
            good = certificate((3, 3, 11), [(0, 0), (3, 4)])
            path.write_text(json.dumps(good))
            command = [sys.executable, str(cli), '--verify', str(path)]
            valid = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            good['selected_edges'] += 1
            path.write_text(json.dumps(good))
            corrupt = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(corrupt.returncode, 2)
            self.assertIn('differs from the reconstructed proof', corrupt.stderr)


if __name__ == '__main__':
    unittest.main()
