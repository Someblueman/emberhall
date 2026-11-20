"""Full labelled-graph oracle independent of the compressed lift construction."""

from collections import deque
from itertools import combinations, combinations_with_replacement, permutations
from math import factorial, prod
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

from three_observer_labels import (
    BOUNDARY_MARKS, BOUNDARY_PROFILE, BOUNDARY_START, BOUNDARY_TARGET,
    boundary_census, buffer_permute, buffer_transpose, complementary_family, connect,
    connect_complementary, connect_realized, connect_with_zero_pair, explore,
    maximum_labelled_components, realize_fixed_observers, validate,
)


def pairings(goods, marks):
    if not goods:
        yield ()
        return
    a = goods[0]
    for b in goods[1:]:
        if marks[a] & marks[b] == 0:
            for tail in pairings(tuple(g for g in goods if g not in (a, b)), marks):
                yield ((a, b),) + tail


def owners(state):
    result = [-1] * (2 * len(state))
    for i, pair in enumerate(state):
        for g in pair:
            result[g] = i
    return tuple(result)


def reference_components(states):
    unseen, result = set(states), []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        found, queue = {start}, deque([start])
        while queue:
            state = queue.popleft()
            for a, b in combinations(range(len(state)), 2):
                if state[a] == state[b]:
                    continue
                nxt = list(state)
                nxt[a], nxt[b] = nxt[b], nxt[a]
                nxt = tuple(nxt)
                if nxt in unseen:
                    unseen.remove(nxt)
                    found.add(nxt)
                    queue.append(nxt)
        result.append(found)
    return result


def fair_by_deletions(profile, allocation):
    bundles = [[g for g, i in enumerate(allocation) if i == j]
               for j in range(len(profile))]
    return all(not bundle or any(sum(row[g] for g in bundles[i]) >=
                                sum(row[g] for g in bundle if g != removed)
                                for removed in bundle)
               for i, row in enumerate(profile) for bundle in bundles)


