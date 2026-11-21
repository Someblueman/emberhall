"""Proof corruption, independent propositional checks, and actual lifted paths."""

import copy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random
import unittest

from five_agent_eight import EXAMPLE
from protected_linear_certificate import (BooleanDiagrams, Propagation, padded_bridge,
                                          protected_bridge, verify_certificate)
from test_five_agent_protected import fair, neighbors


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path(__file__).with_name("protected_linear_certificate.json").read_text())

    def test_complete_portable_certificate(self):
        stats = verify_certificate(self.data)
        self.assertEqual((stats["vertices"], stats["edges"]), (112, 241))
        self.assertEqual(stats["RUP_steps"], 9574)

    def test_reject_corrupt_mathematics(self):
        bad = copy.deepcopy(self.data)
        bad["theory"][0][1][0][1] += 1
        with self.assertRaisesRegex(ValueError, "does not sum"):
            verify_certificate(bad)
        bad = copy.deepcopy(self.data)
        bad["theory"][0][1][0][2] = 0
        with self.assertRaisesRegex(ValueError, "multiplier"):
            verify_certificate(bad)
        primitive = next(k for k, spec in enumerate(self.data["variables"], 1) if spec[0] == "linear")
        bad = copy.deepcopy(self.data)
        bad["tautologies"] = [[primitive]]
        with self.assertRaisesRegex(ValueError, "tautology is false"):
            verify_certificate(bad)
        bad = copy.deepcopy(self.data)
        bad["proof"] = [[]]
        with self.assertRaisesRegex(ValueError, "RUP step"):
            verify_certificate(bad)
        bad = copy.deepcopy(self.data)
        bad["proof"] = bad["proof"][:-1]
        with self.assertRaisesRegex(ValueError, "empty clause"):
            verify_certificate(bad)

    def test_reject_changed_graph_and_definitions(self):
        bad = copy.deepcopy(self.data)
        bad["edges"][0] = [0, 0]
        with self.assertRaisesRegex(ValueError, "exchange edge"):
            verify_certificate(bad)
        bad = copy.deepcopy(self.data)
        k = next(k for k, v in enumerate(bad["variables"]) if v[0] == "and")
        bad["variables"][k][1][0] = k + 1
        with self.assertRaisesRegex(ValueError, "literal"):
            verify_certificate(bad)

    def test_boolean_diagrams_against_truth_tables(self):
        rng = random.Random(2026112056)
        for _ in range(60):
            definitions = {}
            for k in range(5, 13):
                op = rng.choice(("and", "or", "iff"))
                args = tuple(rng.choice((-1, 1)) * rng.randrange(2, k) for _ in range(2))
                definitions[k] = op, args
            clause = tuple(rng.choice((-1, 1)) * rng.randrange(2, 13) for _ in range(3))
            def evaluate(lit, values):
                if lit < 0:
                    return not evaluate(-lit, values)
                if lit not in definitions:
                    return values[lit]
                op, args = definitions[lit]
                a, b = (evaluate(v, values) for v in args)
                return (a and b) if op == "and" else (a or b) if op == "or" else a == b
            expected = all(any(evaluate(v, dict(zip((2, 3, 4), assignment))) for v in clause)
                           for assignment in product((False, True), repeat=3))
            self.assertEqual(BooleanDiagrams(definitions).tautology(clause), expected)

    def test_watched_propagation_against_simple_set_expansion(self):
        rng = random.Random(2026112057)
        for _ in range(60):
            clauses = [tuple({rng.choice((-1, 1)) * rng.randrange(2, 7)
                              for _ in range(rng.randrange(1, 4))}) for _ in range(14)]
            checker = Propagation()
            for clause in clauses:
                checker.add(clause)
            for _ in range(8):
                query = tuple(rng.choice((-1, 1)) * rng.randrange(2, 7) for _ in range(2))
                values = {-v for v in query}
                while True:
                    if any(-v in values for v in values):
                        expected = True
                        break
                    unknown = [set(c) - {-v for v in values} for c in clauses if not set(c) & values]
                    if any(not c for c in unknown):
                        expected = True
                        break
                    expanded = values | {next(iter(c)) for c in unknown if len(c) == 1}
                    if expanded == values:
                        expected = False
                        break
                    values = expanded
                self.assertEqual(checker.contradiction(query), expected)

    def test_certified_routes_for_rationals_and_ties(self):
        rng = random.Random(2026112058)
        for trial in range(100):
            u = [[Fraction(rng.randrange(8), rng.choice((1, 3, 11))) if trial else 0
                  for _ in range(8)] for _ in range(5)]
            for i, h in enumerate((1, 2, 3)):
                u[i][h] = max(u[i][h:])
            for i, h in ((3, 4), (4, 5)):
                u[i][h] = max(u[i][4:])
                u[i][0] = max(u[i])
            route = protected_bridge(tuple(map(tuple, u)))
            self.assertLessEqual(len(route), 112)
            self.assertTrue(all(a[0] in (3, 4) and fair(u, a) for a in route))
            self.assertTrue(all(b in set(neighbors(a)) for a, b in zip(route, route[1:])))

    def test_thirteen_good_failure_is_repaired(self):
        u = [list(row) + [0] * 5 for row in EXAMPLE]
        for i in range(5):
            u[i][8 + i] = 2000
        for i in (3, 4):
            u[i][0] = u[i][10] = 1000
            u[i][11] = u[i][12] = 90
        prefix = tuple((i, 8 + i) for i in range(5))
        route = padded_bridge(tuple(map(tuple, u)), prefix, tuple(range(8)))
        self.assertTrue(all(fair(u, a) and a[8:] == (0, 1, 2, 3, 4) for a in route))
        self.assertTrue(all(b in set(neighbors(a)) for a, b in zip(route, route[1:])))

    def test_longer_prefixes_and_missing_dominance(self):
        for rounds in (2, 4, 7):
            u = [list(row) + [0] * (5 * rounds) for row in EXAMPLE]
            prefix = tuple((i, 8 + 5 * t + i) for t in range(rounds) for i in range(5))
            for t in range(rounds):
                for i in range(5):
                    u[i][8 + 5 * t + i] = 1000 * (rounds - t)
            route = padded_bridge(tuple(map(tuple, u)), prefix, tuple(range(8)))
            self.assertTrue(all(fair(u, a) and a[8:] == (0, 1, 2, 3, 4) * rounds for a in route))
        u = [list(row) + [0] * 5 for row in EXAMPLE]
        for i in range(5):
            u[i][8 + i] = 1000
        u[3][12] = 2000
        prefix = ((0, 8), (1, 9), (2, 10), (4, 12), (3, 11))
        with self.assertRaisesRegex(ValueError, "dominance"):
            padded_bridge(tuple(map(tuple, u)), prefix, tuple(range(8)))

    def test_padding_rejects_negative_aliases_and_wrong_sizes(self):
        seven = tuple(row[:7] for row in EXAMPLE)
        with self.assertRaisesRegex(ValueError, "shape"):
            padded_bridge(seven, (), (-1,) + tuple(range(7)))
        with self.assertRaisesRegex(ValueError, "shape"):
            padded_bridge(EXAMPLE, (), (-1,) + tuple(range(1, 8)))
        with self.assertRaisesRegex(ValueError, "shape"):
            padded_bridge(EXAMPLE, ((0, 0),), tuple(range(8)))


if __name__ == "__main__":
    unittest.main()
