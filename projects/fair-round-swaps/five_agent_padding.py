"""Five-agent 5q+2 paths using a protected seven-good bridge.

The round/prefix construction adapts Sorrel's four_agent_lift.py; its proof
and the new protected bridge are in FIVE_AGENT_PADDING.md.
"""

from __future__ import annotations

import json

from five_agent_seven import LEFT, RIGHT, _lend, _path
from swaps import (Allocation, Profile, Witness, after_pick, allocation, ef1,
                   exchange, favorites, rounds_for, validate_profile, validate_witness)


def protected_bridge(u: Profile) -> list[Allocation]:
    """Connect the canonical seven-good braid while g stays with i or j.

    Only the first round must be greedy; the final assignment may be free.
    This does not connect arbitrary EF1 states of the protected graph.
    """
    validate_profile(u)
    if len(u) != 5 or len(u[0]) != 7:
        raise ValueError("need five agents and seven goods")
    required = ((2, 0, (1, 2, 3, 4, 5, 6)), (3, 0, (1, 2, 3, 4, 5, 6)),
                (0, 1, (2, 3, 4, 5, 6)), (1, 2, (3, 4, 5, 6)),
                (4, 3, (4, 5, 6)), (2, 4, (5, 6)), (3, 5, (4, 6)))
    if any(u[i][g] < u[i][h] for i, g, others in required for h in others):
        raise ValueError("first-round braid inequalities do not hold")
    a, b = allocation(LEFT, 7), allocation(RIGHT, 7)
    if u[4][3] >= u[4][2]:
        return _path(u, a, b, lambda s: s[3] == 4 and s[0] in (2, 3))
    left, right = _lend(u, a), _lend(u, b)
    middle = _path(u, left[-1], right[-1], lambda s: s[2] == 4 and s[0] in (2, 3))
    return left[:-1] + middle + right[-2::-1]


def padded_path(u: Profile, prefix: Witness, tail: tuple[int, ...],
                start: Allocation, target: Allocation,
                carriers: tuple[int, int] = (2, 3)) -> list[Allocation]:
    """Lift the protected braid through complete greedy rounds omitting g."""
    validate_profile(u)
    m = len(u[0])
    if (len(u) != 5 or m < 7 or m % 5 != 2 or len(tail) != 7
            or len(set(tail)) != 7 or any(type(g) is not int or g not in range(m) for g in tail)
            or len(prefix) != m - 7 or len(carriers) != 2
            or len(set(carriers)) != 2 or not set(carriers) <= {2, 3, 4}):
        raise ValueError("need five agents, two singleton carriers and seven tail goods")
    remaining = tuple(g for g in range(m) if g != tail[0])
    eligible = set(range(5))
    common = [[] for _ in range(5)]
    for i, g in prefix:
        if i not in eligible or g not in remaining or g not in favorites(u, i, remaining):
            raise ValueError("prefix is not greedy with the protected good omitted")
        common[i].append(g)
        eligible.remove(i)
        if not eligible:
            eligible = set(range(5))
        remaining = tuple(h for h in remaining if h != g)
    if set(remaining) != set(tail[1:]) or eligible != set(range(5)):
        raise ValueError("prefix does not leave the declared tail")
    if any(sum(u[a][g] for g in common[a]) < sum(u[a][g] for g in common[b])
           for a in range(5) for b in carriers if a != b):
        raise ValueError("prefix bundles do not dominate the carrier bundles")
    if any(len(state) != 7 or any(type(i) is not int or i not in range(5) for i in state)
           for state in (start, target)):
        raise ValueError("need two seven-good allocations with known owners")

    third = next(i for i in (2, 3, 4) if i not in carriers)
    roles = (0, 1, *carriers, third)
    inverse = {old: new for new, old in enumerate(roles)}
    small = tuple(tuple(u[i][g] for g in tail) for i in roles)
    aa, bb = (tuple(inverse[i] for i in state) for state in (start, target))
    left, right = allocation(LEFT, 7), allocation(RIGHT, 7)
    if (aa, bb) == (left, right):
        route = protected_bridge(small)
    elif (aa, bb) == (right, left):
        route = protected_bridge(small)[::-1]
    else:
        raise ValueError("padding accepts the two braid endpoints, not arbitrary fair tails")
    result = []
    for a in route:
        full = list(allocation(prefix, m))
        for g, owner in zip(tail, a):
            full[g] = roles[owner]
        full = tuple(full)
        if not ef1(u, full):
            raise AssertionError("protected padding lost EF1")
        result.append(full)
    return result


