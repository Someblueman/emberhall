"""Four-agent 4q+2 EF1 paths; the universal argument is in FOUR_AGENT_LIFT.md.

The fixed-size searches are exact and use EF1 states outside picking outcomes.
The small protected bridge, rather than unrestricted tail lifting, is the
constructive step that permits the mathematical induction.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations

from swaps import (Allocation, Profile, Witness, after_pick, allocation, ef1,
                   exchange, favorites, rounds_for, validate_profile, validate_witness)


def _search(u: Profile, start: Allocation, target: Allocation, allowed=None):
    n, m = len(u), len(u[0])
    if any(not ef1(u, a) for a in (start, target)):
        raise ValueError("both allocations must be EF1")
    sizes = tuple(start.count(i) for i in range(n))
    if tuple(target.count(i) for i in range(n)) != sizes:
        raise ValueError("different size vectors")
    if allowed is not None and any(not allowed(a) for a in (start, target)):
        raise ValueError("endpoint violates the protected-good condition")
    parents = {start: None}
    queue = deque([start])
    while queue and target not in parents:
        a = queue.popleft()
        for g, h in combinations(range(m), 2):
            if a[g] == a[h]:
                continue
            b = list(a)
            b[g], b[h] = b[h], b[g]
            b = tuple(b)
            if b not in parents and (allowed is None or allowed(b)) and ef1(u, b):
                parents[b] = a
                queue.append(b)
    if target not in parents:
        raise AssertionError("claimed connected endpoints are disconnected")
    result = [target]
    while parents[result[-1]] is not None:
        result.append(parents[result[-1]])
    return list(reversed(result))


def five_path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Connect any EF1 allocations with three agents and sizes (2,2,1)."""
    validate_profile(u)
    if len(u) != 3 or len(u[0]) != 5:
        raise ValueError("need three agents and five goods")
    if any(tuple(a.count(i) for i in range(3)) != (2, 2, 1) for a in (start, target)):
        raise ValueError("need size vector (2,2,1)")
    return _search(u, start, target)


