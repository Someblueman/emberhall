"""One final recipient: a full four-agent fiber and five-agent round lift."""

from __future__ import annotations

from collections import deque
from itertools import combinations, permutations
import json

from single_extra import greedy_witness, path as one_extra_path
from swaps import (Allocation, Profile, Witness, after_pick, allocation, ef1,
                   exchange, favorites, rounds_for, validate_profile, validate_witness)


def swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def normalize(u: Profile, start: Allocation) -> list[Allocation]:
    """Improve a four-agent fair state to a neutral-D greedy state."""
    validate_profile(u)
    if (len(u) != 4 or len(u[0]) != 5 or len(start) != 5
            or tuple(start.count(i) for i in range(4)) != (2, 1, 1, 1)
            or not ef1(u, start)):
        raise ValueError("need a fair four-agent (2,1,1,1) allocation")
    route = [start]
    while True:
        a = route[-1]
        spares = [g for g, i in enumerate(a) if i == 0]
        if all(u[i][a.index(i)] >= max(u[i][g] for g in spares) for i in (1, 2, 3)):
            break
        candidate = None
        for i in (1, 2, 3):
            own = a.index(i)
            preferred = max(spares, key=lambda g: u[i][g])
            b = swap(a, own, preferred)
            if u[i][preferred] > u[i][own] and ef1(u, b):
                candidate = b
                break
        if candidate is None:
            for i, j in combinations((1, 2, 3), 2):
                x, y = a.index(i), a.index(j)
                if u[i][y] > u[i][x] and u[j][x] > u[j][y]:
                    candidate = swap(a, x, y)
                    break
        if candidate is None or not ef1(u, candidate):
            raise AssertionError("the blocking graph must contain a two-cycle")
        route.append(candidate)

    while True:
        a = route[-1]
        cycle = next((order for length in (2, 3) for order in permutations((1, 2, 3), length)
                      if all(u[i][a.index(order[k-1])] > u[i][a.index(i)]
                             for k, i in enumerate(order))), None)
        if cycle is None:
            return route
        i = cycle[0]
        spares = [g for g, owner in enumerate(a) if owner == 0]
        buffer = max(spares, key=lambda g: u[i][g])
        carried = a.index(i)
        route.append(swap(a, carried, buffer))
        for j in cycle[1:]:
            own = route[-1].index(j)
            route.append(swap(route[-1], carried, own))
            carried = own
        route.append(swap(route[-1], carried, buffer))
        if not all(ef1(u, state) for state in route[-len(cycle)-1:]):
            raise AssertionError("safe-spare cycle rotation lost EF1")


def five_path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Connect every pair of fair four-agent five-good states, not just greedy ones."""
    left, right = normalize(u, start), normalize(u, target)
    neutral = ((0,) * 5,) + u[1:]
    if any(greedy_witness(neutral, a) is None for a in (left[-1], right[-1])):
        raise AssertionError("acyclic safe-spare state must have a neutral-D witness")
    middle = one_extra_path(neutral, left[-1], right[-1])
    return left[:-1] + middle + right[-2::-1]


def _search(u, start, target, allowed):
    if not all(allowed(a) and ef1(u, a) for a in (start, target)):
        raise ValueError("need fair endpoints in the allowed graph")
    parents = {start: None}
    queue = deque([start])
    while queue and target not in parents:
        a = queue.popleft()
        for x, y in combinations(range(len(a)), 2):
            if a[x] == a[y]:
                continue
            b = swap(a, x, y)
            if b not in parents and allowed(b) and ef1(u, b):
                parents[b] = a
                queue.append(b)
    if target not in parents:
        raise AssertionError("proved fair endpoints are disconnected")
    result = [target]
    while parents[result[-1]] is not None:
        result.append(parents[result[-1]])
    return result[::-1]


def protected_path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Keep good 0 with singleton 1 or 2 in the full protected six-good graph."""
    validate_profile(u)
    if len(u) != 5 or len(u[0]) != 6 or any(u[i][0] < max(u[i]) for i in (1, 2)):
        raise ValueError("need six goods and a common favorite of carriers 1 and 2")
    if any(tuple(a.count(i) for i in range(5)) != (2, 1, 1, 1, 1)
           for a in (start, target)):
        raise ValueError("need size vector (2,1,1,1,1)")
    return _search(u, start, target, lambda a: a[0] in (1, 2))


