"""Independent original-tree distances, exhaustive controls and real CLI checks."""
from collections import Counter, deque
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import long_frontier as lf


def metric(lengths):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length+1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    distances = {}
    for root in graph:
        seen = {root: 0}
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in seen:
                    seen[v] = seen[u]+1
                    queue.append(v)
        distances[root] = seen
    return distances


def profile(vertices, distances):
    return Counter(distances[u][v] for u, v in combinations(vertices, 2))


class LongFrontierTest(unittest.TestCase):
    def test_infinite_certificate_with_independent_counts(self):
        for lengths, modulus in [((3, 9, 15), 6), ((19, 11, 27), 8),
                                 ((13, 23, 33), 10), ((227, 67, 11), 8)]:
            distances = metric(lengths)
            for arms in combinations((1, 2, 3), 2):
                result = lf.penultimate_certificate(lengths, modulus, arms)
                omitted = set(result['omitted'])
                retained = set(distances)-omitted
                selected = [(u, v) for u, v in combinations(retained, 2)
                            if distances[u][v] % modulus == 2]
                degree = Counter(v for edge in selected for v in edge)
                self.assertEqual(len(selected), result['selected_edges'])
                self.assertTrue(all(degree[v] % 2 == result['degree_parity']
                                    for v in retained))
                self.assertNotEqual(len(selected) % 2, result['required_edge_parity'])
                self.assertFalse(result['all_omissions_obstructed'])

    def test_symbolic_arithmetic_at_large_parameters(self):
        for t in (0, 1, 2, 101, 10**40):
            result = lf.penultimate_certificate(tuple(n+7560*t for n in (227, 67, 11)))
            self.assertEqual(result['size'], 152+11340*t)
            self.assertEqual(result['actual_edge_parity'], 1)
            self.assertEqual(result['required_edge_parity'], 0)

    def test_all_colourings_of_small_supports(self):
        for lengths in ((1, 1, 1), (2, 3, 4), (3, 3, 3), (5, 4, 2)):
            distances = metric(lengths)
            vertices = list(distances)
            for holes in [()] + list(combinations(vertices, 2)):
                retained = set(vertices)-set(holes)
                possible = False
                for chosen in combinations(sorted(retained), len(retained)//2):
                    if profile(chosen, distances) == profile(retained-set(chosen), distances):
                        possible = True
                        break
                result = lf.complete_support(lengths, holes)
                self.assertEqual(result['status'] == 'witness', possible, (lengths, holes))
                if result['status'] == 'witness':
                    left, right = map(lambda key: set(result[key]), ('left', 'right'))
                    self.assertFalse(left & right)
                    self.assertEqual(left | right, retained)
                    self.assertEqual(profile(left, distances), profile(right, distances))

    def test_certificate_recount_and_corruption(self):
        lengths = (227, 67, 11)
        holes = [(1, 226), (3, 10)]
        result = lf.complete_support(lengths, holes)
        self.assertEqual(result['status'], 'support_obstructed')
        certificate = result['certificate']
        self.assertTrue(lf.verify_certificate(lengths, holes, certificate)['valid'])
        altered = dict(certificate, distances=[])
        self.assertFalse(lf.verify_certificate(lengths, holes, altered)['valid'])
        self.assertFalse(lf.verify_certificate(lengths, [(1, 1), (1, 3)],
                                               certificate)['valid'])

    def test_consistent_parity_can_still_fail_integer_equations(self):
        result = lf.complete_support((227, 67, 11), [(0, 0), (1, 2)])
        self.assertEqual(result['status'], 'support_obstructed')
        self.assertNotIn('certificate', result)
        self.assertEqual(result['proof'], 'exhaustive parity completion')
        self.assertGreater(result['balanced_candidates'], 0)

    def test_limits_and_input_boundaries(self):
        self.assertEqual(lf.complete_support((4, 3, 2), max_free=0)['status'], 'inconclusive')
        for lengths, holes in [((2, 2, 2), ()), ((1, 1, 1), [(1, 1), (1, 1)])]:
            with self.assertRaises(ValueError):
                lf.complete_support(lengths, holes)
        with self.assertRaises(ValueError):
            lf.complete_support((227, 67, 11), max_vertices=20)
        for modulus in (True, 4, 7):
            with self.assertRaises(ValueError):
                lf.penultimate_certificate((3, 3, 3), modulus)

    def test_real_cli_witness_and_altered_pair(self):
        script = str(Path(lf.__file__))
        run = subprocess.run([sys.executable, script, '--solve', '5', '4', '2',
                              '--omit', '1', '1', '--omit', '1', '2'],
                             capture_output=True, text=True, check=True)
        pair = json.loads(run.stdout)
        distances = metric(pair['lengths'])
        self.assertEqual(profile(map(tuple, pair['left']), distances),
                         profile(map(tuple, pair['right']), distances))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'pair.json'
            path.write_text(json.dumps(pair))
            self.assertEqual(subprocess.run([sys.executable, script, '--check', str(path)],
                                            capture_output=True).returncode, 0)
            pair['left'][0] = [1, 1]
            path.write_text(json.dumps(pair))
            bad = subprocess.run([sys.executable, script, '--check', str(path)],
                                 capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertFalse(json.loads(bad.stdout)['homometric'])


if __name__ == '__main__':
    unittest.main()
