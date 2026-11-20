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

    def test_gap_family_full_partition(self):
        for t in (2, 3, 4, 5, 6, 7, 14, 15):
            with self.subTest(t=t):
                result = pc.gap_family_witness(t)
                left, right = result["left"], result["right"]
                self.assert_witness(result["lengths"], (left, right))
                self.assertEqual(len(left), (7 * t) // 2)
                self.assertEqual(len(set(left) | set(right)), 7 * t - (t % 2))
        for t in (0, 1, -1, True):
            with self.assertRaises(ValueError):
                pc.gap_family_witness(t)

    def test_shell_omitted_vertex_correction(self):
        lengths = (9, 7, 4)
        left, right = pc.alternating_pair(lengths, (1, 2, 3))
        all_vertices = [pc.CENTRE] + [(i, d) for i, n in enumerate(lengths, 1)
                                    for d in range(1, n + 1)]
        for altered in (False, True):
            a = left.copy()
            if altered:
                a[a.index(pc.CENTRE)] = (1, 9)
            signs = {v: (1 if v in a else -1) for v in a + right}
            holes = set(all_vertices) - signs.keys()
            corrected, uncorrected = {}, {}
            for d in range(1, 17):
                full = sum(s * sum(pc.distance(v, w) == d for w in all_vertices)
                           for v, s in signs.items())
                correction = sum(s * sum(pc.distance(v, w) == d for w in holes)
                                 for v, s in signs.items())
                corrected[d] = full - correction
                uncorrected[d] = full
            lp, rp = graph_profile(lengths, a), graph_profile(lengths, right)
            self.assertEqual(corrected, {d: 2 * (lp[d] - rp[d]) for d in corrected})
            if not altered:
                self.assertFalse(any(corrected.values()))
                self.assertTrue(any(uncorrected.values()))

    def test_gap_family_formal_identity(self):
        # Integer Laurent coefficients in TWO INDEPENDENT variables z and r.
        # This verifies the displayed identity, not finitely many values of h.
        def term(i=0, j=0, coefficient=1):
            return {(i, j): coefficient}

        def add(*polys):
            result = Counter()
            for p in polys:
                result.update(p)
            return {key: value for key, value in result.items() if value}

        def mul(*polys):
            result = term()
            for p in polys:
                out = Counter()
                for (i, j), a in result.items():
                    for (k, l), b in p.items():
                        out[i + k, j + l] += a * b
                result = {key: value for key, value in out.items() if value}
            return result

        def invert(p):
            return {(-i, -j): c for (i, j), c in p.items()}

        one, z, r = term(), term(1), term(0, 1)
        t1 = add(z, term(0, 8, -1),
                 mul(term(0, 1, -2), add(one, r), add(one, term(-1, 4)),
                     add(z, term(0, 1, -1))))
        t2 = add(z, term(1, 4, -1),
                 mul(term(0, 1, -2), add(one, term(0, 2)), add(one, term(1, 1, -1))))
        t3 = add(term(1, 0, -1), term(1, 2), term(1, 1, 2), term(0, 2, -2))
        residual = add(
            mul(term(0, 0, -1), add(one, term(1, 0, -1)),
                add(one, term(-1, 8, -1), term(0, 4, -1), term(0, 2, -1))),
            mul(t1, add(one, term(0, 4, -1), term(0, 2, -1))),
            mul(t2, add(one, term(-1, 8, -1), term(0, 2, -1))),
            mul(t3, add(one, term(-1, 8, -1), term(0, 4, -1))),
            mul(term(0, 8), invert(t1)), mul(term(1, 4), invert(t2)),
            mul(term(1, 2), invert(t3)))
        self.assertEqual(residual, {})
        # Odd t omits the long-arm leaf, leaving lengths 8h+2, 4h+2, 2h+1.
        a = add(z, term(3, 8, -1),
                mul(term(1, 1, -2), add(one, r), add(one, term(0, 4)),
                    add(z, term(0, 1, -1))))
        b = add(term(1, 0, -1), term(3, 4),
                mul(term(0, 0, 2), add(one, term(1, 2)), add(z, term(0, 1, -1))))
        c = add(term(1, 0, -1), term(2, 2),
                mul(term(1, 1, 2), add(z, term(0, 1, -1))))
        odd_residual = add(
            mul(term(0, 0, -1), add(one, term(1, 0, -1)),
                add(one, term(2, 8, -1), term(2, 4, -1), term(1, 2, -1))),
            mul(a, add(one, term(2, 4, -1), term(1, 2, -1))),
            mul(b, add(one, term(2, 8, -1), term(1, 2, -1))),
            mul(c, add(one, term(2, 8, -1), term(2, 4, -1))),
            mul(term(3, 8), invert(a)), mul(term(3, 4), invert(b)),
            mul(term(2, 2), invert(c)))
        self.assertEqual(odd_residual, {})


if __name__ == "__main__":
    unittest.main()
