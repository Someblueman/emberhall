#!/usr/bin/env python3
"""Construct the stopped deep-turn family using the gaps proved in deep-turn.md."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, adjacent, nest
from weighted_open import exterior, in_gap


def stopped_prefix(a: int, turn: int, stop: int) -> Order:
    if not 2 <= turn <= a or not 2 <= stop <= a - turn + 1:
        raise ValueError("require turn >= 2, stop >= 2 and a - turn >= stop - 1")
    # First choose an inward mountain, then the remaining mountains are forced.
    prefix = nest(exterior(turn - 1), a - turn + 1, "M")
    for j in range(1, stop):
        prefix = in_gap(prefix, a - j + 1, a - j - 1)
    return adjacent(prefix, "V")


def completions(a: int, turn: int, stop: int, length: int) -> Iterator[Order]:
    """Emit each labeled order once, by first branch and first adjacent stop."""
    if length < 0:
        raise ValueError("suffix length must be nonnegative")
    prefix = stopped_prefix(a, turn, stop)
    if length == 0:
        yield prefix
        return

    # The first mountain may go adjacent even on a continuing trajectory.
    near = adjacent(prefix, "M")
    for step in range(2, min(length, stop + 1) + 1):
        yield nest(near, length - step + 1, "M")
        h = stop - step + 1
        near = in_gap(near, a + h, a - h - 1)
    yield nest(near, max(0, length - stop - 1), "M")

    far = prefix
    for step in range(1, min(length, stop - 2) + 1):
        if step > 1:
            yield nest(far, length - step + 1, "M")
        h = stop - step - 1
        far = in_gap(far, a + h, a - h + 1)
    if stop >= 3:
        yield nest(far, max(0, length - stop + 2), "M")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mountains", type=int)
    parser.add_argument("turn", type=int)
    parser.add_argument("stop", type=int)
    parser.add_argument("--suffix", type=int, help="defaults to the valley stop")
    parser.add_argument("--verify", action="store_true", help="compare full labeled sets")
    args = parser.parse_args()
    a, turn, r = args.mountains, args.turn, args.stop
    c = r if args.suffix is None else args.suffix
    try:
        prefix = stopped_prefix(a, turn, r)
        orders = set(completions(a, turn, r, c))
    except ValueError as error:
        parser.error(str(error))
    print(f"M^{a} V^{r} M^{c}, first inward mountain {turn}, first adjacent valley after V1 at {r}")
    print(f"Stopped prefix: {' '.join(map(str, prefix))}")
    print(f"{len(orders)} labeled completions")
    if args.verify:
        from reconstruction import extend
        direct = set(extend(prefix, "M" * a + "V" * r + "M" * c))
        if orders != direct:
            raise AssertionError("constructed and enumerated sets differ")
        print("The independent matching checker returns the same full orders.")


if __name__ == "__main__":
    main()
