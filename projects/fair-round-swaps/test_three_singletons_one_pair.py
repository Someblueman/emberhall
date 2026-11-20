"""Independent ordered-partition, deletion and full-graph census audit."""

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

import three_singletons_one_pair as subject


def ordered_partitions():
    result = set()
    for order in permutations(range(5)):
        for cuts in product((False, True), repeat=4):
            row, rank = [0] * 5, 0
            for position, good in enumerate(order):
                if position and cuts[position - 1]:
                    rank += 1
                row[good] = rank
            result.add(tuple(row))
    return tuple(sorted(result))


STATES = tuple(sorted(set(permutations((0, 1, 2, 3, 3)))))


def adjacent(a, b):
    changed = [i for i in range(5) if a[i] != b[i]]
    return (len(changed) == 2 and a[changed[0]] == b[changed[1]]
            and a[changed[1]] == b[changed[0]])


NEIGHBORS = tuple(tuple(j for j, b in enumerate(STATES) if adjacent(a, b)) for a in STATES)


def literal_fair(profile, state):
    bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(4)]
    return all(any(sum(row[g] for g in bundles[i]) >=
                   sum(row[g] for g in bundle if g != removed) for removed in bundle)
               for i, row in enumerate(profile) for bundle in bundles)


def graph_components(mask):
    unseen = {i for i in range(60) if mask & (1 << i)}
    parts = []
    while unseen:
        root = unseen.pop()
        queue, found = deque([root]), {root}
        while queue:
            for j in NEIGHBORS[queue.popleft()]:
                if j in unseen:
                    unseen.remove(j)
                    found.add(j)
                    queue.append(j)
        parts.append(found)
    return parts


