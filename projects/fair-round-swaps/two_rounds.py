"""Candidate EF1 paths for three-agent greedy outcomes with 3q+1 goods."""

from __future__ import annotations

from fractions import Fraction

from swaps import (Allocation, Profile, Witness, after_pick, allocation, ef1, exchange,
                   rounds_for, validate_profile, validate_witness)


def _swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def burden(row, goods) -> int | Fraction:
    values = [row[g] for g in goods]
    return sum(values) - max(values, default=0)


def tail_bridge(u: Profile, a: Allocation, b: Allocation, *, shared: int,
                pivot: int, x: int, y: int) -> list[Allocation]:
    """Use a common last-round pick as the pivot under the stated sum bounds.

    Roles are D=0, i=1, j=2. See TWO_ROUNDS.md for the exact hypotheses.
    """
    validate_profile(u)
    if len(u) != 3 or not ef1(u, a) or not ef1(u, b):
        raise ValueError("need two EF1 endpoints for three agents")
    if (a[shared], b[shared], a[x], b[x], a[y], b[y]) != (1, 2, 0, 1, 2, 0):
        raise ValueError("endpoints do not have the shared-favorite three-cycle")
    if a[pivot] != 0 or b[pivot] != 0 or len({shared, pivot, x, y}) != 4:
        raise ValueError("pivot must be a distinct common good of the double recipient")
    common = [tuple(g for g in range(len(a)) if a[g] == b[g] == i) for i in range(3)]
    p, own_i, own_j = tuple(g for g in common[0] if g != pivot), common[1], common[2]
    if any(a[g] != b[g] for g in range(len(a)) if g not in (shared, x, y)):
        raise ValueError("unexpected differences outside the three-cycle")
    total = lambda i, goods: sum(u[i][g] for g in goods)
    hypotheses = (
        total(1, own_i) >= total(1, own_j),
        total(2, own_j) >= total(2, own_i),
        total(0, p) >= total(0, own_i),
        total(0, p) >= total(0, own_j),
        total(1, own_i) >= burden(u[1], p + (x,)),
        total(2, own_j) >= burden(u[2], p + (y,)),
        all(u[i][shared] >= max(u[i][x], u[i][y]) for i in (1, 2)),
    )
    if not all(hypotheses):
        raise ValueError("pivot does not satisfy the bridge sum bounds")
    c = _swap(a, shared, y)
    e = _swap(a, x, y)
    if ef1(u, c):
        result = [a, c, b]
    elif ef1(u, e):
        result = [a, e, b]
    else:
        c = _swap(a, pivot, y)
        result = [a, c, _swap(c, shared, pivot), b]
    assert all(ef1(u, state) for state in result)
    assert all(exchange(left, right) for left, right in zip(result, result[1:]))
    return result


def braid(u: Profile, shared: int = 0) -> tuple[Witness, Witness, list[Allocation]]:
    """Build two canonical three-agent braid endpoints and connect them.

    There are q full rounds and a final pick for D=0. Agents 1 and 2 must
    share a favorite. This only connects the constructed endpoints.
    """
    validate_profile(u)
    m = len(u[0])
    if len(u) != 3 or m < 4 or (m - 1) % 3 or type(shared) is not int or shared not in range(m):
        raise ValueError("need three agents, 3q+1 goods and an existing shared good")
    if any(u[i][shared] != max(u[i]) for i in (1, 2)):
        raise ValueError("the shared good must maximize both carrier utilities")
    wa, wb, result = _paired(u, (), 1, 2, shared)
    rounds = rounds_for(3, m, (0,))
    validate_witness(u, rounds, wa)
    validate_witness(u, rounds, wb)
    assert all(ef1(u, state) for state in result)
    assert all(exchange(left, right) for left, right in zip(result, result[1:]))
    return wa, wb, result


def _complete(u: Profile, prefix: Witness) -> Witness:
    rs = rounds_for(3, len(u[0]), (0,))
    pool = set(range(len(u[0])))
    result = list(prefix)
    for i, g in prefix:
        if i not in rs[0] or g not in pool or u[i][g] != max(u[i][h] for h in pool):
            raise AssertionError("invalid greedy prefix")
        pool.remove(g)
        rs = after_pick(rs, i)
    while rs:
        i = min(rs[0])
        g = max(sorted(pool), key=lambda h: u[i][h])
        result.append((i, g))
        pool.remove(g)
        rs = after_pick(rs, i)
    return tuple(result)


