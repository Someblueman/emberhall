import unittest

from delayed_escape import adjacent, extend, first_internal
from last_turn import completions, stopped_prefixes
from reconstruction import extend as matching_extensions


def stopped_last_turn(a, r):
    mountain, = (p for p in extend((0,), "M" * a) if first_internal(p) == a)
    states = [mountain]
    for step in range(1, r + 1):
        states = [child for p in states for child in extend(p, "V")
                  if step == 1 or (child == adjacent(p, "V")) == (step == r)]
    return states


class LastTurnTest(unittest.TestCase):
    def test_full_labeled_sets(self):
        for r in range(5, 16):
            for a in {r, r + 1, r + 2, r + 5}:
                with self.subTest(a=a, r=r):
                    families = stopped_prefixes(a, r)
                    self.assertEqual(set(families.values()), set(stopped_last_turn(a, r)))
                    self.assertEqual(len(families), 2 if a == r else 3)
                    for name, prefix in families.items():
                        found = list(completions(a, r, name))
                        direct = set(matching_extensions(prefix, "M"*a + "V"*r + "M"*r))
                        self.assertEqual(set(found), direct)
                        self.assertEqual(len(found), len(direct))
                        self.assertEqual(len(found), 3*r - 2 if name == "outer" else 2*r)

    def test_short_stops(self):
        for r, expected in [(2, [3, 4]), (3, [5, 6]), (4, [8, 8])]:
            a = 7
            counts = sorted(sum(1 for _ in matching_extensions(p, "M"*a + "V"*r + "M"*r))
                            for p in stopped_last_turn(a, r))
            self.assertEqual(counts, expected)
            with self.assertRaises(ValueError):
                stopped_prefixes(a, r)

    def test_no_direct_branch_at_equal_lengths(self):
        with self.assertRaises(ValueError):
            list(completions(6, 6, "direct"))


if __name__ == "__main__":
    unittest.main()
