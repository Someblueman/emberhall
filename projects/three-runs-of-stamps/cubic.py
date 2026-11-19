#!/usr/bin/env python3
"""Count labeled stamp stacks with three equal runs. See cubic.md."""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator

from delayed_escape import Order, direction, extend, nest, put
from escape_chain import recover
from weighted_open import exterior


def matching_walk(order: Order, symbol: str, touched: set[int]) -> Iterator[int]:
    """Yield all legal gaps. Record jump endpoints, barriers and gap neighbors."""
    last = len(order) - 1
    step = direction(last, symbol)
    pos = order.index(last)
    while True:
        gap = pos + int(step > 0)
        touched.update(order[max(0, gap - 1):gap + 1])
        yield gap
        pos += step
        if not 0 <= pos < len(order):
            return
        face = order[pos]
        touched.add(face)
        partner = face + (1 if face % 2 == last % 2 else -1)
        if partner < 0:
            continue
        touched.add(partner)
        other = order.index(partner)
        if (other - pos) * step < 0:
            return
        pos = other


def fourth_weights(a: int, d: int) -> tuple[list[int], set[int]]:
    """Exact r=4 stopped-prefix weights for the two near-end mountain types."""
    if a < 5 or d not in (0, 1):
        raise ValueError("require a >= 5 and d in {0,1}")
    states = [nest(exterior(a - d - 1), d + 1, "M")]
    touched: set[int] = set()
    for step in range(1, 5):
        children = []
        for order in states:
            for j, gap in enumerate(matching_walk(order, "V", touched)):
                if step == 1 or ((j == 0) == (step == 4)):
                    children.append(put(order, gap))
        states = children
    weights = []
    for prefix in states:
        leaves = [prefix]
        for _ in range(4):
            leaves = [put(order, gap) for order in leaves
                      for gap in matching_walk(order, "M", touched)]
        weights.append(len(leaves))
    return sorted(weights), touched


def sectors(k: int) -> dict[int | None, int]:
    """Contribution indexed by the first adjacent valley after step one."""
    if k < 2:
        raise ValueError("the cubic requires k >= 2")
    if k == 2:
        return {2: 5, None: 5}
    totals: dict[int | None, int] = {2: k*k + k + 3}
    for r in range(3, k):
        base = 2*(r - 1)*k + 8*r*r - 27*r + 25
        tails = (k - r)*(k + 2*r - 4)
        totals[r] = base + tails
    totals[k] = 7*k*k - 23*k + 21
    totals[None] = (9*k*k - 19*k + 12)//2
    return totals


def cubic(k: int) -> int:
    if k < 2:
        raise ValueError("the cubic requires k >= 2")
    return (9*k**3 - 25*k*k + 30*k - 12)//2


def enumerate_sectors(k: int) -> Counter[int | None]:
    """Unpruned gap-signature enumeration, classified by deleting larger faces."""
    counts: Counter[int | None] = Counter()
    for order in extend((0,), "M"*k + "V"*k + "M"*k):
        prefix = tuple(face for face in order if face <= 2*k)
        counts[recover(prefix, k, k).stop] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("k", type=int)
    parser.add_argument("--verify", action="store_true",
                        help="enumerate every stack and compare each sector (use small k)")
    args = parser.parse_args()
    try:
        totals = sectors(args.k)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"M^{args.k} V^{args.k} M^{args.k}")
    for stop, count in totals.items():
        print(f"First adjacent valley after step one: {stop or 'never'} | {count}")
    if sum(totals.values()) != cubic(args.k):
        raise AssertionError("sector sum differs from the cubic")
    print(f"{cubic(args.k)} legal labeled stacks")
    if args.verify:
        if enumerate_sectors(args.k) != totals:
            raise AssertionError("unpruned sector counts differ")
        print("Every sector agrees with unpruned enumeration.")


if __name__ == "__main__":
    main()
