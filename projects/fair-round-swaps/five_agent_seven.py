"""Exact five-agent, seven-good EF1 paths and the shared-favorite braid."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
import argparse
from itertools import combinations
import json

from swaps import (Allocation, Profile, Witness, allocation, ef1, exchange, rounds_for,
                   validate_profile, validate_witness)

# Agents D,E,i,j,h = 0,1,2,3,4; goods g,k,l,t,x,y,z = 0,...,6.
LEFT = ((2, 0), (0, 1), (1, 2), (4, 3), (3, 5), (0, 4), (1, 6))
RIGHT = ((3, 0), (0, 1), (1, 2), (4, 3), (2, 4), (0, 5), (1, 6))
EXAMPLE: Profile = (
    (0, 100, 90, 80, 70, 60, 50),
    (0, 0, 100, 90, 80, 70, 60),
    (100, 90, 20, 10, 60, 0, 1),
    (100, 90, 20, 10, 0, 60, 1),
    (100, 100, 90, 40, 30, 20, 10),
)


def swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def _path(u: Profile, start: Allocation, target: Allocation,
          permitted: Callable[[Allocation], bool]) -> list[Allocation]:
    """Search all allowed EF1 neighbors, including non-picking states."""
    if not all(permitted(a) and ef1(u, a) for a in (start, target)):
        raise ValueError("endpoints do not belong to the requested fair subgraph")
    previous: dict[Allocation, Allocation | None] = {start: None}
    queue = deque([start])
    while queue:
        a = queue.popleft()
        if a == target:
            result = [a]
            while previous[result[-1]] is not None:
                result.append(previous[result[-1]])
            return result[::-1]
        for x, y in combinations(range(7), 2):
            if a[x] == a[y]:
                continue
            b = swap(a, x, y)
            if b not in previous and permitted(b) and ef1(u, b):
                previous[b] = a
                queue.append(b)
    raise AssertionError("proved endpoints were disconnected")


def _lend(u: Profile, a: Allocation) -> list[Allocation]:
    """Put E's preferred available tail in E, then exchange l and t."""
    d_tail = next(g for g in (4, 5, 6) if a[g] == 0)
    e_tail = next(g for g in (4, 5, 6) if a[g] == 1)
    result = [a]
    if u[1][d_tail] > u[1][e_tail]:
        result.append(swap(a, d_tail, e_tail))
    result.append(swap(result[-1], 2, 3))
    return result


