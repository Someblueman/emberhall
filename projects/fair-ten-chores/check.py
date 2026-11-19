"""Build and replay a triangle certificate for the three-agent chore problem."""

import argparse
from collections import deque
from dataclasses import dataclass
from itertools import combinations, product
import json
from pathlib import Path
import sys


@dataclass
class Complex:
    words: list[str]
    edges: list[tuple[int, int]]
    neighbors: list[set[int]]
    boundaries: list[tuple[int, int, int]]


def reconstruct(size, conflicts):
    words = [
        "".join(colors) for colors in product("012", repeat=size)
        if all(colors[i] != colors[j] for i, j in conflicts)
    ]
    masks = [
        [sum(1 << i for i, c in enumerate(word) if c == color) for color in "012"]
        for word in words
    ]
    neighbors = [set() for _ in words]
    numbers = {}
    for u, v in combinations(range(len(words)), 2):
        if all((a & ~b).bit_count() <= 1 and (b & ~a).bit_count() <= 1
               for a, b in zip(masks[u], masks[v])):
            numbers[u, v] = len(numbers) + 1
            neighbors[u].add(v)
            neighbors[v].add(u)
    boundaries = [
        (numbers[u, v], numbers[v, w], -numbers[u, w])
        for u, v in numbers for w in sorted(neighbors[u] & neighbors[v]) if v < w
    ]
    return Complex(words, list(numbers), neighbors, boundaries)


def make_certificate(graph):
    queue = deque([0])
    visited = {0}
    numbers = {edge: i for i, edge in enumerate(graph.edges, 1)}
    tree = []
    while queue:
        u = queue.popleft()
        for v in sorted(graph.neighbors[u] - visited):
            visited.add(v)
            queue.append(v)
            tree.append(numbers[min(u, v), max(u, v)])

    trivial = set(tree)
    steps = []
    while True:
        before = len(trivial)
        for boundary in graph.boundaries:
            unknown = [abs(letter) for letter in boundary if abs(letter) not in trivial]
            if len(unknown) == 1:
                steps.append(list(boundary))
                trivial.add(unknown[0])
        if len(trivial) == before:
            break
    return {"words": graph.words.copy(), "edges": [list(e) for e in graph.edges],
            "tree": tree, "steps": steps}


class InvalidProof(ValueError):
    pass


def verify(graph, certificate):
    """Trust no search steps. Reconstruct directed walks and replay in given order."""
    if not isinstance(certificate, dict) or set(certificate) != {"words", "edges", "tree", "steps"}:
        raise InvalidProof("expected a table of assignments, edges, tree and steps")
    if certificate["words"] != graph.words:
        raise InvalidProof("assignment list differs from all legal colorings")
    edges = certificate["edges"]
    if not isinstance(edges, list) or len(edges) != len(graph.edges):
        raise InvalidProof("edge count differs from the reconstructed graph")
    for supplied, expected in zip(edges, graph.edges):
        if (not isinstance(supplied, list) or len(supplied) != 2
                or any(type(endpoint) is not int for endpoint in supplied)
                or tuple(supplied) != expected):
            raise InvalidProof("edge differs from the reconstructed exchanges")

    tree = certificate["tree"]
    if not isinstance(tree, list) or len(tree) != len(graph.words) - 1:
        raise InvalidProof("a spanning tree needs one fewer edge than vertices")
    tree_neighbors = [[] for _ in graph.words]
    for i in tree:
        if type(i) is not int or not 1 <= i <= len(edges):
            raise InvalidProof("invalid tree edge")
        u, v = edges[i - 1]
        tree_neighbors[u].append(v)
        tree_neighbors[v].append(u)
    visited = {0}
    pending = [0]
    while pending:
        for neighbor in tree_neighbors[pending.pop()]:
            if neighbor not in visited:
                visited.add(neighbor)
                pending.append(neighbor)
    if len(visited) != len(graph.words):
        raise InvalidProof("tree does not reach every assignment")

    known = set(tree)
    if not isinstance(certificate["steps"], list):
        raise InvalidProof("expected an ordered list of triangle reductions")
    for index, boundary in enumerate(certificate["steps"], 1):
        if (not isinstance(boundary, list) or len(boundary) != 3
                or any(type(x) is not int or not 1 <= abs(x) <= len(edges) for x in boundary)):
            raise InvalidProof(f"step {index} has an invalid signed edge")
        walk = [edges[x - 1] if x > 0 else edges[-x - 1][::-1] for x in boundary]
        if any(walk[i][1] != walk[(i + 1) % 3][0] for i in range(3)):
            raise InvalidProof(f"step {index} is not an oriented triangle boundary")
        remaining = [x for x in boundary if abs(x) not in known]
        if len(remaining) != 1:
            raise InvalidProof(f"step {index} must have exactly one unproved letter")
        known.add(abs(remaining[0]))
    missing = len(edges) - len(known)
    if missing:
        message = "1 edge generator remains" if missing == 1 else f"{missing} edge generators remain"
        raise InvalidProof(f"{message} unproved")


def obstruction_cost(bundle):
    if not bundle:
        return 0
    if len(bundle) == 1:
        return 1 if bundle <= {0, 3} else 2
    if len(bundle) == 2 and 6 in bundle and bundle.isdisjoint({0, 3}):
        return 3
    return 4


def obstruction_ef1(word):
    bundles = [{i for i, c in enumerate(word) if c == color} for color in "012"]
    for own in bundles:
        deletions = [own] + [own - {item} for item in own]
        best = min(map(obstruction_cost, deletions))
        if any(best > obstruction_cost(other) for other in bundles):
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    files = parser.add_mutually_exclusive_group()
    files.add_argument("--write-certificate", type=Path, metavar="FILE")
    files.add_argument("--verify", type=Path, metavar="FILE",
                       help="reconstruct the graph and replay this certificate without searching")
    parser.add_argument("--obstruction", action="store_true",
                        help="use the published seven-vertex conflict graph; failure expected")
    args = parser.parse_args()
    if args.obstruction:
        conflicts = list(product(range(3), range(3, 6))) + [(0, 6), (3, 6)]
        graph = reconstruct(7, conflicts)
        print(f"Seven-vertex control: {sum(map(obstruction_ef1, graph.words))} complete EF1 assignments")
    else:
        graph = reconstruct(10, [(i, i + 1) for i in range(9)])
    print(f"{len(graph.words)} assignments, {len(graph.edges)} exchanges, "
          f"{len(graph.boundaries)} triangles")
    try:
        if args.verify is None:
            certificate = make_certificate(graph)
        else:
            certificate = json.loads(args.verify.read_text(encoding="utf-8"))
        verify(graph, certificate)
        if args.write_certificate:
            args.write_certificate.write_text(json.dumps(certificate, separators=(",", ":")) + "\n",
                                              encoding="utf-8")
    except (ValueError, OSError) as exc:
        print(f"Certificate rejected: {exc}", file=sys.stderr)
        return 1
    print(f"{len(certificate['tree'])} tree edges, {len(certificate['steps'])} signed reductions, "
          "0 unproved generators")
    print("The allocation complex is connected and simply connected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
