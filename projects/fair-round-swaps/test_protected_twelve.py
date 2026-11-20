"""Independently check paths and keep resource limits distinct from separation."""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from protected_twelve import (Graph, START, TARGET, candidate_cut, check_cover, load_frontier,
                              profile, smt2, splice_cover, cover_vertices, frontier_vertices, verify_ten_step_distance)


# Fixed r=5 fixture from Tern 8398f70; no pending helper-module dependency.
ANTICHAIN_PROFILE = (
    (1, 500, 3, 4, 5, 6, 17, 16, 15, 14, 13, 12),
    (1, 2, 500, 4, 5, 6, 17, 16, 15, 14, 13, 12),
    (1, 2, 3, 500, 5, 6, 17, 16, 15, 14, 13, 12),
    (1, 2, 3, 4, 500, 6, 17, 16, 15, 14, 13, 12),
    (1, 2, 3, 4, 5, 500, 17, 16, 15, 14, 13, 12),
    (60, 2, 11, 21, 31, 41, 50, 1, 10, 20, 30, 40),
    (60, 2, 41, 31, 21, 11, 1, 50, 40, 30, 20, 10)
)


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(7)]
    for i, row in enumerate(u):
        own = sum(row[g] for g in bundles[i])
        for bundle in bundles:
            if not any(own >= sum(row[g] for g in bundle if g != removed)
                       for removed in bundle):
                return False
    return True


