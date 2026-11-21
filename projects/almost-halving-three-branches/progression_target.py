"""Optimal pairs on T((q+1)d, qd, (q-1)d), q>=2, d>=1.

This settles the divisible subfamily, not every arithmetic progression.
"""
from __future__ import annotations

import argparse
import json

from next_family import positive_integer
from progression_partitions import multiple_pair
from published_cases import block_pair, check_pair

Poly = dict[tuple[int, int, int], int]


def _mon(z: int = 0, r: int = 0, s: int = 0) -> Poly:
    return {(z, r, s): 1}


def _add(*polynomials: Poly) -> Poly:
    result: Poly = {}
    for polynomial in polynomials:
        for powers, value in polynomial.items():
            result[powers] = result.get(powers, 0) + value
    return {powers: value for powers, value in result.items() if value}


def _scale(polynomial: Poly, value: int) -> Poly:
    return {powers: coefficient * value for powers, coefficient in polynomial.items()
            if coefficient * value}


def _mul(*polynomials: Poly) -> Poly:
    result = _mon()
    for polynomial in polynomials:
        product: Poly = {}
        for powers, value in result.items():
            for other, coefficient in polynomial.items():
                degree = tuple(a + b for a, b in zip(powers, other))
                product[degree] = product.get(degree, 0) + value * coefficient
        result = {powers: value for powers, value in product.items() if value}
    return result


def even_divisor_words(q: int, parity: int) -> list[tuple[list[str], str]]:
    """Interior words and boundary signs for odd q and h=d/2."""
    if type(q) is not int or q < 3 or q % 2 != 1 or parity not in (0, 1):
        raise ValueError("require odd q >= 3 and parity 0 or 1")
    n = 2 * q - 2
    if parity == 0:
        return [(["-+"] * 2 + ["--"] * n + ["+-"] * 2, "+" + "-" * (2 * q)),
                (["+-"] * (2 * q), "-" * (2 * q)),
                (["++"] * n, "+" * n)]
    middle = [word for j in range(q - 2)
              for word in (["++"] * 2 if j % 2 == 0 else ["--"] * 2)]
    boundaries = "".join("-" if ((j - 1) // 2) % 2 == 0 else "+"
                         for j in range(1, 2 * q + 2))
    return [(["-+", "--", "+-"] + middle + ["+-", "--", "-+"], boundaries),
            (["+-"] + ["++"] * n + ["-+"], "+-" * q),
            (["--"] * n, "-+" * (q - 1))]


def divisible_witness(q: int, d: int) -> dict:
    positive_integer(q)
    positive_integer(d)
    if q < 2:
        raise ValueError("q must be at least 2")
    lengths = ((q + 1) * d, q * d, (q - 1) * d)
    if q % 2 == 0:
        left, right = block_pair((lengths[0] - 1, lengths[1], lengths[2]), (1, 2, 3))
        method = "published odd block on a prefix subtree"
    elif d % 2:
        left, right = multiple_pair(q * d, d)
        method = "odd multiple full partition"
    else:
        h = d // 2
        signs = {(0, 0): 1}
        for arm, (words, boundaries) in enumerate(even_divisor_words(q, h % 2), 1):
            for j, word in enumerate(words):
                for p in range(1, h):
                    signs[arm, j * h + p] = 1 if word[(p - 1) % 2] == "+" else -1
            for j, sign in enumerate(boundaries, 1):
                signs[arm, j * h] = 1 if sign == "+" else -1
        left = sorted(v for v, sign in signs.items() if sign == 1)
        right = sorted(v for v, sign in signs.items() if sign == -1)
        method = "even divisor periodic partition"
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != (3 * q * d + 1) // 2:
        raise ArithmeticError("divisible-family construction failed its exact check")
    omitted = [] if q * d % 2 else [(1, lengths[0])]
    return {**result, "lengths": lengths, "left": left, "right": right,
            "q": q, "d": d, "method": method, "omitted": omitted}


def even_divisor_residual(parity: int) -> Poly:
    """Clear the full-shell identity in independent z,r,s (s=r**(2q-2))."""
    if parity not in (0, 1):
        raise ValueError("parity must be 0 or 1")
    one, z, r, s = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    r2, r4 = _mon(r=2), _mon(r=4)
    D = _add(one, _scale(_mon(2), -1))
    U = _mul(_add(z, _scale(r, -1)), _add(one, z))
    E = _mul(_add(_scale(z, -1), _scale(r, -1)) if parity == 0
             else _add(r, _scale(z, -1)), _add(one, _scale(z, -1)))
    gamma = _add(one, _scale(_mul(s, r2), -1))
    if parity == 0:
        H = _add(one, _scale(r, -1))
        y1 = _add(_mul(H, E, _add(one, r), gamma),
                  _scale(_mul(U, r2, _add(one, _scale(s, -1))), -1),
                  _mul(D, _add(_mul(H, r), _scale(_mul(r2, gamma), -1))))
        y2 = _scale(_mul(_add(E, _mul(D, r)), gamma), -1)
        y3 = _mul(_add(U, _mul(D, r)), _add(one, _scale(s, -1)))
        reflection_factor = _mon(2, 1)
    else:
        H = _add(one, _scale(r4, -1))
        plus = _add(one, r, r2, _mon(r=3))
        minus = _add(one, _scale(r, -1), r2, _scale(_mon(r=3), -1))
        f = _add(one, _scale(r2, -1))
        y1 = _add(_mul(H, _add(_mul(E, f, _add(one, _scale(_mul(s, r), -1))),
                              _scale(_mul(U, _add(r, _mul(s, r2))), -1))),
                  _mul(U, r, _add(one, r), _add(r2, s), f),
                  _mul(D, _add(_scale(_mul(r, _add(one, r), _add(one, _scale(s, -1)), f), -1),
                               _mul(s, _add(_scale(r, -1), _scale(r2, -1), _mon(r=3)), H))))
        y2 = _add(_mul(H, E, _add(_mul(s, r), _scale(one, -1))),
                  _mul(U, r, _add(one, _scale(s, -1)), plus), _mul(D, r, gamma, minus))
        y3 = _scale(_mul(_add(one, _scale(s, -1)), _add(_mul(U, plus), _mul(D, r, minus))), -1)
        reflection_factor = _mon(2, 4)
    ends = (_mon(-1, 4, 1), _mon(r=2, s=1), s)
    result = _mul(D, H, _add(one, *[_scale(a, -1) for a in ends]))
    for i, numerator in enumerate((y1, y2, y3)):
        star = {tuple(-a for a in powers): value for powers, value in numerator.items()}
        result = _add(result,
                      _mul(numerator, _add(one, *[_scale(a, -1) for j, a in enumerate(ends) if j != i])),
                      _scale(_mul(reflection_factor, ends[i], star), -1))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("q", type=int, nargs="?")
    parser.add_argument("d", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.q is not None or args.d is not None:
            parser.error("--prove does not take parameters")
        if even_divisor_residual(0) or even_divisor_residual(1):
            raise ArithmeticError("nonzero three-variable symbolic residual")
        print("PASS: both even-divisor identities in independent z,r,s")
        return 0
    if args.q is None or args.d is None:
        parser.error("give q>=2 and d>=1, or --prove")
    try:
        result = divisible_witness(args.q, args.d)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
