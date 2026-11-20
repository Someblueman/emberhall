"""Independent finite semantics and corrupted-proof tests for reserved pairs."""

from copy import deepcopy
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

from reserved_completion import terminal_buffer
from reserved_three_pairs import (BooleanDiagrams, Formulas, Propagation, certificate, graph,
                                  reserved_path, verified_proof, verify_certificate)


def fair(u, state):
    bundles = [[g for g, a in enumerate(state) if a == i] for i in range(4)]
    return all(any(sum(row[g] for g in own) >= sum(row[g] for g in other if g != h)
                   for h in other) for row, own in zip(u, bundles) for other in bundles)


def check_path(test, u, start, singleton, anchors):
    path, witness = reserved_path(u, start, singleton, anchors)
    test.assertEqual(path[0], start)
    test.assertLessEqual(len(path), 630)
    sizes = tuple(start.count(i) for i in range(4))
    for state in path:
        test.assertTrue(fair(u, state))
        test.assertEqual(tuple(state.count(i) for i in range(4)), sizes)
    for a, b in zip(path, path[1:]):
        changed = [g for g in range(7) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((a[x], a[y]), (b[y], b[x]))
    test.assertEqual(tuple(i for i, _ in witness),
                     tuple(i for i, _ in anchors) + (singleton,) + tuple(i for i, _ in anchors))
    remaining, final = set(range(7)), [-1] * 7
    for i, g in witness:
        test.assertIn(g, remaining)
        test.assertTrue(all(u[i][g] >= u[i][h] for h in remaining))
        remaining.remove(g)
        final[g] = i
    test.assertEqual(tuple(final), path[-1])
    return len(path) - 1


class ReservedThreePairsTests(unittest.TestCase):
    def test_complete_graph_and_portable_proof(self):
        states, edges = graph()
        independent = set(permutations((0, 0, 1, 1, 2, 2, 3)))
        self.assertEqual(set(states), independent)
        self.assertEqual(len(states), 630)
        expected = set()
        index = {a: k for k, a in enumerate(states)}
        for a in independent:
            for x, y in combinations(range(7), 2):
                if a[x] == a[y]:
                    continue
                b = list(a)
                b[x], b[y] = b[y], b[x]
                expected.add(tuple(sorted((index[a], index[tuple(b)]))))
        self.assertEqual(set(edges), expected)
        self.assertEqual(len(edges), 5670)
        result = verified_proof()
        self.assertEqual(result["linear_lemmas"], 506)
        self.assertEqual(result["Boolean_lemmas"], 459)
        self.assertEqual(result["RUP_steps"], 7306)

    def test_arbitrary_rows_beyond_terminal_guards(self):
        u = ((8, 10, 1, 7, 2, 20, 0), (3, 11, 8, 9, 2, 20, 0),
             (0, 1, 10, 1, 1, 20, 1), (2, 1, 5, 7, 1, 9, 0))
        start, anchors = (3, 0, 0, 1, 1, 2, 2), ((2, 5), (0, 1), (1, 3))
        self.assertIsNone(terminal_buffer(u, start, 3, anchors))
        self.assertGreater(max(u[3][g] for g in (2, 4, 6)), u[3][0])
        check_path(self, u, start, 3, anchors)

    def test_selected_formula_premises_against_independent_meanings(self):
        data = certificate()
        states, edges = graph()
        model = Formulas(data["variables"], states, edges, data["premises"])
        units = model.clauses[-len(data["premises"]):]
        index = {a: k for k, a in enumerate(states)}
        rng = Random(20261120102)
        for case in range(20):
            u = tuple(tuple(rng.randrange(10) if case else 0 for _ in range(7)) for _ in range(4))
            fairness = [fair(u, a) for a in states]
            assigned_fair = [bool(rng.randrange(2)) for _ in states]
            reach = [bool(rng.randrange(2)) for _ in states]
            outcomes = set()
            def pick(t, remaining, owners):
                if t == 7:
                    outcomes.add(tuple(owners))
                    return
                agent = (0, 1, 2, 3, 0, 1, 2)[t]
                best = max(u[agent][g] for g in remaining)
                for g in remaining:
                    if u[agent][g] == best:
                        changed = owners[:]
                        changed[g] = agent
                        pick(t + 1, remaining - {g}, changed)
            pick(0, set(range(7)), [-1] * 7)
            expected = [v >= 0 for row in u for v in row]
            expected.extend(u[i][i] >= u[i][g] for i in range(3) for g in range(7)
                            if g != 6 and g not in range(i))
            for k, state in enumerate(states):
                expected.append(assigned_fair[k] == fairness[k])
                for x, y in combinations(range(7), 2):
                    if state[x] == state[y]:
                        continue
                    b = list(state)
                    b[x], b[y] = b[y], b[x]
                    j = index[tuple(b)]
                    if j > k:
                        expected.append(not (assigned_fair[k] and assigned_fair[j]) or reach[k] == reach[j])
                expected.append(state not in outcomes or not reach[k])
            root = index[(0, 1, 2, 0, 1, 2, 3)]
            expected.extend((assigned_fair[root], reach[root]))
            self.assertEqual(len(expected), 6975)
            values = {1: True}
            for k, spec in enumerate(data["variables"][1:], 2):
                kind = spec[0]
                if kind == "linear":
                    values[k] = sum(c * v for c, v in zip(spec[2], u[spec[1]])) >= 0
                elif kind in ("fair", "reach"):
                    values[k] = (assigned_fair if kind == "fair" else reach)[spec[1]]
                else:
                    args = [values[abs(v)] == (v > 0) for v in spec[1]]
                    values[k] = all(args) if kind == "and" else any(args) if kind == "or" else args[0] == args[1]
            for premise, unit in zip(data["premises"], units):
                self.assertEqual(len(unit), 1)
                self.assertEqual(values[abs(unit[0])] == (unit[0] > 0), expected[premise])

    def test_exact_paths_with_ties_and_arbitrary_labels(self):
        rng = Random(20261120101)
        outside = longest = 0
        for case in range(100):
            u = [[Fraction(rng.randrange(15), rng.choice((1, 2, 7))) for _ in range(7)]
                 for _ in range(4)]
            if case == 0:
                u = [[0] * 7 for _ in range(4)]
            singleton = rng.randrange(4)
            order = [a for a in range(4) if a != singleton]
            rng.shuffle(order)
            z = rng.randrange(7)
            remaining, start, anchors = set(range(7)) - {z}, [-1] * 7, []
            start[z] = singleton
            for a in order:
                p = max(remaining, key=lambda g: (u[a][g], g))
                start[p] = a
                anchors.append((a, p))
                remaining.remove(p)
            tails = sorted(remaining)
            rng.shuffle(tails)
            u[singleton][z] = 2
            for (a, p), t in zip(anchors, tails):
                start[t] = a
                if u[singleton][t] > 2:
                    u[singleton][p] = Fraction(rng.randrange(5), 2)
            u, start, anchors = tuple(map(tuple, u)), tuple(start), tuple(anchors)
            if terminal_buffer(u, start, singleton, anchors) is None:
                outside += 1
            longest = max(longest, check_path(self, u, start, singleton, anchors))
        self.assertGreater(outside, 0)
        print(f"reserved three-pair paths: 100; outside terminal guards: {outside}; longest: {longest}")

    def test_corrupted_certificates_are_rejected(self):
        original = certificate()
        bad = deepcopy(original)
        bad["states"][0][0] = 3
        with self.assertRaisesRegex(ValueError, "complete graph"):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad["premises"].append(6975)
        with self.assertRaisesRegex(ValueError, "premise index"):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad["theory"][0][1][0][1] = 0
        with self.assertRaisesRegex(ValueError, "positive multiplier"):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad["tautologies"][0] = []
        with self.assertRaisesRegex(ValueError, "tautology"):
            verify_certificate(bad)
        bad = deepcopy(original)
        bad["proof"] = []
        with self.assertRaisesRegex(ValueError, "empty clause"):
            verify_certificate(bad)

    def test_boolean_and_propagation_primitives(self):
        diagrams = BooleanDiagrams({5: ("and", (2, -3)), 6: ("or", (5, 4)), 7: ("iff", (6, 2))})
        for clause in combinations((2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7), 3):
            expected = True
            for a, b, c in product((False, True), repeat=3):
                values = {2: a, 3: b, 4: c, 5: a and not b}
                values[6] = values[5] or c
                values[7] = values[6] == a
                expected &= any(values[abs(v)] == (v > 0) for v in clause)
            self.assertEqual(diagrams.tautology(clause), expected)
        engine = Propagation()
        for clause in ((2, 3), (-2, 4), (-3, 4)):
            engine.add(clause)
        self.assertTrue(engine.contradiction((4,)))
        self.assertFalse(engine.contradiction((2,)))
        engine.add((-4,))
        self.assertTrue(engine.contradiction(()))

    def test_real_command_and_invalid_input(self):
        command = subprocess.run([sys.executable, "-S", str(Path(__file__).with_name("reserved_three_pairs.py"))],
                                 check=True, capture_output=True, text=True)
        self.assertIn('"status": "verified"', command.stdout)
        with self.assertRaises(ValueError):
            reserved_path(((1, 2, 3), (3, 2, 1)), (0, 1, 1), 0, ((1, 2),))
        with self.assertRaises(ValueError):
            reserved_path(((0,) * 7,) * 4, (0, 1, 2, 0, 1, 2, 3), 3, ((0, 1), (1, 0), (2, 2)))


if __name__ == "__main__":
    unittest.main()
