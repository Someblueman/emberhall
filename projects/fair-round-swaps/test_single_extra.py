"""Independent deletion checks and brute picking orders for SINGLE_EXTRA.md."""

from fractions import Fraction
from itertools import combinations, product
from random import Random
import unittest

from single_extra import greedy_witness, isolated_family, neighbor_up_to_four, rejected_swaps
from swaps import allocation, picking_outcomes, rounds_for, states_with_sizes, validate_witness


def deletion_fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(len(u))]
    for i, row in enumerate(u):
        own = sum(row[g] for g in bundles[i])
        for goods in bundles:
            if goods and not any(own >= sum(row[g] for g in goods if g != removed)
                                 for removed in goods):
                return False
    return True


def neighbors(a):
    for x, y in combinations(range(len(a)), 2):
        if a[x] != a[y]:
            b = list(a)
            b[x], b[y] = b[y], b[x]
            yield (x, y), tuple(b)


class SingleExtraTest(unittest.TestCase):
    def test_family_every_neighbor_and_ordinal_perturbations(self):
        for n in (5, 6, 7, 10, 17):
            for strict in (False, True):
                u, a, b = isolated_family(n, strict=strict)
                # Unequal positive gaps preserve the ordinal statement exactly.
                u = tuple(tuple(Fraction(2 ** int(x), 3) for x in row) for row in u)
                with self.subTest(n=n, strict=strict):
                    self.assertTrue(deletion_fair(u, a))
                    self.assertTrue(deletion_fair(u, b))
                    self.assertNotEqual(a, b)
                    adjacent = list(neighbors(a))
                    self.assertEqual(len(adjacent), n * (n + 1) // 2 - 1)
                    self.assertTrue(all(not deletion_fair(u, state) for _, state in adjacent))
                    failures = rejected_swaps(u, a)
                    self.assertEqual(set(failures), {pair for pair, _ in adjacent})
                    self.assertIsNone(greedy_witness(u, a))
                    self.assertIsNone(greedy_witness(u, b))

    def test_entire_six_good_graph_and_brute_greedy_endpoints(self):
        u, a, _ = isolated_family(5)
        states = states_with_sizes((2, 1, 1, 1, 1))
        fair = {state for state in states if deletion_fair(u, state)}
        todo = set(fair)
        groups = []
        while todo:
            reached = {todo.pop()}
            frontier = list(reached)
            while frontier:
                state = frontier.pop()
                for _, next_state in neighbors(state):
                    if next_state in todo:
                        todo.remove(next_state)
                        reached.add(next_state)
                        frontier.append(next_state)
            groups.append(reached)
        self.assertEqual(len(states), 360)
        self.assertEqual(sorted(map(len, groups)), [1, 89])
        self.assertIn({a}, groups)
        brute = picking_outcomes(u, rounds_for(5, 6, (0,)))
        recognized = {state for state in states if greedy_witness(u, state) is not None}
        self.assertEqual(recognized, set(brute))
        self.assertEqual(len(brute), 24)
        self.assertTrue(any(set(brute) <= group for group in groups))

    def test_topological_recognizer_with_ties_and_relabeling(self):
        rng = Random(2026112007)
        for n in (2, 3, 4, 5):
            states = states_with_sizes((2,) + (1,) * (n - 1))
            for trial in range(12):
                u = tuple(tuple(rng.randrange(3) if trial else 0 for _ in range(n + 1))
                          for _ in range(n))
                brute = picking_outcomes(u, rounds_for(n, n + 1, (0,)))
                for a in states:
                    w = greedy_witness(u, a)
                    self.assertEqual(w is not None, a in brute)
                    if w is not None:
                        validate_witness(u, rounds_for(n, n + 1, (0,)), w)
                        self.assertEqual(allocation(w, n + 1), a)
                # The double recipient need not be agent zero.
                rename = tuple(reversed(range(n)))
                moved_u = tuple(u[rename[i]] for i in range(n))
                a = states[trial % len(states)]
                moved_a = tuple(rename[i] for i in a)
                self.assertEqual(greedy_witness(u, a) is not None,
                                 greedy_witness(moved_u, moved_a) is not None)

    def test_constructed_neighbor_for_every_binary_profile_up_to_four(self):
        checked = 0
        for n in (2, 3, 4):
            m = n + 1
            a = (0, 0) + tuple(range(1, n))
            for flat in product((0, 1), repeat=m * (n - 1)):
                u = ((0,) * m,) + tuple(tuple(flat[j * m:(j + 1) * m])
                                       for j in range(n - 1))
                if deletion_fair(u, a):
                    b = neighbor_up_to_four(u, a)
                    self.assertIn(b, {state for _, state in neighbors(a)})
                    self.assertTrue(deletion_fair(u, b))
                    checked += 1
        # A singleton fails exactly on bits own=0, double=(1,1).
        self.assertEqual(checked, sum((7 * 2 ** (n - 2)) ** (n - 1) for n in (2, 3, 4)))

    def test_invalid_model_is_refused(self):
        with self.assertRaises(ValueError):
            isolated_family(4)
        for u, a in [(((1, 2), (2, 1)), (0, 1)),
                     (((1, 2, 3), (3, 2, 1)), (0, 0, 0))]:
            with self.assertRaises(ValueError):
                greedy_witness(u, a)
        u, a, _ = isolated_family(5)
        with self.assertRaises(ValueError):
            neighbor_up_to_four(u, a)


if __name__ == "__main__":
    unittest.main()
