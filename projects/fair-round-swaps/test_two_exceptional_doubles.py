from itertools import combinations, permutations, product
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from two_exceptional_doubles import (DONOR_FAILURE, DONOR_PATH, Graph,
                                    binary_profiles, connect_two_level, favorite_singleton_path, sampled_profiles,
                                    search, separation_query, two_level_orbits, two_level_representative)


# Keep these direct oracles local; no unintegrated test helper is required.
def fair(u, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in bundle if g != removed)
                   for removed in bundle + [None])
               for i, row in enumerate(u) for bundle in bundles)


def states(r):
    labels = tuple(i for i in range(r) for _ in range(2))+(r, r+1)
    return sorted(s for s in set(permutations(labels)) if s[0] in (r, r+1))


def neighbors(state):
    for a, b in combinations(range(len(state)), 2):
        if state[a] != state[b]:
            following = list(state)
            following[a], following[b] = following[b], following[a]
            yield tuple(following)


class TwoExceptionalDoubleTests(unittest.TestCase):
    def test_a_nonfavorite_singleton_really_must_move(self):
        u = ((0,0,2,2,64,64), (0,64,0,1,2,2), (6,5,3,4,1,2), (6,3,1,4,2,5))
        a, b = (2,3,0,1,1,0), (2,3,1,0,0,1)
        allowed = {s for s in states(2) if s[0] == 2 and fair(u, s)}
        self.assertEqual({s for s in allowed if s[1] == 3}, {a, b})
        distances, queue = {a: 0}, [a]
        for state in queue:
            for following in neighbors(state):
                if following in allowed and following not in distances:
                    distances[following] = distances[state]+1
                    queue.append(following)
        self.assertEqual(len(allowed), 12)
        self.assertEqual(distances[b], 4)
        self.assertFalse(any(s in {a, b} for s in neighbors(a)))
        with self.assertRaisesRegex(ValueError, 'same favorite'):
            favorite_singleton_path(u, a, b)

    def test_attachment_can_require_a_recipient_to_lose_value(self):
        u = ((0,0,0,1,2,2), (0,1,0,0,2,2), (6,4,5,3,1,2), (6,5,2,3,4,1))
        start = (2,1,0,0,3,1)
        route = (start, (2,1,0,1,3,0), (2,3,0,1,1,0))
        self.assertTrue(all(fair(u, s) for s in route))
        self.assertTrue(all(b in neighbors(a) for a, b in zip(route, route[1:])))
        allowed = {s for s in states(2) if s[0] == 2 and fair(u, s)}
        self.assertEqual(len(allowed), 10)

        def value(s):
            return (u[3][s.index(3)],)+tuple(sum(u[i][g] for g in range(6) if s[g] == i)
                                           for i in (0, 1))

        reached, queue = {start}, [start]
        for s in queue:
            before = value(s)
            for t in neighbors(s):
                if t not in allowed or t in reached:
                    continue
                after = value(t)
                if after[0] > before[0] or (after[0] == before[0]
                        and after[1] >= before[1] and after[2] >= before[2]):
                    reached.add(t)
                    queue.append(t)
        self.assertFalse(any(s[1] == 3 for s in reached))

    def test_favorite_singleton_all_small_ternary_rows(self):
        graph = Graph(2)
        fixed = [a for a in graph.states if a[0] == 2 and a[1] == 3]
        carrier = (4, 3, 0, 1, 2, 0)
        for a in product(range(3), repeat=4):
            for b in product(range(3), repeat=4):
                u = ((0, 0)+a, (0, 0)+b, carrier, carrier)
                allowed = [state for state in fixed if fair(u, state)]
                for target in allowed:
                    route = favorite_singleton_path(u, allowed[0], target)
                    self.assertEqual((route[0], route[-1]), (allowed[0], target))
                    self.assertTrue(all(fair(u, state) for state in route))
                    self.assertTrue(all(b in neighbors(a) for a, b in zip(route, route[1:])))

    def test_favorite_singleton_compensation_and_large_real_profiles(self):
        u = ((0, 0, 1, 1, 100, 1, 0, 0), (0, 0, 1, 2, 100, 0, 10, 20),
             (1,)*8, (100, 90, 1, 2, 3, 4, 5, 6), (100, 90, 6, 5, 4, 3, 2, 1))
        start = (3, 4, 0, 0, 1, 1, 2, 2)
        target = (3, 4, 0, 2, 0, 2, 1, 1)
        direct = list(start)
        direct[4], direct[3] = direct[3], direct[4]
        self.assertFalse(fair(u, direct))
        route = favorite_singleton_path(u, start, target)
        self.assertEqual(route[:4], [start, (3,4,0,0,1,2,1,2),
                                    (3,4,0,1,0,2,1,2), (3,4,0,2,0,2,1,1)])
        # Both branches of the second recipient's strict threshold at an automatic donor.
        for row, moved, target in (
                ((0,0,10,5,0,1,1,1), 3, (3,4,0,1,0,2,1,2)),
                ((0,0,0,5,0,1,1,5), 4, (3,4,0,1,2,0,1,2))):
            profile = ((0,0,100,20,10,1,1,2), row)+u[2:]
            start = (3,4,2,0,0,1,1,2)
            route = favorite_singleton_path(profile, start, target)
            self.assertEqual([g for g in range(8) if route[0][g] != route[1][g]], [2, moved])
            self.assertTrue(all(fair(profile, a) for a in route))
        rng = random.Random(2026112063)
        for r in (3, 4, 7, 15):
            m = 2*r+2
            for trial in range(8):
                special = tuple((0, 0)+tuple(Fraction(rng.randrange(40), 7)
                                             for _ in range(2*r)) for _ in range(2))
                carrier = (100, 99)+tuple(rng.randrange(90) for _ in range(2*r))
                u = special+((0,)+(1,)*(m-1),)*(r-2)+(carrier, carrier)
                if r == 3:
                    allowed = [a for a in Graph(r).states
                               if a[0] == r and a[1] == r+1 and fair(u, a)]
                    pairs = [(allowed[0], a) for a in allowed]
                else:
                    goods = list(range(2, m))
                    w = max(goods, key=lambda g: u[0][g])
                    goods.remove(w)
                    z = max(goods, key=lambda g: u[1][g])
                    goods.remove(z)
                    state = [r, r+1]+[-1]*(m-2)
                    state[w], state[z] = 0, 1
                    for g, agent in zip(goods, [0, 1]+[i for i in range(2, r) for _ in range(2)]):
                        state[g] = agent
                    start = tuple(state)
                    for _ in range(200):
                        a, b = rng.sample(range(2, m), 2)
                        state[a], state[b] = state[b], state[a]
                        if not fair(u, state):
                            state[a], state[b] = state[b], state[a]
                    pairs = [(start, tuple(state))]
                for start, target in pairs:
                    route = favorite_singleton_path(u, start, target)
                    self.assertLessEqual(len(route)-1, 2*r+3)
                    self.assertTrue(all(fair(u, a) and a[0] == r and a[1] == r+1 for a in route))
                    self.assertTrue(all(b in neighbors(a) for a, b in zip(route, route[1:])))
        with self.assertRaisesRegex(ValueError, 'same favorite'):
            favorite_singleton_path(DONOR_FAILURE, DONOR_PATH[0], DONOR_PATH[-1])

    def test_complete_column_orbits_and_small_graphs(self):
        six = tuple(two_level_orbits(2))
        self.assertEqual(len(six), 15504)
        self.assertEqual(len(set(six)), 15504)
        self.assertEqual(sum(1 for _ in two_level_orbits(3)), 170544)
        result = search(Graph(2), six, fixed_owners=True)
        self.assertEqual((result['checked'], result['separated']), (15504, False))
        self.assertFalse(result['fixed_owner_separated'])
        rng = random.Random(2026112061)
        orbit_set = set(six)
        for _ in range(200):
            rows = tuple(tuple(rng.randrange(2) for _ in range(5)) for _ in range(4))
            order = sorted(range(5), key=lambda g: sum(rows[i][g] << i for i in range(4)))
            canonical = tuple((int(i >= 2),)+tuple(rows[i][g] for g in order) for i in range(4))
            self.assertIn(canonical, orbit_set)

    def test_full_cut_export_uses_the_whole_graph(self):
        text = separation_query()
        self.assertEqual(text.count('() Real)'), 32)
        self.assertEqual(text.count('() Bool)'), 2520)
        self.assertEqual(text.count('(assert (=>'), 11970)
        self.assertEqual(text.count('(check-sat)'), 1)
        bounded = separation_query(bounded_integers=True)
        self.assertEqual(bounded.count('() Int)'), 32)
        self.assertEqual(bounded.count(' 256))'), 32)
        self.assertNotIn('() Real)', bounded)
        attached = separation_query(favorite_attachment=True)
        self.assertEqual(attached.count('() Bool)'), 1260)
        self.assertEqual(attached.count('(assert (=> (and'), 5670)
        self.assertEqual(attached.count('(assert (=> f'), 0)
        self.assertEqual(attached.count('(assert (<= (+'), 4)
        self.assertIn('(assert (>= u4_1 u4_7))', attached)
        self.assertIn('(assert (>= u0_2 u0_7))', attached)
        self.assertIn('(assert (>= u1_4 u1_7))', attached)
        self.assertNotIn('(assert (>= u1_4 u1_2))', attached)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'cut.smt2'
            run = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name(
                'two_exceptional_doubles.py')), '--write-separation-query', str(path)],
                check=True, capture_output=True, text=True)
            self.assertEqual(path.read_text(), text)
            self.assertIn('unverified', json.loads(run.stdout)['scope'])

    def test_two_level_cardinalities_and_constructor(self):
        rng = random.Random(2026112062)
        for r in (2, 3):
            graph = Graph(r)
            for trial in range(8):
                binary = next(sampled_profiles(r, trial, 1, 2))
                u = []
                for i, row in enumerate(binary):
                    low = Fraction(rng.randrange(3), 3)
                    high = 2*low if trial % 2 and low else low+2
                    u.append((high+1 if i >= r else 100,)+tuple(high if x else low for x in row[1:]))
                if r == 3:
                    u[2] = (100,)+(Fraction(7, 5),)*(graph.m-1)
                u = tuple(u)
                converted = two_level_representative(u)
                expected = sum(1 << k for k, state in enumerate(graph.states) if fair(u, state))
                self.assertEqual(graph.fair_mask(converted), expected)
                allowed = [a for k, a in enumerate(graph.states) if expected & (1 << k)]
                route = connect_two_level(u, allowed[0], allowed[-1])
                self.assertTrue(all(fair(u, a) for a in route))
                self.assertTrue(all(b in neighbors(a) for a, b in zip(route, route[1:])))
                same = [a for a in allowed if a[0] == allowed[0][0]]
                self.assertTrue(all(a[0] == same[0][0] for a in connect_two_level(u, same[0], same[-1])))
        boundary = ((0, 1, 1, 2, 2, 2), (0, 1, 1, 1, 1, 1),
                    (10, 1, 1, 1, 1, 1), (10, 1, 1, 1, 1, 1))
        state = (2, 0, 0, 1, 1, 3)
        self.assertTrue(fair(boundary, state))
        self.assertEqual(two_level_representative(boundary)[0], (0,)*6)
        naive = ((0, 0, 0, 1, 1, 1),)+boundary[1:]
        self.assertFalse(fair(naive, state))
        with self.assertRaisesRegex(ValueError, 'two non-g values'):
            two_level_representative(DONOR_FAILURE)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'two-level.json'
            path.write_text(json.dumps([[str(v) for v in row] for row in u]))
            run = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name(
                'two_exceptional_doubles.py')), '--two-level-input', str(path),
                '--start', ','.join(map(str, allowed[0])), '--target', ','.join(map(str, allowed[-1]))],
                check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(run.stdout)['complete_graph']['component_sizes'], [len(allowed)])

    def test_complete_state_and_edge_generation(self):
        for r, count, degree in ((2, 60, 9), (3, 1260, 19)):
            graph = Graph(r)
            self.assertEqual(set(graph.states), set(states(r)))
            self.assertEqual(len(graph.states), count)
            for index, state in enumerate(graph.states):
                expected = set()
                for other in graph.states:
                    changed = [g for g in range(graph.m) if state[g] != other[g]]
                    if len(changed) == 2:
                        a, b = changed
                        if state[a] == other[b] and state[b] == other[a]:
                            expected.add(graph.index[other])
                actual = {k for k in range(count) if graph.adjacency[index] & (1 << k)}
                self.assertEqual(actual, expected)
                self.assertEqual(len(actual), degree)

    def test_masks_match_literal_deletions(self):
        for r in (2, 3):
            graph = Graph(r)
            profiles = list(sampled_profiles(r, 851+r, 25, 4))
            profiles += list(sampled_profiles(r, 452+r, 25, 4, True))
            for u in profiles:
                got = graph.fair_mask(u)
                expected = sum(1 << k for k, state in enumerate(graph.states) if fair(u, state))
                self.assertEqual(got, expected)

    def test_every_binary_observer_row_and_distinct_fair_graph(self):
        for r in (2, 3):
            graph = Graph(r)
            for observer in (0, 1, r, r+1):
                for bits in product((0, 1), repeat=2*r+1):
                    row = (int(observer >= r),)+bits
                    expected = 0
                    for k, state in enumerate(graph.states):
                        own = sum(row[g] for g, owner in enumerate(state) if owner == observer)
                        bundles = [[g for g, owner in enumerate(state) if owner == j]
                                   for j in range(r+2)]
                        if all(any(own >= sum(row[g] for g in bundle if g != removed)
                                   for removed in bundle + [None]) for bundle in bundles):
                            expected |= 1 << k
                    self.assertEqual(graph.observer_mask(observer, row), expected)
        graph = Graph(2)
        masks = {graph.fair_mask(u) for u in binary_profiles()}
        for mask in masks:
            fair_states = {s for k, s in enumerate(graph.states) if mask & (1 << k)}
            reached, queue = {min(fair_states)}, [min(fair_states)]
            for state in queue:
                for other in neighbors(state):
                    if other in fair_states and other not in reached:
                        reached.add(other)
                        queue.append(other)
            self.assertEqual(reached, fair_states)

    def test_component_negative_control_and_connected_control(self):
        graph = Graph(2)
        uniform = ((1,)*6,)*4
        mask = graph.fair_mask(uniform)
        self.assertEqual(graph.components(mask), (mask,))
        # This is a graph-algorithm control, not a claimed valuation example.
        a, b = next((a, b) for a, b in combinations(range(60), 2)
                    if not graph.adjacency[a] & (1 << b))
        groups = graph.components((1 << a) | (1 << b))
        self.assertEqual(len(groups), 2)
        self.assertEqual(sorted(x.bit_count() for x in groups), [1, 1])

    def test_both_direct_acquisitions_fail_but_a_short_repair_exists(self):
        u, start = DONOR_FAILURE, DONOR_PATH[0]
        self.assertTrue(all(fair(u, s) for s in DONOR_PATH))
        for a, b in zip(DONOR_PATH, DONOR_PATH[1:]):
            changed = [g for g in range(6) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))
        for other in (2, 3):
            attempted = list(start)
            attempted[1], attempted[other] = attempted[other], attempted[1]
            self.assertFalse(fair(u, tuple(attempted)))
        self.assertEqual(Graph(2).certificate(u), {
            'all_states': 60, 'fair_states': 36, 'component_sizes': [36]})

    def test_reproducibility_and_complete_binary_domain(self):
        self.assertEqual(list(sampled_profiles(3, 7, 10, 4)),
                         list(sampled_profiles(3, 7, 10, 4)))
        result = search(Graph(2), binary_profiles())
        self.assertEqual(result['checked'], 40960)
        self.assertFalse(result['separated'])
        self.assertEqual(result['largest_fair_graph'], 54)
        for u in sampled_profiles(3, 9, 10, 4, True):
            self.assertTrue(all(v in (0, 1, 2, 8, 64) for row in u[:2] for v in row))
            self.assertTrue(all(len(set(row[1:])) == 7 for row in u[-2:]))

    def test_scope_boundaries_and_actual_command(self):
        with self.assertRaises(ValueError):
            Graph(4)
        graph = Graph(3)
        u = list(next(sampled_profiles(3, 1, 1, 4)))
        u[2] = (0, 0, 0, 0, 0, 0, 1, 1)
        with self.assertRaisesRegex(ValueError, 'automatically fair'):
            graph.fair_mask(tuple(u))
        with self.assertRaises(ValueError):
            graph.fair_mask(((1,)*6,)*4)
        with self.assertRaises(ValueError):
            list(sampled_profiles(2, 1, -1, 4))
        with self.assertRaises(ValueError):
            next(binary_profiles(3, 6))
        eight = next(binary_profiles(3, 2))
        self.assertEqual(tuple(map(len, eight)), (8,)*5)
        self.assertEqual(sum(eight[0]), 2)
        self.assertEqual(len(Graph(3).components(Graph(3).fair_mask(eight))), 1)
        run = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name(
            'two_exceptional_doubles.py')), '--binary'], capture_output=True,
            text=True, check=True)
        self.assertEqual(json.loads(run.stdout)['checked'], 40960)

    def test_three_exceptional_boundary_is_outside_this_domain(self):
        # Fern's earlier eight-good isolated state, reconstructed here only
        # as a domain-boundary control, not a new endpoint counterexample.
        base = ((1,0,2,0,0,2,2,2), (2,0,1,0,2,0,2,2),
                (0,0,0,1,0,0,1,1), (0,2,2,0,2,0,1,3),
                (2,2,2,0,2,0,0,3))
        u = tuple(tuple(20*v+g+1 for g, v in enumerate(row)) for row in base)
        isolated = (0,0,1,1,2,2,3,4)
        other = (1,2,1,2,3,0,0,4)
        self.assertTrue(fair(u, isolated) and fair(u, other))
        self.assertTrue(all(row[7] == max(row) for row in u[-2:]))
        candidates = list(neighbors(isolated))
        self.assertEqual(len(candidates), 25)
        self.assertFalse(any(fair(u, state) for state in candidates))
        # Relabel its common favorite as zero for this checker's convention.
        order = (7,1,2,3,4,5,6,0)
        shifted = tuple(tuple(row[g] for g in order) for row in u)
        with self.assertRaisesRegex(ValueError, 'automatically fair'):
            Graph(3).fair_mask(shifted)


if __name__ == '__main__':
    unittest.main()
