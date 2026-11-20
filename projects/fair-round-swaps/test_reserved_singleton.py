"""Independent deletion/order checks for the local result and retained flaws."""

from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

from reserved_singleton import (LOSS_ANCHORS, LOSS_PROFILE, LOSS_START, LOSS_STRICT_PROFILE,
                                improve, pair_obstruction, validate_reserved)


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(len(u))]
    for i, row in enumerate(u):
        own = sum(row[g] for g in bundles[i])
        for b in bundles:
            if b and not any(own >= sum(row[g] for g in b if g != removed)
                             for removed in b):
                return False
    return True


def check_route(test, u, route, singleton):
    sizes = tuple(route[0].count(i) for i in range(len(u)))
    before = u[singleton][route[0].index(singleton)]
    for a in route:
        test.assertTrue(fair(u, a))
        test.assertEqual(tuple(a.count(i) for i in range(len(u))), sizes)
        test.assertGreaterEqual(u[singleton][a.index(singleton)], before)
    for a, b in zip(route, route[1:]):
        changed = [g for g in range(len(a)) if a[g] != b[g]]
        test.assertEqual(len(changed), 2)
        x, y = changed
        test.assertNotEqual(a[x], a[y])
        test.assertEqual((a[x], a[y]), (b[y], b[x]))


def has_anchors(u, a, singleton):
    """Enumerate all anchor choices/order, without the production validator."""
    others = [i for i in range(len(u)) if i != singleton]
    for order in permutations(others):
        for chosen in product(*([g for g, owner in enumerate(a) if owner == i]
                                 for i in order)):
            remaining = set(range(len(a))) - {a.index(singleton)}
            for i, g in zip(order, chosen):
                if any(u[i][h] > u[i][g] for h in remaining):
                    break
                remaining.remove(g)
            else:
                return True
    return False


class ReservedSingletonTests(unittest.TestCase):
    def test_blocked_tail_uses_later_anchor(self):
        u = ((9, 15, 3, 3, 12), (18, 3, 6, 5, 0), (12, 6, 12, 1, 0))
        start = (0, 2, 1, 2, 1)
        # Taking the best tail gives the last double value 7 against a
        # pair with both goods worth 12. Its old anchor is a safe repair.
        self.assertFalse(fair(u, (1, 2, 1, 2, 0)))
        route, branch = improve(u, start, 0, ((1, 2), (2, 1)))
        self.assertEqual(branch, "blocking-anchor")
        self.assertEqual(route, [start, (2, 0, 1, 2, 1)])
        check_route(self, u, route, 0)

    def test_generated_certified_inputs(self):
        rng = Random(20261120081)
        counts = {}
        tested = 0
        for n in range(2, 13):
            m = 2 * n - 1
            for case in range(150):
                u = tuple(tuple(Fraction(rng.randrange(7), rng.choice((1, 1, 3)))
                                for _ in range(m)) for _ in range(n))
                if case == 0:
                    u = tuple((0,) * m for _ in range(n))
                singleton = rng.randrange(n)
                z = rng.randrange(m)
                order = [i for i in range(n) if i != singleton]
                rng.shuffle(order)
                remaining = set(range(m)) - {z}
                owners = [-1] * m
                owners[z] = singleton
                anchors = []
                for i in order:
                    best = max(u[i][g] for g in remaining)
                    g = rng.choice(sorted(g for g in remaining if u[i][g] == best))
                    remaining.remove(g)
                    owners[g] = i
                    anchors.append((i, g))
                tails = list(remaining)
                rng.shuffle(tails)
                for i, g in zip(order, tails):
                    owners[g] = i
                owners = tuple(owners)
                if not fair(u, owners):
                    continue
                route, branch = improve(u, owners, singleton, tuple(anchors))
                check_route(self, u, route, singleton)
                self.assertLessEqual(len(route), 3)
                if branch != "favorite":
                    self.assertGreater(u[singleton][route[-1].index(singleton)],
                                       u[singleton][z])
                counts[branch] = counts.get(branch, 0) + 1
                tested += 1
        self.assertEqual(set(counts), {"favorite", "best-tail", "blocking-anchor", "best-anchor"})
        self.assertGreater(tested, 400)
        print(f"reserved inputs: {tested}; branches: {counts}")

    def test_improvement_can_lose_every_anchor_certificate(self):
        for u in (LOSS_PROFILE, LOSS_STRICT_PROFILE):
            self.assertTrue(has_anchors(u, LOSS_START, 3))
            route, branch = improve(u, LOSS_START, 3, LOSS_ANCHORS)
            self.assertEqual(branch, "best-tail")
            self.assertEqual(route, [LOSS_START, (1, 0, 1, 0, 2, 2, 3)])
            check_route(self, u, route, 3)
            self.assertFalse(has_anchors(u, route[-1], 3))
            # This is a failed invariant, not a disconnected endpoint pair.
            continuation = [route[-1], (1, 1, 0, 0, 2, 2, 3), (1, 2, 0, 0, 1, 2, 3)]
            check_route(self, u, continuation, 3)
            remaining = set(range(7))
            for i, g in ((3, 6), (2, 5), (1, 4), (0, 3), (2, 1), (1, 0), (0, 2)):
                self.assertTrue(all(u[i][g] >= u[i][h] for h in remaining))
                remaining.remove(g)

    def test_pair_only_isolation_threshold_obstruction(self):
        for n in (3, 4, 6, 12):
            for strict in (False, True):
                u, initial = pair_obstruction(n, strict)
                self.assertTrue(fair(u, initial))
                if strict:
                    for row in u:
                        self.assertGreater(min(row), 0)
                        self.assertEqual(len(set(row)), len(row))
                for x in range(2 * n):
                    for y in range(x):
                        if initial[x] != initial[y]:
                            b = list(initial)
                            b[x], b[y] = b[y], b[x]
                            self.assertFalse(fair(u, b), (n, strict, x, y))
                # Produce an actual different greedy endpoint independently.
                remaining = set(range(2 * n))
                greedy = [-1] * (2 * n)
                for i in list(range(n)) * 2:
                    g = max(remaining, key=lambda h: (u[i][h], -h))
                    self.assertTrue(all(u[i][g] >= u[i][h] for h in remaining))
                    greedy[g] = i
                    remaining.remove(g)
                self.assertNotEqual(tuple(greedy), initial)
                self.assertTrue(fair(u, greedy))

    def test_refuse_invalid_certificate_and_real_command(self):
        for bad in (((0, 1), (1, 0), (2, 5)), ((0, -1), (1, 0), (2, 5)),
                    ((0, 3), (0, 1), (2, 5))):
            with self.assertRaises(ValueError):
                validate_reserved(LOSS_PROFILE, LOSS_START, 3, bad)
        with self.assertRaises(ValueError):
            improve(LOSS_PROFILE, LOSS_START[:-1], 3, LOSS_ANCHORS)
        with self.assertRaises(ValueError):
            pair_obstruction(2)
        command = subprocess.run([sys.executable, str(Path(__file__).with_name("reserved_singleton.py"))],
                                 check=True, text=True, capture_output=True)
        self.assertIn("new serial-anchor certificate: None", command.stdout)
        self.assertIn("all 12 exchanges rejected", command.stdout)


if __name__ == "__main__":
    unittest.main()
