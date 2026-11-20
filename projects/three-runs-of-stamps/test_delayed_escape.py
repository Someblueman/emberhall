"""Independent finite checks for the delayed valley family."""
import itertools
from pathlib import Path
import subprocess
import sys
import unittest

from delayed_escape import (adjacent, census, delayed_prefixes, equal_tail_formula,
                            extend, first_internal, gaps)


def legal(order, assignment):
    """Full permutation predicate, with no gap sweep or insertion history."""
    if sorted(order) != list(range(len(assignment) + 1)):
        return False
    at = {label: position for position, label in enumerate(order)}
    for i, symbol in enumerate(assignment):
        if (at[i] < at[i + 1]) != ((symbol == "V") == (i % 2 == 0)):
            return False
        for j in range(i + 2, len(assignment), 2):
            ends = sorted((at[i], at[i + 1]))
            if (ends[0] < at[j] < ends[1]) != (ends[0] < at[j + 1] < ends[1]):
                return False
    return True


def signature_family(order, a, b, escape):
    """Recover insertion positions by restriction, independently of generation."""
    for step in range(1, b + 1):
        last = a + step
        prefix = tuple(x for x in order if x <= last)
        is_adjacent = abs(prefix.index(last) - prefix.index(last - 1)) == 1
        if is_adjacent != (step != escape):
            return False
    return True


