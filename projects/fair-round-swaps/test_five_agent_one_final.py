from fractions import Fraction
from itertools import combinations
import random
import unittest

from five_agent_one_final import five_path, normalize, padded_path, path, protected_path
from single_extra import greedy_witness
from swaps import allocation, states_with_sizes


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in bundle if g != deleted)
                   for deleted in [None] + bundle)
               for i, row in enumerate(u) for bundle in bundles)


def witness(u, rng, prefix=()):
    remaining = set(range(len(u[0]))) - {g for _, g in prefix}
    result = list(prefix)
    for r in range(len(u[0]) // 5):
        used = {i for i, _ in prefix} if r == 0 else set()
        for i in rng.sample([i for i in range(5) if i not in used], 5-len(used)):
            best = max(u[i][g] for g in remaining)
            g = rng.choice([g for g in sorted(remaining) if u[i][g] == best])
            result.append((i, g)); remaining.remove(g)
    result.append((0, remaining.pop()))
    return tuple(result)


class OneFinalTests(unittest.TestCase):
    def check(self, u, route, fixed=()):
        sizes = tuple(route[0].count(i) for i in range(len(u)))
        for a in route:
            self.assertTrue(fair(u, a), a)
            self.assertEqual(tuple(a.count(i) for i in range(len(u))), sizes)
            self.assertTrue(all(a[g] == i for i, g in fixed))
        for a, b in zip(route, route[1:]):
            changed = [g for g in range(len(a)) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_normalize_all_fair_states_in_fresh_profiles(self):
        rng = random.Random(23818)
        states = states_with_sizes((2, 1, 1, 1))
        self.assertEqual(len(states), 60)
        count = 0
        for _ in range(100):
            u = tuple(tuple(Fraction(rng.randrange(8), rng.randrange(1, 5)) for _ in range(5))
                      for _ in range(4))
            fair_states = [a for a in states if fair(u, a)]
            for a in fair_states:
                route = normalize(u, a)
                self.check(u, route)
                end = route[-1]
                spares = [g for g in range(5) if end[g] == 0]
                self.assertTrue(all(u[i][end.index(i)] >= max(u[i][g] for g in spares)
                                    for i in (1, 2, 3)))
                self.assertIsNotNone(greedy_witness(((0,) * 5,) + u[1:], end))
                count += 1
            self.check(u, five_path(u, fair_states[0], fair_states[-1]))
        self.assertGreater(count, 1000)

    def test_three_cycle_uses_a_fair_spare_buffer(self):
        u = ((0, 0, 0, 0, 0), (2, 3, 1, 0, 0),
             (1, 2, 3, 0, 0), (3, 1, 2, 0, 0))
        a = (1, 2, 3, 0, 0)
        route = normalize(u, a)
        self.check(u, route)
        self.assertGreaterEqual(len(route), 5)
        self.assertEqual(route[-1][3:], (0, 0))
        self.assertTrue(all(u[i][route[-1].index(i)] > u[i][a.index(i)] for i in (1, 2, 3)))

    def test_blocked_spare_transfers_force_a_mutual_improvement(self):
        u = ((0,) * 5, (2, 3, 0, 4, 1), (3, 2, 0, 1, 4), (0, 0, 5, 0, 0))
        a = (1, 2, 3, 0, 0)
        self.assertFalse(fair(u, (0, 2, 3, 1, 0)))
        self.assertFalse(fair(u, (1, 0, 3, 0, 2)))
        route = normalize(u, a)
        self.assertEqual(route[1], (2, 1, 3, 0, 0))
        self.check(u, route)

    def test_every_protected_fair_vertex_in_fresh_profiles(self):
        rng = random.Random(23819)
        states = states_with_sizes((2, 1, 1, 1, 1))
        for _ in range(35):
            rows = [[rng.randrange(8) for _ in range(6)] for _ in range(5)]
            rows[1][0] = rows[2][0] = 9
            u = tuple(tuple(row) for row in rows)
            vertices = [a for a in states if a[0] in (1, 2) and fair(u, a)]
            for a in vertices:
                route = protected_path(u, vertices[0], a)
                self.check(u, route)
                self.assertTrue(all(s[0] in (1, 2) for s in route))

    def test_padded_arbitrary_fair_tails_and_carrier_roles(self):
        rng = random.Random(23820)
        states = states_with_sizes((2, 1, 1, 1, 1))
        for rounds in range(5):
            rows = [[rng.randrange(8) for _ in range(6)] for _ in range(5)]
            rows[1][0] = rows[2][0] = 9
            small = tuple(tuple(row) for row in rows)
            vertices = [a for a in states if a[0] in (1, 2) and fair(small, a)]
            for row in rows:
                row.extend([0] * (5*rounds))
            prefix = []
            for r in range(rounds):
                for i in range(5):
                    g = 6+5*r+i; prefix.append((i, g))
                    for j in range(5):
                        rows[j][g] = 100*(rounds-r) + (50 if i == j else rng.randrange(30))
            for carriers in combinations(range(1, 5), 2):
                roles = (0, *carriers, *(i for i in range(1, 5) if i not in carriers))
                u = tuple(tuple(rows[roles.index(i)]) for i in range(5))
                pp = tuple((roles[i], g) for i, g in prefix)
                a, b = (tuple(roles[i] for i in state) for state in (vertices[0], vertices[-1]))
                route = padded_path(u, pp, tuple(range(6)), a, b, carriers)
                self.check(u, route, pp)

    def test_long_greedy_endpoints_and_exact_prefixes(self):
        rng = random.Random(23821)
        for q in (1, 2, 3, 5, 8):
            for trial in range(4):
                u = tuple(tuple(Fraction(rng.randrange(9), rng.randrange(1, 4))
                                for _ in range(5*q+1)) for _ in range(5))
                prefix = witness(u, rng)[:trial]
                a, b = witness(u, rng, prefix), witness(u, rng, prefix)
                route = path(u, a, b)
                self.assertEqual(route[0], allocation(a, len(u[0])))
                self.assertEqual(route[-1], allocation(b, len(u[0])))
                # The established one-extra base connects in the ambient graph;
                # fixed first-round prefixes are promised by the q>=2 induction.
                self.check(u, route, prefix if q >= 2 else ())

    def test_invalid_cases(self):
        with self.assertRaises(ValueError):
            normalize(((0,) * 5,) * 4, (0,) * 5)
        with self.assertRaises(ValueError):
            protected_path(((0,) * 6,) * 4, (0, 0, 1, 2, 3, 4), (0, 0, 1, 2, 3, 4))
        with self.assertRaises(ValueError):
            path(((0,) * 7,) * 5, (), ())

    def test_uncancelled_braids_for_each_singleton_pair(self):
        rng = random.Random(23822)
        for q in (2, 5, 8):
            m = 5*q+1
            for i, j in combinations(range(1, 5), 2):
                for _ in range(500):
                    rows = [rng.sample(range(m), m) for _ in range(5)]
                    rows[i][0] = rows[j][0] = m+5
                    pool = set(range(1, m)); a, b = [(i, 0)], [(j, 0)]
                    for r in range(q):
                        for h in range(5):
                            if h in (i, j):
                                continue
                            g = max(pool, key=lambda g: rows[h][g]); pool.remove(g)
                            a.append((h, g)); b.append((h, g))
                        x = max(pool, key=lambda g: rows[i][g])
                        y = max(pool, key=lambda g: rows[j][g])
                        if x == y:
                            break
                        pool -= {x, y}; a.append((j, y)); b.append((i, x))
                        if r < q-1:
                            a.append((i, x)); b.append((j, y))
                        else:
                            a.append((0, x)); b.append((0, y))
                            break
                    if len(a) == m:
                        break
                self.assertEqual(len(a), m)
                u = tuple(tuple(row) for row in rows)
                a, b = tuple(a), tuple(b)
                self.check(u, path(u, a, b))


if __name__ == '__main__':
    unittest.main()
