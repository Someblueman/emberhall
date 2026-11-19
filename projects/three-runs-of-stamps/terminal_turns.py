#!/usr/bin/env python3
"""Count the three early-turn terminal families; see terminal-turns.md."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, adjacent, direction, nest, put
from reconstruction import extend, legal
from weighted_open import exterior, in_gap


def terminal_prefix(k: int, turn: int) -> tuple[Order, int]:
    """Construct the sole stop-k prefix, and the old boundary face H."""
    if k < 3 or turn not in (2, 3, 4) or turn > k:
        raise ValueError("require k >= 3 and 2 <= turn <= min(4,k)")
    core = exterior(turn - 1)
    prefix = nest(core, k - turn + 1, "M")
    oriented = core[::-1] if turn % 2 == 0 else core
    block = tuple(x for x in oriented if x not in (turn - 2, turn - 1))
    high = block[-1] if block else turn - 2
    for j in range(1, k - turn + 1):
        prefix = in_gap(prefix, k - j + 1, k - j - 1)
    prefix = in_gap(prefix, high, turn)
    for _ in range(turn - 2):
        prefix = outward(prefix, "V")
    return adjacent(prefix, "V"), high


def outward(prefix: Order, symbol: str) -> Order:
    return put(prefix, len(prefix) if direction(len(prefix) - 1, symbol) == 1 else 0)


def open_frontiers(k: int, turn: int) -> Iterator[dict[str, Order]]:
    prefix, high = terminal_prefix(k, turn)

    def gap_g(order: Order, h: int) -> Order:
        return in_gap(order, k + h, k - h + 1)

    def gap_f(order: Order, h: int) -> Order:
        return in_gap(order, k + h, k - h - 1)

    states = {"fast": gap_g(prefix, k - 2), "close": adjacent(prefix, "M")}
    yield states
    for step in range(2, k + 1):
        following = {}
        for route, order in states.items():
            if route == "fast" and step <= k - 2:
                following[route] = gap_g(order, k - step - 1)
            elif route == "close":
                following["escape"] = outward(order, "M")
                if turn == 2:
                    following["middle"] = gap_f(order, k - 1)
            elif route == "middle":
                following[route] = gap_f(order, k - step + 1)
            elif route == "escape":
                following[route] = outward(order, "M")
                if step == turn:
                    following["middle"] = in_gap(order, high, 2 * k - turn + 1)
                if step == 4:
                    following["pocket"] = in_gap(order, 2 * k + 1, 2)
            elif route == "pocket":
                following[route] = gap_g(order, k - step + 3)
        states = following
        yield states


def completion_records(k: int, turn: int) -> Iterator[tuple[tuple[str, int], Order]]:
    for step, frontier in enumerate(open_frontiers(k, turn), 1):
        for route, order in frontier.items():
            yield (route, step), nest(order, k - step, "M")


def recover(order: Order, k: int, turn: int) -> tuple[str, int]:
    prefix, _ = terminal_prefix(k, turn)
    if not legal(order, "M" * k + "V" * k + "M" * k):
        raise ValueError("not a legal complete three-run stack")
    if tuple(x for x in order if x <= 2 * k) != prefix:
        raise ValueError("stack has a different valley prefix")
    step = k
    for j in range(2, k + 1):
        last = 2 * k + j
        small = tuple(x for x in order if x <= last)
        if abs(small.index(last) - small.index(last - 1)) == 1:
            step = j - 1
            break
    partial = tuple(x for x in order if x <= 2 * k + step)
    frontier = next(f for j, f in enumerate(open_frontiers(k, turn), 1) if j == step)
    routes = [route for route, value in frontier.items() if value == partial]
    if len(routes) != 1 or nest(partial, k - step, "M") != order:
        raise ValueError("stack is not represented by a unique construction parameter")
    return routes[0], step


def verify(k: int, turn: int) -> int:
    prefix, _ = terminal_prefix(k, turn)
    records = list(completion_records(k, turn))
    constructed = {s for _, s in records}
    direct = set(extend(prefix, "M" * k + "V" * k + "M" * k))
    if len(constructed) != len(records) or constructed != direct:
        raise AssertionError((k, turn, "complete-set mismatch"))
    if len(records) != 4 * k - turn - 4:
        raise AssertionError((k, turn, "weight mismatch"))
    for parameter, order in records:
        if recover(order, k, turn) != parameter:
            raise AssertionError((k, turn, "inverse mismatch"))
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        terminal_prefix(args.k, 2)
        for turn in range(2, min(4, args.k) + 1):
            records = list(completion_records(args.k, turn))
            if args.verify:
                verify(args.k, turn)
            print(f"turn {turn}: {len(records)} stacks; theorem {4 * args.k - turn - 4}")
            print("open histories:", [len(f) for f in open_frontiers(args.k, turn)])
        if args.verify:
            print("All complete labeled sets and inverse parameters match direct matching-stack enumeration.")
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
