"""Exact constructions and certificates for T(10t, 7t, 4t).

Standard library only. See NEXT_FAMILY.md for the symbolic argument.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json

from published_cases import check_pair

# a/b mean +/- the alternating word (-1)^p inside each block;
# +/- mean constant words. Boundary signs are listed separately.
TABLES = {
    0: (("aaaaaabb----aabbbbbb", "+++++------++------"),
        ("bbbbbbbbbbbbbb", "--------------"),
        ("aa++++aa", "++++++++")),
    1: (("ab++++ba++++ab++++ba", "-++++-++++++-++++-+"),
        ("ba----ab----ba", "+-----------+-"),
        ("ba----ba", "+-----++")),
}
# Odd t: h=(t-1)//2. Each word repeats inside its block. Index by h%4.
ODD_TABLES = {
    0: (('++-+ ++-+ ++++ ++++ ++++ ++++ --+- --+- ---- ---- ---- ---- ---+ ---+ ++++ ++++ ++++ ++++ +++- +++-', '+++++------++++++--'),
        ('--+- --+- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- -+-- -+--', '--------------'),
        ('++++ ++++ ++++ ++++ ++++ ++++ ++++ ++++', '++++++++')),
    1: (('+-++ -+-+ ---+ ---- ---- -+-- -+-- +-+- +-+- -+-+ -+-+ +-+- +-+- -+-- -+-- ---- ---- ---+ -+-+ +-++', '++------++------+++'),
        ('-+-- +-+- +++- ++++ ++++ +-++ --+- --+- +++- ++++ ++++ +-++ +-+- ---+', '--+++---+++-+-'),
        ('++-+ ++-+ -+-+ +-+- +-+- -+-+ ++-+ ++-+', '++--++++')),
    2: (('++-+ -+++ ++++ ++++ ++++ ++++ --+- +--- ---- ---- ---- ---- ---+ -+-- ++++ ++++ ++++ ++++ +++- +-++', '+++++------+-++++-+'),
        ('--+- +--- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- -+-- ---+', '------------+-'),
        ('++++ ++++ ++++ ++++ ++++ ++++ ++++ ++++', '++++++++')),
    3: (('+--+ +-+- +-++ +-++ +-++ +-++ --+- +-++ +-+- -+-+ -+-+ +-+- +++- --+- +++- +++- +++- +++- +-+- ++--', '-++++-+-++---------'),
        ('-++- -+-+ -+-- -+-- -+-- -+-- -+-+ -+-+ -+-- -+-- -+-- -+-- -+-+ ++--', '+-------------'),
        ('+++- -+-- -+-+ +-+- +-+- -+-+ -+-- +++-', '++--++-+')),
}
WEIGHTS = (1, 1, 0, -1, 1, 0, -1, -1, 2, -1, -1, 0, 1, -1, 0, 1, -1, -2)
Vertex = tuple[int, int]
Poly = dict[tuple[int, int], int]


def positive_integer(value: object) -> int:
    if type(value) is not int or value < 1:
        raise ValueError("t must be a positive integer")
    return value


def family_witness(t: int) -> dict:
    """Construct an optimal pair on T(10t,7t,4t), for every integer t>=2."""
    positive_integer(t)
    if t < 2:
        raise ValueError("this construction requires t >= 2")
    h = t // 2
    signs: dict[Vertex, int] = {(0, 0): 1}
    if t % 2 == 0:
        for arm, (blocks, boundaries) in enumerate(TABLES[h % 2], 1):
            for j, kind in enumerate(blocks):
                for p in range(1, h):
                    signs[arm, j * h + p] = (
                        (1 if kind == "+" else -1) if kind in "+-"
                        else (1 if kind == "a" else -1) * (-1) ** p)
            for j, sign in enumerate(boundaries, 1):
                signs[arm, j * h] = 1 if sign == "+" else -1
    else:
        for arm, (words, boundaries) in enumerate(ODD_TABLES[h % 4], 1):
            words = words.split()
            for j, word in enumerate(words):
                start = j * h + j // 2
                extra = j % 2 - int(arm == 1 and j == len(words) - 1)
                for p in range(1, h + extra):
                    signs[arm, start + p] = 1 if word[(p - 1) % 4] == "+" else -1
            for j, sign in enumerate(boundaries, 1):
                signs[arm, j * h + j // 2] = 1 if sign == "+" else -1
    left = sorted(v for v, sign in signs.items() if sign == 1)
    right = sorted(v for v, sign in signs.items() if sign == -1)
    lengths = (10 * t, 7 * t, 4 * t)
    result = check_pair(lengths, left, right)
    if not result["homometric"] or not result["meets_target"]:
        raise ArithmeticError("the signed template failed its distance check")
    omitted = [(1, 10 * t)] + ([(1, 10 * t - 1)] if t % 2 else [])
    return {**result, "lengths": lengths, "left": left, "right": right,
            "omitted": omitted, "construction": "next family",
            "t": t, "upper_bound": (21 * t) // 2, "attains_bound": True}


def add(*terms: Poly) -> Poly:
    out: defaultdict[tuple[int, int], int] = defaultdict(int)
    for term in terms:
        for power, coefficient in term.items():
            out[power] += coefficient
    return {power: c for power, c in out.items() if c}


def multiply(a: Poly, b: Poly) -> Poly:
    out: defaultdict[tuple[int, int], int] = defaultdict(int)
    for (i, j), c in a.items():
        for (k, ell), d in b.items():
            out[i + k, j + ell] += c * d
    return {power: c for power, c in out.items() if c}


def scale(p: Poly, c: int) -> Poly:
    return {power: c * v for power, v in p.items() if c * v}


def monomial(z: int = 0, r: int = 0) -> Poly:
    return {(z, r): 1}


def even_symbolic_residual(parity: int) -> tuple[Poly, tuple[int, int]]:
    """Return D*Q and the two coefficients of the affine size imbalance.

    z and r are independent Laurent indeterminates; r=z**h is substituted
    only after the zero identity is established. No finite t is used here.
    """
    if parity not in (0, 1):
        raise ValueError("parity must be 0 or 1")
    one, z, r = monomial(), monomial(1), monomial(0, 1)
    d = add(one, scale(monomial(2), -1))
    ends = [monomial(-1, 20), monomial(0, 14), monomial(0, 8)]
    epsilon = 1 if parity == 0 else -1
    numerators = []
    slope, intercept = 0, 1  # centre has sign +1
    for blocks, boundaries in TABLES[parity]:
        p: Poly = {}
        for j, kind in enumerate(blocks):
            if kind in "+-":
                sign = 1 if kind == "+" else -1
                term = multiply(add(z, scale(r, -1)), add(one, z))
                slope += sign
                intercept -= sign
            else:
                sign = 1 if kind == "a" else -1
                term = multiply(add(scale(z, -1), scale(r, -epsilon)),
                                add(one, scale(z, -1)))
                intercept += sign * (-1 if parity == 0 else 0)
            p = add(p, scale(multiply(monomial(0, j), term), sign))
        for j, symbol in enumerate(boundaries, 1):
            sign = 1 if symbol == "+" else -1
            p = add(p, scale(multiply(monomial(0, j), d), sign))
            intercept += sign
        numerators.append(p)
    residual = multiply(d, add(one, *[scale(a, -1) for a in ends]))
    for i, p in enumerate(numerators):
        factor = add(one, *[scale(a, -1) for j, a in enumerate(ends) if i != j])
        reflected = {(-a, -b): c for (a, b), c in p.items()}
        residual = add(residual, multiply(p, factor),
                       multiply(multiply(monomial(2), ends[i]), reflected))
    return residual, (slope, intercept)


def odd_symbolic_residual(remainder: int) -> tuple[Poly, tuple[int, int]]:
    """Return D*Q and the imbalance in q, with h=4q+remainder."""
    if remainder not in range(4):
        raise ValueError("remainder must be 0, 1, 2 or 3")
    one = monomial()
    d = add(one, scale(monomial(4), -1))
    ends = [monomial(8, 20), monomial(7, 14), monomial(4, 8)]
    numerators = []
    slope, intercept = 0, 1
    for arm, (words, boundaries) in enumerate(ODD_TABLES[remainder], 1):
        words = words.split()
        numerator: Poly = {}
        for j, word in enumerate(words):
            values = [1 if c == "+" else -1 for c in word]
            extra = j % 2 - int(arm == 1 and j == len(words) - 1)
            start = monomial(j // 2, j)
            first = {(p, 0): sign for p, sign in enumerate(values, 1)}
            tail = {(p, 0): values[(remainder + extra + p - 1) % 4] for p in range(4)}
            block = add(first, scale(multiply(monomial(extra, 1), tail), -1))
            numerator = add(numerator, multiply(start, block))
            slope += sum(values)
            n = remainder + extra - 1
            intercept += sum(values[:n]) if n >= 0 else -values[-1]
        for j, symbol in enumerate(boundaries, 1):
            sign = 1 if symbol == "+" else -1
            numerator = add(numerator, scale(multiply(monomial(j // 2, j), d), sign))
            intercept += sign
        numerators.append(numerator)
    residual = multiply(d, add(one, *[scale(a, -1) for a in ends]))
    for i, p in enumerate(numerators):
        factor = add(one, *[scale(a, -1) for j, a in enumerate(ends) if i != j])
        reflected = {(-a, -b): c for (a, b), c in p.items()}
        residual = add(residual, multiply(p, factor),
                       multiply(multiply(monomial(4), ends[i]), reflected))
    return residual, (slope, intercept)


def partition_certificate() -> dict[Vertex, int]:
    """Exact coefficient expansion of sum_j WEIGHTS[j] * [z**j] Q.

    The result is 2*(s0+s(1,3)+s(2,1)). Replacing each depth by t times
    that depth gives the identity at arbitrary scale, because Q's shifts
    and reflections preserve depth residues modulo t.
    """
    lengths = (10, 7, 4)
    result = {}
    for arm, depth in [(0, 0)] + [(i, p) for i, a in enumerate(lengths, 1)
                                          for p in range(1, a + 1)]:
        terms: defaultdict[int, int] = defaultdict(int)
        if arm == 0:
            terms[0] += 1
            for a in lengths:
                terms[a] -= 1
        else:
            terms[depth] += 1
            terms[lengths[arm - 1] - depth] -= 1
            for j, a in enumerate(lengths, 1):
                if arm != j:
                    terms[depth + a] -= 1
        coefficient = sum(WEIGHTS[p] * c for p, c in terms.items())
        if coefficient:
            result[arm, depth] = coefficient
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true", help="check all six exact symbolic identities")
    parser.add_argument("--summary", action="store_true", help="omit vertex lists and profiles")
    args = parser.parse_args()
    if args.prove:
        if args.t is not None:
            parser.error("--prove does not take t")
        for parity in (0, 1):
            residual, balance = even_symbolic_residual(parity)
            if residual or balance != (0, 0):
                raise ArithmeticError("nonzero symbolic residual")
        for remainder in range(4):
            residual, balance = odd_symbolic_residual(remainder)
            if residual or balance != (0, 0):
                raise ArithmeticError("nonzero odd symbolic residual")
        if partition_certificate() != {(0, 0): 2, (1, 3): 2, (2, 1): 2}:
            raise ArithmeticError("incorrect partition certificate")
        print("PASS: six Laurent identities, six size identities, full-partition certificate")
        return 0
    if args.t is None:
        parser.error("give t >= 2 or --prove")
    try:
        result = family_witness(args.t)
    except ValueError as error:
        parser.exit(2, f"{error}\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
