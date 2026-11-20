"""A constructive one-anchor bridge; no solver or proof archive is needed.

The two carriers have a shared favorite. Every double has an anchor that
dominates the tail pool. See ONE_ANCHOR_CERTIFICATE.md for the all-real proof.
"""

from __future__ import annotations

import argparse
import json
from random import Random

from swaps import Allocation, Profile, ef1, exchange, validate_profile


def validate(u: Profile) -> int:
    validate_profile(u)
    r = len(u) - 2
    if r < 1 or len(u[0]) != 2 * r + 2:
        raise ValueError("need r double recipients, two carriers and 2r+2 goods")
    tails = range(r + 1, 2 * r + 2)
    if any(u[i][0] < max(u[i]) for i in (r, r + 1)):
        raise ValueError("good zero must be a shared favorite")
    if any(u[d][d + 1] < u[d][g] for d in range(r) for g in tails):
        raise ValueError("every original anchor must dominate every tail")
    return r


def canonical_endpoints(r: int) -> tuple[Allocation, Allocation]:
    if type(r) is not int or r < 1:
        raise ValueError("need at least one double recipient")
    start = (r,) + tuple(range(r)) + (0, r + 1) + tuple(range(1, r))
    target = (r + 1,) + tuple(range(r)) + (r, 0) + tuple(range(1, r))
    return start, target


def _endpoint(u, state, r):
    if (len(state) != 2 * r + 2 or any(type(a) is not int or a not in range(r + 2) for a in state)
            or tuple(state.count(a) for a in range(r + 2)) != (2,) * r + (1, 1)
            or state[0] not in (r, r + 1)
            or any(state[d + 1] != d for d in range(r))):
        raise ValueError("endpoint must retain every original anchor and its size vector")
    active = 2 * r + 1 - state[0]
    z = state.index(active)
    if z <= r or any(u[active][g] > u[active][z] for g in range(r + 1, 2 * r + 2)):
        raise ValueError("active carrier must hold a favorite original tail")


def crossing(u: Profile) -> tuple[Allocation, int, int | None, int | None]:
    """A common fair crossing, with at most one original anchor displaced."""
    r = validate(u)
    goods = tuple(range(1, 2 * r + 2))
    top = [set(sorted(goods, key=lambda g: (-u[i][g], g))[:r + 1]) for i in (r, r + 1)]
    t = min(top[0] & top[1])
    while True:
        better = next((g for g in goods if u[r][g] > u[r][t]
                       and u[r + 1][g] > u[r + 1][t]), None)
        if better is None:
            break
        t = better
    marks = {g: int(u[r][g] > u[r][t]) + 2 * int(u[r + 1][g] > u[r + 1][t]) for g in goods}
    if any(mark == 3 for mark in marks.values()):
        raise AssertionError("crossing good is not Pareto maximal")
    pivot = t - 1 if t <= r else None
    q = (max(range(r + 1, 2 * r + 2), key=lambda g: (u[pivot][g], -g))
         if pivot is not None else None)
    anchors = {d: q if d == pivot else d + 1 for d in range(r)}
    tails = sorted(set(goods) - {t} - set(anchors.values()))
    matched = {}

    def augment(d, seen):
        for g in tails:
            if g in seen or marks[g] & marks[anchors[d]]:
                continue
            seen.add(g)
            if g not in matched or augment(matched[g], seen):
                matched[g] = d
                return True
        return False

    for d in range(r):
        if not augment(d, set()):
            raise AssertionError("Hall's condition failed")
    owners = [-1] * (2 * r + 2)
    owners[0], owners[t] = r, r + 1
    for d, a in anchors.items():
        owners[a] = d
    for g, d in matched.items():
        owners[g] = d
    result = tuple(owners)
    if not ef1(u, result):
        raise AssertionError("constructed crossing is not EF1")
    return result, t, pivot, q


def _attach(u, start, target, t, pivot, q, r):
    """Attach one endpoint to its owner-side crossing in at most r+1 moves."""
    active = 2 * r + 1 - start[0]
    z = start.index(active)
    before = list(target)
    moves = []
    if pivot is None:
        if z != t:
            before[t], before[z] = before[z], before[t]
            moves = [(z, t)]
    elif target[z] == pivot:
        before[t], before[z] = before[z], before[t]
        moves = [(z, t)]
    else:
        other = target[z]
        p = next(g for g, a in enumerate(target) if a == pivot and g != q)
        if u[active][q] >= u[active][t]:
            before[t], before[q], before[z] = pivot, other, active
            moves = [(z, q), (q, t)]
        else:
            before[t], before[p], before[z] = pivot, other, active
            moves = [(z, t), (z, p)]
    before = tuple(before)
    route = [start]

    def move(x, y):
        if x == y:
            return
        result = list(route[-1])
        result[x], result[y] = result[y], result[x]
        result = tuple(result)
        if (not exchange(route[-1], result) or not ef1(u, result)
                or sum(result[d + 1] != d for d in range(r)) > 1
                or result[0] not in (r, r + 1)):
            raise AssertionError("attachment left the fair one-anchor domain")
        route.append(result)

    for d in range(r):
        held = next(g for g in range(r + 1, 2 * r + 2) if route[-1][g] == d)
        wanted = next(g for g in range(r + 1, 2 * r + 2) if before[g] == d)
        move(held, wanted)
    if route[-1] != before:
        raise AssertionError("tail permutation missed its prescribed state")
    for x, y in moves:
        move(x, y)
    if route[-1] != target or len(route) - 1 > r + 1:
        raise AssertionError("attachment bound or endpoint failed")
    return route


def one_anchor_bridge(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Connect opposite favorite owners in <=2r+3 swaps, with <=1 anchor away."""
    r = validate(u)
    _endpoint(u, start, r)
    _endpoint(u, target, r)
    if start[0] == target[0]:
        raise ValueError("the two endpoints must give good zero to different carriers")
    common, t, pivot, q = crossing(u)
    left = tuple(start[0] if a == r else 2 * r + 1 - start[0] if a == r + 1 else a
                 for a in common)
    right = list(left)
    right[0], right[t] = right[t], right[0]
    right = tuple(right)
    first = _attach(u, start, left, t, pivot, q, r)
    second = _attach(u, target, right, t, pivot, q, r)
    route = first + [right] + list(reversed(second[:-1]))
    if not exchange(left, right) or not ef1(u, right) or len(route) - 1 > 2 * r + 3:
        raise AssertionError("crossing or total bound failed")
    return route


def example(r: int, seed: int = 0) -> Profile:
    rng = Random(seed)
    rows = [[rng.randrange(20) for _ in range(2 * r + 2)] for _ in range(r + 2)]
    for d in range(r):
        rows[d][d + 1] = max(rows[d][r + 1:]) + rng.randrange(4)
    for i, z in ((r, r + 1), (r + 1, r + 2)):
        rows[i][z] = max(rows[i][r + 1:]) + 1
        rows[i][0] = max(rows[i]) + 1
    return tuple(map(tuple, rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.pairs < 1:
        parser.error("--pairs must be positive")
    u = example(args.pairs, args.seed)
    start, target = canonical_endpoints(args.pairs)
    route = one_anchor_bridge(u, start, target)
    print(json.dumps({"pairs": args.pairs, "exchanges": len(route) - 1,
                      "bound": 2 * args.pairs + 3,
                      "maximum_anchors_away": max(sum(a[d + 1] != d for d in range(args.pairs))
                                                   for a in route), "path": route}))


if __name__ == "__main__":
    main()
