"""EF1 exchange paths for any number of complete rounds and final recipients.

The one-round and all-size one-anchor constructions are separate prerequisites;
see ARBITRARY_FEW_FINAL.md for their exact source pins.
"""

from __future__ import annotations

import argparse
import json

from arbitrary_single_round import path as one_round_path
from one_anchor_certificate import canonical_endpoints, one_anchor_bridge
from swaps import (Allocation, Profile, Witness, after_pick, allocation, ef1,
                   exchange, favorites, rounds_for,
                   validate_profile, validate_witness)


def _core_path(u: Profile, r: int) -> list[Allocation]:
    """Only the canonical shared-favorite braid, not arbitrary endpoints."""
    return one_anchor_bridge(u, *canonical_endpoints(r))


def _singletons(start: Allocation, target: Allocation) -> list[Allocation]:
    """All bundles have size at most one, so every intermediate state is EF1."""
    route = [start]
    for good, owner in enumerate(target):
        if route[-1][good] != owner:
            other = route[-1].index(owner)
            state = list(route[-1])
            state[good], state[other] = state[other], state[good]
            route.append(tuple(state))
    return route


def _free_base(u: Profile, a: Witness, b: Witness, r: int) -> list[Allocation]:
    """Attach arbitrary final assignments to actual greedy endpoints."""
    n, m = len(u), len(u[0])
    if r == 0:
        return _singletons(allocation(a, m), allocation(b, m))

    def finish(w):
        pool = set(range(m)) - {g for _, g in w[:n]}
        route, witness = [allocation(w, m)], list(w[:n])
        for i in range(r):
            g = favorites(u, i, tuple(sorted(pool)))[0]
            if route[-1][g] != i:
                h = next(h for h in pool if route[-1][h] == i)
                state = list(route[-1])
                state[g], state[h] = state[h], state[g]
                route.append(tuple(state))
            pool.remove(g)
            witness.append((i, g))
        return route, tuple(witness)

    left, aa = finish(a)
    right, bb = finish(b)
    return left + one_round_path(u, aa, bb, tuple(range(r)))[1:] + right[-2::-1]


def _pad(u: Profile, prefix: Witness, route: list[Allocation],
         carriers: tuple[int, int], g: int) -> list[Allocation]:
    """Validate and restore the common rounds with the favorite omitted."""
    n, m = len(u), len(u[0])
    remaining = set(range(m)) - {g}
    bundles = [[] for _ in u]
    if len(prefix) % n:
        raise AssertionError("common prefix does not consist of complete rounds")
    for offset in range(0, len(prefix), n):
        picks = prefix[offset:offset + n]
        if {i for i, _ in picks} != set(range(n)):
            raise AssertionError("common round misses an agent")
        for i, h in picks:
            if h not in remaining or h not in favorites(u, i, tuple(remaining)):
                raise AssertionError("common prefix is not greedy with g omitted")
            remaining.remove(h)
            bundles[i].append(h)
    if any(sum(row[h] for h in bundles[i]) < sum(row[h] for h in bundles[j])
           for i, row in enumerate(u) for j in carriers if i != j):
        raise AssertionError("common bundle does not dominate a carrier bundle")
    result = []
    for tail in route:
        if {h for h, i in enumerate(tail) if i >= 0} != remaining | {g}:
            raise AssertionError("local route covers the wrong residual goods")
        state = list(tail)
        for i, h in prefix:
            state[h] = i
        result.append(tuple(state))
    return result


