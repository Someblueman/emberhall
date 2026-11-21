"""Exact shell equations for arbitrary holes and independently coloured layers.

The no-go theorem is scoped in EDGE_DEPENDENT.md; it is not a bound on all pairs.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import json
from math import gcd
from pathlib import Path

from progression_target import _add, _mon, _mul, _scale

Vertex = tuple[int, int]
Poly = dict[int, int]


def add(*polys: Poly) -> Poly:
    out: Counter = Counter()
    for poly in polys:
        for power, value in poly.items():
            out[power] += value
    return {power: value for power, value in out.items() if value}


def shift(poly: Poly, power: int, factor: int = 1) -> Poly:
    return {k + power: factor * v for k, v in poly.items() if factor * v}


def multiply(left: Poly, right: Poly) -> Poly:
    return add(*(shift(left, k, v) for k, v in right.items()))


def validate_lengths(lengths) -> None:
    if (len(lengths) != 3
            or any(type(n) is not int or n < 1 for n in lengths)):
        raise ValueError("require three positive integer arm lengths")


def vertices(lengths: tuple[int, int, int]) -> list[Vertex]:
    validate_lengths(lengths)
    return [(0, 0)] + [(i, p) for i, n in enumerate(lengths, 1)
                       for p in range(1, n + 1)]


def validate_signs(lengths, signs, *, full: bool = False) -> None:
    universe = set(vertices(lengths))
    if (not set(signs) <= universe
            or any(type(s) is not int or s not in (-1, 1) for s in signs.values())
            or (full and set(signs) != universe)):
        raise ValueError("signs must assign +/-1 to valid, distinct tree vertices")


def components(lengths, signs) -> tuple[Poly, Poly, Poly, Poly, Poly]:
    """Return C,V,U,X,Y. No balance or homometry assumption is used here."""
    centre = signs.get((0, 0), 0)
    ends = [{n: 1} for n in lengths]
    c = add({0: 1}, *(shift(a, 0, -1) for a in ends))
    v, u, x, y = {}, {}, {}, {}
    for i, n in enumerate(lengths, 1):
        arm = {p: signs[i, p] for p in range(1, n + 1) if (i, p) in signs}
        kernel = add({0: 1}, *(shift(a, 0, -1)
                              for j, a in enumerate(ends, 1) if j != i))
        v = add(v, multiply(arm, kernel))
        u = add(u, {n - p: s for p, s in arm.items()})
        leaf = signs.get((i, n), 0)
        x = add(x, multiply(add({0: centre}, {n: -leaf}), kernel))
        y = add(y, {n: centre}, {0: -leaf})
    return c, v, u, x, y


def full_shell(lengths, signs) -> Poly:
    c, v, u, _, _ = components(lengths, signs)
    return add(shift(c, 0, signs.get((0, 0), 0)), v, shift(u, 0, -1))


def shell_numerator(lengths, signs) -> Poly:
    """(1-z)*2*(positive profile-negative profile), with arbitrary holes."""
    validate_signs(lengths, signs)
    if sum(signs.values()):
        raise ValueError("the two colour classes must have equal size")
    correction = Counter()
    for arm, depth in set(vertices(lengths)) - set(signs):
        for (i, p), s in signs.items():
            distance = abs(depth - p) if arm == i else depth + p
            correction[distance] += s
    return add(shift(full_shell(lengths, signs), 1),
               shift(dict(correction), 0, -1), shift(dict(correction), 1))


def layer_residuals(lengths, rows) -> list[Poly]:
    """Exact residue equations for arbitrary edge signs, not just seed layers.

    A row is ('child' or 'parent', a full +/-1 assignment on the coarse tree).
    Child rows alone represent every assignment of signs to inserted vertices.
    The coarse original colouring must separately be balanced and homometric.
    """
    factor = len(rows) + 1
    if factor < 3 or factor % 2 == 0:
        raise ValueError("require an odd subdivision factor >= 3")
    terms = []
    for endpoint, signs in rows:
        validate_signs(lengths, signs, full=True)
        if endpoint not in ("parent", "child"):
            raise ValueError("endpoint must be parent or child")
        _, v, u, x, y = components(lengths, signs)
        terms.append((shift(v, -1) if endpoint == "child" else add(v, x),
                      u if endpoint == "child" else shift(add(u, y), -1)))
    return [add(terms[r][0], shift(terms[-1-r][1], 0, -1))
            for r in range(factor - 1)]


def lift(lengths, base, rows):
    validate_signs(lengths, base, full=True)
    if sum(base.values()) or full_shell(lengths, base):
        raise ValueError("the coarse base must be balanced and homometric")
    layer_residuals(lengths, rows)  # Validate rows even when their residual is nonzero.
    factor = len(rows) + 1
    signs = {(0, 0): base[0, 0]}
    for i, n in enumerate(lengths, 1):
        for p in range(1, n + 1):
            signs[i, factor*p] = base[i, p]
            for r, (endpoint, row) in enumerate(rows, 1):
                source = (i, p) if endpoint == "child" else (
                    (i, p-1) if p > 1 else (0, 0))
                signs[i, factor*(p-1)+r] = row[source]
    return tuple(factor*n for n in lengths), signs


def graph_counts(lengths, subset) -> dict[int, int]:
    """Independent original-tree BFS counter; no shell algebra is used."""
    graph = {v: [] for v in vertices(lengths)}
    for i, n in enumerate(lengths, 1):
        previous = (0, 0)
        for p in range(1, n + 1):
            v = (i, p)
            graph[v].append(previous)
            graph[previous].append(v)
            previous = v
    subset = sorted(subset)
    counts = Counter()
    for index, source in enumerate(subset):
        distances = {source: 0}
        pending = deque([source])
        while pending:
            v = pending.popleft()
            for other in graph[v]:
                if other not in distances:
                    distances[other] = distances[v] + 1
                    pending.append(other)
        counts.update(distances[v] for v in subset[index+1:])
    return dict(sorted(counts.items()))


def check_pair(lengths, left, right) -> dict:
    universe = set(vertices(lengths))
    converted = []
    for subset in (left, right):
        if any(not isinstance(v, (list, tuple)) or len(v) != 2
               or any(type(x) is not int for x in v) for v in subset):
            raise ValueError("vertices must be integer [arm, depth] pairs")
        subset = [tuple(v) for v in subset]
        if len(set(subset)) != len(subset) or not set(subset) <= universe:
            raise ValueError("duplicate or invalid vertex")
        converted.append(subset)
    left, right = converted
    if len(left) != len(right) or set(left) & set(right):
        raise ValueError("require disjoint equal-size sets")
    lp, rp = graph_counts(lengths, left), graph_counts(lengths, right)
    signs = {**dict.fromkeys(left, 1), **dict.fromkeys(right, -1)}
    numerator = shell_numerator(lengths, signs)
    if (lp == rp) != (not numerator):
        raise ArithmeticError("BFS and the shell identity disagree")
    target = len(universe)//2-1
    return {"lengths": lengths, "left": left, "right": right,
            "size": len(left), "target": target, "meets_target": len(left) >= target,
            "homometric": lp == rp, "left_profile": lp, "right_profile": rp,
            "shell_numerator": numerator}


def parameter_certificate(t: int) -> dict:
    if type(t) is not int or t < 0:
        raise ValueError("parameter must be a nonnegative integer")
    remaining = t % 3 == 0 and t % 15 != 3 and t % 11 not in (1, 6, 9)
    n, m = 1064*t, 760*t
    five = (gcd(n+14, n+3), gcd(n+14, 4), gcd(n+3, 15))
    seven = (gcd(m+10, m+2), gcd(m+10, 3), gcd(m+2, 11))
    if remaining and (five[0:2] != (1, 2) or five[2] not in (1, 3, 5)
                      or seven != (2, 1, 1)):
        raise ArithmeticError("gcd certificate failed")
    return {"parameter": t, "remaining_class": remaining,
            "five_gcds": five, "seven_gcds": seven,
            "independent_seed_layers_excluded": remaining,
            "target_ruled_out": False}


def odd_common_factor_bound(lengths) -> dict:
    """Exclude every full partition, not just lifts, on the stated odd-arm domain."""
    validate_lengths(lengths)
    factor = gcd(*lengths)
    if factor == 1 or any(n % 2 == 0 for n in lengths):
        raise ValueError("require three odd lengths with a common factor greater than one")
    target = (1 + sum(lengths))//2 - 1
    return {"lengths": lengths, "common_odd_factor": factor,
            "odd_quotients": [n//factor for n in lengths], "upper_bound": target,
            "target": target, "full_partition_impossible": True,
            "target_ruled_out": False}


def prove() -> dict:
    # Laurent identity behind the elimination in equation (8) of the document.
    one, a, b, c = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    d, e = _mon(1, -1), _mon(1, s=-1)
    total = _add(one, _scale(a, -1), _scale(b, -1), _scale(c, -1))
    k = _add(one, _scale(b, -1), _scale(c, -1))
    for centre in (-1, 1):
        for opposite in range(3):
            ends = (a, b, c)
            leaves = [centre if i != opposite else -centre for i in range(3)]
            boundary = {}
            for i, endpoint in enumerate(ends):
                kernel = _add(one, *[_scale(other, -1) for j, other in enumerate(ends)
                                     if j != i])
                boundary = _add(boundary, _mul(
                    _add(_scale(one, centre), _scale(endpoint, -leaves[i])), kernel))
            same = [endpoint for i, endpoint in enumerate(ends) if i != opposite]
            expected = _add(_scale(total, centre), _scale(_mul(
                _add(one, _scale(same[0], -1)),
                _add(one, _scale(same[1], -1))), 2*centre))
            if _add(boundary, _scale(expected, -1)):
                raise ArithmeticError("endpoint boundary identity failed")
    residual = _add(_scale(total, -1),
                    _scale(_mul(k, _add(a, _scale(one, -1),
                                       _scale(d, -1), _scale(e, -1))), -1),
                    _scale(_mul(_add(d, e), _mul(_add(one, _scale(b, -1)),
                                                               _add(one, _scale(c, -1)))), -1))
    if residual:
        raise ArithmeticError("nonzero elimination identity")
    # Five: the same coefficient of P occurs at 5 and 5+k; the RHS changes sign.
    rhs = {j: (-1)**(j-5) for j in range(5, 16)}
    for period in (1, 3, 5):
        coefficient = lambda power: tuple(
            sum(power == r+j for j in range(0, 15, period))
            for r in range(1, period+1))
        if coefficient(5) != coefficient(5+period) or rhs[5] == rhs[5+period]:
            raise ArithmeticError("five-family contradiction failed")
    # Seven: coefficients at 4,12 force p=r=-1, whereas degree 1 requires p+r=0.
    lhs_p, lhs_r = {1: 1, 4: -1}, {1: 1, 12: -1}
    rhs = {4: 1, 5: -1, 12: 1, 13: -1}
    p, r = rhs[4]//lhs_p[4], rhs[12]//lhs_r[12]
    if p*lhs_p[1] + r*lhs_r[1] == rhs.get(1, 0):
        raise ArithmeticError("seven-family contradiction failed")
    residues = [t for t in range(165) if parameter_certificate(t)["remaining_class"]]
    if len(residues) != 32:
        raise ArithmeticError("unexpected residue count")
    # Modulo z**g+1, A_i=-1: 3*Q-Q* = 8*(s+sum S_i).
    q, reflected_q = (4, 3, 1), (4, 1, 3)
    if tuple(3*a-b for a, b in zip(q, reflected_q)) != (8, 8, 0):
        raise ArithmeticError("odd common-factor identity failed")
    lengths, base, seeds = mixed_rows()
    if sum(base.values()) or full_shell(lengths, base) or any(
            layer_residuals(lengths, [("child", seed) for seed in seeds])):
        raise ArithmeticError("mixed-edge polynomial certificate failed")
    return {"proof": "PASS", "excluded_class": "independent homometric seed layers",
            "remaining_residues_mod_165": residues, "mixed_edge_certificate": "PASS",
            "target_ruled_out": False}


def demo() -> dict:
    lengths = (3, 2, 2)
    vv = vertices(lengths)
    base = dict(zip(vv, (1, -1, -1, -1, -1, 1, 1, 1)))
    seed = dict(zip(vv, (1, -1, -1, -1, 1, 1, -1, 1)))
    rows = [("child", seed), ("child", {v: -s for v, s in seed.items()})]
    if any(layer_residuals(lengths, rows)):
        raise ArithmeticError("positive control layer identity failed")
    fine, signs = lift(lengths, base, rows)
    left = [v for v, s in signs.items() if s == 1]
    right = [v for v, s in signs.items() if s == -1]
    result = check_pair(fine, left, right)
    altered = dict(signs)
    altered[0, 0], altered[1, 1] = altered[1, 1], altered[0, 0]
    rejection = check_pair(fine, [v for v, s in altered.items() if s == 1],
                           [v for v, s in altered.items() if s == -1])
    if not result["homometric"] or rejection["homometric"]:
        raise ArithmeticError("positive/altered control failed")
    return {**result, "construction": "independent seed layers, positive control",
            "altered_pair_rejected": True}


def mixed_rows():
    """Return the fixed, exactly checkable mixed-edge polynomial certificate."""
    lengths = (18, 14, 3)
    base = {(0, 0): 1}
    for i, n in enumerate(lengths, 1):
        base.update({(i, p): -1 if i == 1 else 1 for p in range(1, n+1)})
    words = (("++-+-++--+-----+--", "+-+++-+++++-++", "-+-"),
             ("-+-+---+-+-+++-+++", "+---+-+---+---", "-++"))
    seeds = []
    for arm_words in words:
        seed = {(0, 0): 1}  # Child rows never use this entry.
        for i, word in enumerate(arm_words, 1):
            seed.update({(i, p): 1 if s == "+" else -1
                         for p, s in enumerate(word, 1)})
        seeds.append(seed)
    return lengths, base, seeds


def mixed_control(factor: int) -> dict:
    """All odd g: target-size pair on T(18g+1,14g+1,3g); only g=5 is affine t=0."""
    if type(factor) is not int or factor < 3 or factor % 2 == 0:
        raise ValueError("require an odd subdivision factor >= 3")
    lengths, base, seeds = mixed_rows()
    if any(layer_residuals(lengths, [("child", seed) for seed in seeds])):
        raise ArithmeticError("mixed-edge certificate failed")
    half = (factor-1)//2
    rows = [("child", seeds[0])]*half + [("child", seeds[1])]*half
    fine, signs = lift(lengths, base, rows)
    original = (fine[0]+1, fine[1]+1, fine[2])
    result = check_pair(original, [v for v, s in signs.items() if s == 1],
                        [v for v, s in signs.items() if s == -1])
    if not result["homometric"] or result["size"] != result["target"]:
        raise ArithmeticError("mixed-edge witness failed")
    return {**result, "factor": factor, "affine_family_parameter": 0 if factor == 5 else None,
            "construction": "mixed symmetric and antisymmetric edge fillers"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prove", action="store_true")
    group.add_argument("--parameter", type=int)
    group.add_argument("--demo", action="store_true")
    group.add_argument("--mixed-control", type=int, metavar="ODD_G")
    group.add_argument("--odd-common-factor", nargs=3, type=int, metavar=("A", "B", "C"))
    group.add_argument("--check", type=Path)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        if args.prove:
            result = prove()
        elif args.parameter is not None:
            result = parameter_certificate(args.parameter)
        elif args.demo:
            result = demo()
        elif args.mixed_control is not None:
            result = mixed_control(args.mixed_control)
        elif args.odd_common_factor is not None:
            result = odd_common_factor_bound(tuple(args.odd_common_factor))
        else:
            pair = json.loads(args.check.read_text())
            result = check_pair(tuple(pair["lengths"]), pair["left"], pair["right"])
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"{error}\n")
    if args.summary:
        result = {k: v for k, v in result.items()
                  if k not in ("left", "right", "left_profile", "right_profile")}
    print(json.dumps(result, sort_keys=True))
    return int(result.get("homometric") is False)


if __name__ == "__main__":
    raise SystemExit(main())
