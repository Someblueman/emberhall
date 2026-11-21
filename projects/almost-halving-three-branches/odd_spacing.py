"""A proved odd-spacing family with short arm four; standard library only."""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import reduce
import json
from math import gcd, lcm

from next_family import add, monomial, multiply, scale
from published_cases import check_pair


def four_short_witness(b: int) -> dict:
    """Target-size pair on T(2b-4,b,4), for every odd integer b>=5."""
    if type(b) is not int or b < 5 or b % 2 != 1:
        raise ValueError("require an odd integer b >= 5")
    signs = {(0, 0): 1}
    for p in range(1, 2 * b - 3):
        if p <= b - 2:
            sign = -1 if p % 2 else 1
        elif p == b - 1:
            sign = -1
        elif p == b:
            sign = 1
        else:
            sign = 1 if p % 2 else -1
        signs[1, p] = sign
    for p in range(1, b - 1):
        signs[2, p] = 1 if p % 2 else -1
    for p in range(1, 5):
        signs[3, p] = -1 if p % 2 else 1
    left = sorted(v for v, sign in signs.items() if sign == 1)
    right = sorted(v for v, sign in signs.items() if sign == -1)
    lengths = (2 * b - 4, b, 4)
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != (3 * b - 1) // 2:
        raise ArithmeticError("four-short-arm construction failed")
    return {**result, "lengths": lengths, "left": left, "right": right,
            "b": b, "d": b - 4, "omitted": [(2, b - 1), (2, b)],
            "construction": "odd middle, short arm four"}


def symbolic_residual() -> dict:
    """D*Q in independent z,u, with D=1+z and u=z**b."""
    one, z = monomial(), monomial(1)
    denominator = add(one, z)
    ends = (monomial(-4, 2), monomial(-2, 1), monomial(4))
    numerators = (
        add(scale(z, -1), scale(monomial(-1, 1), -2),
            scale(monomial(-3, 2), -1)),
        add(z, monomial(-1, 1)),
        add(monomial(5), scale(z, -1)),
    )
    result = multiply(denominator, add(one, *[scale(a, -1) for a in ends]))
    for i, p in enumerate(numerators):
        reflected = {(-a, -b): value for (a, b), value in p.items()}
        result = add(result,
                     multiply(p, add(one, *[scale(a, -1) for j, a in enumerate(ends)
                                           if j != i])),
                     scale(multiply(multiply(z, ends[i]), reflected), -1))
    return result


def template_obstruction_identity() -> dict:
    """Check the cleared constant-shell residual of the forced numerator.

    Here the second independent variable is v=z**c, not u=z**b.
    The residual is -2*(z**4-v)*(z-1), forcing c=4.
    """
    one, z, v = monomial(), monomial(1), monomial(0, 1)
    denominator = add(monomial(4), scale(one, -1))
    numerator = multiply(z, add(monomial(4, 1), v,
                                 scale(monomial(4), -3), one))
    reflected = {(-a, -b): value for (a, b), value in numerator.items()}
    actual = add(numerator, multiply(monomial(5, 1), reflected),
                 scale(multiply(multiply(add(one, z), add(v, scale(one, -1))),
                                denominator), -1))
    expected = scale(multiply(add(monomial(4), scale(v, -1)),
                              add(z, scale(one, -1))), -2)
    return add(actual, scale(expected, -1))


