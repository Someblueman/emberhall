import unittest

from deep_turn import completions, stopped_prefix
from reconstruction import extend, inward_step


def stop_at(order, a, r):
    for j in range(2, r + 1):
        old = [face for face in order if face <= a + j]
        if abs(old.index(a + j) - old.index(a + j - 1)) == 1:
            return j
    return None


class DeepTurnTest(unittest.TestCase):
    def test_unique_prefix_and_complete_suffix(self):
        for a in range(3, 11):
            for r in range(2, a):
                by_turn = {}
                for order in extend((0,), "M" * a + "V" * r):
                    if stop_at(order, a, r) == r:
                        mountain = tuple(x for x in order if x <= a)
                        by_turn.setdefault(inward_step(mountain), []).append(order)
                for turn in range(2, a - r + 2):
                    with self.subTest(a=a, turn=turn, r=r):
                        prefix = stopped_prefix(a, turn, r)
                        self.assertEqual(by_turn[turn], [prefix])
                        for c in {0, 1, max(0, r - 2), r - 1, r, r + 1, r + 3}:
                            actual = list(completions(a, turn, r, c))
                            direct = set(extend(prefix, "M" * a + "V" * r + "M" * c))
                            self.assertEqual(set(actual), direct)
                            self.assertEqual(len(actual), len(direct))
                            self.assertEqual(len(actual), 1 if c == 0 else
                                             min(c, r + 1) + min(c, r - 2))

    def test_one_layer_short_adds_a_second_prefix(self):
        a, turn, r = 8, 5, 5
        prefixes = [o for o in extend((0,), "M" * a + "V" * r)
                    if stop_at(o, a, r) == r
                    and inward_step(tuple(x for x in o if x <= a)) == turn]
        counts = sorted(sum(1 for _ in extend(p, "M" * a + "V" * r + "M" * r))
                        for p in prefixes)
        self.assertEqual(counts, [14, 15])
        with self.assertRaises(ValueError):
            stopped_prefix(a, turn, r)

    def test_negative_suffix(self):
        with self.assertRaises(ValueError):
            list(completions(6, 2, 5, -1))


if __name__ == "__main__":
    unittest.main()