def _paired(u: Profile, prefix: Witness, i: int, j: int, shared: int):
    """Shared-favorite bridge following a fixed first-round prefix."""
    q = (len(u[0]) - 1) // 3
    words = [list(prefix), list(prefix)]
    pools = [set(range(len(u[0]))) - {g for _, g in prefix} for _ in range(2)]
    x = y = shared
    eligible = set(range(3)) - {a for a, _ in prefix}
    closed = False

    def pick(which, agent, good):
        assert good in pools[which] and u[agent][good] == max(u[agent][h] for h in pools[which])
        words[which].append((agent, good))
        pools[which].remove(good)

    for round_index in range(q):
        pick(0, i, x)
        pick(1, j, y)
        assert pools[0] == pools[1]
        for agent in sorted(eligible - {i, j}):
            good = max(sorted(pools[0]), key=lambda h: u[agent][h])
            pick(0, agent, good)
            pick(1, agent, good)
        y = max(sorted(pools[0]), key=lambda h: u[j][h])
        x = max(sorted(pools[1]), key=lambda h: u[i][h])
        pick(0, j, y)
        pick(1, i, x)
        if x == y:
            closed = True
            break
        eligible = set(range(3))
    wa, wb = _complete(u, tuple(words[0])), _complete(u, tuple(words[1]))
    a, b = allocation(wa, len(u[0])), allocation(wb, len(u[0]))
    if closed or 0 in (i, j):
        route = [a, b]
    else:
        pivot = [good for agent, good in wa if agent == 0][-2]
        if i == 1:
            route = tail_bridge(u, a, b, shared=shared, pivot=pivot, x=x, y=y)
        else:
            route = list(reversed(tail_bridge(u, b, a, shared=shared, pivot=pivot, x=y, y=x)))
    return wa, wb, route


def _join(a, b):
    assert a[-1] == b[0]
    return a + b[1:]


def _connect_prefix(u: Profile, wa: Witness, wb: Witness, depth: int) -> list[Allocation]:
    """Inner induction on the common prefix of the first complete round."""
    m = len(u[0])
    a, b = allocation(wa, m), allocation(wb, m)
    if a == b:
        return [a]
    if m == 4:
        from single_extra import path as one_extra_path
        return one_extra_path(u, a, b)
    prefix = wa[:depth]
    assert prefix == wb[:depth]
    if depth == 3:
        removed = {g for _, g in prefix}
        goods = [g for g in range(m) if g not in removed]
        index = {g: k for k, g in enumerate(goods)}
        smaller = tuple(tuple(row[g] for g in goods) for row in u)
        va = tuple((i, index[g]) for i, g in wa[3:])
        vb = tuple((i, index[g]) for i, g in wb[3:])
        lifted = []
        for state in _connect_prefix(smaller, va, vb, 0):
            full = [-1] * m
            for i, g in prefix:
                full[g] = i
            for g, i in zip(goods, state):
                full[g] = i
            lifted.append(tuple(full))
        return lifted
    i, g = wa[depth]
    j, h = wb[depth]
    if (i, g) == (j, h):
        return _connect_prefix(u, wa, wb, depth + 1)
    eligible = set(range(3)) - {agent for agent, _ in prefix}
    remaining = set(range(m)) - {good for _, good in prefix}
    if i == j and len(eligible) > 1:
        other = min(eligible - {i})
        good = max(sorted(remaining), key=lambda x: u[other][x])
        middle = _complete(u, prefix + ((other, good),))
        return _join(_connect_prefix(u, wa, middle, depth),
                     _connect_prefix(u, middle, wb, depth))
    if i == j:  # Last first-round pick: take both tied goods across the boundary.
        ra = _complete(u, prefix + ((i, g), (i, h)))
        rb = prefix + ((i, h), (i, g)) + ra[depth + 2:]
        route = [allocation(ra, m)]
    elif g != h:
        ra = _complete(u, prefix + ((i, g), (j, h)))
        rb = prefix + ((j, h), (i, g)) + ra[depth + 2:]
        route = [allocation(ra, m)]
    else:
        ra, rb, route = _paired(u, prefix, i, j, g)
    return _join(_join(_connect_prefix(u, wa, ra, depth), route),
                 _connect_prefix(u, rb, wb, depth))


def path(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Candidate EF1 path for three agents and 3q+1 goods, extra recipient 0."""
    validate_profile(u)
    if len(u) != 3 or len(u[0]) < 4 or (len(u[0]) - 1) % 3:
        raise ValueError("need three agents and 3q+1 goods")
    rounds = rounds_for(3, len(u[0]), (0,))
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    result = _connect_prefix(u, start, target, 0)
    result = [a for k, a in enumerate(result) if k == 0 or a != result[k - 1]]
    assert result[0] == allocation(start, len(u[0])) and result[-1] == allocation(target, len(u[0]))
    assert all(ef1(u, a) for a in result)
    assert all(exchange(a, b) for a, b in zip(result, result[1:]))
    return result


EXAMPLE: Profile = (
    (0, 100, 90, 90, 10, 1, 1),
    (100, 90, 20, 61, 60, 30, 50),
    (100, 90, 61, 20, 60, 50, 30),
)


def main() -> None:
    wa, wb, _ = braid(EXAMPLE)
    result = path(EXAMPLE, wa, wb)
    print("three agents, seven goods: two complete greedy rounds and one final pick")
    print("left picks:", " ".join(f"{i}:{g}" for i, g in wa))
    print("right picks:", " ".join(f"{i}:{g}" for i, g in wb))
    for index, state in enumerate(result):
        print(f"{index}: {''.join(map(str, state))}")
    print(f"Verified: {len(result) - 1} exchanges, all states EF1")
    print("Scope: candidate three-agent 3q+1 theorem; general agent count remains open")


if __name__ == "__main__":
    main()
