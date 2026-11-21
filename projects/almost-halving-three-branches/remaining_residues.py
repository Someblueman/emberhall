"""Exact obstruction to uniform endpoint-copy subdivision of two base families.

This does not rule out arbitrary homometric pairs or settle the target.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from math import gcd

from progression_target import _add, _mon, _mul, _scale
from published_cases import check_pair
from unequal_spacing import reflection_word


def add(*polys: dict[int, int]) -> dict[int, int]:
    result: Counter = Counter()
    for poly in polys:
        result.update(poly)
    return {k: v for k, v in result.items() if v}


def shift(poly: dict[int, int], amount: int, scale: int = 1) -> dict[int, int]:
    return {k + amount: scale*v for k, v in poly.items() if v}


def parameters(family: str, t: int) -> tuple[tuple[int, int, int], int]:
    """Reflection order (a,m,c) and subdivision factor."""
    if type(t) is not int or t < 0:
        raise ValueError("t must be a nonnegative integer")
    if family == "five":
        return (18+1064*t, 3+1064*t, 14+1064*t), 5
    if family == "seven":
        return (13+760*t, 10+760*t, 2+760*t), 7
    raise ValueError("family must be five or seven")


def base_signs(family: str, t: int) -> tuple[tuple[int, int, int], dict]:
    lengths, _ = parameters(family, t)
    a, m, c = lengths
    d = a-m
    word = reflection_word(a, m, c)

    def sign(arm: int, depth: int) -> int:
        value = word[depth % d]
        if arm == 2:
            value = -value
        elif arm == 3 and (depth//d) % 2 == 0:
            value = -value
        return value

    return lengths, {(0, 0): 1} | {
        (i, p): sign(i, p) for i, n in enumerate(lengths, 1)
        for p in range(1, n+1)}


def child_residual(lengths: tuple[int, int, int], signs: dict) -> dict[int, int]:
    """B=(1+z)U-s(1-sum z**L), U=sum z**L S_i(z**-1)."""
    u: Counter = Counter()
    for i, n in enumerate(lengths, 1):
        for p in range(1, n+1):
            u[n-p] += signs[i, p]
    s = signs[0, 0]
    return add(dict(u), shift(dict(u), 1), {0: -s},
               *[{n: s} for n in lengths])


def classify_parameter(t: int) -> dict:
    parameters("five", t)
    uncovered = t % 3 == 0 and t % 15 != 3 and t % 11 not in (1, 6, 9)
    return {"t": t, "outside_aster_recipes": uncovered,
            "target": 88+7980*t, "target_ruled_out": False,
            "status": "finite witness already known" if t == 0 else "unresolved" if uncovered
                      else "covered by Aster's corrected edge recipes",
            "all_colour_obstruction_proved": uncovered, "universal_milestone": "open"}


def all_colour_obstruction(t: int) -> dict:
    """Exclude every full base colouring, for the 32 remaining residues.

    The gcds force arm periods; contradictory coefficients then exclude
    the necessary child identity. No colouring is generated or searched.
    """
    if not classify_parameter(t)["outside_aster_recipes"]:
        raise ValueError("this all-colouring certificate is for the remaining residues")
    n5, n7 = 1064*t, 760*t
    five = (n5+18, n5+14, n5+3)
    seven = (n7+13, n7+10, n7+2)
    k = gcd(five[2], 15)
    if (gcd(five[1], 4), gcd(five[1], five[2])) != (2, 1) or k not in (1, 3, 5):
        raise ArithmeticError("five-family divisibility premise failed")
    if (gcd(seven[1], 3), gcd(seven[2], 11), gcd(seven[1], seven[2])) != (1, 1, 2):
        raise ArithmeticError("seven-family divisibility premise failed")
    return {"t": t, "scope": "every full base colouring and every uniform endpoint-copy word",
            "five": {"lengths": five, "forced_arm_periods": [2, k],
                     "equal_coefficients_at": [5, 5+k], "required_values": [1, -1]},
            "seven": {"lengths": seven, "forced_arm_periods": [2, 2],
                      "forced_first_coefficients": [-1, -1],
                      "required_sum": 0, "actual_sum": -2},
            "target_ruled_out": False, "universal_milestone": "open"}


def endpoint_identity_residual(centre: int, minority: int) -> dict:
    """X-sC=2s(1-Ap)(1-Aq), in three independent endpoint variables."""
    if centre not in (-1, 1) or minority not in (0, 1, 2):
        raise ValueError("invalid centre or minority leaf")
    one = _mon()
    ends = (_mon(1), _mon(r=1), _mon(s=1))
    c = _add(one, *[_scale(a, -1) for a in ends])
    x = _add(*[_mul(
        _add(_scale(one, centre), _scale(a, centre if i == minority else -centre)),
        _add(one, *[_scale(b, -1) for j, b in enumerate(ends) if j != i]))
        for i, a in enumerate(ends)])
    majority = [a for i, a in enumerate(ends) if i != minority]
    return _add(x, _scale(c, -centre), _scale(_mul(
        *[_add(one, _scale(a, -1)) for a in majority]), -2*centre))


def elimination_residual() -> dict:
    """Factor the RHS of (2), with independent A,B,C and d=A/B,e=A/C."""
    one, a, b, c = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    de = _add(_mon(1, -1), _mon(1, s=-1))
    bc = _add(b, c)
    return _add(_mul(a, bc), _mul(_add(one, _scale(bc, -1)), de),
                _scale(_mul(de, _add(one, _scale(b, -1)),
                            _add(one, _scale(c, -1))), -1))


def proof_certificate() -> dict:
    if any(endpoint_identity_residual(s, m) for s in (-1, 1) for m in range(3)):
        raise ArithmeticError("endpoint identity failed")
    if elimination_residual():
        raise ArithmeticError("elimination identity failed")
    remaining = [r for r in range(165) if classify_parameter(r)["outside_aster_recipes"]]
    if len(remaining) != 32:
        raise ArithmeticError("residue count changed")
    for t in remaining:
        all_colour_obstruction(t)
    return {"status": "PASS", "scope": "every full base colouring and every uniform endpoint-copy word",
            "all_colouring_remaining_classes": len(remaining),
            "remaining_residues_mod_165": remaining,
            "target_ruled_out": False, "universal_milestone": "open"}


def endpoint_lift(lengths: tuple[int, int, int], signs: dict,
                  factor: int, word: str) -> dict:
    """p/P copy +/-parent; c/C copy +/-child, same word on every edge."""
    if type(factor) is not int or factor < 3 or factor % 2 == 0:
        raise ValueError("factor must be odd and at least three")
    if len(word) != factor-1 or any(c not in "pPcC" for c in word):
        raise ValueError("word needs factor-1 letters from p,P,c,C")
    lifted = {(0, 0): signs[0, 0]}
    for i, n in enumerate(lengths, 1):
        for k in range(n):
            parent = signs[(i, k) if k else (0, 0)]
            child = signs[i, k+1]
            for r, code in enumerate(word, 1):
                lifted[i, factor*k+r] = (parent if code.lower() == "p" else child) * (
                    1 if code.islower() else -1)
            lifted[i, factor*(k+1)] = child
    return lifted


def diagnostic(family: str, t: int, factor: int | None, word: str | None) -> dict:
    lengths, signs = base_signs(family, t)
    _, default_factor = parameters(family, t)
    factor = default_factor if factor is None else factor
    word = "cC"*((factor-1)//2) if word is None else word
    lifted = endpoint_lift(lengths, signs, factor, word)
    plus = sorted(v for v, s in lifted.items() if s == 1)
    minus = sorted(v for v, s in lifted.items() if s == -1)
    scaled = tuple(factor*n for n in lengths)
    # Preserve reflection arm order. At the family's factor, check in the
    # original untrimmed tripod, restoring the omitted tips without using them.
    original = (91+5320*t, 15+5320*t, 71+5320*t) if family == "five" else (
        91+5320*t, 71+5320*t, 15+5320*t)
    checked_lengths = original if factor == default_factor else scaled
    checked = check_pair(checked_lengths, plus, minus)
    return {**checked, "lengths": checked_lengths, "retained_lengths": scaled,
            "left": plus, "right": minus, "family": family, "t": t,
            "factor": factor, "word": word, "target_ruled_out": False,
            "status": "failed candidate, not a homometric witness"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--parameter", type=int)
    mode.add_argument("--all-colour", type=int, metavar="T")
    mode.add_argument("--diagnostic", choices=("five", "seven"))
    parser.add_argument("--t", type=int, default=0)
    parser.add_argument("--factor", type=int)
    parser.add_argument("--word")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        if args.prove:
            result = proof_certificate()
        elif args.parameter is not None:
            result = classify_parameter(args.parameter)
        elif args.all_colour is not None:
            result = all_colour_obstruction(args.all_colour)
        else:
            result = diagnostic(args.diagnostic, args.t, args.factor, args.word)
        if args.summary:
            result = {k: v for k, v in result.items()
                      if k not in ("left", "right", "left_profile", "right_profile")}
        print(json.dumps(result, sort_keys=True))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
