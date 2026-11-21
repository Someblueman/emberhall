"""Half-minus-one pairs for every odd middle arm and positive even spacing.

Standard library only. See NEXT_ODD_FAMILY.md for the all-parameter proof.
"""
from __future__ import annotations

import argparse
import json

from progression_target import _add, _mon, _mul, _scale
from published_cases import check_pair


def family_witness(b: int, d: int) -> dict:
    """Construct on T(b+d,b,b-d), for odd b and even 0<d<b."""
    if (type(b) is not int or type(d) is not int
            or b < 3 or b % 2 != 1 or d < 2 or d % 2 or d >= b):
        raise ValueError("require odd integer b >= 3 and even integer 0 < d < b")
    signs = {(0, 0): 1}
    for p in range(1, b + d + 1):
        if p <= d:
            sign = 1 if p % 2 else -1
        elif p <= b:
            sign = -1
        else:
            sign = 1 if (p - b) % 2 else -1
        signs[1, p] = sign
    for p in range(1, b):
        signs[2, p] = -1 if p % 2 else 1
    for p in range(1, b - d):
        signs[3, p] = 1
    left = sorted(v for v, sign in signs.items() if sign == 1)
    right = sorted(v for v, sign in signs.items() if sign == -1)
    lengths = (b + d, b, b - d)
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != (3 * b - 1) // 2:
        raise ArithmeticError("odd-middle/even-spacing construction failed")
    return {**result, "lengths": lengths, "left": left, "right": right,
            "b": b, "d": d, "omitted": [(2, b), (3, b - d)],
            "construction": "odd middle, even spacing"}


def symbolic_residual() -> dict:
    """D*Q in independent z,u,v; u=z**b, v=z**d only after checking."""
    one, z, u, v = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    minus, plus = _add(one, _scale(z, -1)), _add(one, z)
    denominator = _add(one, _scale(_mon(2), -1))
    ends = (_mon(r=1, s=1), _mon(-1, 1), _mon(-1, 1, -1))
    numerators = (
        _add(_mul(z, minus, _add(one, u), _add(one, _scale(v, -1))),
             _scale(_mul(z, plus, _add(v, _scale(u, -1))), -1)),
        _mul(_add(u, _scale(z, -1)), minus),
        _mul(_add(z, _scale(_mon(r=1, s=-1), -1)), plus),
    )
    residual = _mul(denominator, _add(one, *[_scale(a, -1) for a in ends]))
    for i, numerator in enumerate(numerators):
        reflected = {tuple(-x for x in powers): value
                     for powers, value in numerator.items()}
        residual = _add(
            residual,
            _mul(numerator, _add(one, *[_scale(a, -1) for j, a in enumerate(ends)
                                       if j != i])),
            _mul(_mon(2), ends[i], reflected),
        )
    return residual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("b", type=int, nargs="?")
    parser.add_argument("d", type=int, nargs="?")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.b is not None or args.d is not None:
            parser.error("--prove does not take b or d")
        if symbolic_residual():
            raise ArithmeticError("nonzero symbolic residual")
        print("PASS: exact Laurent identity in independent z, u, v")
        return 0
    if args.b is None or args.d is None:
        parser.error("give b and d, or --prove")
    try:
        result = family_witness(args.b, args.d)
    except ValueError as error:
        parser.exit(2, str(error) + "\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
