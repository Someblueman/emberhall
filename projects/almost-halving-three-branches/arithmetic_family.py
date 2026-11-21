"""Optimal homometric pairs on T(11t,8t,5t), using only the standard library."""
from __future__ import annotations

import argparse
import json

from next_family import add, monomial, multiply, positive_integer, scale
from published_cases import check_pair


# Repeated two-sign interior words, then the signs at block boundaries.
TABLES = {
    0: (("-+ -+ ++ +- +- -- -+ -+ ++ +- +-", "++---+++--"),
        ("+- +- -- +- +- -- +- +-", "--------"),
        ("-+ -+ ++ -+ -+", "+++++")),
    1: (("++ -+ -- +- ++ ++ ++ +- -- -+ ++", "+--+++--++"),
        ("-- +- ++ -- -- ++ -+ --", "-+---+--"),
        ("-+ +- -- -+ +-", "-++-+")),
}


def family_witness(t: int) -> dict:
    positive_integer(t)
    signs = {(0, 0): 1}
    for arm, (words, boundaries) in enumerate(TABLES[t % 2], 1):
        for j, word in enumerate(words.split()):
            for p in range(1, t):
                signs[arm, j * t + p] = 1 if word[(p - 1) % 2] == "+" else -1
        for j, sign in enumerate(boundaries, 1):
            signs[arm, j * t] = 1 if sign == "+" else -1
    lengths = (11 * t, 8 * t, 5 * t)
    left = sorted(v for v, s in signs.items() if s == 1)
    right = sorted(v for v, s in signs.items() if s == -1)
    result = check_pair(lengths, left, right)
    if not result["homometric"] or len(left) != 12 * t:
        raise ArithmeticError("the arithmetic-family template failed its exact check")
    return {**result, "lengths": lengths, "left": left, "right": right,
            "omitted": [(1, 11 * t)], "t": t,
            "construction": "arithmetic next family"}


def symbolic_residual(parity: int) -> tuple[dict, tuple[int, int]]:
    """Exact D*Q and size imbalance for t=2q+parity, r=z**t."""
    if parity not in (0, 1):
        raise ValueError("parity must be zero or one")
    d = add(monomial(), scale(monomial(2), -1))
    ends = (monomial(-1, 11), monomial(0, 8), monomial(0, 5))
    numerators = []
    slope, intercept = 0, 1
    for words, boundaries in TABLES[parity]:
        numerator = {}
        for j, word in enumerate(words.split()):
            values = [1 if c == "+" else -1 for c in word]
            first = {(p, 0): s for p, s in enumerate(values, 1)}
            tail = {(p, 0): values[(parity + p - 1) % 2] for p in range(2)}
            block = add(first, scale(multiply(monomial(0, 1), tail), -1))
            numerator = add(numerator, multiply(monomial(0, j), block))
            slope += sum(values)
            if parity == 0:
                intercept -= values[-1]
        for j, sign in enumerate(boundaries, 1):
            value = 1 if sign == "+" else -1
            numerator = add(numerator, scale(multiply(monomial(0, j), d), value))
            intercept += value
        numerators.append(numerator)
    residual = multiply(d, add(monomial(), *[scale(a, -1) for a in ends]))
    for i, p in enumerate(numerators):
        factor = add(monomial(), *[scale(a, -1) for j, a in enumerate(ends) if i != j])
        reflected = {(-a, -b): c for (a, b), c in p.items()}
        residual = add(residual, multiply(p, factor),
                       multiply(multiply(monomial(2), ends[i]), reflected))
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
        for parity in (0, 1):
            if symbolic_residual(parity) != ({}, (0, 0)):
                raise ArithmeticError("nonzero symbolic residual")
        print("PASS: both Laurent identities and both size identities")
        return 0
    if args.t is None:
        parser.error("give positive t or --prove")
    try:
        result = family_witness(args.t)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