class TwelveTests(unittest.TestCase):
    def check(self, u, result):
        self.assertEqual(result['status'], 'connected')
        path = [tuple(a) for a in result['path']]
        self.assertEqual((path[0], path[-1]), (START, TARGET))
        for a in path:
            self.assertTrue(fair(u, a))
            self.assertIn(a[0], (5, 6))
            self.assertEqual(tuple(a.count(i) for i in range(7)), (2,)*5+(1, 1))
        for a, b in zip(path, path[1:]):
            changed = [g for g in range(12) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_profiles_and_antichain(self):
        for seed in range(15):
            u = profile(seed)
            self.check(u, Graph(u).search())
        u = ANTICHAIN_PROFILE
        self.check(u, Graph(u).search())
        zero = ((0,)*12,)*7
        result = Graph(zero).search()
        self.check(zero, result)
        self.assertEqual(len(result['path'])-1, 2)

    def test_exact_fairness_and_neighbors(self):
        u = tuple(tuple(Fraction(x, i+3) for x in row)
                  for i, row in enumerate(profile(43)))
        graph = Graph(u)
        rng = random.Random(2026112045)
        for _ in range(500):
            a = [i for i in range(5) for _ in range(2)]+[5, 6]
            rng.shuffle(a)
            holder = rng.choice((5, 6))
            h = a.index(holder)
            a[0], a[h] = a[h], a[0]
            a = tuple(a)
            self.assertEqual(graph.fair(a), fair(u, a))
            expected = set()
            for x, y in combinations(range(12), 2):
                b = list(a)
                b[x], b[y] = b[y], b[x]
                if tuple(b) != a and b[0] in (5, 6):
                    expected.add(tuple(b))
            self.assertEqual(set(graph.neighbors(a)), expected)
            self.assertEqual(len(expected), 51)

    def test_budget_is_not_a_counterexample(self):
        u = ANTICHAIN_PROFILE
        graph = Graph(u)
        stopped = graph.search(2)
        self.assertEqual(stopped['status'], 'budget_exhausted')
        self.assertIsNone(stopped['path'])
        self.assertEqual(stopped['checked'], 2)
        self.check(u, graph.search(200000))
        with self.assertRaises(ValueError):
            graph.search(1)
        with self.assertRaises(ValueError):
            Graph(u[:-1])
        bad = [list(row) for row in u]
        bad[5][0] = 0
        with self.assertRaises(ValueError):
            Graph(tuple(map(tuple, bad)))

    def test_actual_budgeted_command(self):
        result = subprocess.run([sys.executable, '-S',
                                 str(Path(__file__).with_name('protected_twelve.py')),
                                 '--seed', '0', '--max-checks', '2'],
                                check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'budget_exhausted')
        self.assertIn('unresolved', data['scope'])

    def test_retained_case_and_query_domain(self):
        data = load_frontier()
        states = [tuple(a) for a in data['states']]
        self.assertEqual(len(states), len(set(states)))
        for a in states:
            self.assertIn(a[0], (5, 6))
            self.assertEqual(tuple(a.count(i) for i in range(7)), (2,)*5+(1, 1))
        u = tuple(tuple(Fraction(x) for x in row) for row in data['last']['utilities'])
        self.check(u, Graph(u).search(250000))
        # Independent all-deletions and all-transpositions check of the finite
        # candidate's failure; the full graph path above still exists.
        allowed = {a for a in states if fair(u, a)}
        seen, pending = {START}, [START]
        while pending:
            a = pending.pop()
            for x, y in combinations(range(12), 2):
                b = list(a)
                b[x], b[y] = b[y], b[x]
                b = tuple(b)
                if b in allowed and b not in seen:
                    seen.add(b)
                    pending.append(b)
        self.assertNotIn(TARGET, seen)
        self.assertEqual(candidate_cut(u, states), {
            'candidate_vertices': 12010, 'fair_vertices': 1650,
            'start_component': 742, 'target_reached': False,
            'scope': 'retained subgraph only'})
        self.assertEqual((len(allowed), len(seen)), (1650, 742))
        text = smt2([START, TARGET])
        self.assertEqual(text.count('() Real)'), 84)
        self.assertIn('(assert (not r1))', text)
        self.assertEqual(text.count('(check-sat)'), 1)
        with self.assertRaises(ValueError):
            smt2([START, START, TARGET])
        path = Graph(((0,)*12,)*7).search()['path']
        cover = smt2(path, [path])
        self.assertIn('(assert (not (and f0 f1 f2)))', cover)
        self.assertNotIn('(assert (not r', cover)
        with self.assertRaises(ValueError):
            smt2(path, [[START, TARGET]])


    def test_enlarged_cover_has_a_checked_external_repair(self):
        data = load_frontier()
        phase = data['continuations'][-1]
        case = phase['final_counterexample']
        paths = data['paths']
        self.assertEqual((phase['initial_paths'], len(paths)), (1581, 2189))
        self.assertEqual(phase['status'], 'time_limit')
        u = tuple(tuple(Fraction(x) for x in row) for row in case['utilities'])
        # This direct deletion predicate is independent of the new reporter.
        self.assertFalse(any(all(fair(u, a) for a in path) for path in paths))
        report = check_cover(u, paths)
        self.assertEqual((report['paths'], report['fair_paths']), (2189, 0))
        self.assertIsNone(report['first_fair_path'])
        self.check(u, case['search'])
        self.check(u, Graph(u).search(250000))
        self.assertEqual(len(case['search']['path'])-1, 8)
        zero = ((0,)*12,)*7
        self.assertEqual(check_cover(zero, paths)['fair_paths'], len(paths))
        with self.assertRaises(ValueError):
            check_cover(u, [[START, TARGET]])
        broken = [list(a) for a in paths[0]]
        broken[1][0] = 0
        with self.assertRaises(ValueError):
            check_cover(u, [broken])

    def test_splicing_uses_all_real_edges_between_retained_vertices(self):
        data = load_frontier()
        case = data['continuations'][-1]['final_counterexample']
        u = tuple(tuple(Fraction(x) for x in row) for row in case['utilities'])
        paths = data['paths']
        self.assertEqual(check_cover(u, paths)['fair_paths'], 0)
        result = splice_cover(u, paths)
        self.check(u, result)
        self.assertEqual((result['vertices'], result['fair_vertices']), (4097, 696))
        # This is a new route through the union, not a fair member of the list.
        self.assertNotIn(tuple(result['path']), {tuple(map(tuple, p)) for p in paths})
        self.assertTrue(set(result['path']) <= set(cover_vertices(paths)))
        # Independently rebuild every edge among fair union vertices.
        allowed = {a for a in cover_vertices(paths) if fair(u, a)}
        seen, pending = {START}, [START]
        while pending:
            a = pending.pop()
            for x, y in combinations(range(12), 2):
                b = list(a)
                b[x], b[y] = b[y], b[x]
                b = tuple(b)
                if b in allowed and b not in seen:
                    seen.add(b)
                    pending.append(b)
        self.assertIn(TARGET, seen)
        self.assertEqual(len(seen), 693)
        missing = splice_cover(u, paths[:1])
        self.assertEqual(missing['status'], 'uncovered')
        self.assertIsNone(missing['path'])
        with self.assertRaises(ValueError):
            splice_cover(u, [])
        with self.assertRaises(ValueError):
            cover_vertices([[START, TARGET]])
        command = subprocess.run([sys.executable, '-S',
                                  str(Path(__file__).with_name('protected_twelve.py')),
                                  '--splice-cover'], check=True, capture_output=True, text=True)
        report = json.loads(command.stdout)
        self.assertEqual(report['listed']['fair_paths'], 0)
        self.check(u, report['spliced'])
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'spliced.smt2'
            subprocess.run([sys.executable, '-S',
                            str(Path(__file__).with_name('protected_twelve.py')),
                            '--splice-cover', '--write-smt2', str(target)],
                           check=True, capture_output=True, text=True)
            query = target.read_text()
            self.assertEqual(query.count('() Real)'), 84)
            self.assertIn('(assert (not r', query)
            self.assertEqual(query.count('(check-sat)'), 1)

    def test_retained_spliced_frontier_fails_only_in_its_finite_pool(self):
        data = load_frontier()
        continuation = data['splice_search']
        phase = continuation['phases'][-1]
        self.assertIn(phase['status'], ('iteration_limit', 'time_limit', 'vertex_limit', 'budget_exhausted'))
        if phase['status'] != 'budget_exhausted':
            self.assertEqual(phase['final_query_status'], 'sat')
        case = continuation['final_counterexample']
        u = tuple(tuple(Fraction(x) for x in row) for row in case['utilities'])
        vertices = frontier_vertices(data)
        self.assertEqual(len(vertices), phase['final_vertices'])
        # A fresh deletion/transposition traversal proves the saved finite cut.
        allowed = {a for a in vertices if fair(u, a)}
        seen, pending = {START}, [START]
        while pending:
            a = pending.pop()
            for x, y in combinations(range(12), 2):
                b = list(a)
                b[x], b[y] = b[y], b[x]
                b = tuple(b)
                if b in allowed and b not in seen:
                    seen.add(b)
                    pending.append(b)
        self.assertNotIn(TARGET, seen)
        self.assertEqual((len(allowed), len(seen)),
                         (case['cut']['fair_vertices'], case['cut']['start_component']))
        self.assertEqual(candidate_cut(u, vertices), case['cut'])
        if phase['status'] == 'budget_exhausted':
            self.assertEqual(case['search']['status'], 'budget_exhausted')
            self.assertEqual(Graph(u).search(250000)['status'], 'budget_exhausted')
            repair = continuation['adjudication']['search']
            self.check(u, Graph(u).search(2494800))
        else:
            repair = case['search']
        self.check(u, repair)
        self.assertTrue(any(tuple(a) not in set(vertices) for a in repair['path']))
        command = subprocess.run([sys.executable, '-S',
                                  str(Path(__file__).with_name('protected_twelve.py')),
                                  '--splice-cover', '--max-checks', '2'],
                                 check=True, capture_output=True, text=True)
        report = json.loads(command.stdout)['frontier']
        self.assertFalse(report['candidate']['target_reached'])
        self.assertEqual(report['full_graph']['status'], 'budget_exhausted')
        self.assertIsNone(report['full_graph']['path'])

    def test_exact_ten_step_distance_has_no_shorter_full_graph_path(self):
        data = load_frontier()
        case = data['splice_search']['ten_step_case']
        u = tuple(map(tuple, case['utilities']))
        route = tuple(map(tuple, case['path']))
        self.check(u, {'status': 'connected', 'path': route})
        self.assertTrue(all(v > 0 for row in u for v in row))
        self.assertTrue(all(len(set(row)) == 12 for row in u))
        self.assertEqual(min(abs(row[a]+row[b]-row[c]) for row in u
                             for a, b in combinations(range(12), 2)
                             for c in range(12) if c not in (a, b)), 1)
        cache = {}

        def neighbors(a):
            for x, y in combinations(range(12), 2):
                b = list(a)
                b[x], b[y] = b[y], b[x]
                if b != list(a) and b[0] in (5, 6):
                    yield tuple(b)

        def ball(root):
            seen, layer, counts = {root}, {root}, [1]
            for _ in range(4):
                following = set()
                for a in layer:
                    for b in neighbors(a):
                        if b not in cache:
                            cache[b] = fair(u, b)  # Literal deletion oracle.
                        if b not in seen and cache[b]:
                            following.add(b)
                seen.update(following)
                layer = following
                counts.append(len(layer))
            return seen, counts

        left, counts_left = ball(START)
        right, counts_right = ball(TARGET)
        self.assertEqual(counts_left, [1, 22, 206, 1165, 4398])
        self.assertEqual(counts_right, [1, 21, 198, 1149, 4406])
        self.assertFalse(left & right)
        self.assertFalse(any(b in right for a in left for b in neighbors(a)))
        result = verify_ten_step_distance(u, route)
        self.assertEqual(result['distance'], 10)
        self.assertEqual(result['ball_sizes'], [5792, 5775])
        shortcut = [START]
        for x, y in ((0, 6), (0, 7)):
            state = list(shortcut[-1])
            state[x], state[y] = state[y], state[x]
            shortcut.append(tuple(state))
        self.assertEqual(shortcut[-1], TARGET)
        self.assertEqual(shortcut[1][0], 0)
        self.assertTrue(all(fair(u, state) for state in shortcut))
        self.assertEqual(sum(x != y for x, y in zip(START, TARGET)), 3)
        old = data['continuations'][-1]['final_counterexample']
        old_u = tuple(tuple(Fraction(v) for v in row) for row in old['utilities'])
        old_route = list(map(tuple, old['search']['path']))
        detour = [old_route[0], old_route[1]] + old_route
        with self.assertRaisesRegex(ValueError, 'at most nine'):
            verify_ten_step_distance(old_u, detour)
        command = subprocess.run([sys.executable, '-S',
                                  str(Path(__file__).with_name('protected_twelve.py')),
                                  '--ten-step-case'], check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(command.stdout)['distance'], 10)

    def test_cover_case_command_keeps_the_graph_budget_separate(self):
        result = subprocess.run([sys.executable, '-S',
                                 str(Path(__file__).with_name('protected_twelve.py')),
                                 '--cover-case', '--max-checks', '2'],
                                check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['cover']['fair_paths'], 0)
        self.assertEqual(data['search']['status'], 'budget_exhausted')
        self.assertIsNone(data['search']['path'])
        self.assertEqual(len(data['utilities']), 7)


if __name__ == '__main__':
    unittest.main()