def padded_path(u: Profile, prefix: Witness, tail: tuple[int, ...],
                start: Allocation, target: Allocation, carriers=(1, 2)) -> list[Allocation]:
    validate_profile(u)
    m = len(u[0])
    if (len(u) != 5 or m < 6 or m % 5 != 1 or len(tail) != 6
            or len(set(tail)) != 6 or any(type(g) is not int or g not in range(m) for g in tail)
            or len(prefix) != m-6 or len(carriers) != 2 or len(set(carriers)) != 2
            or not set(carriers) <= {1, 2, 3, 4}):
        raise ValueError("need a complete-round prefix and six distinct tail goods")
    remaining = tuple(g for g in range(m) if g != tail[0])
    common = [[] for _ in range(5)]
    eligible = set(range(5))
    for i, g in prefix:
        if i not in eligible or g not in remaining or g not in favorites(u, i, remaining):
            raise ValueError("prefix is not greedy with the protected good omitted")
        common[i].append(g); eligible.remove(i)
        if not eligible:
            eligible = set(range(5))
        remaining = tuple(h for h in remaining if h != g)
    if set(remaining) != set(tail[1:]) or eligible != set(range(5)):
        raise ValueError("prefix does not leave the declared tail")
    if any(sum(u[a][g] for g in common[a]) < sum(u[a][g] for g in common[b])
           for a in range(5) for b in carriers if a != b):
        raise ValueError("prefix bundles do not dominate the carrier bundles")
    roles = (0, *carriers, *(i for i in range(1, 5) if i not in carriers))
    inverse = {old: new for new, old in enumerate(roles)}
    if any(len(a) != 6 or any(type(i) is not int or i not in inverse for i in a)
           for a in (start, target)):
        raise ValueError("need two complete six-good allocations")
    small = tuple(tuple(u[i][g] for g in tail) for i in roles)
    aa, bb = (tuple(inverse[i] for i in a) for a in (start, target))
    result = []
    for a in protected_path(small, aa, bb):
        full = list(allocation(prefix, m))
        for g, owner in zip(tail, a):
            full[g] = roles[owner]
        full = tuple(full)
        if not ef1(u, full):
            raise AssertionError("protected padding lost EF1")
        result.append(full)
    return result


# The same round/prefix induction as the frozen two-final constructor.
def _construct(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Outer round induction and inner fixed-first-round-prefix induction."""
    m = len(u[0])
    final = (0,)
    if m == 6:
        # A single final good has no assignment choice.
        return one_extra_path(u, allocation(start, m), allocation(target, m))

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
    """Connect five-agent 5q+1 greedy outcomes with final recipient 0."""
    validate_profile(u)
    m = len(u[0])
    if len(u) != 5 or m < 6 or m % 5 != 1:
        raise ValueError("need five agents and 5q+1 goods, q>=1")
    rs = rounds_for(5, m, (0,))
    validate_witness(u, rs, start)
    validate_witness(u, rs, target)
    result = []
    for a in _construct(u, start, target):
        if not result or result[-1] != a:
            result.append(a)
    if not all(ef1(u, a) for a in result):
        raise AssertionError("constructed path leaves EF1")
    if not all(exchange(a, b) for a, b in zip(result, result[1:])):
        raise AssertionError("constructed path includes a non-exchange")
    return result


def main() -> None:
    u = tuple(tuple(range(16, 0, -1)) for _ in range(5))
    left = tuple((i, 5*r+i) for r in range(3) for i in range(5)) + ((0, 15),)
    right = tuple((4-i, 5*r+i) for r in range(3) for i in range(5)) + ((0, 15),)
    route = path(u, left, right)
    print(json.dumps({"goods": 16, "path": ["".join(map(str, a)) for a in route],
                      "exchanges": len(route)-1,
                      "scope": "five agents, 5q+1 goods; other remainders are separate"}, indent=2))


if __name__ == '__main__':
    main()

