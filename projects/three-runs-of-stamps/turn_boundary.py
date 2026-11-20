#!/usr/bin/env python3
"""Construct the first turn-boundary family; see turn-boundary.md."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from delayed_escape import Order, adjacent, nest
from reconstruction import extend, legal
from weighted_open import exterior, in_gap, outward_mountain

KINDS = ("inside", "outside")


def mountain_core(a: int, r: int) -> tuple[Order, int, int, int]:
    """Return mountain, u, L, H in the proof's reflected coordinates.

    Only the names L,H depend on reflection: all returned stacks remain in
    the original labeled orientation. No legality search selects these faces.
    """
    if r < 3 or a < r + 1:
        raise ValueError("require r >= 3 and a >= r+1")
    turn = a - r + 2
    core = exterior(turn - 1)
    mountain = nest(core, a - turn + 1, "M")
    oriented = core[::-1] if turn % 2 == 0 else core
    block = tuple(x for x in oriented if x not in (turn - 2, turn - 1))
    return mountain, turn - 2, block[0], block[-1]


def boundary_prefix(a: int, r: int, kind: str) -> Order:
    """Build one of the two prefixes stopping at valley r, without search."""
    if kind not in KINDS:
        raise ValueError("kind must be inside or outside")
    prefix, u, low, high = mountain_core(a, r)
    for j in range(1, r - 1):
        prefix = in_gap(prefix, a - j + 1, a - j - 1)
    endpoints = (u, low) if kind == "inside" else (high, a - r + 2)
    return adjacent(in_gap(prefix, *endpoints), "V")


def open_frontiers(a: int, r: int, kind: str) -> Iterator[dict[str, Order]]:
    """All suffix histories with no adjacent M after the first M.

    Branches use only the named gaps in the theorem, never a legality sweep.
    The initial adjacent M is allowed; adjacency traps only from M2 onward.
    """
    base = boundary_prefix(a, r, kind)
    _, u, _, high = mountain_core(a, r)
    x = lambda j: a + j
    v = lambda j: a - j
    states = {
        "fast": in_gap(base, x(r - 2), v(r - 3)),
        "close": adjacent(base, "M"),
    }
    if kind == "inside":
        states["escape"] = in_gap(base, high, v(r - 2))
    yield states
    for step in range(2, r + 1):
        following = {}
        for route, prefix in states.items():
            if route == "fast" and step <= r - 2:
                h = r - step - 1
                following[route] = in_gap(prefix, x(h), v(h - 1))
            elif route == "close":
                boundary = u if kind == "inside" else high
                following["middle"] = in_gap(prefix, boundary, x(r - 1))
                if kind == "outside":
                    following["escape"] = outward_mountain(prefix)
            elif route == "middle":
                h = r - step + 1
                following[route] = in_gap(prefix, x(h), v(h + 1))
            elif route == "escape":
                following[route] = outward_mountain(prefix)
                if step == 4:
                    following["pocket"] = in_gap(prefix, a + r + 1, v(r - 2))
            elif route == "pocket":
                h = r - step + 3
                following[route] = in_gap(prefix, x(h), v(h - 1))
        states = following
        yield states


def completion_records(a: int, r: int, kind: str) -> Iterator[tuple[tuple[str, int], Order]]:
    """Parametrize every completion by (route, first-closing index).

    Index r means no adjacent M2,...,Mr. Otherwise the first adjacent
    insertion is at index+1; every later insertion is forced.
    """
    for step, frontier in enumerate(open_frontiers(a, r, kind), 1):
        for route, prefix in frontier.items():
            yield (route, step), nest(prefix, r - step, "M")


def recover(order: Order, a: int, r: int, kind: str) -> tuple[str, int]:
    """Recover a construction parameter from a legal complete family member."""
    base = boundary_prefix(a, r, kind)
    word = "M" * a + "V" * r + "M" * r
    if not legal(order, word) or tuple(x for x in order if x <= a + r) != base:
        raise ValueError("not a legal completion of the selected prefix")
    step = r
    for j in range(2, r + 1):
        label = a + r + j
        small = tuple(x for x in order if x <= label)
        if abs(small.index(label) - small.index(label - 1)) == 1:
            step = j - 1
            break
    partial = tuple(x for x in order if x <= a + r + step)
    frontier = next(f for j, f in enumerate(open_frontiers(a, r, kind), 1) if j == step)
    routes = [route for route, value in frontier.items() if value == partial]
    if len(routes) != 1 or nest(partial, r - step, "M") != order:
        raise ValueError("completion does not match the constructive inverse")
    return routes[0], step


def compress_core(order: Order, a: int, r: int) -> Order:
    """Delete the protected exterior interior, obtaining the a=r+1 core.

    Domain: a boundary-family prefix or completion with its old R block
    intact. This checks the block, not the full crease assignment.
    """
    mountain_core(a, r)
    delta = a - r - 1
    turn = delta + 3
    block = tuple(x for x in exterior(turn - 1) if x < turn - 2)
    if sorted(order) != list(range(len(order))):
        raise ValueError("order must contain all consecutive face labels")
    if not all(face in order for face in block):
        raise ValueError("missing protected core")
    at = order.index(block[0])
    if order[at:at + len(block)] != block:
        raise ValueError("protected core is not an intact block")
    reduced = tuple(x - delta for x in order if x >= delta)
    return reduced[::-1] if turn % 2 == 0 else reduced


def expand_core(order: Order, a: int, r: int) -> Order:
    """Inverse core map, restoring the actual labeled exterior block."""
    mountain_core(a, r)
    delta = a - r - 1
    turn = delta + 3
    if sorted(order) != list(range(len(order))) or len(order) < r + 2:
        raise ValueError("a complete smaller-core order is required")
    oriented = order[::-1] if turn % 2 == 0 else order
    lifted = tuple(x + delta for x in oriented)
    block = tuple(x for x in exterior(turn - 1) if x < turn - 2)
    at = lifted.index(delta)
    return lifted[:at] + block + lifted[at + 1:]


def expected_weight(r: int, kind: str) -> int:
    if r < 3 or kind not in KINDS:
        raise ValueError("require r >= 3 and kind inside or outside")
    return 4 * r - (5 if kind == "inside" else 6)


def verify(a: int, r: int, kind: str) -> int:
    """Compare complete labeled sets and inverse with a separate stack search."""
    prefix = boundary_prefix(a, r, kind)
    records = list(completion_records(a, r, kind))
    constructed = {stack for _, stack in records}
    direct = set(extend(prefix, "M" * a + "V" * r + "M" * r))
    if constructed != direct or len(records) != len(constructed):
        raise AssertionError((a, r, kind, "complete-set or injectivity mismatch"))
    if len(constructed) != expected_weight(r, kind):
        raise AssertionError((a, r, kind, "weight mismatch"))
    for parameter, stack in records:
        if recover(stack, a, r, kind) != parameter:
            raise AssertionError((a, r, kind, "inverse mismatch"))
    return len(constructed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mountains", type=int, default=8)
    parser.add_argument("--stop", type=int, default=7)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--list", action="store_true", help="print construction parameters and stacks")
    args = parser.parse_args()
    try:
        mountain_core(args.mountains, args.stop)
        for kind in KINDS:
            records = list(completion_records(args.mountains, args.stop, kind))
            if args.verify:
                verify(args.mountains, args.stop, kind)
            print(f"{kind}: {len(records)} stacks; theorem {expected_weight(args.stop, kind)}")
            print("open histories:", [len(f) for f in open_frontiers(args.mountains, args.stop, kind)])
            if args.list:
                for parameter, stack in records:
                    print(parameter, *stack)
        if args.verify:
            print("Both complete labeled sets and their inverses match direct matching-stack enumeration.")
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
