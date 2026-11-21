"""Independent original-tree counters and exact identities for the five-fold lift."""
from collections import Counter, deque
from itertools import combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import paired_edge_five as five


def graph_profile(lengths, vertices):
    """Literal BFS on the original tree; no polynomial or packing code."""
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length+1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    vertices = list(vertices)
    result = Counter()
    for i, source in enumerate(vertices):
        distances, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex]+1
                    queue.append(neighbor)
        result.update(distances[target] for target in vertices[i+1:])
    return result


class FiveConstructionTests(unittest.TestCase):
    def test_all_parameter_identities_and_corrupted_pattern(self):
        self.assertTrue(all(not p for p in five.proof_residuals().values()))
        blocks = list(five.EDGE_BLOCKS)
        blocks[0] = "-"+blocks[0][1:]
        self.assertTrue(any(five.proof_residuals(blocks).values()))

    def test_domain_and_all_eight_missing_classes(self):
        missing = [t for t in range(165) if t % 15 == 9 and t % 11 not in (1, 6, 9)]
        self.assertEqual(missing, [24, 54, 69, 84, 99, 114, 129, 159])
        for t in missing + [24+165*10**30]:
            k = five.parameter_k(t)
            self.assertEqual(tuple(30*k+n for n in five.TAIL_LENGTHS),
                             tuple(n+1064*t for n in (18, 14, 3)))
        for t in (-1, True, 0.5, 0, 1, 3, 165):
            with self.assertRaises(ValueError):
                five.parameter_k(t)
        for k in (-1, True, 1.2):
            with self.assertRaises(ValueError):
                five.build_pair(k)

    def test_positive_lifts_with_independent_original_tree_distances(self):
        for k in (0, 1, 3):
            pair = five.build_pair(k)
            left, right = five.validate_pair(pair["lengths"], pair["left"], pair["right"])
            self.assertEqual(len(left), 133+225*k)
            self.assertEqual(len(left), len(right))
            self.assertFalse(left & right)
            n = 1+sum(pair["lengths"])
            self.assertEqual(n-len(left)-len(right), 2)
            self.assertEqual(pair["omitted"], [(1, pair["lengths"][0]),
                                              (2, pair["lengths"][1])])
            expected = graph_profile(pair["lengths"], left)
            self.assertEqual(expected, graph_profile(pair["lengths"], right))
            actual = five.distance_profile(pair["lengths"], left)
            self.assertEqual(expected, Counter({d: c for d, c in enumerate(actual) if c}))
            self.assertTrue(five.check_pair(pair)["meets_target"])

    def test_packing_on_unrelated_triples_and_a_byte_boundary(self):
        for lengths in ((7, 5, 2), (4, 11, 3), (17, 3, 2), (255, 257, 2)):
            vertices = [(i, d) for i, n in enumerate(lengths, 1)
                        for d in range(1, n+1) if (d+i) % 3 != 1]
            vertices.append((0, 0))
            expected = graph_profile(lengths, vertices)
            actual = five.distance_profile(lengths, vertices)
            self.assertEqual(expected, Counter({d: c for d, c in enumerate(actual) if c}))

    def test_altered_pair_is_rejected_without_changing_sizes(self):
        pair = five.build_pair(0)
        pair["left"].remove((0, 0))
        pair["left"].append(pair["omitted"][0])
        result = five.check_pair(pair)
        self.assertEqual((result["size"], result["right_size"]), (133, 133))
        self.assertFalse(result["homometric"])
        self.assertIsNotNone(result["mismatch_distance"])

    def test_invalid_pair_boundaries(self):
        for lengths, left, right in (
            ((1, 1, 1), [(0, 0), (0, 0)], []),
            ((1, 1, 1), [(0, 0)], [(0, 0)]),
            ((1, 1, 1), [(1, 2)], []),
            ((1, True, 1), [], []),
        ):
            with self.assertRaises(ValueError):
                five.validate_pair(lengths, left, right)
        with self.assertRaises(ValueError):
            five.proof_residuals(["bad"]*3)

    def test_nonperiodic_counterexample_rejects_inherited_reduction(self):
        self.assertEqual(five.nonperiodic_residuals(), ({}, {}))
        # k=850 corresponds to h=4256 and the actually missing affine t=24.
        for k in (0, 2, 850):
            x, y = five.nonperiodic_rows(k)
            lengths = (54+30*k, 50+30*k, 39+30*k)
            self.assertEqual(tuple(map(len, x)), lengths)
            self.assertNotEqual(x[2][0], x[2][3])
            for first, second in ((x, y), (y, x)):
                residual = Counter()
                for arm, length in enumerate(lengths):
                    for edge, sign in enumerate(first[arm]):
                        value = 1 if sign == "+" else -1
                        residual[edge] += value
                        for other, endpoint in enumerate(lengths):
                            if other != arm:
                                residual[edge+endpoint] -= value
                    for edge, sign in enumerate(second[arm]):
                        residual[length-1-edge] -= 1 if sign == "+" else -1
                self.assertFalse(any(residual.values()))

    def test_real_cli_round_trip_and_refusal(self):
        script = str(Path(five.__file__))
        with TemporaryDirectory() as directory:
            path = Path(directory)/"pair.json"
            made = subprocess.run([sys.executable, script, "--base-k", "0", "--witness", str(path)],
                                  capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(made.stdout)["meets_target"])
            checked = subprocess.run([sys.executable, script, "--check", str(path)],
                                     capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(checked.stdout)["homometric"])
            pair = json.loads(path.read_text())
            pair["left"].remove([0, 0])
            pair["left"].append(pair["omitted"][0])
            path.write_text(json.dumps(pair))
            invalid = subprocess.run([sys.executable, script, "--check", str(path)],
                                     capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 1)
            self.assertFalse(json.loads(invalid.stdout)["homometric"])
        refusal = subprocess.run([sys.executable, script, "0"], capture_output=True, text=True)
        self.assertEqual(refusal.returncode, 2)
        self.assertIn("other cases are not ruled out", refusal.stderr)
        proof = subprocess.run([sys.executable, script, "--prove"], capture_output=True,
                               text=True, check=True)
        self.assertIn("every t=9 mod15", proof.stdout)


if __name__ == "__main__":
    unittest.main()
