from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from five_agent_padding import _construct, padded_path, path, protected_bridge
from five_agent_seven import EXAMPLE, LEFT, RIGHT
from swaps import allocation, validate_witness, rounds_for
from test_five_agent_seven import fair, profile


def greedy(u, rng, prefix=()):
    m = len(u[0])
    result = list(prefix)
    remaining = set(range(m)) - {g for _, g in prefix}
    for r in range(m // 5):
        used = {i for i, _ in prefix} if r == 0 else set()
        for i in rng.sample([a for a in range(5) if a not in used], 5-len(used)):
            best = max(u[i][g] for g in remaining)
            g = rng.choice([g for g in sorted(remaining) if u[i][g] == best])
            result.append((i, g))
            remaining.remove(g)
    for i in rng.sample([0, 1], 2):
        g = max(sorted(remaining), key=lambda g: u[i][g])
        result.append((i, g))
        remaining.remove(g)
    return tuple(result)


def prefix_case(rounds, rng):
    rows = [list(row) for row in profile(rng)]
    for row in rows:
        row.extend([0] * (5 * rounds))
    prefix = []
    for r in range(rounds):
        base = 1000 * (rounds-r)
        for i in range(5):
            good = 7 + 5*r + i
            prefix.append((i, good))
            for a in range(5):
                rows[a][good] = base + (200 if a == i else rng.randrange(100))
    return tuple(tuple(row) for row in rows), tuple(prefix)


def coupled_case(q, rng, carriers=(2, 3)):
    """Keep the two unequal last choices alive through every complete round."""
    m = 5*q+2
    i, j = carriers
    others = [a for a in range(5) if a not in carriers]
    for _ in range(500):
        rows = [rng.sample(range(m), m) for _ in range(5)]
        rows[i][0] = rows[j][0] = m+5
        pool = set(range(1, m))
        left, right = [(i, 0)], [(j, 0)]
        for r in range(q):
            for a in others:
                g = max(pool, key=lambda g: rows[a][g])
                pool.remove(g)
                left.append((a, g)); right.append((a, g))
            x = max(pool, key=lambda g: rows[i][g])
            y = max(pool, key=lambda g: rows[j][g])
            if x == y:
                break
            pool -= {x, y}
            left.append((j, y)); right.append((i, x))
            if r < q-1:
                left.append((i, x)); right.append((j, y))
            else:
                z = pool.pop()
                rows[0][x] = max(rows[0][x], rows[0][z])
                rows[0][y] = max(rows[0][y], rows[0][z])
                left.extend(((0, x), (1, z)))
                right.extend(((0, y), (1, z)))
                return tuple(tuple(row) for row in rows), tuple(left), tuple(right)
    raise AssertionError('could not generate the required uncancelled braid')


class PaddingTests(unittest.TestCase):
    def check_path(self, u, start, target, route, fixed=()):
        self.assertEqual(route[0], allocation(start, len(u[0])))
        self.assertEqual(route[-1], allocation(target, len(u[0])))
        for a in route:
            self.assertTrue(fair(u, a), a)
            q = len(u[0]) // 5
            self.assertEqual(tuple(a.count(i) for i in range(5)), (q+1, q+1, q, q, q))
            self.assertTrue(all(a[g] == i for i, g in fixed))
        for a, b in zip(route, route[1:]):
            changes = [g for g in range(len(a)) if a[g] != b[g]]
            self.assertEqual(len(changes), 2)
            g, h = changes
            self.assertEqual((a[g], a[h]), (b[h], b[g]))

    def test_protection_and_free_final_assignment(self):
        rng = random.Random(23780)
        for _ in range(250):
            rows = [list(row) for row in profile(rng)]
            # Deliberately make one final assignment non-greedy while preserving
            # every first-round hypothesis: only D's tail order changes.
            rows[0][6] = max(rows[0][4:])
            rows[0][1] = max(rows[0][1:])
            u = tuple(tuple(row) for row in rows)
            route = protected_bridge(u)
            self.check_path(u, LEFT, RIGHT, route)
            self.assertTrue(all(a[0] in (2, 3) for a in route))

    def test_actual_padding_through_eight_common_rounds(self):
        rng = random.Random(23781)
        for q in range(9):
            for _ in range(8):
                u, prefix = prefix_case(q, rng)
                for carriers in ((2, 3), (2, 4), (4, 3)):
                    third = next(i for i in (2, 3, 4) if i not in carriers)
                    roles = (0, 1, *carriers, third)
                    # Relabel whole observer rows and prefix owners together.
                    renamed = tuple(u[roles.index(i)] for i in range(5))
                    pp = tuple((roles[i], g) for i, g in prefix)
                    a = tuple(roles[i] for i in allocation(LEFT, 7))
                    b = tuple(roles[i] for i in allocation(RIGHT, 7))
                    route = padded_path(renamed, pp, tuple(range(7)), a, b, carriers)
                    left = pp + tuple((roles[i], g) for i, g in LEFT)
                    right = pp + tuple((roles[i], g) for i, g in RIGHT)
                    self.check_path(renamed, left, right, route, pp)

    def test_random_long_endpoints_and_fixed_prefixes(self):
        rng = random.Random(23782)
        for q in range(1, 6):
            for trial in range(8):
                m = 5*q+2
                u = tuple(tuple(Fraction(rng.randrange(8), rng.randrange(1, 5))
                                for _ in range(m)) for _ in range(5))
                # Retain a growing exact first-round prefix in half the cases.
                prefix = ()
                if trial % 2:
                    prefix = greedy(u, rng)[:trial % 5]
                a, b = greedy(u, rng, prefix), greedy(u, rng, prefix)
                self.check_path(u, a, b, path(u, a, b), prefix)

    def test_last_first_round_agent_with_tied_choices(self):
        u = ((0,) * 12,) * 5
        prefix = tuple(zip(range(4), range(4)))
        a = prefix + ((4, 4), (4, 5), (0, 6), (1, 7), (2, 8), (3, 9), (0, 10), (1, 11))
        b = prefix + ((4, 5), (4, 4), (0, 6), (1, 7), (2, 8), (3, 9), (0, 10), (1, 11))
        self.check_path(u, a, b, path(u, a, b), prefix)

    def test_uncancelled_braids_with_all_three_carrier_pairs(self):
        rng = random.Random(23784)
        for q in (2, 3, 5, 8):
            for carriers in ((2, 3), (2, 4), (3, 4)):
                u, a, b = coupled_case(q, rng, carriers)
                validate_witness(u, rounds_for(5, len(u[0]), (0, 1)), a)
                validate_witness(u, rounds_for(5, len(u[0]), (0, 1)), b)
                self.check_path(u, a, b, path(u, a, b))

    def test_free_final_recursive_endpoints(self):
        rng = random.Random(23785)
        for q in (1, 2, 4):
            m = 5*q+2
            u = tuple(tuple(rng.randrange(10) for _ in range(m)) for _ in range(5))
            a, b = greedy(u, rng), greedy(u, rng)
            # Keep the complete greedy rounds but reverse the last assignment.
            b = b[:-2] + ((b[-2][0], b[-1][1]), (b[-1][0], b[-2][1]))
            route = []
            for state in _construct(u, a, b):
                if not route or state != route[-1]:
                    route.append(state)
            self.check_path(u, a, b, route)

    def test_padding_rejects_missing_hypotheses(self):
        rng = random.Random(23783)
        u, prefix = prefix_case(1, rng)
        a, b = allocation(LEFT, 7), allocation(RIGHT, 7)
        with self.assertRaises(ValueError):
            padded_path(u, prefix, (0, 1, 2, 3, 4, 5, 5), a, b)
        with self.assertRaisesRegex(ValueError, 'braid endpoints'):
            padded_path(u, prefix, tuple(range(7)), a, (0,) * 7)
        with self.assertRaises(ValueError):
            padded_path(u, prefix, tuple(range(7)), a, b, (0, 2))
        rows = [list(row) for row in u]
        # Agent 0 picks after carrier 2 has taken good 9, which agent 0 prefers.
        rows[0][9] = 1300
        bad_prefix = ((2, 9), (0, 7), (1, 8), (3, 10), (4, 11))
        with self.assertRaisesRegex(ValueError, 'dominate'):
            padded_path(tuple(tuple(row) for row in rows), bad_prefix, tuple(range(7)), a, b)

    def test_real_command(self):
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('five_agent_padding.py'))],
                             check=True, text=True, capture_output=True)
        data = json.loads(run.stdout)
        self.assertEqual(data['goods'], 12)
        self.assertGreaterEqual(data['exchanges'], 1)


if __name__ == '__main__':
    unittest.main()
