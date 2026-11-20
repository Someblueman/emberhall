"""Literal deletion and complete-graph audits of the temporary-loss theorem."""

from fractions import Fraction
import heapq
from itertools import combinations, permutations
import json
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

from extra_buffer_attachment import (OwnerGraph, audit, barrier_certificate, family,
                                     greedy_family, greedy_route, greedy_witnesses,
                                     routes, totals, verify, verify_greedy)


def fair(u, state):
    bundles = [[g for g, a in enumerate(state) if a == j] for j in range(len(u))]
    return all(not other or any(sum(row[g] for g in own) >=
                                sum(row[g] for g in other if g != removed)
                                for removed in other)
               for row, own in zip(u, bundles) for other in bundles)


def cost(u, start, state):
    agents = (0, 1, len(u) - 2, len(u) - 1)
    return max([0] + [sum(u[a][g] for g, b in enumerate(start) if b == a)
                           - sum(u[a][g] for g, b in enumerate(state) if b == a)
                           for a in agents])


class BufferAttachmentTests(unittest.TestCase):
    def test_greedy_endpoints_and_independent_full_graph_optimum(self):
        for r in (3, 4, 8, 15):
            for scale in (None, 10 * (2 * r + 2)):
                u, start = greedy_family(r, scale)
                if scale is not None:
                    self.assertTrue(all(min(row) > 0 and len(set(row)) == len(row) for row in u))
                result = verify_greedy(r, scale)
                path = greedy_route(start)
                self.assertTrue(all(fair(u, state) for state in path))
                for witness, state in zip(greedy_witnesses(r), (start, path[-1])):
                    remaining = set(range(len(start)))
                    owners = [-1] * len(start)
                    for offset, (agent, good) in enumerate(witness):
                        self.assertEqual(u[agent][good], max(u[agent][h] for h in remaining))
                        remaining.remove(good)
                        owners[good] = agent
                    self.assertEqual(tuple(owners), state)
                    self.assertEqual({a for a, _ in witness[:r + 2]}, set(range(r + 2)))
                    self.assertEqual({a for a, _ in witness[r + 2:]}, set(range(r)))
                self.assertEqual(max(cost(u, start, state) for state in path),
                                 result["optimal_maximum_temporary_loss"])
        # This audit allows good zero to move to any agent. Its shortest
        # bottleneck result does not assume a protected carrier or given path.
        graph = OwnerGraph(3, fixed_g=False)
        for scale in (None, 100):
            u, start = greedy_family(3, scale)
            allowed = {i for i, state in enumerate(graph.states) if fair(u, state)}
            self.assertEqual(allowed, graph.fair_vertices(u))
            source, target = graph.index[start], graph.index[greedy_route(start)[-1]]
            best, queue = {source: 0}, [(0, source)]
            while queue:
                value, vertex = heapq.heappop(queue)
                if value != best[vertex]:
                    continue
                for neighbor in graph.adjacency[vertex]:
                    if neighbor not in allowed:
                        continue
                    candidate = max(value, cost(u, start, graph.states[neighbor]))
                    if neighbor not in best or candidate < best[neighbor]:
                        best[neighbor] = candidate
                        heapq.heappush(queue, (candidate, neighbor))
            self.assertEqual(best[target], 8 if scale is None else 796)

    def test_family_paths_and_departure_certificate(self):
        for r in (2, 3, 4, 8, 25):
            for scale in (None, 10 * (2 * r + 2)):
                u, start = family(r, scale)
                report = verify(r, scale)
                expected = 1 if scale is None else scale - 3 if r == 2 else scale - 2 * r
                self.assertEqual(report["optimal_maximum_temporary_loss"], expected)
                if scale is not None:
                    self.assertTrue(all(min(row) > 0 and len(set(row)) == len(row) for row in u))
                    initial, final = totals(u, start), totals(u, routes(start)[0][-1])
                    self.assertTrue(all(initial[i] < final[i] for i in (0, 1, 3)))
                    self.assertEqual(initial[2], final[2])
                for path in routes(start):
                    for state in path:
                        self.assertTrue(fair(u, state))
                        self.assertEqual(state[0], r)
                        self.assertEqual(sorted(state), sorted(start))
                    for left, right in zip(path, path[1:]):
                        changed = [g for g in range(len(start)) if left[g] != right[g]]
                        self.assertEqual(len(changed), 2)
                        x, y = changed
                        self.assertEqual((left[x], left[y]), (right[y], right[x]))

    def test_complete_small_graph_and_independent_minimax(self):
        for r in (2, 3):
            graph = OwnerGraph(r, fixed_g=False)
            rest = [a for a in range(r) for _ in range(2)] + [r, r + 1]
            literal_states = set(permutations(rest))
            self.assertEqual(set(graph.states), literal_states)
            for scale in (None, 100):
                u, start = family(r, scale)
                literal_fair = {state for state in literal_states if fair(u, state)}
                self.assertEqual({graph.states[i] for i in graph.fair_vertices(u)}, literal_fair)
                adjacency = {}
                for state in literal_fair:
                    neighbors = set()
                    for x, y in combinations(range(len(state)), 2):
                        changed = list(state)
                        changed[x], changed[y] = changed[y], changed[x]
                        if state[x] != state[y] and tuple(changed) in literal_fair:
                            neighbors.add(tuple(changed))
                    adjacency[state] = neighbors
                    self.assertEqual(neighbors, {graph.states[i] for i in
                        graph.adjacency[graph.index[state]] if graph.states[i] in literal_fair})
                target = routes(start)[0][-1]
                best, queue = {start: 0}, [(0, start)]
                while queue:
                    value, state = heapq.heappop(queue)
                    if value != best[state]:
                        continue
                    for neighbor in adjacency[state]:
                        candidate = max(value, cost(u, start, neighbor))
                        if neighbor not in best or candidate < best[neighbor]:
                            best[neighbor] = candidate
                            heapq.heappush(queue, (candidate, neighbor))
                self.assertEqual(best[target], verify(r, scale)["optimal_maximum_temporary_loss"])

    def test_complete_ten_good_graph(self):
        result = audit(4, 100)
        self.assertEqual(result, {
            "all_states": 22680, "undirected_edges": 362880, "fair_states": 5320,
            "floor_states": 36, "full_start_component": 5320,
            "floor_start_component": 6, "target_meets_floors": True,
            "target_in_floor_start_component": False,
        })
        graph = OwnerGraph(4)
        u, start = family(4, 100)
        fixed = [state for state in graph.states if state[:6] == start[:6]]
        self.assertEqual(len(fixed), 6)
        self.assertTrue(all(fair(u, state) for state in fixed))
        self.assertTrue(all(barrier_certificate(u, state)["minimum_departure_loss"] == 92
                            for state in fixed))

    def test_open_rational_neighborhood(self):
        rng = Random(2026112086)
        for r in (2, 4, 9):
            base, start = family(r, 100)
            for _ in range(24):
                u = tuple(tuple(Fraction(v) + Fraction(rng.randrange(-5, 6), 100)
                                for v in row) for row in base)
                self.assertTrue(all(min(row) > 0 and len(set(row)) == len(row) for row in u))
                self.assertGreater(barrier_certificate(u, start)["minimum_departure_loss"], 0)
                for path in routes(start):
                    self.assertTrue(all(fair(u, state) for state in path))
                    first, last = totals(u, start), totals(u, path[-1])
                    self.assertTrue(all(last[i] > first[i] for i in (0, 1, 3)))
                    self.assertEqual(first[2], last[2])

    def test_command_and_rejected_domains(self):
        script = Path(__file__).with_name("extra_buffer_attachment.py")
        run = subprocess.run([sys.executable, "-S", str(script), "--pairs", "4", "--audit"],
                             text=True, capture_output=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(result["optimal_maximum_temporary_loss"], 92)
        self.assertTrue(result["complete_graph"]["target_meets_floors"])
        for r, scale in ((1, None), (True, None), (4, 10), (4, 1.5)):
            with self.assertRaises(ValueError):
                family(r, scale)
        with self.assertRaises(ValueError):
            OwnerGraph(5)
        u, start = family(4)
        with self.assertRaises(ValueError):
            barrier_certificate(tuple((1,) * 10 for _ in u), start)


if __name__ == "__main__":
    unittest.main()
