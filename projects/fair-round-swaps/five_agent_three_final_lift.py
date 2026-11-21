"""Five-agent 5q+3 paths using the portable protected eight-good certificate."""

from __future__ import annotations

import argparse
import json

from five_agent_eight import path as one_round_path
from protected_linear_certificate import padded_bridge
from swaps import (after_pick, allocation, ef1, exchange, favorites,
                   rounds_for, validate_profile, validate_witness)


FINAL = (0, 1, 2)


def _free_base(u, start, target):
    """Attach free final assignments to genuinely greedy eight-good witnesses."""
    def finish(w):
        remaining = set(range(8)) - {g for _, g in w[:5]}
        result, witness = [allocation(w, 8)], list(w[:5])
        for i in FINAL:
            g = max(sorted(remaining), key=lambda h: u[i][h])
            if result[-1][g] != i:
                old = next(h for h in remaining if result[-1][h] == i)
                a = list(result[-1])
                a[g], a[old] = a[old], a[g]
                result.append(tuple(a))
            remaining.remove(g)
            witness.append((i, g))
        return result, tuple(witness)
    left, a = finish(start)
    right, b = finish(target)
    return left + one_round_path(u, a, b, FINAL)[1:] + right[-2::-1]


def _construct(u, start, target):
    m = len(u[0])
    if m == 8:
        return _free_base(u, start, target)

    def complete(rounds, goods):
        result = []
        while goods:
            i = rounds[0][0]
            g = favorites(u, i, goods)[0]
            result.append((i, g))
            rounds = after_pick(rounds, i)
            goods = tuple(h for h in goods if h != g)
        return tuple(result)

    def braid(rounds, goods, prefix, i, j, g):
        left, right = [(i, g)], [(j, g)]
        common = tuple(h for h in goods if h != g)
        eligible, later = rounds[0], rounds[1:]
        while True:
            anchors = {}
            for a in eligible:
                if a not in (i, j):
                    h = favorites(u, a, common)[0]
                    left.append((a, h))
                    right.append((a, h))
                    anchors[a] = h
                    common = tuple(k for k in common if k != h)
            x, y = favorites(u, i, common)[0], favorites(u, j, common)[0]
            left.append((j, y))
            right.append((i, x))
            common = tuple(h for h in common if h not in (x, y))
            if x == y:
                rest = complete(later, common)
                left, right = tuple(left) + rest, tuple(right) + rest
                return left, right, [allocation(prefix + w, m) for w in (left, right)]
            if len(later) == 1:
                if i in FINAL or j in FINAL:
                    carrier = i if i in FINAL else j
                    rest = tuple(zip((a for a in FINAL if a != carrier), common))
                    left = tuple(left) + ((carrier, x),) + rest
                    right = tuple(right) + ((carrier, y),) + rest
                    return left, right, [allocation(prefix + w, m) for w in (left, right)]
                tail = (g, *(anchors[a] for a in FINAL), x, y, *common)
                rest = tuple(zip(FINAL[1:], common))
                left = tuple(left) + ((FINAL[0], x),) + rest
                right = tuple(right) + ((FINAL[0], y),) + rest
                full_left, full_right = prefix + left, prefix + right
                by_agent = {a: [h for b, h in full_left if a == b and h not in tail]
                            for a in range(5)}
                positions = {h: k for k, (_, h) in enumerate(full_left)}
                common_prefix = []
                for t in range(len(by_agent[0])):
                    earlier = sorted(FINAL, key=lambda a: positions[by_agent[a][t]])
                    common_prefix.extend((a, by_agent[a][t]) for a in (*earlier, i, j))
                # The certificate's carriers are 3,4. The two actual carriers
                # may arrive in the opposite order; relabel rows and owners.
                roles = FINAL + (i, j)
                inverse = {old: new for new, old in enumerate(roles)}
                reduced = tuple(u[a] for a in roles)
                reduced_prefix = tuple((inverse[a], h) for a, h in common_prefix)
                route = [tuple(roles[a] for a in state)
                         for state in padded_bridge(reduced, reduced_prefix, tail)]
                if (route[0] != allocation(full_left, m)
                        or route[-1] != allocation(full_right, m)):
                    raise AssertionError("protected braid changed its endpoints")
                return left, right, route
            left.append((i, x))
            right.append((j, y))
            eligible, later = later[0], later[1:]

    def connect(rounds, goods, a, b, prefix):
        if a == b:
            return [allocation(prefix + a, m)]
        if len(prefix) == 5:
            labels = {g: k for k, g in enumerate(goods)}
            small = tuple(tuple(row[g] for g in goods) for row in u)
            aa = tuple((i, labels[g]) for i, g in a)
            bb = tuple((i, labels[g]) for i, g in b)
            result = []
            for state in _construct(small, aa, bb):
                full = list(allocation(prefix, m))
                for g, owner in zip(goods, state):
                    full[g] = owner
                result.append(tuple(full))
            return result
        (i, g), (j, h) = a[0], b[0]
        if (i, g) == (j, h):
            return connect(after_pick(rounds, i), tuple(k for k in goods if k != g),
                           a[1:], b[1:], prefix + ((i, g),))
        if i == j and len(rounds[0]) > 1:
            other = next(k for k in rounds[0] if k != i)
            favorite = favorites(u, other, goods)[0]
            mid = ((other, favorite),) + complete(after_pick(rounds, other),
                                                 tuple(k for k in goods if k != favorite))
            return connect(rounds, goods, a, mid, prefix) + connect(rounds, goods, mid, b, prefix)[1:]
        if i == j:
            remaining = tuple(k for k in goods if k not in (g, h))
            rest = complete(after_pick(after_pick(rounds, i), i), remaining)
            left, right = ((i, g), (i, h)) + rest, ((i, h), (i, g)) + rest
            middle = [allocation(prefix + left, m)]
        elif g != h:
            rest = complete(after_pick(after_pick(rounds, i), j),
                            tuple(k for k in goods if k not in (g, h)))
            left, right = ((i, g), (j, h)) + rest, ((j, h), (i, g)) + rest
            middle = [allocation(prefix + left, m)]
        else:
            left, right, middle = braid(rounds, goods, prefix, i, j, g)
        return (connect(rounds, goods, a, left, prefix) + middle[1:]
                + connect(rounds, goods, right, b, prefix)[1:])

    return connect(rounds_for(5, m, FINAL), tuple(range(m)), start, target, ())


