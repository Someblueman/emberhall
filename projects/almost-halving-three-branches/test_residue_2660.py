"""Tests for residue_2660: the affine-certificate obstruction at t=1 mod 2660."""
import unittest
from collections import Counter, deque

from residue_2660 import (
    PERIOD, BASE, CERT_2660, FRONTIER, build_system, check_pair,
    classify, make_identity, level01_obstruction, t1_witness,
    verify_certificate_2660,
)


def _bfs_profile(lengths, vertices):
    adj = {(0, 0): []}
    for arm, L in enumerate(lengths, 1):
        prev = (0, 0)
        for d in range(1, L + 1):
            v = (arm, d)
            adj.setdefault(v, [])
            adj[prev].append(v)
            adj[v].append(prev)
            prev = v
    count = Counter()
    vertex_set = list(vertices)
    index = {v: 0 for v in vertex_set}
    dists = {}
    for source in vertex_set:
        dist = {source: 0}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    queue.append(w)
        dists[source] = dist
    for i, u in enumerate(vertex_set):
        for w in vertex_set[i + 1:]:
            count[dists[u][w]] += 1
    return count


class CertificateTest(unittest.TestCase):
    def test_three_row_certificate(self):
        lines = verify_certificate_2660()
        self.assertEqual(len(lines), 3)

    def test_level01_obstructs_flagship_period(self):
        verdict, _ = level01_obstruction(PERIOD)
        self.assertEqual(verdict, 'obstructed')

    def test_level01_obstructs_all_periods(self):
        for delta in (1, 5, 19, 133, 665, 1330):
            verdict, _ = level01_obstruction(delta)
            self.assertEqual(verdict, 'obstructed', delta)

    def test_certificate_cycle_forces_zero(self):
        # The three obstruction equations, recomputed from the identity,
        # are s_a + s_b = 0, s_a + s_c = 0, s_b + s_c = 0, which force
        # a = b = c = 0 over the integers and so exclude +/-1 signs.
        varspec, rows_list = build_system(PERIOD)
        expected = {
            (2799, 178): (('T', 0, 9), ('T', 1, 0)),
            (2743, 122): (('T', 0, 9), ('B', 2, 2632)),
            (2724, 102): (('T', 1, 0), ('B', 2, 2632)),
        }
        for mon, (va, vb) in expected.items():
            cs, rhs = rows_list[mon]
            got = {(varspec[vi], c) for (vi, c) in cs}
            self.assertEqual(got, {(va, 1), (vb, 1)})
            self.assertEqual(rhs, 0)
        # The cycle argument over Z.
        for a in (1, -1):
            for b in (1, -1):
                for c in (1, -1):
                    self.assertFalse(
                        (a + b == 0 and a + c == 0 and b + c == 0),
                        f'(a,b,c)=({a},{b},{c}) should not zeroes the cycle')

    def test_identity_matches_fixed_difference(self):
        from fixed_difference_family import FAMILIES, identity_residual
        rows = FAMILIES[23]
        P = [r[0] for r in rows]
        T = [r[2] for r in rows]
        B = [r[1] for r in rows]
        mine = make_identity(56, (1, 1, 1), BASE, P, T, B,
                             holes=((0, 19), (0, 'tip')))
        self.assertEqual(mine, identity_residual(23, rows))
        self.assertEqual(mine, {})

    def test_identity_counts_profile_difference(self):
        # The identity, once substituted, is D(1-z) times twice the actual
        # profile difference (small balanced case).
        delta, es = 4, (2, 3, 2)
        P = ['+0', '+', '+']
        T = ['+-0', '--', '+-']
        bases = tuple(len(P[i]) + len(T[i]) for i in range(3))
        B = ['++--', '+-+-', '-+-+']
        from residue_2660 import _add, _scale, _mul, _monomial
        R = make_identity(delta, es, bases, P, T, B,
                          holes=((0, 2), (0, 'tip')))

        def build(k):
            return [P[i] + B[i] * (es[i] * k) + T[i] for i in range(3)]

        def brute(words):
            groups = {1: [], -1: []}
            groups[-1].append((0, 0))
            for arm, w in enumerate(words, 1):
                for d, ch in enumerate(w, 1):
                    if ch == '+':
                        groups[1].append((arm, d))
                    elif ch == '-':
                        groups[-1].append((arm, d))
            from itertools import combinations

            def prof(vs):
                return Counter(abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]
                               for u, v in combinations(vs, 2))
            pa, pb = prof(groups[1]), prof(groups[-1])
            return {d: pa[d] - pb[d] for d in sorted(set(pa) | set(pb))
                    if pa[d] != pb[d]}

        def subst(Rp, wp):
            Q = Counter()
            for (z, w), c in Rp.items():
                Q[z + w * wp] += c
            return {e: c for e, c in Q.items() if c}

        def mul(p, q):
            r = Counter()
            for e, c in p.items():
                for f, d in q.items():
                    r[e + f] += c * d
            return {e: c for e, c in r.items() if c}

        Dz = {0: 1, delta: -1}
        omz = {0: 1, 1: -1}
        for k in (0, 1):
            diff = brute(build(k))
            expected = mul(mul(Dz, omz), {d: 2 * c for d, c in diff.items()})
            self.assertEqual(subst(R, delta * k), expected, k)


class WitnessTest(unittest.TestCase):
    def test_t1_frontier_recount(self):
        witness = t1_witness()
        checked = check_pair(witness['lengths'], witness['left'],
                             witness['right'])
        self.assertTrue(checked['homometric'])
        self.assertEqual(checked['size'], 100)
        self.assertEqual(checked['pairs_per_side'], 4950)

    def test_t1_bfs_recount(self):
        witness = t1_witness()
        left = _bfs_profile((99, 79, 23), witness['left'])
        right = _bfs_profile((99, 79, 23), witness['right'])
        self.assertEqual(left, right)
        self.assertEqual(sum(left.values()), 4950)

    def test_t1_holes_and_lengths(self):
        witness = t1_witness()
        self.assertEqual(witness['holes'], [(1, 19), (1, 99)])
        self.assertEqual(witness['lengths'], [99, 79, 23])

    def test_altered_witness_is_rejected(self):
        witness = t1_witness()
        left = list(witness['left'])
        right = list(witness['right'])
        # Exchange one vertex between the sides: sizes stay equal and sets
        # stay disjoint, but the homometry breaks.
        left[0], right[0] = right[0], left[0]
        checked = check_pair(witness['lengths'], left, right)
        self.assertFalse(checked['homometric'])

    def test_classify(self):
        self.assertEqual(classify(1)['status'], 'attained')
        self.assertEqual(classify(3)['status'], 'attained (full-prefix, GAP)')
        self.assertEqual(classify(2661)['status'], 'open')
        self.assertEqual(classify(2661)['target'], 267430)
        with self.assertRaises(ValueError):
            classify(0)


if __name__ == '__main__':
    unittest.main()
