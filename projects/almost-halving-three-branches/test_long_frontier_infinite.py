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

    def test_moments_witness_holds_symbolically_for_all_t_ge_1(self):
        for t0, (counts, y0, dy) in frontier.MOMENTS_WITNESS_BRANCHES.items():
            base = frontier.moments_witness(t0)
            nxt = frontier.moments_witness(t0 + 4)
            self.assertTrue(base['first_moment_equations_hold'])
            self.assertFalse(base['homometric_pair_proved'])
            self.assertEqual(len(base['cells']), 25)
            # Check exact affine growth of moment_constant and monotone quadratic bound margins for all k>=0
            for i, (c0, c1) in enumerate(zip(base['cells'], nxt['cells'])):
                self.assertEqual(c0['column'], c1['column'])
                self.assertEqual(c0['moment_linear'], c1['moment_linear'])
                if i > 0:
                    self.assertEqual(c1['count'] - c0['count'], 3780)
                    p0 = (c0['count'] + counts[i]) // 2
                    self.assertGreaterEqual(dy[i] + 3780 * (c0['count'] - p0), 0)
                    self.assertGreaterEqual(3780 * p0 - dy[i], 0)
            dmc_eq = [sum(counts[i] * (c1['moment_constant'][r] - c0['moment_constant'][r])
                          + dy[i] * c0['moment_linear'][r] for i, (c0, c1) in enumerate(zip(base['cells'], nxt['cells'])))
                      for r in range(8)]
            self.assertEqual(dmc_eq, [0] * 8)
            huge = frontier.moments_witness(t0 + 4 * 10**60)
            self.assertTrue(huge['first_moment_equations_hold'])
        for bad_t in (0, -1, True):
            with self.assertRaises(ValueError):
                frontier.moments_witness(bad_t)
        cli = [sys.executable, str(Path(frontier.__file__))]
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run(cli + ['4', '--moments-witness'], text=True, capture_output=True, check=True)
            saved = json.loads(run.stdout)
            self.assertTrue(saved['first_moment_equations_hold'])
            path = Path(folder) / 'm17.json'
            path.write_text(json.dumps(saved))
            ok = subprocess.run(cli + ['--verify', str(path)], text=True, capture_output=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            saved['signed_moments'][1] += 2
            path.write_text(json.dumps(saved))
            bad = subprocess.run(cli + ['--verify', str(path)], text=True, capture_output=True)
            self.assertEqual(bad.returncode, 1, bad.stderr)

    def test_second_moment_bounds_match_subsets(self):
        for n in range(1, 10):
            for p in range(0, n + 1):
                count = 2 * p - n
                tot_y = n * (n - 1) // 2
                tot_z = n * (n - 1) * (n - 2) // 6
                by_y = {}
                for subset in combinations(range(n), p):
                    y_val = 2 * sum(subset) - tot_y
                    z_val = 2 * sum(j * (j - 1) // 2 for j in subset) - tot_z
                    lo, hi = by_y.get(y_val, (z_val, z_val))
                    by_y[y_val] = (min(lo, z_val), max(hi, z_val))
                for y_val, (true_lo, true_hi) in by_y.items():
                    lo, hi, par = frontier.second_moment_bounds(n, count, y_val)
                    self.assertEqual((lo, hi, par), (true_lo, true_hi, (-tot_z) % 2))

    def test_triple_moments_witness_all_t_ge_1_and_defects(self):
        # Verify exact polynomial inequalities proving Y and Z stay in Schur bounds for ALL k>=0!
        def padd(a, b):
            return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(max(len(a), len(b)))]

        def psub(a, b):
            return [(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(max(len(a), len(b)))]

        def pmul(a, b):
            out = [0] * (len(a) + len(b) - 1)
            for i, x in enumerate(a):
                for j, y in enumerate(b):
                    out[i + j] += x * y
            while len(out) > 1 and out[-1] == 0:
                out.pop()
            return out

        for t0, (counts, y0, y1, y2, z0, z1, z2, z3) in frontier.TRIPLE_ROOT_WITNESS_BRANCHES.items():
            # Verify k=0, 1, 2 (and huge k) directly against verify_triple_moments
            for k in (0, 1, 2, 10**60):
                w = frontier.triple_moments_witness(t0 + 4 * k)
                self.assertTrue(w["aggregate_equations_hold"])
                self.assertTrue(w["first_moment_equations_hold"])
                self.assertTrue(w["second_moment_equations_hold"])
                self.assertFalse(w["homometric_pair_proved"])

            # Prove quadratic Y and cubic Z remain inside Schur bounds for EVERY integer k >= 0
            base = frontier.triple_moments_witness(t0)
            for j, cell in enumerate(base["cells"]):
                if j == 0:
                    continue
                n_p = [cell["count"], 3780]
                p_p = [(cell["count"] + counts[j]) // 2, 1890]
                y_p = [y0[j], y1[j], y2[j]]
                z_p = [z0[j], z1[j], z2[j], z3[j]]
                two_tot_y = pmul(n_p, psub(n_p, [1]))
                m4_p = padd(pmul([2], y_p), two_tot_y)
                self.assertTrue(all(c % 4 == 0 for c in m4_p))
                m_p = [c // 4 for c in m4_p]
                six_tot_z = pmul(two_tot_y, psub(n_p, [2]))

                a_p = psub(pmul([2], m_p), pmul(p_p, psub(p_p, [1])))
                ub_24p2 = padd(
                    pmul(p_p, padd(padd(pmul([3], pmul(a_p, a_p)),
                                        pmul(pmul([6], pmul(p_p, psub(p_p, [2]))), a_p)),
                                   pmul(pmul([4], pmul(p_p, p_p)), pmul(psub(p_p, [1]), psub(p_p, [2]))))),
                    pmul(pmul([12], pmul(p_p, p_p)), padd(a_p, pmul([2], pmul(p_p, p_p)))),
                )
                lhs_min = psub(pmul(pmul([12], pmul(p_p, p_p)), z_p),
                               psub(ub_24p2, pmul(pmul([2], pmul(p_p, p_p)), six_tot_z)))
                self.assertTrue(all(c >= 0 for c in lhs_min))

                d_p = psub(n_p, p_p)
                b_p = pmul([2], d_p)
                u_p = psub(pmul(p_p, psub(psub(pmul([2], n_p), p_p), [1])), pmul([2], m_p))
                qn_p = psub(u_p, b_p)
                rn_p = psub(pmul(b_p, psub(p_p, [1])), u_p)
                ln_p = psub(pmul(b_p, n_p), rn_p)
                self.assertTrue(all(c >= 0 for c in psub(qn_p, b_p)))
                self.assertTrue(all(c >= 0 for c in rn_p))
                self.assertTrue(all(c >= 0 for c in psub(ln_p, pmul([2], b_p))))
                b3_p = pmul(b_p, pmul(b_p, b_p))
                s2_lb = padd(pmul(pmul(qn_p, psub(qn_p, b_p)), psub(qn_p, pmul([2], b_p))),
                             psub(pmul(b3_p, six_tot_z),
                                  pmul(pmul(ln_p, psub(ln_p, b_p)), psub(ln_p, pmul([2], b_p)))))
                rhs_max = psub(psub(pmul([2], s2_lb), pmul(b3_p, six_tot_z)), pmul(pmul([6], b3_p), z_p))
                self.assertTrue(all(c >= 0 for c in rhs_max))

            # Earlier 17-equation witness must fail E''(-1) = 0 for every t0 + 4k
            defect = frontier.bramble_second_moment_defect(t0)
            self.assertTrue(defect["second_moment_quadratic_annihilated"])
            self.assertNotEqual(defect["weighted_second_moment_defect"], 0)
            self.assertFalse(defect["triple_root_lift_possible_for_earlier_witness"])

        # CLI & corruption test for --triple-moments-witness and --structural-obstructions
        cli = [sys.executable, str(Path(frontier.__file__))]
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run(cli + ['4', '--triple-moments-witness'], text=True, capture_output=True, check=True)
            saved = json.loads(run.stdout)
            self.assertTrue(saved['second_moment_equations_hold'])
            path = Path(folder) / 'm25.json'
            path.write_text(json.dumps(saved))
            ok = subprocess.run(cli + ['--verify', str(path)], text=True, capture_output=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            saved['signed_second_moments'][1] += 2
            path.write_text(json.dumps(saved))
            bad = subprocess.run(cli + ['--verify', str(path)], text=True, capture_output=True)
            self.assertEqual(bad.returncode, 1, bad.stderr)
            st = subprocess.run(cli + ['1', '--structural-obstructions'], text=True, capture_output=True, check=True)
            st_data = json.loads(st.stdout)
            self.assertFalse(st_data['synchronized_periodic_fixed_hole_Q2_possible'])
            self.assertFalse(st_data['terminal_constant_run_possible'])
            self.assertTrue(st_data['cross_arm_23_exceeds_max_arm'])

        # Concrete positive-control witness check: T(27,11,3) with holes (1,9),(1,27) satisfies verify_triple_moments!
        small = frontier.compressed_system((27, 11, 3), [(1, 9), (1, 27)], 8)
        left_set = {(1, 1), (1, 3), (1, 5), (1, 8), (1, 11), (1, 12), (1, 13), (1, 15),
                    (1, 16), (1, 19), (1, 22), (1, 23), (1, 25), (1, 26), (2, 1), (2, 3),
                    (2, 5), (2, 6), (2, 9), (3, 2)}
        counts_small, y_small, z_small = [], [], []
        for cell in small["cells"]:
            depths = range(cell["first"], cell["hi"] + 1, 8)
            signs = [1 if (cell["arm"], d) in left_set else -1 for d in depths]
            counts_small.append(sum(signs))
            y_small.append(sum(j * s for j, s in enumerate(signs)))
            z_small.append(sum(j * (j - 1) // 2 * s for j, s in enumerate(signs)))
        res_small = frontier.verify_triple_moments(small, counts_small, y_small, z_small)
        self.assertTrue(res_small["second_moment_equations_hold"])


if __name__ == '__main__':
    unittest.main()
