"""Independent finite checks for the one-final-recipient proof and constructor."""

from itertools import permutations
import random
import unittest

from four_agent_one_final import EXAMPLE, LEFT, RIGHT, carrier_path, padded_path, path
from swaps import allocation, favorites, rounds_for


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(4)]
    return all(any(sum(u[i][g] for g in bundles[i]) >=
                       sum(u[i][g] for g in bundles[j] if g != removed)
                       for removed in bundles[j])
               for i in range(4) for j in range(4) if i != j)


def verify(case, u, result, a, b, carriers=None, g=0):
    case.assertEqual((result[0], result[-1]), (a, b))
    for state in result:
        case.assertTrue(fair(u, state))
        case.assertEqual(tuple(state.count(i) for i in range(4)), tuple(a.count(i) for i in range(4)))
        if carriers is not None:
            case.assertIn(state[g], carriers)
    for before, after in zip(result, result[1:]):
        changed = [h for h in range(len(a)) if before[h] != after[h]]
        case.assertEqual(len(changed), 2)
        x, y = changed
        case.assertEqual((before[x], before[y]), (after[y], after[x]))


class OneFinalTests(unittest.TestCase):
    def test_exact_demo_and_greedy_endpoints(self):
        verify(self, EXAMPLE, carrier_path(EXAMPLE, LEFT, RIGHT), LEFT, RIGHT, (1, 2))
        a = ((1, 0), (0, 1), (3, 2), (2, 4), (0, 3))
        b = ((2, 0), (0, 1), (3, 2), (1, 3), (0, 4))
        verify(self, EXAMPLE, path(EXAMPLE, a, b), LEFT, RIGHT)

    def test_all_protected_pairs_and_ties_for_each_carrier_choice(self):
        states = tuple(sorted(set(permutations((0, 0, 1, 2, 3)))))
        rng = random.Random(2026112030)
        for carriers in ((1, 2), (1, 3), (2, 3)):
            for sample in range(60):
                rows = [[rng.randrange(8) for _ in range(5)] for _ in range(4)]
                for i in carriers:
                    rows[i][0] = max(rows[i])
                if sample == 0:
                    rows = [[0] * 5 for _ in range(4)]
                u = tuple(map(tuple, rows))
                allowed = [a for a in states if a[0] in carriers and fair(u, a)]
                for a, b in ((allowed[0], allowed[-1]), (rng.choice(allowed), rng.choice(allowed))):
                    verify(self, u, carrier_path(u, a, b, carriers), a, b, carriers)

    def test_padded_braids_through_six_complete_rounds(self):
        rng = random.Random(2026112031)
        checked = 0
        for q in range(2, 7):
            for _ in range(100):
                m = 4 * q + 1
                rows = [[rng.randrange(50) for _ in range(m)] for _ in range(4)]
                rows[1][0] = rows[2][0] = 50
                u = tuple(map(tuple, rows))
                remaining, prefix = tuple(range(1, m)), []
                for _ in range(q - 1):
                    for i in (0, 3):
                        h = favorites(u, i, remaining)[0]
                        prefix.append((i, h))
                        remaining = tuple(g for g in remaining if g != h)
                    x, y = favorites(u, 1, remaining)[0], favorites(u, 2, remaining)[0]
                    if x == y:
                        break
                    prefix.extend(((1, x), (2, y)))
                    remaining = tuple(g for g in remaining if g not in (x, y))
                if len(prefix) != 4 * (q - 1):
                    continue
                k = favorites(u, 0, remaining)[0]
                remaining = tuple(g for g in remaining if g != k)
                l = favorites(u, 3, remaining)[0]
                remaining = tuple(g for g in remaining if g != l)
                x, y = favorites(u, 1, remaining)[0], favorites(u, 2, remaining)[0]
                if x == y:
                    continue
                tail = (0, k, l, x, y)
                result = padded_path(u, tuple(prefix), tail, LEFT, RIGHT)
                verify(self, u, result, result[0], result[-1], (1, 2))
                self.assertTrue(all(a[g] == i for a in result for i, g in prefix))
                checked += 1
        self.assertGreater(checked, 40)

    def test_full_nine_good_endpoint_constructor(self):
        rng = random.Random(2026112032)
        for _ in range(8):
            u = tuple(tuple(rng.randrange(10) for _ in range(9)) for _ in range(4))
            def witness():
                remaining, result = tuple(range(9)), []
                for agents in rounds_for(4, 9, (0,)):
                    order = list(agents)
                    rng.shuffle(order)
                    for i in order:
                        g = rng.choice(favorites(u, i, remaining))
                        result.append((i, g))
                        remaining = tuple(h for h in remaining if h != g)
                return tuple(result)
            a, b = witness(), witness()
            verify(self, u, path(u, a, b), allocation(a, 9), allocation(b, 9))

    def test_invalid_protection_and_prefix(self):
        with self.assertRaisesRegex(ValueError, 'distinct singleton'):
            carrier_path(EXAMPLE, LEFT, RIGHT, (0, 1))
        rows = list(map(list, EXAMPLE))
        rows[1][0] = 0
        with self.assertRaisesRegex(ValueError, 'favorite'):
            carrier_path(tuple(map(tuple, rows)), LEFT, RIGHT)
        with self.assertRaisesRegex(ValueError, 'five distinct'):
            padded_path(EXAMPLE, (), (0, 1, 2, 3, 3), LEFT, RIGHT)
        with self.assertRaisesRegex(ValueError, '4q'):
            path(((0,) * 6,) * 4, (), ())


if __name__ == '__main__':
    unittest.main()
