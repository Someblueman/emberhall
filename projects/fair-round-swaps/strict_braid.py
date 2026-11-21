"""Exact bounded-integer refinement of a canonical braid, not connectivity."""

from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations
import json
from math import comb, isqrt, lcm
from pathlib import Path

from swaps import Profile, ef1, exchange, validate_profile

# Integer refinement of Tern d7bebfd's retained twelve-good profile. The
# accompanying path is a positive witness, not a connectivity certificate.
FRONTIER = (
    (185, 119, 65, 47, 15, 11, 7, 39, 41, 23, 1, 53),
    (297, 7, 171, 125, 79, 15, 33, 11, 17, 3, 45, 31),
    (254, 166, 13, 87, 78, 15, 27, 4, 22, 3, 50, 8),
    (296, 29, 187, 108, 78, 18, 7, 10, 48, 2, 1, 4),
    (153, 77, 71, 75, 53, 49, 21, 17, 35, 1, 19, 27),
    (22, 19, 17, 15, 11, 18, 21, 13, 16, 12, 14, 20),
    (22, 14, 17, 16, 19, 13, 12, 21, 15, 20, 18, 11),
)
FRONTIER_SWAPS = ((6, 8), (10, 11), (2, 7), (0, 2), (2, 6), (10, 11), (7, 8))


def validate_braid(u: Profile) -> int:
    validate_profile(u)
    r, m = len(u) - 2, len(u[0])
    if r < 1 or m != 2*r + 2:
        raise ValueError("need r double recipients, two carriers, and 2r+2 goods")
    if any(u[i][i+1] < u[i][g] for i in range(r) for g in range(i+2, m)):
        raise ValueError("anchors must be greedy in their listed order")
    if any(u[i][0] < value for i in (r, r+1) for value in u[i]):
        raise ValueError("good zero must maximize both carrier rows")
    if any(u[r][r+1] < u[r][g] or u[r+1][r+2] < u[r+1][g]
           for g in range(r+1, m)):
        raise ValueError("carrier alternatives must maximize the tail pool")
    return r


