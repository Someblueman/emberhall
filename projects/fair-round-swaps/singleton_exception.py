"""Full one-pair EF1 connectivity with one arbitrary singleton utility row."""
from __future__ import annotations

import json

from binary_one_pair import path as binary_path
from single_extra import one_extra_bundles
from swaps import ef1, exchange, validate_profile


def reduced_profile(utilities, exceptional):
    validate_profile(utilities)
    n, m = len(utilities), len(utilities[0])
    if m != n + 1 or type(exceptional) is not int or exceptional not in range(1, n):
        raise ValueError("need one pair and a distinct exceptional singleton")
    rows = [(0,) * m]
    for i, row in enumerate(utilities[1:], 1):
        if i == exceptional:
            rows.append(tuple(row))
        else:
            if len(set(row)) > 2:
                raise ValueError("all other singleton rows must have at most two values")
            rows.append(tuple(int(v > min(row)) for v in row))
    return tuple(rows)


def _swap(state, g, h):
    result = list(state)
    result[g], result[h] = result[h], result[g]
    return tuple(result)


def favorite_path(utilities, start, exceptional=1):
    """Give the exceptional singleton its fixed favorite in at most b+2 swaps.

    b is the number of binary singleton recipients. Its utility need not be
    monotone before reaching that favorite. Nonterminal repairs strictly
    increase the number of satisfied binary recipients.
    """
    u = reduced_profile(utilities, exceptional)
    state = tuple(start)
    _, doubled = one_extra_bundles(u, state)
    if doubled != 0:
        raise ValueError("recipient zero must own the pair")
    if not ef1(u, state):
        raise ValueError("start must be EF1")
    a = exceptional
    binary = tuple(i for i in range(1, len(u)) if i != a)
    h = max(range(len(state)), key=lambda g: (u[a][g], -g))
    route, repairs, transfers = [state], 0, 0

    def satisfied():
        return sum(u[i][state.index(i)] for i in binary)

    def move(g, t, *, repair=False):
        nonlocal state, repairs
        before = satisfied()
        target = _swap(state, g, t)
        assert exchange(state, target) and ef1(u, target)
        state = target
        route.append(state)
        if repair:
            assert satisfied() > before
            repairs += 1
            assert repairs <= len(binary)

    while state[h] != a:
        z = state.index(a)
        pair = tuple(g for g, owner in enumerate(state) if owner == 0)
        own = {i: state.index(i) for i in binary}
        if ef1(u, _swap(state, z, h)):
            move(z, h)
            break
        if state[h] == 0:
            q = next(g for g in pair if g != h)
            # The failed favorite exchange has an unsatisfied binary blocker.
            j = next(i for i in binary if not u[i][own[i]] and u[i][z] and u[i][q])
            x = own[j]
            if u[a][x] >= u[a][q]:
                move(z, x, repair=True)
            elif ef1(u, _swap(state, q, x)):
                move(q, x, repair=True)
            else:
                k = next(i for i in binary if not u[i][own[i]] and u[i][h]
                         and u[i][x] and not u[i][q])
                move(x, own[k], repair=True)
        else:
            d = state[h]
            assert d in binary and u[d][h] and not u[d][z]
            assert all(u[d][g] for g in pair)
            q = min(pair, key=lambda g: (u[a][g], g))
            p = next(g for g in pair if g != q)
            if ef1(u, _swap(state, h, p)):
                move(h, p)
                transfers += 1
                assert transfers <= 1
                continue
            j = next(i for i in binary if not u[i][own[i]] and u[i][h]
                     and u[i][q] and not u[i][p])
            x = own[j]
            if u[d][x]:
                move(h, x)
                move(z, h)
                break
            if ef1(u, _swap(state, p, x)):
                move(p, x)
                move(z, h)
                break
            k = next(i for i in binary if not u[i][own[i]] and u[i][q]
                     and u[i][x] and not u[i][p])
            move(x, own[k], repair=True)
    assert len(route) - 1 <= len(binary) + 2
    assert state[h] == a
    return tuple(route)


def path(utilities, start, target, exceptional=1):
    """Connect any fair endpoints in this domain; no greedy premise is used."""
    u = reduced_profile(utilities, exceptional)
    left = favorite_path(utilities, start, exceptional)
    right = favorite_path(utilities, target, exceptional)
    h = left[-1].index(exceptional)
    assert right[-1].index(exceptional) == h
    agents = tuple(i for i in range(len(u)) if i != exceptional)
    goods = tuple(g for g in range(len(u[0])) if g != h)
    agent_index = {a: i for i, a in enumerate(agents)}
    sub_u = tuple(tuple(u[a][g] for g in goods) for a in agents)
    sub_start = tuple(agent_index[left[-1][g]] for g in goods)
    sub_target = tuple(agent_index[right[-1][g]] for g in goods)
    if len(agents) == 1:
        assert sub_start == sub_target
        middle = (left[-1],)
    else:
        middle = []
        for sub_state in binary_path(sub_u, sub_start, sub_target):
            lifted = list(left[-1])
            for g, owner in zip(goods, sub_state):
                lifted[g] = agents[owner]
            middle.append(tuple(lifted))
    result = left + tuple(middle[1:]) + right[-2::-1]
    assert result[0] == tuple(start) and result[-1] == tuple(target)
    assert all(ef1(utilities, state) for state in result)
    assert all(exchange(a, b) for a, b in zip(result, result[1:]))
    return result


def main():
    # The two agents disagree about the pair; the exceptional row is ordinally unrestricted.
    u = ((9, 1, 4, 0, 8), (4, 3, 0, 1, 5), (0, 0, 1, 0, 1), (0, 1, 1, 1, 0))
    start, target = (1, 2, 3, 0, 0), (0, 3, 2, 0, 1)
    route = path(u, start, target)
    print(json.dumps({"utility_rows": u, "start": start, "target": target,
                      "favorite_path": favorite_path(u, start), "path": route,
                      "swaps": len(route) - 1,
                      "verified": "original EF1, fixed sizes, single exchanges"}, indent=2))


if __name__ == "__main__":
    main()
