"""Fresh graph-distance checks, separate from the Laurent proof."""
from collections import Counter, deque
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import next_family as nf
import published_cases as pc


def distances(lengths):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    result = {}
    for source in graph:
        seen, queue = {source: 0}, deque([source])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1
                    queue.append(v)
        result[source] = seen
    return result


def counts(vertices, metric):
    return Counter(metric[u][v] for i, u in enumerate(vertices) for v in vertices[i + 1:])


class NextFamilyTest(unittest.TestCase):
    def test_symbolic_identities_use_independent_indeterminates(self):
        for parity in (0, 1):
            self.assertEqual(nf.even_symbolic_residual(parity), ({}, (0, 0)))
        for remainder in range(4):
            self.assertEqual(nf.odd_symbolic_residual(remainder), ({}, (0, 0)))
        self.assertEqual(nf.partition_certificate(), {(0, 0): 2, (1, 3): 2, (2, 1): 2})

    def test_fresh_unequal_triples_by_breadth_first_search(self):
        for t in (2, 3, 4, 5, 7, 9, 11, 14, 17, 22, 23, 29):
            with self.subTest(t=t):
                result = nf.family_witness(t)
                left, right = result["left"], result["right"]
                metric = distances(result["lengths"])
                self.assertEqual(len(left), 21 * t // 2)
                self.assertEqual(len(right), len(left))
                self.assertFalse(set(left) & set(right))
                omitted = {(1, 10 * t)} | ({(1, 10 * t - 1)} if t % 2 else set())
                self.assertEqual(set(metric) - set(left) - set(right), omitted)
                lp, rp = counts(left, metric), counts(right, metric)
                self.assertEqual(lp, rp)
                self.assertEqual(sum(lp.values()), len(left) * (len(left) - 1) // 2)
                self.assertEqual(lp, result["left_profile"])

    def test_certificate_against_full_shells_not_retained_shells(self):
        rng = random.Random(577)
        for t in (1, 2, 3, 7, 11):
            metric = distances((10 * t, 7 * t, 4 * t))
            vertices = list(metric)
            rng.shuffle(vertices)
            values = [1, -1] * (len(vertices) // 2) + [0] * (len(vertices) % 2)
            signs = dict(zip(vertices, values))
            shells = Counter()
            for u in vertices:
                for v, distance in metric[u].items():
                    if distance:
                        shells[distance] += signs[u]
            lhs = sum(w * (shells[j * t + 1] - shells[j * t])
                      for j, w in enumerate(nf.WEIGHTS))
            rhs = 2 * (signs[0, 0] + signs[1, 3 * t] + signs[2, t])
            self.assertEqual(lhs, rhs)

    def test_altered_equal_sized_disjoint_pair_rejected(self):
        for t in (14, 17):
            result = nf.family_witness(t)
            left = list(result["left"])
            left[left.index((0, 0))] = (1, 10 * t)
            self.assertFalse(pc.check_pair(result["lengths"], left, result["right"])["homometric"])

    def test_input_boundaries_are_explicit(self):
        for value in (0, -2, True, 2.0, 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                nf.family_witness(value)

    def test_cli_proof_and_witness_round_trip(self):
        script = str(Path(nf.__file__))
        proof = subprocess.run([sys.executable, script, "--prove"],
                               text=True, capture_output=True, check=True)
        self.assertIn("PASS", proof.stdout)
        run = subprocess.run([sys.executable, script, "12"],
                             text=True, capture_output=True, check=True)
        result = json.loads(run.stdout)
        checked = subprocess.run([sys.executable, str(Path(pc.__file__)), "--check", "-"],
                                 input=run.stdout, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(result["size"], 126)
        self.assertEqual(result["target"], 125)
        odd = subprocess.run([sys.executable, script, "11", "--summary"],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(odd.stdout)["size"], 115)


if __name__ == "__main__":
    unittest.main()