class DelayedEscapeTests(unittest.TestCase):
    def test_sweep_against_all_permutations_through_six_faces(self):
        for n in range(1, 7):
            for symbols in itertools.product("MV", repeat=n - 1):
                assignment = "".join(symbols)
                expected = {p for p in itertools.permutations(range(n)) if legal(p, assignment)}
                actual = list(extend((0,), assignment))
                self.assertEqual(set(actual), expected, assignment)
                self.assertEqual(len(actual), len(set(actual)))

    def test_entire_seven_face_universe(self):
        actual = {s for p in delayed_prefixes(2, 2) for s in extend(p, "MM")}
        expected = {s for s in itertools.permutations(range(7))
                    if legal(s, "MMVVMM") and signature_family(s, 2, 2, 2)}
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 5)

    def test_trapping_after_an_adjacent_same_symbol_step(self):
        # This is a local lemma, so challenge every legal short prefix, not
        # just mountain/valley families or the examples used in its proof.
        for n in range(2, 7):
            for symbols in itertools.product("MV", repeat=n - 1):
                assignment = "".join(symbols)
                for prefix in extend((0,), assignment):
                    folded = adjacent(prefix, assignment[-1])
                    for _ in range(4):
                        self.assertEqual(list(gaps(folded, assignment[-1])),
                                         [adjacent(folded, assignment[-1]).index(len(folded))])
                        folded = adjacent(folded, assignment[-1])

    def test_no_delayed_escape_after_step_two(self):
        for a in range(2, 9):
            for b in range(3, 10):
                for escape in range(3, b + 1):
                    self.assertEqual(list(delayed_prefixes(a, b, escape)), [])

    def test_exact_base_cases_and_prefix_classes(self):
        for a in range(2, 13):
            for b in (2, 3):
                prefixes = list(delayed_prefixes(a, b))
                self.assertEqual(len(prefixes), a if a <= 3 else a + 1)
                self.assertEqual(len(prefixes), len(set(prefixes)))
                buckets = {}
                for p in prefixes:
                    q = tuple(x for x in p if x <= a)
                    t = first_internal(q)
                    buckets.setdefault(t, []).append(sum(1 for _ in extend(p, "M" * b)))
                    self.assertTrue(legal(p, "M" * a + "V" * b))
                    self.assertTrue(signature_family(p, a, b, 2))
                self.assertEqual(buckets[None], [b if b == 2 else 4])
                self.assertEqual(buckets[a], [3 if b == 2 else 5])
                if a == 3:
                    self.assertEqual(buckets[2], [4 if b == 2 else 6])
                elif a >= 4:
                    self.assertEqual(sorted(buckets[a - 1]), [2, 4] if b == 2 else [6, 7])
                    for t in range(2, a - 1):
                        self.assertEqual(buckets[t], [2 if b == 2 else 4])

    def test_collar_bijection_not_only_cardinality(self):
        for a in range(2, 8):
            for prefix in delayed_prefixes(a, 3):
                n = len(prefix)
                larger = adjacent(prefix, "V")
                for length in range(1, 5):
                    collapsed, stopped = [], []
                    for order in extend(larger, "M" * (length + 1)):
                        early = tuple(x for x in order if x <= n + 2)
                        if min(early.index(n), early.index(n + 1)) < early.index(n + 2) < max(
                                early.index(n), early.index(n + 1)):
                            stopped.append(order)
                        else:
                            collapsed.append(tuple(x if x < n else x - 2 for x in order
                                                   if x not in (n, n + 1)))
                    self.assertEqual(len(stopped), 1)
                    self.assertEqual(len(collapsed), len(set(collapsed)))
                    self.assertEqual(set(collapsed), set(extend(prefix, "M" * length)))

    def test_symbolic_three_step_gap_trees(self):
        # Each string is one complete row/branch of the proof's symbolic table.
        common = ["x3,w x3,z1 z2,z1", "a,x1 a,z1 z2,z1"]
        trees = {
            "deep": common + ["x3,w u,x2 z2,x2", "x3,w u,x2 x1,v"],
            "exterior": common + ["x3,w -,x2 z2,x2", "x3,w -,x2 x1,+"],
            "last": common + ["x3,w -,x2 z2,x2", "x3,w -,x2 x1,r0",
                               "x3,w -,x2 v,+"],
            "near": common + ["x3,w -,u z2,u", "x3,w -,u v,+",
                               "x3,w h,x2 z2,x2", "x3,w h,x2 x1,v"],
            "far": ["x3,l u,x2 z2,x2", "x3,l u,x2 x1,v",
                    "x3,l x3,z1 z2,z1", "h,w -,u z2,u", "h,w -,u v,+",
                    "h,w h,z1 z2,z1", "a,x1 a,z1 z2,z1"],
        }
        for a in range(2, 13):
            for prefix in delayed_prefixes(a, 3):
                normal = prefix if a % 2 == 0 else prefix[::-1]
                t = first_internal(tuple(x for x in prefix if x <= a))
                r = [x for x in normal if x <= a - 4]
                kind = "exterior" if t is None else "last" if t == a else "deep"
                if t == a - 1:
                    kind = "near" if not r or normal.index(a + 2) > normal.index(r[-1]) else "far"
                last_r = [x for x in normal if x <= a - 3]
                names = dict(a=a, u=a-3, v=a-2, w=a-1, x1=a+1, x2=a+2,
                             x3=a+3, z1=a+4, z2=a+5, h=r[-1] if r else a-3,
                             l=r[0] if r else None, r0=last_r[0] if last_r else a-2)
                names.update({"-": None, "+": None})
                expected = {tuple(tuple(names[x] for x in gap.split(","))
                                  for gap in row.split()) for row in trees[kind]}
                actual = set()
                for order in extend(prefix, "MMM"):
                    trace = []
                    for new in range(a + 4, a + 7):
                        small = tuple(x for x in order if x <= new)
                        if a % 2:
                            small = small[::-1]
                        at = small.index(new)
                        trace.append((small[at-1] if at else None,
                                      small[at+1] if at+1 < len(small) else None))
                    actual.add(tuple(trace))
                self.assertEqual(actual, expected, (a, t, kind))

    def test_closed_formula_unequal_lengths_and_both_parities(self):
        for a in range(2, 11):
            for b in range(2, 11):
                prefixes, totals = census(a, b, b)
                self.assertEqual(sum(totals.values()), equal_tail_formula(a, b), (a, b))
                self.assertEqual(prefixes, a if a <= 3 else a + 1)

    def test_failed_uniform_formula_has_a_concrete_counterexample(self):
        self.assertNotEqual(census(3, 3, 3)[1].total(), (3 + 1) * 3 + 3 + 7)
        prefix = (1, 4, 3, 2, 6, 5, 0)
        self.assertIn(prefix, set(delayed_prefixes(3, 3)))
        self.assertEqual(len(list(extend(prefix, "MMM"))), 6)

    def test_native_command_and_invalid_input(self):
        command = [sys.executable, str(Path(__file__).with_name("delayed_escape.py"))]
        result = subprocess.run(command + ["--k", "4"], capture_output=True, text=True, check=True)
        self.assertIn("5 prefixes; 31 completions", result.stdout)
        self.assertIn("author formula: 31", result.stdout)
        for args in (["--k", "1"], ["--escape", "1"], ["--c", "-1"]):
            self.assertNotEqual(subprocess.run(command + args, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
