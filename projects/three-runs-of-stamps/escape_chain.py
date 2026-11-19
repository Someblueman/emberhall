#!/usr/bin/env python3
"""Exact first-adjacent-valley decomposition; see escape-chain.md."""
from __future__ import annotations

import argparse
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass

from delayed_escape import Order, adjacent, extend, first_internal, gaps, nest, put, ranks


@dataclass(frozen=True)
class Chain:
    prefix: Order
    stop: int | None
    tail: int

    def expand(self) -> Order:
        return nest(self.prefix, self.tail)


def chains(a: int, b: int) -> Iterator[Chain]:
    """Retain only nonadjacent branches; collapse each trapped tail once."""
    if a < 2 or b < 2:
        raise ValueError("require a,b >= 2")

    def visit(prefix: Order, step: int) -> Iterator[Chain]:
        if step == b:
            yield Chain(prefix, None, 0)
            return
        stopped = adjacent(prefix, "V")
        for gap in gaps(prefix, "V"):
            child = put(prefix, gap)
            if child == stopped:
                yield Chain(child, step + 1, b - step - 1)
            else:
                yield from visit(child, step + 1)

    for mountain in extend((0,), "M" * a):
        for gap in gaps(mountain, "V"):
            yield from visit(put(mountain, gap), 1)


def recover(order: Order, a: int, b: int) -> Chain:
    """Inverse on legal M^a V^b orders; recover first adjacent V after V1."""
    ranks(order)
    if a < 2 or b < 2 or len(order) != a + b + 1:
        raise ValueError("expected a full two-run order with a,b >= 2")
    for step in range(2, b + 1):
        last = a + step
        small = tuple(x for x in order if x <= last)
        if abs(small.index(last) - small.index(last - 1)) == 1:
            chain = Chain(small, step, b - step)
            if chain.expand() != order:
                raise ValueError("order violates the forced-tail invariant")
            return chain
    return Chain(order, None, 0)


def report(a: int, b: int) -> dict[int | None, dict[str, int]]:
    """Sum exact base completions and one-per-layer collar contributions."""
    buckets = defaultdict(lambda: {"prefixes": 0, "base": 0, "tail": 0, "total": 0})
    for chain in chains(a, b):
        length = b if chain.stop is None else chain.stop
        base = sum(1 for _ in extend(chain.prefix, "M" * length))
        bucket = buckets[chain.stop]
        bucket["prefixes"] += 1
        bucket["base"] += base
        bucket["tail"] += chain.tail
        bucket["total"] += base + chain.tail
    return dict(buckets)


def conjectured_bases(k: int) -> dict[int | None, int]:
    """Unproved weighted counts, retained as explicit targets, not counting code."""
    if k < 3:
        raise ValueError("weighted conjectures are stated only for k >= 3")
    return {2: 2*k + 5,
            **{r: 2*(r-1)*k + 8*r*r - 27*r + 25 for r in range(3, k)},
            k: 7*k*k - 23*k + 21,
            None: (9*k*k - 19*k + 12)//2}


def stop_weights(a: int, r: int) -> dict[int | None, list[tuple[Order, int]]]:
    """Retain each stop-r prefix and weight, grouped by its mountain turn."""
    weights = defaultdict(list)
    for chain in chains(a, r):
        if chain.stop == r:
            mountain = tuple(x for x in chain.prefix if x <= a)
            weight = sum(1 for _ in extend(chain.prefix, "M" * r))
            weights[first_internal(mountain)].append((chain.prefix, weight))
    return dict(weights)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=4, help="equal run lengths")
    parser.add_argument("--a", type=int, help="initial mountain length")
    parser.add_argument("--b", type=int, help="both remaining run lengths")
    parser.add_argument("--verify", action="store_true", help="compare every reduced count with direct extension")
    parser.add_argument("--screen", action="store_true", help="display residuals against unproved weighted formulas (equal runs, k>=3)")
    parser.add_argument("--by-turn", action="store_true", help="show each stop-b prefix and its weight, grouped by first inward mountain")
    args = parser.parse_args()
    a = args.k if args.a is None else args.a
    b = args.k if args.b is None else args.b
    try:
        if args.screen and (a != b or a < 3):
            raise ValueError("--screen requires equal run lengths of at least 3")
        rows = report(a, b)
        if args.verify:
            for chain in chains(a, b):
                length = b if chain.stop is None else chain.stop
                reduced = sum(1 for _ in extend(chain.prefix, "M" * length)) + chain.tail
                direct = sum(1 for _ in extend(chain.expand(), "M" * b))
                if reduced != direct:
                    raise ValueError(f"tail reduction failed for {chain}")
    except ValueError as exc:
        parser.error(str(exc))
    print(f"M^{a} V^{b} M^{b}: exact decomposition, no fitted formula")
    print("first adjacent V | prefixes | base completions | tail bonus | total")
    for stop in sorted(rows, key=lambda x: b + 1 if x is None else x):
        row = rows[stop]
        label = "none" if stop is None else str(stop)
        print(f"{label:>16} | {row['prefixes']:8} | {row['base']:16} | {row['tail']:10} | {row['total']:5}")
    print(f"total: {sum(row['prefixes'] for row in rows.values())} prefixes; "
          f"{sum(row['total'] for row in rows.values())} completions")
    if args.verify:
        print("Every tail reduction agrees with direct extension.")
    if args.screen:
        residuals = {r: rows[r]['base'] - value for r, value in conjectured_bases(a).items()}
        print("Unproved weighted-formula residuals (enumerated minus conjectured):", residuals)
    if args.by_turn:
        weights = stop_weights(a, b)
        print(f"Stop-{b} base cases by first internal mountain step:")
        for turn in sorted(weights, key=lambda x: a + 1 if x is None else x):
            for prefix, weight in weights[turn]:
                print("exterior" if turn is None else turn, ":", *prefix, "=>", weight)


if __name__ == "__main__":
    main()
