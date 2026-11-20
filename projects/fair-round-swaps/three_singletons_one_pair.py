"""Exact five-good EF1 graph for three singletons and one pair recipient.

The complete weak-order census is an exhaustive finite proof obligation,
not a sample. See THREE_SINGLETONS_ONE_PAIR.md for the ordinal reduction.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from time import monotonic

SINGLES = tuple(permutations(range(5), 3))
PAIRS = tuple(tuple(g for g in range(5) if g not in single) for single in SINGLES)
STATES = tuple(tuple(single.index(g) if g in single else 3 for g in range(5))
               for single in SINGLES)
INDEX = {state: i for i, state in enumerate(STATES)}


def _neighbors(state: tuple[int, ...]) -> int:
    bits = 0
    for a, b in combinations(range(5), 2):
        if state[a] != state[b]:
            nxt = list(state)
            nxt[a], nxt[b] = nxt[b], nxt[a]
            bits |= 1 << INDEX[tuple(nxt)]
    return bits


NEIGHBORS = tuple(_neighbors(state) for state in STATES)
SHARP_PROFILE = ((3, 1, 2, 4, 5), (1, 4, 5, 2, 3), (4, 3, 5, 2, 1), (1, 2, 3, 4, 5))
SHARP_START = (0, 3, 1, 2, 3)
SHARP_TARGET = (0, 2, 3, 3, 1)


def row_mask(row: tuple, singleton: int) -> int:
    return sum(1 << i for i, (single, pair) in enumerate(zip(SINGLES, PAIRS))
               if row[single[singleton]] >= min(row[g] for g in pair))


def fair_mask(profile: tuple[tuple, ...]) -> int:
    if (len(profile) != 4 or any(len(row) != 5 for row in profile)
            or any(type(v) not in (int, Fraction) or v < 0 for row in profile for v in row)):
        raise ValueError("need four rows of five exact nonnegative values")
    return row_mask(profile[0], 0) & row_mask(profile[1], 1) & row_mask(profile[2], 2)


@lru_cache(maxsize=65536)
def component_masks(mask: int) -> tuple[int, ...]:
    """All components in the induced graph, with bounded memoization only."""
    if type(mask) is not int or mask < 0 or mask >> 60:
        raise ValueError("mask must be a subset of the sixty allocation states")
    components = []
    while mask:
        frontier = mask & -mask
        reached = 0
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            if reached & bit:
                continue
            reached |= bit
            frontier |= NEIGHBORS[bit.bit_length() - 1] & mask & ~reached
        components.append(reached)
        mask &= ~reached
    return tuple(components)


def path(profile: tuple[tuple, ...], start: tuple[int, ...],
         target: tuple[int, ...]) -> tuple[tuple[int, ...], ...] | None:
    mask = fair_mask(profile)
    if start not in INDEX or target not in INDEX:
        raise ValueError("endpoints must have sizes (1,1,1,2)")
    a, b = INDEX[start], INDEX[target]
    if not (mask & (1 << a) and mask & (1 << b)):
        raise ValueError("endpoints must be EF1")
    previous, queue = {a: None}, deque([a])
    while queue and b not in previous:
        i = queue.popleft()
        neighbors = NEIGHBORS[i] & mask
        while neighbors:
            bit = neighbors & -neighbors
            neighbors ^= bit
            j = bit.bit_length() - 1
            if j not in previous:
                previous[j] = i
                queue.append(j)
    if b not in previous:
        return None
    route, i = [], b
    while i is not None:
        route.append(STATES[i])
        i = previous[i]
    return tuple(route[::-1])


def diameter(mask: int) -> tuple[int, int, int]:
    """Exact diameter and a witnessing pair of vertex indices of a connected graph."""
    if not mask or len(component_masks(mask)) != 1:
        raise ValueError("diameter requires a nonempty connected induced graph")
    first = (mask & -mask).bit_length() - 1
    best = (0, first, first)
    starts = mask
    while starts:
        bit = starts & -starts
        starts ^= bit
        source = bit.bit_length() - 1
        reached, frontier, distance = 0, bit, -1
        last = bit
        while frontier:
            distance += 1
            reached |= frontier
            last, following = frontier, 0
            while frontier:
                item = frontier & -frontier
                frontier ^= item
                following |= NEIGHBORS[item.bit_length() - 1]
            frontier = following & mask & ~reached
        if distance > best[0]:
            best = (distance, source, (last & -last).bit_length() - 1)
    return best


def weak_orders() -> tuple[tuple[int, ...], ...]:
    """All dense weak ranks on five labelled goods, including all ties."""
    return tuple(row for row in product(range(5), repeat=5)
                 if set(row) == set(range(max(row) + 1)))


def canonical_first_rows() -> tuple[tuple[int, ...], ...]:
    rows = []
    for increments in product((0, 1), repeat=4):
        row = [0]
        for step in increments:
            row.append(row[-1] + step)
        rows.append(tuple(row))
    return tuple(rows)


def census(seconds: float = 600, *, diameters: bool = False) -> dict:
    """Stop at a full-graph obstruction, a deadline, or complete coverage.

    Equal intersections of the first two observer masks are combined with
    their multiplicities. This changes neither the third observer cases nor
    the induced graph. A deadline result never becomes a proof of coverage.
    """
    if seconds < 0:
        raise ValueError("seconds must be nonnegative")
    started = monotonic()
    orders, first = weak_orders(), canonical_first_rows()
    second_masks = tuple(row_mask(row, 1) for row in orders)
    third_masks = tuple(row_mask(row, 2) for row in orders)
    multiplicities, representatives = Counter(), {}
    for a in first:
        mask = row_mask(a, 0)
        for b, bmask in zip(orders, second_masks):
            combined = mask & bmask
            multiplicities[combined] += 1
            representatives.setdefault(combined, (a, b))
    result = {"status": "INCOMPLETE", "states": len(STATES),
              "edges": sum(x.bit_count() for x in NEIGHBORS) // 2,
              "weak_orders": len(orders), "canonical_first_rows": len(first),
              "two_row_masks": len(multiplicities), "profiles_checked": 0,
              "profiles_required": len(first) * len(orders) ** 2}
    histogram = Counter()
    measured = {}
    component_masks.cache_clear()
    for ab, count in multiplicities.items():
        if monotonic() - started >= seconds:
            break
        for c, cmask in zip(orders, third_masks):
            mask = ab & cmask
            parts = component_masks(mask)
            result["profiles_checked"] += count
            histogram[mask.bit_count()] += count
            if len(parts) != 1:
                a, b = representatives[ab]
                result.update(status="DISCONNECTED" if parts else "EMPTY",
                              profile=tuple(tuple(v + 1 for v in row) for row in (a, b, c))
                                      + ((1, 2, 3, 4, 5),),
                              components=tuple(tuple(STATES[i] for i in range(60)
                                                     if part & (1 << i)) for part in parts))
                break
            if diameters and mask not in measured:
                measured[mask] = diameter(mask)
                distance, source, target = measured[mask]
                if distance > result.get("maximum_diameter", -1):
                    a, b = representatives[ab]
                    result.update(maximum_diameter=distance,
                                  diameter_profile=tuple(tuple(v + 1 for v in row) for row in (a, b, c))
                                                   + ((1, 2, 3, 4, 5),),
                                  diameter_endpoints=(STATES[source], STATES[target]))
        else:
            continue
        break
    else:
        result["status"] = "CONNECTED_FOR_ALL"
    result["fair_state_histogram"] = dict(sorted(histogram.items()))
    if diameters:
        result["distinct_graphs_measured"] = len(measured)
    result["elapsed_seconds"] = monotonic() - started
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=600,
                        help="census time limit; incomplete coverage returns exit status 2")
    parser.add_argument("--diameters", action="store_true", help="also measure every distinct fair graph")
    args = parser.parse_args()
    result = census(args.seconds, diameters=args.diameters)
    if result["status"] == "CONNECTED_FOR_ALL":
        route = path(SHARP_PROFILE, SHARP_START, SHARP_TARGET)
        result["strict_sharp_example"] = {"profile": SHARP_PROFILE, "path": route,
                                          "distance": len(route) - 1,
                                          "fair_states": fair_mask(SHARP_PROFILE).bit_count()}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result["status"] in {"INCOMPLETE", "EMPTY"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
