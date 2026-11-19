"""Tests for the complete first-adjacent-valley decomposition."""
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from delayed_escape import extend
from escape_chain import chains, conjectured_bases, recover, report, stop_weights


def legal(order, assignment):
    at = {face: position for position, face in enumerate(order)}
    for i, symbol in enumerate(assignment):
        if (at[i] > at[i + 1]) != ((symbol == "M") == (i % 2 == 0)):
            return False
        for j in range(i + 2, len(assignment), 2):
            lo, hi = sorted((at[i], at[i + 1]))
            if (lo < at[j] < hi) != (lo < at[j + 1] < hi):
                return False
    return True


class EscapeChainTests(unittest.TestCase):
    def test_full_permutation_control(self):
        expected = {s for s in itertools.permutations(range(5)) if legal(s, "MMVV")}
        self.assertEqual({chain.expand() for chain in chains(2, 2)}, expected)
        expected_full = {s for s in itertools.permutations(range(7)) if legal(s, "MMVVMM")}
        actual = {s for chain in chains(2, 2) for s in extend(chain.expand(), "MM")}
        self.assertEqual(actual, expected_full)
        self.assertEqual(len(expected_full), 10)

    def test_decomposition_and_inverse_all_small_unequal_lengths(self):
        for a in range(2, 9):
            for b in range(2, 9):
                found = list(chains(a, b))
                expanded = [chain.expand() for chain in found]
                self.assertEqual(len(expanded), len(set(expanded)), (a, b))
                self.assertEqual(set(expanded), set(extend((0,), "M" * a + "V" * b)))
                for chain, order in zip(found, expanded):
                    self.assertEqual(recover(order, a, b), chain)
                    self.assertTrue(legal(order, "M" * a + "V" * b))

    def test_each_collar_reduction_against_full_extension(self):
        for a in range(2, 8):
            for b in range(2, 8):
                for chain in chains(a, b):
                    length = b if chain.stop is None else chain.stop
                    reduced = sum(1 for _ in extend(chain.prefix, "M" * length)) + chain.tail
                    direct = sum(1 for _ in extend(chain.expand(), "M" * b))
                    self.assertEqual(reduced, direct, (a, b, chain))

    def test_bucket_totals_and_published_small_controls(self):
        for k, expected in ((2, 10), (3, 48), (4, 142), (5, 319),
                            (6, 606), (7, 1030), (8, 1618)):
            rows = report(k, k)
            self.assertEqual(sum(row['total'] for row in rows.values()), expected)
            self.assertEqual(sum(row['prefixes'] for row in rows.values()), 2*k*k - 3*k + 2)
            # This bucket independently recovers the earlier first-valley family.
            self.assertEqual(rows[2]['total'], 5 if k == 2 else k*k + k + 3)
            self.assertEqual(rows[None]['tail'], 0)

    def test_extra_double_escape_gap_tree(self):
        templates = ["x3,l u,x2 z2,x2", "x3,l u,x2 x1,v",
                     "x3,l x3,z1 z2,z1", "h,x1 a,u z2,u",
                     "h,x1 a,u v,+", "h,x1 h,z1 z2,z1"]
        for a in range(3, 13):
            extra = []
            for chain in chains(a, 3):
                first = tuple(x for x in chain.prefix if x <= a + 1)
                if chain.stop == 3 and abs(first.index(a) - first.index(a+1)) != 1:
                    extra.append(chain.prefix)
            self.assertEqual(len(extra), int(a >= 4))
            for prefix in extra:
                normal = prefix if a % 2 == 0 else prefix[::-1]
                inner = [x for x in normal if x <= a-4]
                names = dict(a=a, u=a-3, v=a-2, x1=a+1, x2=a+2, x3=a+3,
                             z1=a+4, z2=a+5, l=inner[0], h=inner[-1])
                names['+'] = None
                expected = {tuple(tuple(names[x] for x in g.split(',')) for g in row.split())
                            for row in templates}
                actual = set()
                for order in extend(prefix, 'MMM'):
                    trace = []
                    for new in range(a+4, a+7):
                        small = tuple(x for x in order if x <= new)
                        if a % 2:
                            small = small[::-1]
                        i = small.index(new)
                        trace.append((small[i-1] if i else None,
                                      small[i+1] if i+1 < len(small) else None))
                    actual.add(tuple(trace))
                self.assertEqual(actual, expected, a)
        for a in range(4, 11):
            for b in range(3, 10):
                row = report(a, b)[3]
                self.assertEqual(row['prefixes'], a+2)
                self.assertEqual(row['total'], (a+2)*b+a+10)

    def test_recorded_finite_weighted_screen(self):
        for k in range(3, 14):
            rows = report(k, k)
            self.assertEqual({r: row['base'] for r, row in rows.items()}, conjectured_bases(k))
        # Outside the stated interior range the same expression already fails.
        self.assertNotEqual(report(4, 4)[4]['base'], 2*(4-1)*4 + 8*4*4 - 27*4 + 25)
        weights = stop_weights(6, 4)
        self.assertEqual({t: sorted(weight for _, weight in rows) for t, rows in weights.items()},
                         {2: [6], 3: [6], 4: [10, 11], 5: [9, 9], 6: [8, 8], None: [6, 8]})

    def test_forced_tail_is_not_accepted_silently(self):
        chain = next(c for c in chains(3, 5) if c.tail)
        invalid = list(chain.expand())
        i, j = invalid.index(len(invalid) - 1), invalid.index(len(invalid) - 2)
        invalid[i], invalid[j] = invalid[j], invalid[i]
        with self.assertRaises(ValueError):
            recover(tuple(invalid), 3, 5)
        for a, b in ((1, 2), (2, 1), (0, 0)):
            with self.assertRaises(ValueError):
                list(chains(a, b))
        with self.assertRaises(ValueError):
            recover((0, 1), 2, 2)

    def test_open_chain_cannot_use_the_adjacent_collar_lemma(self):
        opened = (1, 3, 8, 5, 6, 7, 4, 9, 2, 0)
        stopped = (1, 3, 8, 5, 6, 7, 4, 10, 9, 2, 0)
        self.assertEqual(sum(1 for _ in extend(opened, 'MMM')), 3)
        self.assertEqual(sum(1 for _ in extend(stopped, 'MMMM')), 6)
        full = (1, 3, 8, 11, 13, 14, 12, 5, 6, 7, 4, 10, 9, 2, 0)
        self.assertTrue(legal(full, 'M'*6 + 'V'*4 + 'M'*4))
        collapsed = tuple(x if x < 10 else x-2 for x in full if x not in (10, 11))
        self.assertFalse(legal(collapsed, 'M'*6 + 'V'*3 + 'M'*3))

    def test_native_reduced_and_direct_command(self):
        command = [sys.executable, str(Path(__file__).with_name("escape_chain.py"))]
        result = subprocess.run(command + ["--k", "4", "--verify"],
                                capture_output=True, text=True, check=True)
        self.assertIn("total: 22 prefixes; 142 completions", result.stdout)
        self.assertIn("Every tail reduction agrees", result.stdout)
        result = subprocess.run(command + ['--a', '6', '--b', '4', '--by-turn'],
                                capture_output=True, text=True, check=True)
        self.assertIn('Stop-4 base cases by first internal mountain step:', result.stdout)
        self.assertIn('exterior :', result.stdout)
        for args in (["--k", "1"], ["--screen", "--a", "3", "--b", "4"],
                     ["--screen", "--k", "2"]):
            self.assertNotEqual(subprocess.run(command + args, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
