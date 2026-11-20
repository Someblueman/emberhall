"""Independent finite definitions for the four-good certificate."""

from fractions import Fraction
from itertools import combinations, permutations, product
import unittest

import four_goods as subject


def ordered_partitions():
    # Alternative enumeration: permute labels, then cut between tie blocks.
    result = set()
    for ordering in permutations(range(4)):
        for cuts in product((False, True), repeat=3):
            ranks = [0] * 4
            rank = 0
            for j, good in enumerate(ordering):
                if j and cuts[j - 1]:
                    rank += 1
                ranks[good] = rank
            result.add(tuple(ranks))
    return result


def general_ef1(utilities, allocation):
    bundles = [[g for g in range(4) if allocation[g] == i] for i in range(3)]
    for i, row in enumerate(utilities):
        own = sum(row[g] for g in bundles[i])
        for bundle in bundles:
            if bundle and all(own < sum(row[h] for h in bundle if h != g)
                              for g in bundle):
                return False
    return True


def is_exchange(a, b):
    changed = [g for g in range(4) if a[g] != b[g]]
    return (len(changed) == 2 and a[changed[0]] == b[changed[1]]
            and a[changed[1]] == b[changed[0]])


class FourGoodsTests(unittest.TestCase):
    def test_complete_enumerations(self):
        self.assertEqual(set(subject.weak_orders()), ordered_partitions())
        self.assertEqual(len(subject.weak_orders()), 75)
        self.assertEqual(set(subject.STATES),
                         {a for a in product(range(3), repeat=4)
                          if tuple(a.count(i) for i in range(3)) == (2, 1, 1)})

    def test_every_graph_against_general_definition(self):
        # A's row is irrelevant; use nonzero, nonuniform exact values.
        owner_row = (Fraction(1, 7), 900, 0, Fraction(8, 13))
        for b, c in product(ordered_partitions(), repeat=2):
            rows = (owner_row, b, c)
            vertices = {a for a in subject.STATES if general_ef1(rows, a)}
            reference = {a: {z for z in vertices if is_exchange(a, z)} for a in vertices}
            actual = subject.graph(b, c)
            self.assertEqual({a: set(v) for a, v in actual.items()}, reference)
            # Boolean reachability by at most three exchanges; no BFS calls.
            for a in vertices:
                reached = {a}
                for _ in range(3):
                    reached |= {z for x in tuple(reached) for z in reference[x]}
                self.assertEqual(reached, vertices)

    def test_rank_reduction_with_nonuniform_rational_gaps(self):
        levels = (Fraction(0), Fraction(1, 1000), Fraction(7, 3), Fraction(10**9))
        for b, c in product(ordered_partitions(), repeat=2):
            rows = ((0, 0, 0, 0), tuple(levels[r] for r in b),
                    tuple(levels[r] for r in c))
            for a in subject.STATES:
                self.assertEqual(general_ef1(rows, a), subject.fair(a, b, c))

    def test_sharp_distance_and_paths(self):
        b, c = (0, 0, 1, 1), (1, 1, 0, 0)
        edges = subject.graph(b, c)
        pairs = [(a, z) for a, z in combinations(edges, 2)
                 if z not in {a, *edges[a], *(v for u in edges[a] for v in edges[u])}]
        self.assertTrue(pairs)
        for a, z in pairs:
            path = subject.shortest_path(b, c, a, z)
            self.assertEqual(len(path), 4)
            self.assertEqual((path[0], path[-1]), (a, z))
            self.assertTrue(all(is_exchange(x, y) for x, y in zip(path, path[1:])))
            self.assertTrue(all(x in edges for x in path))
        with self.assertRaisesRegex(ValueError, "endpoints"):
            subject.shortest_path(b, c, (0, 0, 1, 2), (0, 0, 0, 0))

    def test_certificate_is_complete(self):
        result = subject.certificate()
        self.assertEqual(result["profiles"], 5625)
        self.assertEqual(result["distinct_graphs"], 346)
        self.assertEqual(result["diameter_histogram"], {2: 4311, 3: 1314})
        self.assertEqual(result["certificate_sha256"],
                         "a7c8f21c0e0eff04bf99de48e669944dfb92b174160e5251a85d03ba8200d121")


if __name__ == "__main__":
    unittest.main()
