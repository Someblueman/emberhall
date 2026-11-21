"""A two-hole obstruction and a sharp boundary for coarse distance counts.

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


def coarse_certificate(lengths, holes):
    """Construct a balanced partition matching two coarse distance counts.

    This is NOT a homometry certificate. Cells are arm/depth-residue classes;
    the first `left` retained depths in each cell belong to the left part.
    Storage and arithmetic do not grow with the arm lengths.
    """
    lengths = validate_lengths(lengths)
    holes = validate_vertices(lengths, holes)
    if len(holes) != 2 or any(n % 4 != 3 for n in lengths):
        raise ValueError("three lengths congruent to three and two holes are required")
    k = sum((n - 3) // 4 for n in lengths)
    if k % 2:
        raise ValueError("the sum of the three arm quotients must be even")
    if holes[0][1] % 2 != holes[1][1] % 2:
        raise ValueError("opposite-parity holes are already obstructed")
    if all(d % 4 == 0 for _, d in holes):
        raise ValueError("two zero-residue holes are already obstructed")
    cells = []
    if (0, 0) not in holes:
        cells.append({"arm": 0, "residue": 0, "count": 1, "left": 0})
    for arm, length in enumerate(lengths, 1):
        for residue in range(4):
            count = (length - residue) // 4 + (residue != 0)
            count -= sum(a == arm and d % 4 == residue for a, d in holes)
            cells.append({"arm": arm, "residue": residue, "count": count, "left": 0})

    def allocate(residues, amount):
        for cell in cells:
            if cell['residue'] in residues:
                take = min(amount, cell['count'])
                cell['left'] = take
                amount -= take
        assert amount == 0

    adjacent = False
    if holes[0][1] % 2 == 0:
        h = sum(d % 4 == 0 for _, d in holes)
        allocate({0}, k + 1 if h == 0 else k // 2)
        allocate({2}, 0 if h == 0 else k // 2 + 1)
        allocate({1, 3}, k + 3)
    else:
        allocate({0, 2}, 2*k + 4)
        (a, d), (b, e) = holes
        adjacent = ((abs(d-e) if a == b else d+e) % 4 == 2)
        if adjacent:
            # An even depth-two vertex has degree K+1. A retained odd
            # vertex adjacent to exactly one hole has degree K+2.
            # Swapping these increases the edge-count difference by one.
            next(c for c in cells if c['arm'] == 1 and c['residue'] == 2)['left'] -= 1
            for cell in cells:
                arm, residue = cell['arm'], cell['residue']
                if residue % 2 and cell['count'] and sum(
                        (residue-depth if arm == branch else residue+depth) % 4 == 2
                        for branch, depth in holes) == 1:
                    cell['left'] += 1
                    break
            else:
                raise AssertionError("the proved single-neighbor odd cell is missing")
    return {"lengths": list(lengths), "holes": [list(h) for h in holes],
            "cells": cells, "target_size": 2*k+4,
            "odd_hole_swap": adjacent,
            "equal_odd_distance_counts": True,
            "equal_two_mod_four_distance_counts": True,
            "homometric_pair_proved": False}


def verify_coarse_certificate(saved):
    """Check the canonical compressed construction, including its limits."""
    if not isinstance(saved, dict):
        raise ValueError("coarse certificate must be a JSON object")
    try:
        expected = coarse_certificate(saved['lengths'], saved['holes'])
    except KeyError as error:
        raise ValueError("coarse certificate is missing lengths or holes") from error
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("coarse certificate differs from the reconstructed construction")
    return expected


def coarse_pair(saved, max_vertices=512):
    """Expand the first-retained-depth convention, only for bounded audits."""
    saved = verify_coarse_certificate(saved)
    if type(max_vertices) is not int or max_vertices < 1:
        raise ValueError("audit limit must be a positive integer")
    if 1 + sum(saved['lengths']) > max_vertices:
        raise ValueError("original-tree audit exceeds its vertex limit")
    holes = set(map(tuple, saved['holes']))
    left, right = [], []
    for cell in saved['cells']:
        arm, residue = cell['arm'], cell['residue']
        vertices = ([(0, 0)] if arm == 0 else
                    [(arm, d) for d in range(1, saved['lengths'][arm-1]+1)
                     if d % 4 == residue and (arm, d) not in holes])
        left.extend(vertices[:cell['left']])
        right.extend(vertices[cell['left']:])
    return left, right


def audit_coarse_certificate(saved, max_vertices=512):
    """BFS in the original tree; report exact failure as well as coarse success."""
    left, right = coarse_pair(saved, max_vertices)
    graph = {(0, 0): []}
    for arm, length in enumerate(saved['lengths'], 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    profiles = []
    for part in (left, right):
        profile = {}
        for i, source in enumerate(part):
            distances = {source: 0}
            queue = deque([source])
            while queue:
                vertex = queue.popleft()
                for neighbor in graph[vertex]:
                    if neighbor not in distances:
                        distances[neighbor] = distances[vertex] + 1
                        queue.append(neighbor)
            for target in part[i+1:]:
                d = distances[target]
                profile[d] = profile.get(d, 0) + 1
        profiles.append(profile)
    coarse = [[sum(n for d, n in p.items() if d % 2),
               sum(n for d, n in p.items() if d % 4 == 2)] for p in profiles]
    if len(left) != saved['target_size'] or len(right) != len(left) or coarse[0] != coarse[1]:
        raise ValueError("original-tree audit contradicts the coarse construction")
    return {"original_tree_distances_checked": True, "coarse_counts": coarse[0],
            "actual_homometric_pair": profiles[0] == profiles[1],
            "first_exact_mismatch": next((d for d in sorted(profiles[0].keys() | profiles[1].keys())
                                          if profiles[0].get(d, 0) != profiles[1].get(d, 0)), None)}


def parity_obstruction(parameter):
    """Exclude the pure depth-parity partition for every frontier parameter.

    Rows list every possible leaf/interior placement forced by the largest
    remaining distance. Coefficients use x=z^2. See the interval proof.
    This excludes a sign pattern for all holes, not arbitrary colourings.
    """
    lengths = frontier_lengths(parameter)
    p = [(length-1)//2 for length in lengths]
    rows = []
    for leaf in (0, 1):
        others = [i for i in range(3) if i != leaf]
        target_top = max(p[leaf], p[others[0]]+p[others[1]]+1)
        for arm in range(3):
            if arm == leaf:
                q = target_top-max(p[i] for i in others)-1
                mismatch = (34 if parameter == 0 else 108) if leaf == 0 else 28
            else:
                other = next(i for i in range(3) if i not in (leaf, arm))
                # Removing the pair with the leaf shortens that cross interval.
                q = target_top-max(p[leaf], p[other]+1)
                mismatch = (108 if arm == 1 else 80) if leaf == 0 else 28
            row = {"leaf_arm": leaf+1, "interior_arm": arm+1, "forced_index": q}
            if not 1 <= q < p[arm]:
                row['excluded_by'] = 'forced index is not interior'
            else:
                r = mismatch
                actual = int(1 <= r <= q) + int(1 <= r <= p[arm]-q)
                actual += sum(q < r <= q+p[i]+1 for i in range(3) if i != arm)
                pair_distance = p[leaf]-q if arm == leaf else p[leaf]+q+1
                actual -= int(r == pair_distance)
                required = int(1 <= r <= p[leaf]) + int(1 <= r <= p[others[0]]+p[others[1]]+1)
                if actual == required:
                    raise AssertionError('the parity obstruction coefficient must disagree')
                row.update(excluded_by='coefficient mismatch', power=r,
                           actual_coefficient=actual, required_coefficient=required)
            rows.append(row)
    return {"lengths": list(lengths), "parameter": parameter, "cases": rows,
            "pure_depth_parity_partition_excluded": True,
            "all_colourings_excluded": False}


def verify_parity_obstruction(saved):
    if not isinstance(saved, dict):
        raise ValueError('parity obstruction must be a JSON object')
    try:
        expected = parity_obstruction(saved['parameter'])
    except KeyError as error:
        raise ValueError('parity obstruction is missing its parameter') from error
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('parity obstruction differs from the reconstructed proof')
    return expected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter", type=int, default=0,
                        help="t in T(227+7560t,67+7560t,11+7560t)")
    parser.add_argument("--lengths", type=int, nargs=3,
                        help="instead use any three lengths in the proved domain")
    parser.add_argument("--holes", nargs=2, default=["0:0", "1:4"],
                        help="two arm:depth vertices (centre is 0:0)")
    parser.add_argument("--verify", type=Path, help="verify a saved JSON certificate")
    parser.add_argument("--parity-obstruction", action="store_true",
                        help="exclude pure depth-parity sets on the entire frontier")
    parser.add_argument("--coarse", action="store_true",
                        help="construct only the two coarse distance-count equalities")
    parser.add_argument("--audit", action="store_true", help="BFS check, up to 512 vertices")
    args = parser.parse_args(argv)
    try:
        if args.parity_obstruction:
            if args.coarse or args.audit or args.lengths:
                parser.error("--parity-obstruction accepts only --parameter or --verify")
            result = (verify_parity_obstruction(json.loads(args.verify.read_text()))
                      if args.verify else parity_obstruction(args.parameter))
        elif args.verify:
            saved = json.loads(args.verify.read_text())
            result = (verify_coarse_certificate(saved) if args.coarse else verify_certificate(saved))
        else:
            lengths = args.lengths if args.lengths else frontier_lengths(args.parameter)
            holes = [tuple(map(int, value.split(":"))) for value in args.holes]
            result = (coarse_certificate(lengths, holes) if args.coarse else certificate(lengths, holes))
        if args.audit:
            audit = (audit_coarse_certificate(result) if args.coarse else audit_original_tree(result))
            print(json.dumps({"certificate": result, "audit": audit}, indent=2))
        else:
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
