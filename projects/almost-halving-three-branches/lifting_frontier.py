"""All-colouring obstruction for two holes at depths divisible by four.

This is a restriction on supports, not an all-pairs bound for a tripod.
See LIFTING_FRONTIER.md. Python standard library only.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path

from published_cases import validate_lengths, validate_vertices


SCOPE = "exactly two omitted vertices, both at depths divisible by four"


def frontier_lengths(parameter):
    if type(parameter) is not int or parameter < 0:
        raise ValueError("frontier parameter must be a nonnegative integer")
    return tuple(n + 7560 * parameter for n in (227, 67, 11))


def certificate(lengths, holes):
    """Prove impossibility for every colouring of the specified support.

    The selected graph joins original-tree distances congruent to 2 mod 4.
    Its vertex degrees are equal mod 4, but its edge count disagrees with
    that common degree times the required size of one part.
    """
    lengths = validate_lengths(lengths)
    holes = validate_vertices(lengths, holes)
    if any(n % 4 != 3 for n in lengths):
        raise ValueError("every arm length must be three modulo four")
    if len(holes) != 2 or any(depth % 4 for _, depth in holes):
        raise ValueError("exactly two distinct holes at depths divisible by four are required")
    k = sum((n - 3) // 4 for n in lengths)
    if k % 2:
        raise ValueError("the sum of the three arm quotients must be even")
    size = 2 * k + 4
    edges = 2 * (k + 1) * (k + 3)
    degree = (k + 3) % 4
    return {
        "lengths": list(lengths), "holes": [list(h) for h in holes],
        "scope": SCOPE, "selected_distance_modulus": 4,
        "selected_distance_residue": 2, "degree_modulus": 4,
        "common_degree_residue": degree,
        "residue_vertex_counts": [k - 1, k + 3, k + 3, k + 3],
        "degree_by_depth_residue": [k + 3, k + 3, k - 1, k + 3],
        "selected_edges": edges, "target_size": size,
        "required_edge_residue": degree * size % 4,
        "actual_edge_residue": edges % 4,
        "contradiction_residue": (edges - degree * size) % 4,
        "every_colouring_of_this_support_excluded": True,
        "all_omissions_obstructed": False,
    }


def verify_certificate(saved):
    """Rebuild every certificate field; do not trust saved verdicts or counts."""
    if not isinstance(saved, dict):
        raise ValueError("certificate must be a JSON object")
    try:
        expected = certificate(saved["lengths"], saved["holes"])
    except KeyError as error:
        raise ValueError("certificate is missing lengths or holes") from error
    # JSON's bools compare equal to integers in Python; require exact types too.
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("certificate differs from the reconstructed proof")
    return expected


def audit_original_tree(saved, max_vertices=512):
    """Independently count selected edges using BFS in the unmodified tree.

    O(N^2) audit for small inputs. Holes are removed only from the retained
    vertex list; they remain in the graph traversed for every distance.
    """
    saved = verify_certificate(saved)
    lengths = saved["lengths"]
    if type(max_vertices) is not int or max_vertices < 1:
        raise ValueError("audit limit must be a positive integer")
    if 1 + sum(lengths) > max_vertices:
        raise ValueError("original-tree audit exceeds its vertex limit")
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    holes = set(map(tuple, saved["holes"]))
    retained = [v for v in graph if v not in holes]
    degrees = []
    for source in retained:
        distances = {source: 0}
        queue = deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        degrees.append(sum(distances[v] % 4 == 2 for v in retained))
    edges = sum(degrees) // 2
    valid = (edges == saved["selected_edges"]
             and all(degree == saved["degree_by_depth_residue"][v[1] % 4]
                     for v, degree in zip(retained, degrees))
             and edges % 4 != saved["required_edge_residue"])
    if not valid:
        raise ValueError("original-tree audit contradicts the certificate")
    return {"original_vertices": len(graph), "retained_vertices": len(retained),
            "selected_edges": edges, "original_tree_distances_checked": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter", type=int, default=0,
                        help="t in T(227+7560t,67+7560t,11+7560t)")
    parser.add_argument("--lengths", type=int, nargs=3,
                        help="instead use any three lengths in the proved domain")
    parser.add_argument("--holes", nargs=2, default=["0:0", "1:4"],
                        help="two arm:depth vertices (centre is 0:0)")
    parser.add_argument("--verify", type=Path, help="verify a saved JSON certificate")
    parser.add_argument("--audit", action="store_true", help="BFS check, up to 512 vertices")
    args = parser.parse_args(argv)
    try:
        if args.verify:
            result = verify_certificate(json.loads(args.verify.read_text()))
        else:
            lengths = args.lengths if args.lengths else frontier_lengths(args.parameter)
            holes = [tuple(map(int, value.split(":"))) for value in args.holes]
            result = certificate(lengths, holes)
        if args.audit:
            audit = audit_original_tree(result)
            print(json.dumps({"certificate": result, "audit": audit}, indent=2))
        else:
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
