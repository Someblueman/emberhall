"""Candidate EF1 paths for any one complete plus incomplete picking round.

Requires the accepted five_agent_eight.py at f45ab98 or a compatible later
integration. Its singleton reduction and local anchor bridge are dependencies.
"""

from __future__ import annotations

import json

from five_agent_eight import anchor_bridge, singleton_reduction
from near_complete import path as near_complete_path
from swaps import (Allocation, Profile, Witness, allocation, ef1, exchange,
                   favorites, rounds_for, validate_profile, validate_witness)


def _checked(u: Profile, route: list[Allocation]) -> list[Allocation]:
    result = []
    for a in route:
        if not result or a != result[-1]:
            result.append(a)
    if (not all(ef1(u, a) for a in result)
            or not all(exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("constructed route lost EF1 or single exchanges")
    return result


def _complete(u: Profile, prefix: Witness, final: tuple[int, ...]) -> Witness:
    pool = tuple(g for g in range(len(u[0])) if g not in {h for _, h in prefix})
    used = {i for i, _ in prefix}
    result = list(prefix)
    for i in tuple(j for j in range(len(u)) if j not in used) + final:
        g = favorites(u, i, pool)[0]
        result.append((i, g))
        pool = tuple(h for h in pool if h != g)
    return tuple(result)


def _finish(u: Profile, first: Witness, start: Allocation,
            final: tuple[int, ...]) -> tuple[list[Allocation], Witness]:
    target = _complete(u, first, final)
    remaining = {g for _, g in target[len(u):]}
    route = [start]
    for i, g in target[len(u):]:
        if route[-1][g] != i:
            old = next(h for h in remaining if route[-1][h] == i)
            a = list(route[-1])
            a[g], a[old] = a[old], a[g]
            route.append(tuple(a))
        remaining.remove(g)
    return _checked(u, route), target


def _fiber(u: Profile, a: Witness, b: Witness,
           final: tuple[int, ...]) -> list[Allocation]:
    if a[0] != b[0] or a[0][0] in final:
        raise ValueError("fiber needs the same first singleton and favorite")
    fixed, g = a[0]
    agents = tuple(i for i in range(len(u)) if i != fixed)
    goods = tuple(h for h in range(len(u[0])) if h != g)
    ai = {i: k for k, i in enumerate(agents)}
    gi = {h: k for k, h in enumerate(goods)}
    small = tuple(tuple(u[i][h] for h in goods) for i in agents)
    small_final = tuple(ai[i] for i in final)
    aa, bb = (tuple((ai[i], gi[h]) for i, h in w[1:]) for w in (a, b))
    result = []
    for state in path(small, aa, bb, small_final):
        full = [fixed] * len(u[0])
        for h, owner in zip(goods, state):
            full[h] = agents[owner]
        result.append(tuple(full))
    return result


def _singleton_path(u: Profile, a: Witness, b: Witness,
                    final: tuple[int, ...]) -> list[Allocation]:
    (i, g), (j, h) = a[0], b[0]
    m = len(u[0])
    if (i, g) == (j, h):
        return _fiber(u, a, b, final)
    if i == j:
        other = next(k for k in range(len(u)) if k not in final and k != i)
        f = favorites(u, other, tuple(range(m)))[0]
        middle = _complete(u, ((other, f),), final)
        return (_singleton_path(u, a, middle, final)
                + _singleton_path(u, middle, b, final)[1:])
    if g != h:
        left = _complete(u, ((i, g), (j, h)), final)
        right = ((j, h), (i, g)) + left[2:]
        return _fiber(u, a, left, final) + _fiber(u, b, right, final)[-2::-1]

    # Fix the other singleton picks first. Each dominates the remaining local
    # goods except g, so even a temporary double bundle containing g is safe.
    pool = tuple(t for t in range(m) if t != g)
    fixed = []
    for k in range(len(u)):
        if k not in final and k not in (i, j):
            chosen = favorites(u, k, pool)[0]
            fixed.append((k, chosen))
            pool = tuple(t for t in pool if t != chosen)
    local_goods = (g,) + pool
    anchors = []
    for k in final:
        chosen = favorites(u, k, pool)[0]
        anchors.append(chosen)
        pool = tuple(t for t in pool if t != chosen)
    x, y = favorites(u, i, pool)[0], favorites(u, j, pool)[0]
    common = tuple(fixed) + tuple(zip(final, anchors))
    left_first = ((i, g),) + common + ((j, y),)
    right_first = ((j, g),) + common + ((i, x),)
    if x == y:
        left = _complete(u, left_first, final)
        right = right_first + left[len(u):]
        middle = [allocation(left, m), allocation(right, m)]
        return (_fiber(u, a, left, final) + middle[1:]
                + _fiber(u, b, right, final)[-2::-1])

    roles = final + (i, j)
    gi = {t: k for k, t in enumerate(local_goods)}
    small = tuple(tuple(u[k][t] for t in local_goods) for k in roles)
    tails = (x,) + tuple(t for t in pool if t not in (x, y))
    middle = []
    for state in anchor_bridge(small, tuple(gi[t] for t in anchors),
                               tuple(gi[t] for t in tails), 0, gi[x], gi[y]):
        full = list(allocation(tuple(fixed), m))
        for t, owner in zip(local_goods, state):
            full[t] = roles[owner]
        middle.append(tuple(full))
    left_tail, left = _finish(u, left_first, middle[0], final)
    right_tail, right = _finish(u, right_first, middle[-1], final)
    return (_fiber(u, a, left, final) + left_tail[-2::-1] + middle[1:]
            + right_tail[1:] + _fiber(u, b, right, final)[-2::-1])


def path(u: Profile, start: Witness, target: Witness,
         final: tuple[int, ...]) -> list[Allocation]:
    """Connect any two greedy n+r endpoints, with 1<=r<n and a fixed final set."""
    validate_profile(u)
    n, m = len(u), len(u[0])
    if not n < m < 2*n:
        raise ValueError("need exactly one complete and one incomplete round")
    rs = rounds_for(n, m, final)
    validate_witness(u, rs, start)
    validate_witness(u, rs, target)
    final = tuple(sorted(final))
    if len(final) == n-1:
        route = [allocation(w, m) for w in near_complete_path(u, rs, start, target)]
    else:
        left, a = singleton_reduction(u, start, final)
        right, b = singleton_reduction(u, target, final)
        route = left[:-1] + _singleton_path(u, a, b, final) + right[-2::-1]
    route = _checked(u, route)
    if (route[0] != allocation(start, m) or route[-1] != allocation(target, m)):
        raise AssertionError("constructed route changed endpoints")
    return route


def main() -> None:
    n, final = 6, (0, 1)
    u = ((10,) + (0,)*7,) * n
    start = ((4, 0), (2, 1), (3, 2), (5, 3), (0, 4), (1, 5), (0, 6), (1, 7))
    target = ((5, 0), (2, 1), (3, 2), (4, 3), (0, 4), (1, 5), (0, 7), (1, 6))
    route = path(u, start, target, final)
    print(json.dumps({"agents": n, "goods": len(u[0]), "final": final,
                      "path": ["".join(map(str, a)) for a in route],
                      "exchanges": len(route)-1,
                      "scope": "candidate one-complete-round theorem; earlier rounds excluded"},
                     indent=2))


if __name__ == '__main__':
    main()
