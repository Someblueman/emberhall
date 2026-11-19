#!/usr/bin/env python3
"""Inspect exterior open valley chains with an independent legality checker."""
from __future__ import annotations

import argparse
from collections.abc import Iterator

from reconstruction import Stack, adjacent_valley, extend, legal


def exterior(a: int) -> Stack:
    """The mountain stack whose endpoint stayed exterior at every step."""
    return tuple(range(a if a % 2 else a - 1, 0, -2)) + (0,) + tuple(range(2, a + 1, 2))


def children(prefix: Stack, directions: str) -> Iterator[Stack]:
    """Extend by exactly one crease, checking the full matching."""
    n = len(prefix)
    for gap in range(n + 1):
        child = prefix[:gap] + (n,) + prefix[gap:]
        if legal(child, directions):
            yield child


def open_paths(a: int, depth: int) -> Iterator[Stack]:
    """All exterior-M prefixes with no adjacent V from step two onward."""
    if a < 2 or depth < 1:
        raise ValueError("mountains >= 2 and positive valley depth required")
    frontier = [exterior(a)]
    for step in range(1, depth + 1):
        word = "M" * a + "V" * step
        next_frontier = []
        for prefix in frontier:
            for child in children(prefix, word):
                last = len(child) - 1
                if step == 1 or abs(child.index(last) - child.index(last - 1)) != 1:
                    next_frontier.append(child)
        frontier = next_frontier
    yield from frontier


def stopped_prefixes(a: int, stop: int) -> Iterator[Stack]:
    if stop < 2:
        raise ValueError("first adjacent valley is at least step two")
    for prefix in open_paths(a, stop - 1):
        yield adjacent_valley(prefix)


def weights(a: int, stop: int) -> list[tuple[Stack, int]]:
    word = "M" * a + "V" * stop + "M" * stop
    return [(p, sum(1 for _ in extend(p, word))) for p in stopped_prefixes(a, stop)]


def outer_prefix(a: int, stop: int) -> Stack:
    """All pre-stop valleys go exterior; the final one is adjacent."""
    if a < 2 or stop < 2:
        raise ValueError("both mountain length and stop must be at least two")
    prefix = exterior(a)
    for _ in range(1, stop):
        at = len(prefix) if (len(prefix) - 1) % 2 == 0 else 0
        prefix = prefix[:at] + (len(prefix),) + prefix[at:]
    return adjacent_valley(prefix)


def compress_core(order: Stack, a: int) -> Stack:
    """Delete old interior labels, keeping a-2,a-1,a, and normalize parity.

    This map is only claimed on the outer-prefix family. Its old block
    excluding a must still be consecutive; reject a broken block explicitly.
    """
    if a < 2 or len(order) < a + 1 or set(order) != set(range(len(order))):
        raise ValueError("a complete labeled order and a >= 2 are required")
    block = tuple(x for x in exterior(a) if x != a)
    start = order.index(block[0])
    if order[start:start + len(block)] != block:
        raise ValueError("old mountain core is not an intact block")
    reduced = tuple(x - a + 2 for x in order if x >= a - 2)
    return reduced[::-1] if a % 2 else reduced


def expand_core(order: Stack, a: int) -> Stack:
    """Inverse of compress_core: restore the original exterior spiral block."""
    if a < 2 or len(order) < 3 or set(order) != set(range(len(order))):
        raise ValueError("a complete three-face-core order and a >= 2 are required")
    oriented = order[::-1] if a % 2 else order
    lifted = tuple(x + a - 2 for x in oriented)
    middle = tuple(x for x in exterior(a) if x not in (a - 1, a))
    at = lifted.index(a - 2)
    return lifted[:at] + middle + lifted[at + 1:]


def check_reduction(a: int, stop: int, mountains: int) -> tuple[int, int]:
    if mountains < 0:
        raise ValueError("suffix length cannot be negative")
    large = set(extend(outer_prefix(a, stop), "M" * a + "V" * stop + "M" * mountains))
    small = set(extend(outer_prefix(2, stop), "MM" + "V" * stop + "M" * mountains))
    compressed = {compress_core(order, a) for order in large}
    expanded = {expand_core(order, a) for order in small}
    if compressed != small or expanded != large or len(large) != len(compressed):
        raise AssertionError((a, stop, mountains, "core map mismatch"))
    return len(large), len(small)