def _construct(u: Profile, start: Witness, target: Witness, r: int) -> list[Allocation]:
    n, m = len(u), len(u[0])
    final = tuple(range(r))
    if m == n + r:
        return _free_base(u, start, target, r)

    def complete(rs, goods):
        result = []
        while goods:
            i = rs[0][0]
            g = favorites(u, i, goods)[0]
            result.append((i, g))
            rs = after_pick(rs, i)
            goods = tuple(h for h in goods if h != g)
        return tuple(result)

    def braid(rs, goods, prefix, i, j, g):
        left, right = [(i, g)], [(j, g)]
        common = tuple(h for h in goods if h != g)
        eligible, later = rs[0], rs[1:]
        noncarriers = tuple(k for k in range(n) if k not in (i, j))
        while True:
            # In the last round, freeze extra singletons before the moving core.
            order = eligible
            if r and len(later) == 1:
                order = tuple(k for k in eligible if k not in final) + final
            anchors = {}
            for k in order:
                if k in (i, j):
                    continue
                h = favorites(u, k, common)[0]
                anchors[k] = h
                left.append((k, h))
                right.append((k, h))
                common = tuple(t for t in common if t != h)
            x, y = favorites(u, i, common)[0], favorites(u, j, common)[0]
            left.append((j, y))
            right.append((i, x))
            common = tuple(h for h in common if h not in (x, y))
            if x == y:
                rest = complete(later, common)
                a, b = tuple(left) + rest, tuple(right) + rest
                return a, b, [allocation(prefix + w, m) for w in (a, b)]
            if r and len(later) == 1:
                carrier = next((k for k in (i, j) if k in final), None)
                recipient = carrier if carrier is not None else final[0]
                rest = tuple(zip((k for k in final if k != recipient), common))
                a = tuple(left) + ((recipient, x),) + rest
                b = tuple(right) + ((recipient, y),) + rest
                if carrier is not None:
                    return a, b, [allocation(prefix + w, m) for w in (a, b)]
                core = (g,) + tuple(anchors[k] for k in final) + (x, y) + common
                roles = final + (i, j)
                local = tuple(tuple(u[k][h] for h in core) for k in roles)
                spectator_picks = tuple((k, anchors[k]) for k in noncarriers if k not in final)
                tail_route = []
                for state in _core_path(local, r):
                    full = list(allocation(spectator_picks, m))
                    for h, owner in zip(core, state):
                        full[h] = roles[owner]
                    tail_route.append(tuple(full))
                tail_goods = set(core) | {h for _, h in spectator_picks}
                full_a, full_b = prefix + a, prefix + b
                by_agent = {k: [h for owner, h in full_a if owner == k and h not in tail_goods]
                            for k in range(n)}
                positions = {h: t for t, (_, h) in enumerate(full_a)}
                common_prefix = []
                for t in range(len(by_agent[0])):
                    earlier = sorted(noncarriers, key=lambda k: positions[by_agent[k][t]])
                    common_prefix.extend((k, by_agent[k][t]) for k in (*earlier, i, j))
                route = _pad(u, tuple(common_prefix), tail_route, (i, j), g)
                if route[0] != allocation(full_a, m) or route[-1] != allocation(full_b, m):
                    raise AssertionError("protected braid changed its endpoints")
                return a, b, route
            left.append((i, x))
            right.append((j, y))
            eligible, later = later[0], later[1:]

    def connect(rs, goods, a, b, prefix):
        if a == b or allocation(a, m) == allocation(b, m):
            return [allocation(prefix + a, m)]
        if len(prefix) == n:
            labels = {g: k for k, g in enumerate(goods)}
            small = tuple(tuple(row[g] for g in goods) for row in u)
            aa, bb = (tuple((i, labels[g]) for i, g in w) for w in (a, b))
            result = []
            for tail in _construct(small, aa, bb, r):
                state = list(allocation(prefix, m))
                for g, owner in zip(goods, tail):
                    state[g] = owner
                result.append(tuple(state))
            return result
        (i, g), (j, h) = a[0], b[0]
        if (i, g) == (j, h):
            return connect(after_pick(rs, i), tuple(k for k in goods if k != g),
                           a[1:], b[1:], prefix + ((i, g),))
        if i == j and len(rs[0]) > 1:
            other = next(k for k in rs[0] if k != i)
            f = favorites(u, other, goods)[0]
            middle = ((other, f),) + complete(after_pick(rs, other),
                                             tuple(k for k in goods if k != f))
            return connect(rs, goods, a, middle, prefix) + connect(rs, goods, middle, b, prefix)[1:]
        if i == j:
            rest = complete(after_pick(after_pick(rs, i), i), tuple(k for k in goods if k not in (g, h)))
            aa, bb = ((i, g), (i, h)) + rest, ((i, h), (i, g)) + rest
            middle = [allocation(prefix + aa, m)]
        elif g != h:
            rest = complete(after_pick(after_pick(rs, i), j), tuple(k for k in goods if k not in (g, h)))
            aa, bb = ((i, g), (j, h)) + rest, ((j, h), (i, g)) + rest
            middle = [allocation(prefix + aa, m)]
        else:
            aa, bb, middle = braid(rs, goods, prefix, i, j, g)
        return (connect(rs, goods, a, aa, prefix) + middle[1:]
                + connect(rs, goods, bb, b, prefix)[1:])

    return connect(rounds_for(n, m, final), tuple(range(m)), start, target, ())


