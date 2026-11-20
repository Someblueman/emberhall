"""Complete finite row types for singleton/pair EF1; standard library only.

Coverage rests on ROW_TYPE_CATALOGUE.md, not on a sampled utility grid.
The default budget admits four goods and refuses five before enumeration.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import combinations, product
import json
from math import comb, gcd
from typing import Sequence

Row = tuple[int, ...]


def comparison_forms(m: int) -> tuple[Row, ...]:
    """Coordinates, item differences, and two distinct items minus a third."""
    if type(m) is not int or m < 1:
        raise ValueError("the number of goods must be a positive integer")
    result = []
    for i in range(m):
        result.append(tuple(int(g == i) for g in range(m)))
    for i, j in combinations(range(m), 2):
        result.append(tuple(int(g == i) - int(g == j) for g in range(m)))
    for i, j in combinations(range(m), 2):
        for k in range(m):
            if k not in (i, j):
                result.append(tuple(int(g in (i, j)) - int(g == k) for g in range(m)))
    return tuple(result)


def _signature(row, forms) -> tuple[int, ...]:
    values = (sum(a*b for a, b in zip(form, row)) for form in forms)
    return tuple((v > 0) - (v < 0) for v in values)


def row_signature(row: Sequence[int | Fraction]) -> tuple[int, ...]:
    """The label-sensitive type; zeros and comparison ties are retained."""
    if not row or any(type(v) not in (int, Fraction) or v < 0 for v in row):
        raise ValueError("need a nonempty row of exact nonnegative rational values")
    return _signature(row, comparison_forms(len(row)))


def _scaled_inverse(matrix: tuple[Row, ...]) -> tuple[Row, ...] | None:
    """Return abs(det(A))*inverse(A), an integer matrix, or None if singular."""
    m = len(matrix)
    work = [[Fraction(v) for v in row] + [Fraction(i == j) for j in range(m)]
            for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for col in range(m):
        pivot = next((i for i in range(col, m) if work[i][col]), None)
        if pivot is None:
            return None
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            determinant = -determinant
        value = work[col][col]
        determinant *= value
        work[col] = [v/value for v in work[col]]
        for i in range(m):
            if i != col and work[i][col]:
                scale = work[i][col]
                work[i] = [v-scale*w for v, w in zip(work[i], work[col])]
    inverse = [[v*abs(determinant) for v in row[m:]] for row in work]
    if determinant.denominator != 1 or any(v.denominator != 1 for row in inverse for v in row):
        raise AssertionError("integer matrix produced a noninteger adjugate")
    return tuple(tuple(map(int, row)) for row in inverse)


@dataclass(frozen=True)
class RowCatalogue:
    goods: int
    rows: tuple[Row, ...]
    system_upper_bound: int
    bases_examined: int
    nonsingular_bases: int
    right_sides_checked: int
    nonnegative_solutions: int
    primitive_candidates: int

    def summary(self) -> dict:
        result = asdict(self)
        del result["rows"]
        result.update(row_types=len(self.rows), integer_bound=2**self.goods,
                      largest_representative=max(map(max, self.rows)))
        return result


def catalogue(m: int, *, max_systems: int = 1_000_000) -> RowCatalogue:
    """Enumerate every realizable type, or refuse the entire run before starting.

    Enumerate independent sets of m forms with right sides -1, 0, 1 (only
    0, 1 for coordinate forms). Clear the determinant, reject negative rows,
    divide by the coordinate gcd, and keep one row for each complete sign type.
    This is exponential work, with a declared upper bound on right-side systems.
    """
    if type(m) is not int or m < 1:
        raise ValueError("the number of goods must be a positive integer")
    if type(max_systems) is not int or max_systems < 1:
        raise ValueError("max_systems must be a positive integer")
    # Avoid constructing even the forms or an enormous power on a refused call.
    if m > max_systems.bit_length():
        raise ValueError("system budget exceeded before enumeration")
    form_count = m + m*(m-1)**2//2
    upper = comb(form_count, m) * 3**m
    if upper > max_systems:
        raise ValueError(f"system budget exceeded: upper bound {upper} > {max_systems}")
    forms = comparison_forms(m)
    bound = 2**m
    candidates = {(0,)*m}
    bases = nonsingular = systems = nonnegative = 0
    for indices in combinations(range(len(forms)), m):
        bases += 1
        inverse = _scaled_inverse(tuple(forms[i] for i in indices))
        if inverse is None:
            continue
        nonsingular += 1
        domains = [(0, 1) if i < m else (-1, 0, 1) for i in indices]
        for right in product(*domains):
            systems += 1
            row = tuple(sum(a*b for a, b in zip(coefs, right)) for coefs in inverse)
            if min(row) < 0:
                continue
            if max(row) > bound:
                raise AssertionError("Cramer/Hadamard coordinate bound failed")
            nonnegative += 1
            divisor = gcd(*row)
            candidates.add(tuple(v//divisor for v in row) if divisor else row)
    representatives = {}
    for row in sorted(candidates, key=lambda r: (max(r), sum(r), r)):
        representatives.setdefault(_signature(row, forms), row)
    return RowCatalogue(m, tuple(representatives[s] for s in sorted(representatives)),
                        upper, bases, nonsingular, systems, nonnegative, len(candidates))


def _components(mask: int, neighbors: tuple[int, ...]) -> tuple[int, ...]:
    components = []
    while mask:
        reached = frontier = mask & -mask
        mask ^= frontier
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            fresh = neighbors[bit.bit_length()-1] & mask
            mask ^= fresh
            reached |= fresh
            frontier |= fresh
        components.append(reached)
    return tuple(components)


def graph_census(bank: RowCatalogue, sizes: tuple[int, ...]) -> dict:
    """All real-profile EF1 vertex sets for a small labeled size vector.

    Row predicates are deduplicated before taking their Cartesian product.
    Every fixed-size allocation is considered, including non-picking states.
    """
    m, n = bank.goods, len(sizes)
    if (m > 4 or n < 2 or any(type(s) is not int or s not in (1, 2) for s in sizes)
            or sum(sizes) != m):
        raise ValueError("census requires at most four goods and singleton/pair bundles")
    states = tuple(a for a in product(range(n), repeat=m)
                   if tuple(a.count(i) for i in range(n)) == sizes)
    index = {state: k for k, state in enumerate(states)}
    bundles = [[tuple(g for g in range(m) if a[g] == i) for i in range(n)] for a in states]
    neighbors = []
    for state in states:
        mask = 0
        for x, y in combinations(range(m), 2):
            if state[x] != state[y]:
                changed = list(state)
                changed[x], changed[y] = changed[y], changed[x]
                mask |= 1 << index[tuple(changed)]
        neighbors.append(mask)
    neighbors = tuple(neighbors)
    observer_masks = []
    for observer in range(n):
        masks = set()
        for row in bank.rows:
            fair = 0
            for k, allocation in enumerate(bundles):
                own = sum(row[g] for g in allocation[observer])
                if all(len(target) < 2 or own >= min(row[g] for g in target)
                       for target in allocation):
                    fair |= 1 << k
            masks.add(fair)
        observer_masks.append(tuple(sorted(masks)))
    graphs = set()
    for masks in product(*observer_masks):
        fair = (1 << len(states))-1
        for mask in masks:
            fair &= mask
        graphs.add(fair)
    histogram = {}
    diameter = 0
    disconnected = empty = 0
    for fair in graphs:
        groups = _components(fair, neighbors)
        empty += not groups
        disconnected += len(groups) > 1
        histogram[len(groups)] = histogram.get(len(groups), 0)+1
        for start in range(len(states)):
            if not fair & (1 << start):
                continue
            reached = frontier = 1 << start
            distance = -1
            while frontier:
                distance += 1
                following = 0
                for k in range(len(states)):
                    if frontier & (1 << k):
                        following |= neighbors[k]
                frontier = following & fair & ~reached
                reached |= frontier
            diameter = max(diameter, distance)
    return {"sizes": list(sizes), "allocations": len(states),
            "row_profiles_covered": len(bank.rows)**n,
            "observer_types": list(map(len, observer_masks)), "distinct_graphs": len(graphs),
            "component_histogram": dict(sorted(histogram.items())),
            "empty_graphs": empty, "disconnected_graphs": disconnected,
            "maximum_component_diameter": diameter}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goods", type=int, default=3)
    parser.add_argument("--max-systems", type=int, default=1_000_000)
    parser.add_argument("--rows", action="store_true", help="include every representative")
    parser.add_argument("--sizes", help="also census all EF1 graphs, e.g. 2,2 or 2,1,1")
    args = parser.parse_args()
    try:
        bank = catalogue(args.goods, max_systems=args.max_systems)
        result = bank.summary()
        if args.rows:
            result["rows"] = bank.rows
        if args.sizes:
            result["graph_census"] = graph_census(bank, tuple(map(int, args.sizes.split(","))))
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
