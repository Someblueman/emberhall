"""Independent deletion checks for the all-remainder endpoint constructor."""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from arbitrary_few_final import _construct, _free_base, braid_example, path
from swaps import allocation, rounds_for


def fair(u, state):
    for i, row in enumerate(u):
        own = sum(row[g] for g, owner in enumerate(state) if owner == i)
        for j in range(len(u)):
            bundle = [g for g, owner in enumerate(state) if owner == j]
            if bundle and not any(own >= sum(row[h] for h in bundle if h != removed)
                                  for removed in bundle):
                return False
    return True


def witness(u, final, rng, prefix=()):
    n, m = len(u), len(u[0])
    result, pool = list(prefix), set(range(m)) - {g for _, g in prefix}
    for t, eligible in enumerate(rounds_for(n, m, final)):
        order = [i for i in eligible if t > 0 or i not in {j for j, _ in prefix}]
        rng.shuffle(order)
        for i in order:
            best = max(u[i][h] for h in pool)
            g = rng.choice(sorted(h for h in pool if u[i][h] == best))
            result.append((i, g))
            pool.remove(g)
    return tuple(result)


class FewFinalTests(unittest.TestCase):
    def check_route(self, u, a, b, final, route, fixed=()):
        n, m = len(u), len(u[0])
        self.assertEqual(route[0], allocation(a, m))
        self.assertEqual(route[-1], allocation(b, m))
        sizes = tuple(m//n + (i in final) for i in range(n))
        for state in route:
            self.assertEqual(tuple(state.count(i) for i in range(n)), sizes)
            self.assertTrue(fair(u, state), state)
            self.assertTrue(all(state[g] == i for i, g in fixed))
        for aa, bb in zip(route, route[1:]):
            changed = [g for g in range(m) if aa[g] != bb[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((aa[x], aa[y]), (bb[y], bb[x]))

    def test_uncancelled_braids_and_spectators(self):
        cases = 0
        for r in (2, 3, 4):
            for n in (r+2, r+3, 8, 12):
                for q in (2, 3, 7):
                    u, a, b, final = braid_example(n, q, r)
                    route = path(u, a, b, final)
                    self.check_route(u, a, b, final, route)
                    self.assertTrue(all(state[0] in (n-2, n-1) for state in route))
                    # All earlier common non-g goods and all last-round extra
                    # singleton picks must stay with their original owners.
                    changed = {g for aa, bb in zip(route, route[1:])
                               for g in range(len(aa)) if aa[g] != bb[g]}
                    last_goods = {g for _, g in a[(q-1)*n:]}
                    self.assertTrue(changed <= last_goods | {0})
                    for i, g in a[(q-1)*n:q*n]:
                        if i not in final and i not in (n-2, n-1):
                            self.assertTrue(all(state[g] == i for state in route))
                    cases += 1
        self.assertEqual(cases, 36)

    def test_rational_profiles_labels_and_near_complete_boundary(self):
        rng = random.Random(2026112071)
        cases = 0
        for r in (2, 3, 4):
            for n in (r+1, r+2, r+4, 9):
                for q in (1, 2, 3):
                    for trial in range(3):
                        m = n*q+r
                        u = tuple(tuple(Fraction(rng.randrange(8), rng.choice((1, 3, 11)))
                                        if trial else 0 for _ in range(m)) for _ in range(n))
                        final = tuple(rng.sample(range(n), r))
                        a, b = witness(u, final, rng), witness(u, final, rng)
                        self.check_route(u, a, b, final, path(u, a, b, final))
                        cases += 1
        self.assertEqual(cases, 108)

    def test_fixed_first_prefixes_and_complete_rounds(self):
        for r in (2, 3, 4):
            n = 8
            u, a, b, final = braid_example(n, 4, r)
            for length in (1, 3, n-2):
                common = a[1:1+length]
                aa = common + a[:1] + a[1+length:]
                bb = common + b[:1] + b[1+length:]
                route = path(u, aa, bb, final)
                self.check_route(u, aa, bb, final, route, common)
            # Add two strictly dominant common rounds, preserving all their
            # labelled goods when the outer induction calls the residual path.
            m = len(u[0])
            padded = [list(row) + [0]*(2*n) for row in u]
            prefix = tuple((i, m+t*n+i) for t in range(2) for i in range(n))
            for t in range(2):
                for i in range(n):
                    padded[i][m+t*n+i] = 1000*(2-t)
            padded = tuple(map(tuple, padded))
            aa, bb = prefix + a, prefix + b
            self.check_route(padded, aa, bb, final, path(padded, aa, bb, final), prefix)

    def test_carrier_final_absorption_and_last_picker_tie(self):
        for r in (2, 3, 4):
            for carriers in ((0, 5), (5, 0), (0, 1)):
                u, a, b, final = braid_example(6, 4, r, carriers)
                route = path(u, a, b, final)
                self.check_route(u, a, b, final, route)
                self.assertEqual(len(route), 2)
            n, m, final = 6, 12+r, tuple(range(r))
            u = ((0,)*m,)*n
            a = tuple(zip(tuple(range(n))*2 + final, range(m)))
            b = list(a)
            b[n-1], b[n] = (n-1, n), (0, n-1)
            b = tuple(b)
            self.check_route(u, a, b, final, path(u, a, b, final), a[:n-1])

    def test_free_final_base_and_label_equivariance(self):
        rng = random.Random(2026112072)
        for r in (2, 3, 4):
            n, m = r+3, 2*r+3
            u = tuple(tuple(rng.randrange(5) for _ in range(m)) for _ in range(n))
            final = tuple(range(r))
            a, b = witness(u, final, rng), witness(u, final, rng)
            # Deliberately free final assignments; only the complete rounds
            # must remain greedy at this internal induction boundary.
            aa = a[:n] + tuple((i, g) for i, (_, g) in zip(final, reversed(a[n:])))
            bb = b[:n] + tuple((i, g) for i, (_, g) in zip(final, reversed(b[n:])))
            self.check_route(u, aa, bb, final, _free_base(u, aa, bb, r))
            u, a, b, final = braid_example(n, 3, r)
            agents, goods = list(range(n)), list(range(len(u[0])))
            rng.shuffle(agents)
            rng.shuffle(goods)
            changed_u = [[0]*len(goods) for _ in agents]
            for i, row in enumerate(u):
                for g, value in enumerate(row):
                    changed_u[agents[i]][goods[g]] = value
            changed_u = tuple(map(tuple, changed_u))
            aa, bb = (tuple((agents[i], goods[g]) for i, g in w) for w in (a, b))
            ff = tuple(agents[i] for i in reversed(final))
            self.check_route(changed_u, aa, bb, ff, path(changed_u, aa, bb, ff))

    def test_nontrivial_four_core_inside_earlier_rounds(self):
        from one_anchor_certificate import example
        from swaps import validate_witness
        core = [list(row) for row in example(4, 41)]
        for i in range(4):
            for g in range(1, 5):
                core[i][g] = 100-g
        for n, q in ((6, 2), (7, 3), (9, 4)):
            u, a, b, final = braid_example(n, q, 4)
            changed = [list(row) for row in u]
            left = dict(a[(q-1)*n:q*n])
            right = dict(b[(q-1)*n:q*n])
            goods = ((0,) + tuple(left[i] for i in final)
                     + (right[n-2], left[n-1]) + tuple(range(n*q+1, n*q+4)))
            for i, owner in enumerate(final + (n-2, n-1)):
                for g, h in enumerate(goods):
                    changed[owner][h] = core[i][g]
            for owner in (n-2, n-1):
                changed[owner][0] = u[owner][0]
            u = tuple(map(tuple, changed))
            greedy = []
            for w in (a, b):
                prefix = list(w[:n*q])
                pool = set(range(n*q+4)) - {g for _, g in prefix}
                for owner in final:
                    g = max(sorted(pool), key=lambda h: u[owner][h])
                    prefix.append((owner, g))
                    pool.remove(g)
                greedy.append(tuple(prefix))
            for w in greedy:
                validate_witness(u, rounds_for(n, n*q+4, final), w)
            route = path(u, *greedy, final)
            fixed = tuple((i, h) for i, h in a if h not in goods)
            self.check_route(u, *greedy, final, route)
            # Only the prescribed common-prefix lift freezes these goods.
            # Connecting arbitrary greedy endpoints may use other fair moves.
            lifted = _construct(u, a, b, 4)
            self.check_route(u, a, b, final, lifted, fixed)
            self.assertGreater(len(lifted)-1, 2)
            self.assertTrue(all(state[0] in (n-2, n-1) for state in route))
            self.assertGreater(len(route)-1, 2)
            # The original favorite is below earlier goods for double owners;
            # the lift must not silently assume it is everyone's top good.
            self.assertTrue(any(u[i][g] > u[i][0] for i, g in a[:n] if i in final))

    def test_bad_inputs_and_actual_command(self):
        u, a, b, final = braid_example(6, 2, 3)
        for ff in ((0,), (0, 0, 1), (0, 1, 9), (False, 1, 2), (0, 1, 2, 3, 4)):
            with self.assertRaises(ValueError):
                path(u, a, b, ff)
        with self.assertRaises(ValueError):
            path(u, a[:-1], b, final)
        bad = ((a[0][0], a[1][1]),) + a[1:]
        with self.assertRaises(ValueError):
            path(u, bad, b, final)
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('arbitrary_few_final.py')),
                                 '--agents', '7', '--rounds', '4', '--final', '4'],
                                check=True, capture_output=True, text=True)
        output = json.loads(result.stdout)
        self.assertEqual((output['agents'], output['goods']), (7, 32))
        self.assertGreater(output['exchanges'], 0)
        u, a, b, final = braid_example(7, 4, 4)
        self.check_route(u, a, b, final, [tuple(s) for s in output['path']])

    def test_all_remainders_and_no_complete_round(self):
        rng = random.Random(2026112089)
        for n in range(2, 8):
            for q in range(4):
                for r in range(n):
                    if n*q+r == 0:
                        continue
                    for tied in (True, False):
                        m = n*q+r
                        u = tuple(tuple(0 if tied else Fraction(rng.randrange(8), 3)
                                        for _ in range(m)) for _ in range(n))
                        final = tuple(rng.sample(range(n), r))
                        a, b = witness(u, final, rng), witness(u, final, rng)
                        self.check_route(u, a, b, final, path(u, a, b, final))

    def test_forced_large_remainders_and_complete_round_braids(self):
        for n, r in ((2, 0), (3, 1), (7, 5), (10, 8), (10, 9)):
            for q in (1, 2, 5):
                u, a, b, final = braid_example(n, q, r)
                route = path(u, a, b, final)
                self.check_route(u, a, b, final, route)
        n = 9
        u, a, b, final = braid_example(n, 4, 6)
        for length in (1, 4, n-2):
            prefix = a[1:1+length]
            aa = prefix+a[:1]+a[1+length:]
            bb = prefix+b[:1]+b[1+length:]
            self.check_route(u, aa, bb, final, path(u, aa, bb, final), prefix)


if __name__ == '__main__':
    unittest.main()
