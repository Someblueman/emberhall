"""Independent recurrence and local-identity checks for the uniform theorem."""
from itertools import product
import random
import unittest

from short_arm_structure import (classify, coefficients, explicit_stream,
                                 prove_identities, survivor_type)
from short_arm_lifts import elimination


def reference(x, y, q, length):
    P, nums = elimination(len(x), x, y, 1, q)
    out = [[], []]
    for k in range(length):
        for s, n in zip(out, nums):
            s.append(-n.get(k, 0)+sum(c*s[k-j] for j, c in P.items() if 0 < j <= k))
    return out


class ShortArmStructureTest(unittest.TestCase):
    def test_formal_identities_and_base_case(self):
        result = prove_identities()
        self.assertEqual(result['base_b2_survivors'], 3)
        self.assertEqual(result['type_A_identity_terms'], 0)
        self.assertEqual(result['type_B_identity_terms'], 0)
        self.assertEqual(result['local_coefficient_identity_terms'], 0)
        self.assertGreater(result['corrupt_identity_terms'], 0)

    def test_all_boundaries_through_middle_six(self):
        for b in (2, 4, 6):
            count = 0
            for values in product((-1, 1), repeat=2*b+1):
                x, y, q = values[:b], values[b:2*b], values[-1]
                result = classify(x, y, q)
                count += result['infinite_valid']
                if not result['infinite_valid']:
                    k, arm, value = result['first_invalid']
                    self.assertEqual(reference(x, y, q, k+1)[arm][k], value)
            self.assertEqual(count, 2**(b-1)+1)

    def test_independent_recurrence_beyond_old_census(self):
        rng = random.Random(68319)
        for b in (8, 10, 12, 16, 20):
            for _ in range(10):
                x = tuple(rng.choice((-1, 1)) for _ in range(b))
                y = tuple(rng.choice((-1, 1)) for _ in range(b))
                q = rng.choice((-1, 1))
                self.assertEqual(coefficients(x, y, q, 3*b), reference(x, y, q, 3*b))
                self.assertEqual(classify(x, y, q)['infinite_valid'], survivor_type(x, y, q) is not None)
            x = [rng.choice((-1, 1)) for _ in range(b)]
            x[-1] = x[0]
            y = x[::-1]
            length = 4*b*(b-1)
            self.assertEqual(reference(x, y, 1, length), explicit_stream(x, y, 1, length))
            self.assertEqual(reference([-1]*b, [1]*b, -1, length),
                             explicit_stream([-1]*b, [1]*b, -1, length))

    def test_local_necessity_identities(self):
        rng = random.Random(117)
        for b in (4, 6, 8, 12, 18):
            for u, v in product((-1, 1), repeat=2):
                x, y = [-1]*(b-1)+[u], [1]*(b-1)+[v]
                X, Y = reference(x, y, -1, 2*b)
                self.assertEqual((X[2*b-1], Y[2*b-1]), (v-2, u+2))
            for _ in range(10):
                x = [rng.choice((-1, 1)) for _ in range(b)]
                y = [rng.choice((-1, 1)) for _ in range(b)]
                X, Y = reference(x, y, 1, 2*b)
                self.assertEqual(X[b-1], -x[-1]+y[-1]-1)
                self.assertEqual(X[2*b-1], -x[0]-y[b-2]+y[-1])
                self.assertEqual(Y[2*b-2], x[0]-x[-1]+1)

    def test_validation(self):
        for x, y, q in (([1]*3, [1]*3, 1), ([1]*4, [1]*2, 1), ([0, 1], [1, 1], 1), ([1.0, 1], [1, 1], 1), ([True, 1], [1, 1], 1)):
            with self.assertRaises(ValueError):
                classify(x, y, q)


if __name__ == '__main__':
    unittest.main()
