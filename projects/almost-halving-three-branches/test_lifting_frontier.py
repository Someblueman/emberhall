"""Independent original-tree checks for the all-colouring omission theorem."""
from collections import Counter, deque
from copy import deepcopy
from itertools import combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lifting_frontier import (audit_original_tree, certificate, frontier_lengths,
                              verify_certificate, coarse_certificate, coarse_pair,
                              verify_coarse_certificate, audit_coarse_certificate,
                              parity_obstruction, verify_parity_obstruction,
                              swap_adjacency_certificate, verify_swap_adjacency_certificate,
                              _adjacent_swap_systems, one_swap_obstruction_certificate,
                              verify_one_swap_obstruction)


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


class CoarseFrontierTests(unittest.TestCase):
    def test_every_surviving_support_has_original_distance_witness(self):
        checked = swaps = 0
        for lengths in ((3, 3, 3), (3, 3, 11), (3, 7, 7), (7, 7, 11)):
            vertices, distances = graph_distances(lengths)
            for holes in combinations(vertices, 2):
                if holes[0][1] % 2 != holes[1][1] % 2 or all(d % 4 == 0 for _, d in holes):
                    continue
                saved = coarse_certificate(lengths, holes)
                left, right = coarse_pair(saved)
                self.assertEqual(len(left), saved['target_size'])
                self.assertEqual(len(right), len(left))
                self.assertFalse(set(left) & set(right))
                self.assertEqual(set(left) | set(right), set(vertices) - set(holes))
                a, b = histogram(left, distances), histogram(right, distances)
                self.assertEqual(sum(n for d, n in a.items() if d % 2),
                                 sum(n for d, n in b.items() if d % 2))
                self.assertEqual(sum(n for d, n in a.items() if d % 4 == 2),
                                 sum(n for d, n in b.items() if d % 4 == 2))
                checked += 1
                swaps += saved['odd_hole_swap']
        self.assertEqual((checked, swaps), (308, 108))

    def test_odd_hole_degree_equation_for_every_colouring(self):
        lengths = (3, 3, 3)
        vertices, distances = graph_distances(lengths)
        # Nonadjacent, same-arm adjacent, and different-arm adjacent holes.
        for holes in (((1, 1), (1, 3)), ((1, 1), (2, 1)), ((1, 1), (2, 3))):
            retained = [v for v in vertices if v not in holes]
            for left in combinations(retained, 4):
                left = set(left)
                right = set(retained) - left
                signed = lambda v: 1 if v in left else -1
                s2 = sum(signed(v) for v in retained if v[1] % 4 == 2)
                neighbors = sum(signed(v) for h in holes for v in retained
                                if distances[v, h] % 4 == 2)
                a, b = histogram(left, distances), histogram(right, distances)
                difference = sum(n for d, n in a.items() if d % 4 == 2) - sum(
                    n for d, n in b.items() if d % 4 == 2)
                self.assertEqual(2*difference, -2*s2-neighbors)

    def test_symbolic_size_and_exact_distance_failure(self):
        for holes in (((1, 1), (2, 1)), ((1, 1), (2, 3)),
                      ((1, 2), (2, 2)), ((0, 0), (3, 2))):
            saved = coarse_certificate(frontier_lengths(10**60), holes)
            self.assertLessEqual(len(saved['cells']), 13)
            self.assertEqual(sum(c['left'] for c in saved['cells']), saved['target_size'])
            self.assertEqual(verify_coarse_certificate(saved), saved)
            with self.assertRaisesRegex(ValueError, 'vertex limit'):
                coarse_pair(saved)
        result = audit_coarse_certificate(coarse_certificate(frontier_lengths(0), [(1, 1), (2, 1)]))
        self.assertEqual(result['coarse_counts'], [151, 5700])
        self.assertFalse(result['actual_homometric_pair'])
        self.assertEqual(result['first_exact_mismatch'], 2)

    def test_coarse_domains_and_corruption(self):
        for holes in (((0, 0), (1, 1)), ((0, 0), (3, 4))):
            with self.assertRaisesRegex(ValueError, 'already obstructed'):
                coarse_certificate((3, 3, 11), holes)
        saved = coarse_certificate((3, 3, 3), [(1, 1), (2, 1)])
        for field in ('target_size', 'homometric_pair_proved', 'odd_hole_swap'):
            broken = deepcopy(saved)
            broken[field] = not broken[field] if type(broken[field]) is bool else broken[field]+1
            with self.assertRaises(ValueError):
                verify_coarse_certificate(broken)
        broken = deepcopy(saved)
        broken['cells'][0]['left'] += 1
        with self.assertRaises(ValueError):
            verify_coarse_certificate(broken)
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'coarse.json'
            path.write_text(json.dumps(broken))
            result = subprocess.run([sys.executable, str(cli), '--coarse', '--verify', str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('differs from the reconstructed construction', result.stderr)


class PureParityObstructionTests(unittest.TestCase):
    def test_original_tree_counts_of_every_interior_candidate(self):
        saved = parity_obstruction(0)
        vertices, distances = graph_distances(saved['lengths'])
        for row in saved['cases']:
            if row['excluded_by'] != 'coefficient mismatch':
                continue
            leaf = (row['leaf_arm'], saved['lengths'][row['leaf_arm']-1])
            interior = (row['interior_arm'], 2*row['forced_index']+1)
            left = [v for v in vertices if v[1] % 2 == 0]
            right = [v for v in vertices if v[1] % 2 and v not in (leaf, interior)]
            self.assertEqual(len(left), len(right))
            a, b = histogram(left, distances), histogram(right, distances)
            self.assertEqual(a[2*row['power']]-b[2*row['power']], -1)

    def test_arbitrary_parameters_and_corruption(self):
        for t in (0, 1, 2, 3, 100, 10**60):
            saved = parity_obstruction(t)
            self.assertEqual(verify_parity_obstruction(saved), saved)
            self.assertEqual(len(saved['cases']), 6)
            interior = [r for r in saved['cases'] if r['excluded_by'] == 'coefficient mismatch']
            self.assertEqual(len(interior), 3 if t == 0 else 5)
            self.assertTrue(all((r['actual_coefficient'], r['required_coefficient']) == (1, 2)
                                for r in interior))
        for field in ('all_colourings_excluded', 'parameter'):
            broken = deepcopy(saved)
            broken[field] = True if field == 'all_colourings_excluded' else -1
            with self.assertRaises(ValueError):
                verify_parity_obstruction(broken)
        broken = parity_obstruction(1)
        broken['cases'][0]['required_coefficient'] = 1
        with self.assertRaises(ValueError):
            verify_parity_obstruction(broken)


class SwapAdjacencyTests(unittest.TestCase):
    def test_every_original_tree_root_pair_and_adjacent_shell_formula(self):
        lengths = frontier_lengths(0)
        vertices, distances = graph_distances(lengths)
        even = [v for v in vertices if v[1] % 2 == 0]
        odd = [v for v in vertices if v[1] % 2]
        from_even = {u: Counter(distances[u, w] for w in odd) for u in even}
        from_odd = {v: Counter(distances[v, w] for w in even) for v in odd}
        admitted = 0
        for u in even:
            for v in odd:
                difference = from_even[u].copy()
                difference.subtract(from_odd[v])
                nonnegative = all(n >= 0 for n in difference.values())
                self.assertEqual(nonnegative, distances[u, v] == 1)
                if not nonnegative:
                    continue
                self.assertEqual(sum(difference.values()), 2)
                a, depth = u
                if a == 0:
                    expected = Counter((1, lengths[v[0]-1]))
                elif v[1] == depth-1:
                    expected = Counter(depth+length for j, length in enumerate(lengths, 1) if j != a)
                else:
                    expected = Counter((depth+1, lengths[a-1]-depth))
                self.assertEqual(+difference, expected)
                admitted += 1
        self.assertEqual(admitted, 305)

    def test_symbolic_certificate_and_cli_corruption(self):
        saved = swap_adjacency_certificate()
        self.assertEqual(sum(saved['classification'].values()), 2880)
        self.assertEqual(verify_swap_adjacency_certificate(saved), saved)
        self.assertFalse(saved['one_swap_homometric_pairs_excluded'])
        for field in ('endpoint_systems', 'all_colourings_excluded'):
            broken = deepcopy(saved)
            broken[field] = True if field == 'all_colourings_excluded' else 2879
            with self.assertRaises(ValueError):
                verify_swap_adjacency_certificate(broken)
        broken = deepcopy(saved)
        broken['classification']['adjacency_forced'] += 1
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'adjacency.json'
            path.write_text(json.dumps(broken))
            result = subprocess.run([sys.executable, str(cli), '--swap-adjacency', '--verify', str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('differs from the reconstructed proof', result.stderr)


class OneSwapObstructionTests(unittest.TestCase):
    def test_all_original_tree_hole_candidates_for_adjacent_swaps(self):
        vertices, distances = graph_distances(frontier_lengths(0))
        even = [v for v in vertices if v[1] % 2 == 0]
        odd = [v for v in vertices if v[1] % 2]
        from_even = {u: Counter(distances[u, w] for w in odd) for u in even}
        from_odd = {v: Counter(distances[v, w] for w in even) for v in odd}
        checked = 0
        for u in even:
            for v in odd:
                if distances[u, v] != 1:
                    continue
                difference = from_even[u].copy()
                difference.subtract(from_odd[v])
                shells = list((+difference).elements())
                self.assertEqual(len(shells), 2)
                candidates = [[h for h in odd if h != v and distances[u, h] == d] for d in shells]
                for h1, h2 in product(*candidates):
                    if h1 == h2 or shells[0] == shells[1] and h1 > h2:
                        continue
                    left = [w for w in even if w != u] + [v]
                    right = [w for w in odd if w not in (v, h1, h2)] + [u]
                    self.assertEqual(len(left), len(right))
                    self.assertNotEqual(histogram(left, distances), histogram(right, distances))
                    checked += 1
        self.assertEqual(checked, 1155)

    def test_positive_control_and_symbolic_negative_certificate(self):
        vertices, distances = graph_distances((7, 5, 3))
        u, v, holes = (2, 2), (2, 1), ((1, 7), (3, 3))
        left = [w for w in vertices if w[1] % 2 == 0 and w != u] + [v]
        right = [w for w in vertices if w[1] % 2 and w not in (*holes, v)] + [u]
        self.assertEqual(len(left), 7)
        self.assertEqual(histogram(left, distances), histogram(right, distances))
        _, surviving = _adjacent_swap_systems((3, 2, 1), 0)
        self.assertTrue(surviving)
        saved = one_swap_obstruction_certificate()
        self.assertEqual(saved['adjacent_endpoint_families'], 127)
        self.assertEqual(verify_one_swap_obstruction(saved), saved)
        self.assertTrue(saved['one_swap_homometric_pairs_excluded'])
        self.assertFalse(saved['all_colourings_excluded'])
        broken = deepcopy(saved)
        broken['surviving_affine_systems'] = 1
        with self.assertRaises(ValueError):
            verify_one_swap_obstruction(broken)
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'one-swap.json'
            saved['all_colourings_excluded'] = True
            path.write_text(json.dumps(saved))
            result = subprocess.run([sys.executable, str(cli), '--one-swap-obstruction', '--verify', str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('differs from the reconstructed proof', result.stderr)


if __name__ == '__main__':
    unittest.main()
