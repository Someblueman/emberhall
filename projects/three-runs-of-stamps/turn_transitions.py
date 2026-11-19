#!/usr/bin/env python3
"""Construct the next two inward-turn rows; see turn-transitions.md."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, adjacent, direction, nest, put
from reconstruction import extend, legal
from weighted_open import exterior, in_gap

KINDS = ("core", "wrap")


def basis(a: int, r: int, offset: int) -> tuple[Order, int, int, int, int, int]:
    """Mountain and the old-core boundary names u,L,H,K,N."""
    if offset not in (3, 4) or r < 5 or a < r + 1:
        raise ValueError("require offset 3 or 4, r >= 5 and a >= r+1")
    turn = a - r + offset
    core = exterior(turn - 1)
    mountain = nest(core, a - turn + 1, "M")
    oriented = core[::-1] if turn % 2 == 0 else core
    block = tuple(x for x in oriented if x not in (turn - 2, turn - 1))
    return mountain, turn - 2, block[0], block[-1], block[-2], block[1]


def outward(prefix: Order, symbol: str) -> Order:
    gap = len(prefix) if direction(len(prefix) - 1, symbol) == 1 else 0
    return put(prefix, gap)


def transition_prefix(a: int, r: int, offset: int, kind: str) -> Order:
    if kind not in KINDS:
        raise ValueError("kind must be core or wrap")
    prefix, u, low, high, penultimate, second = basis(a, r, offset)
    depth = r - offset
    for j in range(1, depth + 1):
        prefix = in_gap(prefix, a - j + 1, a - j - 1)
    if kind == "core":
        prefix = in_gap(prefix, u, low)
        prefix = in_gap(prefix, penultimate, high)
        if offset == 4:
            prefix = in_gap(prefix, low, second)
    else:
        prefix = in_gap(prefix, high, a - depth)
        prefix = outward(prefix, "V")
        if offset == 4:
            prefix = outward(prefix, "V")
    return adjacent(prefix, "V")


def open_frontiers(a: int, r: int, offset: int, kind: str) -> Iterator[dict[str, Order]]:
    """Named-gap construction, independent of the matching-stack search."""
    base = transition_prefix(a, r, offset, kind)
    _, u, low, high, penultimate, _ = basis(a, r, offset)
    depth = r - offset

    def gap_g(prefix: Order, h: int) -> Order:
        return in_gap(prefix, a + h, a - h + 1)

    def gap_f(prefix: Order, h: int) -> Order:
        return in_gap(prefix, a + h, a - h - 1)

    if kind == "core":
        first = (in_gap(base, a + r - 2, low) if offset == 3
                 else in_gap(base, penultimate, a + r - 2))
        states = {"entry": first, "close": adjacent(base, "M")}
    else:
        states = {"fast": gap_g(base, r - 2), "close": adjacent(base, "M")}
    yield states
    for step in range(2, r + 1):
        following = {}
        for route, prefix in states.items():
            if route == "close":
                if kind == "wrap":
                    following["escape"] = outward(prefix, "M")
                else:
                    boundary = high if offset == 3 else low
                    following["middle"] = in_gap(prefix, boundary, a + r - 1)
            elif route == "entry":
                if step == offset - 1:
                    following["fast"] = gap_g(prefix, r - step - 1)
                    following["escape"] = in_gap(prefix, high, a - depth)
                else:
                    following[route] = in_gap(prefix, low, a + r - 3)
            elif route == "fast" and step <= r - 2:
                following[route] = gap_g(prefix, r - step - 1)
            elif route == "middle":
                if kind == "core" and step <= offset:
                    boundary = u if step == offset else high
                    following[route] = in_gap(prefix, boundary, a + r - step + 1)
                else:
                    following[route] = gap_f(prefix, r - step + 1)
            elif route == "escape":
                following[route] = outward(prefix, "M")
                if kind == "wrap":
                    if step == offset:
                        following["middle"] = in_gap(prefix, high, a + r - offset + 1)
                    if step == 4:
                        following["pocket"] = in_gap(prefix, a + r + 1, a - r + 2)
                elif step == offset + 2:
                    following["pocket"] = in_gap(prefix, a + r + offset - 1, a - depth)
            elif route == "pocket":
                following[route] = gap_g(prefix, r - step + 3)
        states = following
        yield states


def completion_records(
    a: int, r: int, offset: int, kind: str
) -> Iterator[tuple[tuple[str, int], Order]]:
    """Every (route,index) selects one open prefix and its forced ending."""
    for step, frontier in enumerate(open_frontiers(a, r, offset, kind), 1):
        for route, prefix in frontier.items():
            yield (route, step), nest(prefix, r - step, "M")


def recover(order: Order, a: int, r: int, offset: int, kind: str) -> tuple[str, int]:
    base = transition_prefix(a, r, offset, kind)
    if not legal(order, "M" * a + "V" * r + "M" * r):
        raise ValueError("not a legal stack of the selected shape")
    if tuple(x for x in order if x <= a + r) != base:
        raise ValueError("stack has a different valley prefix")
    step = r
    for j in range(2, r + 1):
        last = a + r + j
        partial = tuple(x for x in order if x <= last)
        if abs(partial.index(last) - partial.index(last - 1)) == 1:
            step = j - 1
            break
    partial = tuple(x for x in order if x <= a + r + step)
    frontier = next(f for j, f in enumerate(open_frontiers(a, r, offset, kind), 1) if j == step)
    routes = [route for route, prefix in frontier.items() if prefix == partial]
    if len(routes) != 1 or nest(partial, r - step, "M") != order:
        raise ValueError("stack is outside the constructive parameterization")
    return routes[0], step


def expected_weight(r: int, offset: int, kind: str) -> int:
    if r < 5 or offset not in (3, 4) or kind not in KINDS:
        raise ValueError("require offset 3 or 4, r >= 5 and kind core or wrap")
    return 4 * r - (7 if offset == 3 else 9 if kind == "core" else 8)


def verify(a: int, r: int, offset: int, kind: str) -> int:
    prefix = transition_prefix(a, r, offset, kind)
    records = list(completion_records(a, r, offset, kind))
    constructed = {stack for _, stack in records}
    direct = set(extend(prefix, "M" * a + "V" * r + "M" * r))
    if len(records) != len(constructed) or constructed != direct:
        raise AssertionError((a, r, offset, kind, "complete-set mismatch"))
    if len(records) != expected_weight(r, offset, kind):
        raise AssertionError((a, r, offset, kind, "weight mismatch"))
    for parameter, stack in records:
        if recover(stack, a, r, offset, kind) != parameter:
            raise AssertionError((a, r, offset, kind, "inverse mismatch"))
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mountains", type=int, default=9)
    parser.add_argument("--stop", type=int, default=8)
    parser.add_argument("--offset", type=int, choices=(3, 4), default=3)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        for kind in KINDS:
            records = list(completion_records(args.mountains, args.stop, args.offset, kind))
            if args.verify:
                verify(args.mountains, args.stop, args.offset, kind)
            print(f"offset {args.offset}, {kind}: {len(records)} stacks; "
                  f"theorem {expected_weight(args.stop, args.offset, kind)}")
            print("open histories:", [len(f) for f in open_frontiers(
                args.mountains, args.stop, args.offset, kind)])
        if args.verify:
            print("Complete labeled sets and both inverse maps match direct matching-stack enumeration.")
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
