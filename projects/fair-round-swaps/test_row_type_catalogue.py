"""Independent arithmetic, deletion, and picking oracles for the catalogue."""

from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys
import unittest

import row_type_catalogue as subject


def sign(value):
    return (value > 0) - (value < 0)


def direct_type(row):
    result = [sign(v) for v in row]
    result += [sign(row[i]-row[j]) for i in range(len(row)) for j in range(i+1, len(row))]
    result += [sign(row[i]+row[j]-row[k])
               for i in range(len(row)) for j in range(i+1, len(row))
               for k in range(len(row)) if k != i and k != j]
    return tuple(result)


def direct_states(sizes):
    labels = tuple(i for i, size in enumerate(sizes) for _ in range(size))
    return tuple(sorted(set(permutations(labels))))


def deletion_mask(row, observer, states, n):
    result = 0
    for k, allocation in enumerate(states):
        own = sum(v for v, owner in zip(row, allocation) if owner == observer)
        good = True
        for target in range(n):
            bundle = [g for g, owner in enumerate(allocation) if owner == target]
            if bundle and not any(own >= sum(row[h] for h in bundle if h != removed)
                                  for removed in bundle):
                good = False
        if good:
            result |= 1 << k
    return result


def schedules(sizes):
    n, q = len(sizes), min(sizes)
    last = tuple(i for i, size in enumerate(sizes) if size > q)
    finals = tuple(permutations(last)) if last else ((),)
    return tuple(sum(rounds, ()) + tail
                 for rounds in product(tuple(permutations(range(n))), repeat=q)
                 for tail in finals)


def witness_mask(row, observer, witnesses):
    result = 0
    for k, witness in enumerate(witnesses):
        remaining = list(range(len(row)))
        legal = True
        for agent, good in witness:
            if agent == observer and any(row[h] > row[good] for h in remaining):
                legal = False
                break
            remaining.remove(good)
        if legal:
            result |= 1 << k
    return result


def reference_graph_census(row_masks, states):
    graphs = set()
    for chosen in product(*row_masks):
        fair = (1 << len(states))-1
        for mask in chosen:
            fair &= mask
        graphs.add(fair)
    adjacency = {a: {b for b in states if sum(x != y for x, y in zip(a, b)) == 2}
                 for a in states}
    disconnected, diameter = 0, 0
    for mask in graphs:
        fair = {a for k, a in enumerate(states) if mask & (1 << k)}
        for start in fair:
            distances = {start: 0}
            frontier = [start]
            for a in frontier:
                for b in (adjacency[a] & fair) - distances.keys():
                    distances[b] = distances[a]+1
                    frontier.append(b)
            diameter = max(diameter, max(distances.values()))
            if len(distances) < len(fair):
                disconnected += 1
                break
    return len(graphs), disconnected, diameter


class RowCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banks = {m: subject.catalogue(m) for m in range(1, 5)}
        cls.grids = {}
        for m in range(1, 5):
            found = {}
            # A different algorithm: scan the entire proved integer box.
            for row in product(range(2**m+1), repeat=m):
                found.setdefault(direct_type(row), row)
            cls.grids[m] = found

    def test_complete_integer_boxes_and_no_extra_or_duplicate_types(self):
        for m, count in ((1, 2), (2, 6), (3, 44), (4, 818)):
            bank = self.banks[m]
            actual = {direct_type(row) for row in bank.rows}
            self.assertEqual(actual, self.grids[m].keys())
            self.assertEqual(len(bank.rows), count)
            self.assertEqual(len(actual), count)
            self.assertIn((0,)*m, bank.rows)
            for row in bank.rows:
                self.assertTrue(all(type(v) is int and 0 <= v <= 2**m for v in row))
                self.assertEqual(subject.row_signature(row), direct_type(row))

    def test_all_observer_deletions_and_all_greedy_witnesses(self):
        # Equality of each observer's masks proves equality of their
        # intersections for every row combination, without sampling profiles.
        for sizes in ((2, 1), (2, 2), (2, 1, 1)):
            m, n = sum(sizes), len(sizes)
            states = direct_states(sizes)
            witnesses = tuple(tuple(zip(order, goods)) for order in schedules(sizes)
                              for goods in permutations(range(m)))
            deletion_pairs, witness_pairs = [[] for _ in sizes], [[] for _ in sizes]
            for k, row in enumerate(self.banks[m].rows):
                reference = self.grids[m][direct_type(row)]
                rational = tuple(Fraction(v, k % 7+1) for v in reference)
                for i in range(n):
                    before = deletion_mask(rational, i, states, n)
                    after = deletion_mask(row, i, states, n)
                    self.assertEqual(before, after)
                    deletion_pairs[i].append((before, after))
                    before = witness_mask(rational, i, witnesses)
                    after = witness_mask(row, i, witnesses)
                    self.assertEqual(before, after)
                    witness_pairs[i].append((before, after))
            census = subject.graph_census(self.banks[m], sizes)
            independent = reference_graph_census(
                [set(a for a, _ in pairs) for pairs in deletion_pairs], states)
            self.assertEqual((census['distinct_graphs'], census['disconnected_graphs'],
                              census['maximum_component_diameter']), independent)
            if n == 2:
                # Explicitly cover all 44^2 / 818^2 profiles, including
                # every schedule and tied pick, rather than one witness per outcome.
                for left, right in product(deletion_pairs[0], deletion_pairs[1]):
                    self.assertEqual(left[0] & right[0], left[1] & right[1])
                for left, right in product(witness_pairs[0], witness_pairs[1]):
                    self.assertEqual(left[0] & right[0], left[1] & right[1])

    def test_census_calibrations(self):
        for sizes, vertices, graphs, diameter in (((2, 1), 3, 4, 1),
                                                   ((2, 2), 6, 22, 2),
                                                   ((2, 1, 1), 12, 346, 3)):
            result = subject.graph_census(self.banks[sum(sizes)], sizes)
            self.assertEqual(result['allocations'], vertices)
            self.assertEqual(result['distinct_graphs'], graphs)
            self.assertEqual(result['maximum_component_diameter'], diameter)
            self.assertEqual(result['empty_graphs'], 0)
            self.assertEqual(result['disconnected_graphs'], 0)

    def test_exact_ties_large_rationals_and_relabeling(self):
        rows = ((0, 0, 0, 0), (0, 1, 1, 2), (1, 2, 3, 7), (2, 2, 4, 6))
        types = self.grids[4]
        for row in rows:
            for permuted in permutations(row):
                rational = tuple(Fraction(v, 10**100+267) for v in permuted)
                self.assertIn(subject.row_signature(rational), types)
                self.assertEqual(subject.row_signature(rational), direct_type(permuted))

    def test_rejections_and_budget_are_not_partial_catalogues(self):
        for m in (0, -1, True, 2.0):
            with self.assertRaises(ValueError):
                subject.catalogue(m)
        for budget in (0, -1, False, 2.0):
            with self.assertRaises(ValueError):
                subject.catalogue(3, max_systems=budget)
        for m, budget in ((4, 1000), (5, 1_000_000), (10**9, 1)):
            with self.assertRaisesRegex(ValueError, 'budget'):
                subject.catalogue(m, max_systems=budget)
        for row in ((), (1, -1), (0, 1.0), (False, 1), ('1/2', 1)):
            with self.assertRaises(ValueError):
                subject.row_signature(row)
        for sizes in ((4,), (3, 1), (2, 1), (2, 2.0), (2, True, 1)):
            with self.assertRaises(ValueError):
                subject.graph_census(self.banks[4], sizes)

    def test_real_command_and_preflight_refusal(self):
        script = Path(subject.__file__)
        run = subprocess.run([sys.executable, '-S', str(script), '--goods', '3', '--rows',
                              '--sizes', '2,1'], capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(len(result['rows']), 44)
        self.assertEqual(result['graph_census']['distinct_graphs'], 4)
        refused = subprocess.run([sys.executable, '-S', str(script), '--goods', '5'],
                                 capture_output=True, text=True)
        self.assertEqual(refused.returncode, 2)
        self.assertIn('system budget exceeded', refused.stderr)
        self.assertEqual(refused.stdout, '')


if __name__ == '__main__':
    unittest.main()
