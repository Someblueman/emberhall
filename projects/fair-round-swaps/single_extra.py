"""Exact one-extra-good boundary; see SINGLE_EXTRA.md for proof and limits."""

from __future__ import annotations

from itertools import combinations

from swaps import (Allocation, Profile, Witness, components, ef1, exchange,
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
    for n in (5, 6, 7, 10, 25):
        for strict in (False, True):
            profile, a, b = isolated_family(n, strict=strict)
            assert ef1(profile, a) and ef1(profile, b)
            assert len(rejected_swaps(profile, a)) == (n + 1) * n // 2 - 1
            assert greedy_witness(profile, a) is None
    print("family checks: n=5,6,7,10,25, both tied and strict utilities")
    print("Scope: defeats all-EF1 connectivity; greedy-endpoint question remains open")


if __name__ == "__main__":
    main()
