"""Normalize one-extra EF1 allocations with a safe spare to greedy outcomes."""

from __future__ import annotations

import json

from single_extra import one_extra_bundles, path as greedy_path
from swaps import (Allocation, Profile, Witness, allocation, ef1, exchange,
                   rounds_for, validate_witness)


def safe_spares(u: Profile, a: Allocation) -> tuple[int, ...]:
    """Goods in the double bundle dominated by every singleton's own good."""
    bundles, doubled = one_extra_bundles(u, a)
    return tuple(g for g in bundles[doubled]
                 if all(u[i][bundles[i][0]] >= u[i][g]
                        for i in range(len(u)) if i != doubled))


def _swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def _order_or_cycle(u: Profile, a: Allocation, singles: tuple[int, ...]
                    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Peel current maximizers; if stuck, follow strict preferences to a cycle."""
    goods = {i: a.index(i) for i in singles}
    prefers = {i: {j for j in singles if u[i][goods[j]] > u[i][goods[i]]}
               for i in singles}
    remaining = set(singles)
    order = []
    while remaining:
        ready = next((i for i in sorted(remaining) if not prefers[i] & remaining), None)
        if ready is None:
            visited = {}
            walk = []
            i = min(remaining)
            while i not in visited:
                visited[i] = len(walk)
                walk.append(i)
                i = min(prefers[i] & remaining)
            return (), tuple(walk[visited[i]:])
        order.append(ready)
        remaining.remove(ready)
    return tuple(order), ()


def normalize(u: Profile, start: Allocation) -> tuple[list[Allocation], Witness]:
    """Reach a genuine greedy endpoint within at most 2*n*(n-1) exchanges.

    Only one double bundle is allowed. A missing safe spare is an unsupported
    premise, not a claim that the starting allocation is disconnected.
    """
    bundles, doubled = one_extra_bundles(u, start)
    spares = safe_spares(u, start)
    if not spares:
        raise ValueError("normalization requires a safe spare")
    singles = tuple(i for i in range(len(u)) if i != doubled)
    anchor = spares[0]
    variable = next(g for g in bundles[doubled] if g != anchor)
    route = [start]

    # Retain the safe anchor while giving away any desired variable spare.
    while True:
        a = route[-1]
        receiver = next((i for i in singles
                         if u[i][variable] > u[i][a.index(i)]), None)
        if receiver is None:
            break
        old = a.index(receiver)
        route.append(_swap(a, old, variable))
        variable = old

    # Both spares are now dominated by every singleton's own good.
    while True:
        a = route[-1]
        order, cycle = _order_or_cycle(u, a, singles)
        if not cycle:
            break
        first = cycle[0]
        spares = tuple(g for g, owner in enumerate(a) if owner == doubled)
        buffer = max(spares, key=lambda g: u[first][g])
        carried = a.index(first)
        route.append(_swap(a, buffer, carried))
        for i in reversed(cycle[1:]):
            own = route[-1].index(i)
            route.append(_swap(route[-1], carried, own))
            carried = own
        route.append(_swap(route[-1], carried, buffer))

    final = route[-1]
    pair = tuple(g for g, owner in enumerate(final) if owner == doubled)
    first = max(pair, key=lambda g: u[doubled][g])
    last = next(g for g in pair if g != first)
    witness = tuple((i, final.index(i)) for i in order) + ((doubled, first), (doubled, last))
    validate_witness(u, rounds_for(len(u), len(start), (doubled,)), witness)
    if (allocation(witness, len(start)) != final
            or len(route) - 1 > 2 * len(u) * (len(u) - 1)
            or not all(ef1(u, a) for a in route)
            or not all(exchange(a, b) for a, b in zip(route, route[1:]))):
        raise AssertionError("safe-spare construction violated its proof invariants")
    return route, witness


def path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Connect two safe-spare states through the known greedy component."""
    _, left_d = one_extra_bundles(u, start)
    _, right_d = one_extra_bundles(u, target)
    if left_d != right_d:
        raise ValueError("endpoints must have the same doubled recipient")
    left, _ = normalize(u, start)
    right, _ = normalize(u, target)
    middle = greedy_path(u, left[-1], right[-1])
    return left[:-1] + middle + right[-2::-1]


def cycle_example(n: int = 6) -> tuple[Profile, Allocation]:
    """A nongreedy safe-spare state with a strict (n-1)-singleton cycle."""
    if type(n) is not int or n < 3:
        raise ValueError("cycle example needs at least three agents")
    rows = [tuple(range(n + 1))]
    for i in range(1, n):
        row = [0] * (n + 1)
        row[i + 1] = 1
        row[2 + i % (n - 1)] = 2
        rows.append(tuple(row))
    return tuple(rows), (0, 0) + tuple(range(1, n))


def main() -> None:
    u, start = cycle_example()
    route, witness = normalize(u, start)
    print(json.dumps({"agents": len(u), "start": start,
                      "initial_safe_spares": safe_spares(u, start),
                      "path": route, "greedy_witness": witness,
                      "exchanges": len(route) - 1,
                      "scope": "one double bundle and a safe spare; arbitrary agent count"},
                     indent=2))


if __name__ == '__main__':
    main()
