"""Independent deletion and schedule checks for the isolated-state boundary."""

from itertools import combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys
import unittest

from five_agent_three_final import (EIGHT, EIGHT_STATE, SIDE, SIDE_STATE,
                                   certificate, rejected_exchanges, strict_refinement)
from swaps import ef1, states_with_sizes


def deletion_fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(len(u))]
    for i, row in enumerate(u):
        own = sum(row[g] for g in bundles[i])
        for bundle in bundles:
            if not any(own >= sum(row[g] for g in bundle if g != removed)
                       for removed in [None] + bundle):
                return False
    return True


def schedule_outcomes(u):
    """Enumerate permutations of each round, then every maximizing tie choice."""
    result = set()

    def pick(order, remaining, owners):
        if not order:
            result.add(tuple(owners))
            return
        i = order[0]
        maximum = max(u[i][g] for g in remaining)
        for g in remaining:
            if u[i][g] == maximum:
                changed = owners[:]
                changed[g] = i
                pick(order[1:], [h for h in remaining if h != g], changed)

    for first, final in product(permutations(range(len(u))), permutations((0, 1, 2))):
        pick(first + final, list(range(len(u[0]))), [-1] * len(u[0]))
    return result


class ObstructionTests(unittest.TestCase):
    def test_every_state_against_explicit_deletions(self):
        for u, a in ((SIDE, SIDE_STATE), (EIGHT, EIGHT_STATE)):
            for profile in (u, strict_refinement(u)):
                states = states_with_sizes(tuple(a.count(i) for i in range(len(u))))
                self.assertEqual(len(states), 630 if len(u) == 4 else 5040)
                for state in states:
                    self.assertEqual(ef1(profile, state), deletion_fair(profile, state))

    def test_every_exchange_is_rejected_with_a_valid_witness(self):
        for u, a in ((SIDE, SIDE_STATE), (EIGHT, EIGHT_STATE)):
            original = rejected_exchanges(u, a)
            self.assertEqual(len(original), 18 if len(u) == 4 else 25)
            self.assertEqual({tuple(w['swap']) for w in original},
                             {(x, y) for x, y in combinations(range(len(a)), 2)
                              if a[x] != a[y]})
            for profile in (u, strict_refinement(u)):
                self.assertTrue(deletion_fair(profile, a))
                for witness in original:
                    x, y = witness['swap']
                    b = list(a)
                    b[x], b[y] = b[y], b[x]
                    self.assertFalse(deletion_fair(profile, b))
                    i, j = witness['observer'], witness['envied']
                    own = sum(profile[i][g] for g, owner in enumerate(b) if owner == i)
                    other = [g for g, owner in enumerate(b) if owner == j]
                    self.assertTrue(all(own < sum(profile[i][g] for g in other if g != h)
                                        for h in [None] + other))

    def test_exact_greedy_census_including_ties(self):
        for u, a, expected, strict_count in ((SIDE, SIDE_STATE, 55, 18),
                                            (EIGHT, EIGHT_STATE, 395, 84)):
            for profile, count in ((u, expected), (strict_refinement(u), strict_count)):
                greedy = schedule_outcomes(profile)
                self.assertEqual(len(greedy), count)
                self.assertNotIn(a, greedy)
                self.assertTrue(all(deletion_fair(profile, b) for b in greedy))
                result = certificate(profile, a)
                self.assertEqual(result['greedy_outcomes'], count)
                self.assertEqual(len(result['greedy_component_sizes']), 1)
                self.assertEqual(result['component_sizes'][0], 1)

    def test_strict_refinement_and_rejection_boundaries(self):
        for u in (SIDE, EIGHT):
            for row in strict_refinement(u):
                self.assertGreater(min(row), 0)
                self.assertEqual(len(set(row)), len(row))
        with self.assertRaisesRegex(ValueError, 'certified only'):
            strict_refinement(((0, 1), (1, 0)))
        other = next(iter(schedule_outcomes(SIDE)))
        with self.assertRaisesRegex(ValueError, 'preserves EF1'):
            rejected_exchanges(SIDE, other)
        with self.assertRaisesRegex(ValueError, 'not EF1'):
            rejected_exchanges(SIDE, (0, 1, 0, 1, 2, 2, 3))

    def test_real_command(self):
        run = subprocess.run([sys.executable, str(Path(__file__).with_name(
            'five_agent_three_final.py'))], capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        eight = result['five_agents_eight_goods']
        self.assertEqual(eight['component_sizes'], [1, 790])
        self.assertEqual(eight['favorite_protected']['component_sizes'], [1, 318])
        self.assertIn('greedy-endpoint question stays open', result['scope'])


if __name__ == '__main__':
    unittest.main()
