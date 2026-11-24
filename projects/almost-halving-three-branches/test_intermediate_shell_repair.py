"""Independent original-tree and exhaustive controls for upper-shell completion."""
from collections import Counter, deque
from itertools import combinations, product
import random
import unittest

import intermediate_shell_repair as repair


SEED = ('+-+-+-+-+-+-+-+-+-0-+-++++++++++++++++-+-++++++++++++++++'
        '-+-++++++++++++++++-+--+-+-+-+-+-+-+-+-+-0',
        '+-+-+-+-+-+-+-+-+-++-+----------------+-+----------------'
        '+-++-+-+-+-+-+-+-+-+-+',
        '+-+-----------------+-+')


def graph_distances(lengths):
    graph = {(0, 0): []}
    for arm, n in enumerate(lengths, 1):
        previous = (0, 0)
        for d in range(1, n+1):
            vertex = (arm, d)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    result = {}
    for source in graph:
        row, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for other in graph[vertex]:
                if other not in row:
                    row[other] = row[vertex]+1
                    queue.append(other)
        result[source] = row
    return result


def bfs_counts(words, distances):
    vertices = {(i, d): v for i, w in enumerate(words, 1)
                for d, v in enumerate(w, 1) if v}
    vertices[0, 0] = -1
    profiles = []
    for sign in (1, -1):
        group = [v for v in vertices if vertices[v] == sign]
        profiles.append(Counter(distances[u][v] for u, v in combinations(group, 2)))
    return profiles


