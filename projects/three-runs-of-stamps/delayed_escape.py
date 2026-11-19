#!/usr/bin/env python3
"""Exact gap-signature experiments for a delayed valley escape; no dependencies."""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator

Order = tuple[int, ...]


def ranks(order: Order) -> dict[int, int]:
    if not order or sorted(order) != list(range(len(order))):
        raise ValueError("order must contain each face from zero exactly once")
    return {face: at for at, face in enumerate(order)}


def direction(face: int, symbol: str) -> int:
    """Direction of the new face relative to face (left=-1, right=1)."""
    if symbol not in ("M", "V"):
        raise ValueError("a crease must be M or V")
    return -1 if (symbol == "M") == (face % 2 == 0) else 1


def gaps(order: Order, symbol: str) -> Iterator[int]:
    """Sweep interval-membership bits; yield the gaps legal for one new face.

    Every old arc on the new arc's side contributes one bit. Crossing a face
    toggles its arc's bit. A gap is reachable precisely when its bits match
    the current endpoint's bits and its direction is correct.
    """
    at = ranks(order)
    last = len(order) - 1
    toggles = [0] * len(order)
    endpoint_signature = 0
    for edge in range(last % 2, last, 2):
        bit = 1 << (edge // 2)
        lo, hi = sorted((at[edge], at[edge + 1]))
        toggles[lo] ^= bit
        toggles[hi] ^= bit
        if lo < at[last] < hi:
            endpoint_signature |= bit
    step = direction(last, symbol)
    signature = 0
    for gap in range(len(order) + 1):
        if signature == endpoint_signature and ((gap > at[last]) == (step == 1)):
            yield gap
        if gap < len(order):
            signature ^= toggles[gap]


def put(order: Order, gap: int) -> Order:
    return order[:gap] + (len(order),) + order[gap:]


def extend(order: Order, assignment: str) -> Iterator[Order]:
    if any(symbol not in "MV" for symbol in assignment):
        raise ValueError("assignment must contain only M and V")
    if not assignment:
        yield order
    else:
        for gap in gaps(order, assignment[0]):
            yield from extend(put(order, gap), assignment[1:])


def adjacent(order: Order, symbol: str) -> Order:
    """Insert in the adjacent gap on the required side."""
    last = len(order) - 1
    gap = order.index(last) + (direction(last, symbol) == 1)
    return put(order, gap)


def nest(order: Order, number: int, symbol: str = "V") -> Order:
    if number < 0:
        raise ValueError("number of folds cannot be negative")
    for _ in range(number):
        order = adjacent(order, symbol)
    return order


def delayed_prefixes(a: int, b: int, escape: int = 2) -> Iterator[Order]:
    """M^a, escape-th V nonadjacent, all other V insertions adjacent.

    Requires escape >= 2, so these prefixes exclude the first-valley family.
    """
    if a < 2 or b < 2 or not 2 <= escape <= b:
        raise ValueError("require a,b >= 2 and 2 <= escape <= b")
    for mountain in extend((0,), "M" * a):
        before = nest(mountain, escape - 1)
        immediate = adjacent(before, "V")
        for gap in gaps(before, "V"):
            child = put(before, gap)
            if child != immediate:
                yield nest(child, b - escape)


def first_internal(order: Order) -> int | None:
    """First mountain face inserted off the exterior, or None."""
    for face in range(2, len(order)):
        smaller = tuple(x for x in order if x <= face)
        if smaller[0] != face and smaller[-1] != face:
            return face
    return None


def census(a: int, b: int, c: int, escape: int = 2) -> tuple[int, Counter]:
    if c < 0:
        raise ValueError("third-run length cannot be negative")
    totals = Counter()
    count = 0
    for prefix in delayed_prefixes(a, b, escape):
        mountain = tuple(x for x in prefix if x <= a)
        completions = sum(1 for _ in extend(prefix, "M" * c))
        totals[first_internal(mountain)] += completions
        count += 1
    return count, totals


def equal_tail_formula(a: int, b: int) -> int:
    """Author formula for M^a V^b M^b, justified in delayed-escape.md."""
    if a < 2 or b < 2:
        raise ValueError("require a,b >= 2")
    if b == 2:
        return 5 if a == 2 else 9 if a == 3 else 2 * a + 5
    return 2 * b + 3 if a == 2 else 3 * b + 6 if a == 3 else (a + 1) * b + a + 7


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=4, help="equal run length")
    parser.add_argument("--a", type=int, help="mountain-run length")
    parser.add_argument("--b", type=int, help="valley-run length")
    parser.add_argument("--c", type=int, help="final mountain-run length")
    parser.add_argument("--escape", type=int, default=2, help="nonadjacent valley step")
    parser.add_argument("--list", action="store_true", help="print prefixes and completion counts")
    args = parser.parse_args()
    a, b, c = (args.k if value is None else value for value in (args.a, args.b, args.c))
    try:
        prefixes, totals = census(a, b, c, args.escape)
        if args.list:
            for prefix in delayed_prefixes(a, b, args.escape):
                total = sum(1 for _ in extend(prefix, "M" * c))
                print(" ".join(map(str, prefix)), "=>", total)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"M^{a} V^{b} M^{c}; nonadjacent V at step {args.escape}")
    print(f"{prefixes} prefixes; {sum(totals.values())} completions")
    print("by first internal mountain step:", dict(totals))
    if b == c:
        expected = equal_tail_formula(a, b) if args.escape == 2 else 0
        print(f"author formula: {expected} (see delayed-escape.md; independent review pending)")


if __name__ == "__main__":
    main()
