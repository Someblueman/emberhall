"""Candidate constructive EF1 paths for n agents and n*q+1 goods."""

from __future__ import annotations

import json

from safe_spare import path as safe_path
from single_extra import one_extra_bundles, path as one_extra_path
from swaps import (Allocation, Profile, Witness, after_pick, allocation, ef1,
                   exchange, favorites, rounds_for, validate_profile, validate_witness)


def _fiber(u: Profile, a: Allocation, b: Allocation, holder: int, good: int
           ) -> list[Allocation]:
    agents = tuple(i for i in range(len(u)) if i != holder)
    goods = tuple(g for g in range(len(a)) if g != good)
    index = {i: j for j, i in enumerate(agents)}
    small = tuple(tuple(u[i][g] for g in goods) for i in agents)
    aa, bb = (tuple(index[state[g]] for g in goods) for state in (a, b))
    result = []
    for reduced in safe_path(small, aa, bb):
        full = [holder] * len(a)
        for g, owner in zip(goods, reduced):
            full[g] = agents[owner]
        result.append(tuple(full))
    return result


def protected_path(u: Profile, start: Allocation, target: Allocation,
                   carriers: tuple[int, int], good: int) -> list[Allocation]:
    """Connect safe-spare fibers while keeping the common favorite on carriers.

    Each endpoint, after removing its favorite holder, must have a safe spare.
    Greedy one-extra endpoints satisfy this premise. Other EF1 states may not.
    """
    _, doubled = one_extra_bundles(u, start)
    _, target_d = one_extra_bundles(u, target)
    n = len(u)
    if (n < 3 or target_d != doubled or len(carriers) != 2
            or len(set(carriers)) != 2 or doubled in carriers
            or any(type(i) is not int or i not in range(n) for i in carriers)
            or type(good) is not int or good not in range(n + 1)
            or any(u[i][good] != max(u[i]) for i in carriers)
            or any(a[good] not in carriers for a in (start, target))):
        raise ValueError("need one double recipient and a favorite shared by two singleton carriers")
    left_holder, right_holder = start[good], target[good]
    if left_holder == right_holder:
        return _fiber(u, start, target, left_holder, good)

    pool = tuple(g for g in range(n + 1) if g != good)
    common = {}
    for i in range(n):
        if i not in (doubled, *carriers):
            chosen = favorites(u, i, pool)[0]
            common[chosen] = i
            pool = tuple(g for g in pool if g != chosen)
    # Two top-two sets on three goods intersect, including with ties.
    pivot = next(g for g in pool
                 if all(u[i][g] >= min(u[i][h] for h in pool if h != g)
                        for i in carriers))
    left = [doubled] * (n + 1)
    for g, owner in common.items():
        left[g] = owner
    left[good], left[pivot] = left_holder, right_holder
    right = left[:]
    right[good], right[pivot] = right_holder, left_holder
    left, right = tuple(left), tuple(right)
    before = _fiber(u, start, left, left_holder, good)
    after = _fiber(u, right, target, right_holder, good)
    return before + after


def padded_path(u: Profile, prefix: Witness, tail: tuple[int, ...],
                start: Allocation, target: Allocation,
                carriers: tuple[int, int]) -> list[Allocation]:
    """Lift a protected one-extra bridge through common complete rounds."""
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (len(carriers) != 2 or len(set(carriers)) != 2
            or any(type(i) is not int or i not in range(n) for i in carriers)
            or len(tail) != n + 1 or len(set(tail)) != n + 1
            or any(type(g) is not int or g not in range(m) for g in tail)
            or len(prefix) != m - n - 1 or len(prefix) % n):
        raise ValueError("need common complete rounds and n+1 distinct tail goods")
    remaining = tuple(g for g in range(m) if g != tail[0])
    eligible = set(range(n))
    common = [[] for _ in range(n)]
    for i, g in prefix:
        if i not in eligible or g not in remaining or g not in favorites(u, i, remaining):
            raise ValueError("prefix is not greedy with the protected good omitted")
        common[i].append(g)
        eligible.remove(i)
        if not eligible:
            eligible = set(range(n))
        remaining = tuple(h for h in remaining if h != g)
    if set(remaining) != set(tail[1:]):
        raise ValueError("prefix does not leave the specified tail")
    if any(sum(u[i][g] for g in common[i]) < sum(u[i][g] for g in common[j])
           for i in range(n) for j in carriers if i != j):
        raise ValueError("common bundles do not dominate both carrier bundles")
    small = tuple(tuple(row[g] for g in tail) for row in u)
    result = []
    for a in protected_path(small, start, target, carriers, 0):
        full = list(allocation(prefix, m))
        for g, owner in zip(tail, a):
            full[g] = owner
        full = tuple(full)
        if not ef1(u, full):
            raise AssertionError("common-prefix padding lost EF1")
        result.append(full)
    return result


