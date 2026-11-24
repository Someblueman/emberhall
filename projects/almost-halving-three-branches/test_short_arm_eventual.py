"""Independent coefficient-counting checks of the eventual lift theorem."""
import itertools
import random
import unittest
import short_arm_eventual as s


def finite_coefficients(X, Y):
    # Build each original equation from individual signs, without polynomial
    # helpers, elimination, generating functions, or the parity criterion.
    lengths = [len(w) for w in X]
    answers = []
    for left, right in ((X, Y), (Y, X)):
        counts = [0]*(2*max(lengths)+1)
        for i in range(3):
            for depth, sign in enumerate(left[i]):
                counts[depth] += sign
                for j in range(3):
                    if j != i:
                        counts[depth+lengths[j]] -= sign
            for depth, sign in enumerate(right[i]):
                counts[lengths[i]-1-depth] -= sign
        answers.append(counts)
    return answers


def forced(a, x, y, q):
    # Independent formal-series long division of the published elimination;
    # no survivor classification used, so nonsurvivor boundaries are included.
    b = len(x)
    def plus(*ps):
        out = {}
        for p in ps:
            for k, v in p.items():
                out[k] = out.get(k, 0)+v
        return {k: v for k, v in out.items() if v}
    def times(p, r):
        return plus(*({i+j: v*w} for i, v in p.items() for j, w in r.items()))
    P = times(times({0: -1, 1: 1}, {0: 1, b: -1}), {0: 1, b-1: 1})
    C = {b: 1, b-1: -1, 0: -1}
    def row(u, v, p, r):
        N = plus(times({0: -1, 1: 1}, plus(times(C, dict(enumerate(u))),
                   {2*b-2-k: val for k, val in enumerate(v)})),
                 times({0: -1, b: 1}, plus({k: p*val for k, val in C.items()}, {0: r})))
        seq = []
        for n in range(a):
            seq.append(-N.get(n, 0)+sum(val*seq[n-k] for k, val in P.items() if 0 < k <= n))
        seq[-1] -= v[-1]+r
        return seq
    return [row(x, y, 1, q), list(x), [1]], [row(y, x, q, 1), list(y), [q]]


class EventualTests(unittest.TestCase):
    def test_formal_proof_and_corruption(self):
        self.assertTrue(s.prove_identities()['altered_pair_rejected'])

    def test_all_boundaries_small_b_against_original_equations(self):
        for b in (2, 4):
            for a in (s.threshold(b), s.threshold(b)+2, s.threshold(b)+4):
                admitted = []
                for bits in itertools.product((-1, 1), repeat=2*b+1):
                    x, y, q = bits[:b], bits[b:2*b], bits[-1]
                    X, Y = forced(a, x, y, q)
                    if any(v not in (-1, 1) for w in X+Y for v in w):
                        continue
                    independent = finite_coefficients(X, Y)
                    self.assertEqual([dict((i, v) for i, v in enumerate(r) if v) for r in independent], s.equations(X, Y))
                    if not any(any(r) for r in independent):
                        admitted.append(bits)
                expected = [(-1,)*b+(1,)*b+(-1,)] if a % (2*(b-1)) == 0 else []
                self.assertEqual(admitted, expected)

    def test_typeA_parity_and_finite_exclusion(self):
        for b in (2, 4, 6, 8):
            L = b-1
            for middle in itertools.product((-1, 1), repeat=b-2):
                for endpoint in (-1, 1):
                    x = (endpoint,)+middle+(endpoint,)
                    y = x[::-1]
                    for residue in range(0, 2*L, 2):
                        a = 4*L+residue
                        X, Y = s.candidate(a, x, y, 1)
                        self.assertTrue(any(any(r) for r in finite_coefficients(X, Y)))
                    # Interior periodic extensions start with +1, independent
                    # of the exceptional coefficient at depth zero.
                    U = [1]+[-v for v in middle]
                    V = [1]+[-v for v in middle[::-1]]
                    U += [-v for v in U[:]]
                    V += [-v for v in V[:]]
                    self.assertEqual(sum(U[::2])-sum(V[1::2]), 2)

    def test_typeB_every_residue_and_fresh_large_lengths(self):
        for b in (2, 4, 6, 10, 18):
            L = b-1
            for residue in range(0, 2*L, 2):
                a = 4*L+residue
                X, Y = s.candidate(a, (-1,)*b, (1,)*b, -1)
                self.assertEqual(not any(any(r) for r in finite_coefficients(X, Y)), residue == 0)
            a = ((s.threshold(b)+2*L-1)//(2*L)+2)*(2*L)
            report = s.solve_eventual(a, b)
            self.assertTrue(report['solvable'])
            self.assertFalse(any(any(r) for r in finite_coefficients(report['X'], report['Y'])))
            if b > 2:
                self.assertFalse(s.solve_eventual(a+2, b)['solvable'])

    def test_random_boundary_stream_formula_and_tip_correction(self):
        rng = random.Random(2718)
        for b in (4, 12, 24):
            for _ in range(12):
                endpoint = rng.choice((-1, 1))
                x = (endpoint,)+tuple(rng.choice((-1, 1)) for _ in range(b-2))+(endpoint,)
                a = 4*b+2
                self.assertEqual(s.candidate(a, x, x[::-1], 1), forced(a, x, x[::-1], 1))
        for bad in ((7, 4), (6, 4), (40, 3)):
            with self.assertRaises(ValueError):
                s.solve_eventual(*bad)


if __name__ == '__main__':
    unittest.main()
