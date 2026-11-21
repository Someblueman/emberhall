"""Safe-tail normalization and a two-exchange improvement outside that domain.

Pair anchors must have been picked greedily with the singleton good withheld.
The output need not admit another such anchor order. See RESERVED_SINGLETON.md.
"""

from __future__ import annotations

from itertools import permutations, product

from swaps import (Allocation, Profile, Witness, ef1, exchange, rounds_for,
                   validate_profile, validate_witness)


def validate_reserved(u: Profile, owners: Allocation, singleton: int,
                      anchors: tuple[tuple[int, int], ...]) -> None:
    """Validate the allocation and its supplied serial-anchor certificate."""
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (m != 2 * n - 1 or len(owners) != m
            or any(type(a) is not int or a not in range(n) for a in owners)
            or type(singleton) is not int or singleton not in range(n)):
        raise ValueError("need one singleton and all other agents of size two")
    if any(owners.count(a) != (1 if a == singleton else 2) for a in range(n)):
        raise ValueError("wrong labeled bundle sizes")
    doubles = set(range(n)) - {singleton}
    if len(anchors) != n - 1 or {a for a, _ in anchors} != doubles:
        raise ValueError("each double recipient needs one anchor pick")
    remaining = set(range(m)) - {owners.index(singleton)}
    for a, g in anchors:
        if type(g) is not int or g not in remaining or owners[g] != a:
            raise ValueError("anchor must be a distinct good held by its picker")
        if any(u[a][h] > u[a][g] for h in remaining):
            raise ValueError("anchor is not maximizing with singleton withheld")
        remaining.remove(g)
    if not ef1(u, owners):
        raise ValueError("initial allocation must be EF1")


def anchor_certificate(u: Profile, owners: Allocation, singleton: int):
    """Exhaustive diagnostic for small inputs; never used by the construction."""
    doubles = tuple(a for a in range(len(u)) if a != singleton)
    for order in permutations(doubles):
        for picks in product(*(tuple(g for g, a in enumerate(owners) if a == d)
                               for d in order)):
            certificate = tuple(zip(order, picks))
            try:
                validate_reserved(u, owners, singleton, certificate)
            except ValueError:
                continue
            return certificate
    return None


def improve(u: Profile, owners: Allocation, singleton: int,
            anchors: tuple[tuple[int, int], ...]) -> tuple[list[Allocation], str]:
    """Strictly improve the singleton in <=2 swaps, unless it has a favorite.

    Returns allocations and one of favorite, best-tail, blocking-anchor,
    or best-anchor. Only the input is certified as a reserved-anchor state.
    """
    validate_reserved(u, owners, singleton, anchors)
    z = owners.index(singleton)
    row = u[singleton]
    if row[z] == max(row):
        return [owners], "favorite"
    picked = dict(anchors)
    tails = tuple(g for g, a in enumerate(owners)
                  if a != singleton and g != picked[a])
    route = [owners]

    def swap(x: int, y: int) -> None:
        if x == y:
            return
        current = route[-1]
        changed = list(current)
        changed[x], changed[y] = changed[y], changed[x]
        target = tuple(changed)
        if not exchange(current, target) or not ef1(u, target):
            raise AssertionError("proved construction produced an invalid exchange")
        route.append(target)

    h = max(tails, key=lambda g: (row[g], -g))
    if row[h] <= row[z]:
        # Every tail is safe for the singleton. Give the owner of its global
        # favorite its own best tail before removing that owner's anchor.
        f = max(range(len(row)), key=lambda g: (row[g], -g))
        donor = owners[f]
        q = max(tails, key=lambda g: (u[donor][g], -g))
        old_tail = next(g for g in tails if owners[g] == donor)
        swap(q, old_tail)
        swap(z, f)
        branch = "best-anchor"
    else:
        # A high tail must be paired with an anchor no better than z to S.
        donor = next(a for a, g in reversed(anchors) if row[g] <= row[z])
        old_tail = next(g for g in tails if owners[g] == donor)
        swap(h, old_tail)
        prepared = route[-1]
        candidate = list(prepared)
        candidate[z], candidate[h] = candidate[h], candidate[z]
        if ef1(u, tuple(candidate)):
            swap(z, h)
            branch = "best-tail"
        else:
            # Only a later double can block the new pair {anchor_donor,z}.
            p = picked[donor]
            position = next(k for k, (a, _) in enumerate(anchors) if a == donor)
            blocker = next(a for a, _ in anchors[position + 1:]
                           if sum(u[a][g] for g, b in enumerate(prepared) if b == a)
                           < min(u[a][p], u[a][z]))
            swap(z, picked[blocker])
            branch = "blocking-anchor"
    if row[route[-1].index(singleton)] <= row[z] or len(route) > 3:
        raise AssertionError("singleton did not strictly improve within two exchanges")
    return route, branch


