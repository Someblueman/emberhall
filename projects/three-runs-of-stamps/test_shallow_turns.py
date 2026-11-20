"""Independent whole-set and boundary challenges to the shallow-turn proof."""
import subprocess
import sys
import unittest
from pathlib import Path

from reconstruction import extend, inward_step, legal
from shallow_turns import (Parameter, constructed, expand, expected_weights,
                           frontiers, mountain, parameters, prefixes, recover)


def next_orders(prefix, word, symbol):
    """Full matching predicate; no named-gap constructor or signature sweep."""
    label = len(prefix)
    return {prefix[:i] + (label,) + prefix[i:] for i in range(label+1)
            if legal(prefix[:i] + (label,) + prefix[i:], word+symbol)}


def independent_prefixes(a, r, d):
    mountains = {p for p in extend((0,), "M"*a) if inward_step(p) == a-d}
    states = mountains
    for j in range(1, r+1):
        children = {child for p in states
                    for child in next_orders(p, "M"*a+"V"*(j-1), "V")}
        # No adjacency condition on V1; precisely the first adjacency at Vr.
        states = {p for p in children if j == 1 or
                  (abs(p.index(a+j)-p.index(a+j-1)) == 1) == (j == r)}
    return states


def boundary(prefix):
    """Compute enclosing arc and maximal children ahead from raw positions."""
    rank = {v: i for i, v in enumerate(prefix)}
    last = len(prefix)-1
    arcs = []
    for edge in range(last % 2, last, 2):
        lo, hi = sorted((rank[edge], rank[edge+1]))
        arcs.append((lo, hi, edge))
    parents = [arc for arc in arcs if arc[0] < rank[last] < arc[1]]
    parent = min(parents, key=lambda arc: arc[1]-arc[0]) if parents else (
        -1, len(prefix), None)
    inside = [arc for arc in arcs if parent[0] <= arc[0] and arc[1] <= parent[1]
              and not arc[0] < rank[last] < arc[1]]
    maximal = [arc for arc in inside if not any(
        other[0] < arc[0] and arc[1] < other[1] for other in inside)]
    ahead = [arc[2] for arc in maximal if
             (arc[0] > rank[last] if last % 2 else arc[1] < rank[last])]
    return parent[2], set(ahead)


def expected_boundary(path, j, a, r, d):
    """The document's table, at the moment before M_j is inserted."""
    t = a-d
    x = lambda i: a+i
    y = lambda i: a+r+i
    if path == "A-main":
        return a-r+j-3, {x(r-j+1)}
    if path == "A-return":
        children = {a-r+j-3}
        if j == r-d-1:
            children.add(t)
        return x(r-j-1), children
    if path == "B-main":
        children = {x(r-j+1)}
        if j == r-d-3:
            children.add(x(d))
        return a-r+j+1, children
    if path == "B-return":
        return x(r-j-1), {a-r+j+1} if j < r-1 else set()
    if path in ("A-inner", "B-inner"):
        start = r-d-1 if path[0] == "A" else r-d-3
        h = j-start
        if path[0] == "A":
            return x(d-h), {t+h} if h < d else set()
        return t+h-2, {x(d-h)} if h <= d else set()
    if path in ("A-outer", "B-outer"):
        start = r-d-1 if path[0] == "A" else r-d-3
        if j == start+1:
            return None, {t-3 if path[0] == "A" else x(d+3)}
        if j == start+2:
            return None, {t-2 if path[0] == "A" else x(d+2)}
        if j == start+3:
            return None, {y(start), t-1 if path[0] == "A" else x(d+1)}
        return None, {y(j-3)}
    if path in ("A-slow", "B-slow"):
        start = r-d+2 if path[0] == "A" else r-d
        h = j-start
        if path[0] == "A":
            return x(d-h+1), {t+h-1}
        return t+h-3, {x(d-h+1)}
    if path == "C-outer":
        if j == 2:
            return None, {x(r-1)}
        if j == 3:
            return None, {x(r-2)}
        if j == 4:
            return None, {y(1), x(r-3)}
        return None, {y(j-3)}
    if path in ("C-return", "C-slow"):
        effective = j if path == "C-return" else j-4
        if effective == r-d-4:
            return x(d+3), {t-3, x(d+1)}
        return x(r-effective-1), {x(r-effective-3)}
    start = r-d-4 + (4 if "late" in path else 0)
    h = j-start
    if path.endswith("first"):
        return x(d+3-h), {t+h-3} if h < d+3 else set()
    return t+h-3, {x(d+1-h)} if h < d+2 else set()