def path(u, start, target, final=FINAL):
    """Connect greedy five-agent 5q+3 witnesses, with arbitrary final labels."""
    validate_profile(u)
    m = len(u[0])
    if len(u) != 5 or m < 8 or m % 5 != 3:
        raise ValueError("need five agents and 5q+3 goods, q>=1")
    rounds = rounds_for(5, m, final)
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    roles = tuple(sorted(final)) + tuple(i for i in range(5) if i not in final)
    inverse = {old: new for new, old in enumerate(roles)}
    reduced = tuple(u[a] for a in roles)
    a = tuple((inverse[i], g) for i, g in start)
    b = tuple((inverse[i], g) for i, g in target)
    result = []
    for state in _construct(reduced, a, b):
        full = tuple(roles[i] for i in state)
        if not result or full != result[-1]:
            result.append(full)
    if (result[0] != allocation(start, m) or result[-1] != allocation(target, m)
            or any(not ef1(u, state) for state in result)
            or any(not exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("constructed route failed its endpoint, fairness or exchange check")
    return result


def example(q):
    """An uncancelled braid lasting q rounds; no initial complete round agrees."""
    if type(q) is not int or q < 1:
        raise ValueError("round count must be positive")
    m = 5 * q + 3
    u = [[0] * m for _ in range(5)]
    left, right = [], []
    previous_x = previous_y = 0
    for t in range(q):
        anchors = tuple(1 + 5 * t + i for i in range(3))
        x, y = 4 + 5 * t, 5 + 5 * t
        for i, h in enumerate(anchors):
            u[i][h] = 100 * (q - t)
        u[3][x], u[3][y] = 10 * (q - t) + 1, 10 * (q - t)
        u[4][x], u[4][y] = 10 * (q - t), 10 * (q - t) + 1
        left.append((3, previous_x))
        right.append((4, previous_y))
        left.extend(zip(FINAL, anchors))
        right.extend(zip(FINAL, anchors))
        left.append((4, y))
        right.append((3, x))
        previous_x, previous_y = x, y
    u[3][0] = u[4][0] = 10 * q + 20
    left.extend(((0, previous_x), (1, m - 2), (2, m - 1)))
    right.extend(((0, previous_y), (1, m - 2), (2, m - 1)))
    return tuple(map(tuple, u)), tuple(left), tuple(right)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=2)
    args = parser.parse_args()
    u, a, b = example(args.rounds)
    route = path(u, a, b)
    print(json.dumps({"goods": len(u[0]), "exchanges": len(route) - 1,
                      "path": ["".join(map(str, state)) for state in route],
                      "method": "round/prefix recursion with a certified protected bridge"}, indent=2))
