"""Original-deletion and independently enumerated graph checks."""
from collections import deque
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

import four_singletons_one_pair as subject
from single_extra import isolated_family


def literal_fair(utilities, owners):
    bundles = [[g for g, owner in enumerate(owners) if owner == i]
               for i in range(len(utilities))]
    return all(any(sum(row[g] for g in bundles[i]) >=
                       sum(row[g] for g in bundle if g != removed)
                   for removed in bundle)
               for i, row in enumerate(utilities) for bundle in bundles if bundle)


class OnePairTests(unittest.TestCase):
    def test_full_graph_and_strict_example(self):
        states = set()
        for pair in combinations(range(6), 2):
            rest = [g for g in range(6) if g not in pair]
            for singleton_goods in permutations(rest):
                state = [0] * 6
                for i, g in enumerate(singleton_goods, 1):
                    state[g] = i
                states.add(tuple(state))
        self.assertEqual(states, set(subject.STATES))
        for i, state in enumerate(subject.STATES):
            expected = {other for other in states
                        if sum(x != y for x, y in zip(state, other)) == 2}
            actual = {subject.STATES[j] for j in range(360) if subject.ADJACENCY[i] >> j & 1}
            self.assertEqual(actual, expected)
        utilities, isolated, _ = isolated_family(5, strict=True)
        live = {state for state in states if literal_fair(utilities, state)}
        self.assertEqual(len(live), 60)
        sizes, left = [], set(live)
        while left:
            reached = {min(left)}
            queue = deque(reached)
            while queue:
                state = queue.popleft()
                for other in live - reached:
                    if sum(x != y for x, y in zip(state, other)) == 2:
                        reached.add(other)
                        queue.append(other)
            sizes.append(len(reached))
            left -= reached
        self.assertEqual(sorted(sizes), [1, 59])
        self.assertIn(isolated, live)

    def test_original_deletions_and_cardinal_invariance(self):
        rng = Random(61120)
        for _ in range(24):
            rows = [tuple(Fraction(rng.randrange(8), rng.choice((1, 3, 7)))
                          for _ in range(6)) for _ in range(4)]
            pair_row = tuple(rng.randrange(100) for _ in range(6))
            mask = subject.fair_mask(rows)
            for i, state in enumerate(subject.STATES):
                self.assertEqual(bool(mask >> i & 1), literal_fair([pair_row] + rows, state))
            rank_rows = [subject.ranks(row) for row in rows]
            stretched = [tuple(Fraction(10 ** v, 3) for v in row) for row in rank_rows]
            self.assertEqual(subject.fair_mask(stretched), mask)

    def test_family_with_independent_deletions(self):
        for k in (4, 5, 6, 7, 8, 12):
            utilities, start, target = subject.four_multivalued_family(k)
            self.assertTrue(literal_fair(utilities, start))
            self.assertTrue(literal_fair(utilities, target))
            self.assertEqual(sum(len(set(row)) > 2 for row in utilities[1:]), 4)
            self.assertTrue(all(min(row) > 0 for row in utilities))
            count = 0
            for x, y in combinations(range(k + 2), 2):
                if start[x] == start[y]:
                    continue
                changed = list(start)
                changed[x], changed[y] = changed[y], changed[x]
                self.assertFalse(literal_fair(utilities, changed), (k, x, y))
                count += 1
            self.assertEqual(count, (k + 2) * (k + 1) // 2 - 1)
            cycle = (0, 3, 2, 1)
            for current, previous in zip(cycle, cycle[-1:] + cycle[:-1]):
                self.assertGreater(utilities[current + 1][previous], utilities[current + 1][current])
            result = subject.fair_neighbor_or_cycle(utilities, start)
            self.assertEqual(result['kind'], 'cycle')
            self.assertEqual(len(result['recipients']), 4)

    def test_general_alternating_cycle_boundary(self):
        # Both best-buffer swaps fail, but a mutual-improvement swap is fair.
        u = ((1, 1, 1, 1), (3, 4, 2, 5), (4, 3, 5, 2))
        self.assertEqual(subject.fair_neighbor_or_cycle(u, (1, 2, 0, 0)),
                         {'kind': 'neighbor', 'state': (2, 1, 0, 0)})
        rng = Random(117)
        for k in (1, 2, 3, 4, 7, 10):
            for _ in range(200):
                rows = [tuple(rng.randrange(6 if i <= 3 else 2) for _ in range(k + 2))
                        for i in range(k + 1)]
                start = tuple(range(1, k + 1)) + (0, 0)
                if literal_fair(rows, start):
                    result = subject.fair_neighbor_or_cycle(rows, start)
                    self.assertEqual(result['kind'], 'neighbor')
                    self.assertTrue(literal_fair(rows, result['state']))
                    self.assertEqual(sum(a != b for a, b in zip(start, result['state'])), 2)

    def test_orbit_coverage_and_complete_census(self):
        # Enumerating all 6^6 words independently recovers every weak-order shape.
        orders = {row for row in product(range(6), repeat=6)
                  if set(row) == set(range(max(row) + 1))}
        self.assertEqual(len(orders), 4683)
        self.assertEqual({tuple(sorted(row)) for row in orders}, set(subject.sorted_orders()))
        representatives = subject.binary_orders()
        self.assertEqual(len(representatives), 57)
        for row in product((0, 1), repeat=6):
            candidates = [r for r in representatives if subject.row_mask(row, 0) == subject.row_mask(r, 0)]
            self.assertEqual(len(candidates), 1)
            for i in range(4):
                self.assertEqual(subject.row_mask(row, i), subject.row_mask(candidates[0], i))
        result = subject.check_profiles(subject.census_profiles())
        self.assertEqual(result['status'], 'all_checked_graphs_connected')
        self.assertEqual((result['profiles'], result['distinct_graphs']), (1040288, 467896))
        self.assertEqual(sum(result['vertex_histogram'].values()), 1040288)
        self.assertEqual(result['stream_sha256'],
                         '723d254378c6a87d636c1b77f6b7d47dd1ef5356e930b6e152449e012d0091fe')

    def test_greedy_endpoints_still_connect_and_command(self):
        utilities, isolated, _ = isolated_family(5, strict=True)
        outcomes = set()
        for schedule in permutations(range(5)):
            remaining, owners = set(range(6)), [-1] * 6
            for i in schedule + (0,):
                g = max(remaining, key=lambda x: utilities[i][x])
                owners[g] = i
                remaining.remove(g)
            state = tuple(owners)
            self.assertTrue(literal_fair(utilities, state))
            self.assertNotEqual(state, isolated)
            outcomes.add(state)
        self.assertGreater(len(outcomes), 1)
        root = min(outcomes)
        for target in outcomes:
            path = subject.shortest_path(utilities[1:], root, target)
            self.assertTrue(all(literal_fair(utilities, state) for state in path))
        with self.assertRaisesRegex(ValueError, 'disconnected'):
            subject.shortest_path(utilities[1:], isolated, root)
        result = subprocess.run([sys.executable, '-S', str(Path(subject.__file__))],
                                text=True, capture_output=True, check=True)
        self.assertIn('"isolated_EF1_state"', result.stdout)
        self.assertIn('"excluded_exchanges": 14', result.stdout)
        for k in (2, 3):
            with self.assertRaises(ValueError):
                isolated_family(k + 1, strict=True)
        with self.assertRaisesRegex(ValueError, 'exact nonnegative'):
            subject.fair_mask([[1.0] * 6] * 4)


if __name__ == '__main__':
    unittest.main()
