"""Exact retained-tree search and a proved b=2d+3 subfamily.

The full two-middle-tip conjecture remains open. See MIDDLE_PREFIX.md.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import lcm

from next_family import add, monomial, multiply, scale
from progression_partitions import validate
from published_cases import check_pair


def parameters(b: int, d: int) -> tuple[int, int, int]:
    validate(b, d)
    if b < 3 or b % 2 != 1 or d % 2 != 1:
        raise ValueError("require odd b >= 3 and odd 1 <= d < b")
    return b + d, b - 2, b - d


def shell_rows(lengths: tuple[int, int, int]) -> tuple[list, list[dict]]:
    vertices = [(0, 0)] + [(arm, p) for arm, length in enumerate(lengths, 1)
                            for p in range(1, length + 1)]
    rows = [{i: 1 for i in range(len(vertices))}]
    rows += [{} for _ in range(sum(sorted(lengths)[-2:]))]
    for i, (arm, p) in enumerate(vertices):
        for j, (other, q) in enumerate(vertices):
            if i != j:
                distance = abs(p - q) if arm == other else p + q
                rows[distance][i] = rows[distance].get(i, 0) + 1
    return vertices, rows


def reduce_rows(rows: list[dict]) -> dict[int, dict[int, Fraction]]:
    """Exact sparse row reduction; no floating-point rank decisions."""
    pivots = {}
    for source in sorted(rows, key=len):
        row = {i: Fraction(c) for i, c in source.items() if c}
        while row:
            j = min(row)
            if j not in pivots:
                c = row[j]
                pivots[j] = {i: value / c for i, value in row.items()}
                break
            c = row[j]
            for i, value in pivots[j].items():
                row[i] = row.get(i, 0) - c * value
                if not row[i]:
                    del row[i]
    for j in sorted(pivots, reverse=True):
        for k, row in pivots.items():
            if k < j and j in row:
                c = row[j]
                for i, value in pivots[j].items():
                    row[i] = row.get(i, 0) - c * value
                    if not row[i]:
                        del row[i]
    return pivots


def sign_search(constraints: list[tuple], targets: list[int], n: int,
                node_limit: int) -> tuple[list[int] | None, int, bool]:
    """Return (signs, visited nodes, exhausted); a limit is never a negative."""
    nodes = 0

    def possible(total: int, terms: list, target: int) -> bool:
        radius = sum(abs(c) for _, c in terms)
        if abs(total) > target + radius:
            return False
        # Exact reachable signed sums, shifted upward by radius.
        bits = 1
        for _, c in terms:
            bits |= bits << (2 * abs(c))
        return any(offset >= 0 and (bits >> offset) & 1
                   for offset in (target - total + radius, -target - total + radius))

    def visit(signs: list[int]) -> list[int] | None:
        nonlocal nodes
        nodes += 1
        if nodes > node_limit:
            raise TimeoutError
        while True:
            changed = False
            live = []
            for row, target in zip(constraints, targets):
                total = sum(c * signs[i] for i, c in row if signs[i])
                terms = [(i, c) for i, c in row if not signs[i]]
                radius = sum(abs(c) for _, c in terms)
                if target == 1 and abs(total) + radius <= 1 and (total + radius) % 2 == 1:
                    continue
                if not possible(total, terms, target):
                    return None
                if terms:
                    live.append(terms)
                for i, c in terms:
                    others = [(j, a) for j, a in terms if j != i]
                    plus = possible(total + c, others, target)
                    minus = possible(total - c, others, target)
                    if plus != minus:
                        signs[i] = 1 if plus else -1
                        changed = True
                        break
                if changed:
                    break
            if not changed:
                break
        if not live:
            return [s or 1 for s in signs]
        scores = [0.0] * n
        for row in live:
            for i, c in row:
                scores[i] += abs(c) / len(row) ** 2
        j = max(range(n), key=lambda i: scores[i])
        for sign in (1, -1):
            child = signs.copy()
            child[j] = sign
            result = visit(child)
            if result is not None:
                return result
        return None

    try:
        # Global sign reversal preserves every constraint.
        result = visit([1] + [0] * (n - 1)) if n else visit([])
    except TimeoutError:
        return None, node_limit, False
    return result, nodes, True


def checked_witness(b: int, d: int, signs: dict) -> dict:
    retained = parameters(b, d)
    vertices = {(0, 0)} | {(i, p) for i, length in enumerate(retained, 1)
                           for p in range(1, length + 1)}
    if set(signs) != vertices or any(s not in (-1, 1) for s in signs.values()):
        raise ValueError("signs must colour every retained vertex exactly once")
    left = sorted(v for v, s in signs.items() if s == 1)
    right = sorted(v for v, s in signs.items() if s == -1)
    lengths = b + d, b, b - d
    result = check_pair(lengths, left, right)
    if not result["homometric"] or len(left) != (3 * b - 1) // 2:
        raise ValueError("retained signs are not a balanced homometric partition")
    return {**result, "lengths": lengths, "retained_lengths": retained,
            "left": left, "right": right, "omitted": [(2, b - 1), (2, b)]}


def search(b: int, d: int, node_limit: int = 100000) -> dict:
    retained = parameters(b, d)
    if type(node_limit) is not int or node_limit < 1:
        raise ValueError("node limit must be a positive integer")
    if sum(retained) + 1 > 900:
        raise ValueError("exact search is limited to 900 retained vertices")
    vertices, rows = shell_rows(retained)
    pivots = reduce_rows(rows)
    free = [i for i in range(len(vertices)) if i not in pivots]
    indices = {j: i for i, j in enumerate(free)}
    constraints, targets = [], []
    for j, row in sorted(pivots.items()):
        denominator = lcm(*(c.denominator for c in row.values()))
        constraints.append(tuple((indices[i], int(c * denominator))
                                 for i, c in sorted(row.items()) if i != j))
        targets.append(denominator)
    values, nodes, exhausted = sign_search(constraints, targets, len(free), node_limit)
    result = {"b": b, "d": d, "nodes": nodes, "node_limit": node_limit,
              "retained_lengths": retained}
    if values is None:
        return {**result, "status": "no-partition" if exhausted else "node-limit"}
    signs = {j: values[i] for i, j in enumerate(free)}
    for j, row in pivots.items():
        signs[j] = -sum(c * signs[i] for i, c in row.items() if i != j)
    if any(s not in (-1, 1) for s in signs.values()):
        raise ArithmeticError("search returned a non-sign pivot value")
    return {**result, **checked_witness(b, d, {v: int(signs[i])
                                             for i, v in enumerate(vertices)}),
            "status": "partition"}


# Words start at offset 3; boundary words start at offset -2.
TABLES = {
    0: (
        ('-+-+ -+-+ -+++ -+++ -+-+ -+-+', '...++ +-+-+ +-+-+ +-+++ +-+++ +-+-+ +-+-+-++-'),
        ('+-+- +-+- -+-+ -+-+', '...-- -+-+- -+-++ +-+-+ +-+--+'),
        ('-+-- -+--', '...-- --+-- --+---+'),
    ),
    1: (
        ('++++ ++++ +-++ -+++ ++++ ++++', '...++ +++++ +++++ +-+++ -+++- +++++ ++++++++-'),
        ('---- ---- ---- ----', '...-- ----- ----- ----- -----+'),
        ('--+- -+--', '...-- --+-- -+----+'),
    ),
    2: (
        ('-+-+ -+-+ -+++ ++-+ -+-+ -+-+', '...++ +-+-+ +-+-+ +++-+ +-+++ +-+-+ +-+-+-++-'),
        ('+-+- +-+- -+-+ -+-+', '...-- -+-+- -+-++ +-+-+ +-+--+'),
        ('-+-- ---+', '...-- +---+ --+---+'),
    ),
    3: (
        ('++++ ++++ +-++ ++-+ ++++ ++++', '...++ +++++ +++++ +++-+ -+++- +++++ ++++++++-'),
        ('---- ---- ---- ----', '...-- ----- ----- ----- -----+'),
        ('--+- ---+', '...-- +---+ -+----+'),
    ),
}

SMALL_SIGNS = {
    0: ('+---+-', '+++', '---+'),
    1: ('---+-----+--', '+++++++', '-++--+'),
    2: ('----+---+---+----+', '++-++++-++-', '+-+++-++'),
    3: ('---+-+-----------+-+----', '-++++-++++-++++', '+++-++++-+'),
    4: ('++++++++++-+++-+++-++++++++++-', '------------------+', '---+---+---+'),
}


def family_signs(d: int) -> dict:
    """Full retained partition for b=2d+3; small bases plus four exact tables."""
    b = 2 * d + 3
    lengths = parameters(b, d)
    h = (d - 1) // 2
    if h < 5:
        words = SMALL_SIGNS[h]
        return {(0, 0): 1, **{(arm, p): 1 if s == "+" else -1
                               for arm, word in enumerate(words, 1)
                               for p, s in enumerate(word, 1)}}
    signs = {(0, 0): 1}
    for arm, ((words, boundaries), length) in enumerate(zip(TABLES[h % 4], lengths), 1):
        for j, word in enumerate(words.split()):
            for p in range(3, h - 2):
                signs[arm, j * h + p] = 1 if word[(p - 3) % 4] == "+" else -1
        for j, word in enumerate(boundaries.split()):
            for p, s in enumerate(word, -2):
                if s != ".":
                    if not 1 <= j * h + p <= length:
                        raise ArithmeticError("table boundary outside retained arm")
                    signs[arm, j * h + p] = 1 if s == "+" else -1
    return signs


def symbolic_residual(m: int) -> tuple[dict, tuple[int, int]]:
    if type(m) is not int or m not in range(4):
        raise ValueError("remainder must be 0, 1, 2 or 3")
    D = add(monomial(), scale(monomial(4), -1))
    ends = monomial(6, 6), monomial(3, 4), monomial(4, 2)
    numerators = []
    slope, intercept = 0, 1
    for words, boundaries in TABLES[m]:
        P = {}
        for j, word in enumerate(words.split()):
            values = [1 if s == "+" else -1 for s in word]
            head = {(p, 0): values[p - 3] for p in range(3, 7)}
            tail = {(p, 1): values[(m + p - 3) % 4] for p in range(-2, 2)}
            P = add(P, multiply(monomial(0, j), add(head, scale(tail, -1))))
            slope += sum(values)
            q, r = divmod(m - 5, 4)
            intercept += q * sum(values) + sum(values[:r])
        for j, word in enumerate(boundaries.split()):
            for p, s in enumerate(word, -2):
                if s != ".":
                    value = 1 if s == "+" else -1
                    P = add(P, scale(multiply(D, monomial(p, j)), value))
                    intercept += value
        numerators.append(P)
    residual = multiply(D, add(monomial(), *[scale(a, -1) for a in ends]))
    for i, P in enumerate(numerators):
        inverse = {(-a, -b): c for (a, b), c in P.items()}
        residual = add(residual,
                       multiply(P, add(monomial(), *[scale(a, -1)
                                                    for j, a in enumerate(ends) if i != j])),
                       multiply(multiply(monomial(4), ends[i]), inverse))
    return residual, (slope, intercept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("d", type=int, nargs="?")
    parser.add_argument("--family", type=int, metavar="D", help="proved b=2d+3 construction")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--nodes", type=int, default=100000)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        if args.prove:
            if args.b is not None or args.d is not None or args.family is not None:
                parser.error("--prove takes no parameters")
            if any(symbolic_residual(m) != ({}, (0, 0)) for m in range(4)):
                raise ArithmeticError("nonzero symbolic residual")
            for h in range(5):
                d = 2 * h + 1
                checked_witness(2 * d + 3, d, family_signs(d))
            print("PASS: four Laurent identities, four size identities, five base cases")
            return 0
        if args.family is not None:
            if args.b is not None or args.d is not None:
                parser.error("--family takes d alone")
            result = checked_witness(2 * args.family + 3, args.family, family_signs(args.family))
            result["status"] = "partition"
        else:
            if args.b is None or args.d is None:
                parser.error("give b and d, --family D, or --prove")
            result = search(args.b, args.d, args.nodes)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {k: v for k, v in result.items()
                  if k not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 3 if result["status"] == "node-limit" else 0


if __name__ == "__main__":
    raise SystemExit(main())
