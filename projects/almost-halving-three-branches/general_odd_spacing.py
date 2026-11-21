"""Periodic homometric pairs with even short arm c and middle 2c-1+4t."""
from __future__ import annotations

import argparse
import json

from progression_target import _add, _mon, _mul, _scale
from published_cases import check_pair


def periodic_witness(c: int, t: int) -> dict:
    """Meet half-minus-one on T(3c-2+8t,2c-1+4t,c), even c>=4, t>=0."""
    if type(c) is not int or c < 4 or c % 2:
        raise ValueError("short arm c must be an even integer >= 4")
    if type(t) is not int or t < 0:
        raise ValueError("step count t must be a nonnegative integer")
    b = 2*c-1+4*t
    k, phase = divmod(t, 2)
    if phase == 0:
        words = (
            "-"*c + "++++----"*k + "-"*(c-3) + "----++++"*k + "-"*(c+1),
            "+"*c + "----++++"*k + "+"*(c-3),
            "+"*c,
        )
    else:
        words = (
            "-"*(c+1) + "+-++-+--"*k + "+-"*((c+2)//2) + "+"
            + "--+-++-+"*k + "-"*(c+2),
            "+"*(c+1) + "-+--+-++"*k + "+"*c,
            "-+"*(c//2),
        )
    left, right = [(0, 0)], []
    for arm, word in enumerate(words, 1):
        for depth, sign in enumerate(word, 1):
            (left if sign == "+" else right).append((arm, depth))
    lengths = (2*b-c, b, c)
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != (3*b-1)//2:
        raise ArithmeticError("periodic odd-spacing construction failed")
    return {**result, "lengths": lengths, "left": left, "right": right,
            "b": b, "d": b-c, "short_arm": c, "steps": t, "repetitions": k, "phase": phase,
            "omitted": [(2, b-1), (2, b)],
            "construction": "periodic odd spacing"}


def symbolic_residual(phase: int) -> dict:
    """D*Q in independent z,u,v, where D=1-z**8, u=z**(8k), v=z**c."""
    one, z, u, v = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    denominator = _add(one, _scale(_mon(8), -1))
    geometric = _add(*[_mon(j) for j in range(8)])
    c_arm = _mul(geometric, _add(z, _scale(_mon(1, s=1), -1)))
    c_minus_three = _mul(geometric, _add(z, _scale(_mon(-2, s=1), -1)))
    c_plus_one = _mul(geometric, _add(z, _scale(_mon(2, s=1), -1)))
    repeated = _mul(
        _add(*[_mon(j) for j in range(1, 5)],
             *[_scale(_mon(j), -1) for j in range(5, 9)]),
        _add(one, _scale(u, -1)),
    )
    if phase not in (0, 1):
        raise ValueError("phase must be 0 or 1")
    numerators = (
        _add(_scale(c_arm, -1), _mul(v, repeated),
             _scale(_mul(v, u, c_minus_three), -1),
             _scale(_mul(_mon(-3, 1, 2), repeated), -1),
             _scale(_mul(_mon(-3, 2, 2), c_plus_one), -1)),
        _add(c_arm, _scale(_mul(v, repeated), -1), _mul(v, u, c_minus_three)),
        c_arm,
    )
    ends = (_mon(-2, 2, 3), _mon(-3, 1, 2), v)
    if phase == 1:
        alternating = _add(*[_scale(_mon(j), (-1)**j) for j in range(8)])
        def repeated_word(word: str) -> dict:
            polynomial = _add(*[_scale(_mon(j), 1 if sign == "+" else -1)
                                for j, sign in enumerate(word, 1)])
            return _mul(polynomial, _add(one, _scale(u, -1)))
        central = _mul(alternating, _add(z, _mon(4, s=1)))
        c_plus_two = _mul(geometric, _add(z, _scale(_mon(3, s=1), -1)))
        numerators = (
            _add(_scale(c_plus_one, -1), _mul(_mon(1, s=1), repeated_word("+-++-+--")),
                 _mul(_mon(1, 1, 1), central),
                 _mul(_mon(4, 1, 2), repeated_word("--+-++-+")),
                 _scale(_mul(_mon(4, 2, 2), c_plus_two), -1)),
            _add(c_plus_one, _mul(_mon(1, s=1), repeated_word("-+--+-++")),
                 _mul(_mon(1, 1, 1), c_arm)),
            _mul(alternating, _add(_scale(z, -1), _mon(1, s=1))),
        )
        ends = (_mon(6, 2, 3), _mon(1, 1, 2), v)
    residual = _mul(denominator, _add(one, *[_scale(a, -1) for a in ends]))
    for i, numerator in enumerate(numerators):
        reflected = {tuple(-x for x in powers): coefficient
                     for powers, coefficient in numerator.items()}
        residual = _add(
            residual,
            _mul(numerator, _add(one, *[_scale(a, -1)
                                       for j, a in enumerate(ends) if j != i])),
            _mul(_mon(8), ends[i], reflected),
        )
    return residual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("c", type=int, nargs="?", help="even short-arm length, at least 4")
    parser.add_argument("t", type=int, nargs="?", help="nonnegative t, giving middle length 2c-1+4t")
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.c is not None or args.t is not None:
            parser.error("--prove does not take c or t")
        if any(symbolic_residual(phase) for phase in (0, 1)):
            raise ArithmeticError("nonzero symbolic residual")
        print("PASS: both periodic odd-spacing identities in independent z,u,v")
        return 0
    if args.c is None or args.t is None:
        parser.error("give both c and t, or --prove")
    try:
        result = periodic_witness(args.c, args.t)
    except ValueError as error:
        parser.exit(2, str(error)+"\n")
    if args.summary:
        result = {key: value for key, value in result.items()
                  if key not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
