"""Independent exact linear-system checks for the short-arm lift classifier."""
from collections import Counter, deque
from fractions import Fraction
from itertools import product
import unittest

from short_arm_lifts import (period_bound_certificate, construct_double, prove_double_family, construct_uniform, prove_uniform_family, branches, construct, elimination, extend, forced_stream,
                             prove_four_arm, prove_fixed_middle, residuals, solve, cancellation_indices)
from two_row_subdivision import _build_two_row_matrix


def rational_count(a, b=4):
    # Independent matrix construction in two_row_subdivision, then exact Q RREF.
    matrix, n = _build_two_row_matrix((a, b, 1))
    rows = [[Fraction(v) for v in row] for row in matrix]
    pivots, rank = [], 0
    for c in range(n):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][c]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        f = rows[rank][c]
        rows[rank] = [v/f for v in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][c]:
                f = rows[r][c]
                rows[r] = [x-f*y for x, y in zip(rows[r], rows[rank])]
        pivots.append(c)
        rank += 1
    free = [c for c in range(n) if c not in pivots]
    count = 0
    for values in product((-1, 1), repeat=len(free)):
        vec = [Fraction(0)]*n
        for c, v in zip(free, values):
            vec[c] = v
        for r, c in enumerate(pivots):
            vec[c] = -sum(rows[r][f]*vec[f] for f in free)
        if all(v in (-1, 1) for v in vec):
            count += 1
    return count//2