def in_gap(prefix: Stack, first: int, second: int) -> Stack:
    """Insert the next label between two specified neighboring labels."""
    i, j = prefix.index(first), prefix.index(second)
    if abs(i - j) != 1:
        raise AssertionError((prefix, first, second, "not a gap"))
    at = max(i, j)
    return prefix[:at] + (len(prefix),) + prefix[at:]


def outward_mountain(prefix: Stack) -> Stack:
    at = len(prefix) if (len(prefix) - 1) % 2 else 0
    return prefix[:at] + (len(prefix),) + prefix[at:]


def adjacent_mountain(prefix: Stack) -> Stack:
    last = len(prefix) - 1
    at = prefix.index(last) + (last % 2 == 1)
    return prefix[:at] + (last + 1,) + prefix[at:]


def outer_open_frontiers(stop: int) -> Iterator[dict[str, Stack]]:
    """Construct the proved nonadjacent M trajectories, without legality search.

    Labels x_j=2+j are old valley faces; y_j=2+stop+j are new mountain
    faces. The small stops 2..6 are separate bases, not this generic table.
    """
    if stop < 7:
        raise ValueError("the uniform trajectory table requires stop >= 7")
    base = outer_prefix(2, stop)
    x = lambda j: j + 2
    states = {
        "fast": in_gap(base, x(stop - 2), x(stop - 4)),
        "start": in_gap(base, x(stop - 3), x(stop)),
    }
    yield states
    for step in range(2, stop + 1):
        next_states = {}
        for kind, prefix in states.items():
            if kind == "fast":
                if step <= stop - 4:
                    next_states[kind] = in_gap(prefix, x(stop-step-1), x(stop-step-3))
                elif step == stop - 3:
                    next_states["core-left"] = in_gap(prefix, x(2), 1)
                    next_states["core-middle"] = in_gap(prefix, 0, 2)
            elif kind == "core-left" and step == stop - 2:
                next_states["core-exit"] = in_gap(prefix, 2, x(1))
            elif kind == "start":
                if step <= 3:
                    next_states[kind] = outward_mountain(prefix)
                elif step == 4:
                    next_states["slow"] = in_gap(prefix, x(stop - 3), stop + 3)
                    next_states["outer"] = outward_mountain(prefix)
            elif kind == "slow":
                j = step - 4
                next_states[kind] = in_gap(prefix, x(stop-j-1), x(stop-j-3))
            elif kind == "outer":
                next_states[kind] = outward_mountain(prefix)
        states = next_states
        yield states


def outer_constructed(stop: int) -> set[Stack]:
    """Full diagonal completions from first-stop labels and the gap table."""
    frontiers = list(outer_open_frontiers(stop))
    result = set(frontiers[-1].values())
    for frontier in frontiers[:-1]:
        for prefix in frontier.values():
            # Once two consecutive mountains are adjacent, all later ones
            # are forced to take the adjacent gap.
            while len(prefix) < 3 + 2*stop:
                prefix = adjacent_mountain(prefix)
            result.add(prefix)
    return result


def region_boundary(order: Stack) -> tuple[int | None, tuple[int, ...]]:
    """Nearest same-side enclosing arc and maximal children in the next direction.

    This is a direct interval calculation for checking the proof's boundary
    table, independent of the matching-stack legality predicate.
    """
    last = len(order) - 1
    rank = {face: i for i, face in enumerate(order)}
    at = rank[last]
    arcs = []
    for edge in range(last % 2, last, 2):
        left, right = sorted((rank[edge], rank[edge + 1]))
        arcs.append((left, right, edge))
    enclosing = [arc for arc in arcs if arc[0] < at < arc[1]]
    parent = min(enclosing, key=lambda arc: arc[1] - arc[0]) if enclosing else (
        -1, len(order), None)
    candidates = [arc for arc in arcs
                  if parent[0] <= arc[0] and arc[1] <= parent[1]
                  and not arc[0] < at < arc[1]]
    children_here = [arc for arc in candidates if not any(
        other[0] < arc[0] < arc[1] < other[1] for other in candidates)]
    rightward = bool(last % 2)
    ahead = [arc for arc in children_here if (arc[0] > at if rightward else arc[1] < at)]
    return parent[2], tuple(arc[2] for arc in sorted(ahead))