def carrier_path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Keep good 0 with singleton 2 or 3, who must both rank it maximal."""
    validate_profile(u)
    if len(u) != 4 or len(u[0]) != 6:
        raise ValueError("need four agents and six goods")
    if any(u[i][0] < max(u[i]) for i in (2, 3)):
        raise ValueError("good 0 must be a favorite of both singleton agents")
    if any(tuple(a.count(i) for i in range(4)) != (2, 2, 1, 1)
           for a in (start, target)):
        raise ValueError("need size vector (2,2,1,1)")
    return _search(u, start, target, lambda a: a[0] in (2, 3))


def padded_path(u: Profile, prefix: Witness, tail: tuple[int, ...],
                start: Allocation, target: Allocation,
                carriers: tuple[int, int] = (2, 3)) -> list[Allocation]:
    """Lift a protected six-good path after a greedy prefix that omits g.

    `tail[0]` is g. `start` and `target` refer to the six positions in `tail`.
    The common prefix must satisfy the carrier-dominance hypothesis in the
    proof, which this function checks exactly rather than presuming it.
    """
    validate_profile(u)
    m = len(u[0])
    if len(carriers) != 2 or set(carriers) != {2, 3}:
        raise ValueError("two-final padding requires singleton carriers 2 and 3")
    if (len(u) != 4 or m % 4 != 2 or m < 6 or len(tail) != 6
            or len(set(tail)) != 6 or any(type(g) is not int or g not in range(m) for g in tail)
            or len(prefix) != m - 6):
        raise ValueError("need a complete-round prefix and six distinct tail goods")
    remaining = tuple(g for g in range(m) if g != tail[0])
    eligible = set(range(4))
    common = [[] for _ in range(4)]
    for i, g in prefix:
        if i not in eligible or g not in remaining or g not in favorites(u, i, remaining):
            raise ValueError("prefix is not greedy with the protected good omitted")
        common[i].append(g)
        eligible.remove(i)
        if not eligible:
            eligible = set(range(4))
        remaining = tuple(h for h in remaining if h != g)
    if set(remaining) != set(tail[1:]) or eligible != set(range(4)):
        raise ValueError("prefix does not leave the declared tail")
    if any(sum(u[a][g] for g in common[a]) < sum(u[a][g] for g in common[b])
           for a in range(4) for b in (2, 3) if a != b):
        raise ValueError("common bundles do not dominate the carrier bundles")
    small = tuple(tuple(row[g] for g in tail) for row in u)
    result = []
    for a in carrier_path(small, start, target):
        full = [-1] * m
        for i, goods in enumerate(common):
            for g in goods:
                full[g] = i
        for g, owner in zip(tail, a):
            full[g] = owner
        full = tuple(full)
        if not ef1(u, full):
            raise AssertionError("protected padding lemma violated")
        result.append(full)
    if not all(exchange(a, b) for a, b in zip(result, result[1:])):
        raise AssertionError("padding changed an exchange")
    return result


def _construct(u: Profile, start: Witness, target: Witness,
               final: tuple[int, ...], protected) -> list[Allocation]:
    """The outer round induction and inner fixed-first-round-prefix induction."""
    m = len(u[0])
    if m == 4 + len(final):
        return _search(u, allocation(start, m), allocation(target, m))

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
                noncarriers = tuple(a for a in range(4) if a not in (i, j))
                tail = (g, *(middle_goods[a] for a in noncarriers), x, y, *common)
                rest = tuple(zip(final[1:], common))
                left = tuple(left) + ((final[0], x),) + rest
                right = tuple(right) + ((final[0], y),) + rest
                full_left, full_right = prefix + left, prefix + right
                # The common bundles form greedy rounds after omitting g.
                by_agent = {a: [h for b, h in full_left if a == b and h not in tail]
                            for a in range(4)}
                positions = {h: index for index, (_, h) in enumerate(full_left)}
                common_prefix = []
                for t in range(len(by_agent[0])):
                    earlier = sorted(noncarriers, key=lambda a: positions[by_agent[a][t]])
                    common_prefix.extend((a, by_agent[a][t]) for a in (*earlier, i, j))
                a, b = allocation(full_left, m), allocation(full_right, m)
                route = protected(u, tuple(common_prefix), tail,
                                  tuple(a[h] for h in tail), tuple(b[h] for h in tail), (i, j))
                return left, right, route
            left.append((i, x))
            right.append((j, y))
            eligible, later = later[0], later[1:]

    def connect(rs, goods, a, b, prefix):
        if a == b:
            return [allocation(prefix + a, m)]
        if len(prefix) == 4:
            labels = {g: index for index, g in enumerate(goods)}
            small = tuple(tuple(row[g] for g in goods) for row in u)
            aa = tuple((i, labels[g]) for i, g in a)
            bb = tuple((i, labels[g]) for i, g in b)
            result = []
            for reduced in _construct(small, aa, bb, final, protected):
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

    return connect(rounds_for(4, m, final), tuple(range(m)), start, target, ())


def path(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Construct an EF1 path for four-agent 4q+2 greedy endpoints, q>=1.

    Final recipients are 0,1. Only six-good subproblems use graph search;
    there is no shortest-path or polynomial complexity guarantee.
    """
    validate_profile(u)
    m = len(u[0])
    if len(u) != 4 or m < 6 or m % 4 != 2:
        raise ValueError("need four agents and 4q+2 goods with q>=1")
    rounds = rounds_for(4, m, (0, 1))
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    result = []
    for a in _construct(u, start, target, (0, 1), padded_path):
        if not result or a != result[-1]:
            result.append(a)
    if not all(ef1(u, a) for a in result):
        raise AssertionError("constructed path leaves EF1")
    if not all(exchange(a, b) for a, b in zip(result, result[1:])):
        raise AssertionError("constructed path has a non-exchange step")
    return result


EXAMPLE: Profile = (
    (0, 2, 0, 5, 2, 2, 0, 2, 5, 1),
    (1, 100, 1, 5, 1, 1, 0, 20, 100, 20),
    (0, 100, 0, 2, 100, 20, 5, 2, 5, 5),
    (2, 5, 5, 5, 20, 0, 0, 20, 20, 1),
)
PREFIX = ((0, 3), (1, 1), (2, 5), (3, 7))
TAIL = (4, 8, 9, 6, 2, 0)
LEFT = (2, 0, 1, 0, 3, 1)
RIGHT = (3, 0, 1, 2, 0, 1)


if __name__ == "__main__":
    from two_final_extension import bridge

    small = tuple(tuple(row[g] for g in TAIL) for row in EXAMPLE)
    naive = bridge(small)[1]
    wrong = list(allocation(PREFIX, 10))
    for g, owner in zip(TAIL, naive):
        wrong[g] = owner
    assert not ef1(EXAMPLE, tuple(wrong))
    print("Unrestricted six-good lift fails: agent 2 has 25; removing either 100 leaves 100")
    result = padded_path(EXAMPLE, PREFIX, TAIL, LEFT, RIGHT)
    print("Protected ten-good bridge:")
    for index, a in enumerate(result):
        print(f"{index}: {''.join(map(str, a))}")
    print(f"Verified: {len(result)-1} exchanges, every full allocation EF1")
    print("Reconstructed theorem: four agents, 4q+2 goods; general agent count remains open")