def bridge(u: Profile) -> list[Allocation]:
    """Connect the two documented greedy braid witnesses, including all ties.

    Utilities use canonical agent/good labels above. This accepts only the
    specified seven-pick schedules, not arbitrary five-agent allocations.
    """
    validate_profile(u)
    if len(u) != 5 or len(u[0]) != 7:
        raise ValueError("need five agents and seven goods")
    rounds = rounds_for(5, 7, (0, 1))
    validate_witness(u, rounds, LEFT)
    validate_witness(u, rounds, RIGHT)
    start, target = allocation(LEFT, 7), allocation(RIGHT, 7)
    if u[4][2] <= u[4][3]:
        result = _path(u, start, target,
                       lambda a: a[3] == 4 and a[1] == 0 and a[0] != 0)
    else:
        left, right = _lend(u, start), _lend(u, target)
        middle = _path(u, left[-1], right[-1],
                       lambda a: a[2] == 4 and a[0] in (2, 3))
        result = left[:-1] + middle + right[-2::-1]
    if not (result[0] == start and result[-1] == target
            and all(ef1(u, a) for a in result)
            and all(exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("invalid constructed bridge")
    return result


def _validate(u: Profile, witness: Witness, final: tuple[int, ...]) -> None:
    validate_profile(u)
    if len(u) != 5 or len(u[0]) != 7:
        raise ValueError("need five agents and seven goods")
    validate_witness(u, rounds_for(5, 7, final), witness)


def _complete(u: Profile, prefix: Witness, final: tuple[int, ...]) -> Witness:
    """Finish a legal first-round prefix greedily, with deterministic ties."""
    result = list(prefix)
    remaining = set(range(7)) - {g for _, g in prefix}
    first = {i for i, _ in prefix}
    for i in tuple(j for j in range(5) if j not in first) + final:
        g = max(sorted(remaining), key=lambda good: u[i][good])
        result.append((i, g))
        remaining.remove(g)
    return tuple(result)


def singleton_reduction(u: Profile, witness: Witness,
                        final: tuple[int, ...] = (0, 1)
                        ) -> tuple[list[Allocation], Witness]:
    """Reach a greedy outcome that starts with a singleton; see Sections 4–5.

    Preparatory swaps preserve the original singleton's global favorite.
    The last fiber has at most 30 or 12 allocations, including non-greedy ones.
    """
    _validate(u, witness, final)
    first = witness[:5]
    pos = next(p for p, (i, _) in enumerate(first) if i not in final)
    i, b = first[pos]
    start = allocation(witness, 7)
    if u[i][b] == max(u[i]):
        target_witness = ((i, b),) + tuple(p for p in first if p[0] != i) + witness[5:]
        _validate(u, target_witness, final)
        return [start], target_witness

    donor, g = max(first[:pos], key=lambda pick: u[i][pick[1]])
    other = next(j for j in final if j != donor)
    tails = dict(witness[5:])
    route = [start]
    if u[donor][tails[other]] > u[donor][tails[donor]]:
        route.append(swap(route[-1], tails[donor], tails[other]))
    route.append(swap(route[-1], g, b))
    donor_anchor = b
    other_before = next((good for j, good in first[:pos] if j == other), None)

    if other_before is None:
        r, f = first[pos + 1]
        if u[r][b] > u[r][f]:
            route.append(swap(route[-1], b, f))
            favorite, donor_anchor = b, f
        else:
            favorite = f
        if r not in final:
            prefix = ((i, g), (r, favorite))
        else:
            other_before = favorite

    if other_before is not None:
        j, c = next((j, good) for j, good in first[pos + 1:] if j not in final)
        if u[j][donor_anchor] > u[j][c]:
            route.append(swap(route[-1], donor_anchor, c))
            c = donor_anchor
        prefix = ((i, g), (other, other_before), (j, c))

    target_witness = _complete(u, prefix, final)
    _validate(u, target_witness, final)
    fixed = {good: j for j, good in prefix}
    tail = _path(u, route[-1], allocation(target_witness, 7),
                 lambda a: all(a[good] == owner for good, owner in fixed.items()))
    route.extend(tail[1:])
    if not all(ef1(u, a) for a in route):
        raise AssertionError("singleton reduction lost EF1")
    return route, target_witness


def path(u: Profile, start: Witness, target: Witness,
         final: tuple[int, ...] = (0, 1)) -> list[Allocation]:
    """Connect arbitrary greedy endpoints in the full 1,260-state size graph.

    The proof gives existence. Breadth-first search returns a shortest path
    for this fixed size case, without asserting whole-graph connectivity.
    """
    _validate(u, start, final)
    _validate(u, target, final)
    return _path(u, allocation(start, 7), allocation(target, 7), lambda a: True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--general', action='store_true',
                        help='run two noncanonical greedy schedules through the full graph')
    args = parser.parse_args()
    left, right = LEFT, RIGHT
    if args.general:
        left = _complete(EXAMPLE, ((0, 1),), (0, 1))
        right = _complete(EXAMPLE, ((4, 0),), (0, 1))
        route = path(EXAMPLE, left, right)
    else:
        route = bridge(EXAMPLE)
    print(json.dumps({"case": "five-agent seven-good EF1 paths",
                      "method": "full EF1 graph" if args.general else "anchor loan",
                      "witnesses": {"start": left, "target": right},
                      "path": ["".join(map(str, a)) for a in route],
                      "exchanges": len(route) - 1,
                      "scope": "five agents, seven goods; larger cases remain open"},
                     indent=2))


if __name__ == "__main__":
    main()
