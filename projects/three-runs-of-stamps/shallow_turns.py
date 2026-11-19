#!/usr/bin/env python3
"""Construct the three shallow-turn stamp families; see shallow-turns.md.

The constructors choose named gaps, never run a legality search.  The CLI
compares their entire output sets with the separate matching-stack checker.
"""
from __future__ import annotations

import argparse
from collections.abc import Iterator
from dataclasses import dataclass

from weighted_open import exterior, in_gap, outward_mountain, adjacent_mountain
from delayed_escape import adjacent, put

Order = tuple[int, ...]


def validate(a: int, r: int, d: int) -> None:
    if not (r >= 6 and a >= r + 1 and 1 <= d <= r - 5):
        raise ValueError("require r >= 6, a >= r+1 and 1 <= d <= r-5")


def old(label: int) -> int:
    """At the zero-face core, the formal old endpoint -1 means face zero."""
    if label < -1:
        raise ValueError("the named old gap has passed the zero-face core")
    return max(label, 0)


def outward_valley(prefix: Order) -> Order:
    return put(prefix, len(prefix) if (len(prefix) - 1) % 2 == 0 else 0)


def mountain(a: int, d: int) -> Order:
    """Unique M^a stack first turning inward at t=a-d."""
    prefix = exterior(a - d - 1)
    for _ in range(d + 1):
        prefix = adjacent_mountain(prefix)
    return prefix


def prefixes(a: int, r: int, d: int) -> dict[str, Order]:
    """A: direct crossing; B: outward then return; C: stay outward."""
    validate(a, r, d)
    t = a - d
    common = mountain(a, d)
    for j in range(1, d + 1):
        common = in_gap(common, a - j - 1, a - j + 1)
    direct = common
    for j in range(d + 1, r):
        direct = in_gap(direct, old(a - j - 1), old(a - j - 3))
    outside = in_gap(common, t - 3, t)
    for _ in range(2):
        outside = outward_valley(outside)
    returned = in_gap(outside, t - 3, a + d + 1)
    for j in range(d + 5, r):
        returned = in_gap(returned, old(a - j + 3), old(a - j + 1))
    for _ in range(d + 4, r):
        outside = outward_valley(outside)
    return {"A": adjacent(direct, "V"),
            "B": adjacent(returned, "V"),
            "C": adjacent(outside, "V")}


def path_step(prefix: Order, path: str, j: int, a: int, r: int, d: int) -> Order:
    """Regular named gaps and the first gap of each finite return path."""
    t = a - d

    def x(i: int) -> int:
        return a + i

    def gap(u: int, v: int) -> Order:
        return in_gap(prefix, old(u), old(v))

    if path == "A-main":
        return gap(a-r+j-2, x(r-j+1))
    if path == "A-return":
        return gap(a-r+j-2, x(r-j-1))
    if path in ("A-inner", "A-slow"):
        start = r-d-1 if path == "A-inner" else r-d+3
        h = j-start
        return gap(t+1+h, x(d-h))
    if path == "B-main":
        return gap(a-r+j+2, x(r-j+1))
    if path == "B-return":
        return gap(a-r+j+2, x(r-j-1))
    if path in ("B-inner", "B-slow"):
        start = r-d-3 if path == "B-inner" else r-d+1
        h = j-start
        return gap(t-1+h, x(d-h))
    if path == "C-return":
        return gap(x(r-j-1), x(r-j-3))
    if path == "C-slow":
        return gap(x(r-j+3), x(r-j+1))
    if path in ("C-first", "C-second", "C-late-first", "C-late-second"):
        start = r-d-4 + (4 if "late" in path else 0)
        h = j-start
        if path.endswith("first"):
            return gap(t-2+h, x(d+3-h))
        if h == 0:
            return gap(t-3, x(d+1))
        return gap(t-2+h, x(d+1-h))
    raise ValueError(f"unknown path: {path}")