class UpperShellTests(unittest.TestCase):
    def test_equivalence_and_uniqueness_exhaustive(self):
        # No completion equation is used by the BFS oracle. Includes B+C>A,
        # B+C=A and B+C<A, and an interior hole next to the forced suffix.
        for lengths, h in (((6, 4, 3), 1), ((7, 4, 3), 2), ((8, 4, 2), 3)):
            a, b, c = lengths
            distances = graph_distances(lengths)
            for bits in product((-1, 1), repeat=b+c):
                y, z = list(bits[:b]), list(bits[b:])
                expected = []
                for suffix in product((-1, 1), repeat=b-1):
                    x = [1]*(a-b)+list(suffix)+[0]
                    x[h-1] = 0
                    words = [x, y, z]
                    pos, neg = bfs_counts(words, distances)
                    equal = all(pos[d] == neg[d] for d in range(a+1, a+b))
                    self.assertEqual(repair.audit_upper(lengths, h, words)['upper_shells_equal'], equal)
                    if equal:
                        expected.append(list(suffix))
                actual = repair.complete_upper(lengths, h, y, z)
                self.assertEqual(expected, [actual['suffix']] if actual['sign_feasible'] else [])

    def test_literal_counter_against_fresh_bfs(self):
        rng = random.Random(923178)
        for lengths, h in (((13, 9, 6), 3), ((17, 12, 8), 4), ((19, 11, 5), 7)):
            distances = graph_distances(lengths)
            for _ in range(8):
                words = [[rng.choice((-1, 1)) for _ in range(n)] for n in lengths]
                words[0][h-1] = words[0][-1] = 0
                profiles = bfs_counts(words, distances)
                for d in range(lengths[0]+1, lengths[0]+lengths[1]+1):
                    self.assertEqual(repair.actual_upper_counts(lengths, h, words, d),
                                     (profiles[0][d], profiles[1][d]))

    def test_real_seed_and_altered_witness(self):
        words = [[0 if v == '0' else 1 if v == '+' else -1 for v in w] for w in SEED]
        self.assertTrue(repair.audit_upper((99, 79, 23), 19, words)['upper_shells_equal'])
        words[0][-2] *= -1
        self.assertFalse(repair.audit_upper((99, 79, 23), 19, words)['upper_shells_equal'])
        pos, neg = repair.actual_upper_counts((99, 79, 23), 19, words, 177)
        self.assertNotEqual(pos, neg)

    def test_all_parameter_forced_window(self):
        # The retained last 23 signs are untouched by any of the eight
        # minimal corrections, which lie at offsets 61..75.
        observed = {}
        for j in range(1, 24):
            q = 1 if SEED[0][98-j] == '+' else -1
            z = 1 if SEED[2][23-j] == '+' else -1
            if q == z:
                observed[j] = -q
        self.assertEqual(observed, repair.FORCED)
        for k in (1, 4, 17, 10**12):
            result = repair.frontier_restriction(k)
            t = result['t']
            self.assertEqual(len(result['required_arm1'])+len(result['required_arm2']), 24)
            for j in repair.FORCED:
                self.assertTrue(19 < 43*t-j <= 19+99*(t-1))
                self.assertTrue(0 < 23*t-j+1 <= 79*(t-1))
                self.assertLess(79*t-23*t+j, 99*t-23*t)

    def test_full_identity_against_independent_unbalanced_graphs(self):
        rng = random.Random(19479)
        for lengths, h in (((11, 7, 4), 3), ((15, 9, 5), 4), ((21, 13, 7), 6)):
            distances = graph_distances(lengths)
            for _ in range(10):
                words = [[rng.choice((-1, 1)) for _ in range(n)] for n in lengths]
                words[0][h-1] = words[0][-1] = 0
                profiles = bfs_counts(words, distances)
                expected = Counter()
                for d in set(profiles[0]) | set(profiles[1]):
                    difference = 2*(profiles[0][d]-profiles[1][d])
                    expected[d] += difference
                    expected[d+1] -= difference
                expected[1] -= 2*(-1+sum(map(sum, words)))
                self.assertEqual(repair.full_identity(lengths, h, -1, words),
                                 {d: v for d, v in expected.items() if v})

    def test_two_sided_completion_recovers_full_seed(self):
        words = [[0 if v == '0' else 1 if v == '+' else -1 for v in row] for row in SEED]
        result = repair.complete_family_first_arm(0, -1, words[0][:18], words[1], words[2])
        self.assertTrue(result['valid'])
        self.assertEqual(result['arm1'], words[0])
        profiles = bfs_counts(words, graph_distances((99, 79, 23)))
        self.assertEqual(profiles[0], profiles[1])
        self.assertEqual(sum(profiles[0].values()), 4950)
        # The full identity catches an alteration outside the upper suffix,
        # while upper-shell equality on its own intentionally still passes.
        words[0][0] *= -1
        self.assertTrue(repair.audit_upper((99, 79, 23), 19, words)['upper_shells_equal'])
        self.assertTrue(repair.full_identity((99, 79, 23), 19, -1, words))
        altered = bfs_counts(words, graph_distances((99, 79, 23)))
        self.assertNotEqual(altered[0], altered[1])

    def test_twenty_shell_restriction_against_full_literal_identity(self):
        survivors = 0
        for bits in product((-1, 1), repeat=4):
            y, z = [bits[0], bits[2]], [bits[1], bits[3]]
            result = repair.local_twenty(y, z)
            survivors += result['valid']
            for t in (3, 5):
                # Fresh unequal triples. Only literal boundary words enter
                # the tested coefficients; every other sign is arbitrary.
                words = []
                for arm, (base, cut) in enumerate(((99, 19), (79, 0), (23, 0))):
                    seed = [0 if v == '0' else 1 if v == '+' else -1 for v in SEED[arm]]
                    words.append(seed[:cut]+[-1]*(base*(t-1))+seed[cut:])
                words[1][:17] = [1, 1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1]
                words[1][17:19], words[2][17:19] = y, z
                # Choosing any literal candidate for x38,x39 lets us check
                # the exact equations independently of the local solver.
                for x38, x39 in product((-1, 1), repeat=2):
                    words[0][37:39] = [x38, x39]
                    residual = repair.full_identity(tuple(map(len, words)), 19, -1, words)
                    self.assertEqual(residual.get(19, 0), result['arm1_depth38']-x38)
                    self.assertEqual(residual.get(20, 0), x38+y[1]+z[1]-x39)
        self.assertEqual(survivors, 9)
        self.assertFalse(repair.local_twenty([-1, -1], [-1, -1])['valid'])
        self.assertTrue(repair.local_twenty([-1, 1], [-1, -1])['valid'])

    def test_boundary_count_by_independent_two_state_matrices(self):
        populations = []
        for initial in ([2, 0], [0, 1]):
            minus, plus = initial
            for old, new in zip(repair.LOCAL_K[1:], repair.LOCAL_K[2:]):
                if old == new:
                    minus, plus = 2*minus+plus, minus+2*plus
                else:
                    self.assertEqual(new-old, 2)
                    minus, plus = minus, 2*minus+plus
            populations.append((minus, plus))
        self.assertEqual(populations, [(1238004, 1794474), (547641, 793800)])
        a, b = populations[0]
        c, d = populations[1]
        result = repair.boundary_twenty_count()
        self.assertEqual(result['first_18_prefix_pairs'], a+b+c+d)
        self.assertEqual(result['first_20_prefix_pairs'], 9*a+3*b+7*c+3*d)
        self.assertEqual(result['first_20_prefix_pairs'], 22740345)

    def test_periodic_certificate_cancellation_and_separation(self):
        for k in (1, 3, 17):
            for period in range(1, 2660*k+1):
                if (2660*k) % period:
                    continue
                result = repair.periodic_obstruction(period, k)
                self.assertEqual(result['sum'], {'constant': -2})
                self.assertLess(result['maximum_z_span'], result['minimum_bin_separation'])
                self.assertEqual((2660*k) % result['effective_period'], 0)
        for period in (0, 3, 2661):
            with self.assertRaises(ValueError):
                repair.periodic_obstruction(period)

    def test_four_rows_against_fresh_literal_full_identities(self):
        rng = random.Random(7519)
        for k, period, choice in ((1, 7, 173), (1, 20, 0), (2, 19, 255),
                                  (1, 2660, 85), (3, 3, 146), (3, 3990, 42)):
            blocks = [[rng.choice((-1, 1)) for _ in range(period)] for _ in range(3)]
            words = repair.periodic_words(k, blocks, choice)
            residual = repair.full_identity(tuple(map(len, words)), 19, -1, words)
            certificate = repair.periodic_obstruction(period, k)
            p = certificate['effective_period']
            coeffs = [residual.get(6+base*2660*k, 0)-residual.get(6+base*2660*k-p, 0)
                      for base in (0, 23, 79, 99)]
            # Normalize short blocks to the certificate's effective period.
            a5, a6 = blocks[0][4 % period], blocks[0][5 % period]
            b5, c5 = blocks[1][4 % period], blocks[2][4 % period]
            u75 = 1 if choice & 128 else -1
            self.assertEqual(coeffs, [a5-a6+b5+c5, -1-c5, -b5-u75,
                                      -1-a5+a6+u75])
            self.assertEqual(sum(coeffs), -2)
            self.assertTrue(residual)

    def test_geometric_coefficient_reader_against_full_graph_identity(self):
        rng = random.Random(266079)
        for lengths, h in (((11, 7, 4), 3), ((15, 9, 5), 4), ((21, 13, 7), 6)):
            words = [[rng.choice((-1, 1)) for _ in range(n)] for n in lengths]
            words[0][h-1] = words[0][-1] = 0
            residual = repair.full_identity(lengths, h, -1, words)
            for n in range(-1, lengths[0]+lengths[1]+3):
                row = repair._coefficient_row(lengths, h, n)
                value = sum(coefficient*(-1 if arm == 0 else words[arm-1][depth-1])
                            for (arm, depth), coefficient in row.items())
                self.assertEqual(value, residual.get(n, 0))

    def test_local_matching_obstruction_allows_nonperiodic_interiors(self):
        for k, period, choice in ((1, 20, 0), (2, 19, 173), (3, 3, 255)):
            certificate = repair.local_repair_equation(k, period)
            p = certificate['effective_period']
            words = repair.periodic_words(k, [[1]*period, [-1]*period, [1]*period], choice)
            named = {(arm, depth) for arm, depth, _, _ in certificate['terms']}
            # This breaks full periodicity outside every named boundary.
            depth = next(d for d in range(10000, 11000) if (2, d) not in named)
            words[1][depth-1] *= -1
            residual = repair.full_identity(tuple(map(len, words)), 19, -1, words)
            actual = sum(residual.get(6+base*2660*k, 0)
                         -residual.get(6+base*2660*k-p, 0) for base in (0, 23, 79, 99))
            equation = certificate['constant']+sum(
                coefficient*words[arm-1][d-1] for arm, d, coefficient, _ in certificate['terms'])
            self.assertEqual(actual, equation)
            self.assertEqual(actual, -2)
            self.assertLessEqual(len(named), 232)
        # Huge scales are still exact bounded-size algebra, not generated trees.
        for k, p in ((10**18, 2660*10**18), (3, 6), (17, 7)):
            certificate = repair.local_repair_equation(k, p)
            self.assertEqual(certificate['constant'], -2)

    def test_arbitrary_word_window_audit_refuses_false_full_verdict(self):
        words = repair.periodic_words(1, [[1]*20]*3, 85)
        before = repair.audit_repair_window(1, 20, words)
        self.assertTrue(before['locally_matching'])
        self.assertTrue(before['excluded_by_this_equation'])
        certificate = repair.local_repair_equation(1, 20)
        arm, depth, _, _ = next(term for term in certificate['terms'] if term[2] == -1)
        words[arm-1][depth-1] = -1
        after = repair.audit_repair_window(1, 20, words)
        self.assertTrue(after['necessary_equation_passes'])
        self.assertFalse(after['full_homometry_claimed'])
        self.assertTrue(repair.full_identity(tuple(map(len, words)), 19, -1, words))
        words[0][0] *= -1
        with self.assertRaises(ValueError):
            repair.audit_repair_window(1, 20, words)

    def test_validation(self):
        for lengths, h in (((6, 4, 3), 3), ((6, 6, 3), 1), ((True, 4, 3), 1)):
            with self.assertRaises(ValueError):
                repair.complete_upper(lengths, h, [1]*4, [1]*3)
        with self.assertRaises(ValueError):
            repair.complete_upper((7, 4, 2), 1, [True]*4, [1]*2)


if __name__ == '__main__':
    unittest.main()
