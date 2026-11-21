"""Exact odd-subdivision defect and obstructions to local recolouring repairs.

Includes a corrected alternating-edge lift on an explicit length class.
The universal tripod milestone remains open.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
import sys

from progression_partitions import classify
from progression_target import _add, _mon, _mul, _scale
from published_cases import check_pair, validate_lengths
from unequal_spacing import full_partition


def integer(value: int, name: str, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def odd_factor(value: int) -> None:
    integer(value, "factor", 3)
    if value % 2 == 0:
        raise ValueError("factor must be odd")


def symbolic_residuals(tips: tuple[int, int, int], centre: int) -> tuple[dict, dict]:
    """Coefficients of E and E* after subtracting 2sE(1-Ap)(1-Aq).

    The three independent monomial coordinates here mean A1,A2,A3.
    E=sum(z**j, j=1..h); C=1+E+E*. Base Q=0 was eliminated.
    """
    if (type(centre) is not int or centre not in (-1, 1) or len(tips) != 3
            or any(type(s) is not int or s not in (-1, 1) for s in tips)):
        raise ValueError("centre and tip signs must be +/-1")
    if sum(tips) != centre:
        raise ValueError("tip signs must sum to the centre sign")
    one = _mon()
    ends = (_mon(1), _mon(r=1), _mon(s=1))
    common = _add(one, *[_scale(a, -1) for a in ends])
    ecoef = _scale(common, -centre)
    starcoef = _scale(common, -centre)
    for i, (a, sign) in enumerate(zip(ends, tips)):
        ecoef = _add(ecoef, _mul(_add(_scale(one, centre), _scale(a, -sign)),
                               _add(one, *[_scale(b, -1) for j, b in enumerate(ends)
                                           if i != j])))
        starcoef = _add(starcoef, _scale(a, -centre), _scale(one, sign))
    majority = [a for a, sign in zip(ends, tips) if sign == centre]
    expected = _scale(_mul(*[_add(one, _scale(a, -1)) for a in majority]), 2*centre)
    return _add(ecoef, _scale(expected, -1)), starcoef


def stencil_word(factor: int, stencil: tuple[int, ...] | None) -> tuple[int, ...]:
    odd_factor(factor)
    if stencil is None:
        return (1,)*(factor//2)
    if len(stencil) != factor//2 or any(type(s) is not int or s not in (-1, 1) for s in stencil):
        raise ValueError("stencil must have exactly (factor-1)/2 signs, each +/-1")
    return stencil


def defect(lengths: tuple[int, int, int], factor: int,
           centre: int, tips: tuple[int, int, int],
           stencil: tuple[int, ...] | None = None) -> dict[int, int]:
    """Every coefficient of D=left-distance-polynomial minus right's."""
    lengths = validate_lengths(lengths)
    odd_factor(factor)
    symbolic_residuals(tips, centre)  # validate the sign domain
    a, b = [factor*n for n, sign in zip(lengths, tips) if sign == centre]
    word = stencil_word(factor, stencil)
    h = len(word)
    prefix = [0]
    for sign in word:
        prefix.append(prefix[-1]+sign)
    def ramp(d: int) -> int:
        return prefix[min(h, max(0, d-1))]
    return {d: value for d in range(2, a+b+h+1)
            if (value := centre*(ramp(d)-ramp(d-a)-ramp(d-b)+ramp(d-a-b)))}


