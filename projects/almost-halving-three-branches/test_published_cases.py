"""Independent graph-distance checks of the supported constructions."""
from collections import Counter, deque
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import unittest

import published_cases as pc


def graph_profile(lengths, vertices):
    graph = {pc.CENTRE: []}
    for arm, length in enumerate(lengths, 1):
        previous = pc.CENTRE
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    distances = {}
    for source in vertices:
        queue = deque([source])
        seen = {source: 0}
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1
                    queue.append(v)
        distances[source] = seen
    return Counter(distances[u][v] for u, v in combinations(vertices, 2))


class PublishedCasesTest(unittest.TestCase):
    def assert_witness(self, lengths, pair):
        left, right = pair
        self.assertFalse(set(left) & set(right))
        self.assertEqual(len(left), len(right))
        lp = graph_profile(lengths, left)
        rp = graph_profile(lengths, right)
        self.assertEqual(lp, rp)
        self.assertEqual(pc.profile(left), lp)
        self.assertTrue(pc.check_pair(lengths, left, right)["homometric"])

    def test_paths_cover_both_order_parities(self):
        for lengths in [(1, 1, 1), (8, 5, 2), (7, 5, 2), (2, 9, 4)]:
            with self.subTest(lengths=lengths):
                pair = pc.path_pair(lengths)
                self.assert_witness(lengths, pair)
                self.assertEqual(len(pair[0]), (sum(sorted(lengths)[1:]) + 1) // 2)

    def test_alternating_even_odd_and_empty_tail(self):
        for lengths in [(9, 7, 4), (9, 7, 5), (4, 1, 1), (3, 3, 3), (4, 4, 4)]:
            with self.subTest(lengths=lengths):
                pair = pc.alternating_pair(lengths, (1, 2, 3))
                self.assert_witness(lengths, pair)
                self.assertEqual(len(pair[0]), lengths[1] + lengths[2] // 2)

    def test_block_odd_quotients_and_remainders(self):
        for x in (1, 2, 5):
            for c in (1, 4):
                for q in (1, 3, 5):
                    for r in {0, x - 1}:
                        lengths = (q * x + r - 1, c + x, c)
                        if lengths[0] < lengths[1]:
                            continue
                        with self.subTest(lengths=lengths):
                            pair = pc.block_pair(lengths, (1, 2, 3))
                            self.assert_witness(lengths, pair)
                            self.assertEqual(sum(lengths) + 1 - 2 * len(pair[0]), r)

    def test_even_quotient_is_not_repaired(self):
        for lengths in [(15, 7, 3), (16, 7, 3), (17, 7, 3), (18, 7, 3)]:
            with self.subTest(lengths=lengths):
                with self.assertRaisesRegex(ValueError, "overruns"):
                    pc.block_pair(lengths, (1, 2, 3))

    def test_all_arm_label_permutations(self):
        for lengths in [(3, 11, 7), (7, 3, 11), (5, 9, 7)]:
            result = pc.witness(lengths)
            self.assert_witness(lengths, (result["left"], result["right"]))

    def test_multiplicities_not_just_distance_support(self):
        left = [(1, d) for d in (1, 2, 3, 5)]
        right = [(2, d) for d in (1, 2, 4, 5)]
        self.assertEqual(set(pc.profile(left)), set(pc.profile(right)))
        result = pc.check_pair((5, 5, 1), left, right)
        self.assertFalse(result["homometric"])
        self.assertEqual(result["difference"], {2: 1, 3: -1})

    def test_input_boundaries(self):
        for lengths in [(0, 2, 3), (True, 2, 3), (2, 3), (1.5, 2, 3)]:
            with self.assertRaises(ValueError):
                pc.check_pair(lengths, [], [])
        for left, right in [([(1, 1)] * 2, []), ([(0, 1)], []),
                            ([(4, 1)], []), ([(1, 4)], []),
                            ([(1, 1)], [(1, 1)]), ([(1, 1)], [])]:
            with self.assertRaises(ValueError):
                pc.check_pair((3, 3, 3), left, right)

    def test_uncovered_does_not_claim_refutation(self):
        result = pc.witness((23, 12, 6))
        self.assertEqual(result["size"], 18)
        self.assertEqual(result["target"], 20)
        self.assertTrue(result["homometric"])
        self.assertFalse(result["meets_target"])

    def test_real_cli_rejects_altered_json(self):
        script = str(Path(pc.__file__))
        left, right = pc.alternating_pair((10, 7, 5), (1, 2, 3))
        left[left.index(pc.CENTRE)] = (1, 10)
        result = {"lengths": (10, 7, 5), "left": left, "right": right}
        run = subprocess.run([sys.executable, script, "--check", "-"],
                             input=json.dumps(result), text=True, capture_output=True)
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(run.stdout)["homometric"])


if __name__ == "__main__":
    unittest.main()