def _reduced_system(rows: list[list[int]], columns: int) -> tuple[list, list[int]]:
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivots = []
    for column in range(columns):
        rank = len(pivots)
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        row = matrix[rank] = [value / divisor for value in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = [a - factor*b for a, b in zip(matrix[i], row)]
        pivots.append(column)
    return matrix, pivots


def _bounded_signs(constraints: list, free: list[int], max_nodes: int) -> tuple[dict | None, int, bool]:
    nodes = 0

    def visit(assigned: dict[int, int]) -> dict | None:
        nonlocal nodes
        if nodes == max_nodes:
            raise TimeoutError
        nodes += 1
        while True:
            changed = False
            for coefficients, targets in constraints:
                total = sum(a*assigned[j] for j, a in coefficients.items() if j in assigned)
                remaining = {j: a for j, a in coefficients.items() if j not in assigned}
                radius = sum(abs(a) for a in remaining.values())
                divisor = reduce(gcd, (abs(a) for a in remaining.values()), 0)
                allowed = [target for target in targets
                           if total-radius <= target <= total+radius
                           and (not divisor or (target-total+sum(remaining.values())) % (2*divisor) == 0)]
                if not allowed:
                    return None
                if len(remaining) == 1:
                    j, coefficient = next(iter(remaining.items()))
                    signs = [sign for sign in (-1, 1) if total+coefficient*sign in allowed]
                    if len(signs) == 1:
                        assigned[j] = signs[0]
                        changed = True
            if not changed:
                break
        if len(assigned) == len(free):
            return assigned
        def weight(j: int) -> float:
            return sum(abs(row[j]) / sum(k not in assigned for k in row)
                       for row, _ in constraints if j in row)
        column = max((j for j in free if j not in assigned), key=weight)
        for sign in (1, -1):
            answer = visit({**assigned, column: sign})
            if answer is not None:
                return answer
        return None

    try:
        return visit({}), nodes, False
    except TimeoutError:
        return None, nodes, True


def search_prefix(b: int, d: int, *, max_nodes: int = 100_000) -> dict:
    """Finite search omitting the middle arm's last two vertices only.

    Failure says nothing about pairs using another retained vertex set.
    The vertex cap bounds rational elimination before the node budget applies.
    """
    if (type(b) is not int or type(d) is not int or b < 3 or b % 2 != 1
            or not 0 < d < b or type(max_nodes) is not int or max_nodes < 1):
        raise ValueError("require odd b >= 3, integer 0 < d < b and positive node budget")
    if 3*b-1 > 200:
        raise ValueError("finite search is limited to 200 retained vertices")
    lengths = (b+d, b, b-d)
    retained = (b+d, b-2, b-d)
    vertices = [(0, 0)] + [(a, p) for a, length in enumerate(retained, 1)
                            for p in range(1, length+1)]
    n = len(vertices)
    rows = [[1]*n + [0]]
    for k in range(1, sum(sorted(retained)[-2:])+1):
        row = []
        for a, p in vertices:
            value = sum(k <= length for length in retained) if a == 0 else (
                int(p == k) + int(p-k >= 1) + int(p+k <= retained[a-1])
                + sum(1 <= k-p <= length for j, length in enumerate(retained, 1) if j != a))
            row.append(value)
        rows.append(row + [0])
    rows.append([1] + [0]*(n-1) + [1])  # Fix centre sign; global reversal loses no pair.
    matrix, pivots = _reduced_system(rows, n)
    base = {"lengths": lengths, "b": b, "d": d,
            "omitted": [(2, b-1), (2, b)], "max_nodes": max_nodes}
    if any(not any(row[:n]) and row[n] for row in matrix):
        return {**base, "search_status": "no-prefix-pair", "nodes": 0}
    free = [j for j in range(n) if j not in pivots]
    constraints = []
    for row in matrix[:len(pivots)]:
        denominator = lcm(*(value.denominator for value in row))
        coefficients = {j: int(row[j]*denominator) for j in free if row[j]}
        constant = int(row[-1]*denominator)
        constraints.append((coefficients, (constant-denominator, constant+denominator)))
    assigned, nodes, limited = _bounded_signs(constraints, free, max_nodes)
    if assigned is None:
        return {**base, "search_status": "node-limit" if limited else "no-prefix-pair",
                "nodes": nodes}
    signs = [0]*n
    for j, value in assigned.items():
        signs[j] = value
    for i, j in enumerate(pivots):
        value = matrix[i][-1] - sum(matrix[i][k]*signs[k] for k in free)
        if value not in (-1, 1):
            raise ArithmeticError("sign reconstruction failed")
        signs[j] = int(value)
    left = [v for v, sign in zip(vertices, signs) if sign == 1]
    right = [v for v, sign in zip(vertices, signs) if sign == -1]
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != (3*b-1)//2:
        raise ArithmeticError("finite prefix search failed its exact check")
    return {**base, **result, "left": left, "right": right,
            "search_status": "found", "nodes": nodes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--search-spacing", type=int, metavar="D",
                        help="finite middle-prefix search at spacing D; not a general proof")
    parser.add_argument("--nodes", type=int, help="finite-search node budget (default 100000)")
    args = parser.parse_args()
    if args.nodes is not None and args.search_spacing is None:
        parser.error("--nodes requires --search-spacing")
    if args.prove:
        if args.b is not None or args.search_spacing is not None:
            parser.error("--prove does not take b")
        if symbolic_residual() or template_obstruction_identity():
            raise ArithmeticError("nonzero symbolic residual")
        print("PASS: construction identity and fixed-template obstruction")
        return 0
    if args.b is None:
        parser.error("give b, or --prove")
    try:
        result = (four_short_witness(args.b) if args.search_spacing is None
                  else search_prefix(args.b, args.search_spacing,
                                     max_nodes=100_000 if args.nodes is None else args.nodes))
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