def subdivision_lift(lengths: tuple[int, int, int], left: list, right: list,
                     factor: int, stencil: tuple[int, ...] | None = None) -> dict:
    """Apply one common symmetric sign stencil to every original vertex cell."""
    lengths = validate_lengths(lengths)
    odd_factor(factor)
    word = stencil_word(factor, stencil)
    base = check_pair(lengths, left, right)
    if not base["homometric"] or 2*base["size"] != 1+sum(lengths):
        raise ValueError("base must be a full equal homometric partition")
    signs = {tuple(v): 1 for v in left} | {tuple(v): -1 for v in right}
    centre = signs[0, 0]
    tips = tuple(signs[i, n] for i, n in enumerate(lengths, 1))
    if sum(tips) != centre:
        raise ArithmeticError("base violates the distance-one tip identity")
    lifted = {(0, 0): centre}
    for i, n in enumerate(lengths, 1):
        for p in range(1, factor*n+1):
            nearest = (p+factor//2)//factor
            offset = abs(p-factor*nearest)
            mask = word[offset-1] if offset else 1
            lifted[i, p] = mask*signs[(i, nearest) if nearest else (0, 0)]
    plus = [v for v, sign in lifted.items() if sign == 1]
    minus = [v for v, sign in lifted.items() if sign == -1]
    large = tuple(factor*n for n in lengths)
    checked = check_pair(large, plus, minus)
    predicted = defect(lengths, factor, centre, tips, word)
    if checked["difference"] != predicted or len(plus) != len(minus):
        raise ArithmeticError("subdivision disagrees with the exact defect identity")
    return {**checked, "lengths": large, "left": plus, "right": minus,
            "base_lengths": lengths, "factor": factor, "stencil": "".join("+" if s == 1 else "-" for s in word), "centre_sign": centre,
            "tip_signs": tips, "status": "diagnostic: not a homometric witness"}


def edge_filler_residual() -> dict:
    """D times the filler equation, with independent r=Z**d, B, C and A=rB."""
    one, r, b, c = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    a = _mul(r, b)
    plus = _add(one, r)
    n1 = _scale(_mul(_add(one, _scale(a, -1)), plus), -1)
    n2 = _mul(_add(one, _scale(b, -1)), plus)
    n3 = _scale(_mul(_add(one, _scale(r, -1)), _add(one, _scale(c, -1))), -1)
    return _add(_mul(n1, _add(_scale(one, 2), _scale(b, -1), _scale(c, -1))),
                _mul(n2, _add(_scale(one, 2), _scale(a, -1), _scale(c, -1))),
                _scale(_mul(n3, _add(a, b)), -1))


def corrected_lift(lengths: tuple[int, int, int], left: list, right: list,
                   factor: int, order: tuple[int, int, int]) -> dict:
    """Lift any full base in either of the two proved edge-recipe domains.

    Original vertex signs are kept; each edge's inserted word alternates.
    order uses zero-based arm indices: negative constant, positive constant,
    then alternating blocks of width d. Every check uses the original metric.
    """
    lengths = validate_lengths(lengths)
    odd_factor(factor)
    if tuple(sorted(order)) != (0, 1, 2):
        raise ValueError("order must permute the three zero-based arms")
    i, j, k = order
    d = lengths[i]-lengths[j]
    if d <= 0:
        raise ValueError("require L_i>L_j")
    if lengths[k] % (2*d) == 0:
        recipe = "constant arms, alternating blocks"
    elif d % 2 and lengths[j] % d == 0 and lengths[k] % 2 == 0:
        recipe = "odd periodic arms, alternating third arm"
    else:
        raise ValueError("no proved alternating-edge recipe for this arm order")
    base = check_pair(lengths, left, right)
    if not base["homometric"] or 2*base["size"] != 1+sum(lengths):
        raise ValueError("base must be a full equal homometric partition")
    signs = {tuple(v): 1 for v in left} | {tuple(v): -1 for v in right}
    lifted = {(0, 0): signs[0, 0]}
    for arm, n in enumerate(lengths):
        for edge in range(n):
            if recipe == "constant arms, alternating blocks":
                tau = -1 if arm == i else 1 if arm == j else (-1 if (edge//d) % 2 == 0 else 1)
            else:
                alternating = 1 if (edge % d) % 2 == 0 else -1
                tau = -alternating if arm == i else alternating if arm == j else (-1 if edge % 2 == 0 else 1)
            for r in range(1, factor):
                lifted[arm+1, factor*edge+r] = tau*(1 if r % 2 else -1)
            lifted[arm+1, factor*(edge+1)] = signs[arm+1, edge+1]
    plus = [v for v, sign in lifted.items() if sign == 1]
    minus = [v for v, sign in lifted.items() if sign == -1]
    large = tuple(factor*n for n in lengths)
    result = check_pair(large, plus, minus)
    if not result["homometric"] or 2*result["size"] != 1+sum(large):
        raise ArithmeticError("corrected lift failed the original-tree distance check")
    return {**result, "lengths": large, "base_lengths": lengths,
            "left": plus, "right": minus, "factor": factor, "block_width": d,
            "arm_order": order, "recipe": recipe, "construction": "corrected alternating-edge subdivision"}


def priority_lift(family: str, t: int) -> dict:
    """Construct the proved subfamilies, using an existing coarse partition."""
    integer(t, "t")
    if family == "five":
        coarse = (18+1064*t, 14+1064*t, 3+1064*t)
        factor, base_order = 5, (0, 2, 1)
        order = (0, 2, 1) if t % 15 in (3, 14) else (1, 2, 0) if t % 11 in (1, 6) else None
    elif family == "seven":
        coarse = (13+760*t, 10+760*t, 2+760*t)
        factor, base_order = 7, (0, 1, 2)
        order = (0, 1, 2) if t % 3 in (1, 2) else (0, 2, 1) if t % 11 in (1, 9) else None
    else:
        raise ValueError("family must be five or seven")
    if order is None:
        raise ValueError("parameter outside the proved corrected-lift subfamilies")
    base = full_partition(*(coarse[i] for i in base_order))
    remap = lambda vertices: [(base_order[i-1]+1, p) if i else (0, 0) for i, p in vertices]
    result = corrected_lift(coarse, remap(base["left"]), remap(base["right"]), factor, order)
    original = (91+5320*t, 71+5320*t, 15+5320*t)
    checked = check_pair(original, result["left"], result["right"])
    if not checked["meets_target"] or checked["size"] != 88+7980*t:
        raise ArithmeticError("priority lift failed in the original untrimmed tree")
    return {**result, **checked, "lengths": original, "retained_lengths": result["lengths"],
            "family": family, "t": t, "priority": "provisional", "universal_milestone": "open"}


def repair_certificate(lengths: tuple[int, int, int], factor: int,
                       tips: tuple[int, int, int], centre: int, radius: int) -> dict:
    """Support obstructions, conditional on a full homometric base with these tips.

    A failed inequality is inconclusive. Neither result excludes global repairs.
    """
    lengths = validate_lengths(lengths)
    odd_factor(factor)
    integer(radius, "radius")
    symbolic_residuals(tips, centre)
    ends = tuple(factor*n for n in lengths)
    k = sum(n for n, sign in zip(ends, tips) if sign == centre) + factor//2
    # A centre-ball change cannot affect any distance beyond max(ends)+radius.
    centre_limit = k-max(ends)-1
    # For a centre-and-tip change, (1-z) times its shell polynomial is
    # supported only near 0, Ni, and on [Ni+Nj-radius, Ni+Nj].
    critical = [k, *[abs(k-n) for n in ends]]
    critical += [a+b-k for a, b in combinations(ends, 2) if a+b >= k]
    boundary_limit = min(critical)-1
    return {"lengths": ends, "radius": radius, "centre_sign": centre,
            "tip_signs": tips, "extreme_distance": k, "defect_coefficient": -centre,
            "centre_ball_max_radius": centre_limit,
            "centre_ball_repair_impossible": radius <= centre_limit,
            "centre_and_tips_max_radius": boundary_limit,
            "centre_and_tips_repair_impossible": radius <= boundary_limit,
            "scope": "full recolourings; conditional on this full base and tip signs",
            "global_repair": "unresolved"}


def priority_certificates(family: str, t: int, radius: int) -> dict:
    """No base-existence assumption: report conditional bounds for all tip patterns."""
    integer(t, "t")
    integer(radius, "radius")
    if family not in ("five", "seven"):
        raise ValueError("family must be five or seven")
    offset, factor = ((90, 70, 15), 5) if family == "five" else ((91, 70, 14), 7)
    large = tuple(n+5320*t for n in offset)
    small = tuple(n//factor for n in large)
    cases = []
    for minority in range(3):
        tips = tuple(-1 if i == minority else 1 for i in range(3))
        cases.append(repair_certificate(small, factor, tips, 1, radius))
    return {"family": family, "t": t, "retained_lengths": large,
            "original_target": 88+7980*t, "radius": radius,
            "all_centre_ball_repairs_impossible": all(c["centre_ball_repair_impossible"] for c in cases),
            "all_centre_and_tips_repairs_impossible": all(c["centre_and_tips_repair_impossible"] for c in cases),
            "conditional_cases": cases, "base_existence": "not asserted",
            "universal_milestone": "open", "priority": "provisional"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--example", nargs=2, type=int, metavar=("B", "D"))
    mode.add_argument("--lift", metavar="JSON", help="full base partition; '-' reads stdin")
    mode.add_argument("--priority-lift", choices=("five", "seven"))
    mode.add_argument("--obstruction", choices=("five", "seven"))
    parser.add_argument("--factor", type=int)
    parser.add_argument("--stencil", help="symmetric cell mask, centre outward; e.g. +-, default all +")
    parser.add_argument("--t", type=int)
    parser.add_argument("--radius", type=int)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        if args.prove:
            if args.factor is not None or args.t is not None or args.radius is not None or args.stencil is not None:
                parser.error("--prove takes no parameters")
            for centre in (-1, 1):
                for minority in range(3):
                    tips = tuple(-centre if i == minority else centre for i in range(3))
                    if any(symbolic_residuals(tips, centre)):
                        raise ArithmeticError("nonzero symbolic residual")
            if edge_filler_residual():
                raise ArithmeticError("nonzero alternating-edge identity")
            print("PASS: six stencil patterns and the alternating-edge lift identity")
            return 0
        if args.priority_lift:
            if args.t is None or args.radius is not None or args.factor is not None or args.stencil is not None:
                parser.error("--priority-lift requires only --t")
            result = priority_lift(args.priority_lift, args.t)
        elif args.obstruction:
            if args.t is None or args.radius is None or args.factor is not None or args.stencil is not None:
                parser.error("--obstruction requires --t and --radius, and no --factor")
            result = priority_certificates(args.obstruction, args.t, args.radius)
        else:
            if args.factor is None or args.t is not None or args.radius is not None:
                parser.error("a lift requires --factor, and no --t or --radius")
            if args.example:
                base = classify(*args.example, include_witness=True)
                if not base["full_partition"]:
                    raise ValueError("example has no full partition")
            else:
                base = json.loads(sys.stdin.read() if args.lift == "-"
                                  else Path(args.lift).read_text())
            if not isinstance(base, dict):
                raise ValueError("base must be a JSON object")
            if args.stencil is not None and any(c not in "+-" for c in args.stencil):
                raise ValueError("stencil uses only + and -")
            word = tuple(1 if c == "+" else -1 for c in args.stencil) if args.stencil is not None else None
            result = subdivision_lift(base["lengths"], base["left"], base["right"], args.factor, word)
        if args.summary:
            if result.get("difference"):
                difference = result["difference"]
                result["defect_summary"] = {"nonzero_distances": len(difference),
                                           "first": min(difference), "last": max(difference),
                                           "distance_two": difference[2]}
            result = {k: v for k, v in result.items() if k not in
                      {"left", "right", "left_profile", "right_profile", "difference", "conditional_cases"}}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, str(error)+"\n")


if __name__ == "__main__":
    raise SystemExit(main())
