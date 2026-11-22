"""Exact non-affine row joins for the fixed-hole tripod integer system.

Every table is an original integer equation, including the endpoint and
balance coefficients. Pairwise consistency is only pruning; an empty search
tree, or a checked full sign word, is needed to decide existence.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path

import word_frontier as frontier

FORMAT = "tripod-integer-row-joins-v1"


@lru_cache(maxsize=None)
def integer_patterns(coefficients):
    """Bit p is set precisely when the sign pattern p satisfies the row."""
    return sum(1 << p for p in range(1 << len(coefficients))
               if sum(a * (1 - 2 * ((p >> i) & 1))
                      for i, a in enumerate(coefficients)) == 0)


@lru_cache(maxsize=None)
def selectors(width, positions):
    """Partition all row assignments by their bits on an ordered overlap."""
    masks = [0] * (1 << len(positions))
    for pattern in range(1 << width):
        value = sum(((pattern >> i) & 1) << j
                    for j, i in enumerate(positions))
        masks[value] |= 1 << pattern
    return tuple(masks)


def projection(domain, masks):
    return sum(1 << i for i, mask in enumerate(masks) if domain & mask)


class RowJoins:
    """A reversible relational consistency engine, with no affine hulls."""

    def __init__(self, system):
        self.system = system
        rows = list(system.rows.values())
        self.keys = [tuple(sorted(row)) for row in rows]
        self.domains = [integer_patterns(tuple(row[v] for v in key))
                        for row, key in zip(rows, self.keys)]
        # The last table fixes the centre positive, quotienting global reversal.
        self.keys.append((system.vertices.index((0, 0)),))
        self.domains.append(1)
        incidents = defaultdict(list)
        for i, key in enumerate(self.keys):
            for variable in key:
                incidents[variable].append(i)
        shared = defaultdict(list)
        for variable, containing in incidents.items():
            for pair in combinations(containing, 2):
                shared[pair].append(variable)
        self.adjacent = [[] for _ in self.keys]
        for (i, j), overlap in shared.items():
            left = selectors(len(self.keys[i]),
                             tuple(self.keys[i].index(v) for v in overlap))
            right = selectors(len(self.keys[j]),
                              tuple(self.keys[j].index(v) for v in overlap))
            self.adjacent[i].append((j, left, right))
            self.adjacent[j].append((i, right, left))
        self.edges = len(shared)
        self.trail = []
        self.revisions = 0
        self.arc_checks = 0

    def restrict(self, row, domain):
        old = self.domains[row]
        if domain & ~old:
            raise AssertionError("restriction enlarged an integer relation")
        if domain != old:
            self.trail.append((row, old))
            self.domains[row] = domain
            self.revisions += 1

    def restore(self, mark):
        while len(self.trail) > mark:
            row, domain = self.trail.pop()
            self.domains[row] = domain

    def propagate(self, changed):
        queue = deque(changed)
        pending = set(queue)
        while queue:
            i = queue.popleft()
            pending.remove(i)
            if not self.domains[i]:
                return False
            for j, left, right in self.adjacent[i]:
                self.arc_checks += 1
                allowed = projection(self.domains[i], left)
                if projection(self.domains[j], right) & ~allowed:
                    mask = sum(m for k, m in enumerate(right) if allowed >> k & 1)
                    domain = self.domains[j] & mask
                    self.restrict(j, domain)
                    if not domain:
                        return False
                    if j not in pending:
                        queue.append(j)
                        pending.add(j)
        return True

    def branch(self):
        # Fewest tuples first; prefer a larger table on a tie. All choices are
        # deterministic, so an exhaustive negative can be replayed exactly.
        best = None
        for row, domain in enumerate(self.domains):
            count = domain.bit_count()
            if count > 1:
                priority = (count, -len(self.keys[row]), row)
                if best is None or priority < best:
                    best = priority
        if best is None:
            return None
        row = best[2]
        domain = self.domains[row]
        choices = []
        for i in range(len(self.keys[row])):
            left = domain & selectors(len(self.keys[row]), (i,))[0]
            right = domain ^ left
            if left and right:
                choices.append((abs(left.bit_count() - right.bit_count()),
                                i, left, right))
        _, _, left, right = min(choices)
        return row, left, right

    def witness(self):
        values = {}
        for key, domain in zip(self.keys, self.domains):
            if domain.bit_count() != 1:
                raise AssertionError("a non-singleton relation is not a word")
            pattern = domain.bit_length() - 1
            for i, variable in enumerate(key):
                sign = 1 - 2 * ((pattern >> i) & 1)
                if variable in values and values[variable] != sign:
                    raise AssertionError("joined singleton tables disagree")
                values[variable] = sign
        if len(values) != len(self.system.vertices):
            raise AssertionError("an original sign is missing")
        # Replay all unmodified equations, independently of the row domains.
        if any(sum(a * values[v] for v, a in row.items())
               for row in self.system.rows.values()):
            raise AssertionError("candidate violates an original coefficient")
        word = {"format": "tripod-word-completion-v1",
                "lengths": list(self.system.lengths), "centre": 1}
        by_vertex = {v: values[i] for i, v in enumerate(self.system.vertices)}
        for arm, length in enumerate(self.system.lengths, 1):
            word[f"arm{arm}"] = "".join(
                "+" if by_vertex[arm, d] == 1 else "-"
                for d in range(2 if arm < 3 else 1, length + 1))
        frontier.verify(word)
        return word


def solve(lengths, *, max_nodes=10000, max_variables=24000, closure_only=False):
    for value in (max_nodes, max_variables):
        if type(value) is not int or value < 1:
            raise ValueError("resource limits must be positive integers")
    if type(closure_only) is not bool:
        raise ValueError("closure_only must be boolean")
    lengths = frontier.lengths_checked(lengths)
    result = {"format": FORMAT, "lengths": list(lengths),
              "limits": {"max_nodes": max_nodes, "max_variables": max_variables},
              "closure_only": closure_only, "existence_decided": False}
    if sum(lengths) - 1 > max_variables:
        return {**result, "status": "resource_limit", "reason": "variables"}
    engine = RowJoins(frontier.build_system(lengths))
    initial_patterns = sum(d.bit_count() for d in engine.domains)
    consistent = engine.propagate(range(len(engine.keys)))
    root_patterns = sum(d.bit_count() for d in engine.domains)
    root_revisions = engine.revisions
    engine.trail.clear()
    nodes = 1
    stack = []
    maximum_depth = 0

    def receipt(status, **extra):
        return {**result, "status": status, "nodes": nodes,
                "maximum_depth": maximum_depth, "integer_rows": len(engine.keys) - 1,
                "overlap_edges": engine.edges, "initial_patterns": initial_patterns,
                "root_patterns": root_patterns, "root_revisions": root_revisions,
                "revisions": engine.revisions, "arc_checks": engine.arc_checks, **extra}

    while True:
        if consistent:
            branch = engine.branch()
            if branch is None:
                return receipt("exact", existence_decided=True, exists=True,
                               word=engine.witness())
            if closure_only:
                return receipt("consistent_relaxation")
            if nodes >= max_nodes:
                return receipt("resource_limit", reason="nodes")
            row, left, right = branch
            stack.append((row, right, len(engine.trail)))
            maximum_depth = max(maximum_depth, len(stack))
            engine.restrict(row, left)
        else:
            if not stack:
                return receipt("exact", existence_decided=True, exists=False)
            if nodes >= max_nodes:
                return receipt("resource_limit", reason="nodes")
            row, right, mark = stack.pop()
            engine.restore(mark)
            engine.restrict(row, right)
        nodes += 1
        consistent = engine.propagate((row,))


def verify(saved):
    if type(saved) is not dict or saved.get("format") != FORMAT:
        raise ValueError("expected an integer-row-join receipt")
    limits = saved.get("limits")
    if type(limits) is not dict or set(limits) != {"max_nodes", "max_variables"}:
        raise ValueError("invalid receipt limits")
    expected = solve(saved.get("lengths"), closure_only=saved.get("closure_only"), **limits)
    if json.dumps(expected, sort_keys=True) != json.dumps(saved, sort_keys=True):
        raise ValueError("receipt differs from complete deterministic replay")
    return {"valid": True, "status": expected["status"],
            "existence_decided": expected["existence_decided"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lengths", type=int, nargs=3)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--max-nodes", type=int, default=10000)
    parser.add_argument("--max-variables", type=int, default=24000)
    parser.add_argument("--closure-only", action="store_true")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.verify:
            result = verify(json.loads(args.verify.read_text()))
        else:
            result = solve(args.lengths, max_nodes=args.max_nodes,
                           max_variables=args.max_variables, closure_only=args.closure_only)
        if args.write:
            args.write.write_text(json.dumps(result, indent=2) + "\n")
        summary = {k: v for k, v in result.items() if k != "word"}
        if "word" in result:
            summary["word_saved"] = bool(args.write)
            summary["word_size"] = sum(args.lengths) - 1
        print(json.dumps(summary, indent=2))
        return 2 if result["status"] == "resource_limit" else 0
    except (ValueError, OSError, TypeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
