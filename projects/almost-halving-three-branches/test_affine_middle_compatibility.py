import random
import unittest
import affine_middle_compatibility as ac
import full_shorter_coupling as fc
from test_aperiodic_completion import bfs_shells


class AffineCompatibilityTests(unittest.TestCase):
    def test_all_scale_identity_endpoints(self):
        rng = random.Random(24511)
        for t in range(1, 10):
            for h in range(2*t-1):
                z = {i: rng.randrange(-5, 6) for i in range(1, 5*t+1)}
                b = {i: sum(c*z[d-13*t] for d, c in fc.middle_operator(t, h, 13*t+i).items())
                     for i in z}
                c = ac.recurrence_forcing(t, h, b)
                a, n, H = 2*t+h+1, 5*t, h+1
                for m in range(1, (n-a)//H+2):
                    lo = a+(m-1)*H
                    for u, v in [(lo, lo), (lo, n), (n, n)]:
                        lhs = sum(c[i-k*H] for i in range(u, v+1) for k in range(m))
                        terms = ac.endpoint_terms(h, u, v, m)
                        self.assertTrue(all(1 <= i <= n for i in terms))
                        self.assertEqual(lhs, sum(value*z[i] for i, value in terms.items()))

    def test_every_literal_middle_passes(self):
        rng = random.Random(8173)
        for t in range(1, 15):
            for h in range(2*t-1):
                z = {i: rng.choice((-1, 1)) for i in range(1, 5*t+1)}
                b = {i: sum(c*z[d-13*t] for d, c in fc.middle_operator(t, h, 13*t+i).items())
                     for i in z}
                self.assertFalse(ac.rectangle_test(t, h, b)['excluded'])

    def test_scan_against_exhaustive_rectangles(self):
        rng = random.Random(9173)
        for t in range(1, 8):
            for h in range(2*t-1):
                b = {i: rng.choice((-4, -2, 0, 2, 4)) for i in range(1, 5*t+1)}
                c = ac.recurrence_forcing(t, h, b)
                a, n, H = 2*t+h+1, 5*t, h+1
                fail = False
                for m in range(1, (n-a)//H+2):
                    for u in range(a+(m-1)*H, n+1):
                        for v in range(u, n+1):
                            value = sum(c[i-k*H] for i in range(u, v+1) for k in range(m))
                            fail |= abs(value) > 8
                self.assertEqual(ac.rectangle_test(t, h, b)['excluded'], fail)

    def test_literal_second_word_beyond_reflected_test(self):
        t, h = 3, 1
        word = ['+']*(79*t)
        for d in [38, 151, 11, 197, 50, 204, 35]: word[d-1] = '-'
        b = ac.forcing(t, h, 1, ''.join(word))
        self.assertTrue(ac.reflected_test(t, b))
        q = ac.rectangle_test(t, h, b)
        self.assertTrue(q['excluded'])
        self.assertLessEqual(max(map(abs, b.values())), 4)
        self.assertEqual(q['rectangle'], [14, 15, 1])
        self.assertEqual(q['value'], 10)

    def test_accumulation_is_stronger_than_individual_recurrence_rows(self):
        t, h = 5, 2
        word = ['+']*(79*t)
        for d in [311, 138, 262, 229]: word[d-1] = '-'
        b = ac.forcing(t, h, 1, ''.join(word))
        self.assertEqual(ac.reflected_test(t, b), [-2])
        self.assertLessEqual(max(map(abs, b.values())), 4)
        self.assertLessEqual(max(map(abs, ac.recurrence_forcing(t, h, b).values())), 4)
        q = ac.rectangle_test(t, h, b)
        self.assertEqual(q['rectangle'], [19, 22, 3])
        self.assertEqual(q['value'], -10)

    def test_independent_adjacency_bfs(self):
        rng = random.Random(38191)
        for t in (1, 2, 3):
            for h in sorted({0, 2*t-2}):
                L, holes = fc.geometry(t, h)
                y = {d: rng.choice((-1, 1)) for d in range(1, 79*t+1)}
                z = {d: rng.choice((-2, -1, 0, 1, 2)) for d in range(13*t+1, 18*t+1)}
                zero = dict.fromkeys(z, 0)
                baseline = fc.linear_completion(t, h, 1 if h else 0, y, zero)
                changed = fc.linear_completion(t, h, 1 if h else 0, y, z)
                F0, _ = bfs_shells(L, baseline)
                F1, _ = bfs_shells(L, changed)
                b = ac.forcing(t, h, 1 if h else 0,
                               ''.join('+' if y[d] == 1 else '-' for d in y))
                for i in range(1, 5*t+1):
                    e = 92*t+1+i
                    self.assertEqual(b[i], F0[e]-F0[e-1])
                    image = sum(c*z[d] for d, c in fc.middle_operator(t, h, 13*t+i).items())
                    self.assertEqual(F1[e]-F1[e-1], b[i]-image)

    def test_centre_hole_exact_inverse(self):
        from fractions import Fraction
        rng = random.Random(921101)
        for t in range(1, 31):
            b = {i: Fraction(rng.randrange(-7, 8), rng.randrange(1, 5)) for i in range(1, 5*t+1)}
            z = ac.solve_centre_hole(t, b)
            for i in b:
                self.assertEqual(sum(c*z[d-13*t] for d, c in fc.middle_operator(t, 0, 13*t+i).items()), b[i])
            literal = {i: rng.choice((-1, 1)) for i in b}
            image = {i: sum(c*literal[d-13*t] for d, c in fc.middle_operator(t, 0, 13*t+i).items()) for i in b}
            self.assertEqual(ac.solve_centre_hole(t, image), literal)
        self.assertTrue(all(isinstance(v, Fraction) for v in z.values()))

    def test_exact_seed_elimination_against_full_rational_matrix(self):
        from fractions import Fraction
        rng = random.Random(4117)
        def rank(rows):
            rows = [[Fraction(v) for v in row] for row in rows]
            r = 0
            for col in range(len(rows[0])):
                k = next((i for i in range(r, len(rows)) if rows[i][col]), None)
                if k is None: continue
                rows[r], rows[k] = rows[k], rows[r]
                scale = rows[r][col]
                rows[r] = [v/scale for v in rows[r]]
                for i in range(r+1, len(rows)):
                    scale = rows[i][col]
                    rows[i] = [v-scale*w for v, w in zip(rows[i], rows[r])]
                r += 1
                if r == len(rows): break
            return r
        for t in range(1, 7):
            for h in range(2*t-1):
                n = 5*t
                matrix = [[fc.middle_operator(t, h, 13*t+i).get(13*t+j, 0)
                           for j in range(1, n+1)] for i in range(1, n+1)]
                expected_rank = rank(matrix)
                b = {i: Fraction(rng.randrange(-3, 4), 2) for i in range(1, n+1)}
                result = ac.exact_middle(t, h, b)
                augmented_rank = rank([row+[b[i]] for i, row in enumerate(matrix, 1)])
                self.assertEqual(result['consistent'], expected_rank == augmented_rank)
                # Guaranteed-consistent nonzero forcing exercises every singular scale.
                target = [rng.randrange(-3, 4) for _ in range(n)]
                b = {i: sum(a*x for a, x in zip(row, target)) for i, row in enumerate(matrix, 1)}
                result = ac.exact_middle(t, h, b)
                self.assertTrue(result['consistent'])
                self.assertEqual(result['rational_kernel_dimension'], n-expected_rank)
                self.assertEqual(result['rational_cokernel_dimension'], n-expected_rank)
                vectors = [result['middle']]
                vectors += [{i: sum(a*x for a, x in zip(row, seed))
                             for i, row in result['transfer'].items()}
                            for seed in result['kernel_seeds']]
                for k, vector in enumerate(vectors):
                    for i, row in enumerate(matrix, 1):
                        self.assertEqual(sum(a*vector[j] for j, a in enumerate(row, 1)), b[i] if k == 0 else 0)

    def test_validation(self):
        for t, h in [(0, 0), (1, 1), (2, -1), (True, 0)]:
            with self.assertRaises(ValueError): ac.validate(t, h)
        with self.assertRaises(ValueError): ac.forcing(1, 0, 1, '+'*79)
        with self.assertRaises(ValueError): ac.forcing(1, 0, 0, '+'*78)


if __name__ == '__main__': unittest.main()
