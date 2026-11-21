"""Exhaustive small matching checks and independent EF1 path checks."""

from dataclasses import replace
from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from common_crossing import Crossing
from tail_matchings import crossing_paths, example, reconfigure, three_observer_boundary


def fair(u, state):
    for i, row in enumerate(u):
        own = sum(row[g] for g, owner in enumerate(state) if owner == i)
        for j in range(len(u)):
            goods = [g for g, owner in enumerate(state) if owner == j]
            if goods and not any(own >= sum(row[g] for g in goods if g != removed)
                                 for removed in goods):
                return False
    return True


class TailMatchingTests(unittest.TestCase):
    def test_all_two_set_patterns_and_matchings_through_four_pairs(self):
        total = 0
        for r in range(1, 5):
            choices = tuple(permutations(range(r)))
            for masks in product(range(4), repeat=2*r):
                anchors, tails = masks[:r], dict(enumerate(masks[r:]))
                legal = [p for p in choices if all(not anchors[k] & tails[g]
                                                  for k, g in enumerate(p))]
                if not legal:
                    continue
                for start in legal:
                    route = reconfigure(anchors, tails, start, legal[0])
                    self.assertEqual((route[0], route[-1]), (start, legal[0]))
                    inverse = {g: k for k, g in enumerate(start)}
                    seen, cycles = set(), 0
                    for k in range(r):
                        if k in seen:
                            continue
                        cycles += 1
                        while k not in seen:
                            seen.add(k)
                            k = inverse[legal[0][k]]
                    self.assertEqual(len(route)-1, r-cycles)
                    for state in route:
                        self.assertEqual(set(state), set(range(r)))
                        self.assertTrue(all(not anchors[k] & tails[g] for k, g in enumerate(state)))
                    for a, b in zip(route, route[1:]):
                        changed = [k for k in range(r) if a[k] != b[k]]
                        self.assertEqual(len(changed), 2)
                        x, y = changed
                        self.assertEqual((a[x], a[y]), (b[y], b[x]))
                    total += 1
        # For each permutation there are nine allowed anchor/tail mask pairs.
        self.assertEqual(total, 9 + 2*9**2 + 6*9**3 + 24*9**4)

    def check_sides(self, u, source, routes, shared, carriers):
        for side, route in enumerate(routes):
            self.assertEqual(route[0], source.sides[side])
            for state in route:
                self.assertTrue(fair(u, state))
                self.assertEqual(state[shared], carriers[side])
                self.assertEqual(state[source.pivot], carriers[1-side])
                self.assertTrue(all(state[g] == i for i, g in source.anchors))
                self.assertEqual(tuple(state.count(i) for i in range(len(u))),
                                 tuple(1 if i in carriers else 2 for i in range(len(u))))
            for a, b in zip(route, route[1:]):
                changed = [g for g in range(len(a)) if a[g] != b[g]]
                self.assertEqual(len(changed), 2)
                x, y = changed
                self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_overlapping_sets_rationals_and_arbitrary_labels(self):
        rng = random.Random(2026112043)
        overlap = 0
        for r in (1, 2, 3, 4, 8, 15):
            for _ in range(20):
                n, m = r+2, 2*r+2
                am = tuple(rng.randrange(4) for _ in range(r))
                tm = tuple(rng.choice([v for v in range(4) if not v & a]) for a in am)
                overlap += 3 in am or 3 in tm
                u = [[0]*m for _ in range(n)]
                for i in range(r):
                    u[i][i+2] = 10
                for bit, i in enumerate((r, r+1)):
                    u[i][0], u[i][1] = 5, 1
                    for g, mask in enumerate(am+tm, 2):
                        u[i][g] = 2 if mask & (1 << bit) else rng.choice((0, 1))
                current = list(range(r))
                for _ in range(50):
                    a, b = rng.randrange(r), rng.randrange(r)
                    if not am[a] & tm[current[b]] and not am[b] & tm[current[a]]:
                        current[a], current[b] = current[b], current[a]
                agents, goods = list(range(n)), list(range(m))
                rng.shuffle(agents)
                rng.shuffle(goods)
                values = [[0]*m for _ in range(n)]
                for i in range(n):
                    for g in range(m):
                        values[agents[i]][goods[g]] = Fraction(u[i][g], 3)
                values = tuple(map(tuple, values))
                anchors = tuple((agents[i], goods[2+i]) for i in range(r))
                tails = tuple((agents[i], goods[2+r+i]) for i in range(r))
                target = tuple((agents[i], goods[2+r+current[i]]) for i in range(r))
                state = [-1]*m
                for i, g in anchors+tails:
                    state[g] = i
                carriers = (agents[r], agents[r+1])
                state[goods[0]], state[goods[1]] = carriers
                left = tuple(state)
                state[goods[0]], state[goods[1]] = reversed(carriers)
                source = Crossing(goods[1], anchors, tails, (left, tuple(state)))
                routes = crossing_paths(values, goods[0], carriers, source, tuple(reversed(target)))
                self.check_sides(values, source, routes, goods[0], carriers)
                self.assertTrue(all(routes[0][-1][g] == i for i, g in target))
        self.assertGreater(overlap, 0)

    def test_blocked_direct_swap_and_two_swap_repair(self):
        u, source, target = example()
        routes = crossing_paths(u, 0, (3, 4), source, target)
        self.check_sides(u, source, routes, 0, (3, 4))
        self.assertEqual(len(routes[0])-1, 2)
        wrong = list(source.sides[0])
        wrong[6], wrong[7] = wrong[7], wrong[6]
        self.assertFalse(fair(u, wrong))
        self.assertEqual(reconfigure((1, 2, 0), {5: 1, 6: 2, 7: 0},
                                     (6, 7, 5), (7, 5, 6)),
                         [(6, 7, 5), (6, 5, 7), (7, 5, 6)])
        # Choosing the first available helper would disturb the already
        # correct position 0 and use four swaps. A helper inside the relative
        # cycle leaves it fixed and achieves the two-swap lower bound.
        route = reconfigure((0, 0, 1, 2), {0: 0, 1: 2, 2: 0, 3: 0},
                            (0, 3, 1, 2), (0, 1, 2, 3))
        self.assertEqual(len(route)-1, 2)
        self.assertTrue(all(state[0] == 0 for state in route))

    def test_invalid_endpoints_and_false_anchor_certificate(self):
        for args in [((1,), {4: 1}, (4,), (4,)),
                     ((4,), {4: 0}, (4,), (4,)),
                     ((0, 0), {4: 0}, (4, 4), (4, 4)),
                     ((0,), {4: 0}, (4,), (5,)),
                     ((False,), {4: 0}, (4,), (4,))]:
            with self.assertRaises(ValueError):
                reconfigure(*args)
        u, source, target = example()
        with self.assertRaises(ValueError):
            crossing_paths(u, 0, (3, 4), source, ((0, 5), (1, 7), (2, 6)))
        with self.assertRaises(ValueError):
            crossing_paths(u, 0, (3, 4), replace(source, sides=tuple(reversed(source.sides))), target)
        bad = [list(row) for row in u]
        bad[0][5] = 11
        with self.assertRaisesRegex(ValueError, 'dominating'):
            crossing_paths(tuple(map(tuple, bad)), 0, (3, 4), source, target)
        # The combinatorial API also supports nonconsecutive integer labels.
        self.assertEqual(reconfigure((0, 0), {-8: 0, 42: 3}, (-8, 42), (42, -8)),
                         [(-8, 42), (42, -8)])

    def test_actual_command(self):
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('tail_matchings.py'))],
                             check=True, capture_output=True, text=True)
        data = json.loads(run.stdout)
        self.assertEqual(data['exchanges_on_each_side'], 2)
        u, source, _ = example()
        routes = tuple([tuple(s) for s in data[key]] for key in ('left_path', 'right_path'))
        self.check_sides(u, source, routes, 0, (3, 4))

    def test_three_observers_disconnect_only_the_fixed_tail_slice(self):
        u, start, target = three_observer_boundary()
        allowed = []
        for tails in permutations((3, 4, 5)):
            state = list(range(3)) + [-1]*3 + [3, 4, 5]
            for owner, good in enumerate(tails):
                state[good] = owner
            if fair(u, state):
                allowed.append(tuple(state))
        self.assertEqual(set(allowed), {start, target})
        self.assertEqual(sum(a != b for a, b in zip(start, target)), 3)
        for a, b in ((3, 4), (3, 5), (4, 5)):
            state = list(start)
            state[a], state[b] = state[b], state[a]
            self.assertFalse(fair(u, state))


if __name__ == '__main__':
    unittest.main()