def inner_prefix(a: int, stop: int) -> Stack:
    """Enter the old mountain spiral at the third V; stop before its core."""
    if stop < 4 or a < stop + 1:
        raise ValueError("the inner table requires stop >= 4 and mountains >= stop+1")
    prefix = exterior(a)
    for _ in range(2):
        at = len(prefix) if (len(prefix) - 1) % 2 == 0 else 0
        prefix = prefix[:at] + (len(prefix),) + prefix[at:]
    for step in range(3, stop):
        prefix = in_gap(prefix, a-step+1, a-step+3)
    return adjacent_valley(prefix)


def inner_open_frontiers(a: int, stop: int) -> Iterator[dict[str, Stack]]:
    """Two explicit interleaved paths, with only the first surviving at the end."""
    base = inner_prefix(a, stop)
    states = {
        "first": in_gap(base, a+stop, a-stop+2),
        "second": in_gap(base, a-stop+3, a+stop-2),
    }
    yield states
    for step in range(2, stop + 1):
        next_states = {}
        for kind, prefix in states.items():
            if step <= stop - 2:
                valley = a+stop-step+(1 if kind == "first" else -1)
                next_states[kind] = in_gap(prefix, a-stop+step+2, valley)
            elif kind == "first":
                next_states[kind] = outward_mountain(prefix)
        states = next_states
        yield states


def inner_constructed(a: int, stop: int) -> set[Stack]:
    frontiers = list(inner_open_frontiers(a, stop))
    result = set(frontiers[-1].values())
    for frontier in frontiers[:-1]:
        for prefix in frontier.values():
            while len(prefix) < a + 2*stop + 1:
                prefix = adjacent_mountain(prefix)
            result.add(prefix)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mountains", type=int, default=8)
    parser.add_argument("--stop", type=int, default=5)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--inner", action="store_true", help="compare the proved inner trajectory table")
    mode.add_argument("--table", action="store_true", help="compare the proved outer trajectory table")
    mode.add_argument("--outer", action="store_true", help="check the exterior-core bijection")
    parser.add_argument("--suffix", type=int, help="mountain suffix for --outer; default is --stop")
    args = parser.parse_args()
    if args.suffix is not None and not args.outer:
        parser.error("--suffix requires --outer")
    try:
        if args.inner:
            constructed = inner_constructed(args.mountains, args.stop)
            counted = set(extend(inner_prefix(args.mountains, args.stop),
                                 "M"*args.mountains + "V"*args.stop + "M"*args.stop))
            if constructed != counted:
                raise AssertionError("inner table differs from exhaustive enumeration")
            print(f"{len(constructed)} stacks; proved inner weight: {2*args.stop-2}")
            return
        if args.table:
            constructed = outer_constructed(args.stop)
            counted = set(extend(outer_prefix(2, args.stop), "MM" + "V"*args.stop + "M"*args.stop))
            if constructed != counted:
                raise AssertionError("trajectory table differs from exhaustive enumeration")
            print(f"{len(constructed)} stacks; proved exterior weight: {3*args.stop-4}")
            print("Constructive table and independent exhaustive sets agree.")
            return
        if args.outer:
            suffix = args.stop if args.suffix is None else args.suffix
            large, small = check_reduction(args.mountains, args.stop, suffix)
            print(f"{args.mountains}-mountain core: {large}; two-mountain core: {small}")
            print("The actual deletion and expansion maps agree on these complete sets.")
            return
        rows = weights(args.mountains, args.stop)
    except ValueError as exc:
        parser.error(str(exc))
    for prefix, total in rows:
        print(f"{total} completions: {' '.join(map(str, prefix))}")
    print("Exact finite counts; any arbitrary-length formula needs a proof.")


if __name__ == "__main__":
    main()
