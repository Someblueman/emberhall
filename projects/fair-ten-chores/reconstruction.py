"""Independent finite reconstruction; no imports from the author's checker.

Run with Python 3.10+. Certificates are transient Python data, not large files
committed to the repository. See RECONSTRUCTION.md for the mathematical bridge.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from itertools import combinations, permutations, product
import json
from pathlib import Path
import time


@dataclass
class Complex:
    vertices: list[tuple[int, ...]]
    edges: list[tuple[int, int]]
    triangles: list[tuple[int, int, int]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def assignments(size: int, conflicts: list[tuple[int, int]]) -> list[tuple[int, ...]]:
    """Partition into independent sets, rather than filtering all 3**size words."""
    universe = frozenset(range(size))
    independent = [frozenset(i for i in range(size) if mask >> i & 1)
                   for mask in range(1 << size)
                   if all(not (mask >> a & 1 and mask >> b & 1)
                          for a, b in conflicts)]
    allowed = set(independent)
    result = []
    for first in independent:
        for second in independent:
            if first & second:
                continue
            third = universe - first - second
            if third in allowed:
                result.append(tuple(0 if i in first else 1 if i in second else 2
                                    for i in range(size)))
    return sorted(result)


def bundles(word: tuple[int, ...]) -> tuple[frozenset[int], ...]:
    return tuple(frozenset(i for i, owner in enumerate(word) if owner == c)
                 for c in range(3))


def build(size: int, conflicts: list[tuple[int, int]]) -> Complex:
    vertices = assignments(size, conflicts)
    parts = [bundles(word) for word in vertices]
    edges = [(i, j) for i, j in combinations(range(len(vertices)), 2)
             if all(len(a - b) <= 1 and len(b - a) <= 1
                    for a, b in zip(parts[i], parts[j]))]
    adjacent = [set() for _ in vertices]
    for i, j in edges:
        adjacent[i].add(j)
        adjacent[j].add(i)
    triangles = [(i, j, k) for i, j in edges
                 for k in sorted(adjacent[i] & adjacent[j]) if k > j]
    return Complex(vertices, edges, triangles)


def exchange_edges(vertices: list[tuple[int, ...]]) -> set[tuple[int, int]]:
    """Separate enumeration: move <=1 item out of/into each of three labels."""
    indices = {word: i for i, word in enumerate(vertices)}
    result = set()
    for i, word in enumerate(vertices):
        options = [(None, *sorted(b)) for b in bundles(word)]
        for choices in product(*options):
            sources = [c for c in range(3) if choices[c] is not None]
            for targets in permutations(range(3), len(sources)):
                if any(c == d for c, d in zip(sources, targets)):
                    continue
                other = list(word)
                for c, d in zip(sources, targets):
                    other[choices[c]] = d
                j = indices.get(tuple(other))
                if j is not None and i < j:
                    result.add((i, j))
    return result


def spanning_tree(complex_: Complex) -> list[tuple[int, int]]:
    """Depth-first tree, deliberately different from the exploratory BFS tree."""
    adjacent = [[] for _ in complex_.vertices]
    for i, j in complex_.edges:
        adjacent[i].append(j)
        adjacent[j].append(i)
    seen = {0}
    stack = [(0, iter(adjacent[0]))]
    result = []
    while stack:
        i, neighbours = stack[-1]
        j = next(neighbours, None)
        if j is None:
            stack.pop()
        elif j not in seen:
            seen.add(j)
            result.append((min(i, j), max(i, j)))
            stack.append((j, iter(adjacent[j])))
    require(len(seen) == len(complex_.vertices), "disconnected allocation graph")
    return result


def reduce_word(word) -> tuple[int, ...]:
    """Only free cancellation and cyclic conjugation, never commutation."""
    stack = []
    for letter in word:
        if letter == 0:
            continue
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    left, right = 0, len(stack)
    while right - left >= 2 and stack[left] == -stack[right - 1]:
        left += 1
        right -= 1
    return tuple(stack[left:right])


def boundary_words(complex_: Complex) -> list[tuple[int, int, int]]:
    labels = {edge: i + 1 for i, edge in enumerate(complex_.edges)}
    return [(labels[i, j], labels[j, k], -labels[i, k])
            for i, j, k in complex_.triangles]


def deduction(word: tuple[int, ...]) -> tuple[int, int] | None:
    if len(word) == 1:
        return abs(word[0]), 0
    if len(word) != 2 or abs(word[0]) == abs(word[1]):
        # x*x=1 is torsion, not x=1. x*x^-1 was already cancelled.
        return None
    a, b = word
    if abs(a) > abs(b):
        return abs(a), -b if a > 0 else b
    return abs(b), -a if b > 0 else a


def derive(complex_: Complex) -> dict:
    """Rewrite affected triangle words explicitly, maintaining their order."""
    tree = spanning_tree(complex_)
    labels = {edge: i + 1 for i, edge in enumerate(complex_.edges)}
    dead = {labels[edge] for edge in tree}
    boundaries = boundary_words(complex_)
    words = [reduce_word(x for x in word if abs(x) not in dead)
             for word in boundaries]
    occurrences = [set() for _ in range(len(complex_.edges) + 1)]
    for row, word in enumerate(words):
        for letter in word:
            occurrences[abs(letter)].add(row)
    pending = deque(range(len(words)))
    steps = []
    while pending:
        row = pending.popleft()
        rule = deduction(words[row])
        if rule is None:
            continue
        victim, replacement = rule
        require(victim not in dead, "eliminating an already dead generator")
        steps.append((row, victim, replacement))
        dead.add(victim)
        for changed in sorted(occurrences[victim]):
            old = words[changed]
            for letter in old:
                occurrences[abs(letter)].discard(changed)
            new = reduce_word(replacement if x == victim else
                              -replacement if x == -victim else x for x in old)
            words[changed] = new
            for letter in new:
                occurrences[abs(letter)].add(changed)
            pending.append(changed)
    return {"vertices": complex_.vertices, "edges": complex_.edges,
            "boundaries": boundaries, "tree": tree, "steps": steps,
            "remaining": len(complex_.edges) - len(dead)}


def verify(complex_: Complex, certificate: dict, complete: bool = True) -> int:
    """Replay from original boundaries via signed substitution chains.

    This does not trust the producer's mutable words, incidence index, remaining
    count, or choice of eliminations. Arbitrary valid spanning trees are allowed.
    """
    require(certificate["vertices"] == complex_.vertices, "assignment list differs")
    require(certificate["edges"] == complex_.edges, "exchange edge list differs")
    expected = boundary_words(complex_)
    require(certificate["boundaries"] == expected, "oriented triangle differs")
    labels = {edge: i + 1 for i, edge in enumerate(complex_.edges)}
    tree = certificate["tree"]
    require(len(set(tree)) == len(tree) == len(complex_.vertices) - 1,
            "wrong tree size")
    components = list(range(len(complex_.vertices)))
    def root(i):
        while components[i] != i:
            i = components[i]
        return i
    substitutions = {}
    for edge in tree:
        require(edge in labels, "tree edge absent")
        i, j = map(root, edge)
        require(i != j, "tree has a cycle")
        components[i] = j
        substitutions[labels[edge]] = 0
    require(len({root(i) for i in range(len(components))}) == 1, "tree disconnected")
    def expand(letter):
        sign = 1
        while letter:
            if letter < 0:
                sign = -sign
                letter = -letter
            if letter not in substitutions:
                return sign * letter
            letter = substitutions[letter]
        return 0
    for row, victim, replacement in certificate["steps"]:
        require(0 <= row < len(expected), "unknown triangle")
        require(1 <= victim <= len(complex_.edges) and victim not in substitutions,
                "invalid eliminated generator")
        require(replacement == 0 or
                (1 <= abs(replacement) <= len(complex_.edges) and
                 abs(replacement) not in substitutions and abs(replacement) != victim),
                "replacement must be another live generator")
        word = reduce_word(expand(x) for x in expected[row])
        require(sum(abs(x) == victim for x in word) == 1,
                "triangle does not solve uniquely for generator")
        # Check the proposed substitution makes this relation literally trivial.
        after = reduce_word(replacement if x == victim else
                            -replacement if x == -victim else x for x in word)
        require(after == (), "signed triangle deduction is invalid")
        substitutions[victim] = replacement
    remaining = sum(expand(i) != 0 for i in range(1, len(complex_.edges) + 1))
    # Multiple original generators may represent one survivor; count live roots.
    roots = {abs(expand(i)) for i in range(1, len(complex_.edges) + 1)} - {0}
    if complete:
        require(remaining == 0, f"{len(roots)} generators remain unproved")
    require(certificate["remaining"] == len(roots), "producer's residual count differs")
    return len(roots)


def cyclic_check(complex_: Complex) -> None:
    indices = {word: i for i, word in enumerate(complex_.vertices)}
    rotation = [indices[tuple((x + 1) % 3 for x in word)]
                for word in complex_.vertices]
    edge_set, triangle_set = set(complex_.edges), set(complex_.triangles)
    require(all(tuple(sorted((rotation[a], rotation[b]))) in edge_set
                for a, b in complex_.edges), "cyclic action loses an edge")
    require(all(tuple(sorted(rotation[x] for x in tri)) in triangle_set
                for tri in complex_.triangles), "cyclic action loses a triangle")


def expect_rejected(action, label: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(f"accepted poison: {label}")


def poisons(complex_: Complex, certificate: dict) -> None:
    changed = dict(certificate, vertices=certificate["vertices"][:-1])
    expect_rejected(lambda: verify(complex_, changed), "missing assignment")
    changed = dict(certificate, edges=certificate["edges"][:-1])
    expect_rejected(lambda: verify(complex_, changed), "changed edge")
    boundaries = list(certificate["boundaries"])
    a, b, c = boundaries[0]
    boundaries[0] = (a, b, -c)
    changed = dict(certificate, boundaries=boundaries)
    expect_rejected(lambda: verify(complex_, changed), "reversed boundary letter")
    row, victim, replacement = next(step for step in certificate["steps"] if step[2])
    steps = list(certificate["steps"])
    index = steps.index((row, victim, replacement))
    steps[index] = (row, victim, -replacement)
    changed = dict(certificate, steps=steps)
    expect_rejected(lambda: verify(complex_, changed), "wrong signed substitution")
    require(reduce_word((1, 2, -1, -2)) == (1, 2, -1, -2), "commuted letters")
    require(deduction((1, 1)) is None, "killed an order-two generator")


def chore_ef1(word: tuple[int, ...], costs) -> bool:
    parts = bundles(word)
    return all(min([costs[i](own)] + [costs[i](own - {g}) for g in own]) <= costs[i](other)
               for i, own in enumerate(parts) for other in parts)


def negative_control() -> dict:
    conflicts = [(a, b) for a in range(3) for b in range(3, 6)] + [(0, 6), (3, 6)]
    complex_ = build(7, conflicts)
    certificate = derive(complex_)
    remaining = verify(complex_, certificate, complete=False)
    require(remaining > 0, "falsely certified published obstruction")
    expect_rejected(lambda: verify(complex_, certificate), "seven-item topology")
    special = {frozenset((i, 6)) for i in (1, 2, 4, 5)}
    def cost(items):
        if not items:
            return 0
        if len(items) == 1:
            return 1 if next(iter(items)) in (0, 3) else 2
        return 3 if items in special else 4
    subsets = [frozenset(i for i in range(7) if mask >> i & 1) for mask in range(128)]
    require(all(cost(a) <= cost(a | {i}) for a in subsets for i in range(7)),
            "negative-control cost is not monotone")
    fair = sum(chore_ef1(word, [cost] * 3) for word in complex_.vertices)
    require(fair == 0, "published negative control unexpectedly fair")
    return {"vertices": len(complex_.vertices), "edges": len(complex_.edges),
            "triangles": len(complex_.triangles), "surviving_generators": remaining,
            "chore_EF1_assignments": fair}


def compare_author(complex_: Complex, author: dict) -> int:
    """Translate the author's frozen JSON, then replay using only our own code."""
    require(isinstance(author, dict) and set(author) == {"words", "edges", "tree", "steps"},
            "unexpected author certificate fields")
    require(author["words"] == ["".join(map(str, word)) for word in complex_.vertices],
            "author assignment list differs")
    require(isinstance(author["edges"], list) and
            all(isinstance(e, list) and len(e) == 2 and
                all(type(x) is int for x in e) for e in author["edges"]) and
            author["edges"] == [list(e) for e in complex_.edges], "author edges differ")
    tree = author["tree"]
    require(isinstance(tree, list) and
            all(type(x) is int and 1 <= x <= len(complex_.edges) for x in tree),
            "author tree has an invalid edge number")
    boundaries = boundary_words(complex_)
    rows = {word: i for i, word in enumerate(boundaries)}
    known, steps = set(tree), []
    require(isinstance(author["steps"], list), "author steps must be a list")
    for word in author["steps"]:
        require(isinstance(word, list) and len(word) == 3 and
                all(type(x) is int for x in word) and tuple(word) in rows,
                "author step is not an independently reconstructed oriented triangle")
        unknown = [abs(x) for x in word if abs(x) not in known]
        require(len(unknown) == 1, "author step does not eliminate exactly one generator")
        steps.append((rows[tuple(word)], unknown[0], 0))
        known.add(unknown[0])
    translated = {"vertices": complex_.vertices, "edges": complex_.edges,
                  "boundaries": boundaries, "tree": [complex_.edges[x - 1] for x in tree],
                  "steps": steps, "remaining": 0}
    verify(complex_, translated)
    return len(steps)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-items", type=int, choices=range(4, 11), default=10)
    parser.add_argument("--author-certificate", type=Path,
                        help="independently replay a JSON certificate written by check.py")
    args = parser.parse_args()
    start = time.monotonic()
    for size in range(args.max_items + 1):
        complex_ = build(size, [(i, i + 1) for i in range(size - 1)])
        require(len(complex_.vertices) == (1 if size == 0 else 3 * 2 ** (size - 1)),
                "path assignment count")
        require(exchange_edges(complex_.vertices) == set(complex_.edges),
                "independent move enumeration disagrees")
        cyclic_check(complex_)
        certificate = derive(complex_)
        verify(complex_, certificate)
        require(all(chore_ef1(word, [lambda _: 0] * 3) for word in complex_.vertices),
                "zero-cost boundary")
        if size == args.max_items:
            poisons(complex_, certificate)
        print(json.dumps({"items": size, "vertices": len(complex_.vertices),
                          "edges": len(complex_.edges), "triangles": len(complex_.triangles),
                          "deductions": len(certificate["steps"]), "remaining": 0}), flush=True)
    print(json.dumps({"negative_control": negative_control()}), flush=True)
    if args.author_certificate:
        author = json.loads(args.author_certificate.read_text(encoding="utf-8"))
        count = compare_author(complex_, author)
        for field in ("words", "edges"):
            changed = dict(author, **{field: author[field][:-1]})
            expect_rejected(lambda: compare_author(complex_, changed), f"author {field}")
        steps = [list(word) for word in author["steps"]]
        steps[0][0] *= -1
        expect_rejected(lambda: compare_author(complex_, dict(author, steps=steps)),
                        "author reversed triangle edge")
        print(f"PASS author comparison: {count} signed steps; three author poisons rejected")
    print(f"PASS independent reconstruction; four poisons rejected; {time.monotonic()-start:.3f}s")


if __name__ == "__main__":
    main()