class FiveGoodTests(unittest.TestCase):
    def test_complete_rank_and_exchange_domains(self):
        orders = ordered_partitions()
        self.assertEqual(len(orders), 541)
        self.assertEqual(orders, subject.weak_orders())
        self.assertEqual({tuple(sorted(row)) for row in orders}, set(subject.canonical_first_rows()))
        self.assertEqual(len(subject.canonical_first_rows()), 16)
        self.assertEqual(set(STATES), set(subject.STATES))
        self.assertEqual({len(x) for x in NEIGHBORS}, {9})
        for state in STATES:
            index = subject.INDEX[state]
            actual = {subject.STATES[j] for j in range(60) if subject.NEIGHBORS[index] & (1 << j)}
            expected = {other for other in STATES if adjacent(state, other)}
            self.assertEqual(actual, expected)

    def test_full_unaggregated_weak_order_census(self):
        orders = ordered_partitions()
        canonical = tuple(sorted({tuple(sorted(row)) for row in orders}))
        role_masks = []
        # Each row mask is checked by literally deleting one item from the
        # double bundle, in a separately ordered 60-state domain.
        for role in range(3):
            masks = []
            for row in orders:
                allowed = 0
                for i, state in enumerate(STATES):
                    own = row[state.index(role)]
                    pair = [g for g, owner in enumerate(state) if owner == 3]
                    if any(own >= sum(row[g] for g in pair if g != removed) for removed in pair):
                        allowed |= 1 << i
                actual = subject.row_mask(row, role)
                self.assertEqual({subject.STATES[i] for i in range(60) if actual & (1 << i)},
                                 {STATES[i] for i in range(60) if allowed & (1 << i)})
                masks.append(allowed)
            role_masks.append(dict(zip(orders, masks)))
        graphs = Counter()
        for a in canonical:
            for b in orders:
                partial = role_masks[0][a] & role_masks[1][b]
                for c in orders:
                    graphs[partial & role_masks[2][c]] += 1
        histogram = Counter()
        for mask, multiplicity in graphs.items():
            self.assertEqual(len(graph_components(mask)), 1)
            histogram[mask.bit_count()] += multiplicity
            # A separate Boolean-relation product proves all pairs are at
            # distance at most five. It uses this file's independent graph.
            vertices = [i for i in range(60) if mask & (1 << i)]
            one = {i: (1 << i) | sum(1 << j for j in NEIGHBORS[i] if mask & (1 << j))
                   for i in vertices}
            two = {}
            for i in vertices:
                row = one[i]
                for j in NEIGHBORS[i]:
                    if j in one:
                        row |= one[j]
                two[i] = row
            four = {}
            for i in vertices:
                row, via = 0, two[i]
                while via:
                    bit = via & -via
                    via ^= bit
                    row |= two[bit.bit_length() - 1]
                four[i] = row
            for i in vertices:
                row = four[i]
                for j in NEIGHBORS[i]:
                    if j in four:
                        row |= four[j]
                self.assertEqual(row, mask)
        actual = subject.census()
        self.assertEqual(actual["status"], "CONNECTED_FOR_ALL")
        self.assertEqual(actual["profiles_checked"], 4682896)
        self.assertEqual(actual["fair_state_histogram"], dict(sorted(histogram.items())))
        self.assertEqual(sum(graphs.values()), 4682896)
        print(f"independent weak-order audit: {len(graphs)} distinct full EF1 graphs; "
              f"{sum(graphs.values())} unaggregated profiles")

    def test_strict_sharp_diameter_witness(self):
        profile = subject.SHARP_PROFILE
        self.assertTrue(all(min(row) > 0 and len(set(row)) == 5 for row in profile))
        fair = {a for a in STATES if literal_fair(profile, a)}
        self.assertEqual(len(fair), 15)
        distance, queue = {subject.SHARP_START: 0}, deque([subject.SHARP_START])
        while queue:
            a = queue.popleft()
            for b in fair:
                if b not in distance and adjacent(a, b):
                    distance[b] = distance[a] + 1
                    queue.append(b)
        self.assertEqual(distance[subject.SHARP_TARGET], 5)
        route = subject.path(profile, subject.SHARP_START, subject.SHARP_TARGET)
        self.assertEqual(len(route) - 1, 5)
        self.assertEqual(subject.diameter(subject.fair_mask(profile))[0], 5)

    def test_rational_paths_and_relabelling(self):
        rng = Random(20261120518)
        paths = 0
        for _ in range(100):
            profile = tuple(tuple(Fraction(rng.randrange(8), rng.choice((1, 2, 7)))
                                  for _ in range(5)) for _ in range(4))
            fair = [a for a in STATES if literal_fair(profile, a)]
            a, b = rng.choice(fair), rng.choice(fair)
            route = subject.path(profile, a, b)
            self.assertIsNotNone(route)
            self.assertEqual((route[0], route[-1]), (a, b))
            self.assertTrue(all(literal_fair(profile, state) for state in route))
            self.assertTrue(all(adjacent(x, y) for x, y in zip(route, route[1:])))
            self.assertLessEqual(len(route) - 1, 5)
            perm = rng.sample(range(5), 5)
            changed = tuple(tuple(row[g] for g in perm) for row in profile)
            self.assertEqual({tuple(a[g] for g in perm) for a in fair},
                             {a for a in STATES if literal_fair(changed, a)})
            paths += 1
        print(f"rational endpoint and simultaneous-good-relabel checks: {paths}")

    def test_incomplete_is_not_coverage_and_real_command(self):
        self.assertEqual(subject.census(0)["status"], "INCOMPLETE")
        command = subprocess.run([sys.executable, str(Path(subject.__file__)), "--seconds", "0"],
                                 text=True, capture_output=True)
        self.assertEqual(command.returncode, 2)
        self.assertEqual(json.loads(command.stdout)["profiles_checked"], 0)
        with self.assertRaises(ValueError):
            subject.fair_mask(((1, 2, 3, 4, 5),) * 3)
        with self.assertRaises(ValueError):
            subject.fair_mask(((1, 2, 3, 4, 0.5),) * 4)
        with self.assertRaises(ValueError):
            subject.path(((1, 2, 3, 4, 5),) * 4, (0, 0, 1, 2, 3), STATES[0])
        profile = ((1, 2, 3, 4, 5),) * 4
        unfair = next(a for a in STATES if not literal_fair(profile, a))
        with self.assertRaises(ValueError):
            subject.path(profile, unfair, unfair)
        with self.assertRaises(ValueError):
            subject.component_masks(-1)
        self.assertEqual(subject.diameter(1 << 17), (0, 17, 17))


if __name__ == "__main__":
    unittest.main()
