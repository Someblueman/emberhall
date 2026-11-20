#!/usr/bin/env python3
"""Labeled constructions for the last inward mountain, described in last-turn.md."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, adjacent, nest
from weighted_open import exterior, in_gap, outward_mountain


def stopped_prefixes(a: int, r: int) -> dict[str, Order]:
    if r < 5 or a < r:
        raise ValueError("require a >= r >= 5")
    mountain = adjacent(exterior(a - 1), "M")
    outer = adjacent(mountain, "V")
    for j in range(2, r):
        face = a + j
        outer = outer + (face,) if face % 2 else (face,) + outer
        if j == 3:
            returning = outer
    returning = in_gap(returning, a - 3, a + 1)
    for j in range(5, r):
        returning = in_gap(returning, a - j + 3, a - j + 1)
    result = {"outer": adjacent(outer, "V"), "return": adjacent(returning, "V")}
    if a > r:
        direct = mountain
        for j in range(1, r):
            direct = in_gap(direct, a - j - 1, max(0, a - j - 3))
        result["direct"] = adjacent(direct, "V")
    return result


def _direct_or_return(prefix: Order, a: int, r: int, direct: bool) -> Iterator[Order]:
    # In both geometries the moving gap pairs a mountain face with a valley
    # face. The older mountain indices differ by four between the two paths.
    offset = 2 if direct else -2
    far = prefix
    for k in range(1, r - 1):
        far = in_gap(far, a - (r - k + offset), a + r - k - 1)
        yield far
    if direct:
        far = in_gap(far, a, a - 3)
        yield far
        yield outward_mountain(far)

    near = adjacent(prefix, "M")
    yield near
    last_regular = r if direct else r - 4
    for k in range(2, last_regular + 1):
        near = in_gap(near, a - (r - k + offset), a + r - k + 1)
        yield near
    if not direct:
        yield in_gap(near, a, a - 1)
        returning = in_gap(near, a + 1, a + 4)
        yield returning
        for _ in range(2):
            returning = outward_mountain(returning)
            yield returning
        yield outward_mountain(returning)
        yield in_gap(returning, a + 1, a + 2 * r - 3)


def _outer_descent(start: Order, a: int, r: int, delayed: bool) -> Iterator[Order]:
    # The delayed entry follows the same old gaps four mountains later.
    current = start
    for i in range(1, r - 4):
        current = in_gap(current, a + r - i - 1, a + r - i - 3)
        yield current
    pocket = in_gap(current, a - 3, a + 1)
    spiral = in_gap(current, a - 2, a + 3)
    yield pocket
    yield spiral
    if not delayed:
        yield in_gap(pocket, a, a - 1)
        spiral = in_gap(spiral, a - 1, a + 2)
        yield spiral
        yield in_gap(spiral, a, a + 1)


def _outer(prefix: Order, a: int, r: int) -> Iterator[Order]:
    yield from _outer_descent(prefix, a, r, delayed=False)
    outside = adjacent(prefix, "M")
    yield outside
    for k in range(2, r + 1):
        if k == 4:
            delayed = in_gap(outside, a + r - 3, a + r + 1)
            yield delayed
            yield from _outer_descent(delayed, a, r, delayed=True)
        outside = outward_mountain(outside)
        yield outside


def completions(a: int, r: int, family: str) -> Iterator[Order]:
    prefixes = stopped_prefixes(a, r)
    if family not in prefixes:
        raise ValueError("this prefix family does not exist at these lengths")
    prefix = prefixes[family]
    open_orders = (_outer(prefix, a, r) if family == "outer" else
                   _direct_or_return(prefix, a, r, family == "direct"))
    for order in open_orders:
        yield nest(order, a + 2 * r + 1 - len(order), "M")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mountains", type=int)
    parser.add_argument("stop", type=int)
    parser.add_argument("--verify", action="store_true", help="recheck every final order")
    args = parser.parse_args()
    a, r = args.mountains, args.stop
    try:
        prefixes = stopped_prefixes(a, r)
    except ValueError as error:
        parser.error(str(error))
    for family, prefix in prefixes.items():
        orders = list(completions(a, r, family))
        print(f"{family}: {len(orders)} labeled completions")
        if args.verify:
            from reconstruction import extend
            direct = set(extend(prefix, "M" * a + "V" * r + "M" * r))
            if len(orders) != len(direct) or set(orders) != direct:
                raise AssertionError((a, r, family, "labeled orders differ"))
    if args.verify:
        print("All constructed sets agree with the independent matching checker.")


if __name__ == "__main__":
    main()