def _construct(u: Profile, start: Witness, target: Witness, doubled: int
               ) -> list[Allocation]:
    # Round/prefix organization follows Mica's frozen 2a58b53 five-agent
    # constructor. The protected bridge above replaces its full-fiber lemma.
    n, m = len(u), len(u[0])
    final = (doubled,)
    if m == n + 1:
        return one_extra_path(u, allocation(start, m), allocation(target, m))

    def complete(rs, goods):
        picks = []
        while goods:
            i = rs[0][0]
            g = favorites(u, i, goods)[0]
            picks.append((i, g))
            rs = after_pick(rs, i)
            goods = tuple(h for h in goods if h != g)
        return tuple(picks)

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
                left, right = tuple(left) + ((doubled, x),), tuple(right) + ((doubled, y),)
                if doubled in (i, j):
                    return left, right, [allocation(prefix + w, m) for w in (left, right)]
                noncarriers = tuple(a for a in range(n) if a not in (i, j))
                tail = (g, *(middle_goods[a] for a in noncarriers), x, y)
                full_left, full_right = prefix + left, prefix + right
                by_agent = {a: [h for b, h in full_left if a == b and h not in tail]
                            for a in range(n)}
                positions = {h: index for index, (_, h) in enumerate(full_left)}
                common_prefix = []
                for t in range(len(by_agent[doubled])):
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
        if len(prefix) == n:
            labels = {g: index for index, g in enumerate(goods)}
            small = tuple(tuple(row[g] for g in goods) for row in u)
            aa, bb = (tuple((i, labels[g]) for i, g in w) for w in (a, b))
            result = []
            for reduced in _construct(small, aa, bb, doubled):
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

    return connect(rounds_for(n, m, final), tuple(range(m)), start, target, ())


def path(u: Profile, start: Witness, target: Witness, final_agent: int = 0
         ) -> list[Allocation]:
    """Connect greedy endpoints with n*q+1 goods, q>=1; other remainders excluded."""
    validate_profile(u)
    n, m = len(u), len(u[0])
    if m < n + 1 or m % n != 1 or type(final_agent) is not int or final_agent not in range(n):
        raise ValueError("need n*q+1 goods and one valid final recipient")
    rs = rounds_for(n, m, (final_agent,))
    validate_witness(u, rs, start)
    validate_witness(u, rs, target)
    result = []
    for a in _construct(u, start, target, final_agent):
        if not result or result[-1] != a:
            result.append(a)
    if (result[0] != allocation(start, m) or result[-1] != allocation(target, m)
            or not all(ef1(u, a) for a in result)
            or not all(exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("constructed path failed its endpoint, EF1 or exchange contract")
    return result


def braid_example(n: int = 6, q: int = 3) -> tuple[Profile, Witness, Witness]:
    """Force an uncancelled shared-favorite braid through q complete rounds."""
    if type(n) is not int or n < 3 or type(q) is not int or q < 1:
        raise ValueError("example needs n>=3 and q>=1")
    rows = [[0] * (n * q + 1) for _ in range(n)]
    i, j = n - 2, n - 1
    rows[i][0] = rows[j][0] = q + 1
    left, right = [(i, 0)], [(j, 0)]
    for r in range(q):
        for a in range(n - 2):
            g = 1 + r * n + a
            rows[a][g] = q - r
            left.append((a, g))
            right.append((a, g))
        x, y = 1 + r * n + n - 2, 1 + r * n + n - 1
        rows[i][x] = rows[j][y] = q - r
        left.append((j, y))
        right.append((i, x))
        left.append((i if r < q - 1 else 0, x))
        right.append((j if r < q - 1 else 0, y))
    return tuple(map(tuple, rows)), tuple(left), tuple(right)


def main() -> None:
    u, start, target = braid_example()
    route = path(u, start, target)
    print(json.dumps({"agents": len(u), "goods": len(u[0]),
                      "path": ["".join(map(str, a)) for a in route],
                      "exchanges": len(route) - 1,
                      "scope": "candidate n*q+1 theorem; other remainders remain separate"},
                     indent=2))


if __name__ == '__main__':
    main()
