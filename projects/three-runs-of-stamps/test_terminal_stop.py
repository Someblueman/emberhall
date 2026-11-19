import unittest

from delayed_escape import extend as gap_extensions
from escape_chain import chains
from reconstruction import brute, extend
from terminal_stop import completions, terminal_prefixes


class TerminalStopTest(unittest.TestCase):
    def test_each_labeled_set(self):
        for k in range(2, 14):
            word = "M"*k + "V"*k + "M"*k
            terminal = {c.prefix for c in chains(k, k) if c.stop == k}
            seen = set()
            total = 0
            for turn, family, prefix, witness in terminal_prefixes(k):
                with self.subTest(k=k, turn=turn, family=family):
                    self.assertNotIn(prefix, seen)
                    seen.add(prefix)
                    actual = list(completions(k, turn, family, prefix, witness))
                    direct = set(extend(prefix, word))
                    self.assertEqual(len(actual), len(direct))
                    self.assertEqual(set(actual), direct)
                    total += len(actual)
            self.assertEqual(seen, terminal)
            self.assertEqual(total, 5 if k == 2 else 7*k*k - 23*k + 21)

    def test_late_turns_individually(self):
        for k in (15, 16, 22, 25):
            for turn, family, prefix, witness in terminal_prefixes(k):
                if turn is None or turn < 5:
                    continue
                with self.subTest(k=k, turn=turn, family=family):
                    found = set(completions(k, turn, family, prefix, witness))
                    self.assertEqual(found, set(gap_extensions(prefix, "M"*k)))
                    d = k-turn
                    self.assertEqual(len(found), 2*k+2*d if family == "inside" else 3*k+2*d-2)

    def test_smallest_universe(self):
        found = {o for t, family, p, w in terminal_prefixes(2)
                 for o in completions(2, t, family, p, w)}
        direct = set()
        for order in brute("MMVVMM"):
            prefix = tuple(x for x in order if x <= 4)
            if abs(prefix.index(3) - prefix.index(4)) == 1:
                direct.add(order)
        self.assertEqual(found, direct)


if __name__ == "__main__":
    unittest.main()
