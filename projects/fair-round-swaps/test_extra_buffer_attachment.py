"""Independent deletion, picking, and complete-graph checks of the loss barrier."""

from collections import deque
from fractions import Fraction
from itertools import combinations, permutations
import json
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

from extra_buffer_attachment import (audit, barrier_certificate, family, path,
                                     totals, verify, witnesses)


def fair(u, state):
    bundles = [[g for g, a in enumerate(state) if a == j] for j in range(len(u))]
    return all(not other or any(sum(row[g] for g in own) >=
                                sum(row[g] for g in other if g != removed)
                                for removed in other)
               for row, own in zip(u, bundles) for other in bundles)


def loss(u, start, state, proportional=False):
    losses = []
    for i, row in enumerate(u):
        first = sum(row[g] for g, a in enumerate(start) if a == i)
        now = sum(row[g] for g, a in enumerate(state) if a == i)
        losses.append(Fraction(max(0, first - now), first) if proportional else max(0, first - now))
    return max(losses)


def reachable(states, start):
    seen, queue = {start}, deque([start])
    while queue:
        state = queue.popleft()
        for x, y in combinations(range(len(state)), 2):
            changed = list(state)
            changed[x], changed[y] = changed[y], changed[x]
            other = tuple(changed)
            if other in states and other not in seen:
                seen.add(other)
                queue.append(other)
    return seen


class BufferAttachmentTests(unittest.TestCase):
    def test_bare_two_agent_example(self):
        u = ((11, 10, 9, 1), (21, 10, 9, 1))
        start, middle, target = (0, 1, 1, 0), (1, 0, 1, 0), (1, 0, 0, 1)
        for state in (start, middle, target):
            self.assertTrue(fair(u, state))
        self.assertEqual((totals(u, start), totals(u, target)), ((12, 19), (19, 22)))
        all_states = set(permutations((0, 0, 1, 1)))
        floors = {state for state in all_states if loss(u, start, state) == 0}
        self.assertNotIn(target, reachable(floors, start))
        self.assertEqual(loss(u, start, middle), 1)

    def test_strict_family_paths_and_greedy_witnesses(self):
        for r in (2, 3, 4, 8, 20):
            m = 2 * r + 2
            for scale in (m + 1, 10 * m):
                u, start = family(r, scale)
                result = verify(r, scale)
                route = path(start)
                expected = scale + 4 - m
                self.assertTrue(all(min(row) > 0 and len(set(row)) == m for row in u))
                for row in u[2:r]:
                    self.assertGreater(sum(sorted(row)[:2]), max(row))
                for witness, state in zip(witnesses(r), (start, route[-1])):
                    remaining, owners = set(range(m)), [-1] * m
                    for agent, good in witness:
                        self.assertEqual(u[agent][good], max(u[agent][g] for g in remaining))
                        owners[good] = agent
                        remaining.remove(good)
                    self.assertEqual(tuple(owners), state)
                    self.assertEqual({a for a, _ in witness[:r + 2]}, set(range(r + 2)))
                    self.assertEqual({a for a, _ in witness[r + 2:]}, set(range(r)))
                self.assertTrue(all(fair(u, state) for state in route))
                for a, b in zip(route, route[1:]):
                    changed = [g for g in range(m) if a[g] != b[g]]
                    self.assertEqual(len(changed), 2)
                    x, y = changed
                    self.assertEqual((a[x], a[y]), (b[y], b[x]))
                initial, final = totals(u, start), totals(u, route[-1])
                self.assertTrue(all(b >= a for a, b in zip(initial, final)))
                self.assertTrue(all(final[a] > initial[a] for a in (0, 1)))
                self.assertEqual(initial[2:], final[2:])
                self.assertEqual(max(loss(u, start, state) for state in route), expected)
                self.assertEqual(max(loss(u, start, state, True) for state in route),
                                 Fraction(expected, 3 * scale + 9))
                self.assertEqual(result['optimal_maximum_temporary_loss'], expected)

    def test_full_unrestricted_graphs_and_strict_loss_thresholds(self):
        for r in (2, 3):
            u, start = family(r, 100)
            target = path(start)[-1]
            states = set(permutations(tuple(a for a in range(r) for _ in range(2)) + (r, r + 1)))
            allowed = {state for state in states if fair(u, state)}
            expected = 100 + 4 - len(start)
            for proportional, bound in ((False, expected), (True, Fraction(expected, 309))):
                below = {s for s in allowed if loss(u, start, s, proportional) < bound}
                at = {s for s in allowed if loss(u, start, s, proportional) <= bound}
                self.assertNotIn(target, reachable(below, start))
                self.assertIn(target, reachable(at, start))
            result = audit(r, 100)
            self.assertEqual(result['all_states'], len(states))
            self.assertEqual(result['fair_states'], len(allowed))
            self.assertEqual(result['independent_minimax_loss'], expected)
            self.assertEqual(Fraction(result['independent_minimax_proportional_loss']),
                             Fraction(expected, 309))

    def test_rational_perturbations_preserve_the_qualitative_result(self):
        rng = Random(2026112087)
        for r in (2, 4, 9):
            base, start = family(r, 100)
            for _ in range(16):
                u = tuple(tuple(Fraction(v) + Fraction(rng.randrange(-5, 6), 1000)
                                for v in row) for row in base)
                self.assertGreater(barrier_certificate(u, start)['lower_bound'], 0)
                self.assertTrue(all(fair(u, state) for state in path(start)))
                self.assertTrue(all(b >= a for a, b in zip(totals(u, start), totals(u, path(start)[-1]))))
                for witness in witnesses(r):
                    remaining = set(range(len(start)))
                    for agent, good in witness:
                        self.assertEqual(u[agent][good], max(u[agent][g] for g in remaining))
                        remaining.remove(good)

    def test_command_and_invalid_domains(self):
        script = Path(__file__).with_name('extra_buffer_attachment.py')
        run = subprocess.run([sys.executable, '-S', str(script), '--pairs', '3', '--audit'],
                             text=True, capture_output=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(result['optimal_maximum_temporary_loss'], 96)
        self.assertEqual(result['complete_graph']['independent_minimax_loss'], 96)
        for r, scale in ((1, 100), (True, 100), (4, 10), (4, 1.5)):
            with self.assertRaises(ValueError):
                family(r, scale)
        with self.assertRaises(ValueError):
            audit(4)
        u, start = family()
        with self.assertRaises(ValueError):
            barrier_certificate(tuple((1,) * len(start) for _ in u), start)


if __name__ == '__main__':
    unittest.main()
