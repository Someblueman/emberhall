"""Independent original-tree counts for the complete folded transfer."""
from collections import Counter, deque
from itertools import combinations, product
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import word_frontier as frontier


def graph_data(lengths):
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    vertices = [v for v in graph if v not in ((1, 1), (2, 1))]
    pairs = []
    for index, source in enumerate(vertices):
        distance, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for other in graph[vertex]:
                if other not in distance:
                    distance[other] = distance[vertex] + 1
                    queue.append(other)
        pairs.extend((index, j, distance[other])
                     for j, other in enumerate(vertices) if j > index)
    return vertices, pairs


def profile(signs, pairs):
    result = Counter()
    for i, j, distance in pairs:
        result[distance] += (signs[i] + signs[j]) // 2
    return result


def graph_census(lengths):
    vertices, pairs = graph_data(lengths)
    count, example = 0, None
    for tail in product((-1, 1), repeat=len(vertices) - 1):
        signs = (1,) + tail
        if not sum(signs) and not any(profile(signs, pairs).values()):
            count += 1
            example = dict(zip(vertices, signs))
    return count, example


def certificate(lengths, signs):
    saved = {"format": "tripod-word-completion-v1", "lengths": list(lengths), "centre": signs[(0, 0)]}
    for arm, length in enumerate(lengths, 1):
        saved[f"arm{arm}"] = "".join("+" if signs[(arm, d)] == 1 else "-"
                                     for d in range(2 if arm < 3 else 1, length + 1))
    return saved


class FrontierTests(unittest.TestCase):
    def test_complete_transfer_matches_all_graph_colourings(self):
        cases = ((3, 2, 1), (4, 2, 1), (4, 3, 1), (5, 3, 2), (6, 4, 3),
                 (7, 4, 2), (5, 4, 2), (9, 4, 2), (7, 5, 2), (6, 5, 4))
        for lengths in cases:
            with self.subTest(lengths=lengths):
                count, _ = graph_census(lengths)
                answer = frontier.solve(frontier.build_system(lengths))
                self.assertEqual(answer["status"], "exact")
                self.assertEqual(answer["colourings_up_to_reversal"], count)
                self.assertEqual(answer["exists"], bool(count))

    def test_every_polynomial_coefficient_against_bfs(self):
        rng = random.Random(127)
        for lengths in ((4, 2, 1), (7, 5, 3), (8, 6, 5)):
            vertices, pairs = graph_data(lengths)
            system = frontier.build_system(lengths)
            for _ in range(25):
                values = [rng.choice((-1, 1)) for _ in vertices]
                delta = profile(values, pairs)
                signs = dict(zip(vertices, values))
                actual = {degree: sum(coef * signs[system.vertices[i]] for i, coef in row.items())
                          for degree, row in system.rows.items()}
                expected = {degree: 2 * (delta[degree + 1] - delta[degree])
                            - (2 * sum(values) if degree == 0 else 0)
                            for degree in range(sum(lengths[:2]) + 1)}
                self.assertEqual({k: v for k, v in actual.items() if v},
                                 {k: v for k, v in expected.items() if v})

    def test_bound_including_small_lengths_and_colliding_terms(self):
        for a, b, c in combinations(range(1, 10), 3):
            report = frontier.describe(frontier.build_system((c, b, a)))
            self.assertLessEqual(report["assignment_width"], report["uniform_width_bound"])
        reports = [frontier.describe(frontier.build_system((c + 216, c + 56, c)))
                   for c in (11, 57, 113, 545, 7571)]
        self.assertEqual({r["uniform_width_bound"] for r in reports}, {3546})
        self.assertEqual(reports[-1]["variables"], 22984)
        self.assertEqual(reports[-1]["assignment_width"], 1141)
        system = frontier.build_system((7787, 7627, 7571))
        for degree, row in system.rows.items():
            residue = degree % 7571
            folded = min(residue, 7571 - residue)
            self.assertTrue(all(abs(system.layers[i] - folded) <= 272 for i in row))

    def test_accept_and_reject_literal_certificates(self):
        lengths = (4, 2, 1)
        count, signs = graph_census(lengths)
        self.assertGreater(count, 0)
        saved = certificate(lengths, signs)
        self.assertTrue(frontier.verify(saved)["valid"])
        self.assertTrue(frontier.verify(saved, audit_graph=True)["graph_audit"]["distance_multiplicities_equal"])
        saved["arm1"] = ("+" if saved["arm1"][0] == "-" else "-") + saved["arm1"][1:]
        with self.assertRaisesRegex(ValueError, "nonzero"):
            frontier.verify(saved)

    def test_resource_refusal_is_not_a_negative_result(self):
        system = frontier.build_system((7, 4, 2))
        for limits in ({"max_width": 0}, {"max_states": 1}):
            report = frontier.solve(system, **limits)
            self.assertEqual(report["status"], "resource_limit")
            self.assertFalse(report["existence_decided"])
            self.assertNotIn("exists", report)

    def test_validation_and_cli(self):
        for bad in ((3, 3, 1), (3, 2, 0), (3, 2, True), (3, 2)):
            with self.assertRaises(ValueError):
                frontier.build_system(bad)
        command = [sys.executable, str(Path(frontier.__file__))]
        result = subprocess.run(command + ["--lengths", "7", "4", "2", "--solve", "--max-width", "0"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["existence_decided"])
        _, signs = graph_census((4, 2, 1))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "certificate.json"
            path.write_text(json.dumps(certificate((4, 2, 1), signs)))
            result = subprocess.run(command + ["--verify", str(path), "--audit-graph"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            saved = json.loads(path.read_text())
            saved["centre"] = True
            path.write_text(json.dumps(saved))
            result = subprocess.run(command + ["--verify", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
