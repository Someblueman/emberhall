"""Classify full homometric partitions of T(b+d,b,b-d)."""
from __future__ import annotations

import argparse
import json
from math import gcd

from next_family import add, monomial, multiply, positive_integer, scale
from published_cases import block_pair, check_pair


def validate(b: int, d: int) -> None:
    positive_integer(b)
    positive_integer(d)
    if d >= b:
        raise ValueError("require 1 <= d < b")


def multiple_pair(b: int, d: int) -> tuple[list, list]:
    """Full partition when b is odd and d divides b."""
    validate(b, d)
    if b % 2 == 0 or b % d:
        raise ValueError("require odd b divisible by d")
    signs = {(0, 0): 1}
    for p in range(1, b + d + 1):
        signs[1, p] = (-1) ** p
    for arm, length in ((2, b), (3, b - d)):
        for p in range(1, length + 1):
            within = (p - 1) % d + 1
            signs[arm, p] = (-1) ** within * (1 if arm == 2 else -1)
    return ([v for v, s in signs.items() if s == 1],
            [v for v, s in signs.items() if s == -1])


def residue_count(b: int, d: int, residue: int) -> int:
    """Count original vertices at depths congruent to residue modulo d."""
    quotient, remainder = divmod(b, d)
    if residue == 0:
        return 3 * quotient + 1
    return 3 * quotient + 3 * int(residue <= remainder)


def classify(b: int, d: int, *, include_witness: bool = False) -> dict:
    validate(b, d)
    n = 3 * b + 1
    result = {"lengths": (b + d, b, b - d), "order": n,
              "target": n // 2 - 1, "upper_bound": n // 2,
              "target_ruled_out": False}
    if b % 2 == 0:
        return {**result, "full_partition": False, "reason": "odd vertex count"}
    if b % d == 0:
        reason = "odd multiple construction"
        pair = multiple_pair(b, d) if include_witness else None
    elif (b + 1) % (2 * d) == 0:
        reason = "published odd-quotient block construction"
        pair = block_pair((b + d, b, b - d), (1, 2, 3)) if include_witness else None
    else:
        q, r = divmod(b, d)
        g = gcd(b, d)
        if g > 1:
            residues = (1, d - g + 1)
            certificate = {"kind": "unequal parity in one residue class", "gcd": g,
                           "residues": residues,
                           "vertex_counts": [residue_count(b, d, j) for j in residues]}
        elif r < d - 1:
            residues = (0, r + 1)
            certificate = {"kind": "unequal parity in one residue class", "gcd": g,
                           "residues": residues,
                           "vertex_counts": [residue_count(b, d, j) for j in residues]}
        else:
            # r=d-1, gcd=1; failure of the block condition means q is even.
            certificate = {"kind": "zero residue sum would have odd size", "gcd": 1,
                           "residue": 0, "vertex_count": 3 * q + 1}
        return {**result, "full_partition": False, "reason": "root-of-unity obstruction",
                "upper_bound": n // 2 - 1, "certificate": certificate}
    result.update(full_partition=True, reason=reason, maximum=n // 2)
    if pair is not None:
        left, right = pair
        checked = check_pair(result["lengths"], left, right)
        if not checked["homometric"] or checked["size"] != n // 2:
            raise ArithmeticError("full-partition construction failed its exact check")
        result.update(left=left, right=right, left_profile=checked["left_profile"],
                      right_profile=checked["right_profile"])
    return result


def root_elimination_residuals() -> tuple[dict, dict, dict]:
    """Check (y-2)Q + y*(y Q*) = -2(y-1)^2(s0+S)."""
    one, y = monomial(), monomial(1)
    ym2 = add(y, scale(one, -2))
    correction = scale(multiply(add(y, scale(one, -1)),
                                add(y, scale(one, -1))), 2)
    return (
        add(multiply(ym2, add(one, scale(y, -3))),
            multiply(y, add(y, scale(one, -3))), correction),
        add(multiply(ym2, add(one, scale(y, -2))), scale(y, -1), correction),
        add(multiply(ym2, scale(y, -1)), multiply(y, ym2)),
    )


def multiple_construction_residuals() -> tuple[dict, dict]:
    """Two Laurent identities in independent r,x; x=r**(q-1)."""
    one, r, x = monomial(), monomial(1), monomial(0, 1)
    ends = (multiply(monomial(2), x), multiply(r, x), x)
    n1 = scale(multiply(add(one, scale(r, -1)), add(one, scale(ends[0], -1))), -1)
    n2 = scale(multiply(add(one, r), add(one, scale(ends[1], -1))), -1)
    n3 = multiply(add(one, r), add(one, scale(x, -1)))
    base = multiply(add(one, scale(r, -1)), add(one, *[scale(a, -1) for a in ends]))
    constant, linear = base, base
    for i, p in enumerate((n1, n2, n3)):
        reflected = {(-a, -b): c for (a, b), c in p.items()}
        constant = add(constant, multiply(multiply(r, ends[i]), reflected))
        linear = add(linear, multiply(p, add(one, *[scale(a, -1)
                                                   for j, a in enumerate(ends) if i != j])))
    return constant, linear


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("d", type=int, nargs="?")
    parser.add_argument("--witness", action="store_true", help="emit a full pair when one exists")
    parser.add_argument("--prove", action="store_true", help="check exact algebraic identities")
    args = parser.parse_args()
    if args.prove:
        if args.b is not None or args.d is not None:
            parser.error("--prove does not take lengths")
        if any(root_elimination_residuals()) or any(multiple_construction_residuals()):
            raise ArithmeticError("nonzero symbolic identity")
        print("PASS: root elimination and odd-multiple construction identities")
        return 0
    if args.b is None or args.d is None:
        parser.error("give b and d, or --prove")
    try:
        result = classify(args.b, args.d, include_witness=args.witness)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
