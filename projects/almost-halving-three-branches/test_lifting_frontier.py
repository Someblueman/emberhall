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
from lifting_frontier import (interior_obstruction, verify_interior_obstruction,
                              audit_interior_obstruction, extended_obstruction,
                              verify_extended_obstruction, audit_extended_obstruction,
                              terminal_tip_obstruction, verify_terminal_tip_obstruction,
                              audit_terminal_tip_obstruction,
                              linear_degree_obstruction_absence,
                              verify_linear_degree_obstruction_absence,
                              aligned_tip_antisymmetry,
                              verify_aligned_tip_antisymmetry,
                              audit_aligned_tip_antisymmetry)


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


class InteriorObstructionTests(unittest.TestCase):
    def test_same_length_domain_has_a_positive_other_support(self):
        _, distances = graph_distances((3, 3, 3))
        left = [(0, 0), (2, 2), (3, 1), (3, 2)]
        right = [(1, 1), (1, 2), (1, 3), (2, 1)]
        self.assertFalse(set(left) & set(right))
        self.assertEqual(histogram(left, distances), Counter({1: 2, 2: 2, 3: 1, 4: 1}))
        self.assertEqual(histogram(left, distances), histogram(right, distances))
        saved = interior_obstruction((3, 3, 3))
        saved['holes'] = [[2, 3], [3, 3]]
        with self.assertRaises(ValueError):
            verify_interior_obstruction(saved)

    def test_independent_original_tree_degrees_in_every_parameter_parity(self):
        checked = 0
        for x, y, z in product(range(4), repeat=3):
            c, odd = 8*z+3, (x+z) % 2
            b, a = c+8*y, c+8*y+8*x
            vertices, distances = graph_distances((a, b, c))
            for tail_blocks in range(y+1):
                saved = interior_obstruction((a, b, c), tail_blocks)
                retained = [v for v in vertices if list(v) not in saved['holes']]
                degrees = []
                for u in retained:
                    degree = 0
                    for v in retained:
                        d = distances[u, v]
                        residues = saved['low_residues'] if d <= saved['distance_cutoff'] else saved['high_residues']
                        degree += u != v and d % saved['distance_modulus'] in residues
                    degrees.append(degree)
                self.assertEqual(Counter(d % 4 for d in degrees),
                                 Counter({i: n for i, n in enumerate(saved['degree_counts_mod_four']) if n}))
                self.assertEqual({d % 2 for d in degrees}, {odd})
                self.assertEqual(sum(degrees) % 4, 2)
                self.assertEqual(sum(degrees)//2, saved['selected_edges'])
                self.assertEqual(len(retained)//2 % 2, 0)
                checked += 1
        self.assertEqual(checked, 160)

    def test_closed_edge_formula_and_enormous_frontier(self):
        for t in (0, 1, 2, 3, 10**60, 10**60+1):
            saved = interior_obstruction(frontier_lengths(t))
            self.assertEqual(verify_interior_obstruction(saved), saved)
            self.assertEqual(saved['holes'], [[1, 170+7560*t], [2, 10+7560*t]])
            self.assertEqual(saved['common_degree_parity'], 1-t % 2)
            self.assertEqual(sum(saved['degree_counts_mod_four']), 304+22680*t)
            k = sum((n-3)//8 for n in frontier_lengths(t))
            self.assertEqual(saved['selected_edges'], 4*k*k+6*k+829)
            self.assertFalse(saved['all_omissions_obstructed'])
        audit = audit_interior_obstruction(interior_obstruction(frontier_lengths(0)))
        self.assertEqual(audit['selected_edges'], 6527)
        with self.assertRaisesRegex(ValueError, 'vertex limit'):
            audit_interior_obstruction(interior_obstruction(frontier_lengths(1)))

    def test_corruption_domain_and_real_cli(self):
        saved = interior_obstruction(frontier_lengths(0))
        for field in ('selected_edge_parity', 'all_omissions_obstructed', 'target_size'):
            broken = deepcopy(saved)
            broken[field] = not broken[field] if type(broken[field]) is bool else broken[field]+1
            with self.assertRaisesRegex(ValueError, 'differs'):
                verify_interior_obstruction(broken)
        broken = deepcopy(saved)
        broken['holes'][0][1] += 2
        with self.assertRaises(ValueError):
            audit_interior_obstruction(broken)
        for lengths in ((7, 5, 3), (19, 35, 11), (35, 19, 5), (35, 19, True)):
            with self.assertRaises(ValueError):
                interior_obstruction(lengths)
        for tail in (-1, 8, True, 0.5):
            with self.assertRaises(ValueError):
                interior_obstruction(frontier_lengths(0), tail)
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'interior.json'
            path.write_text(json.dumps(saved))
            run = subprocess.run([sys.executable, str(cli), '--interior-obstruction',
                                  '--verify', str(path), '--audit'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['audit']['selected_edges'], 6527)
            saved['extra_edges'] += 1
            path.write_text(json.dumps(saved))
            run = subprocess.run([sys.executable, str(cli), '--interior-obstruction',
                                  '--verify', str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('differs from the reconstructed proof', run.stderr)


class ExtendedObstructionTests(unittest.TestCase):
    def test_mod8_q5_independent_original_tree_degrees(self):
        checked = 0
        for x, y, z in product(range(4), repeat=3):
            c, odd = 8 * z + 3, (x + z + 1) % 2
            b, a = c + 8 * y, c + 8 * y + 8 * x
            if y == 0:
                continue
            vertices, distances = graph_distances((a, b, c))
            for p in range(y):
                saved = extended_obstruction((a, b, c), 'mod8-q5', p)
                retained = [v for v in vertices if list(v) not in saved['holes']]
                degrees = []
                for u in retained:
                    deg = 0
                    for v in retained:
                        d = distances[u, v]
                        if u == v or d >= saved['max_exclusive']:
                            continue
                        if d <= saved['cutoff_lo']:
                            deg += d % 8 in saved['low_residues']
                        elif d <= saved['cutoff_hi']:
                            deg += d in saved['mid_distances']
                        else:
                            deg += d % 8 in saved['high_residues']
                    degrees.append(deg)
                self.assertEqual(Counter(d % 4 for d in degrees),
                                 Counter({i: n for i, n in enumerate(saved['degree_counts_mod_four']) if n}))
                self.assertEqual({d % 2 for d in degrees}, {odd})
                self.assertEqual(sum(degrees) // 2, saved['selected_edges'])
                self.assertEqual(sum(degrees) % 4, 2)
                self.assertEqual(len(retained) // 2 % 2, 0)
                checked += 1
        self.assertEqual(checked, 96)

    def test_mod10_families_independent_original_tree_degrees(self):
        checked_q2 = checked_q0 = 0
        for a, b, c in ((17, 17, 11), (27, 27, 11), (37, 17, 11), (47, 27, 11),
                        (57, 37, 11), (37, 27, 21), (47, 37, 21)):
            vertices, distances = graph_distances((a, b, c))
            limit = (b - c - 6) // 10
            for family, lo in (('mod10-q2', 0), ('mod10-q0', 1)):
                for p in range(lo, limit + 1):
                    saved = extended_obstruction((a, b, c), family, p)
                    retained = [v for v in vertices if list(v) not in saved['holes']]
                    degrees = []
                    for u in retained:
                        deg = 0
                        for v in retained:
                            d = distances[u, v]
                            if u == v or (saved['max_exclusive'] is not None and d >= saved['max_exclusive']):
                                continue
                            if d <= saved['cutoff_lo']:
                                deg += d % 10 in saved['low_residues']
                            elif d <= saved['cutoff_hi']:
                                deg += d in saved['mid_distances']
                            else:
                                deg += d % 10 in saved['high_residues']
                        degrees.append(deg)
                    self.assertEqual(Counter(d % 4 for d in degrees),
                                     Counter({i: n for i, n in enumerate(saved['degree_counts_mod_four']) if n}))
                    self.assertEqual({d % 2 for d in degrees}, {1})
                    self.assertEqual(sum(degrees) // 2, saved['selected_edges'])
                    self.assertEqual(sum(degrees) % 4, 2)
                    if family == 'mod10-q2':
                        checked_q2 += 1
                    else:
                        checked_q0 += 1
        self.assertEqual((checked_q2, checked_q0), (12, 5))

    def test_positive_boundary_and_huge_frontier_parameters(self):
        # Positive boundary: T(27,11,3) lies in mod8-q5 (P=0 excludes (1,22),(2,6)),
        # yet omitting (1,9),(1,27) yields a real size-20 homometric pair.
        vertices, distances = graph_distances((27, 11, 3))
        left = [(1, 1), (1, 3), (1, 5), (1, 8), (1, 11), (1, 12), (1, 13), (1, 15),
                (1, 16), (1, 19), (1, 22), (1, 23), (1, 25), (1, 26), (2, 1), (2, 3),
                (2, 5), (2, 6), (2, 9), (3, 2)]
        right = [(0, 0), (1, 2), (1, 4), (1, 6), (1, 7), (1, 10), (1, 14), (1, 17),
                 (1, 18), (1, 20), (1, 21), (1, 24), (2, 2), (2, 4), (2, 7), (2, 8),
                 (2, 10), (2, 11), (3, 1), (3, 3)]
        self.assertEqual(len(left), 20)
        self.assertEqual(len(right), 20)
        self.assertFalse(set(left) & set(right))
        self.assertEqual(set(vertices) - (set(left) | set(right)), {(1, 9), (1, 27)})
        self.assertEqual(histogram(left, distances), histogram(right, distances))
        with self.assertRaises(ValueError):
            extended_obstruction((27, 11, 3), 'mod10-q2', 0)
        with self.assertRaises(ValueError):
            extended_obstruction((27, 11, 3), 'mod8-q5', 1)
        with self.assertRaises(ValueError):
            terminal_tip_obstruction((19, 11, 3), (1, 2))
        # Huge frontier checks across all three families and terminal tips
        for t in (0, 1, 10**60, 10**60 + 1):
            lengths = frontier_lengths(t)
            for family in ('mod8-q5', 'mod10-q2', 'mod10-q0'):
                saved = extended_obstruction(lengths, family)
                self.assertEqual(verify_extended_obstruction(saved), saved)
                self.assertTrue(saved['every_colouring_of_this_support_excluded'])
                self.assertFalse(saved['all_omissions_obstructed'])
            for arms in ((1, 2), (1, 3), (2, 3)):
                tip_cert = terminal_tip_obstruction(lengths, arms)
                self.assertEqual(verify_terminal_tip_obstruction(tip_cert), tip_cert)
                self.assertTrue(tip_cert['every_colouring_of_this_support_excluded'])
                self.assertFalse(tip_cert['all_omissions_obstructed'])
        # Audit t=0 for each family and terminal tip pair
        self.assertEqual(audit_extended_obstruction(extended_obstruction(frontier_lengths(0), 'mod8-q5', 0))['selected_edges'], 17253)
        self.assertEqual(audit_extended_obstruction(extended_obstruction(frontier_lengths(0), 'mod10-q2', 0))['selected_edges'], 22949)
        self.assertEqual(audit_extended_obstruction(extended_obstruction(frontier_lengths(0), 'mod10-q0', 1))['selected_edges'], 27671)
        for arms, mod in (((1, 2), 5), ((1, 3), 3), ((2, 3), 7)):
            audit = audit_terminal_tip_obstruction(terminal_tip_obstruction(frontier_lengths(0), arms))
            self.assertEqual(len(audit['residue_populations']), mod)
            self.assertEqual(sum(audit['residue_populations']), 304)

    def test_real_cli_and_corruption_rejection(self):
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            for family, expected_edges in (('mod8-q5', 17301), ('mod10-q2', 22949), ('mod10-q0', 27183)):
                saved = extended_obstruction(frontier_lengths(0), family)
                path = Path(directory) / f'{family}.json'
                path.write_text(json.dumps(saved))
                live = subprocess.run([sys.executable, str(cli), '--extended-obstruction',
                                       '--family', family, '--audit'], capture_output=True, text=True)
                self.assertEqual(live.returncode, 0, live.stderr)
                self.assertEqual(json.loads(live.stdout)['audit']['selected_edges'], expected_edges)
                run = subprocess.run([sys.executable, str(cli), '--extended-obstruction',
                                      '--verify', str(path), '--audit'], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(json.loads(run.stdout)['audit']['selected_edges'], expected_edges)
                broken = deepcopy(saved)
                broken['selected_edges'] += 2
                path.write_text(json.dumps(broken))
                bad = subprocess.run([sys.executable, str(cli), '--extended-obstruction',
                                      '--verify', str(path)], capture_output=True, text=True)
                self.assertEqual(bad.returncode, 2)
                self.assertIn('differs from the reconstructed proof', bad.stderr)
            tip_saved = terminal_tip_obstruction(frontier_lengths(0), (2, 3))
            tpath = Path(directory) / 'tips.json'
            tpath.write_text(json.dumps(tip_saved))
            trun = subprocess.run([sys.executable, str(cli), '--terminal-tips',
                                   '--verify', str(tpath), '--audit'], capture_output=True, text=True)
            self.assertEqual(trun.returncode, 0, trun.stderr)
            self.assertEqual(json.loads(trun.stdout)['audit']['retained_vertices'], 304)
            tip_saved['all_omissions_obstructed'] = True
            tpath.write_text(json.dumps(tip_saved))
            tbad = subprocess.run([sys.executable, str(cli), '--terminal-tips',
                                   '--verify', str(tpath)], capture_output=True, text=True)
            self.assertEqual(tbad.returncode, 2)
            self.assertIn('differs from the reconstructed proof', tbad.stderr)


class LinearAbsenceAndTipAntisymmetryTests(unittest.TestCase):
    def test_z64_linear_degree_separation_at_t0(self):
        base = frontier_lengths(0)
        obstructed = [
            ((0, 0), (1, 4)),
            ((1, 222), (2, 62)),
            ((1, 225), (2, 65)),
            ((1, 217), (2, 57)),
            ((2, 67), (3, 11)),
        ]
        for holes in obstructed:
            cert = linear_degree_obstruction_absence(base, holes, 64)
            self.assertFalse(cert['linear_degree_system_consistent'])
            self.assertIsNotNone(cert['failing_distance_row'])
            self.assertEqual(verify_linear_degree_obstruction_absence(cert), cert)

        surviving_q = [q for q in range(4, 57, 2) if q % 10 in (4, 6, 8)]
        self.assertEqual(len(surviving_q), 17)
        for q in surviving_q:
            cert = linear_degree_obstruction_absence(base, ((1, 227 - q), (2, 67 - q)), 64)
            self.assertTrue(cert['linear_degree_system_consistent'])
            self.assertIsNone(cert['failing_distance_row'])
            self.assertFalse(cert['infinite_family_proved'])

        for holes in (((1, 1), (2, 1)), ((1, 2), (2, 2)), ((1, 4), (2, 2))):
            cert = linear_degree_obstruction_absence(base, holes, 64)
            self.assertTrue(cert['linear_degree_system_consistent'])

        # Positive control: valid homometric pair T(27,11,3) omitting (1,9),(1,27) is consistent mod 64
        self.assertTrue(linear_degree_obstruction_absence((27, 11, 3), ((1, 9), (1, 27)), 64)
                        ['linear_degree_system_consistent'])

    def test_aligned_tip_antisymmetry_symbolic_and_audited(self):
        for q in (0, 1, 4, 14, 26, 48, 56):
            for t in (0, 1, 10**60):
                cert = aligned_tip_antisymmetry(frontier_lengths(t), q)
                self.assertEqual(verify_aligned_tip_antisymmetry(cert), cert)
                expected_count = 54 if q == 0 else (55 if 1 <= q <= 55 else 56)
                self.assertEqual(cert['forced_offsets_count'], expected_count)
                self.assertFalse(cert['every_colouring_of_this_support_excluded'])

        # Small-tree audit checks distance ceiling & exact rational RREF
        for q in (0, 1, 4, 6):
            cert = aligned_tip_antisymmetry((19, 11, 5), q)
            audit = audit_aligned_tip_antisymmetry(cert)
            self.assertTrue(audit['symbolic_rref_and_tree_checked'])

        with self.assertRaises(ValueError):
            aligned_tip_antisymmetry(frontier_lengths(0), 57)

    def test_linear_and_tip_cli_and_corruption_rejection(self):
        cli = Path(__file__).with_name('lifting_frontier.py')
        with tempfile.TemporaryDirectory() as directory:
            lin = subprocess.run([sys.executable, str(cli), '--linear-obstruction-check',
                                  '--holes', '1:223', '2:63'], capture_output=True, text=True)
            self.assertEqual(lin.returncode, 0, lin.stderr)
            lin_saved = json.loads(lin.stdout)
            self.assertTrue(lin_saved['linear_degree_system_consistent'])
            lin_path = Path(directory) / 'lin.json'
            lin_path.write_text(json.dumps(lin_saved))
            self.assertEqual(subprocess.run([sys.executable, str(cli), '--linear-obstruction-check',
                                             '--verify', str(lin_path)],
                                            capture_output=True, text=True).returncode, 0)
            broken_lin = deepcopy(lin_saved)
            broken_lin['linear_degree_system_consistent'] = False
            lin_path.write_text(json.dumps(broken_lin))
            bad_lin = subprocess.run([sys.executable, str(cli), '--linear-obstruction-check',
                                      '--verify', str(lin_path)], capture_output=True, text=True)
            self.assertEqual(bad_lin.returncode, 2)

            tip = subprocess.run([sys.executable, str(cli), '--tip-antisymmetry',
                                  '--lengths', '19', '11', '5', '--tip-offset', '4', '--audit'],
                                 capture_output=True, text=True)
            self.assertEqual(tip.returncode, 0, tip.stderr)
            tip_out = json.loads(tip.stdout)
            self.assertTrue(tip_out['audit']['symbolic_rref_and_tree_checked'])
            tip_path = Path(directory) / 'tip.json'
            tip_path.write_text(json.dumps(tip_out['certificate']))
            self.assertEqual(subprocess.run([sys.executable, str(cli), '--tip-antisymmetry',
                                             '--verify', str(tip_path), '--audit'],
                                            capture_output=True, text=True).returncode, 0)
            broken_tip = deepcopy(tip_out['certificate'])
            broken_tip['forced_offsets_count'] += 1
            tip_path.write_text(json.dumps(broken_tip))
            bad_tip = subprocess.run([sys.executable, str(cli), '--tip-antisymmetry',
                                      '--verify', str(tip_path)], capture_output=True, text=True)
            self.assertEqual(bad_tip.returncode, 2)


if __name__ == '__main__':
    unittest.main()
