"""Exact one-extra-good boundary; see SINGLE_EXTRA.md for proof and limits."""

from __future__ import annotations

from itertools import combinations

from swaps import (Allocation, Profile, Witness, allocation, components, ef1, exchange,
                   states_with_sizes, validate_profile)


def one_extra_bundles(u: Profile, a: Allocation) -> tuple[list[tuple[int, ...]], int]:
    validate_profile(u)
    n, m = len(u), len(u[0])
    if m != n + 1 or len(a) != m or any(type(i) is not int or i not in range(n) for i in a):
        raise ValueError("need n+1 goods assigned to n agents")
    bundles = [tuple(g for g, owner in enumerate(a) if owner == i) for i in range(n)]
    doubled = [i for i, goods in enumerate(bundles) if len(goods) == 2]
    if len(doubled) != 1 or any(len(bundles[i]) != 1 for i in range(n) if i not in doubled):
        raise ValueError("need one double bundle and one good for every other agent")
    return bundles, doubled[0]


def isolated_family(n: int, *, strict: bool = False) -> tuple[Profile, Allocation, Allocation]:
    """An isolated EF1 state and a second EF1 state, for every n >= 5.

    Neither endpoint is a greedy picking outcome. This is deliberately NOT a
    counterexample to connectivity between greedy endpoints.
    """
    if type(n) is not int or n < 5:
        raise ValueError("the isolated family requires at least five agents")
    k = n - 1
    rows = [(0,) * (n + 1)]
    for i in range(k):
        row = [0] * (n + 1)
        preferred = k + (i % 2 if i < 4 else 0)
        row[preferred], row[2 * k + 1 - preferred], row[i] = 4, 1, 2
        if i < 4:
            row[(i + 1) % 4] = 3
        if i == 1:
            for g in range(4, k):
                row[g] = 3
        rows.append(tuple(row))
    if strict:
        # Break ties inside each tier while retaining every strict tier gap.
        rows = [tuple((n + 1) * value + g for g, value in enumerate(row))
                for row in rows]
    initial = tuple(range(1, n)) + (0, 0)
    rotated = (4, 1, 2, 3) + tuple(range(5, n)) + (0, 0)
    return tuple(rows), initial, rotated


def greedy_witness(u: Profile, a: Allocation) -> Witness | None:
    """Recognize a one-full-round-plus-one-pick outcome, including arbitrary ties.

    For each possible final good, first-round picks impose a directed precedence
    graph. A topological ordering exists exactly when those picks can be greedy.
    """
    bundles, d = one_extra_bundles(u, a)
    n = len(u)
    for final in bundles[d]:
        picks = tuple(next(g for g in bundle if i != d or g != final)
                      for i, bundle in enumerate(bundles))
        if any(u[i][picks[i]] < u[i][final] for i in range(n)):
            continue
        predecessors = [set(j for j in range(n) if u[i][picks[j]] > u[i][picks[i]])
                        for i in range(n)]
        order: list[int] = []
        remaining = set(range(n))
        while remaining:
            ready = [i for i in sorted(remaining) if not predecessors[i] & remaining]
            if not ready:
                break
            first = ready[0]
            order.append(first)
            remaining.remove(first)
        if not remaining:
            return tuple((i, picks[i]) for i in order) + ((d, final),)
    return None


def neighbor_up_to_four(u: Profile, a: Allocation) -> Allocation:
    """Construct the neighbor proved to exist for 2 <= n <= 4 in this model."""
    bundles, d = one_extra_bundles(u, a)
    if len(u) > 4 or not ef1(u, a):
        raise ValueError("need an EF1 state with at most four agents")
    singletons = [i for i in range(len(u)) if i != d]
    for i in singletons:
        g = max(bundles[d], key=lambda g: u[i][g])
        own = bundles[i][0]
        b = list(a)
        b[own], b[g] = b[g], b[own]
        if ef1(u, tuple(b)):
            return tuple(b)
    for i, j in combinations(singletons, 2):
        x, y = bundles[i][0], bundles[j][0]
        if u[i][y] > u[i][x] and u[j][x] > u[j][y]:
            b = list(a)
            b[x], b[y] = b[y], b[x]
            return tuple(b)
    raise AssertionError("the opposite-color blocker graph must have a two-cycle")


def _swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def _finish(u: Profile, prefix: Witness, d: int) -> Witness:
    """Complete a valid first-round prefix with deterministic maximizing picks."""
    picks = list(prefix)
    goods = set(range(len(u[0]))) - {g for _, g in prefix}
    used = {i for i, _ in prefix}
    for i in range(len(u)):
        if i not in used:
            g = max(sorted(goods), key=lambda g: u[i][g])
            picks.append((i, g))
            goods.remove(g)
    picks.append((d, goods.pop()))
    return tuple(picks)


