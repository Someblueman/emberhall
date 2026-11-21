"""Optimal pairs on T(b+d,b,b-d) for even b and 1<=d<b."""
from __future__ import annotations

import argparse
import json

from next_family import positive_integer
from published_cases import check_pair, path_pair

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


def _even_spacing_signs(b: int, d: int) -> dict:
    """b,d even, 0<d<b: retain (b+d-1,b,b-d)."""
    signs = {(0, 0): 1}
    for p in range(1, b + d):
        signs[1, p] = (-1) ** p if p < d else -1 if p <= b else -(-1) ** p
    for p in range(1, b + 1):
        signs[2, p] = -(-1) ** p
    for p in range(1, b - d + 1):
        signs[3, p] = 1
    return signs


def even_middle_witness(b: int, d: int) -> dict:
    """An optimal pair on T(b+d,b,b-d) for every even b and 0<d<b."""
    positive_integer(b)
    positive_integer(d)
    if b % 2 or d >= b:
        raise ValueError("require even b and 1 <= d < b")
    lengths = (b + d, b, b - d)
    if d == b - 1:
        left, right = path_pair(lengths)
        omitted = [(3, 1)]
        method = "two halves of the diameter path"
    else:
        spacing = d if d % 2 == 0 else d + 1
        signs = _even_spacing_signs(b, spacing)
        left = sorted(v for v, sign in signs.items() if sign == 1)
        right = sorted(v for v, sign in signs.items() if sign == -1)
        omitted = [(1, b + d)] if d % 2 == 0 else [(3, b - d)]
        method = "even spacing signs" if d % 2 == 0 else "neighboring even spacing"
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != 3 * b // 2:
        raise ArithmeticError("even-middle construction failed its exact check")
    return {**result, "lengths": lengths, "left": left, "right": right,
            "b": b, "d": d, "method": method, "omitted": omitted}


def even_middle_residual() -> Poly:
    """D*Q in independent z,u,v, with u=z**b and v=z**d."""
    one, z, u, v = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    minus_z = _add(one, _scale(z, -1))
    plus_z = _add(one, z)
    D = _add(one, _scale(_mon(2), -1))
    ends = (_mon(-1, 1, 1), u, _mon(r=1, s=-1))
    p1 = _add(_mul(minus_z, _add(u, _scale(one, -1)), _add(z, v)),
              _scale(_mul(plus_z, _add(v, _scale(_mul(z, u), -1))), -1))
    p2 = _mul(z, _add(one, _scale(u, -1)), minus_z)
    p3 = _mul(z, _add(one, _scale(ends[2], -1)), plus_z)
    result = _mul(D, _add(one, *[_scale(a, -1) for a in ends]))
    for i, numerator in enumerate((p1, p2, p3)):
        star = {tuple(-a for a in powers): value for powers, value in numerator.items()}
        result = _add(result,
                      _mul(numerator, _add(one, *[_scale(a, -1) for j, a in enumerate(ends) if j != i])),
                      _mul(_mon(2), ends[i], star))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("d", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.b is not None or args.d is not None:
            parser.error("--prove does not take parameters")
        if even_middle_residual():
            raise ArithmeticError("nonzero three-variable symbolic residual")
        print("PASS: even-middle identity in independent z,u,v")
        return 0
    if args.b is None or args.d is None:
        parser.error("give even b and 1 <= d < b, or --prove")
    try:
        result = even_middle_witness(args.b, args.d)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
