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
import math
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


def _interior_degree_classes(lengths, tail_blocks):
    """Count degrees modulo four in eight intervals, without expanding a tree.

    Prefix counts change by multiples of four after 32 steps on either
    side of the cutoff. Each interval fixes the distance branches.
    """
    a, b, c = lengths
    odd = ((a-b+c-3)//8) % 2
    modulus, low, high = 8, {6}, {0, 3, 4, 6, 7}
    tail = 8*tail_blocks+1
    cutoff = a+b-tail
    holes = ((1, a-tail), (2, b-tail))

    def prefix(n, residues):
        if n <= 0:
            return 0
        q, r = divmod(n, modulus)
        return q*len(residues) + sum(0 < s <= r for s in residues)

    def weight(d):
        return int(d > 0 and d % modulus in (low if d <= cutoff else high))

    def total(n):
        cut = min(n, cutoff)
        return prefix(cut, low) + prefix(n, high) - prefix(cut, high)

    def degree(arm, d):
        if arm == 0:
            return sum(total(n) for n in lengths) - sum(weight(h) for _, h in holes)
        value = total(d-1) + total(lengths[arm-1]-d) + weight(d) - 2*total(d)
        value += sum(total(d+n) for j, n in enumerate(lengths, 1) if j != arm)
        return value - sum(weight(abs(d-h) if arm == j else d+h) for j, h in holes)

    intervals = [(1, 1, holes[0][1]-1), (1, holes[0][1]+1, a-1), (1, a, a),
                 (2, 1, holes[1][1]-1), (2, holes[1][1]+1, b-1),
                 (2, b, b), (3, 1, c-1), (3, c, c)]
    counts = [0]*4
    counts[degree(0, 0) % 4] = 1
    for arm, lo, hi in intervals:
        for residue in range(32):
            first = lo + (residue-lo) % 32
            if first <= hi:
                value = degree(arm, first) % 4
                counts[value] += (hi-first)//32 + 1
    return {"holes": [list(h) for h in holes], "distance_cutoff": cutoff,
            "distance_modulus": modulus, "low_residues": sorted(low),
            "high_residues": sorted(high), "degree_counts_mod_four": counts,
            "common_degree_parity": odd}


def interior_obstruction(lengths, tail_blocks=None):
    """Exclude all colourings for an interval of aligned interior holes."""
    lengths = validate_lengths(lengths)
    a, b, c = lengths
    if not a >= b >= c or any(n % 8 != 3 for n in lengths):
        raise ValueError('require a>=b>=c, all three lengths three modulo eight')
    limit = (b-c)//8
    if tail_blocks is None:
        tail_blocks = limit
    if type(tail_blocks) is not int or not 0 <= tail_blocks <= limit:
        raise ValueError('tail blocks must be an integer between zero and (b-c)/8')
    data = _interior_degree_classes(lengths, tail_blocks)
    counts = data['degree_counts_mod_four']
    odd = data['common_degree_parity']
    quotients = [(n-3)//8 for n in lengths]
    k = sum(quotients)
    baseline_edges = 4*k*k+8*k+3
    extra_edges = 2*tail_blocks*(8*tail_blocks+3)
    edges = baseline_edges-2*k+extra_edges
    size = (a+b+c-1)//2
    if (sum(counts) != 2*size or size % 2
            or any(counts[i] for i in range(4) if i % 2 != odd)
            or sum(i*n for i, n in enumerate(counts)) % 4 != 2):
        raise AssertionError('the interior degree obstruction failed')
    return {"lengths": list(lengths), **data, "tail_blocks": tail_blocks, "target_size": size,
            "selected_edge_parity": 1, "required_edge_parity": 0,
            "arm_quotients": quotients, "baseline_edges": baseline_edges,
            "removed_degree_sum": 2*k, "extra_edges": extra_edges,
            "selected_edges": edges,
            "every_colouring_of_this_support_excluded": True,
            "all_omissions_obstructed": False}


def verify_interior_obstruction(saved):
    if not isinstance(saved, dict) or 'lengths' not in saved or 'tail_blocks' not in saved:
        raise ValueError('interior certificate must contain lengths and tail blocks')
    expected = interior_obstruction(saved['lengths'], saved['tail_blocks'])
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('interior certificate differs from the reconstructed proof')
    return expected


def audit_interior_obstruction(saved, max_vertices=512):
    """BFS uses the original tree, including both omitted path vertices."""
    saved = verify_interior_obstruction(saved)
    if type(max_vertices) is not int or max_vertices < 1 or 1+sum(saved['lengths']) > max_vertices:
        raise ValueError('original-tree audit exceeds its positive vertex limit')
    graph = {(0, 0): []}
    for arm, length in enumerate(saved['lengths'], 1):
        previous = (0, 0)
        for depth in range(1, length+1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    retained = [v for v in graph if list(v) not in saved['holes']]
    counts, degree_sum = [0]*4, 0
    for source in retained:
        distances, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex]+1
                    queue.append(neighbor)
        degree = sum(v != source and distances[v] % saved['distance_modulus'] in
                     (saved['low_residues'] if distances[v] <= saved['distance_cutoff']
                      else saved['high_residues']) for v in retained)
        counts[degree % 4] += 1
        degree_sum += degree
    if (counts != saved['degree_counts_mod_four'] or degree_sum % 4 != 2
            or degree_sum//2 != saved['selected_edges']):
        raise ValueError('original-tree audit contradicts the interior certificate')
    return {"original_vertices": len(graph), "retained_vertices": len(retained),
            "selected_edges": degree_sum//2, "original_tree_distances_checked": True}


def _extended_spec(lengths, family, tail_blocks):
    """Validate parameters and return the distance-selection rules for a family."""
    a, b, c = lengths
    if family == 'mod8-q5':
        if not a >= b >= c or any(n % 8 != 3 for n in lengths):
            raise ValueError('mod8-q5 requires a>=b>=c, all three lengths three modulo eight')
        limit = (b - c) // 8 - 1
        if limit < 0:
            raise ValueError('mod8-q5 requires b > c')
        p = limit if tail_blocks is None else tail_blocks
        if type(p) is not int or not 0 <= p <= limit:
            raise ValueError('tail blocks must be an integer between zero and (b-c)/8 - 1')
        q = 8 * p + 5
        cutoff = a + b - q
        quotients = [(n - 3) // 8 for n in lengths]
        k = sum(quotients)
        return {
            "family": family, "modulus": 8, "tail_blocks": p, "hole_deficit": q,
            "holes": ((1, a - q), (2, b - q)), "cutoff_lo": cutoff - 1,
            "cutoff_hi": cutoff + 1, "mid_distances": (cutoff, cutoff + 1),
            "max_exclusive": a + b, "low_residues": (2, 5, 7), "high_residues": (1, 6, 7),
            "common_degree_parity": (k + 1) % 2, "quotient_sum": k, "quotients": quotients,
            "edges": 12 * k * k + 22 * k + 11 + 8 * p, "hole_depth_parity": "even",
        }
    if family in ('mod10-q2', 'mod10-q0'):
        if (not a >= b >= c or a % 10 != 7 or b % 10 != 7 or c % 10 != 1
                or (a + b + c) % 4 != 1):
            raise ValueError(f'{family} requires a>=b>=c with residues (7,7,1) mod 10 and sum 1 mod 4')
        limit = (b - c - 6) // 10
        lo = 0 if family == 'mod10-q2' else 1
        if limit < lo:
            raise ValueError(f'{family} requires larger b-c for this hole offset')
        p = limit if tail_blocks is None else tail_blocks
        if type(p) is not int or not lo <= p <= limit:
            raise ValueError(f'tail blocks must be an integer between {lo} and (b-c-6)/10')
        quotients = [(a - 7) // 10, (b - 7) // 10, (c - 1) // 10]
        k = sum(quotients)
        if family == 'mod10-q2':
            q = 10 * p + 2
            cutoff = a + b - q
            return {
                "family": family, "modulus": 10, "tail_blocks": p, "hole_deficit": q,
                "holes": ((1, a - q), (2, b - q)), "cutoff_lo": cutoff,
                "cutoff_hi": cutoff, "mid_distances": (),
                "max_exclusive": None, "low_residues": (0, 2, 3, 6, 9),
                "high_residues": (0, 6, 7, 8, 9), "common_degree_parity": 1,
                "quotient_sum": k, "quotients": quotients,
                "edges": 25 * k * k + 65 * k + 39, "hole_depth_parity": "odd",
            }
        q = 10 * p
        cutoff = a + b - q
        return {
            "family": family, "modulus": 10, "tail_blocks": p, "hole_deficit": q,
            "holes": ((1, a - q), (2, b - q)), "cutoff_lo": cutoff - 1,
            "cutoff_hi": cutoff + 1, "mid_distances": (cutoff + 1,),
            "max_exclusive": a + b, "low_residues": (1, 3, 4, 6, 8, 9),
            "high_residues": (4, 9), "common_degree_parity": 1,
            "quotient_sum": k, "quotients": quotients,
            "edges": 30 * k * k + 83 * k + 56 - 2 * p * (10 * p + 1),
            "hole_depth_parity": "odd",
        }
    raise ValueError(f'unknown obstruction family: {family}')


def _extended_weight(d, spec):
    if d <= 0 or (spec['max_exclusive'] is not None and d >= spec['max_exclusive']):
        return 0
    if d <= spec['cutoff_lo']:
        return int(d % spec['modulus'] in spec['low_residues'])
    if d <= spec['cutoff_hi']:
        return int(d in spec['mid_distances'])
    return int(d % spec['modulus'] in spec['high_residues'])


def _extended_degree_classes(lengths, spec):
    """Count degrees modulo four over regime-constant arm intervals."""
    a, b, c = lengths
    modulus = spec['modulus']
    low, high = spec['low_residues'], spec['high_residues']
    clo, chi, dmax = spec['cutoff_lo'], spec['cutoff_hi'], spec['max_exclusive']
    mid_set = spec['mid_distances']
    holes = spec['holes']
    period = 4 * modulus

    def prefix(n, residues):
        if n <= 0:
            return 0
        q, r = divmod(n, modulus)
        return q * len(residues) + sum(0 < s <= r for s in residues)

    base_low = prefix(clo, low)
    base_mid = base_low + len(mid_set)
    base_high = prefix(chi, high)

    def total(n):
        if n <= 0:
            return 0
        if dmax is not None and n >= dmax:
            n = dmax - 1
        if n <= clo:
            return prefix(n, low)
        if n <= chi:
            return base_low + sum(d <= n for d in mid_set)
        return base_mid + prefix(n, high) - base_high

    def degree(arm, d):
        if arm == 0:
            return sum(total(n) for n in lengths) - sum(_extended_weight(h, spec) for _, h in holes)
        value = total(d - 1) + total(lengths[arm - 1] - d) + _extended_weight(d, spec) - 2 * total(d)
        value += sum(total(d + n) for j, n in enumerate(lengths, 1) if j != arm)
        return value - sum(_extended_weight(abs(d - h) if arm == j else d + h, spec) for j, h in holes)

    h1, h2 = holes[0][1], holes[1][1]
    intervals = [
        (1, 1, h1 - 1), (1, h1 + 1, h1 + 1 if h1 + 1 < a else a - 1),
        (1, h1 + 2, a - 1), (1, a, a),
        (2, 1, h2 - 1), (2, h2 + 1, h2 + 1 if h2 + 1 < b else b - 1),
        (2, h2 + 2, b - 1), (2, b, b),
        (3, 1, c - 1), (3, c, c),
    ]
    counts = [0] * 4
    counts[degree(0, 0) % 4] = 1
    for arm, lo, hi in intervals:
        if lo > hi:
            continue
        for residue in range(period):
            first = lo + (residue - lo) % period
            if first <= hi:
                value = degree(arm, first) % 4
                counts[value] += (hi - first) // period + 1
    return counts


def extended_obstruction(lengths, family='mod8-q5', tail_blocks=None):
    """Exclude every colouring for the mod8-q5, mod10-q2, or mod10-q0 hole families."""
    lengths = validate_lengths(lengths)
    spec = _extended_spec(lengths, family, tail_blocks)
    counts = _extended_degree_classes(lengths, spec)
    odd = spec['common_degree_parity']
    size = (sum(lengths) - 1) // 2
    if (sum(counts) != 2 * size or size % 2 or spec['edges'] % 2 == 0
            or any(counts[i] for i in range(4) if i % 2 != odd)
            or sum(i * n for i, n in enumerate(counts)) % 4 != 2):
        raise AssertionError('the extended degree obstruction failed')
    return {
        "lengths": list(lengths), "family": family,
        "hole_depth_parity": spec['hole_depth_parity'],
        "holes": [list(h) for h in spec['holes']],
        "tail_blocks": spec['tail_blocks'], "hole_deficit": spec['hole_deficit'],
        "distance_modulus": spec['modulus'],
        "cutoff_lo": spec['cutoff_lo'], "cutoff_hi": spec['cutoff_hi'],
        "mid_distances": list(spec['mid_distances']),
        "max_exclusive": spec['max_exclusive'],
        "low_residues": list(spec['low_residues']),
        "high_residues": list(spec['high_residues']),
        "degree_counts_mod_four": counts, "common_degree_parity": odd,
        "target_size": size, "selected_edge_parity": 1, "required_edge_parity": 0,
        "quotients": spec['quotients'], "quotient_sum": spec['quotient_sum'],
        "selected_edges": spec['edges'],
        "every_colouring_of_this_support_excluded": True,
        "all_omissions_obstructed": False,
    }


def verify_extended_obstruction(saved):
    if not isinstance(saved, dict) or not {'lengths', 'family', 'tail_blocks'} <= saved.keys():
        raise ValueError('extended certificate must contain lengths, family, and tail_blocks')
    expected = extended_obstruction(saved['lengths'], saved['family'], saved['tail_blocks'])
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('extended certificate differs from the reconstructed proof')
    return expected


def audit_extended_obstruction(saved, max_vertices=512):
    """BFS uses the original tree, including both omitted path vertices."""
    saved = verify_extended_obstruction(saved)
    if type(max_vertices) is not int or max_vertices < 1 or 1 + sum(saved['lengths']) > max_vertices:
        raise ValueError('original-tree audit exceeds its positive vertex limit')
    graph = {(0, 0): []}
    for arm, length in enumerate(saved['lengths'], 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    retained = [v for v in graph if list(v) not in saved['holes']]
    spec = _extended_spec(tuple(saved['lengths']), saved['family'], saved['tail_blocks'])
    counts, degree_sum = [0] * 4, 0
    for source in retained:
        distances, queue = {source: 0}, deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        degree = sum(_extended_weight(distances[v], spec) for v in retained if v != source)
        counts[degree % 4] += 1
        degree_sum += degree
    if (counts != saved['degree_counts_mod_four'] or degree_sum % 4 != 2
            or degree_sum // 2 != saved['selected_edges']):
        raise ValueError('original-tree audit contradicts the extended certificate')
    return {"original_vertices": len(graph), "retained_vertices": len(retained),
            "selected_edges": degree_sum // 2, "original_tree_distances_checked": True}


def terminal_tip_obstruction(lengths, arms=(1, 2)):
    """Exclude omitting two arm tips via the full-partition residue lemma."""
    lengths = validate_lengths(lengths)
    if (len(arms) != 2 or any(type(a) is not int or a not in (1, 2, 3) for a in arms)
            or arms[0] == arms[1]):
        raise ValueError('arms must be two distinct arm numbers in {1, 2, 3}')
    arms = tuple(sorted(arms))
    holes = tuple((arm, lengths[arm - 1]) for arm in arms)
    trimmed = [n - (1 if i in arms else 0) for i, n in enumerate(lengths, 1)]
    if any(n < 1 for n in trimmed):
        raise ValueError('trimmed prefix arms must remain positive')
    g = math.gcd(trimmed[0] - trimmed[1], trimmed[1] - trimmed[2])
    if g <= 1:
        raise ValueError('trimmed prefix has trivial arm-difference gcd')
    r = trimmed[0] % g
    h = math.gcd(r, g)
    q_sum = sum(n // g for n in trimmed)
    if r == 0 or (h == 1 and r == g - 1 and q_sum % 2 == 1):
        raise ValueError('trimmed prefix is not obstructed by the residue lemma')
    counts = [q_sum + 1] + [q_sum + 3] * r + [q_sum] * (g - 1 - r)
    reason = 'gcd_parity_mismatch' if h > 1 else 'forced_zero_residue_sum_odd_population'
    return {
        "lengths": list(lengths), "omitted_arms": list(arms),
        "holes": [list(hole) for hole in holes], "trimmed_lengths": trimmed,
        "target_size": (sum(lengths) - 1) // 2, "modulus": g, "remainder": r,
        "gcd_remainder_modulus": h, "quotient_sum": q_sum,
        "residue_populations": counts, "obstruction_reason": reason,
        "every_colouring_of_this_support_excluded": True,
        "all_omissions_obstructed": False,
    }


def verify_terminal_tip_obstruction(saved):
    if not isinstance(saved, dict) or not {'lengths', 'omitted_arms'} <= saved.keys():
        raise ValueError('terminal-tip certificate must contain lengths and omitted_arms')
    expected = terminal_tip_obstruction(saved['lengths'], tuple(saved['omitted_arms']))
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('terminal-tip certificate differs from the reconstructed proof')
    return expected


def audit_terminal_tip_obstruction(saved, max_vertices=512):
    saved = verify_terminal_tip_obstruction(saved)
    if type(max_vertices) is not int or max_vertices < 1 or 1 + sum(saved['lengths']) > max_vertices:
        raise ValueError('original-tree audit exceeds its positive vertex limit')
    graph = {(0, 0): []}
    for arm, length in enumerate(saved['lengths'], 1):
        prev = (0, 0)
        for depth in range(1, length + 1):
            v = (arm, depth)
            graph[v] = [prev]
            graph[prev].append(v)
            prev = v
    retained = [v for v in graph if list(v) not in saved['holes']]
    depths, queue = {(0, 0): 0}, deque([(0, 0)])
    while queue:
        v = queue.popleft()
        for nb in graph[v]:
            if nb not in depths:
                depths[nb] = depths[v] + 1
                queue.append(nb)
    counts = [0] * saved['modulus']
    for v in retained:
        counts[depths[v] % saved['modulus']] += 1
    if counts != saved['residue_populations'] or len(retained) != 2 * saved['target_size']:
        raise ValueError('original-tree audit contradicts the terminal-tip certificate')
    return {"original_vertices": len(graph), "retained_vertices": len(retained),
            "residue_populations": counts, "original_tree_distances_checked": True}


def _howell_consistent_mod_2k(rows, rhs, modulus):
    """Exact Howell elimination over Z/2^k Z testing A*s == rhs (mod modulus)."""
    m = len(rows)
    n = len(rows[0])
    pivots = {}

    def insert_row(vec):
        vec = [x % modulus for x in vec]
        col = 0
        while col < m:
            val = vec[col]
            if val == 0:
                col += 1
                continue
            if col not in pivots:
                odd_part = val
                pw = 1
                while odd_part % 2 == 0:
                    odd_part //= 2
                    pw *= 2
                inv = pow(odd_part, -1, modulus)
                norm = [(x * inv) % modulus for x in vec]
                pivots[col] = norm
                if pw > 1:
                    mult = modulus // pw
                    insert_row([(x * mult) % modulus for x in norm])
                return
            prow = pivots[col]
            pv = prow[col]
            if val % pv == 0:
                q = val // pv
                for j in range(col, m):
                    vec[j] = (vec[j] - q * prow[j]) % modulus
                col += 1
            else:
                odd_part = val
                while odd_part % 2 == 0:
                    odd_part //= 2
                inv = pow(odd_part, -1, modulus)
                norm = [(x * inv) % modulus for x in vec]
                pivots[col] = norm
                q = pv // norm[col]
                old_reduced = [0] * m
                for j in range(col, m):
                    old_reduced[j] = (prow[j] - q * norm[j]) % modulus
                pw_new = norm[col]
                if pw_new > 1:
                    mult = modulus // pw_new
                    insert_row([(x * mult) % modulus for x in norm])
                vec = old_reduced
                col += 1

    for col_idx in range(n):
        insert_row([rows[r][col_idx] for r in range(m)])
    rem = [x % modulus for x in rhs]
    for col in range(m):
        if rem[col] == 0:
            continue
        if col not in pivots or rem[col] % pivots[col][col] != 0:
            return False, col
        prow = pivots[col]
        q = rem[col] // prow[col]
        for j in range(col, m):
            rem[j] = (rem[j] - q * prow[j]) % modulus
    return True, None


def linear_degree_obstruction_absence(lengths, holes, modulus=64, max_vertices=512):
    """Test all weighted-distance degree congruence equations mod 2^k simultaneously.

    For odd modulus M, 2*e_d(G) = sum_v deg_d(v) makes s_v = (M+1)/2 solve every
    degree-distance equation automatically, so no odd linear degree obstruction exists.
    For M = 2^k, Howell elimination on sum s_v = m and sum deg_d(v)*s_v = e_d(G)
    decides every linear combination of vertex-degree congruences mod 2^k at once.
    """
    lengths = validate_lengths(lengths)
    holes = validate_vertices(lengths, holes)
    if type(modulus) is not int or modulus < 2 or (modulus & (modulus - 1)) != 0 or modulus > 256:
        raise ValueError("modulus must be a power of two between 2 and 256")
    if type(max_vertices) is not int or max_vertices < 1 or 1 + sum(lengths) > max_vertices:
        raise ValueError("linear degree consistency check exceeds its positive vertex limit")
    vertices = [(0, 0)] + [(arm, d) for arm, length in enumerate(lengths, 1)
                           for d in range(1, length + 1)]
    hole_set = set(holes)
    retained = [v for v in vertices if v not in hole_set]
    if len(retained) % 2:
        raise ValueError("retained vertex count must be even for an equal-sized bipartition")
    target_size = len(retained) // 2
    max_d = lengths[0] + lengths[1]
    rows = [[1] * len(retained)] + [[0] * len(retained) for _ in range(max_d)]
    rhs = [target_size] + [0] * max_d
    for i, (a1, d1) in enumerate(retained):
        for j in range(i + 1, len(retained)):
            a2, d2 = retained[j]
            dist = abs(d1 - d2) if a1 == a2 else d1 + d2
            rows[dist][i] += 1
            rows[dist][j] += 1
            rhs[dist] += 1
    consistent, fail_row = _howell_consistent_mod_2k(rows, rhs, modulus)
    return {
        "lengths": list(lengths), "holes": [list(h) for h in holes],
        "retained_vertices": len(retained), "target_size": target_size,
        "modulus": modulus,
        "odd_modulus_linear_obstruction_impossible": True,
        "linear_degree_system_consistent": consistent,
        "failing_distance_row": fail_row,
        "scope": "concrete tree size only; tests all Z/2^k Z linear degree-distance equations",
        "infinite_family_proved": False,
    }


def verify_linear_degree_obstruction_absence(saved):
    if not isinstance(saved, dict) or not {"lengths", "holes", "modulus"} <= saved.keys():
        raise ValueError("linear-obstruction certificate must contain lengths, holes, and modulus")
    expected = linear_degree_obstruction_absence(saved["lengths"], saved["holes"], saved["modulus"])
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("linear-obstruction certificate differs from the reconstructed Howell solve")
    return expected


def aligned_tip_antisymmetry(lengths, tip_offset=4):
    """Prove exact sign antisymmetry on upper arm 1 & 2 intervals for aligned holes.

    For lengths (a >= b > c >= 1) and holes (1, a-q), (2, b-q) with 0 <= q <= b-c:
    every retained pair at distance a+b-r (0 <= r <= b-c-1) joins arm 1 and arm 2
    since same-arm, centre, and arm-3 pair distances are at most a+c = a+b-(b-c).
    By strong induction using index-set symmetry i <-> r-i, every r <= max_r
    (b-c-1 for q >= 1; b-c-2 for q == 0) with r != q satisfies s_2(b-r) = -s_1(a-r).
    """
    lengths = validate_lengths(lengths)
    a, b, c = lengths
    if not (a >= b > c >= 1):
        raise ValueError("aligned tip antisymmetry requires a >= b > c >= 1")
    if type(tip_offset) is not int or not 0 <= tip_offset <= b - c:
        raise ValueError("tip_offset must satisfy 0 <= q <= b - c")
    holes = ((1, a - tip_offset), (2, b - tip_offset))
    gap = b - c
    if tip_offset == 0 and gap < 2:
        raise ValueError("tip_offset=0 requires b - c >= 2 to force any antisymmetric pair")
    min_r = 1 if tip_offset == 0 else 0
    max_r = gap - 2 if tip_offset == 0 else gap - 1
    forced_offsets = [r for r in range(min_r, max_r + 1) if r != tip_offset]
    return {
        "lengths": [a, b, c], "tip_offset": tip_offset,
        "holes": [list(h) for h in holes], "arm_gap_b_minus_c": gap,
        "cross_arm1_3_ceiling": a + c, "max_forced_offset": max_r,
        "forced_offsets_count": len(forced_offsets),
        "sample_forced_pairs": [[[1, a - r], [2, b - r]] for r in forced_offsets[:4]],
        "tail_forced_pair": [[1, a - forced_offsets[-1]], [2, b - forced_offsets[-1]]],
        "all_top_pairs_antisymmetric": True,
        "every_colouring_of_this_support_excluded": False,
    }


def verify_aligned_tip_antisymmetry(saved):
    if not isinstance(saved, dict) or not {"lengths", "tip_offset"} <= saved.keys():
        raise ValueError("tip-antisymmetry certificate must contain lengths and tip_offset")
    expected = aligned_tip_antisymmetry(saved["lengths"], saved["tip_offset"])
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("tip-antisymmetry certificate differs from the reconstructed proof")
    return expected


def audit_aligned_tip_antisymmetry(saved, max_vertices=512):
    """Independently check distance bounds and RREF uniqueness on small trees."""
    saved = verify_aligned_tip_antisymmetry(saved)
    if type(max_vertices) is not int or max_vertices < 1 or 1 + sum(saved["lengths"]) > max_vertices:
        raise ValueError("original-tree audit exceeds its positive vertex limit")
    a, b, c = saved["lengths"]
    q = saved["tip_offset"]
    hole_set = set(map(tuple, saved["holes"]))
    vertices = [(0, 0)] + [(arm, d) for arm, length in enumerate(saved["lengths"], 1)
                           for d in range(1, length + 1)]
    retained = [v for v in vertices if v not in hole_set]
    gap = b - c
    max_r = saved["max_forced_offset"]
    for i, (a1, d1) in enumerate(retained):
        for j in range(i + 1, len(retained)):
            a2, d2 = retained[j]
            dist = abs(d1 - d2) if a1 == a2 else d1 + d2
            if dist >= a + b - (gap - 1) and {a1, a2} != {1, 2}:
                raise ValueError("non-(arm1,arm2) pair violated the tip distance ceiling")
    # Build symbolic linear equations for x_i = s_1(a-i), y_i = s_2(b-i), 0 <= i <= max_r, i != q
    active = [i for i in range(max_r + 1) if i != q]
    idx_x = {i: k for k, i in enumerate(active)}
    idx_y = {i: len(active) + k for k, i in enumerate(active)}
    nvars = 2 * len(active)
    mat = []
    for r in range(gap):
        row = [Fraction(0)] * nvars
        for i in range(r + 1):
            j = r - i
            if i != q and j != q and i in idx_x and j in idx_y:
                row[idx_x[i]] += 1
                row[idx_y[j]] += 1
        if any(row):
            mat.append(row)
    piv_row = 0
    piv_cols = []
    for col in range(nvars):
        piv = next((r for r in range(piv_row, len(mat)) if mat[r][col] != 0), None)
        if piv is None:
            continue
        mat[piv_row], mat[piv] = mat[piv], mat[piv_row]
        inv = 1 / mat[piv_row][col]
        mat[piv_row] = [v * inv for v in mat[piv_row]]
        for r in range(len(mat)):
            if r != piv_row and mat[r][col] != 0:
                fac = mat[r][col]
                mat[r] = [mat[r][k] - fac * mat[piv_row][k] for k in range(nvars)]
        piv_cols.append(col)
        piv_row += 1
    for i in range(1 if q == 0 else 0, max_r + 1):
        if i == q:
            continue
        vec = [Fraction(0)] * nvars
        vec[idx_x[i]] = Fraction(1)
        vec[idx_y[i]] = Fraction(1)
        for prow_idx, pcol in enumerate(piv_cols):
            if vec[pcol] != 0:
                fac = vec[pcol]
                vec = [vec[k] - fac * mat[prow_idx][k] for k in range(nvars)]
        if any(vec):
            raise ValueError("symbolic RREF did not force tip antisymmetry")
    return {"original_vertices": len(vertices), "retained_vertices": len(retained),
            "forced_offsets_verified": saved["forced_offsets_count"],
            "symbolic_rref_and_tree_checked": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter", type=int, default=0,
                        help="t in T(227+7560t,67+7560t,11+7560t)")
    parser.add_argument("--lengths", type=int, nargs=3,
                        help="instead use any three lengths in the proved domain")
    parser.add_argument("--holes", nargs=2, default=["0:0", "1:4"],
                        help="two arm:depth vertices (centre is 0:0)")
    parser.add_argument("--verify", type=Path, help="verify a saved JSON certificate")
    parser.add_argument("--interior-obstruction", action="store_true",
                        help="exclude every colouring for the interior-hole family")
    parser.add_argument("--extended-obstruction", action="store_true",
                        help="exclude every colouring for the mod8-q5, mod10-q2, or mod10-q0 families")
    parser.add_argument("--family", default="mod8-q5", choices=("mod8-q5", "mod10-q2", "mod10-q0"),
                        help="extended aligned interior-hole family")
    parser.add_argument("--terminal-tips", action="store_true",
                        help="exclude omitting two arm tips via the full-partition residue lemma")
    parser.add_argument("--arms", type=int, nargs=2, default=[1, 2],
                        help="two distinct arm numbers for --terminal-tips")
    parser.add_argument("--linear-obstruction-check", action="store_true",
                        help="test Z/2^k Z linear degree-distance consistency on concrete lengths")
    parser.add_argument("--modulus", type=int, default=64,
                        help="2-power modulus for --linear-obstruction-check")
    parser.add_argument("--tip-antisymmetry", action="store_true",
                        help="prove aligned tip antisymmetry s_2(b-r) = -s_1(a-r) for 0<=r<=b-c-1")
    parser.add_argument("--tip-offset", type=int, default=4,
                        help="aligned hole tip deficit q in 0<=q<=b-c for --tip-antisymmetry")
    parser.add_argument("--tail-blocks", type=int,
                        help="aligned hole deficit block index")
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
        if args.tail_blocks is not None and (not (args.interior_obstruction or args.extended_obstruction) or args.verify):
            parser.error('--tail-blocks requires --interior-obstruction or --extended-obstruction without --verify')
        other_modes = (
            args.extended_obstruction, args.terminal_tips, args.linear_obstruction_check,
            args.tip_antisymmetry, args.interior_obstruction, args.one_swap_obstruction,
            args.swap_adjacency, args.parity_obstruction, args.coarse,
        )
        if sum(bool(flag) for flag in other_modes) > 1:
            parser.error("proof modes cannot be combined")
        if args.linear_obstruction_check:
            if args.audit:
                parser.error("--linear-obstruction-check directly inspects concrete vertex distances without --audit")
            lengths = args.lengths if args.lengths else frontier_lengths(args.parameter)
            holes = [tuple(map(int, value.split(":"))) for value in args.holes]
            result = (verify_linear_degree_obstruction_absence(json.loads(args.verify.read_text()))
                      if args.verify else linear_degree_obstruction_absence(lengths, holes, args.modulus))
        elif args.tip_antisymmetry:
            if args.holes != ["0:0", "1:4"]:
                parser.error("--tip-antisymmetry fixes its two holes from --tip-offset")
            lengths = args.lengths if args.lengths else frontier_lengths(args.parameter)
            result = (verify_aligned_tip_antisymmetry(json.loads(args.verify.read_text()))
                      if args.verify else aligned_tip_antisymmetry(lengths, args.tip_offset))
        elif args.extended_obstruction:
            if args.holes != ["0:0", "1:4"]:
                parser.error('--extended-obstruction fixes its two holes from the arm lengths')
            result = (verify_extended_obstruction(json.loads(args.verify.read_text())) if args.verify
                      else extended_obstruction(args.lengths or frontier_lengths(args.parameter),
                                                args.family, args.tail_blocks))
        elif args.terminal_tips:
            if args.holes != ["0:0", "1:4"]:
                parser.error('--terminal-tips fixes its two holes from --arms')
            result = (verify_terminal_tip_obstruction(json.loads(args.verify.read_text())) if args.verify
                      else terminal_tip_obstruction(args.lengths or frontier_lengths(args.parameter),
                                                    tuple(args.arms)))
        elif args.interior_obstruction:
            if args.holes != ["0:0", "1:4"]:
                parser.error('--interior-obstruction fixes its two holes from the arm lengths')
            result = (verify_interior_obstruction(json.loads(args.verify.read_text())) if args.verify
                      else interior_obstruction(args.lengths or frontier_lengths(args.parameter),
                                                args.tail_blocks))
        elif args.one_swap_obstruction:
            if args.audit or args.lengths:
                parser.error("--one-swap-obstruction accepts only --verify")
            result = (verify_one_swap_obstruction(json.loads(args.verify.read_text()))
                      if args.verify else one_swap_obstruction_certificate())
        elif args.swap_adjacency:
            if args.audit or args.lengths:
                parser.error("--swap-adjacency accepts only --verify")
            result = (verify_swap_adjacency_certificate(json.loads(args.verify.read_text()))
                      if args.verify else swap_adjacency_certificate())
        elif args.parity_obstruction:
            if args.audit or args.lengths:
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
            audit = (audit_aligned_tip_antisymmetry(result) if args.tip_antisymmetry else
                     audit_extended_obstruction(result) if args.extended_obstruction else
                     audit_terminal_tip_obstruction(result) if args.terminal_tips else
                     audit_interior_obstruction(result) if args.interior_obstruction else
                     audit_coarse_certificate(result) if args.coarse else audit_original_tree(result))
            print(json.dumps({"certificate": result, "audit": audit}, indent=2))
        else:
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
