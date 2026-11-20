from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from four_double_boundary import ESCAPE_MOVES, FullGraph, escape_cover, fair_neighbor, profiles, search
from two_exceptional_doubles import Graph


def literal_fair(u, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in target if g != deleted)
                   for deleted in target+[None])
               for i, row in enumerate(u) for target in bundles)


def literal_neighbors(state):
    r = max(state)-1
    for a, b in combinations(range(len(state)), 2):
        if state[a] == state[b]:
            continue
        other = list(state)
        other[a], other[b] = other[b], other[a]
        if other[0] in (r, r+1):
            yield tuple(other)


class FourDoubleBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.large = FullGraph(4)

    def test_complete_smaller_graphs_match_permutations_and_original_checker(self):
        for r in (2, 3):
            graph, prior = FullGraph(r), Graph(r)
            labels = tuple(i for i in range(r) for _ in range(2))+(r, r+1)
            all_states = {a for a in permutations(labels) if a[0] in (r, r+1)}
            self.assertEqual(set(graph.states), all_states)
            self.assertEqual(graph.states, prior.states)
            for k, state in enumerate(graph.states):
                got = {graph.states[j] for j in graph.adjacency[k]}
                self.assertEqual(got, set(literal_neighbors(state)))
                self.assertEqual(set(graph.adjacency[k]),
                                 {j for j in range(len(prior.states)) if prior.adjacency[k] >> j & 1})
            for u in profiles(r, 2026112075, 9):
                expected = {k for k, state in enumerate(graph.states) if literal_fair(u, state)}
                self.assertEqual(graph.fair_vertices(u), expected)
                self.assertEqual(expected, {k for k in range(len(graph.states))
                                            if prior.fair_mask(u) >> k & 1})

    def test_four_double_graph_and_literal_rational_fairness(self):
        graph = self.large
        self.assertEqual(len(graph.states), 45360)
        self.assertTrue(all(len(a) == len(set(a)) == 33 for a in graph.adjacency))
        self.assertEqual(sum(map(len, graph.adjacency))//2, 748440)
        rng = random.Random(2026112076)
        for k in rng.sample(range(len(graph.states)), 200):
            self.assertEqual({graph.states[j] for j in graph.adjacency[k]},
                             set(literal_neighbors(graph.states[k])))
        for raw in profiles(4, 2026112077, 6):
            u = tuple(tuple(Fraction(v, 7) for v in row) for row in raw)
            fair = graph.fair_vertices(u)
            for k in rng.sample(range(len(graph.states)), 200):
                self.assertEqual(k in fair, literal_fair(u, graph.states[k]))
        uniform = ((1,)*10,)*6
        result = graph.certificate(uniform)
        self.assertEqual(result, {'fair_states': 45360, 'components': [45360],
                                  'owner_components': [[22680], [22680]]})

    def test_components_detect_a_real_boundary_and_negative_control(self):
        graph = FullGraph(2)
        a, b = next((a, b) for a, b in combinations(range(60), 2)
                    if b not in graph.adjacency[a])
        self.assertEqual(sorted(map(len, graph.components({a, b}))), [1, 1])
        u = ((0,0,2,2,64,64), (0,64,0,1,2,2), (6,5,3,4,1,2), (6,3,1,4,2,5))
        fixed = {k for k in graph.fair_vertices(u) if graph.states[k][0:2] == (2, 3)}
        self.assertEqual(sorted(map(len, graph.components(fixed))), [1, 1])

    def test_seeded_search_and_invalid_boundaries(self):
        graph = FullGraph(2)
        self.assertEqual(list(profiles(4, 9, 6)), list(profiles(4, 9, 6)))
        result = search(graph, 12, 12, 60)
        self.assertEqual((result['checked'], result['full_separations']), (12, 0))
        self.assertEqual(result['stop'], 'all requested profiles')
        for seconds in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                search(graph, 0, 1, seconds)
        with self.assertRaises(ValueError):
            list(profiles(4, 0, -1))
        with self.assertRaises(ValueError):
            FullGraph(5)
        wrong = list(next(profiles(4, 0, 1)))
        wrong[2] = (0,0,0,0,0,0,0,1,1,1)
        with self.assertRaisesRegex(ValueError, 'automatically fair'):
            self.large.fair_vertices(tuple(wrong))
        with self.assertRaises(ValueError):
            graph.fair_vertices(((1,)*10,)*6)

    def test_real_command(self):
        run = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name(
            'four_double_boundary.py')), '--samples', '1', '--seconds', '60'],
            check=True, text=True, capture_output=True)
        result = json.loads(run.stdout)
        self.assertEqual((result['all_states'], result['degree'], result['checked']), (45360, 33, 1))
        self.assertEqual(result['full_separations'], 0)
        self.assertIn('only completed sampled', result['scope'])
        run = subprocess.run([sys.executable, '-S', str(Path(__file__).with_name(
            'four_double_boundary.py')), '--escape-cover'], check=True, text=True, capture_output=True)
        result = json.loads(run.stdout)
        self.assertEqual(result['threshold_patterns'], 59049)
        self.assertIn('not a connectivity theorem', result['scope'])

    def test_complete_ordinal_cover_and_integer_realizations(self):
        self.assertEqual(escape_cover(), 59049)
        with self.assertRaisesRegex(AssertionError, 'uncovered'):
            escape_cover(())
        choices = ((0,0), (0,1), (1,0))
        root = (4,0,0,1,1,2,2,3,3,5)
        checked = 0
        for ap, bp, sp in product(product(choices, repeat=3), product(choices, repeat=3),
                                  product(choices, repeat=4)):
            a = (0,0)+sum(ap, ())
            b = bp[0]+(0,0)+bp[1]+bp[2]
            u = ((0,)+a+(0,), (0,)+b+(0,), (1,)*10, (1,)*10,
                 (2,)+(0,)*9, (2,)+sum(sp, ())+(0,))
            following = fair_neighbor(u, root)
            self.assertTrue(literal_fair(u, following))
            changed = [g-1 for g in range(1,9) if root[g] != following[g]]
            self.assertIn(tuple(changed), ESCAPE_MOVES)
            self.assertEqual((following[0], following[9]), (4,5))
            checked += 1
        self.assertEqual(checked, 59049)

    def test_escape_handles_nonbinary_values_and_more_automatic_pairs(self):
        for r in (4, 5, 10):
            rng = random.Random(2026112079+r)
            m = 2*r+2
            for trial in range(25):
                u = tuple((0,0)+tuple(Fraction(rng.randrange(40), 7) for _ in range(2*r))
                          for _ in (0,1))+((0,)+(1,)*(m-1),)*(r-2)
                u += ((100,99)+tuple(rng.randrange(90) for _ in range(2*r)),)*2
                goods = list(range(2,m))
                w = max(goods, key=lambda g: u[0][g]); goods.remove(w)
                z = max(goods, key=lambda g: u[1][g]); goods.remove(z)
                state = [r,r+1]+[-1]*(m-2); state[w]=0; state[z]=1
                for g, i in zip(goods, [0,1]+[i for i in range(2,r) for _ in (0,1)]):
                    state[g]=i
                for _ in range(30):
                    a,b = rng.sample(range(2,m),2); state[a],state[b]=state[b],state[a]
                    if not literal_fair(u,state): state[a],state[b]=state[b],state[a]
                following = fair_neighbor(u,state)
                self.assertTrue(literal_fair(u,following))
                self.assertIn(following, literal_neighbors(state))
                self.assertEqual((following[0],following[1]),(r,r+1))
        with self.assertRaises(ValueError):
            fair_neighbor(((1,)*8,)*5, (3,4,0,0,1,1,2,2))


if __name__ == '__main__':
    unittest.main()