class ShallowTurnTests(unittest.TestCase):
    def test_entire_prefix_census_with_independent_matching(self):
        for r in range(6, 13):
            for d in range(1, r-4):
                for a in (r+1, r+2, r+5):
                    with self.subTest(a=a, r=r, d=d):
                        want = prefixes(a, r, d)
                        self.assertEqual(set(want.values()), independent_prefixes(a, r, d))
                        self.assertEqual(len(set(want.values())), 3)
                        self.assertEqual(inward_step(mountain(a, d)), a-d)

    def test_every_frontier_full_completion_and_inverse(self):
        for r in range(6, 13):
            for d in range(1, r-4):
                for a in (r+1, r+2, r+5):
                    bases = prefixes(a, r, d)
                    for family, base in bases.items():
                        with self.subTest(a=a, r=r, d=d, family=family):
                            states = {base}
                            for j, named in enumerate(frontiers(a, r, d, family), 1):
                                states = {q for p in states for q in next_orders(
                                    p, "M"*a+"V"*r+"M"*(j-1), "M") if j == 1 or
                                    abs(q.index(a+r+j)-q.index(a+r+j-1)) != 1}
                                self.assertEqual(states, set(named.values()))
                                self.assertEqual(len(states), len(named))
                            result = constructed(a, r, d, family)
                            self.assertEqual(result, set(extend(base, "M"*a+"V"*r+"M"*r)))
                            self.assertEqual(len(result), expected_weights(r, d)[family])
                            labels = list(parameters(a, r, d, family))
                            self.assertEqual(len(labels), len(result))
                            self.assertEqual({recover(q, a, r, d) for q in result}, set(labels))
                            for label in labels:
                                self.assertEqual(recover(expand(a, r, d, label), a, r, d), label)

    def test_valley_boundary_induction(self):
        for r in range(6, 19):
            for d in range(1, r-4):
                for a in (r+1, r+2, r+6):
                    t = a-d
                    for family, order in prefixes(a, r, d).items():
                        for j in range(1, r):
                            before = tuple(v for v in order if v < a+j)
                            if j == 1:
                                expected = (a-2, set())
                            elif j <= d:
                                expected = (a-j-1, {a-j+1})
                            elif j == d+1:
                                expected = (t-2, {t-4, t})
                            elif family == "A":
                                child = a-j-3
                                expected = (a-j-1, {child} if child >= 0 else set())
                            elif j <= d+3:
                                expected = (None, {t+d+1-j})
                            elif j == d+4:
                                expected = (None, {t-3, a+d+1})
                            elif family == "B":
                                expected = (a-j+3, {a-j+1})
                            else:
                                expected = (None, {a+j-3})
                            # Reflection reverses direction without changing arcs.
                            self.assertEqual(boundary(before[::-1]), expected,
                                             (a, r, d, family, j))

    def test_symbolic_arc_boundaries_including_coincident_events(self):
        # All paths, both parities, d=1, r=d+5, and long separated phases.
        for r in range(6, 22):
            for d in range(1, r-4):
                for a in (r+1, r+2, r+7):
                    for family in "ABC":
                        for j, states in enumerate(frontiers(a, r, d, family), 2):
                            if j > r:
                                continue
                            for path, state in states.items():
                                self.assertEqual(boundary(state), expected_boundary(path, j, a, r, d),
                                                 (a, r, d, path, j))

    def test_large_named_constructions_are_legal(self):
        for a, r, d in ((52, 45, 1), (52, 45, 20), (46, 45, 40), (83, 60, 31)):
            for family in "ABC":
                result = constructed(a, r, d, family)
                self.assertEqual(len(result), expected_weights(r, d)[family])
                for order in result:
                    self.assertTrue(legal(order, "M"*a+"V"*r+"M"*r))
                    self.assertEqual(expand(a, r, d, recover(order, a, r, d)), order)

    def test_invalid_shapes_and_corrupted_orders(self):
        for args in ((6, 6, 1), (8, 5, 1), (9, 6, 0), (9, 6, 2)):
            with self.assertRaises(ValueError):
                prefixes(*args)
        for label in (Parameter("D", 2, "D-main"), Parameter("A", 0, "A-main"),
                      Parameter("A", 6, "A-inner")):
            with self.assertRaises(ValueError):
                expand(7, 6, 1, label)
        good = expand(7, 6, 1, Parameter("A", 1, "A-main"))
        for bad in (good[:-1], (0,)*len(good), good[::-1], good[:-2]+good[-2:][::-1]):
            with self.assertRaises(ValueError):
                recover(bad, 7, 6, 1)

    def test_native_command(self):
        command = [sys.executable, str(Path(__file__).with_name("shallow_turns.py"))]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertIn("A: 23 complete labeled stacks", result.stdout)
        self.assertIn("B: 24 complete labeled stacks", result.stdout)
        self.assertIn("C: 32 complete labeled stacks", result.stdout)
        bad = subprocess.run(command+["--r", "5"], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("require r >= 6", bad.stderr)


if __name__ == "__main__":
    unittest.main()
