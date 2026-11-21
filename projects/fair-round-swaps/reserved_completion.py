"""Normalize reserved anchors using a terminal anchor or a safe favorite tail.

The singleton need not dominate the original tails. See RESERVED_COMPLETION.md.
Only exact nonnegative rational inputs are accepted by the executable.
"""

from __future__ import annotations

from reserved_singleton import (LOSS_ANCHORS, LOSS_START, LOSS_STRICT_PROFILE,
                                normalize_safe, validate_reserved)
from swaps import (Allocation, Profile, Witness, ef1, exchange, rounds_for,
                   validate_profile, validate_witness)


def acquire_best_tail(u: Profile, owners: Allocation, singleton: int,
                      anchors: tuple[tuple[int, int], ...]
                      ) -> tuple[list[Allocation], tuple[int, ...]]:
    """Acquire a better maximal original tail in <=r+1 fair exchanges.

    No extra terminal guard is needed. The returned agents form an increasing
    subsequence of the original anchor order. Singleton utility stays above
    its initial level, but can decrease between intermediate steps.
    If every original tail is already below the singleton, return unchanged.
    """
    validate_reserved(u, owners, singleton, anchors)
    original = dict(anchors)
    z = owners.index(singleton)
    tails = tuple(g for g, a in enumerate(owners)
                  if a != singleton and g != original[a])
    h = max(tails, key=lambda g: (u[singleton][g], -g))
    if u[singleton][h] <= u[singleton][z]:
        return [owners], ()
    frontier = max(k for k, (_, p) in enumerate(anchors)
                   if u[singleton][p] <= u[singleton][z])
    pivot, q = anchors[frontier]
    route, chain = [owners], []

    def move(x: int, y: int) -> None:
        if x == y:
            return
        target = list(route[-1])
        target[x], target[y] = target[y], target[x]
        target = tuple(target)
        if not exchange(route[-1], target) or not ef1(u, target):
            raise AssertionError("best-tail chain produced an unfair exchange")
        route.append(target)

    move(h, next(t for t in tails if owners[t] == pivot))
    current = z
    while True:
        candidate = list(route[-1])
        candidate[current], candidate[h] = candidate[h], candidate[current]
        if ef1(u, tuple(candidate)):
            move(current, h)
            break
        # A blocker must be a later, as-yet unchanged original double.
        frontier = next(k for k in range(frontier + 1, len(anchors))
                        if sum(u[anchors[k][0]][g] for g, a in enumerate(route[-1])
                               if a == anchors[k][0])
                        < min(u[anchors[k][0]][q], u[anchors[k][0]][current]))
        a, p = anchors[frontier]
        move(current, p)
        chain.append(a)
        current = p
    if len(route) - 1 > len(anchors) + 1:
        raise AssertionError("best-tail exchange bound exceeded")
    return route, tuple(chain)


def terminal_buffer(u: Profile, owners: Allocation, singleton: int,
                    anchors: tuple[tuple[int, int], ...]
                    ) -> tuple[int, int, int, str] | None:
    """Return (pivot, retained good, singleton destination, branch), or None.

    This diagnoses the two terminal guards; the older safe-tail guard is
    handled separately by normalize_guarded.
    """
    validate_reserved(u, owners, singleton, anchors)
    z = owners.index(singleton)
    original = dict(anchors)
    tails = tuple(g for g, a in enumerate(owners)
                  if a != singleton and g != original[a])
    h = max(tails, key=lambda g: (u[singleton][g], -g))
    for pivot, f in reversed(anchors):
        if any(u[a][p] < u[a][f] for a, p in anchors if a != pivot):
            continue
        if u[singleton][f] <= u[singleton][z]:
            return pivot, f, h, "anchor"
        if u[singleton][f] >= u[singleton][h]:
            best = max(u[pivot][t] for t in tails)
            safe = [t for t in tails if u[pivot][t] == best
                    and u[singleton][t] <= u[singleton][z]]
            if safe:
                return pivot, min(safe), f, "tail"
    return None


