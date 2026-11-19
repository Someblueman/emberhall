from itertools import combinations, permutations
import unittest

import check


class PathCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = check.reconstruct(10, [(i, i + 1) for i in range(9)])
        cls.cert = check.make_certificate(cls.graph)

    def test_reconstruct_by_recoloring_at_most_three_positions(self):
        # Each changed position loses and gains a color. All lost colors must
        # be distinct, and all gained colors must be distinct.
        words = ["0", "1", "2"]
        for _ in range(9):
            words = [word + c for word in words for c in "012" if c != word[-1]]
        self.assertEqual(words, self.graph.words)
        index = {word: i for i, word in enumerate(words)}
        found = set()
        for u, word in enumerate(words):
            for n in (1, 2, 3):
                for positions in combinations(range(10), n):
                    old = [word[p] for p in positions]
                    if len(set(old)) < n:
                        continue
                    for new in permutations("012", n):
                        if any(a == b for a, b in zip(old, new)):
                            continue
                        candidate = list(word)
                        for p, color in zip(positions, new):
                            candidate[p] = color
                        v = index.get("".join(candidate))
                        if v is not None and u < v:
                            found.add((u, v))
        self.assertEqual(found, set(self.graph.edges))
        self.assertEqual((len(words), len(found), len(self.graph.boundaries)), (1536, 20616, 53004))
        rotated = [index[w.translate(str.maketrans("012", "120"))] for w in words]
        self.assertEqual(found, {tuple(sorted((rotated[u], rotated[v]))) for u, v in found})

    def test_full_certificate_and_reversed_whole_walk(self):
        check.verify(self.graph, self.cert)
        first = self.cert["steps"][0]
        inverse = [-x for x in reversed(first)]
        check.verify(self.graph, {**self.cert, "steps": [inverse, *self.cert["steps"][1:]]})

    def test_changed_exchange(self):
        edges = list(self.cert["edges"])
        edges[0] = [0, len(self.graph.words) - 1]
        with self.assertRaisesRegex(check.InvalidProof, "reconstructed exchanges"):
            check.verify(self.graph, {**self.cert, "edges": edges})

    def test_missing_assignment(self):
        with self.assertRaisesRegex(check.InvalidProof, "all legal colorings"):
            check.verify(self.graph, {**self.cert, "words": self.cert["words"][:-1]})

    def test_reversed_letter(self):
        steps = list(self.cert["steps"])
        a, b, c = steps[-1]
        steps[-1] = [a, -b, c]
        with self.assertRaisesRegex(check.InvalidProof, "oriented triangle boundary"):
            check.verify(self.graph, {**self.cert, "steps": steps})

    def test_duplicate_tree_edge_cannot_connect_all_vertices(self):
        tree = self.cert["tree"].copy()
        tree[-1] = tree[0]
        with self.assertRaisesRegex(check.InvalidProof, "does not reach"):
            check.verify(self.graph, {**self.cert, "tree": tree})

    def test_missing_last_deduction(self):
        with self.assertRaisesRegex(check.InvalidProof, "1 edge generator remains"):
            check.verify(self.graph, {**self.cert, "steps": self.cert["steps"][:-1]})

    def test_seven_vertex_obstruction(self):
        conflicts = [(u, v) for u in range(3) for v in range(3, 6)] + [(0, 6), (3, 6)]
        graph = check.reconstruct(7, conflicts)
        self.assertEqual(len(graph.words), 42)
        self.assertFalse(any(check.obstruction_ef1(word) for word in graph.words))
        with self.assertRaisesRegex(check.InvalidProof, "42 edge generators remain"):
            check.verify(graph, check.make_certificate(graph))
