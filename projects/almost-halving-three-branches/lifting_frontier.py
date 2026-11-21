"""A two-hole obstruction and a sharp boundary for coarse distance counts.

This is a restriction on supports, not an all-pairs bound for a tripod.
See LIFTING_FRONTIER.md. Python standard library only.
"""
from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
from itertools import permutations, product
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


def _affine_rows(rows):
    """Exact elimination of equations a*t+b*r+c*s+d=0."""
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for column in range(3):
        hit = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if hit is None:
            continue
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        scale = rows[pivot][column]
        rows[pivot] = [x/scale for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [x-scale*y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    if any(not any(row[:3]) and row[3] for row in rows):
        return None
    return rows[:pivot]


def _implied_zero(rows, expression):
    expression = list(map(Fraction, expression))
    for row in rows:
        column = next(i for i in range(3) if row[i])
        scale = expression[column]
        expression = [x-scale*y for x, y in zip(expression, row)]
    return not any(expression)


def swap_adjacency_certificate():
    """Finite affine proof for all t, not a bounded search over trees.

    Classify all 4!*10 endpoint matches for each of 12 root-arm choices.
    A surviving system must force the even and odd roots to be adjacent.
    """
    constants = (113, 33, 5)
    counts = dict(inconsistent=0, nonintegral_or_negative_parameter=0,
                  invalid_root_coordinate=0, adjacency_forced=0)
    deltas = [d for d in product(range(3), repeat=4) if sum(d) == 2]
    for a, b in product(range(-1, 3), range(3)):
        negative = ([(0, 0, 1, 1)] + [(3780, 0, 0, p+1) for p in constants]
                    if a == -1 else
                    [(0, 0, 1, 1), (3780, -1, 0, constants[a]+1)]
                    + [(3780, 1, 0, p+1) for j, p in enumerate(constants) if j != a])
        positive = [(0, int(a != -1), 0, 0), (3780, 0, -1, constants[b])]
        positive += [(3780, 0, 1, p+1) for j, p in enumerate(constants) if j != b]
        for order, delta in product(permutations(range(4)), deltas):
            rows = []
            for i in range(4):
                row = [x-y for x, y in zip(negative[i], positive[order[i]])]
                row[3] -= delta[i]
                rows.append(row)
            if a == -1:
                rows.append([0, 1, 0, 0])
            rows = _affine_rows(rows)
            if rows is None:
                counts['inconsistent'] += 1
                continue
            adjacent = (_implied_zero(rows, (0, 0, 1, 0)) if a == -1 else
                        a == b and (_implied_zero(rows, (0, -1, 1, 0))
                                    or _implied_zero(rows, (0, -1, 1, 1))))
            if adjacent:
                counts['adjacency_forced'] += 1
                continue
            fixed = {}
            for row in rows:
                columns = [i for i, value in enumerate(row[:3]) if value]
                if len(columns) == 1:
                    fixed[columns[0]] = -row[3]
            if 0 in fixed and (fixed[0].denominator != 1 or fixed[0] < 0):
                counts['nonintegral_or_negative_parameter'] += 1
                continue
            if any(value.denominator != 1 or value < (1 if j == 1 and a != -1 else 0)
                   for j, value in fixed.items()):
                counts['invalid_root_coordinate'] += 1
                continue
            raise AssertionError('an endpoint system needs a further mathematical argument')
    return {"family": "T(227+7560t,67+7560t,11+7560t), integer t>=0",
            "endpoint_systems": 2880, "classification": counts,
            "one_swap_roots_must_be_adjacent": True,
            "one_swap_homometric_pairs_excluded": False,
            "all_colourings_excluded": False}


def verify_swap_adjacency_certificate(saved):
    expected = swap_adjacency_certificate()
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('swap adjacency certificate differs from the reconstructed proof')
    return expected


def _reduce_affine(expression, rows):
    expression = list(map(Fraction, (expression[0], expression[1], 0, expression[2])))
    for row in rows:
        column = next(i for i in range(3) if row[i])
        scale = expression[column]
        expression = [x-scale*y for x, y in zip(expression, row)]
    return expression[0], expression[1], expression[3]


def _zero_polynomial_systems(events, rows):
    """Branch on matching positive/negative monomials, at most two ranks."""
    rows = _affine_rows(rows)
    if rows is None:
        return
    reduced = {}
    for exponent, coefficient in events.items():
        key = _reduce_affine(exponent, rows)
        reduced[key] = reduced.get(key, 0) + coefficient
    reduced = {key: value for key, value in reduced.items() if value}
    if not reduced:
        yield rows
        return
    positive = next(key for key, value in reduced.items() if value > 0)
    for negative, value in reduced.items():
        if value < 0:
            t, r, constant = (x-y for x, y in zip(positive, negative))
            yield from _zero_polynomial_systems(events, rows+[[t, r, 0, constant]])


def _adjacent_swap_systems(offsets=(113, 33, 5), step=3780):
    """Exact endpoint equations. Nonempty survivors are a failed proof gate.

    Alternative constants are used only for a known positive control.
    All inequalities are necessary domain checks; unproved ones stay open.
    """
    add = lambda a, b: tuple(x+y for x, y in zip(a, b))
    neg = lambda a: tuple(-x for x in a)
    sub = lambda a, b: add(a, neg(b))
    scale = lambda a, n: tuple(x*n for x in a)
    equation = lambda a: [a[0], a[1], 0, a[2]]
    p = [(step, 0, value) for value in offsets]
    r, one = (0, 1, 0), (0, 0, 1)

    def admissible(rows, bounds, distinct):
        if rows is None:
            return False
        for bound in bounds:
            reduced = _reduce_affine(bound, rows)
            if not any(reduced[:2]) and reduced[2] < 0:
                return False
        if any(not any(_reduce_affine(value, rows)) for value in distinct):
            return False
        for row in rows:
            columns = [i for i, value in enumerate(row[:3]) if value]
            if len(columns) == 1 and (-row[3]).denominator != 1:
                return False
            if columns == [0] and -row[3] < 0:
                return False
        return True

    def holes(a, exponent):
        return ([(a, add(r, exponent)), (a, sub(sub(r, exponent), one))]
                + [(b, sub(exponent, r)) for b in range(3) if b != a])

    def distance_options(v, w):
        a, q = v
        b, s = w
        if a != b:
            return [(add(add(q, s), one), [])]
        difference = sub(q, s)
        return [(difference, [difference]), (neg(difference), [neg(difference)])]

    families, survivors = 0, []
    for a, outward in product(range(3), (True, False)):
        s = r if outward else sub(r, one)
        others = [j for j in range(3) if j != a]
        exponents = [r, sub(p[a], r)] if outward else [add(r, p[j]) for j in others]
        for h1, h2 in product(holes(a, exponents[0]), holes(a, exponents[1])):
            bounds = [r if outward else sub(r, one), sub(p[a], r)]
            for b, q in (h1, h2):
                bounds += [q, sub(p[b], q)]
            distinct = ([sub(h1[1], h2[1])] if h1[0] == h2[0] else [])
            distinct += [sub(q, s) for b, q in (h1, h2) if b == a]
            leaves = ([sub(r, p[a])] if outward and a < 2 else [])
            leaves += [sub(q, p[b]) for b, q in (h1, h2) if b < 2]
            for leaf in leaves:
                rows = _affine_rows([[0, 0, 1, 0], equation(leaf)])
                if not admissible(rows, bounds, distinct):
                    continue
                options = (distance_options(h1, h2), distance_options((a, s), h1),
                           distance_options((a, s), h2))
                for distances in product(*options):
                    local_bounds = bounds+[bound for _, extra in distances for bound in extra]
                    if not admissible(rows, local_bounds, distinct):
                        continue
                    events = {}
                    def put(exponent, coefficient):
                        events[exponent] = events.get(exponent, 0)+coefficient
                    put(one, -3)
                    for i, j in ((0, 1), (0, 2), (1, 2)):
                        put(add(add(p[i], p[j]), scale(one, 2)), 1)
                    for b, q in (h1, h2):
                        put(one, 2)
                        put(add(q, one), 1)
                        put(add(sub(p[b], q), one), -1)
                        for j in range(3):
                            if j != b:
                                put(add(add(q, p[j]), scale(one, 2)), -1)
                    moves = ([add(add(r, p[j]), one) for j in others] if outward else
                             [r, add(sub(p[a], r), one)])
                    for exponent in moves:
                        put(exponent, 1)
                        put(add(exponent, one), -1)
                    for exponent, _ in distances:
                        put(exponent, -1)
                        put(add(exponent, one), 1)
                    families += 1
                    for solution in _zero_polynomial_systems(events, rows):
                        if admissible(solution, local_bounds, distinct):
                            survivors.append(solution)
    return families, survivors


def one_swap_obstruction_certificate():
    adjacency = swap_adjacency_certificate()
    families, survivors = _adjacent_swap_systems()
    if survivors:
        raise AssertionError('adjacent swaps remain unresolved by the symbolic equations')
    return {"family": adjacency['family'], "adjacency_proof": adjacency['classification'],
            "adjacent_endpoint_families": families, "surviving_affine_systems": 0,
            "one_swap_homometric_pairs_excluded": True,
            "all_colourings_excluded": False}


def verify_one_swap_obstruction(saved):
    expected = one_swap_obstruction_certificate()
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('one-swap certificate differs from the reconstructed proof')
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
    parser.add_argument("--one-swap-obstruction", action="store_true",
                        help="exclude every one-swap partition on the entire frontier")
    parser.add_argument("--swap-adjacency", action="store_true",
                        help="symbolically classify one-swap roots for every parameter")
    parser.add_argument("--parity-obstruction", action="store_true",
                        help="exclude pure depth-parity sets on the entire frontier")
    parser.add_argument("--coarse", action="store_true",
                        help="construct only the two coarse distance-count equalities")
    parser.add_argument("--audit", action="store_true", help="BFS check, up to 512 vertices")
    args = parser.parse_args(argv)
    try:
        if args.one_swap_obstruction:
            if args.swap_adjacency or args.parity_obstruction or args.coarse or args.audit or args.lengths:
                parser.error("--one-swap-obstruction accepts only --verify")
            result = (verify_one_swap_obstruction(json.loads(args.verify.read_text()))
                      if args.verify else one_swap_obstruction_certificate())
        elif args.swap_adjacency:
            if args.parity_obstruction or args.coarse or args.audit or args.lengths:
                parser.error("--swap-adjacency accepts only --verify")
            result = (verify_swap_adjacency_certificate(json.loads(args.verify.read_text()))
                      if args.verify else swap_adjacency_certificate())
        elif args.parity_obstruction:
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
