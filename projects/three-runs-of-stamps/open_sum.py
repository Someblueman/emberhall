#!/usr/bin/env python3
"""Construct the unclosed middle-valley sector of M^k V^k M^k."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, nest
from weighted_open import exterior, in_gap, outward_mountain


def outward_valley(order: Order) -> Order:
    label = len(order)
    return order + (label,) if label % 2 else (label,) + order


def valley_prefixes(k: int) -> Iterator[tuple[int | None, str, Order]]:
    """Two different endings, identified by whether the final face is exterior."""
    if k < 2:
        raise ValueError("require k >= 2")
    for turn in [None, *range(2, k + 1)]:
        if turn is None:
            start = exterior(k)
            winding = 0
            entry = 3
        else:
            d = k - turn
            start = nest(exterior(turn - 1), d + 1, "M")
            for j in range(1, d + 1):
                start = in_gap(start, k - j + 1, k - j - 1)
            start = in_gap(start, k - d, max(0, k - d - 3))
            winding = d + 1
            entry = d + 4
        inside = None
        outside = start
        for j in range(winding + 1, k + 1):
            if j == entry:
                if turn is None:
                    inside = in_gap(outside, k, k - 2)
                else:
                    inside = in_gap(outside, k + d + 1, k - d - 3)
            elif inside is not None:
                inside = in_gap(inside, k - j + 3, k - j + 1)
            outside = outward_valley(outside)
        yield turn, "outside", outside
        if inside is not None:
            yield turn, "inside", inside


def outside_paths(prefix: Order, k: int, turn: int | None) -> Iterator[Order]:
    """Open mountains following the exterior, the valley spiral or the old core."""
    exterior_path = prefix
    descent = prefix
    core = prefix
    for step in range(1, k + 1):
        h = k - step + 1
        if turn is not None and step == turn:
            parent = exterior_path if turn <= 3 else descent
            core = in_gap(parent, k + h, max(0, k - h - 2))
            yield core
        elif turn is not None and step > turn:
            core = in_gap(core, k + h, k - h - 1)
            yield core
        if step >= 3:
            if step == 3:
                descent = exterior_path
            if turn is None or step < turn:
                descent = in_gap(descent, k + h, k + h + 2)
            else:
                descent = in_gap(descent, k - h - 1, k + h + 2)
            yield descent
        exterior_path = outward_mountain(exterior_path)
        yield exterior_path


def inside_paths(prefix: Order, k: int, turn: int | None) -> Iterator[Order]:
    current = prefix
    if turn is None:
        for step in range(1, k + 1):
            h = k - step + 1
            current = in_gap(current, k + h, k - h + 3) if h >= 3 else outward_mountain(current)
            yield current
        return

    d = k - turn
    for step in range(1, turn - 3):
        h = k - step + 1
        current = in_gap(current, k + h, k - h + 3)
        yield current
    shortcut = current
    for step in range(turn - 3, k - 2):
        h = k - step + 1
        shortcut = in_gap(shortcut, k + h - 4, k - h + 3)
        yield shortcut
    current = in_gap(current, k + d + 1, k + d + 4)
    yield current
    for _ in range(2):
        current = outward_mountain(current)
        yield current
    delayed = in_gap(current, k + d + 1, 2*k + turn - 3)
    yield delayed
    for step in range(turn, k + 1):
        current = outward_mountain(current)
        yield current
        if step > turn:
            h = k - step + 1
            delayed = in_gap(delayed, k + h, k - h - 1)
            yield delayed


def completions(prefix: Order, k: int, turn: int | None, family: str) -> Iterator[Order]:
    if family == "outside":
        open_paths = outside_paths(prefix, k, turn)
    elif family == "inside":
        open_paths = inside_paths(prefix, k, turn)
    else:
        raise ValueError("unknown valley family")
    for order in open_paths:
        yield nest(order, 3*k + 1 - len(order), "M")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("k", type=int)
    parser.add_argument("--verify", action="store_true", help="compare complete labeled sets")
    args = parser.parse_args()
    k = args.k
    if k < 2:
        parser.error("require k >= 2")
    prefixes = total = 0
    for turn, family, prefix in valley_prefixes(k):
        orders = list(completions(prefix, k, turn, family))
        if args.verify:
            from reconstruction import extend
            direct = set(extend(prefix, "M"*k + "V"*k + "M"*k))
            if len(orders) != len(direct) or set(orders) != direct:
                raise AssertionError((turn, family, "labeled orders differ"))
        prefixes += 1
        total += len(orders)
    print(f"M^{k} V^{k} M^{k}, no adjacent valley from step two onward")
    print(f"{prefixes} prefixes, {total} labeled completions")
    if args.verify:
        print("Each constructed completion set agrees with whole-matching enumeration.")


if __name__ == "__main__":
    main()
