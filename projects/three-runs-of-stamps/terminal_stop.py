#!/usr/bin/env python3
"""Complete terminal-stop census for three equal runs. See terminal-stop.md."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, adjacent, extend, nest
from open_sum import inside_paths, valley_prefixes
from weighted_open import in_gap, outward_mountain


def terminal_prefixes(k: int) -> Iterator[tuple[int | None, str, Order, Order]]:
    """Keep one open witness for each distinct prefix stopped at valley k."""
    found = set()
    for turn, family, witness in valley_prefixes(k):
        stopped = adjacent(tuple(i for i in witness if i != 2*k), "V")
        if stopped not in found:
            found.add(stopped)
            yield turn, family, stopped, witness


def _inside(prefix: Order, witness: Order, k: int, turn: int | None) -> Iterator[Order]:
    # Move the final valley and first mountain as a consecutive pair. Later
    # open steps of the adjacent branch never split either of these gaps.
    near = adjacent(prefix, "M")
    pair = (2*k + 1, 2*k)  # even crease 2k points left
    first, second = 2, 2*k - 1  # q_(k-2), x_(k-1)
    if near.index(first) > near.index(second):
        first, second = second, first
    for order in inside_paths(witness, k, turn):
        at = order.index(pair[0])
        if order[at:at+2] != pair:
            raise AssertionError("open history split the moving pair")
        rest = order[:at] + order[at+2:]
        slot = rest.index(second)
        if slot == 0 or rest[slot-1] != first:
            raise AssertionError("open history entered the destination gap")
        yield rest[:slot] + pair + rest[slot:]
    far = prefix
    for s in range(1, k - 1):
        h = k - s + 1
        far = in_gap(far, k - h + 3, k + h - 2)
        yield far


def _descent(prefix: Order, k: int, turn: int, start: int, end: int) -> Iterator[Order]:
    # The virtual step j is four higher for the early descent. Its two
    # trajectories enter neighboring gaps at the old mountain turn.
    winding = prefix
    core = prefix
    for j in range(start, end + 1):
        h = k - j + 1
        if j == turn:
            core = in_gap(winding, k + h, k - h - 2)
            yield core
        elif j > turn and h >= 0:
            core = in_gap(core, k + h, k - h - 1)
            yield core
        if j < turn:
            winding = in_gap(winding, k + h, k + h + 2)
        else:
            winding = in_gap(winding, k - h - 1, k + h + 2)
        yield winding


def _outside(prefix: Order, k: int, turn: int) -> Iterator[Order]:
    # From the first mountain we can descend straightaway, or spend four
    # steps outside then reach the same old gaps with a shorter horizon.
    yield from _descent(prefix, k, turn, 5, k + 2)
    exterior = adjacent(prefix, "M")
    yield exterior
    for s in range(2, k + 1):
        if s == 4:
            delayed = in_gap(exterior, 2*k - 3, 2*k + 1)
            yield delayed
            yield from _descent(delayed, k, turn, 5, k)
        exterior = outward_mountain(exterior)
        yield exterior


def completions(k: int, turn: int | None, family: str, prefix: Order,
                witness: Order) -> Iterator[Order]:
    if k < 5 or (turn is not None and turn < 5) or (turn is None and family == "outside"):
        # Independent components in the proof. Enumerating their actual gaps
        # keeps the command runnable before the other builder's files arrive.
        yield from extend(prefix, "M"*k)
        return
    paths = (_inside(prefix, witness, k, turn) if family == "inside" else
             _outside(prefix, k, turn))
    for order in paths:
        yield nest(order, 3*k + 1 - len(order), "M")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("k", type=int)
    parser.add_argument("--verify", action="store_true", help="compare the full labeled sets")
    args = parser.parse_args()
    k = args.k
    if k < 2:
        parser.error("require k >= 2")
    count = total = 0
    for turn, family, prefix, witness in terminal_prefixes(k):
        orders = list(completions(k, turn, family, prefix, witness))
        if args.verify:
            from reconstruction import extend as matching
            direct = set(matching(prefix, "M"*k + "V"*k + "M"*k))
            if set(orders) != direct or len(orders) != len(direct):
                raise AssertionError((k, turn, family, "labeled sets differ"))
        count += 1
        total += len(orders)
    print(f"M^{k} V^{k} M^{k}, first adjacent valley after V1 at step {k}")
    print(f"{count} prefixes, {total} labeled completions")
    if args.verify:
        print("Each terminal prefix has the same endings under whole-matching enumeration.")


if __name__ == "__main__":
    main()
