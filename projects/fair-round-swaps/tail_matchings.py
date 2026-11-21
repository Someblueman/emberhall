"""Connect all legal tail matchings, fixing anchors and both singleton goods.

The two upper sets may overlap. See TAIL_MATCHINGS.md for the constructive
proof and its distinction from reaching a greedy endpoint.
"""

from __future__ import annotations

import json

from common_crossing import Crossing, common_crossing
from swaps import Allocation, Profile, Witness, ef1, validate_profile


def reconfigure(anchor_masks: tuple[int, ...], tail_masks: dict[int, int],
                start: tuple[int, ...], target: tuple[int, ...]
                ) -> list[tuple[int, ...]]:
    """Connect two bijections avoiding intersecting two-bit upper-set masks.

    Entry k is the tail label assigned to anchor k. Mask bits indicate a
    good strictly above the pivot for either carrier; a pair is legal iff
    the bitwise intersection of its masks is zero. The number of swaps is
    the unconstrained minimum: r minus the relative permutation's cycles.
    """
    r = len(anchor_masks)
    if (not r or len(start) != r or len(target) != r
            or any(type(m) is not int or m not in range(4) for m in anchor_masks)
            or any(type(g) is not int for g in start + target)
            or len(set(start)) != r or set(start) != set(target)
            or set(tail_masks) != set(start)
            or any(type(m) is not int or m not in range(4) for m in tail_masks.values())):
        raise ValueError("need two bijections of the same tails with two-bit masks")
    if any(anchor_masks[k] & tail_masks[g] for matching in (start, target)
           for k, g in enumerate(matching)):
        raise ValueError("both endpoint matchings must be legal")
    current = list(start)
    owner = {g: k for k, g in enumerate(current)}
    route = [tuple(current)]
    fixed = set()

    def swap(a: int, b: int) -> None:
        current[a], current[b] = current[b], current[a]
        owner[current[a]], owner[current[b]] = a, b
        route.append(tuple(current))

    # Both-high anchors need neutral tails, then first-only, second-only,
    # and finally neutral anchors. Each prefix remains fixed thereafter.
    priority = {3: 0, 1: 1, 2: 2, 0: 3}
    for a in sorted(range(r), key=lambda k: (priority[anchor_masks[k]], k)):
        if current[a] != target[a]:
            c = owner[target[a]]
            if not anchor_masks[c] & tail_masks[current[a]]:
                swap(a, c)
            else:
                # The sole blocked case: a is first-only, c second-only,
                # current[a] second-only, target[a] neutral. Capacity forces
                # an unfixed first-only/neutral anchor holding a first-only
                # or neutral tail. Restrict to a's target-permutation cycle:
                # its own capacity argument suffices, and each swap then
                # splits a cycle, attaining the unconstrained minimum.
                cycle = {a}
                k = owner[target[a]]
                while k != a:
                    cycle.add(k)
                    k = owner[target[k]]
                d = next((k for k in sorted(cycle) if k not in fixed
                          and anchor_masks[k] in (0, 1)
                          and tail_masks[current[k]] in (0, 1)), None)
                if (anchor_masks[a] != 1 or anchor_masks[c] != 2
                        or tail_masks[current[a]] != 2 or tail_masks[target[a]] != 0
                        or d is None):
                    raise AssertionError("the matching capacity argument failed")
                swap(c, d)
                swap(a, d)
        fixed.add(a)
    if tuple(current) != target or len(route)-1 > r-1:
        raise AssertionError("the matching path violated its endpoint or length bound")
    return route


def _sides(shared: int, carriers: tuple[int, int], pivot: int, anchors: Witness,
           tails: Witness, m: int) -> tuple[Allocation, Allocation]:
    state = [-1]*m
    for i, g in anchors + tails:
        state[g] = i
    state[shared], state[pivot] = carriers
    left = tuple(state)
    state[shared], state[pivot] = reversed(carriers)
    return left, tuple(state)


