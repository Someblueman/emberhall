"""Independent deletion and matching checks for the crossing construction."""

from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from common_crossing import (DIRECT_FAILURE, REPAIRED_ATTACHMENT, REPAIRED_WITNESS,
                             _match, attachment_boundary, common_crossing)


def fair(u, state):
    for i, row in enumerate(u):
        own = sum(row[g] for g, owner in enumerate(state) if owner == i)
        for j in range(len(u)):
            bundle = [g for g, owner in enumerate(state) if owner == j]
            if bundle and not any(own >= sum(row[h] for h in bundle if h != removed)
                                  for removed in bundle):
                return False
    return True


class CommonCrossingTests(unittest.TestCase):
    def check_crossing(self, u, shared, carriers, result, order):
        n, m = len(u), len(u[0])
        left, right = result.sides
        self.assertTrue(fair(u, left))
        self.assertTrue(fair(u, right))
        self.assertEqual([g for g in range(m) if left[g] != right[g]],
                         sorted((shared, result.pivot)))
        self.assertEqual((left[shared], left[result.pivot]), carriers)
        self.assertEqual((right[result.pivot], right[shared]), carriers)
        for state in result.sides:
            self.assertEqual(tuple(state.count(i) for i in range(n)),
                             tuple(1 if i in carriers else 2 for i in range(n)))
        pool = set(range(m)) - {shared, result.pivot}
        self.assertEqual(tuple(i for i, _ in result.anchors), order)
        for agent, good in result.anchors:
            self.assertIn(good, pool)
            self.assertTrue(all(u[agent][good] >= u[agent][h] for h in pool))
            pool.remove(good)
        self.assertEqual({g for _, g in result.tails}, pool)
        self.assertEqual({i for i, _ in result.tails}, set(order))
        for i in carriers:
            self.assertLessEqual(sum(u[i][g] > u[i][result.pivot]
                                     for g in range(m) if g != shared), n-2)

    def test_all_disjoint_upper_set_splits_through_four_pairs(self):
        count = 0
        for r in range(1, 5):
            for colors in product(range(3), repeat=2*r):
                if colors.count(1) > r or colors.count(2) > r:
                    continue
                # 0=neither, 1=above pivot for carrier i, 2=above for j.
                u = ((0,)*(2*r+1),)*r + tuple(
                    tuple(int(color == k) for color in colors) + (0,)
                    for k in (1, 2))
                anchors = tuple((i, i) for i in range(r))
                tails = tuple(range(r, 2*r))
                matched = _match(u, (r, r+1), 2*r, anchors, tails)
                self.assertEqual({g for _, g in matched}, set(tails))
                for (_, a), (_, b) in zip(anchors, matched):
                    self.assertFalse(colors[a] == colors[b] != 0)
                count += 1
        self.assertEqual(count, 6060)

    def test_exact_profiles_labels_orders_and_ties(self):
        rng = random.Random(2026112041)
        count = 0
        for r in (1, 2, 3, 4, 7, 12):
            for trial in range(30):
                n, m = r+2, 2*r+2
                shared = rng.randrange(m)
                carriers = tuple(rng.sample(range(n), 2))
                u = [[Fraction(rng.randrange(7), rng.choice((1, 3, 11)))
                      if trial else 0 for _ in range(m)] for _ in range(n)]
                for i in carriers:
                    u[i][shared] = max(u[i])
                u = tuple(map(tuple, u))
                order = [i for i in range(n) if i not in carriers]
                rng.shuffle(order)
                order = tuple(order)
                self.check_crossing(u, shared, carriers,
                                    common_crossing(u, shared, carriers, order), order)
                count += 1
        self.assertEqual(count, 180)

    def test_attachment_boundary_for_every_small_anchor_order(self):
        for r in range(1, 6):
            u, shared, carriers = attachment_boundary(r)
            for order in permutations(range(r)):
                result = common_crossing(u, shared, carriers, order)
                self.check_crossing(u, shared, carriers, result, order)
                self.assertEqual(result.pivot, r+1)
                self.assertEqual({g for _, g in result.anchors}, set(range(1, r+1)))
                self.assertTrue(all(u[carriers[1]][g] > u[carriers[1]][result.pivot]
                                    for _, g in result.tails))
            # Every other potential pivot violates the necessary upper-count
            # condition for one carrier, independently of the constructor.
            for pivot in range(1, 2*r+2):
                if pivot != r+1:
                    self.assertTrue(any(sum(row[g] > row[pivot] for g in range(1, 2*r+2)) > r
                                        for row in (u[i] for i in carriers)))

    def test_malformed_inputs_and_real_command(self):
        u, g, carriers = attachment_boundary(2)
        for wrong in ((2, 2), (2, 4), (True, 3), (2,), (2, 3, 0)):
            with self.assertRaises(ValueError):
                common_crossing(u, g, wrong)
        for wrong in (-1, len(u[0]), False):
            with self.assertRaises(ValueError):
                common_crossing(u, wrong, carriers)
        for order in ((0,), (0, 0), (0, 2), (False, 1)):
            with self.assertRaises(ValueError):
                common_crossing(u, g, carriers, order)
        bad = list(u)
        bad[carriers[0]] = (0,) + bad[carriers[0]][1:]
        with self.assertRaises(ValueError):
            common_crossing(tuple(bad), g, carriers)
        with self.assertRaises(ValueError):
            common_crossing(tuple(row[:-1] for row in u), g, carriers)
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('common_crossing.py')),
                                 '--pairs', '7'], check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['pairs'], 7)
        self.assertEqual(data['pivot_dominates_all_tails'], [True, False])
        u, _, _ = attachment_boundary(7)
        self.assertTrue(all(fair(u, state) for state in data['path']))

    def test_direct_improvement_failure_and_actual_greedy_repair(self):
        u = DIRECT_FAILURE
        result = common_crossing(u, 0, (3, 4))
        self.assertEqual(result.sides[0], REPAIRED_ATTACHMENT[0])
        self.assertEqual(result.pivot, 1)
        self.assertEqual(max(range(1, 8), key=lambda g: u[4][g]), 6)
        wrong = list(result.sides[0])
        wrong[1], wrong[6] = wrong[6], wrong[1]
        self.assertFalse(fair(u, wrong))
        self.assertEqual(sum(u[2][g] for g, owner in enumerate(wrong) if owner == 2), 2)
        self.assertEqual(min(u[2][1], u[2][3]), 3)
        for state in REPAIRED_ATTACHMENT:
            self.assertTrue(fair(u, state))
            self.assertEqual(state[0], 3)
        for a, b in zip(REPAIRED_ATTACHMENT, REPAIRED_ATTACHMENT[1:]):
            changed = [g for g in range(8) if a[g] != b[g]]
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((a[x], a[y]), (b[y], b[x]))
        pool = set(range(8))
        owners = [-1]*8
        for offset, (i, g) in enumerate(REPAIRED_WITNESS):
            eligible = set(range(5)) if offset < 5 else {0, 1, 2}
            used = {a for a, _ in REPAIRED_WITNESS[(0 if offset < 5 else 5):offset]}
            self.assertIn(i, eligible - used)
            self.assertIn(g, pool)
            self.assertTrue(all(u[i][g] >= u[i][h] for h in pool))
            owners[g] = i
            pool.remove(g)
        self.assertFalse(pool)
        self.assertEqual(tuple(owners), REPAIRED_ATTACHMENT[-1])


if __name__ == '__main__':
    unittest.main()