def endpoints(r: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if type(r) is not int or r < 1:
        raise ValueError("need a positive number of double recipients")
    start = (r,) + tuple(range(r)) + (0, r+1) + tuple(range(1, r))
    target = (r+1,) + tuple(range(r)) + (r, 0) + tuple(range(1, r))
    return start, target


def _forms(m):
    """One representative per singleton comparison; every pair comparison."""
    for a, b in combinations(range(m), 2):
        yield ((a, 1), (b, -1))
    for a, b in combinations(range(m), 2):
        for c in range(m):
            if c not in (a, b):
                yield ((a, 1), (b, 1), (c, -1))


def _dot(form, row):
    return sum(coefficient * row[g] for g, coefficient in form)


def _direction(basis, m):
    """A nonzero null vector of independent rows, with a negative free entry."""
    rows = [[Fraction(v) for v in row] for row in basis]
    pivots = []
    for col in range(m):
        pivot = next((k for k in range(len(pivots), len(rows)) if rows[k][col]), None)
        if pivot is None:
            continue
        k = len(pivots)
        rows[k], rows[pivot] = rows[pivot], rows[k]
        scale = rows[k][col]
        rows[k] = [v / scale for v in rows[k]]
        for j in range(len(rows)):
            if j != k:
                scale = rows[j][col]
                rows[j] = [v - scale*w for v, w in zip(rows[j], rows[k])]
        pivots.append(col)
    if len(pivots) != len(basis):
        raise AssertionError("dependent active rows")
    free = next(g for g in range(m) if g not in pivots)
    direction = [Fraction(0)] * m
    direction[free] = -1
    for row, pivot in zip(rows, pivots):
        direction[pivot] = row[free]
    return direction


def _determinant(matrix):
    rows = [[Fraction(v) for v in row] for row in matrix]
    result = Fraction(1)
    for col in range(len(rows)):
        pivot = next((k for k in range(col, len(rows)) if rows[k][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            result = -result
        value = rows[col][col]
        result *= value
        for k in range(col+1, len(rows)):
            factor = rows[k][col] / value
            for j in range(col+1, len(rows)):
                rows[k][j] -= factor * rows[col][j]
    if result.denominator != 1:
        raise AssertionError("integer matrix has a noninteger determinant")
    return int(result)


def _integer_cell(row, forms, bound):
    """Reach a vertex of a rational sign cell, retaining zero equalities."""
    m = len(row)
    constraints = [((g, 1),) for g in range(m)]
    basis, echelon = [], {}
    for form in forms:
        value = _dot(form, row)
        if value:
            constraints.append(form if value > 0 else tuple((g, -c) for g, c in form))
            continue
        # Keep an independent subset of the homogeneous equalities. Their
        # echelon span contains all zero forms, including dependent ones.
        dense = [0] * m
        for g, c in form:
            dense[g] = c
        reduced = list(map(Fraction, dense))
        for pivot, previous in sorted(echelon.items()):
            scale = reduced[pivot]
            reduced = [a-scale*b for a, b in zip(reduced, previous)]
        pivot = next((g for g, v in enumerate(reduced) if v), None)
        if pivot is not None:
            scale = reduced[pivot]
            echelon[pivot] = [v/scale for v in reduced]
            basis.append(dense)
    point = list(map(Fraction, row))
    minimum = min(_dot(form, point) for form in constraints)
    if minimum <= 0:
        raise ValueError("cell requires positive coordinates and signed forms")
    if minimum < 1:
        point = [v/minimum for v in point]
    for _ in range(m-len(basis)):
        direction = _direction(basis, m)
        candidates = [((_dot(form, point)-1) / -slope, k)
                      for k, form in enumerate(constraints)
                      if (slope := _dot(form, direction)) < 0]
        # A negative free coordinate supplies at least one blocking unit row.
        step, chosen = min(candidates)
        point = [v + step*d for v, d in zip(point, direction)]
        active = [0] * m
        for g, c in constraints[chosen]:
            active[g] = c
        basis.append(active)
    determinant = abs(_determinant(basis))
    integers = [v * determinant for v in point]
    if (not determinant or any(v.denominator != 1 for v in integers)
            or any(_dot(form, point) < 1 for form in constraints)):
        raise AssertionError("invalid exact vertex")
    result = tuple(map(int, integers))
    if any(not 1 <= v <= bound for v in result):
        raise AssertionError("Cramer/Hadamard bound failed")
    return result


def strict_braid(u: Profile) -> Profile:
    """Return positive integers <=2**m; no formerly unfair allocation is fair.

    Every nonzero local comparison keeps its sign. Zero comparisons may acquire
    either sign. Canonical endpoint ranks survive; arbitrary tied witnesses need
    not. The mathematical real-input reduction is in STRICT_BRAID.md.
    """
    r = validate_braid(u)
    m = len(u[0])
    result = []
    for i, row in enumerate(u):
        priority = list(range(m))
        if i >= r:
            best = r+1 if i == r else r+2
            priority = [0, best] + [g for g in range(m) if g not in (0, best)]
        direction = [0] * m
        for k, g in enumerate(priority):
            direction[g] = 2**(m-1-k)
        scale = lcm(*(Fraction(v).denominator for v in row))
        perturbed = tuple(int(v*scale) * 2**(m+1) + direction[g]
                          for g, v in enumerate(row))
        result.append(_integer_cell(perturbed, _forms(m), 2**m))
    result = tuple(result)
    validate_braid(result)
    refinement_report(u, result)
    return result


def refinement_report(before: Profile, after: Profile) -> dict[str, int]:
    """Check the local certificate sufficient for the full EF1 graph inclusion."""
    r = validate_braid(before)
    if validate_braid(after) != r:
        raise ValueError("different braid sizes")
    m = len(before[0])
    if any(type(v) is not int or not 1 <= v <= 2**m for row in after for v in row):
        raise ValueError("expected positive integers within the proved bound")
    checked = zeros = 0
    for old, new in zip(before, after):
        for form in _forms(m):
            a, b = _dot(form, old), _dot(form, new)
            if not b or (a and (a > 0) != (b > 0)):
                raise ValueError("a nonzero comparison changed sign or a tie survived")
            checked += 1
            zeros += a == 0
    return {"pairs": r, "goods": m, "integer_bound": 2**m,
            "comparisons_checked": checked, "original_ties": zeros}


def _balanced_forms(m, sizes, max_forms):
    """Every possible EF1 deletion comparison, plus every item ranking."""
    counts = sorted(set(sizes))
    estimate = comb(m, 2) + sum(comb(m, a)*comb(m-a, b-1)
                              for a in counts for b in counts if b > 1 and a+b-1 <= m)
    if max_forms is not None and estimate > max_forms:
        raise ValueError(f"comparison budget exceeded: upper bound {estimate} > {max_forms}")
    forms = {((a, 1), (b, -1)) for a, b in combinations(range(m), 2)}
    for a in counts:
        for own in combinations(range(m), a):
            remaining = tuple(g for g in range(m) if g not in own)
            for b in counts:
                if b <= 1:
                    continue
                for rest in combinations(remaining, b-1):
                    form = tuple(sorted([(g, 1) for g in own] + [(g, -1) for g in rest]))
                    if form[0][1] < 0:
                        form = tuple((g, -c) for g, c in form)
                    forms.add(form)
    return tuple(sorted(forms))


def _balanced_domain(u, sizes, max_forms):
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (len(sizes) != n or any(type(s) is not int or s < 1 for s in sizes)
            or sum(sizes) != m or max(sizes)-min(sizes) > 1):
        raise ValueError("need positive balanced bundle sizes summing to the number of goods")
    if max_forms is not None and (type(max_forms) is not int or max_forms < 1):
        raise ValueError("comparison budget must be positive or None")
    forms = _balanced_forms(m, sizes, max_forms)
    bound = isqrt(max(3, 2*max(sizes))**m)
    return forms, bound


def bounded_profile(u: Profile, sizes: tuple[int, ...], *, max_forms=100000) -> Profile:
    """Preserve the entire EF1 graph and all ranking ties for balanced sizes.

    This does not force strict rankings. Each integer entry is at most
    floor(sqrt(max(3, 2*max(sizes))**m)). A comparison-budget refusal is not a
    mathematical verdict. Passing max_forms=None explicitly removes the cap.
    """
    forms, bound = _balanced_domain(u, sizes, max_forms)
    result = []
    for row in u:
        nonzero = [abs(value) for form in forms if (value := _dot(form, row))]
        shift = Fraction(min(nonzero))/4 if nonzero else Fraction(1)
        positive = tuple(Fraction(v)+shift for v in row)
        converted = _integer_cell(positive, forms, bound)
        # After the positive shift, preserve the full sign cell, including
        # equalities. Item ties have coefficient sum zero and survive the shift.
        for form in forms:
            a, b = _dot(form, positive), _dot(form, converted)
            if (a > 0)-(a < 0) != (b > 0)-(b < 0):
                raise AssertionError("integer compression changed its sign cell")
        result.append(converted)
    return tuple(result)


def balanced_report(before, after, sizes, *, max_forms=100000):
    """Validate an integer graph-equivalent representative by local signs."""
    forms, bound = _balanced_domain(before, sizes, max_forms)
    validate_profile(after)
    if len(after) != len(before) or len(after[0]) != len(before[0]):
        raise ValueError("different matrix dimensions")
    if any(type(v) is not int or not 1 <= v <= bound for row in after for v in row):
        raise ValueError("representative exceeds the positive integer bound")
    for old, new in zip(before, after):
        for form in forms:
            a, b = _dot(form, old), _dot(form, new)
            expected = (a > 0)-(a < 0) if a else sum(c for _, c in form)
            if (expected > 0)-(expected < 0) != (b > 0)-(b < 0):
                raise ValueError("a local comparison or ranking tie was not preserved")
    return {"goods": len(before[0]), "integer_bound": bound,
            "comparisons_checked": len(before)*len(forms),
            "scope": "same entire EF1 graph and weak rankings; connectivity not decided"}


def example(r=5) -> Profile:
    if type(r) is not int or r < 1:
        raise ValueError("need a positive number of pairs")
    m = 2*r+2
    rows = [[(g+i) % 4 for g in range(m)] for i in range(r+2)]
    for i in range(r):
        rows[i][i+1] = max(rows[i][i+1:])
    for i, best in ((r, r+1), (r+1, r+2)):
        rows[i][best] = max(rows[i][r+1:])
        rows[i][0] = max(rows[i])
    return tuple(map(tuple, rows))


def frontier_path(u=FRONTIER):
    if validate_braid(u) != 5:
        raise ValueError("the retained path requires a twelve-good braid")
    route = [endpoints(5)[0]]
    for x, y in FRONTIER_SWAPS:
        state = list(route[-1])
        state[x], state[y] = state[y], state[x]
        route.append(tuple(state))
    if (route[-1] != endpoints(5)[1] or not all(a[0] in (5, 6) and ef1(u, a) for a in route)
            or not all(exchange(a, b) for a, b in zip(route, route[1:]))):
        raise ValueError("the retained path is not valid for these utilities")
    return route


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON utility rows: integers or rational strings")
    parser.add_argument("--pairs", type=int, default=5)
    parser.add_argument("--frontier", action="store_true", help="replay the retained strict case")
    parser.add_argument("--sizes", help="comma-separated balanced sizes; requires --input")
    args = parser.parse_args()
    if args.frontier and (args.input or args.sizes):
        parser.error("choose either --frontier or --input")
    if args.sizes and not args.input:
        parser.error("--sizes requires --input")
    if args.frontier:
        print(json.dumps({"utilities": FRONTIER, "path": frontier_path(), "exchanges": 7,
                          "scope": "one connected strict profile; no universal verdict"}))
        return
    u = example(args.pairs)
    if args.input:
        data = json.loads(args.input.read_text())
        if (not isinstance(data, list) or not all(isinstance(row, list) for row in data)
                or any(type(v) not in (int, str) for row in data for v in row)):
            raise ValueError("expected a matrix of integers or rational strings")
        u = tuple(tuple(Fraction(v) for v in row) for row in data)
    if args.sizes:
        sizes = tuple(int(s) for s in args.sizes.split(','))
        result = bounded_profile(u, sizes)
        print(json.dumps({**balanced_report(u, result, sizes), "utilities": result}))
        return
    result = strict_braid(u)
    print(json.dumps({**refinement_report(u, result), "utilities": result,
                      "scope": "EF1 graph inclusion only; connectivity is not decided"}))


if __name__ == "__main__":
    main()
