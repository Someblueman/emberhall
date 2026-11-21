"""Independent original-graph checks for the finite residue reduction."""
from collections import Counter, deque
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import long_frontier_infinite as frontier


def graph_distances(lengths):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    result = {}
    for start in graph:
        distances = {start: 0}
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        result[start] = distances
    return result


def profile(vertices, distances, modulus=None):
    return Counter(distances[u][v] % modulus if modulus else distances[u][v]
                   for u, v in combinations(vertices, 2))


def cell_counts(system, signs):
    return [sum(signs[cell['arm'], depth]
                for depth in range(cell['first'], cell['hi'] + 1, system['modulus']))
            for cell in system['cells']]


class ResidueReductionTests(unittest.TestCase):
    def test_every_small_hole_pattern_and_balanced_colouring(self):
        lengths = (3, 2, 2)
        distances = graph_distances(lengths)
        vertices = list(distances)
        for holes in [()] + list(combinations(vertices, 2)):
            retained = [v for v in vertices if v not in holes]
            for modulus in (3, 4, 8):
                system = frontier.compressed_system(lengths, holes, modulus)
                for plus in combinations(retained, len(retained) // 2):
                    plus = set(plus)
                    minus = set(retained) - plus
                    signs = {v: 1 if v in plus else -1 for v in retained}
                    counts = cell_counts(system, signs)
                    checked = frontier.verify_counts(system, counts)
                    self.assertEqual(checked['aggregate_equations_hold'],
                                     profile(plus, distances, modulus) ==
                                     profile(minus, distances, modulus))

    def test_grouped_columns_against_full_graph_including_unbalanced_signs(self):
        lengths = (27, 19, 11)
        distances = graph_distances(lengths)
        rng = random.Random(821)
        for holes in [(), ((0, 0), (1, 16)), ((1, 8), (1, 22)), ((2, 4), (3, 10))]:
            system = frontier.compressed_system(lengths, holes)
            retained = [v for v in distances if v not in holes]
            for _ in range(10):
                signs = {v: rng.choice((-1, 1)) for v in retained}
                counts = cell_counts(system, signs)
                residual = frontier.verify_counts(system, counts)['residual']
                moments = [sum(j*signs[cell['arm'], depth] for j, depth in enumerate(
                    range(cell['first'], cell['hi']+1, 8))) for cell in system['cells']]
                moment_result = frontier.verify_moments(system, counts, moments)
                shells = Counter()
                expected_moments = [0]*8
                for u, v in combinations(retained, 2):
                    shells[distances[u][v] % 8] += signs[u] + signs[v]
                    for exponent, coefficient in [(distances[u][v]-1, 1), (distances[u][v], -1)]:
                        quotient, remainder = divmod(exponent, 8)
                        expected_moments[remainder] += coefficient*quotient*(signs[u]+signs[v])
                expected = [shells[(r + 1) % 8] - shells[r] for r in range(8)]
                expected[0] -= 2 * sum(signs.values())
                self.assertEqual(residual, [sum(signs.values())] + expected)
                self.assertEqual(moment_result['moment_residual'], expected_moments)

    def test_moment_bounds_exactly_match_local_sign_words(self):
        system = frontier.compressed_system((7, 4, 2), (), 2)
        counts = [c['count'] % 2 for c in system['cells']]
        canonical = []
        for cell, value in zip(system['cells'], counts):
            n, p = cell['count'], (cell['count']+value)//2
            canonical.append(p*(p-1)-n*(n-1)//2)
        for index, cell in enumerate(system['cells']):
            n, p = cell['count'], (cell['count']+counts[index])//2
            total = n*(n-1)//2
            possible = {2*sum(chosen)-total for chosen in combinations(range(n), p)}
            for moment in range(-total-2, total+3):
                candidate = canonical.copy()
                candidate[index] = moment
                if moment in possible:
                    frontier.verify_moments(system, counts, candidate)
                else:
                    with self.assertRaises(ValueError):
                        frontier.verify_moments(system, counts, candidate)

    def test_even_barrier_holds_symbolically(self):
        base = frontier.even_barrier(0)
        for k in (1, 10, 10**20):
            system = frontier.even_barrier(2*k)
            self.assertTrue(system['aggregate_equations_hold'])
            self.assertEqual(len(system['cells']), 33)
            for old, new in zip(base['cells'], system['cells']):
                self.assertEqual(old['column'], new['column'])
                grows = old['arm'] in (1, 3) or (old['arm'] == 2 and old['lo'] == 11)
                self.assertEqual(new['count'] - old['count'], 1890*k if grows else 0)

    def test_first_moment_obstruction_for_every_order_of_displayed_counts(self):
        for r in (0, 1, 2, 17, 10**20):
            result = frontier.moment_obstruction(4*r)
            self.assertTrue(result['fixed_counts_obstructed'])
            self.assertFalse(result['arbitrary_counts_obstructed'])
            self.assertEqual(result['constant'], 18 + 11340*r)
            self.assertEqual(result['parity_term'], -8)
            self.assertEqual(result['weighted_residual_modulus'], (2+4*r) % 8)
        with self.assertRaises(ValueError):
            frontier.moment_obstruction(2)

    def test_modular_witness_is_not_an_exact_distance_witness(self):
        system = frontier.even_barrier(0)
        left, right = frontier.lift_counts(system, system['signed_counts'])
        distances = graph_distances((227, 67, 11))
        self.assertEqual(len(left), 152)
        self.assertEqual(len(right), 152)
        self.assertFalse(set(left) & set(right))
        self.assertEqual(set(distances) - set(left) - set(right), {(2, 4), (2, 10)})
        self.assertEqual(profile(left, distances, 8), profile(right, distances, 8))
        self.assertNotEqual(profile(left, distances), profile(right, distances))
        self.assertEqual(profile(left, distances)[1] - profile(right, distances)[1], 2)
        self.assertFalse(frontier.check_pair(system['lengths'], left, right)['homometric'])
        moments = [sum(j*(1 if (cell['arm'], depth) in set(left) else -1)
                       for j, depth in enumerate(range(cell['first'], cell['hi']+1, 8)))
                   for cell in system['cells']]
        self.assertFalse(frontier.verify_moments(system, system['signed_counts'], moments)
                         ['first_moment_equations_hold'])

    def test_corruption_and_size_boundaries(self):
        system = frontier.even_barrier(0)
        counts = system['signed_counts'].copy()
        counts[1] = 2
        self.assertFalse(frontier.verify_counts(system, counts)['aggregate_equations_hold'])
        counts[1] = 1
        with self.assertRaises(ValueError):
            frontier.verify_counts(system, counts)
        system['cells'][0]['column'] = [0]*9  # saved columns are never trusted
        self.assertTrue(frontier.verify_counts(system, system['signed_counts'])['aggregate_equations_hold'])
        with self.assertRaises(ValueError):
            frontier.lift_counts(frontier.even_barrier(2), frontier.EVEN_COUNTS)
        for invalid in (-2, 1, True):
            with self.assertRaises(ValueError):
                frontier.even_barrier(invalid)
        for holes in [[(2, 4), (2, 4)], [(3, 12)], [(0, 0)]]:
            with self.assertRaises(ValueError):
                frontier.compressed_system((227, 67, 11), holes)

    def test_real_cli_and_independent_saved_certificate(self):
        command = [sys.executable, str(Path(frontier.__file__)), '0', '--barrier-even']
        result = subprocess.run(command + ['--lift-check'], text=True, capture_output=True, check=True)
        saved = json.loads(result.stdout)
        self.assertFalse(saved['lift_check']['homometric'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'counts.json'
            path.write_text(json.dumps(saved))
            result = subprocess.run(command + ['--verify', str(path)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            saved['signed_counts'][1] = 2
            path.write_text(json.dumps(saved))
            result = subprocess.run(command + ['--verify', str(path)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
        impossible = frontier.compressed_system((227, 67, 11))
        self.assertIsNone(frontier.small_counts(impossible))  # never means an obstruction


if __name__ == '__main__':
    unittest.main()