def _shared_bridge(u: Profile, a: Allocation, b: Allocation,
                   special: int, shared: int, x: int, y: int) -> list[Allocation]:
    """D={special,x}, i=shared,j=y to D={special,y},i=x,j=shared.

    Both singleton agents rank shared at least x,y. Never puts special and
    shared together in D, which is important when lifting a fixed prefix.
    """
    c = _swap(a, shared, y)
    if ef1(u, c):
        return [a, c, b]
    c = _swap(a, x, y)
    if ef1(u, c):
        return [a, c, b]
    c = _swap(a, special, y)
    e = _swap(c, shared, special)
    return [a, c, e, b]


def _without_singleton(u: Profile, wa: Witness, wb: Witness,
                       i: int, good: int) -> list[Allocation]:
    agents = [j for j in range(len(u)) if j != i]
    goods = [g for g in range(len(u[0])) if g != good]
    agent_index = {j: k for k, j in enumerate(agents)}
    good_index = {g: k for k, g in enumerate(goods)}
    restricted = tuple(tuple(u[j][g] for g in goods) for j in agents)

    def restrict(w):
        return tuple((agent_index[j], good_index[g]) for j, g in w if j != i)

    result = []
    for a in _connect(restricted, restrict(wa), restrict(wb)):
        lifted = [i] * len(u[0])
        for g, owner in zip(goods, a):
            lifted[g] = agents[owner]
        result.append(tuple(lifted))
    return result


def _join(left: list[Allocation], right: list[Allocation]) -> list[Allocation]:
    assert left[-1] == right[0]
    return left + right[1:]


def _d_first(u: Profile, wa: Witness, wb: Witness) -> list[Allocation]:
    """Connect one first-D-good class, allowing that good to move inside a path."""
    d, special = wa[0]
    i, h = wa[1]
    j, k = wb[1]
    if (i, h) == (j, k):
        return _without_singleton(u, wa, wb, i, h)
    if i == j:
        other = next(t for t in range(len(u)) if t not in (d, i))
        good = max((g for g in range(len(u[0])) if g != special), key=lambda g: u[other][g])
        middle = _finish(u, ((d, special), (other, good)), d)
        return _join(_d_first(u, wa, middle), _d_first(u, middle, wb))
    if h != k:
        ra = _finish(u, ((d, special), (i, h), (j, k)), d)
        rb = ((d, special), (j, k), (i, h)) + ra[3:]
        bridge = [allocation(ra, len(u[0]))]
    else:
        prefix = [(d, special), (i, h)]
        pool = set(range(len(u[0]))) - {special, h}
        common = []
        for t in range(len(u)):
            if t not in (d, i, j):
                good = max(sorted(pool), key=lambda g: u[t][g])
                common.append((t, good))
                pool.remove(good)
        y = max(sorted(pool), key=lambda g: u[j][g])
        x = max(sorted(pool), key=lambda g: u[i][g])
        ra = _finish(u, tuple(prefix + common + [(j, y)]), d)
        rb = _finish(u, tuple([(d, special), (j, h)] + common + [(i, x)]), d)
        a, b = allocation(ra, len(u[0])), allocation(rb, len(u[0]))
        bridge = [a, b] if x == y else _shared_bridge(u, a, b, special, h, x, y)
    return _join(_join(_d_first(u, wa, ra), bridge), _d_first(u, rb, wb))