def crossing_paths(u: Profile, shared: int, carriers: tuple[int, int],
                   start: Crossing, target_tails: Witness
                   ) -> tuple[list[Allocation], list[Allocation]]:
    """Return synchronized EF1 paths on both sides of a fixed crossing.

    Anchors must dominate every tail for their owners. Serial greediness is
    sufficient but not required. Both singleton goods and all anchors stay
    fixed. The final assignments need only pass the same EF1 upper-set tests.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (n < 3 or m != 2*n-2 or type(shared) is not int or shared not in range(m)
            or len(carriers) != 2 or len(set(carriers)) != 2
            or any(type(i) is not int or i not in range(n) for i in carriers)
            or type(start.pivot) is not int or start.pivot not in range(m)
            or shared == start.pivot
            or any(u[i][shared] != max(u[i]) for i in carriers)):
        raise ValueError("need two singleton carriers sharing a favorite, with r pairs")
    doubles = set(range(n)) - set(carriers)
    for picks in (start.anchors, start.tails, target_tails):
        if (len(picks) != n-2 or {i for i, _ in picks} != doubles
                or any(type(i) is not int or type(g) is not int or g not in range(m)
                       for i, g in picks)):
            raise ValueError("each assignment must give every double recipient one good")
    anchor_goods = {g for _, g in start.anchors}
    tail_goods = set(range(m)) - {shared, start.pivot} - anchor_goods
    if (len(anchor_goods) != n-2 or len(tail_goods) != n-2
            or {g for _, g in start.tails} != tail_goods
            or {g for _, g in target_tails} != tail_goods
            or any(u[i][a] < u[i][g] for i, a in start.anchors for g in tail_goods)):
        raise ValueError("need distinct anchors dominating every disjoint tail")
    if start.sides != _sides(shared, carriers, start.pivot, start.anchors, start.tails, m):
        raise ValueError("crossing sides do not match their anchors and tails")
    mask = lambda g: sum(1 << bit for bit, i in enumerate(carriers)
                         if u[i][g] > u[i][start.pivot])
    agents = tuple(i for i, _ in start.anchors)
    initial, goal = dict(start.tails), dict(target_tails)
    matchings = reconfigure(tuple(mask(a) for _, a in start.anchors),
                            {g: mask(g) for g in tail_goods},
                            tuple(initial[i] for i in agents), tuple(goal[i] for i in agents))
    left, right = [], []
    for matching in matchings:
        tails = tuple(zip(agents, matching))
        a, b = _sides(shared, carriers, start.pivot, start.anchors, tails, m)
        if not ef1(u, a) or not ef1(u, b):
            raise AssertionError("a legal tail matching lost EF1")
        left.append(a)
        right.append(b)
    return left, right


def example() -> tuple[Profile, Crossing, Witness]:
    """A three-cycle for which the direct target swap is forbidden."""
    u: Profile = (
        (0, 0, 10, 0, 0, 0, 0, 0),
        (0, 0, 0, 10, 0, 0, 0, 0),
        (0, 0, 0, 0, 10, 0, 0, 0),
        (3, 1, 2, 0, 0, 2, 0, 0),
        (3, 1, 0, 2, 0, 0, 2, 0),
    )
    return u, common_crossing(u, 0, (3, 4)), ((0, 7), (1, 5), (2, 6))


def three_observer_boundary() -> tuple[Profile, Allocation, Allocation]:
    """Three fixed singleton observers can disconnect the tail-only slice.

    The three pairs retain anchors 0,1,2. Observer k forbids matching
    anchor k to tail k+3. Only the two derangements remain fair, and no
    transposition joins them. This is not a full EF1 graph disconnection.
    """
    rows = []
    for k in range(3):
        row = [0]*9
        row[k] = 3
        rows.append(tuple(row))
    for k in range(3):
        row = [0]*9
        row[k] = row[k+3] = 2
        row[k+6] = 1
        rows.append(tuple(row))
    return tuple(rows), (0, 1, 2, 2, 0, 1, 3, 4, 5), (0, 1, 2, 1, 2, 0, 3, 4, 5)


def main() -> None:
    u, start, target = example()
    left, right = crossing_paths(u, 0, (3, 4), start, target)
    print(json.dumps({"exchanges_on_each_side": len(left)-1,
                      "fixed_anchors": start.anchors, "left_path": left,
                      "right_path": right,
                      "scope": "fixed-anchor matchings, not arbitrary endpoint connectivity"}, indent=2))


if __name__ == "__main__":
    main()
