"""Independent graph controls for the exact two-word completion theorem."""
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import word_realizability as word


def graph(lengths):
    adjacency = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            adjacency[vertex] = [previous]
            adjacency[previous].append(vertex)
            previous = vertex
    distances = {}
    for source in adjacency:
        row, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for other in adjacency[vertex]:
                if other not in row:
                    row[other] = row[vertex] + 1
                    queue.append(other)
        distances[source] = row
    return distances


def assignment(lengths, centre, words):
    result = {(0, 0): centre}
    for arm, text in enumerate(words, 1):
        result.update({(arm, d): 1 if s == "+" else -1
                       for d, s in enumerate(text, 1 if arm == 3 else 2)})
    return result


def homometric(signs, distances):
    groups = [[v for v, s in signs.items() if s == sign] for sign in (1, -1)]
    profiles = [Counter(distances[u][v] for u, v in combinations(group, 2))
                for group in groups]
    return len(groups[0]) == len(groups[1]) and profiles[0] == profiles[1]


class WordTests(unittest.TestCase):
    def test_iff_and_uniqueness_against_every_graph_colouring(self):
        # All three words are enumerated by the independent oracle. The
        # reduction receives only the two shorter words, with centre fixed +.
        for lengths in ((4, 3, 2), (5, 3, 1), (6, 3, 2), (7, 4, 2)):
            a, b, c = lengths
            distances = graph(lengths)
            for suffix in product("+-", repeat=b - 1 + c):
                arm2, arm3 = "".join(suffix[:b - 1]), "".join(suffix[b - 1:])
                expected = []
                for prefix in product("+-", repeat=a - 1):
                    arm1 = "".join(prefix)
                    signs = assignment(lengths, 1, (arm1, arm2, arm3))
                    if homometric(signs, distances):
                        expected.append(arm1)
                self.assertLessEqual(len(expected), 1)
                try:
                    result = word.complete(lengths, 1, arm2, arm3)
                except ValueError:
                    self.assertEqual(expected, [])
                else:
                    self.assertEqual(expected, [result["arm1"]])

    def test_full_shell_against_original_bfs_including_unbalanced_words(self):
        rng = random.Random(7351)
        for lengths in ((4, 3, 2), (13, 8, 5), (21, 12, 7)):
            distances = graph(lengths)
            for _ in range(15):
                words = ["".join(rng.choice("+-") for _ in range(n - (i < 2)))
                         for i, n in enumerate(lengths)]
                centre = rng.choice((-1, 1))
                signs = assignment(lengths, centre, words)
                expected = Counter({0: -2 * sum(signs.values())})
                for u, v in combinations(signs, 2):
                    distance, value = distances[u][v], signs[u] + signs[v]
                    expected[distance - 1] += value
                    expected[distance] -= value
                actual = word.shell_polynomial(lengths, centre,
                    [[1 if s == "+" else -1 for s in text] for text in words])
                self.assertEqual(actual, {d: v for d, v in expected.items() if v})

    def test_frontier_fixed_width_kernel_and_phi3(self):
        rng = random.Random(954)
        for t in (1, 2, 17):
            a, b, c = (n + 7560 * t for n in (227, 67, 11))
            denominator, _ = word.reduction((a, b, c), 1, "-" * (b - 1), "+" * c)
            expected = {}
            low = {0: 1, 1: -1, 3: -1, 56: 1, 57: -1, 59: -1}
            for d, v in low.items():
                expected[d] = v
                expected[2 * b + 4 - d] = v
            expected[c + 2] = expected[2 * b - c + 2] = 1
            for d, v in enumerate((-1, 1, -1, 4, -1, 1, -1), b - 1):
                expected[d] = v
            self.assertEqual(denominator, expected)
            self.assertEqual(len(denominator), 21)
            self.assertEqual({d: v for d, v in denominator.items() if d < c + 2}, low)
        lengths = (227, 67, 11)
        for _ in range(15):
            signs = [[rng.choice((-1, 1)) for _ in range(n - (i < 2))]
                     for i, n in enumerate(lengths)]
            poly = word.shell_polynomial(lengths, 1, signs)
            residue = [sum(v for d, v in poly.items() if d % 3 == r) for r in range(3)]
            chi = sum(s * (1 if d % 3 == 1 else -1 if d % 3 == 0 else 0)
                      for d, s in enumerate(signs[2], 1))
            self.assertEqual(residue[1] - residue[2], 3 * (1 - chi))

    def test_positive_family_and_sign_complement(self):
        for k in (0, 1, 4, 17):
            saved = word.control(k)
            self.assertEqual(saved["arm1"], "--++" * (k + 1))
            audit = word.graph_audit(saved)
            self.assertEqual(audit["size"], 5 + 2 * k)
            other = word.complete(saved["lengths"], -1, "+++", "--")
            self.assertEqual(other["arm1"], "++--" * (k + 1))
        lo, hi = Fraction(682327803828, 10**12), Fraction(682327803829, 10**12)
        self.assertLess(lo**3 + lo - 1, 0)
        self.assertGreater(hi**3 + hi - 1, 0)
        # All a,b,c exceed 100 on t>=1. This deliberately looser bound
        # controls every suppressed term without giant rational powers.
        bound = 2 * hi**56 / (1 - hi) + 3 * hi**100 + 6 * hi**100 / (1 - hi)
        self.assertLess(bound, Fraction(32, 10**10))

    def test_seven_sign_obstruction_is_exact_for_first_four_coefficients(self):
        excluded = 0
        for boundary in product((-1, 1), repeat=7):
            y1, y2, y3, z3, z2, z1, z0 = boundary
            text = "".join("+" if s == 1 else "-" for s in boundary)
            verdict = word.boundary_obstruction((13, 11, 7), text)
            possible = False
            for s, x2, x3, x4, x5 in product((-1, 1), repeat=5):
                q = (-s-x2-z0, s-x3-y1-z0-z1,
                     s-x4+y1-y2-z0-z1-z2,
                     -x5+y1+y2-y3-2*z0-z1-z2-z3)
                possible |= all(v in (-1, 1) for v in q)
                # Independent numerator construction, including endpoints.
                arm2 = "".join("+" if x == 1 else "-" for x in
                               (x2, x3, x4, x5)) + "+" * 6
                denominator, numerator = word.reduction((13, 11, 7), s, arm2, text)
                coefficients = {}
                for n in range(6):
                    coefficients[n] = numerator.get(n, 0) - sum(
                        v * coefficients.get(n-d, 0) for d, v in denominator.items() if 0 < d <= n)
                self.assertEqual(tuple(coefficients[n] for n in range(2, 6)), q)
            self.assertEqual(verdict["excluded"], not possible)
            excluded += not possible
        self.assertEqual(excluded, 48)
        self.assertEqual(word.boundary_table()["excluded_patterns"], 48)

    def test_changed_certificate_and_malformed_input_rejected(self):
        saved = word.control(1)
        for key, value in (("arm1", "+" + saved["arm1"][1:]),
                           ("arm2", "+--"), ("centre", True),
                           ("format", "untrusted"), ("lengths", [9, 4, True])):
            with self.assertRaises(ValueError):
                word.verify_certificate(dict(saved, **{key: value}))
        with self.assertRaises(ValueError):
            word.verify_certificate(dict(saved, valid=True))
        with self.assertRaises(ValueError):
            word.complete((5, 4, 2), 1, "00-", "++")
        with self.assertRaises(ValueError):
            word.graph_audit(saved, max_vertices=2)

    def test_transfer_count_against_all_fifteen_bit_boundaries(self):
        admitted = 0
        for bits in product("+-", repeat=15):
            text = "".join(bits)
            outcomes = [word.prefix_transfer(text, centre, shells=8) for centre in (-1, 1)]
            self.assertLessEqual(sum(outcomes), 1)
            admitted += any(outcomes)
        self.assertEqual(admitted, word.transfer_count(8)["patterns_not_excluded"])
        full = word.transfer_count()
        self.assertEqual(full["patterns_not_excluded"], 66902297797678953520198)
        self.assertEqual(full["live_states_per_centre"], 54)

    def test_transfer_really_realizes_both_end_shells(self):
        states = {(-1-tip, 0, 0, 1): ([], [tip]) for tip in (-1, 1)}
        for _ in range(55):
            following = {}
            for (u, v, w, previous), (prefix, tips) in states.items():
                for current, tip in product((-1, 1), repeat=2):
                    value = u+w+2*previous-current-tip
                    if value in (-2, 0, 2):
                        following[value, u, v, current] = (prefix+[current], tips+[tip])
            states = following
        prefix, tips = next(iter(states.values()))
        signs3 = prefix + list(reversed(tips))
        text = "".join("+" if s == 1 else "-" for s in signs3)
        self.assertTrue(word.prefix_transfer(text, 1))
        lengths = (200, 170, 111)
        a, b, c = lengths
        signs1, signs2 = [1]*(a-1), [1]*(b-1)
        sums = [0, 0]
        for n in range(2, 58):
            previous = 0 if n == 2 else 1 if n == 3 else signs3[n-4]
            current = 1 if n == 2 else signs3[n-3]
            value = sums[n-1] + (sums[n-3] if n >= 3 else 0)
            value += 2*previous-current-signs3[-(n-1)]
            sums.append(value)
            signs1[n-2], signs2[n-2] = {2: (1, 1), 0: (1, -1), -2: (-1, -1)}[value]
        for r in range(56):
            signs1[a-r-2], signs2[b-r-2] = 1, -1
        poly = word.shell_polynomial(lengths, 1, (signs1, signs2, signs3))
        self.assertTrue(poly)  # Local feasibility is not full homometry.
        self.assertTrue(all(poly.get(d, 0) == 0 for d in range(56)))
        self.assertTrue(all(poly.get(a+b-r, 0) == 0 for r in range(56)))

    def test_short_arm_infinite_certificate_by_polynomial_division(self):
        histogram = Counter()
        for bits in product((-1, 1), repeat=11):
            # Expand z^2(2z-1)(1+Z)-z^13-z^2 R3 independently.
            forcing = Counter({3: 2, 2: -1, 13: -1})
            for depth, value in enumerate(bits, 1):
                forcing[depth+3] += 2*value
                forcing[depth+2] -= value
                forcing[13-depth] -= value
            quotient = [0]*23
            for n in range(2, 23):
                quotient[n] = forcing[n] + quotient[n-1]
                if n >= 3:
                    quotient[n] += quotient[n-3]
                if n >= 13:
                    quotient[n] -= quotient[n-13]
                if quotient[n] not in (-2, 0, 2):
                    histogram[n] += 1
                    break
            else:
                self.fail("an unexcluded shortest word invalidates the theorem")
        saved = word.short_arm_certificate()
        self.assertEqual(sorted(histogram.items()),
                         [tuple(x) for x in saved["first_failure_histogram"]])
        self.assertEqual(sum(histogram.values()), 2048)
        self.assertEqual(word.verify_short_arm_certificate(saved), saved)
        with self.assertRaises(ValueError):
            word.verify_short_arm_certificate(dict(saved, minimum_middle_length=31))
        with self.assertRaises(ValueError):
            word.verify_short_arm_certificate(dict(saved, all_hole_supports_excluded=True))

    def test_short_arm_low_equations_against_graph_at_domain_endpoint(self):
        lengths = (39, 32, 11)
        a, b, c = lengths
        distances = graph(lengths)
        rng = random.Random(219)
        for _ in range(12):
            words = [[rng.choice((-1, 1)) for _ in range(n-(i < 2))]
                     for i, n in enumerate(lengths)]
            for r in range(21):
                words[1][b-r-2] = -words[0][a-r-2]
            centre = rng.choice((-1, 1))
            texts = ["".join("+" if s == 1 else "-" for s in values) for values in words]
            signs = assignment(lengths, centre, texts)
            actual = Counter({0: -2*sum(signs.values())})
            for left, right in combinations(signs, 2):
                delta, value = distances[left][right], signs[left]+signs[right]
                actual[delta-1] += value
                actual[delta] -= value
            sums = [0, 0] + [x+y for x, y in zip(words[0], words[1])]
            def v(k):
                return centre if k == 0 else words[2][k-1] if 1 <= k <= c else 0
            for n in range(2, 23):
                expected = -sums[n]+sums[n-1]+(sums[n-3] if n >= 3 else 0)
                expected -= sums[n-13] if n >= 13 else 0
                expected += 2*v(n-3)-v(n-2)-centre*(n == 13)
                expected -= words[2][12-n] if n <= 12 else 0
                self.assertEqual(actual[n-2], expected)
            self.assertTrue(all(actual[a+b-r] == 0 for r in range(21)))

    def test_odd_gap_bound_and_analytic_coefficient_endpoints(self):
        rng = random.Random(1581)
        for c in (3, 5, 7, 11, 17):
            self.assertEqual(word.large_gap_bound(c)["minimum_middle_length"],
                             2*c+2+3**(c+2))
            for _ in range(10):
                signs = [rng.choice((-1, 1)) for _ in range(c)]
                centre = rng.choice((-1, 1))
                rest = Counter({2: -centre, 3: 2*centre, c+2: -centre})
                for d, value in enumerate(signs, 1):
                    rest[d+3] += 2*value
                    rest[d+2] -= value
                    rest[c-d+2] -= value
                self.assertEqual(sum(rest.values()), 0)
                self.assertEqual(rest[2], -centre-signs[-1])
                self.assertEqual(-rest[c+3], -2*signs[-1])
                self.assertEqual(-rest[c+2], -2*signs[-2]+signs[-1]+centre)
        for c in (1, 2, 4, True, 3.0):
            with self.assertRaises(ValueError):
                word.large_gap_bound(c)

    def test_real_cli_round_trip_and_changed_file(self):
        script = Path(word.__file__)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "certificate.json"
            command = [sys.executable, str(script)]
            run = subprocess.run(command + ["--control", "4", "--write", str(path),
                                           "--audit-graph"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["graph_audit"]["size"], 13)
            saved = json.loads(path.read_text())
            saved["arm1"] = "+" + saved["arm1"][1:]
            path.write_text(json.dumps(saved))
            run = subprocess.run(command + ["--check", str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertFalse(json.loads(run.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