class ShortArmLiftsTest(unittest.TestCase):
    def test_complete_infinite_certificate(self):
        proof = prove_four_arm()
        self.assertEqual(proof['tail_solution_counts_up_to_sign'], {0: 1, 2: 0, 4: 0})
        self.assertEqual(proof['boundary_choices_up_to_sign'], 512)

    def test_independent_rational_matrix_exhaustion(self):
        for a in (6, 8, 10, 12, 14, 16, 18):
            self.assertEqual(len(solve(a)), rational_count(a), a)

    def test_other_middle_lengths(self):
        for b in (2, 6):
            proof = prove_fixed_middle(b)
            self.assertEqual(proof["proof"], "PASS")
        for a, b in ((4, 2), (8, 2), (8, 6), (10, 6), (12, 6), (14, 6)):
            self.assertEqual(len(solve(a, b)), rational_count(a, b))
        for a in (32, 34, 36, 38, 40, 50):
            self.assertEqual(len(solve(a, 6)), int(a % 10 == 0))

    def test_middle_eight_certificate(self):
        proof = prove_fixed_middle(8)
        self.assertEqual(proof["boundary_choices_up_to_sign"], 131072)
        self.assertEqual(proof["tail_solution_counts_up_to_sign"],
                         {r: int(r == 0) for r in range(0, 14, 2)})
        # Independent full-matrix Q elimination at an exceptional length.
        self.assertEqual(rational_count(12, 8), 10)

    def test_last_coefficient_boundary_correction(self):
        # A term z^(a-1) survives elimination. Omitting its correction
        # incorrectly rejects even the known gap-two solution at a=6.
        x, y = (1,)*4, (-1, 1)*2
        seq, info = forced_stream(4, x, y, 1, 1)
        raw = [extend(s, info, 6) for s in seq]
        self.assertTrue(any(residuals(6, 4, *raw, x, y, 1, 1)))
        raw[0][-1] -= y[-1]+1
        raw[1][-1] -= x[-1]+1
        self.assertEqual(residuals(6, 4, *raw, x, y, 1, 1), [{}, {}])

    def test_large_residue_classes_and_corruption(self):
        for a in (24, 26, 28, 30, 60, 62, 64, 120):
            solutions = solve(a)
            self.assertEqual(len(solutions), int(a % 6 == 0))
            for s in solutions:
                X, Y = s['X'], s['Y']
                self.assertEqual(residuals(a, 4, X[0], Y[0], X[1], Y[1], X[2][0], Y[2][0]), [{}, {}])
                X[0][0] *= -1
                self.assertTrue(any(residuals(a, 4, X[0], Y[0], X[1], Y[1], 1, Y[2][0])))

    def test_quadratic_stream_bound(self):
        for b in (2, 4, 6, 8, 10, 12):
            proof = period_bound_certificate(b)
            self.assertEqual(proof["period_multiple"], b*(b-1))
            self.assertEqual(proof["remainder_terms"], 0)
            self.assertEqual(proof["quotient_degree"], 2*b*(b-1)-2*b)
        with self.assertRaises(ValueError):
            period_bound_certificate(3)

    def test_elimination_denominator_factorization(self):
        for b in (2, 4, 6):
            P, _ = elimination(b, [1]*b, [-1]*b, 1, -1)
            expected = Counter()
            for i, ci in ((0, -1), (1, 1)):
                for j, cj in ((0, 1), (b, -1)):
                    for k, ck in ((0, 1), (b-1, 1)):
                        expected[i+j+k] += ci*cj*ck
            self.assertEqual(P, {k: v for k, v in expected.items() if v})

    def test_affine_tail_cancellation(self):
        self.assertIsNone(cancellation_indices({}, 6))
        self.assertEqual(cancellation_indices({(12, 0): 1, (0, 1): -1}, 6), {2})
        self.assertEqual(cancellation_indices({(13, 0): 1, (0, 1): -1}, 6), set())
        self.assertEqual(cancellation_indices({(0, 0): 1}, 6), set())

    def test_construct_bfs_and_full_coverage(self):
        for a, b in ((8, 4), (12, 4), (10, 6), (6, 2)):
            w = construct(a, 3, b=b)
            lengths = w['lengths']
            adj = {(0, 0): []}
            for arm, length in enumerate(lengths, 1):
                previous = (0, 0)
                for depth in range(1, length+1):
                    v = (arm, depth)
                    adj[v] = [previous]
                    adj[previous].append(v)
                    previous = v
            left, right = set(map(tuple, w['left'])), set(map(tuple, w['right']))
            self.assertFalse(left & right)
            self.assertEqual(left | right, set(adj))
            self.assertEqual(len(left), len(right))
            def profile(vertices):
                out = Counter()
                vertices = sorted(vertices)
                for i, src in enumerate(vertices):
                    distances, queue = {src: 0}, deque([src])
                    while queue:
                        v = queue.popleft()
                        for u in adj[v]:
                            if u not in distances:
                                distances[u] = distances[v]+1
                                queue.append(u)
                    out.update(distances[v] for v in vertices[i+1:])
                return out
            self.assertEqual(profile(left), profile(right))

    def test_uniform_family_outside_enumeration_cap(self):
        proof = prove_uniform_family()
        self.assertEqual(proof["e1_terms"], 0)
        self.assertEqual(proof["e2_terms"], 0)
        self.assertGreater(proof["corrupt_short_word_terms"], 0)
        for b, k, g in ((2, 3, 3), (10, 1, 3), (12, 2, 5)):
            pair = construct_uniform(b, k, g)
            self.assertTrue(pair["homometric"])
            self.assertEqual(pair["lengths"], [2*k*(b-1)*g, b*g, g])
            self.assertEqual(2*pair["size"], 1+sum(pair["lengths"]))
        for b, k, g in ((3, 1, 3), (2, 1, 3), (4, 0, 3), (4, 1, 4)):
            with self.assertRaises(ValueError):
                construct_uniform(b, k, g)

    def test_double_family(self):
        proof = prove_double_family()
        self.assertEqual((proof["e1_terms"], proof["e2_terms"]), (0, 0))
        self.assertGreater(proof["corrupt_short_word_terms"], 0)
        for b in (4, 6, 10, 12):
            w = construct_double(b, 3)
            self.assertTrue(w["homometric"])
            self.assertEqual(w["lengths"], [6*b, 3*b, 3])
            self.assertEqual(2*w["size"], 1+sum(w["lengths"]))
        for b in (2, 5, True):
            with self.assertRaises(ValueError):
                construct_double(b, 3)

    def test_invalid_inputs_and_scope(self):
        for a, b in ((4, 4), (7, 4), (12, 3), (12, 10), (True, 4)):
            with self.assertRaises(ValueError):
                solve(a, b)
        with self.assertRaisesRegex(ValueError, 'arbitrary partitions'):
            construct(14, 3)
        with self.assertRaises(ValueError):
            construct(12, 4)


if __name__ == '__main__':
    unittest.main()