def path(u: Profile, start: Witness, target: Witness,
         final: tuple[int, ...]) -> list[Allocation]:
    """Connect greedy endpoints with the same labeled sizes, including q=0 or r=0."""
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (len(final) >= n or len(set(final)) != len(final)
            or any(type(i) is not int or i not in range(n) for i in final)
            or m % n != len(final)):
        raise ValueError("need exactly m modulo n distinct final recipients")
    rs = rounds_for(n, m, final)
    validate_witness(u, rs, start)
    validate_witness(u, rs, target)
    roles = tuple(sorted(final)) + tuple(i for i in range(n) if i not in final)
    inverse = {i: k for k, i in enumerate(roles)}
    reduced = tuple(u[i] for i in roles)
    a, b = (tuple((inverse[i], g) for i, g in w) for w in (start, target))
    if m <= n:
        route = _singletons(allocation(a, m), allocation(b, m))
    elif len(final) == n - 1:
        from near_complete import path as near_complete_path
        normalized_rounds = rounds_for(n, m, tuple(range(len(final))))
        route = [allocation(w, m) for w in near_complete_path(reduced, normalized_rounds, a, b)]
    else:
        route = _construct(reduced, a, b, len(final))
    result = []
    for state in route:
        state = tuple(roles[i] for i in state)
        if not result or state != result[-1]:
            result.append(state)
    sizes = tuple(m // n + (i in final) for i in range(n))
    if (result[0] != allocation(start, m) or result[-1] != allocation(target, m)
            or any(tuple(a.count(i) for i in range(n)) != sizes or not ef1(u, a) for a in result)
            or any(not exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("route failed endpoint, size, fairness or exchange checks")
    return result


def braid_example(n: int, q: int, r: int, carriers=None):
    """An uncancelled q-round braid, including optional final-recipient carriers."""
    if (type(n) is not int or type(q) is not int or type(r) is not int
            or n < 2 or q < 0 or r not in range(n) or n * q + r == 0):
        raise ValueError("example needs n>=2, q>=0, 0<=r<n and at least one good")
    if q == 0:
        u = ((0,) * r,) * n
        return u, tuple(zip(range(r), range(r))), tuple(zip(range(r), reversed(range(r)))), tuple(range(r))
    i, j = carriers if carriers is not None else (n - 2, n - 1)
    final = tuple(range(r))
    others = tuple(k for k in range(n) if k not in (i, j))
    order = tuple(k for k in others if k not in final) + tuple(k for k in others if k in final)
    m = n * q + r
    u = [[0] * m for _ in range(n)]
    left, right = [], []
    previous_x = previous_y = 0
    for t in range(q):
        anchors = tuple(1 + n*t + k for k in range(n-2))
        x, y = n-1 + n*t, n + n*t
        if r == 0 and t == q - 1:
            y = x
        for k, h in zip(order, anchors):
            u[k][h] = 100 * (q-t)
        u[i][x], u[i][y] = 10*(q-t)+1, 10*(q-t)
        u[j][x], u[j][y] = 10*(q-t), 10*(q-t)+1
        left.extend(((i, previous_x), *zip(order, anchors), (j, y)))
        right.extend(((j, previous_y), *zip(order, anchors), (i, x)))
        previous_x, previous_y = x, y
    u[i][0] = u[j][0] = 10*q+20
    if r:
        recipient = next((k for k in (i, j) if k in final), final[0])
        rest = tuple(zip((k for k in final if k != recipient), range(n*q+1, m)))
        left.extend(((recipient, previous_x), *rest))
        right.extend(((recipient, previous_y), *rest))
    return tuple(map(tuple, u)), tuple(left), tuple(right), final


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", type=int, default=6)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--final", type=int, default=3)
    args = parser.parse_args()
    u, a, b, final = braid_example(args.agents, args.rounds, args.final)
    route = path(u, a, b, final)
    print(json.dumps({"agents": len(u), "goods": len(u[0]), "final_recipients": final,
                      "exchanges": len(route)-1, "path": route,
                      "scope": "all final remainders; mathematical reconstruction remains separate"}, indent=2))


if __name__ == "__main__":
    main()