def frontiers(a: int, r: int, d: int, family: str) -> Iterator[dict[str, Order]]:
    """All open M paths at each depth 1..r, from the proved gap table.

    Open excludes adjacent insertions starting with the second M.  Distinct
    names denote distinct histories, including when two branches coexist.
    """
    bases = prefixes(a, r, d)
    if family not in bases:
        raise ValueError("family must be A, B or C")
    prefix = bases[family]
    t = a-d

    def x(i: int) -> int:
        return a+i

    def y(i: int) -> int:
        return a+r+i

    if family == "A":
        states = {"A-main": in_gap(prefix, x(r), old(a-r-2)),
                  "A-return": in_gap(prefix, old(a-r-1), x(r-2))}
    elif family == "B":
        states = {"B-main": in_gap(prefix, x(r), old(a-r+2)),
                  "B-return": in_gap(prefix, old(a-r+3), x(r-2))}
    else:
        states = {"C-outer": in_gap(prefix, x(r), x(r-3))}
        if r == d+5:
            # The ordinary return path splits before its first insertion.
            for path in ("C-first", "C-second"):
                states[path] = path_step(prefix, path, 1, a, r, d)
        else:
            states["C-return"] = in_gap(prefix, x(r-4), x(r-2))
    yield states
    for j in range(2, r+1):
        following = {}
        for path, prefix in states.items():
            def regular(name: str = path) -> None:
                following[name] = path_step(prefix, name, j, a, r, d)

            if path == "A-main":
                regular()
            elif path == "A-return":
                if j < r-d-1:
                    regular()
                else:
                    regular("A-inner")
                    following["A-outer"] = in_gap(prefix, t-3, t)
            elif path == "A-inner":
                if j <= r-2:
                    regular()
            elif path == "A-outer":
                following[path] = outward_mountain(prefix)
                if j == r-d+2:
                    following["A-slow"] = in_gap(prefix, t, y(r-d-1))
            elif path == "A-slow":
                regular()
            elif path == "B-return":
                if j <= r-2:
                    regular()
            elif path == "B-main":
                if j < r-d-3:
                    regular()
                else:
                    regular("B-inner")
                    following["B-outer"] = in_gap(prefix, x(d+4), x(d+1))
            elif path == "B-inner":
                if j <= r-3:
                    regular()
            elif path == "B-outer":
                following[path] = outward_mountain(prefix)
                if j == r-d:
                    following["B-slow"] = in_gap(prefix, x(d+1), y(r-d-3))
            elif path == "B-slow":
                regular()
            elif path == "C-outer":
                following[path] = outward_mountain(prefix)
                if j == 4:
                    following["C-slow"] = in_gap(prefix, x(r-3), y(1))
            elif path == "C-return":
                if j < r-d-4:
                    regular()
                else:
                    regular("C-first")
                    regular("C-second")
            elif path == "C-slow":
                if j < r-d:
                    regular()
                else:
                    regular("C-late-first")
                    regular("C-late-second")
            elif path == "C-first":
                if j <= r-2:
                    regular()
            elif path == "C-second":
                if j <= r-3:
                    regular()
            else:  # The two late C returns survive through the horizon.
                regular()
        states = following
        yield states


@dataclass(frozen=True)
class Parameter:
    family: str
    depth: int
    path: str


def expand(a: int, r: int, d: int, parameter: Parameter) -> Order:
    """Close immediately after the named open depth; r means no closure."""
    if not 1 <= parameter.depth <= r:
        raise ValueError("open depth must be between 1 and r")
    levels = list(frontiers(a, r, d, parameter.family))
    if parameter.path not in levels[parameter.depth-1]:
        raise ValueError("path does not exist at the supplied depth")
    order = levels[parameter.depth-1][parameter.path]
    for _ in range(parameter.depth, r):
        order = adjacent_mountain(order)
    return order


def parameters(a: int, r: int, d: int, family: str) -> Iterator[Parameter]:
    for depth, states in enumerate(frontiers(a, r, d, family), 1):
        for path in states:
            yield Parameter(family, depth, path)


def constructed(a: int, r: int, d: int, family: str) -> set[Order]:
    # Build each frontier once; do not repeat it for every parameter.
    result = set()
    for states in frontiers(a, r, d, family):
        for order in states.values():
            for _ in range(a+2*r+1-len(order)):
                order = adjacent_mountain(order)
            result.add(order)
    return result


def recover(order: Order, a: int, r: int, d: int) -> Parameter:
    """Recover the unique family, first closure and open path; reject outsiders."""
    bases = prefixes(a, r, d)
    if len(order) != a+2*r+1 or set(order) != set(range(len(order))):
        raise ValueError("expected a complete labeled order")
    base = tuple(face for face in order if face <= a+r)
    family = next((name for name, prefix in bases.items() if prefix == base), None)
    if family is None:
        raise ValueError("order is outside the three prefix families")
    depth = r
    for j in range(2, r+1):
        label = a+r+j
        restricted = tuple(face for face in order if face <= label)
        if abs(restricted.index(label)-restricted.index(label-1)) == 1:
            depth = j-1
            break
    open_order = tuple(face for face in order if face <= a+r+depth)
    levels = list(frontiers(a, r, d, family))
    paths = [name for name, prefix in levels[depth-1].items() if prefix == open_order]
    if len(paths) != 1:
        raise ValueError("order has no unique open trajectory")
    parameter = Parameter(family, depth, paths[0])
    if expand(a, r, d, parameter) != order:
        raise ValueError("order does not have the forced adjacent tail")
    return parameter


def expected_weights(r: int, d: int) -> dict[str, int]:
    validate(r+1, r, d)
    return {"A": 2*r+2*d-1, "B": 2*r+2*d, "C": 3*r+2*d-2}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", type=int, default=11, help="initial mountain length")
    parser.add_argument("--r", type=int, default=10, help="valley and final mountain length")
    parser.add_argument("--d", type=int, default=2, help="a minus first inward mountain step")
    args = parser.parse_args()
    try:
        bases = prefixes(args.a, args.r, args.d)
    except ValueError as exc:
        parser.error(str(exc))
    from reconstruction import extend
    word = "M"*args.a + "V"*args.r + "M"*args.r
    for family, prefix in bases.items():
        actual = constructed(args.a, args.r, args.d, family)
        independent = set(extend(prefix, word))
        if actual != independent or len(actual) != expected_weights(args.r, args.d)[family]:
            raise AssertionError(f"{family}: whole-set comparison or weight failed")
        for order in actual:
            if expand(args.a, args.r, args.d, recover(order, args.a, args.r, args.d)) != order:
                raise AssertionError("parameter round trip failed")
        print(f"{family}: {len(actual)} complete labeled stacks; full sets and inverse agree")
    print("Shallow band only; author proof awaiting independent review, not the full cubic.")


if __name__ == "__main__":
    main()