def normalize_guarded(u: Profile, owners: Allocation, singleton: int,
                      anchors: tuple[tuple[int, int], ...]
                      ) -> tuple[list[Allocation], Witness]:
    """Give a greedy endpoint in <=2r+1 exchanges under any of three guards.

    The supplied certificate may put the eligible pivot anywhere: its anchor
    can commute past every later original anchor. Safe original tails use
    Rook's earlier construction. All owner labels are preserved and the
    singleton's utility never decreases along the path.
    """
    validate_reserved(u, owners, singleton, anchors)
    original = dict(anchors)
    z = owners.index(singleton)
    tails = tuple(g for g, a in enumerate(owners)
                  if a != singleton and g != original[a])
    h = max(tails, key=lambda g: (u[singleton][g], -g))
    if u[singleton][h] <= u[singleton][z]:
        return normalize_safe(u, owners, singleton, anchors)
    plan = terminal_buffer(u, owners, singleton, anchors)
    if plan is None:
        raise ValueError("neither safe tails nor a terminal buffer is available")
    pivot, q, h, branch = plan

    route = [owners]

    def move(x: int, y: int) -> None:
        if x == y:
            return
        target = list(route[-1])
        target[x], target[y] = target[y], target[x]
        target = tuple(target)
        if not exchange(route[-1], target) or not ef1(u, target):
            raise AssertionError("terminal-pivot proof produced an unfair exchange")
        route.append(target)

    pivot_tail = next(g for g in tails if owners[g] == pivot)
    if branch == "anchor":
        # Both the old holder of h and the pivot have low singleton anchors.
        move(h, pivot_tail)
    else:
        # Both exchanged tails are low for the singleton.
        move(q, pivot_tail)
    move(z, h)

    # All other anchors dominate q. The pivot keeps q while its second slot
    # passes the one extra good through the serial greedy choices.
    provisional = z
    picks = []
    for a, p in anchors:
        if a == pivot:
            continue
        chosen = p
        if u[a][provisional] > u[a][p]:
            chosen = provisional
            move(p, provisional)
            provisional = p
        picks.append((a, chosen))
    # The singleton takes its greedy turn before the pivot. Every original
    # tail and q is below h for it; only the provisional good can be better.
    if u[singleton][provisional] > u[singleton][h]:
        move(h, provisional)
        picks.append((singleton, provisional))
        provisional = h
    else:
        picks.append((singleton, h))
    chosen = max((q, provisional), key=lambda g: (u[pivot][g], -g))
    picks.append((pivot, chosen))

    fixed = dict(picks)
    remaining = set(range(len(owners))) - set(fixed.values())
    finals = []
    for a, _ in anchors:
        g = max(remaining, key=lambda t: (u[a][t], -t))
        old = next(t for t, b in enumerate(route[-1]) if b == a and t != fixed[a])
        move(old, g)
        finals.append((a, g))
        remaining.remove(g)
    witness = tuple(picks + finals)
    validate_witness(u, rounds_for(len(u), len(owners), tuple(original)), witness)
    if len(route) - 1 > 2 * len(anchors) + 1:
        raise AssertionError("terminal-pivot exchange bound exceeded")
    return route, witness


def normalize_with_favorite(u: Profile, owners: Allocation, fixed: int, singleton: int,
                            anchors: tuple[tuple[int, int], ...]
                            ) -> tuple[list[Allocation], Witness]:
    """The same attachment with another singleton holding a global favorite.

    The favorite good and its owner never move. The other singleton need not
    share that favorite. No double row is required to be automatically fair.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (n < 3 or m != 2 * n - 2 or len(owners) != m
            or any(type(a) is not int or a not in range(n) for a in owners)
            or type(fixed) is not int or type(singleton) is not int
            or fixed not in range(n) or singleton not in range(n) or fixed == singleton
            or owners.count(fixed) != 1):
        raise ValueError("need two distinct singleton recipients and double recipients")
    favorite = owners.index(fixed)
    if u[fixed][favorite] != max(u[fixed]):
        raise ValueError("fixed singleton must own a global favorite")
    agents = tuple(a for a in range(n) if a != fixed)
    goods = tuple(g for g in range(m) if g != favorite)
    agent_index = {a: i for i, a in enumerate(agents)}
    good_index = {g: i for i, g in enumerate(goods)}
    if any(a not in agent_index or g not in good_index for a, g in anchors):
        raise ValueError("anchors must exclude the fixed singleton and its good")
    reduced_u = tuple(tuple(u[a][g] for g in goods) for a in agents)
    reduced_a = tuple(agent_index[owners[g]] for g in goods)
    reduced_anchors = tuple((agent_index[a], good_index[g]) for a, g in anchors)
    path, witness = normalize_guarded(reduced_u, reduced_a, agent_index[singleton], reduced_anchors)
    route = []
    for state in path:
        lifted = list(owners)
        for g, a in zip(goods, state):
            lifted[g] = agents[a]
        result = tuple(lifted)
        if not ef1(u, result):
            raise AssertionError("favorite lifting produced an unfair allocation")
        route.append(result)
    full_witness = ((fixed, favorite),) + tuple((agents[a], goods[g]) for a, g in witness)
    validate_witness(u, rounds_for(n, m, tuple(a for a, _ in anchors)), full_witness)
    return route, full_witness


def main() -> None:
    route, witness = normalize_guarded(LOSS_STRICT_PROFILE, LOSS_START, 3, LOSS_ANCHORS)
    print("Terminal-anchor normalization, including an unsafe original tail")
    print(" -> ".join("".join(map(str, a)) for a in route))
    print("Singleton values:", [LOSS_STRICT_PROFILE[3][a.index(3)] for a in route])
    print("Greedy witness:", witness)
    print(f"Verified {len(route) - 1} EF1 exchanges; bound {2 * len(LOSS_ANCHORS) + 1}")


if __name__ == "__main__":
    main()
