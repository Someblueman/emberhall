"""Graph-distance checks independent of the production distance formula."""
from collections import Counter, deque
from itertools import combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys
import unittest

import corrected_subdivision as cs
from progression_partitions import multiple_pair


def graph_distances(lengths):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length+1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    metric = {}
    for root in graph:
        distances = {root: 0}
        pending = deque([root])
        while pending:
            u = pending.popleft()
            for v in graph[u]:
                if v not in distances:
                    distances[v] = distances[u]+1
                    pending.append(v)
        metric[root] = distances
    return metric


def profile(vertices, metric):
    return Counter(metric[tuple(a)][tuple(b)] for a, b in combinations(vertices, 2))


def packed_profile(vertices, lengths):
    """Exact integer convolutions; no production metric or polynomial helpers."""
    bits = (sum(lengths)**2).bit_length()+1
    mask = (1 << bits)-1
    points = set(map(tuple, vertices))
    arms = [sum(1 << (bits*p) for p in range(1, n+1) if (i, p) in points)
            for i, n in enumerate(lengths, 1)]
    encoded = sum(a*b for a, b in combinations(arms, 2))
    if (0, 0) in points:
        encoded += sum(arms)
    for i, (n, a) in enumerate(zip(lengths, arms), 1):
        reverse = sum(1 << (bits*(n-p)) for p in range(1, n+1) if (i, p) in points)
        encoded += ((a*reverse) >> (bits*(n+1))) << bits
    return {d: value for d in range(1, 2*max(lengths)+1)
            if (value := (encoded >> (bits*d)) & mask)}


class CorrectedSubdivisionTest(unittest.TestCase):
    def test_all_formal_tip_patterns(self):
        for centre in (-1, 1):
            for minority in range(3):
                tips = tuple(-centre if i == minority else centre for i in range(3))
                self.assertEqual(cs.symbolic_residuals(tips, centre), ({}, {}))

    def test_all_stencils_and_arm_orders_against_graph(self):
        left, right = multiple_pair(3, 1)
        for order in permutations((1, 2, 3)):
            remap = lambda vertices: [(order[i-1], d) if i else (0, 0) for i, d in vertices]
            lengths = [0]*3
            for old, new in enumerate(order):
                lengths[new-1] = (4, 3, 2)[old]
            for factor in (3, 5, 7):
                metric = graph_distances([factor*n for n in lengths])
                for word in product((-1, 1), repeat=factor//2):
                    for lhs, rhs in ((left, right), (right, left)):
                        result = cs.subdivision_lift(lengths, remap(lhs), remap(rhs), factor, word)
                        a, b = result['left'], result['right']
                        self.assertEqual(len(a), len(b))
                        self.assertFalse(set(a)&set(b))
                        self.assertEqual(set(a)|set(b), set(metric))
                        difference = profile(a, metric)
                        difference.subtract(profile(b, metric))
                        self.assertEqual({d:v for d,v in difference.items() if v}, result['difference'])
                        self.assertEqual(result['difference'][2], result['centre_sign']*word[0])

    def test_fresh_unequal_tree_and_local_support(self):
        left, right = multiple_pair(9, 3)
        result = cs.subdivision_lift((12, 9, 6), left, right, 5, (-1, 1))
        lengths = result['lengths']
        metric = graph_distances(lengths)
        certificate = cs.repair_certificate((12, 9, 6), 5, result['tip_signs'], 1, 4)
        self.assertTrue(certificate['centre_and_tips_repair_impossible'])
        k = certificate['extreme_distance']
        for vertex, distances in metric.items():
            arm, depth = vertex
            if depth <= 4 or (arm and lengths[arm-1]-depth <= 4):
                shell = Counter(distances.values())
                self.assertEqual(shell[k+1]-shell[k], 0)

    def test_infinite_family_bounds_and_inconclusive_boundary(self):
        for family, shift in (('five', -4), ('seven', -5)):
            for t in (1, 2, 100, 10**30):
                result = cs.priority_certificates(family, t, 17)
                self.assertTrue(result['all_centre_and_tips_repairs_impossible'])
                self.assertTrue(result['all_centre_ball_repairs_impossible'])
                self.assertEqual(min(c['centre_ball_max_radius'] for c in result['conditional_cases']), 5320*t+shift)
            self.assertFalse(cs.priority_certificates(family, 1, 18)['all_centre_and_tips_repairs_impossible'])
        self.assertFalse(cs.priority_certificates('five', 0, 0)['all_centre_ball_repairs_impossible'])

    def test_corrected_lift_in_original_tree(self):
        from unequal_spacing import full_partition
        self.assertEqual(cs.edge_filler_residual(), {})
        for lengths in ((7, 4, 6), (6, 3, 4), (9, 6, 4)):
            base = full_partition(*lengths)
            for factor in (3, 5, 7):
                result = cs.corrected_lift(lengths, base['left'], base['right'], factor, (0, 1, 2))
                metric = graph_distances(result['lengths'])
                a, b = result['left'], result['right']
                self.assertEqual(profile(a, metric), profile(b, metric))
                self.assertEqual(packed_profile(a, result['lengths']), dict(profile(a, metric)))
                a = list(a)
                a[0], b[0] = b[0], a[0]
                self.assertNotEqual(profile(a, metric), profile(b, metric))
                self.assertNotEqual(packed_profile(a, result['lengths']), packed_profile(b, result['lengths']))

    def test_bad_base_and_parameters(self):
        left, right = multiple_pair(3, 1)
        altered_left, altered_right = list(left), list(right)
        altered_left[0], altered_right[0] = altered_right[0], altered_left[0]
        with self.assertRaises(ValueError):
            cs.subdivision_lift((4, 3, 2), altered_left, altered_right, 3)
        for factor in (True, 1, 2, 4, 3.0):
            with self.assertRaises(ValueError):
                cs.subdivision_lift((4, 3, 2), left, right, factor)
        for word in ((), (0,), (True,), (1, 1)):
            with self.assertRaises(ValueError):
                cs.subdivision_lift((4, 3, 2), left, right, 3, word)

    def test_actual_commands_and_checker_rejection(self):
        directory = Path(cs.__file__).parent
        run = subprocess.run([sys.executable, str(directory/'corrected_subdivision.py'), '--example', '9', '3', '--factor', '5'], capture_output=True, text=True, check=True)
        check = subprocess.run([sys.executable, str(directory/'published_cases.py'), '--check', '-'], input=run.stdout, capture_output=True, text=True)
        self.assertEqual(check.returncode, 1)
        self.assertFalse(json.loads(check.stdout)['homometric'])
        base = {'lengths': [4, 3, 2], 'left': multiple_pair(3, 1)[0], 'right': multiple_pair(3, 1)[1]}
        command = [sys.executable, str(directory/'corrected_subdivision.py'), '--lift', '-', '--factor', '3', '--summary']
        accepted = subprocess.run(command, input=json.dumps(base), capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        base['left'][0], base['right'][0] = base['right'][0], base['left'][0]
        rejected = subprocess.run(command, input=json.dumps(base), capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn('full equal homometric', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