class LabelledLiftTests(unittest.TestCase):
    def check_path(self, marks, route, start, target):
        self.assertEqual(route[0], start)
        self.assertEqual(route[-1], target)
        for state in route:
            self.assertEqual(sorted(g for p in state for g in p), list(range(len(marks))))
            self.assertTrue(all(marks[a] & marks[b] == 0 for a, b in state))
        for before, after in zip(route, route[1:]):
            a, b = owners(before), owners(after)
            changed = [g for g in range(len(marks)) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_all_three_bit_multisets_through_eight_goods(self):
        profiles = states_checked = paths_checked = 0
        for size in (0, 2, 4, 6, 8):
            for marks in combinations_with_replacement(range(8), size):
                unlabelled = list(pairings(tuple(range(size)), marks))
                if not unlabelled:
                    continue
                profiles += 1
                states = {owners(state): state for p in unlabelled for state in permutations(p)}
                expected = reference_components(states)
                oracle = {state: k for k, group in enumerate(expected) for state in group}
                root = unlabelled[0]
                compressed = explore(marks, root)
                self.assertEqual(set(compressed.representatives), set(unlabelled))
                stats = compressed.statistics()
                self.assertLessEqual(stats["labelled_components"], maximum_labelled_components(size // 2))
                self.assertEqual(stats["labelled_components"], len(expected))
                self.assertEqual({len(g) for g in expected}, {stats["states_per_labelled_component"]})
                for allocation, target in states.items():
                    route = connect(compressed, target)
                    reachable = oracle[allocation] == oracle[owners(root)]
                    self.assertEqual(route is not None, reachable, (marks, root, target))
                    if route is not None:
                        self.check_path(marks, route, root, target)
                        paths_checked += 1
                states_checked += len(states)
        print(f"three-bit census: {profiles} feasible multisets; {states_checked} labelled states; "
              f"{paths_checked} exact constructed routes")

    def test_dynamic_links_and_relabelled_eight_good_graphs(self):
        marks = (0, 1, 2, 5, 3, 4)
        root = ((0, 3), (1, 2), (4, 5))
        c = explore(marks, root)
        self.assertEqual(c.statistics()["labelled_components"], 1)
        route = connect(c, root[::-1])
        self.check_path(marks, route, root, root[::-1])
        self.assertGreater(len(route) - 1, 2)  # third pair cannot swap with either initial pair
        rng = Random(20261120516)
        for _ in range(40):
            marks = tuple(rng.randrange(8) for _ in range(8))
            possible = list(pairings(tuple(range(8)), marks))
            if not possible:
                continue
            root = rng.choice(possible)
            c = explore(marks, root)
            full = {owners(p): p for m in possible for p in permutations(m)}
            oracle = reference_components(full)
            reachable = next(g for g in oracle if owners(root) in g)
            self.assertEqual(c.statistics()["states_per_labelled_component"], len(reachable))
            for allocation in rng.sample(sorted(full), min(15, len(full))):
                target = full[allocation]
                route = connect(c, target)
                self.assertEqual(route is not None, allocation in reachable)
                if route is not None:
                    self.check_path(marks, route, root, target)

    def test_every_compatibility_graph_on_six_goods(self):
        # The lift theorem is for every graph, even when its unlabelled graph
        # disconnects. Encode each forbidden edge by a private observer bit.
        edges = tuple(combinations(range(6), 2))
        feasible_graphs = checked_states = checked_components = 0
        for present in range(1 << len(edges)):
            marks = [0] * 6
            for bit, (a, b) in enumerate(edges):
                if not present & (1 << bit):
                    marks[a] |= 1 << bit
                    marks[b] |= 1 << bit
            marks = tuple(marks)
            matchings = tuple(pairings(tuple(range(6)), marks))
            if not matchings:
                continue
            feasible_graphs += 1
            states = {owners(p): p for m in matchings for p in permutations(m)}
            components = reference_components(states)
            index = {a: k for k, group in enumerate(components) for a in group}
            unseen = set(matchings)
            while unseen:
                root = min(unseen)
                c = explore(marks, root)
                unseen.difference_update(c.representatives)
                root_group = components[index[owners(root)]]
                self.assertEqual(c.statistics()["states_per_labelled_component"], len(root_group))
                for allocation, target in states.items():
                    route = connect(c, target)
                    self.assertEqual(route is not None, allocation in root_group)
                    if route is not None:
                        self.check_path(marks, route, root, target)
                checked_components += 1
            checked_states += len(states)
        self.assertEqual(checked_states, 368640)
        print(f"all six-good graphs: 32768 total, {feasible_graphs} feasible; "
              f"{checked_components} unlabelled components, {checked_states} labelled states")

    def test_zero_buffer_all_sizes_without_enumeration(self):
        for n in (2, 3, 10, 50):
            marks = (0, 0) + tuple(x for i in range(n - 1)
                                  for x in ((1, 6), (2, 5), (3, 4))[i % 3])
            start = tuple((2 * i, 2 * i + 1) for i in range(n))
            for i, j in ((0, n - 1), (n - 2, n - 1), (1, 1)):
                target = list(start)
                target[i], target[j] = target[j], target[i]
                route = buffer_transpose(marks, start, i, j)
                self.check_path(marks, route, start, tuple(target))
                self.assertLessEqual(len(route) - 1, 6)
        start, marks = ((0, 1), (2, 3), (4, 5), (6, 7)), (0,) * 8
        for target in permutations(start):
            route = buffer_permute(marks, start, target)
            self.check_path(marks, route, start, target)
            permutation = [target.index(p) for p in start]
            unseen, pair_moves = set(range(4)), 0
            while unseen:
                cycle, i = [], min(unseen)
                while i in unseen:
                    unseen.remove(i)
                    cycle.append(i)
                    i = permutation[i]
                if len(cycle) > 1:
                    pair_moves += len(cycle) - 1 if 0 in cycle else len(cycle) + 1
            self.assertEqual(len(route) - 1, 2 * pair_moves)
            self.assertLessEqual(len(route) - 1, 2 * (3 * (len(start) - 1) // 2))

    def test_positive_strict_ef1_boundary_and_whole_graph(self):
        for row in BOUNDARY_PROFILE:
            self.assertGreater(min(row), 0)
            self.assertEqual(len(row), len(set(row)))
        self.assertEqual(tuple(sum((1 << i) for i in range(3)
                                   if BOUNDARY_PROFILE[i][g] > BOUNDARY_PROFILE[i][i])
                               for g in range(3, 7)), BOUNDARY_MARKS)
        all_states = {p for p in permutations((0, 1, 2, 3, 3, 4, 4))}
        fair = {p for p in all_states if fair_by_deletions(BOUNDARY_PROFILE, p)}
        self.assertEqual(len(all_states), 1260)
        self.assertEqual(len(fair), 156)
        self.assertEqual([len(g) for g in reference_components(fair)], [156])
        fiber = {p for p in fair if p[:3] == (0, 1, 2)}
        self.assertEqual(fiber, {BOUNDARY_START, BOUNDARY_TARGET})
        self.assertEqual(sorted(map(len, reference_components(fiber))), [1, 1])
        census = boundary_census()
        self.assertEqual(census["component_sizes"], (156,))
        self.assertEqual(len(census["escape"]) - 1, 4)
        self.assertTrue(all(p in fair for p in census["escape"]))
        self.assertNotIn(BOUNDARY_TARGET, next(g for g in reference_components(fiber)
                                             if BOUNDARY_START in g))

    def test_sharp_four_block_families_and_large_constructive_paths(self):
        for counts in ((0, 0, 0, 0), (1, 1, 1, 1), (2, 1, 1, 1), (2, 2, 1, 1)):
            marks, root = complementary_family(counts)
            c = explore(marks, root)
            f = prod(factorial(k) for k in counts)
            self.assertEqual(c.statistics()["unlabelled_states"], f)
            self.assertEqual(c.statistics()["states_per_labelled_component"], f * f)
            self.assertEqual(c.statistics()["labelled_components"], maximum_labelled_components(sum(counts)))
            for order in permutations(root):
                route = connect_complementary(marks, root, order)
                generic = connect(c, order)
                self.assertEqual(route is None, generic is None)
                if route is not None:
                    self.check_path(marks, route, root, order)
                    self.assertLessEqual(len(route) - 1, 2 * len(root))
        counts = (25, 25, 25, 25)
        marks, root = complementary_family(counts)
        target = tuple(p for offset in range(0, 100, 25)
                       for p in root[offset + 1:offset + 25] + root[offset:offset + 1])
        route = connect_complementary(marks, root, target)
        self.check_path(marks, route, root, target)
        self.assertEqual(len(route) - 1, 192)
        changed = list(root)
        changed[0], changed[25] = changed[25], changed[0]
        self.assertIsNone(connect_complementary(marks, root, tuple(changed)))

    def test_exact_positive_strict_realization_for_every_pair_partition(self):
        for marks in (tuple(range(8)), (0, 0, 1, 6, 2, 5), (1, 1, 2, 2, 4, 4)):
            profile = realize_fixed_observers(marks)
            for row in profile:
                self.assertGreater(min(row), 0)
                self.assertEqual(len(row), len(set(row)))
            for pairing in pairings(tuple(range(len(marks))), (0,) * len(marks)):
                state = (0, 1, 2) + tuple(i + 3 for i in owners(pairing))
                legal = all(marks[a] & marks[b] == 0 for a, b in pairing)
                self.assertEqual(fair_by_deletions(profile, state), legal)

    def test_one_observer_loan_crosses_all_label_classes(self):
        marks, root = complementary_family((1, 1, 1, 1))
        profile = realize_fixed_observers(marks)
        for target in permutations(root):
            for observer in range(3):
                order = (observer,) + tuple(i for i in range(3) if i != observer)
                route = connect_realized(marks, root, target, order)
                self.assertLessEqual(len(route) - 1, 2 + 2 * (3 * (len(root) - 1) // 2))
                self.assertTrue(all(fair_by_deletions(profile, state) for state in route))
                self.assertEqual(route[0], (0, 1, 2) + tuple(i + 3 for i in owners(root)))
                self.assertEqual(route[-1], (0, 1, 2) + tuple(i + 3 for i in owners(target)))
                for state in route:
                    self.assertEqual([state.count(i) for i in range(7)], [1, 1, 1, 2, 2, 2, 2])
                    for other in set(range(3)) - {observer}:
                        self.assertEqual(state[other], other)
                for before, after in zip(route, route[1:]):
                    changed = [g for g in range(len(before)) if before[g] != after[g]]
                    self.assertEqual(len(changed), 2)
                    a, b = changed
                    self.assertEqual((before[a], before[b]), (after[b], after[a]))
        # Same argument with a non-complementary pair: only the zero/high loan
        # and unchanged pair legality are used by this construction.
        marks, root = (0, 1, 2, 4, 0, 0), ((0, 1), (2, 3), (4, 5))
        route = connect_realized(marks, root, root[::-1])
        self.assertTrue(all(fair_by_deletions(realize_fixed_observers(marks), a) for a in route))
        marks, root = complementary_family((3, 3, 3, 3))
        profile = realize_fixed_observers(marks)
        route = connect_realized(marks, root, root[::-1])
        self.assertTrue(all(fair_by_deletions(profile, a) for a in route))
        self.assertEqual(len(route) - 1, 34)
        route = connect_realized(BOUNDARY_MARKS, ((0, 1), (2, 3)), ((2, 3), (0, 1)))
        self.assertTrue(all(fair_by_deletions(realize_fixed_observers(BOUNDARY_MARKS), a) for a in route))
        self.check_path((0, 0, 0, 0), connect_with_zero_pair((0, 0, 0, 0),
                        ((0, 1), (2, 3)), ((0, 2), (1, 3))), ((0, 1), (2, 3)), ((0, 2), (1, 3)))

    def test_realized_family_connects_different_matchings_and_label_classes(self):
        rng = Random(20261120517)
        for counts in ((1, 1, 1, 1), (2, 2, 1, 1), (3, 3, 3, 3)):
            marks, root = complementary_family(counts)
            profile = realize_fixed_observers(marks)
            for _ in range(10):
                relabel = list(range(len(marks)))
                for mark in range(8):
                    goods = [g for g, m in enumerate(marks) if m == mark]
                    shuffled = rng.sample(goods, len(goods))
                    for g, h in zip(goods, shuffled):
                        relabel[g] = h
                target = [tuple(sorted(relabel[g] for g in pair)) for pair in root]
                rng.shuffle(target)
                target = tuple(target)
                route = connect_realized(marks, root, target)
                self.assertEqual(route[-1], (0, 1, 2) + tuple(i + 3 for i in owners(target)))
                self.assertLessEqual(len(route) - 1, 5 * len(root) - 1)
                self.assertTrue(all(fair_by_deletions(profile, state) for state in route))
                for a, b in zip(route, route[1:]):
                    changed = [g for g in range(len(a)) if a[g] != b[g]]
                    self.assertEqual(len(changed), 2)
                    x, y = changed
                    self.assertEqual((a[x], a[y]), (b[y], b[x]))

    def test_two_universal_goods_connect_every_target_on_six_goods(self):
        edges = tuple(combinations(range(2, 6), 2))
        checked = 0
        for present in range(1 << len(edges)):
            marks = [0] * 6
            for bit, (a, b) in enumerate(edges):
                if not present & (1 << bit):
                    marks[a] |= 1 << bit
                    marks[b] |= 1 << bit
            marks = tuple(marks)
            base = list(pairings(tuple(range(2, 6)), marks))
            if not base:
                continue
            start = ((0, 1),) + base[0]
            for matching in pairings(tuple(range(6)), marks):
                for target in permutations(matching):
                    route = connect_with_zero_pair(marks, start, target)
                    self.check_path(marks, route, start, target)
                    self.assertLessEqual(len(route) - 1, 9)
                    checked += 1
        print(f"two universal goods: {checked} exact arbitrary-graph endpoint routes")
        # A chordless 24-cycle forces a long alternating cycle, with no
        # unproved direct chord available to shorten the buffer construction.
        n = 26
        marks = [0] * n
        for bit, (a, b) in enumerate(combinations(range(2, n), 2)):
            if b - a not in (1, n - 3):
                marks[a] |= 1 << bit
                marks[b] |= 1 << bit
        marks = tuple(marks)
        root = ((0, 1),) + tuple((i, i + 1) for i in range(2, n, 2))
        tail = tuple((i, i + 1) for i in range(3, n - 1, 2))
        for target in (((0, 1),) + tail + ((2, n - 1),),
                       ((0, 2),) + tail + ((1, n - 1),)):
            target = target[::-1]
            route = connect_with_zero_pair(marks, root, target)
            self.check_path(marks, route, root, target)
            self.assertLessEqual(len(route) - 1, 3 * (3 * (len(root) - 1) // 2))

    def test_realized_loan_all_small_three_bit_profiles(self):
        checked = 0
        for n in (2, 4, 6):
            for marks in combinations_with_replacement(range(8), n):
                matches = list(pairings(tuple(range(n)), marks))
                if not matches:
                    continue
                profile = realize_fixed_observers(marks)
                root, target = matches[0], matches[-1][::-1]
                route = connect_realized(marks, root, target)
                self.assertTrue(all(fair_by_deletions(profile, a) for a in route))
                self.assertLessEqual(len(route) - 1, 4 + 3 * (3 * (n // 2 - 1) // 2))
                checked += 1
        print(f"positive strict realized profiles: {checked} exact EF1 loan routes")

    def test_separate_unlabelled_components_and_invalid_inputs(self):
        # Encode a chordless six-cycle: each forbidden pair gets its own bit.
        marks = [0] * 6
        for bit, (a, b) in enumerate((a, b) for a, b in combinations(range(6), 2)
                                    if (b - a) not in (1, 5)):
            marks[a] |= 1 << bit
            marks[b] |= 1 << bit
        c = explore(tuple(marks), ((0, 1), (2, 3), (4, 5)))
        self.assertEqual(len(c.representatives), 1)
        self.assertIsNone(connect(c, ((0, 5), (1, 2), (3, 4))))
        for marks, state in (((1,), ()), ((-1, 0), ((0, 1),)),
                             ((True, 0), ((0, 1),)), ((0, 0), ((0, 0),)),
                             ((0, 0), ((0, 2),)), ((1, 1), ((0, 1),))):
            with self.assertRaises(ValueError):
                validate(marks, state)
        with self.assertRaisesRegex(ValueError, "zero-marked"):
            buffer_transpose(BOUNDARY_MARKS, ((0, 1), (2, 3)), 0, 1)
        with self.assertRaisesRegex(ValueError, "unknown recipient"):
            buffer_transpose((0, 0), ((0, 1),), 0, 2)
        with self.assertRaises(ValueError):
            maximum_labelled_components(True)
        with self.assertRaises(ValueError):
            complementary_family((1, 1, -1, 1))
        with self.assertRaises(ValueError):
            connect_complementary((0, 0), ((0, 1),), ((0, 1),))
        with self.assertRaises(ValueError):
            realize_fixed_observers((0, 8))
        with self.assertRaises(ValueError):
            connect_with_zero_pair(BOUNDARY_MARKS, ((0, 1), (2, 3)), ((2, 3), (0, 1)))
        with self.assertRaises(ValueError):
            connect_realized((0, 0), ((0, 1),), ((0, 1),), (0, 0, 1))
        run = subprocess.run([sys.executable, str(Path(__file__).with_name("three_observer_labels.py"))],
                             capture_output=True, text=True, check=True)
        self.assertIn("'fair_states': 156", run.stdout)
        self.assertIn("0123344 ->", run.stdout)


if __name__ == "__main__":
    unittest.main()
