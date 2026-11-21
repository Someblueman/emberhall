"""Optimal pairs for T(7t,5t,3t); see ODD_MIDDLE.md."""
from __future__ import annotations

import argparse
import json

from next_family import add, monomial, multiply, positive_integer, scale
from progression_target import even_middle_witness
from published_cases import check_pair, separated_path_pair

# Index by h modulo four, where t=2h+1. Words start at interior offset 1.
TABLES = {
    0: (('++-+ ++-+ ++++ ++++ --+- --+- ---- ---- ---+ ---+ ++++ ++++ +++- +++-', '+++----++++--'),
        ('--+- --+- ---- ---- ---- ---- ---- ---- -+-- -+--', '----------'),
        ('++++ ++++ ++++ ++++ ++++ ++++', '++++++')),
    1: (('+--+ ++++ ++++ ++++ --++ ---- ---- ---- ---- ++-- ++++ ++++ ++++ +--+', '++++-----++++'),
        ('-++- ---- ---- ---- ---- ---- ---- ---- ---- --++', '----------'),
        ('++++ ++++ ++++ ++++ ++++ ++++', '+++++')),
    2: (('++-+ -+++ ++++ ++++ --+- +--- ---- ---- ---+ -+-- ++++ ++++ +++- +-++', '+++----+-++-+'),
        ('--+- +--- ---- ---- ---- ---- ---- ---- -+-- ---+', '--------+-'),
        ('++++ ++++ ++++ ++++ ++++ ++++', '++++++')),
    3: (('++-+ +++- ++++ ++++ ---+ +--- ---- ---- -+-- --+- ++++ ++++ ++-+ +++-', '-+++-----+++-'),
        ('--+- ---+ ---- ---- ---- ---- ---- ---- ---+ +---', '+---------'),
        ('++++ ++++ ++++ ++++ ++++ ++++', '+++++')),
}


def family_witness(t: int) -> dict:
    positive_integer(t)
    lengths = (7 * t, 5 * t, 3 * t)
    if t % 2 == 0:
        return {**even_middle_witness(5 * t, 2 * t), "t": t,
                "construction": "seven-five-three family"}
    if t == 1:
        left, right = separated_path_pair(lengths)
    else:
        h = t // 2
        m = h % 4
        signs = {(0, 0): 1}
        for arm, (words, boundaries) in enumerate(TABLES[m], 1):
            words = words.split()
            for j, word in enumerate(words):
                extra = j % 2 - int(m % 2 == 0 and arm == 1 and j == len(words) - 1)
                for p in range(1, h + extra):
                    signs[arm, j * h + j // 2 + p] = 1 if word[(p - 1) % 4] == "+" else -1
            for j, sign in enumerate(boundaries, 1):
                signs[arm, j * h + j // 2] = 1 if sign == "+" else -1
        left = sorted(v for v, s in signs.items() if s == 1)
        right = sorted(v for v, s in signs.items() if s == -1)
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != 15 * t // 2:
        raise ArithmeticError("odd-middle family failed its exact distance check")
    vertices = {(0, 0)} | {(i, p) for i, a in enumerate(lengths, 1) for p in range(1, a + 1)}
    return {**result, "lengths": lengths, "left": left, "right": right,
            "omitted": sorted(vertices - set(left) - set(right)), "t": t,
            "construction": "seven-five-three family"}


def symbolic_residual(m: int) -> tuple[dict, tuple[int, int]]:
    if m not in range(4):
        raise ValueError("remainder must be 0, 1, 2 or 3")
    D = add(monomial(), scale(monomial(4), -1))
    ends = (monomial(6 if m % 2 else 5, 14), monomial(5, 10),
            monomial(2 if m % 2 else 3, 6))
    numerators = []
    slope, intercept = 0, 1
    for arm, (words, boundaries) in enumerate(TABLES[m], 1):
        words = words.split()
        numerator = {}
        for j, word in enumerate(words):
            values = [1 if c == "+" else -1 for c in word]
            extra = j % 2 - int(m % 2 == 0 and arm == 1 and j == len(words) - 1)
            first = {(p, 0): v for p, v in enumerate(values, 1)}
            tail = {(p, 0): values[(m + extra + p - 1) % 4] for p in range(4)}
            block = add(first, scale(multiply(monomial(extra, 1), tail), -1))
            numerator = add(numerator, multiply(monomial(j // 2, j), block))
            slope += sum(values)
            n = m + extra - 1
            intercept += sum(values[:n]) if n >= 0 else -values[-1]
        for j, sign in enumerate(boundaries, 1):
            value = 1 if sign == "+" else -1
            numerator = add(numerator, scale(multiply(monomial(j // 2, j), D), value))
            intercept += value
        numerators.append(numerator)
    residual = multiply(D, add(monomial(), *[scale(a, -1) for a in ends]))
    for i, P in enumerate(numerators):
        inverse = {(-a, -b): c for (a, b), c in P.items()}
        residual = add(residual,
                       multiply(P, add(monomial(), *[scale(a, -1) for j, a in enumerate(ends) if i != j])),
                       multiply(multiply(monomial(4), ends[i]), inverse))
    return residual, (slope, intercept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.t is not None:
            parser.error("--prove does not take t")
        if any(symbolic_residual(m) != ({}, (0, 0)) for m in range(4)):
            raise ArithmeticError("nonzero symbolic residual")
        print("PASS: four odd-scale Laurent identities and four size identities")
        return 0
    if args.t is None:
        parser.error("give positive t or --prove")
    try:
        result = family_witness(args.t)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {k: v for k, v in result.items()
                  if k not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
