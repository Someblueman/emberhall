"""Constructive one-round EF1 paths when exactly two agents miss the final round.

The default example has five agents and eight goods. See FIVE_AGENT_EIGHT.md
for the proof, including the limits on extending this path to earlier rounds.
"""

from __future__ import annotations

import json

from near_complete import path as near_complete_path
from swaps import (Allocation, Profile, Witness, allocation, ef1, exchange,
                   favorites, rounds_for, validate_profile, validate_witness)


def _swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def _checked(u: Profile, route: list[Allocation]) -> list[Allocation]:
    result = [route[0]]
    for a in route[1:]:
        if a != result[-1]:
            result.append(a)
    sizes = tuple(result[0].count(i) for i in range(len(u)))
    if (any(not ef1(u, a) or tuple(a.count(i) for i in range(len(u))) != sizes
            for a in result)
            or any(not exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("constructed route lost fairness, sizes, or single exchanges")
    return result


def anchor_bridge(u: Profile, anchors: tuple[int, ...], tails: tuple[int, ...],
                  g: int, x: int, y: int) -> list[Allocation]:
    """Connect a two-singleton braid, with doubles 0..r-1 and carriers r,r+1.

    Anchors are in common greedy order. ``tails[d]`` is double d's initial
    tail, exactly one of which is x. The target replaces that x by y and
    changes the singleton holdings (g,y) to (x,g). Final picks may be free.
    """
    validate_profile(u)
    r = len(anchors)
    i, j, last = r, r + 1, r - 1
    m = len(u[0])
    if (r < 1 or len(u) != r + 2 or m != 2 * r + 2 or len(tails) != r
            or x not in tails or set(anchors + tails + (g, y)) != set(range(m))):
        raise ValueError("need distinct anchors, tails, favorite and other singleton good")
    remaining_tails = tails + (y,)
    if (any(u[k][g] != max(u[k]) for k in (i, j))
            or any(u[d][h] < u[d][t] for d, h in enumerate(anchors)
                   for t in anchors[d + 1:] + remaining_tails)
            or any(u[i][x] < u[i][t] or u[j][y] < u[j][t]
                   for t in remaining_tails)):
        raise ValueError("the common greedy braid inequalities do not hold")
    start = [-1] * m
    start[g], start[y] = i, j
    for d, (h, t) in enumerate(zip(anchors, tails)):
        start[h] = start[t] = d
    route = [tuple(start)]
    c = anchors[-1]

    def move(p: int, q: int) -> None:
        route.append(_swap(route[-1], p, q))

    def put(t: int, d: int) -> None:
        if route[-1][t] != d:
            old = next(h for h in remaining_tails if route[-1][h] == d)
            move(t, old)

    if u[i][c] >= u[i][x]:
        # With c on i, all tails are affordable. Give the temporary anchorless
        # double its most valuable tail before it receives g.
        put(max(tails, key=lambda t: u[last][t]), last)
        move(g, c)
        move(g, y)
        best_other = max((t for t in remaining_tails if t != x),
                         key=lambda t: u[last][t])
        wanted = {x, best_other}
        held = {t for t in remaining_tails if route[-1][t] == last}
        if wanted != held:
            move(next(iter(wanted - held)), next(iter(held - wanted)))
        move(c, x)
    elif u[j][c] >= u[j][y]:
        reversed_u = u[:r] + (u[j], u[i])
        reversed_tails = tuple(y if t == x else t for t in tails)
        reverse = anchor_bridge(reversed_u, anchors, reversed_tails, g, y, x)
        result = [tuple(i if d == j else j if d == i else d for d in a)
                  for a in reversed(reverse)]
        return _checked(u, result)
    else:
        # Both carriers prefer their own tail maximum to c, so they tolerate
        # the temporary pair {g,c} after deletion of g.
        put(x, last)
        move(g, x)
        move(g, y)
    for d, t in enumerate(tails):
        put(y if t == x else t, d)
    result = _checked(u, route)
    target = list(start)
    target[g], target[x], target[y] = j, i, start[x]
    if result[-1] != tuple(target):
        raise AssertionError("bridge did not reach its target")
    return result


def _complete(u: Profile, prefix: Witness, final: tuple[int, ...]) -> Witness:
    remaining = tuple(g for g in range(len(u[0])) if g not in dict(prefix).values())
    used = {i for i, _ in prefix}
    result = list(prefix)
    for i in tuple(i for i in range(len(u)) if i not in used) + final:
        g = favorites(u, i, remaining)[0]
        result.append((i, g))
        remaining = tuple(h for h in remaining if h != g)
    return tuple(result)


def _finish(u: Profile, first: Witness, start: Allocation,
            final: tuple[int, ...]) -> tuple[list[Allocation], Witness]:
    """Greedily permute free final goods, keeping the first round fixed."""
    target = _complete(u, first, final)
    remaining = {g for _, g in target[len(u):]}
    route = [start]
    for i, g in target[len(u):]:
        if route[-1][g] != i:
            old = next(h for h in remaining if route[-1][h] == i)
            route.append(_swap(route[-1], g, old))
        remaining.remove(g)
    return _checked(u, route), target


def singleton_reduction(u: Profile, witness: Witness, final: tuple[int, ...]
                        ) -> tuple[list[Allocation], Witness]:
    """Reach an actual greedy outcome beginning with a singleton's favorite.

    This lemma works for any one complete round and a nonempty incomplete
    final round, not only the two-singleton case used by ``path``.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if not n < m < 2 * n:
        raise ValueError("need one complete and one nonempty incomplete round")
    validate_witness(u, rounds_for(n, m, final), witness)
    first = witness[:n]
    i, b = next((i, h) for i, h in first if i not in final)
    g = favorites(u, i, tuple(range(m)))[0]
    if u[i][b] == u[i][g]:
        target = ((i, b),) + tuple(p for p in first if p[0] != i) + witness[n:]
        return [allocation(witness, m)], target
    donor = next(d for d, h in first if h == g)
    tails = dict(witness[n:])
    best = max(tails.values(), key=lambda h: u[donor][h])
    route = [allocation(witness, m)]
    if tails[donor] != best:
        route.append(_swap(route[-1], best, tails[donor]))
    route.append(_swap(route[-1], g, b))
    provisional = b
    prefix = [(i, g)]
    for k, h in first:
        if k in (i, donor):
            continue
        if u[k][provisional] > u[k][h]:
            route.append(_swap(route[-1], provisional, h))
            chosen, provisional = provisional, h
        else:
            chosen = h
        prefix.append((k, chosen))
    prefix.append((donor, max((provisional, best), key=lambda h: u[donor][h])))
    tail_route, target = _finish(u, tuple(prefix), route[-1], final)
    validate_witness(u, rounds_for(n, m, final), target)
    return _checked(u, route + tail_route[1:]), target


def _fiber(u: Profile, start: Witness, target: Witness,
           final: tuple[int, ...]) -> list[Allocation]:
    """Fix one favorite singleton, apply the near-complete theorem underneath."""
    if start[0] != target[0] or start[0][0] in final:
        raise ValueError("fiber requires the same first singleton pick")
    fixed, g = start[0]
    agents = tuple(i for i in range(len(u)) if i != fixed)
    goods = tuple(h for h in range(len(u[0])) if h != g)
    ai = {i: k for k, i in enumerate(agents)}
    gi = {h: k for k, h in enumerate(goods)}
    reduced = tuple(tuple(u[i][h] for h in goods) for i in agents)
    reduced_final = tuple(sorted(ai[i] for i in final))
    def shrink(w: Witness) -> Witness:
        return tuple((ai[i], gi[h]) for i, h in w[1:])
    ws = near_complete_path(reduced, rounds_for(len(agents), len(goods), reduced_final),
                            shrink(start), shrink(target))
    return [allocation(((fixed, g),) + tuple((agents[i], goods[h]) for i, h in w),
                       len(u[0])) for w in ws]


def _singleton_path(u: Profile, a: Witness, b: Witness,
                    final: tuple[int, ...]) -> list[Allocation]:
    (i, g), (j, h) = a[0], b[0]
    if i == j and g == h:
        return _fiber(u, a, b, final)
    if i == j:
        other = next(k for k in range(len(u)) if k not in final and k != i)
        f = favorites(u, other, tuple(range(len(u[0]))))[0]
        middle = _complete(u, ((other, f),), final)
        return _singleton_path(u, a, middle, final) + _singleton_path(u, middle, b, final)[1:]
    if g != h:
        left = _complete(u, ((i, g), (j, h)), final)
        right = ((j, h), (i, g)) + left[2:]
        return _fiber(u, a, left, final) + list(reversed(_fiber(u, b, right, final)))[1:]

    agents = final + (i, j)
    goods = tuple(range(len(u[0])))
    pool = tuple(t for t in goods if t != g)
    anchors = []
    for k in final:
        t = favorites(u, k, pool)[0]
        anchors.append(t)
        pool = tuple(h for h in pool if h != t)
    x, y = favorites(u, i, pool)[0], favorites(u, j, pool)[0]
    common = tuple(zip(final, anchors))
    if x == y:
        left = _complete(u, ((i, g),) + common + ((j, y),), final)
        right = ((j, g),) + common + ((i, x),) + left[len(u):]
        middle = [allocation(left, len(goods)), allocation(right, len(goods))]
        return (_fiber(u, a, left, final) + middle[1:]
                + list(reversed(_fiber(u, b, right, final)))[1:])
    tails = (x,) + tuple(t for t in pool if t not in (x, y))
    relabeled = tuple(u[k] for k in agents)
    bridge = [tuple(agents[k] for k in state)
              for state in anchor_bridge(relabeled, tuple(anchors), tails, g, x, y)]
    left_first = ((i, g),) + common + ((j, y),)
    right_first = ((j, g),) + common + ((i, x),)
    left_tail, left = _finish(u, left_first, bridge[0], final)
    right_tail, right = _finish(u, right_first, bridge[-1], final)
    return (_fiber(u, a, left, final) + list(reversed(left_tail))[1:]
            + bridge[1:] + right_tail[1:]
            + list(reversed(_fiber(u, b, right, final)))[1:])


def path(u: Profile, start: Witness, target: Witness,
         final: tuple[int, ...] = (0, 1, 2)) -> list[Allocation]:
    """Connect greedy n-agent (2n-2)-good endpoints; exactly two singletons.

    No whole-allocation-graph search is used. The recursive near-complete
    constructor is used only after fixing and removing a favorite singleton.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if n < 3 or m != 2 * n - 2 or len(final) != n - 2:
        raise ValueError("need n>=3, 2n-2 goods, and exactly two singleton agents")
    rounds = rounds_for(n, m, final)
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    final = tuple(sorted(final))
    left, a = singleton_reduction(u, start, final)
    right, b = singleton_reduction(u, target, final)
    middle = _singleton_path(u, a, b, final)
    route = _checked(u, left + middle[1:] + right[-2::-1])
    if route[0] != allocation(start, m) or route[-1] != allocation(target, m):
        raise AssertionError("path endpoints changed")
    return route


EXAMPLE: Profile = (
    (0, 100, 90, 80, 70, 60, 50, 40),
    (0, 0, 100, 90, 80, 70, 60, 50),
    (0, 0, 0, 100, 80, 70, 60, 50),
    (100, 90, 80, 70, 60, 0, 20, 10),
    (100, 90, 80, 70, 0, 60, 20, 10),
)
LEFT: Witness = ((3, 0), (0, 1), (1, 2), (2, 3), (4, 5), (0, 4), (1, 6), (2, 7))
RIGHT: Witness = ((4, 0), (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (1, 6), (2, 7))


if __name__ == "__main__":
    route = path(EXAMPLE, LEFT, RIGHT)
    print(json.dumps({"case": "five agents, eight goods",
                      "method": "singleton reduction, anchor bridge, near-complete fibers",
                      "path": ["".join(map(str, a)) for a in route],
                      "exchanges": len(route) - 1,
                      "scope": "one complete round; exactly two agents miss the final round"},
                     indent=2))