def _construct(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Outer round induction and inner fixed-first-round-prefix induction."""
    m = len(u[0])
    final = (0, 1)
    if m == 7:
        # Free final assignments are fair and one swap from greedy assignments.
        return _path(u, allocation(start, m), allocation(target, m), lambda a: True)

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
        while True:
            middle_goods = {}
            for a in eligible:
                if a in (i, j):
                    continue
                h = favorites(u, a, common)[0]
                left.append((a, h))
                right.append((a, h))
                middle_goods[a] = h
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
                if i in final or j in final:
                    carrier = i if i in final else j
                    rest = tuple(zip((a for a in final if a != carrier), common))
                    left = tuple(left) + ((carrier, x),) + rest
                    right = tuple(right) + ((carrier, y),) + rest
                    return left, right, [allocation(prefix + w, m) for w in (left, right)]
                noncarriers = tuple(a for a in range(5) if a not in (i, j))
                tail = (g, *(middle_goods[a] for a in noncarriers), x, y, *common)
                rest = tuple(zip(final[1:], common))
                left = tuple(left) + ((final[0], x),) + rest
                right = tuple(right) + ((final[0], y),) + rest
                full_left, full_right = prefix + left, prefix + right
                by_agent = {a: [h for b, h in full_left if a == b and h not in tail]
                            for a in range(5)}
                positions = {h: index for index, (_, h) in enumerate(full_left)}
                common_prefix = []
                for t in range(len(by_agent[0])):
                    earlier = sorted(noncarriers, key=lambda a: positions[by_agent[a][t]])
                    common_prefix.extend((a, by_agent[a][t]) for a in (*earlier, i, j))
                a, b = allocation(full_left, m), allocation(full_right, m)
                route = padded_path(u, tuple(common_prefix), tail,
                                    tuple(a[h] for h in tail), tuple(b[h] for h in tail), (i, j))
                return left, right, route
            left.append((i, x))
            right.append((j, y))
            eligible, later = later[0], later[1:]

    def connect(rs, goods, a, b, prefix):
        if a == b:
            return [allocation(prefix + a, m)]
        if len(prefix) == 5:
            labels = {g: index for index, g in enumerate(goods)}
            small = tuple(tuple(row[g] for g in goods) for row in u)
            aa = tuple((i, labels[g]) for i, g in a)
            bb = tuple((i, labels[g]) for i, g in b)
            result = []
            for reduced in _construct(small, aa, bb):
                full = list(allocation(prefix, m))
                for g, owner in zip(goods, reduced):
                    full[g] = owner
                result.append(tuple(full))
            return result
        (i, g), (j, h) = a[0], b[0]
        if (i, g) == (j, h):
            return connect(after_pick(rs, i), tuple(k for k in goods if k != g),
                           a[1:], b[1:], prefix + ((i, g),))
        if i == j and len(rs[0]) > 1:
            other = next(k for k in rs[0] if k != i)
            favorite = favorites(u, other, goods)[0]
            mid = ((other, favorite),) + complete(after_pick(rs, other),
                                                 tuple(k for k in goods if k != favorite))
            return connect(rs, goods, a, mid, prefix) + connect(rs, goods, mid, b, prefix)[1:]
        if i == j:
            remaining = tuple(k for k in goods if k not in (g, h))
            rest = complete(after_pick(after_pick(rs, i), i), remaining)
            left, right = ((i, g), (i, h)) + rest, ((i, h), (i, g)) + rest
            middle = [allocation(prefix + left, m)]
        elif g != h:
            rest = complete(after_pick(after_pick(rs, i), j),
                            tuple(k for k in goods if k not in (g, h)))
            left, right = ((i, g), (j, h)) + rest, ((j, h), (i, g)) + rest
            middle = [allocation(prefix + left, m)]
        else:
            left, right, middle = braid(rs, goods, prefix, i, j, g)
        before = connect(rs, goods, a, left, prefix)
        after = connect(rs, goods, right, b, prefix)
        return before + middle[1:] + after[1:]

    return connect(rounds_for(5, m, final), tuple(range(m)), start, target, ())


def path(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Connect five-agent 5q+2 greedy endpoints, with final recipients 0,1."""
    validate_profile(u)
    m = len(u[0])
    if len(u) != 5 or m < 7 or m % 5 != 2:
        raise ValueError("need five agents and 5q+2 goods, q>=1")
    rounds = rounds_for(5, m, (0, 1))
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    result = []
    for a in _construct(u, start, target):
        if not result or a != result[-1]:
            result.append(a)
    if not all(ef1(u, a) for a in result):
        raise AssertionError("constructed path leaves EF1")
    if not all(exchange(a, b) for a, b in zip(result, result[1:])):
        raise AssertionError("constructed path contains a non-exchange")
    return result


def main() -> None:
    # The disagreement survives both complete rounds; no initial round is common.
    u = ((7, 6, 0, 8, 2, 1, 10, 4, 3, 5, 9, 11),
         (10, 4, 11, 7, 1, 0, 3, 5, 2, 8, 6, 9),
         (17, 5, 4, 7, 3, 1, 2, 9, 6, 0, 8, 10),
         (17, 6, 7, 10, 3, 4, 11, 8, 1, 2, 0, 5),
         (3, 5, 9, 11, 8, 10, 4, 0, 7, 1, 6, 2))
    left = ((2, 0), (0, 11), (1, 2), (4, 3), (3, 6), (2, 7),
            (0, 10), (1, 9), (4, 5), (3, 1), (0, 8), (1, 4))
    right = ((3, 0), (0, 11), (1, 2), (4, 3), (2, 7), (3, 6),
             (0, 10), (1, 9), (4, 5), (2, 8), (0, 1), (1, 4))
    route = path(u, left, right)
    print(json.dumps({"goods": 12, "path": ["".join(map(str, a)) for a in route],
                      "exchanges": len(route)-1,
                      "scope": "five agents, 5q+2 goods; other remainders remain open"}, indent=2))


if __name__ == '__main__':
    main()