def normalize_safe(u: Profile, owners: Allocation, singleton: int,
                   anchors: tuple[tuple[int, int], ...]) -> tuple[list[Allocation], Witness]:
    """Normalize when the reserved singleton dominates all original tails.

    This weaker input contract extends the existing provisional-anchor method:
    the input need not itself have a complete greedy picking witness.
    """
    validate_reserved(u, owners, singleton, anchors)
    z = owners.index(singleton)
    original = dict(anchors)
    tails = tuple(g for g, a in enumerate(owners)
                  if a != singleton and g != original[a])
    if any(u[singleton][g] > u[singleton][z] for g in tails):
        raise ValueError("normalization requires the singleton to dominate all tails")
    route, _ = improve(u, owners, singleton, anchors)
    favorite = route[-1].index(singleton)
    picks = [(singleton, favorite)]

    def move(x: int, y: int) -> None:
        if x == y:
            return
        target = list(route[-1])
        target[x], target[y] = target[y], target[x]
        result = tuple(target)
        if not exchange(route[-1], result) or not ef1(u, result):
            raise AssertionError("normalization produced an invalid exchange")
        route.append(result)

    if favorite == z:
        picks.extend(anchors)
    else:
        donor = owners[favorite]
        q = next(g for g, a in enumerate(route[-1]) if a == donor and g != z)
        provisional = z
        for a, p in anchors:
            if a == donor:
                continue
            chosen = p
            if u[a][provisional] > u[a][p]:
                chosen = provisional
                move(p, provisional)
                provisional = p
            picks.append((a, chosen))
        chosen = max((provisional, q), key=lambda g: (u[donor][g], -g))
        picks.append((donor, chosen))

    fixed = dict(picks)
    remaining = set(range(len(owners))) - set(fixed.values())
    finals = []
    for a, _ in anchors:
        g = max(remaining, key=lambda h: (u[a][h], -h))
        old = next(h for h, b in enumerate(route[-1]) if b == a and h != fixed[a])
        move(old, g)
        finals.append((a, g))
        remaining.remove(g)
    witness = tuple(picks + finals)
    schedule = rounds_for(len(u), len(owners), tuple(a for a, _ in anchors))
    validate_witness(u, schedule, witness)
    return route, witness


LOSS_PROFILE = ((1, 0, 3, 4, 0, 0, 0), (2, 1, 0, 1, 4, 0, 2),
                (1, 4, 1, 1, 0, 4, 3), (2, 1, 2, 2, 3, 3, 4))
LOSS_START = (1, 0, 1, 0, 3, 2, 2)
LOSS_ANCHORS = ((0, 3), (1, 0), (2, 5))
LOSS_STRICT_PROFILE = ((11, 1, 31, 41, 2, 3, 4), (23, 11, 1, 12, 41, 2, 22),
                       (11, 41, 12, 13, 1, 42, 31), (21, 11, 22, 23, 31, 30, 41))

# No full pair-only connectivity lemma can replace the lost invariant.
PAIR_PROFILE = ((1, 2, 0, 0, 3, 6), (6, 3, 2, 1, 0, 0),
                (0, 0, 3, 6, 1, 2))
PAIR_ISOLATED = (0, 0, 1, 1, 2, 2)


def pair_obstruction(n: int, strict: bool = False) -> tuple[Profile, Allocation]:
    """An isolated all-size-two EF1 state for every n>=3."""
    if type(n) is not int or n < 3:
        raise ValueError("the obstruction needs at least three agents")
    m = 2 * n
    rows = [list(row) + [0] * (m - 6) for row in PAIR_PROFILE]
    for a in range(3, n):
        row = [3] * 6 + [0] * (m - 6)
        row[2 * a], row[2 * a + 1] = 1, 2
        rows.append(row)
    if strict:
        # Uniform positive slack preserves initial equality and strict failures.
        rows = [[10 * m * v + m + g + 1 for g, v in enumerate(row)] for row in rows]
    return tuple(map(tuple, rows)), tuple(g // 2 for g in range(m))


def main() -> None:
    safe, witness = normalize_safe(((2, 3, 1), (3, 2, 1)), (0, 1, 1), 0, ((1, 1),))
    print("Safe-tail normalization: " + " -> ".join("".join(map(str, a)) for a in safe))
    print("Greedy witness:", witness)
    route, branch = improve(LOSS_PROFILE, LOSS_START, 3, LOSS_ANCHORS)
    print("Reserved singleton: a local improvement, not a normalization")
    print(f"branch: {branch}; exchanges: {len(route) - 1}")
    for a in route:
        print("".join(map(str, a)))
    print("singleton value: 3 -> 4")
    print("new serial-anchor certificate:", anchor_certificate(LOSS_PROFILE, route[-1], 3))
    failures = 0
    for x in range(6):
        for y in range(x):
            if PAIR_ISOLATED[x] != PAIR_ISOLATED[y]:
                a = list(PAIR_ISOLATED)
                a[x], a[y] = a[y], a[x]
                if ef1(PAIR_PROFILE, tuple(a)):
                    raise AssertionError("claimed pair-only isolation is false")
                failures += 1
    print(f"Three pairs: isolated EF1 state; all {failures} exchanges rejected")
    print("Open: attach every reserved-anchor state to a greedy endpoint")


if __name__ == "__main__":
    main()