def _connect(u: Profile, wa: Witness, wb: Witness) -> list[Allocation]:
    m, n = len(u[0]), len(u)
    a, b = allocation(wa, m), allocation(wb, m)
    if a == b:
        return [a]
    if n == 2:  # A state is specified by its singleton good; every two are adjacent.
        return [a, b]
    d = wa[-1][0]
    i, g = wa[0]
    j, h = wb[0]
    if (i, g) == (j, h):
        return _d_first(u, wa, wb) if i == d else _without_singleton(u, wa, wb, i, g)
    if i == j:
        other = next(t for t in range(n) if t != i)
        good = max(range(m), key=lambda g: u[other][g])
        middle = _finish(u, ((other, good),), d)
        return _join(_connect(u, wa, middle), _connect(u, middle, wb))
    if g != h:
        ra = _finish(u, ((i, g), (j, h)), d)
        rb = ((j, h), (i, g)) + ra[2:]
        bridge = [allocation(ra, m)]
    else:
        pool = set(range(m)) - {g}
        common = []
        for t in range(n):
            if t not in (d, i, j):
                good = max(sorted(pool), key=lambda g: u[t][g])
                common.append((t, good))
                pool.remove(good)
        if d in (i, j):
            single = j if i == d else i
            last = max(sorted(pool), key=lambda g: u[single][g])
            wd = _finish(u, tuple([(d, g)] + common + [(single, last)]), d)
            ws = _finish(u, tuple([(single, g)] + common), d)
            ra, rb = (wd, ws) if i == d else (ws, wd)
            bridge = [allocation(ra, m), allocation(rb, m)]
        else:
            special = max(sorted(pool), key=lambda g: u[d][g])
            common.append((d, special))
            pool.remove(special)
            y = max(sorted(pool), key=lambda g: u[j][g])
            x = max(sorted(pool), key=lambda g: u[i][g])
            ra = _finish(u, tuple([(i, g)] + common + [(j, y)]), d)
            rb = _finish(u, tuple([(j, g)] + common + [(i, x)]), d)
            left, right = allocation(ra, m), allocation(rb, m)
            bridge = [left, right] if x == y else _shared_bridge(u, left, right, special, g, x, y)
    return _join(_join(_connect(u, wa, ra), bridge), _connect(u, rb, wb))


def path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """EF1 exchange path between greedy endpoints with exactly one extra good."""
    _, d = one_extra_bundles(u, start)
    _, target_d = one_extra_bundles(u, target)
    if d != target_d:
        raise ValueError("endpoints need the same doubled recipient")
    wa, wb = greedy_witness(u, start), greedy_witness(u, target)
    if wa is None or wb is None:
        raise ValueError("both endpoints must be greedy one-extra-good outcomes")
    result = _connect(u, wa, wb)
    # Discard duplicate joins; validate the output with the general definitions.
    result = [a for index, a in enumerate(result) if index == 0 or a != result[index - 1]]
    assert result[0] == start and result[-1] == target
    assert all(ef1(u, a) for a in result)
    assert all(exchange(a, b) for a, b in zip(result, result[1:]))
    return result


def rejected_swaps(u: Profile, a: Allocation) -> dict[tuple[int, int], tuple[int, int]]:
    """Return a violated observer/owner EF1 inequality for each unfair exchange."""
    failures = {}
    n = len(u)
    for x, y in combinations(range(len(a)), 2):
        if a[x] == a[y]:
            continue
        b = list(a)
        b[x], b[y] = b[y], b[x]
        for i in range(n):
            own = sum(u[i][g] for g, owner in enumerate(b) if owner == i)
            for j in range(n):
                bundle = [u[i][g] for g, owner in enumerate(b) if owner == j]
                if own < sum(bundle) - max(bundle, default=0):
                    failures[x, y] = i, j
                    break
            if (x, y) in failures:
                break
    return failures


def main() -> None:
    u, initial, rotated = isolated_family(5)
    states = states_with_sizes((2, 1, 1, 1, 1))
    fair = tuple(a for a in states if ef1(u, a))
    groups = components(fair)
    greedy = tuple(a for a in fair if greedy_witness(u, a) is not None)
    assert ef1(u, initial) and ef1(u, rotated)
    assert not any(exchange(initial, a) for a in fair)
    assert len(rejected_swaps(u, initial)) == 14
    assert greedy_witness(u, initial) is None
    print("five agents, six goods: 360 fixed-size states")
    print(f"EF1 states: {len(fair)}; component sizes: {sorted(map(len, groups))}")
    print(f"greedy endpoints: {len(greedy)}; all in the same component: "
          f"{any(set(greedy) <= set(group) for group in groups)}")
    print("isolated state: 123400; all 14 possible exchanges violate EF1")
    print("second EF1 state: 412300; neither state is a greedy endpoint")
    routes = [path(u, a, b) for a, b in combinations(greedy, 2)]
    print(f"one-extra construction: {len(routes)} greedy endpoint pairs; "
          f"longest constructed path {max(len(route) - 1 for route in routes)} swaps")
    for n in (5, 6, 7, 10, 25):
        for strict in (False, True):
            profile, a, b = isolated_family(n, strict=strict)
            assert ef1(profile, a) and ef1(profile, b)
            assert len(rejected_swaps(profile, a)) == (n + 1) * n // 2 - 1
            assert greedy_witness(profile, a) is None
    print("family checks: n=5,6,7,10,25, both tied and strict utilities")
    print("Scope: one-extra theorem is a candidate; multiple full rounds remain open")


if __name__ == "__main__":
    main()
