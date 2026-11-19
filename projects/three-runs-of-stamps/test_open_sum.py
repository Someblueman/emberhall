import unittest
from collections import Counter

from delayed_escape import extend as gap_extensions
from delayed_escape import first_internal
from open_sum import completions, valley_prefixes
from reconstruction import extend


def unclosed(order, k):
    for j in range(2, k + 1):
        old = [face for face in order if face <= k + j]
        if abs(old.index(k + j) - old.index(k + j - 1)) == 1:
            return False
    return True


class OpenSumTest(unittest.TestCase):
    def test_complete_prefixes_and_labeled_orders(self):
        for k in range(2, 13):
            word = "M"*k + "V"*k
            seen = set()
            total = 0
            for turn, family, prefix in valley_prefixes(k):
                with self.subTest(k=k, turn=turn, family=family):
                    self.assertTrue(unclosed(prefix, k))
                    self.assertNotIn(prefix, seen)
                    seen.add(prefix)
                    mountain = tuple(x for x in prefix if x <= k)
                    self.assertEqual(first_internal(mountain), turn)
                    self.assertEqual(2*k in (prefix[0], prefix[-1]), family == "outside")
                    actual = list(completions(prefix, k, turn, family))
                    direct = set(extend(prefix, word + "M"*k))
                    self.assertEqual(set(actual), direct)
                    self.assertEqual(len(actual), len(direct))
                    total += len(actual)
            self.assertEqual(seen, {p for p in extend((0,), word) if unclosed(p, k)})
            self.assertEqual(total, (9*k*k - 19*k + 12)//2)

    def test_individual_weights_at_longer_lengths(self):
        for k in (13, 16, 21, 24):
            counts = Counter()
            for t, family, prefix in valley_prefixes(k):
                with self.subTest(k=k, turn=t, family=family):
                    actual = set(completions(prefix, k, t, family))
                    self.assertEqual(actual, set(gap_extensions(prefix, "M"*k)))
                    if t is None:
                        expected = 2*k - 2 if family == "outside" else k
                    else:
                        expected = 3*k - t - 1 if family == "outside" else k + 2*(k-t) + 2
                    self.assertEqual(len(actual), expected)
                    counts[family] += 1
            self.assertEqual(counts, {"outside": k, "inside": k-2})

    def test_smallest_assignment_from_permutations(self):
        from reconstruction import brute
        expected = {o for o in brute("MMVVMM") if unclosed(o, 2)}
        actual = {o for t, f, p in valley_prefixes(2) for o in completions(p, 2, t, f)}
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 5)


if __name__ == "__main__":
    unittest.main()
