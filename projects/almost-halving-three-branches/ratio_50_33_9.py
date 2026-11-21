"""Exact tripod families and arbitrary-hole terminal reconstruction.

See RATIO_50_33_9.md. Every T(50t,33t,9t), t>0, is constructed exactly.
The universal target over arbitrary triples remains open.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from published_cases import check_pair, validate_lengths, validate_vertices


def _parameter(t: int) -> int:
    if type(t) is not int or t < 1:
        raise ValueError("t must be a positive integer")
    return t


def family_bound(t: int) -> dict:
    """Uniform analytic bound, without allocating a tree or claiming existence."""
    t = _parameter(t)
    return {"t": t, "lengths": [50*t, 33*t, 9*t], "target": 46*t-1,
            "maximum_omissions": 3, "minimum_reconstructed_tip_levels": 24*t-3,
            "scope": "every target-or-larger homometric pair, with arbitrary omissions",
            "existence_proved_here": True, "all_tripods_proved": False}


def reconstruct_tail(long_signs: list[int], long_holes: list[int],
                     middle_holes: list[int]) -> list[int]:
    """Solve S+Q=(1-z)(S*H_middle+Q*H_long) below the given cutoff.

    Depths are offsets from retained tips, so holes must have positive offsets.
    This algebraic operation also accepts integer words that are not signs.
    """
    cutoff = len(long_signs)
    for holes in (long_holes, middle_holes):
        if (len(holes) != len(set(holes))
                or any(type(h) is not int or not 1 <= h < cutoff for h in holes)):
            raise ValueError("holes must be distinct positive offsets below the cutoff")
    if any(type(s) is not int for s in long_signs):
        raise ValueError("the long word must contain integers")
    result = []
    for k, sign in enumerate(long_signs):
        value = -sign
        for h in middle_holes:
            if k >= h:
                value += long_signs[k-h]
            if k > h:
                value -= long_signs[k-h-1]
        for h in long_holes:
            if k >= h:
                value += result[k-h]
            if k > h:
                value -= result[k-h-1]
        result.append(value)
    return result


def terminal_certificate(lengths: object, left: object, right: object) -> dict:
    """Necessary high-distance equations for a literal pair; not a full check."""
    lengths = validate_lengths(lengths)
    left = validate_vertices(lengths, left)
    right = validate_vertices(lengths, right)
    if set(left) & set(right):
        raise ValueError("the two sets overlap")
    if len(left) != len(right):
        raise ValueError("the two sets have different sizes")
    signs = dict.fromkeys(left, 1) | dict.fromkeys(right, -1)
    tips = [max((d for (i, d) in signs if i == arm), default=0)
            for arm in range(1, 4)]
    if any(tip == 0 for tip in tips):
        raise ValueError("each arm must have a retained vertex")
    arms = sorted(range(1, 4), key=lambda i: (-tips[i-1], i))
    a, b, c = (tips[i-1] for i in arms)
    cutoff = b-c
    if cutoff <= 0:
        raise ValueError("the second retained arm must exceed the third")
    long_word = [signs.get((arms[0], a-k), 0) for k in range(cutoff)]
    middle_word = [signs.get((arms[1], b-k), 0) for k in range(cutoff)]
    long_holes = [k for k, sign in enumerate(long_word) if not sign]
    middle_holes = [k for k, sign in enumerate(middle_word) if not sign]
    predicted = reconstruct_tail(long_word, long_holes, middle_holes)
    failures = [k for k, (actual, forced) in enumerate(zip(middle_word, predicted))
                if actual != forced]
    return {"arms_long_middle_short": arms, "retained_tips": [a, b, c],
            "cutoff": cutoff, "long_holes": long_holes, "middle_holes": middle_holes,
            "predicted_middle_signs": predicted, "failure_offsets": failures,
            "necessary_condition_passes": not failures,
            "sufficient_for_homometry": False}


def parameter_witness(p: int, q: int, *, layers: int = 1, bands: int = 1) -> dict:
    """Construct the block family, using r=2*bands*p+q."""
    if type(p) is not int or p < 1 or type(q) is not int or q < 0:
        raise ValueError("p must be positive and q must be nonnegative integers")
    if type(layers) is not int or layers < 0:
        raise ValueError("layers must be a nonnegative integer")
    if type(bands) is not int or bands < 1:
        raise ValueError("bands must be a positive integer")
    m, k = layers, bands
    r = 2*k*p+q
    a, b, c = (2*k+3)*p+(4*m+1)*r, (2*k+2)*p+(2*m+1)*r, (2*k+1)*p
    train = Counter()
    for j in range(2*m):
        sign = 1 if j % 2 == 0 else -1
        for i in range(2*k+1):
            train[(i+1)*p+(j+1)*r] += sign*(2 if i % 2 == 0 else -2)
    shift = p+2*m*r
    numerators = [Counter({1: 1, a: -1}), Counter({1: -1, b: 1}), Counter()]
    numerators[2][1] -= 1
    numerators[2][c] += 1
    for i in range(1, 2*k+1):
        numerators[2][i*p] += 2 if i % 2 else -2
    for depth, coefficient in train.items():
        numerators[0][depth] -= coefficient
        numerators[0][depth+shift] -= coefficient
        numerators[1][depth] += coefficient
    left, right = [], [(0, 0)]
    for arm, (numerator, length) in enumerate(zip(numerators, (a, b, c)), 1):
        sign = 0
        for depth in range(1, length+1):
            sign += numerator[depth]
            if depth == length:
                if sign:
                    raise ArithmeticError("a word did not end at its omitted tip")
            elif abs(sign) != 1:
                raise ArithmeticError("a word has a non-sign coefficient")
            else:
                (left if sign == 1 else right).append((arm, depth))
    checked = check_pair([a, b, c], left, right)
    expected = 3*(k+1)*p+(3*m+1)*r-1
    if not checked["homometric"] or checked["size"] != expected:
        raise ArithmeticError("the constructed words failed their original-tree check")
    return {"parameters": [p, q], "layers": m, "bands": k, "step": r, "lengths": [a, b, c],
            "left": left, "right": right, **checked}


def companion_witness(p: int, r: int) -> dict:
    """Construct T(7r+p,5r,2r-p) for 1<=p<r, again omitting only tips."""
    if type(p) is not int or type(r) is not int or not 1 <= p < r:
        raise ValueError("companion parameters must be integers with 1<=p<r")
    runs = (
        ((1, 2*r-p-1), (-1, p), (1, r), (-1, p), (1, r-p),
         (-1, p), (1, r), (-1, p), (1, 2*r-p)),
        ((-1, 2*r-p-1), (1, p), (-1, r), (1, p), (-1, 2*r-p)),
        ((-1, r-p-1), (1, p), (-1, r-p)),
    )
    left, right = [], [(0, 0)]
    for arm, blocks in enumerate(runs, 1):
        depth = 0
        for sign, length in blocks:
            for position in range(depth+1, depth+length+1):
                (left if sign == 1 else right).append((arm, position))
            depth += length
    lengths = [7*r+p, 5*r, 2*r-p]
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or checked["size"] != 7*r-1:
        raise ArithmeticError("the companion words failed their original-tree check")
    return {"companion_parameters": [p, r], "lengths": lengths,
            "left": left, "right": right, **checked}


def family_witness(t: int) -> dict:
    t = _parameter(t)
    return {"t": t, **parameter_witness(3*t, t)}


# Sparse Laurent polynomials in independent variables z,x,y. These tables
# are endpoint numerators, separate from the literal block implementation.
Poly = dict[tuple[int, ...], int]


def _add(*polynomials: Poly) -> Poly:
    result = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, 0)+coefficient
    return {e: c for e, c in result.items() if c}


def _scale(polynomial: Poly, factor: int) -> Poly:
    return {e: factor*c for e, c in polynomial.items() if factor*c}


def _mul(a: Poly, b: Poly) -> Poly:
    result = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            exponent = tuple(x+y for x, y in zip(ea, eb))
            result[exponent] = result.get(exponent, 0)+ca*cb
    return {e: c for e, c in result.items() if c}


def symbolic_numerators() -> tuple[Poly, Poly, Poly]:
    """N_i=(1-z)S_i, with x=z^p and y=z^q substituted only after proof."""
    endpoints = (
        (((3, 1), -2), ((4, 1), 2), ((5, 1), -2), ((5, 2), 2),
         ((6, 2), -2), ((7, 2), 2), ((8, 3), -2), ((9, 3), 2),
         ((10, 3), -2), ((10, 4), 2), ((11, 4), -2), ((12, 4), 2), ((15, 5), -1)),
        (((3, 1), 2), ((4, 1), -2), ((5, 1), 2), ((5, 2), -2),
         ((6, 2), 2), ((7, 2), -2), ((10, 3), 1)),
        (((1, 0), 2), ((2, 0), -2), ((3, 0), 1)),
    )
    result = []
    for first_sign, terms in zip((1, -1, -1), endpoints):
        result.append({(1, 0, 0): first_sign,
                       **{(0, a, b): c for (a, b), c in terms}})
    return tuple(result)


def identity_residual(numerators: tuple[Poly, Poly, Poly] | None = None) -> Poly:
    """Exact z(1-z) times the full signed-shell numerator; zero proves all p,q."""
    ns = symbolic_numerators() if numerators is None else numerators
    if len(ns) != 3:
        raise ValueError("three arm numerators are required")
    one, z = {(0, 0, 0): 1}, {(1, 0, 0): 1}
    endpoints = ({(0, 15, 5): 1}, {(0, 10, 3): 1}, {(0, 3, 0): 1})
    result = _scale(_mul(_add(one, _scale(z, -1)),
                         _add(z, _scale(_add(*endpoints), -1))), -1)
    for i, numerator in enumerate(ns):
        others = _add(*(endpoint for j, endpoint in enumerate(endpoints) if j != i))
        star = {tuple(-value for value in e): c for e, c in numerator.items()}
        result = _add(result, _mul(numerator, _add(z, _scale(others, -1))),
                      _mul(_mul(z, endpoints[i]), star))
    return result


def companion_numerators() -> tuple[Poly, Poly, Poly]:
    """Endpoint numerators in independent z,x,v for the companion family."""
    one, z = {(0, 0, 0): 1}, {(1, 0, 0): 1}
    h, e, c = {(0, 1, 2): 1}, {(0, 0, 5): 1}, {(0, -1, 2): 1}
    k = {(0, -1, 2): 2, (0, 0, 2): -2, (0, 0, 3): 2, (0, 1, 3): -2}
    p = {(0, -1, 1): 1, (0, 0, 1): -1}
    return (_add(z, _scale(_mul(_add(one, h), k), -1), _scale(_mul(h, e), -1)),
            _add(_scale(z, -1), k, e),
            _add(_scale(z, -1), c, _scale(p, 2)))


def companion_identity_residual(numerators: tuple[Poly, Poly, Poly] | None = None) -> Poly:
    ns = companion_numerators() if numerators is None else numerators
    one, z = {(0, 0, 0): 1}, {(1, 0, 0): 1}
    ends = ({(0, 1, 7): 1}, {(0, 0, 5): 1}, {(0, -1, 2): 1})
    result = _scale(_mul(_add(one, _scale(z, -1)),
                         _add(z, _scale(_add(*ends), -1))), -1)
    for i, numerator in enumerate(ns):
        others = _add(*(end for j, end in enumerate(ends) if j != i))
        star = {tuple(-value for value in e): c for e, c in numerator.items()}
        result = _add(result, _mul(numerator, _add(z, _scale(others, -1))),
                      _mul(_mul(z, ends[i]), star))
    return result


def general_symbolic_numerators() -> tuple[Poly, Poly, Poly]:
    """(1+x)(1+v)N_i in independent z,x,v,w,c, before power substitutions."""
    one = {(0, 0, 0, 0, 0): 1}
    z, x, v, w, c = ({tuple(int(i == j) for i in range(5)): 1} for j in range(5))
    h, e = _mul(x, w), _mul(_mul(_mul(x, c), v), w)
    denominator = _mul(_add(one, x), _add(one, v))
    train = _scale(_mul(_mul(_mul(x, v), _add(one, c)),
                        _add(one, _scale(w, -1))), 2)
    short = _mul(_add(_mul(c, x), _scale(c, -1), _scale(x, 2)), _add(one, v))
    return (
        _add(_mul(z, denominator), _scale(_mul(_add(one, h), train), -1),
             _scale(_mul(_mul(h, e), denominator), -1)),
        _add(_scale(_mul(z, denominator), -1), train, _mul(e, denominator)),
        _add(_scale(_mul(z, denominator), -1), short),
    )


def general_identity_residual(numerators: tuple[Poly, Poly, Poly] | None = None) -> Poly:
    """Expand (1+x)(1+v)R, proving all layer and band counts simultaneously."""
    ns = general_symbolic_numerators() if numerators is None else numerators
    if len(ns) != 3:
        raise ValueError("three arm numerators are required")
    one = {(0, 0, 0, 0, 0): 1}
    z, x, v = ({tuple(int(i == j) for i in range(5)): 1} for j in range(3))
    denominator = _mul(_add(one, x), _add(one, v))
    ends = ({(0, 2, 1, 2, 1): 1}, {(0, 1, 1, 1, 1): 1}, {(0, 0, 0, 0, 1): 1})
    result = _scale(_mul(_mul(_add(one, _scale(z, -1)),
                                _add(z, _scale(_add(*ends), -1))), denominator), -1)
    for i, numerator in enumerate(ns):
        others = _add(*(end for j, end in enumerate(ends) if j != i))
        star = {tuple(-value for value in e): coefficient
                for e, coefficient in numerator.items()}
        result = _add(result, _mul(numerator, _add(z, _scale(others, -1))),
                      _mul(_mul(_mul(_mul(z, x), v), ends[i]), star))
    return result


def check_document(document: object) -> dict:
    if not isinstance(document, dict):
        raise ValueError("a witness must be a JSON object")
    lengths, left, right = (document.get(k) for k in ("lengths", "left", "right"))
    checked = check_pair(lengths, left, right)
    return {**checked, "terminal": terminal_certificate(lengths, left, right)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lemma", type=int, metavar="T")
    mode.add_argument("--witness", type=int, metavar="T")
    mode.add_argument("--parameters", type=int, nargs=2, metavar=("P", "Q"))
    mode.add_argument("--companion", type=int, nargs=2, metavar=("P", "R"))
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--check", metavar="FILE", help="JSON witness; '-' reads stdin")
    parser.add_argument("--layers", type=int, default=1,
                        help="nonnegative layer count, only with --parameters")
    parser.add_argument("--bands", type=int, default=1,
                        help="positive short-arm block parameter, only with --parameters")
    args = parser.parse_args()
    if (args.layers != 1 or args.bands != 1) and args.parameters is None:
        parser.error("--layers and --bands apply only to --parameters")
    try:
        if args.lemma is not None:
            result = family_bound(args.lemma)
        elif args.witness is not None:
            result = family_witness(args.witness)
        elif args.parameters is not None:
            result = parameter_witness(*args.parameters, layers=args.layers, bands=args.bands)
        elif args.companion is not None:
            result = companion_witness(*args.companion)
        elif args.prove:
            if (identity_residual() or general_identity_residual()
                    or companion_identity_residual()):
                raise ArithmeticError("the exact Laurent identity failed")
            result = {"identity": "zero polynomials in three and five independent Laurent variables",
                      "domain": "block and companion domains in RATIO_50_33_9.md",
                      "universal_tripod_target": False}
        else:
            data = sys.stdin.read() if args.check == "-" else Path(args.check).read_text()
            result = check_document(json.loads(data))
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("homometric", True) else 1
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
