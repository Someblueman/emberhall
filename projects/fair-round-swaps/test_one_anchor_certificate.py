"""Literal EF1 and original-anchor checks for the constructive bridge."""

from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
from random import Random
import json
import subprocess
import sys
import unittest

from one_anchor_certificate import (canonical_endpoints, crossing, example,
                                    one_anchor_bridge)


def fair(u, state):
    bundles = [[g for g, a in enumerate(state) if a == i] for i in range(len(u))]
    return all(any(sum(row[g] for g in own) >= sum(row[g] for g in other if g != h)
                   for h in other) for row, own in zip(u, bundles) for other in bundles)


def check(test, u, start, target):
    r = len(u) - 2
    route = one_anchor_bridge(u, start, target)
    test.assertEqual((route[0], route[-1]), (start, target))
    test.assertLessEqual(len(route) - 1, 2 * r + 3)
    for state in route:
        test.assertTrue(fair(u, state))
        test.assertEqual(tuple(state.count(i) for i in range(r + 2)), (2,) * r + (1, 1))
        test.assertIn(state[0], (r, r + 1))
        test.assertLessEqual(sum(state[d + 1] != d for d in range(r)), 1)
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(len(a)) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertEqual((a[x], a[y]), (b[y], b[x]))
    return route


class OneAnchorTests(unittest.TestCase):
    def test_all_weak_orders_for_one_double(self):
        orders = [row for row in product(range(4), repeat=4)
                  if set(row) == set(range(max(row) + 1))]
        self.assertEqual(len(orders), 75)
        doubles = [row for row in orders if row[1] >= max(row[2:])]
        first = [row for row in orders if row[0] == max(row) and row[2] >= row[3]]
        second = [row for row in orders if row[0] == max(row) and row[3] >= row[2]]
        count = 0
        for u in product(doubles, first, second):
            check(self, u, *canonical_endpoints(1))
            count += 1
        print(f"complete one-double weak-order triples: {count}")

    def test_all_attachment_cases_and_rational_profiles(self):
        rng = Random(20261120111)
        cases, total, nonserial = Counter(), 0, 0
        for r in range(2, 16):
            for trial in range(30):
                u = example(r, rng.randrange(10**9))
                # Row-specific exact affine refinements retain all hypotheses.
                u = tuple(tuple(Fraction(v, 7) + Fraction(i, 13) for v in row)
                          for i, row in enumerate(u))
                start, target = canonical_endpoints(r)
                check(self, u, start, target)
                nonserial += any(u[d][d + 1] < u[d][g] for d in range(r)
                                 for g in range(d + 2, 2 * r + 2))
                common, t, pivot, q = crossing(u)
                for current in (start, target):
                    active = 2 * r + 1 - current[0]
                    z = current.index(active)
                    if pivot is None:
                        kind = "tail"
                    elif common[z] == pivot:
                        kind = "direct"
                    else:
                        kind = "via-q" if u[active][q] >= u[active][t] else "via-p"
                    cases[kind] += 1
                total += 1
        self.assertEqual(set(cases), {"tail", "direct", "via-q", "via-p"})
        self.assertGreater(nonserial, 0)
        print(f"rational bridges: {total}; nonserial: {nonserial}; attachment cases: {dict(cases)}")

    def test_ties_reversed_owners_and_arbitrary_tail_assignments(self):
        rng = Random(20261120112)
        for r in (1, 2, 3, 5, 10):
            for case in range(10):
                u = example(r, case) if case else ((0,) * (2 * r + 2),) * (r + 2)
                start, target = canonical_endpoints(r)
                for state in (start, target):
                    active = 2 * r + 1 - state[0]
                    z = state.index(active)
                    tails = [g for g in range(r + 1, 2 * r + 2) if g != z]
                    shuffled = [state[g] for g in tails]
                    rng.shuffle(shuffled)
                    changed = list(state)
                    for g, owner in zip(tails, shuffled):
                        changed[g] = owner
                    if state == start:
                        start = tuple(changed)
                    else:
                        target = tuple(changed)
                check(self, u, target, start)

    def test_frozen_path_cover_countermodel(self):
        rows = (
            "132/149 11/596 11/596 11/596 11/596 11/596 1/596 1/149 0 0 3/298 1/298",
            "259/298 5/596 15/596 5/596 15/596 15/596 1/596 0 2/149 3/596 5/596 3/298",
            "3/4 33/596 33/596 23/596 5/298 9/596 13/596 1/298 5/596 1/149 9/596 2/149",
            "521/596 3/596 3/596 3/596 5/149 5/149 1/596 3/149 7/596 1/298 1/149 0",
            "245/298 5/149 5/149 5/149 5/149 3/149 1/298 1/149 0 7/596 1/596 0",
            "107/1192 93/1192 107/1192 97/1192 103/1192 91/1192 105/1192 89/1192 105/1192 95/1192 101/1192 99/1192",
            "323/3576 281/3576 299/3576 305/3576 293/3576 317/3576 269/3576 323/3576 287/3576 311/3576 275/3576 293/3576",
        )
        u = tuple(tuple(map(Fraction, row.split())) for row in rows)
        self.assertTrue(all(sum(row) == 1 for row in u))
        route = check(self, u, *canonical_endpoints(5))
        print(f"frozen 1001-path-cover countermodel: {len(route) - 1} constructive exchanges")

    def test_failures_and_real_command(self):
        with self.assertRaises(ValueError):
            canonical_endpoints(0)
        u = example(2)
        start, target = canonical_endpoints(2)
        with self.assertRaisesRegex(ValueError, "different carriers"):
            one_anchor_bridge(u, start, start)
        changed = [list(row) for row in u]
        changed[0][1] = 0
        with self.assertRaisesRegex(ValueError, "dominate"):
            one_anchor_bridge(tuple(map(tuple, changed)), start, target)
        changed = [list(row) for row in u]
        changed[2][0] = 0
        with self.assertRaisesRegex(ValueError, "shared favorite"):
            one_anchor_bridge(tuple(map(tuple, changed)), start, target)
        command = subprocess.run([sys.executable, "-S", str(Path(__file__).with_name("one_anchor_certificate.py"))],
                                 text=True, capture_output=True, check=True)
        output = json.loads(command.stdout)
        self.assertLessEqual(output["exchanges"], output["bound"])
        self.assertLessEqual(output["maximum_anchors_away"], 1)


if __name__ == "__main__":
    unittest.main()
