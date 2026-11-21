"""Serial-anchor shared-favorite crossings, not paths to specified endpoints.

See COMMON_CROSSING.md for the real-utility proof and attachment boundary.
The executable uses only exact integers and fractions.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json

from swaps import Allocation, Profile, Witness, ef1, exchange, validate_profile


@dataclass(frozen=True)
class Crossing:
    pivot: int
    anchors: Witness
    tails: Witness
    sides: tuple[Allocation, Allocation]


# A direct attempt to improve the pivot-holder by exchanging goods 1 and 6
# makes agent 2 unfair. A different two-exchange route below reaches greediness.
DIRECT_FAILURE: Profile = (
    (0, 0, 0, 3, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 3),
    (0, 3, 0, 3, 2, 0, 1, 0),
    (5, 2, 0, 0, 0, 3, 2, 0),
    (5, 2, 0, 0, 3, 0, 4, 0),
)
REPAIRED_ATTACHMENT: tuple[Allocation, ...] = (
    (3, 4, 2, 0, 2, 1, 0, 1),
    (3, 2, 2, 0, 4, 1, 0, 1),
    (3, 0, 2, 2, 4, 1, 0, 1),
)
REPAIRED_WITNESS: Witness = (
    (3, 0), (2, 3), (1, 7), (0, 6), (4, 4), (1, 5), (0, 1), (2, 2),
)


def _match(u: Profile, carriers: tuple[int, int], pivot: int,
           anchors: Witness, tails: tuple[int, ...]) -> Witness:
    """Augmenting paths; Hall's condition follows from the two upper sets."""
    matched: dict[int, int] = {}  # tail good -> anchor position

    def augment(index: int, seen: set[int]) -> bool:
        anchor = anchors[index][1]
        for tail in tails:
            if tail in seen or any(u[i][anchor] > u[i][pivot]
                                   and u[i][tail] > u[i][pivot] for i in carriers):
                continue
            seen.add(tail)
            if tail not in matched or augment(matched[tail], seen):
                matched[tail] = index
                return True
        return False

    for index in range(len(anchors)):
        if not augment(index, set()):
            raise AssertionError("the proved Hall condition failed")
    by_anchor = {index: tail for tail, index in matched.items()}
    return tuple((agent, by_anchor[index]) for index, (agent, _) in enumerate(anchors))


def common_crossing(u: Profile, shared: int, carriers: tuple[int, int],
                    order: tuple[int, ...] | None = None) -> Crossing:
    """Construct two fair allocations joined by the shared/pivot exchange.

    Each non-carrier receives a pair. The returned anchors form an actual
    serial greedy selection with shared and pivot withheld. Tail matching
    need not be greedy. Arbitrary carrier labels and double orders are allowed.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (n < 3 or m != 2*n-2 or len(carriers) != 2
            or any(type(i) is not int or i not in range(n) for i in carriers)
            or carriers[0] == carriers[1]
            or type(shared) is not int or shared not in range(m)):
        raise ValueError("need r pairs, two distinct singleton carriers, and 2r+2 goods")
    if any(u[i][shared] != max(u[i]) for i in carriers):
        raise ValueError("shared good must maximize both carriers' utilities")
    doubles = tuple(i for i in range(n) if i not in carriers)
    order = doubles if order is None else tuple(order)
    if (len(order) != len(doubles) or any(type(i) is not int for i in order)
            or set(order) != set(doubles)):
        raise ValueError("order must contain every double recipient exactly once")
    r = len(doubles)
    goods = tuple(g for g in range(m) if g != shared)
    top = [set(sorted(goods, key=lambda g: (-u[i][g], g))[:r+1]) for i in carriers]
    pivot = min(top[0] & top[1])
    while True:
        better = [g for g in goods if all(u[i][g] > u[i][pivot] for i in carriers)]
        if not better:
            break
        pivot = better[0]
    pool = set(goods) - {pivot}
    anchors = []
    for agent in order:
        good = max(sorted(pool), key=lambda g: u[agent][g])
        anchors.append((agent, good))
        pool.remove(good)
    anchors = tuple(anchors)
    tails = _match(u, carriers, pivot, anchors, tuple(sorted(pool)))
    state = [-1]*m
    for agent, good in anchors + tails:
        state[good] = agent
    state[shared], state[pivot] = carriers
    left = tuple(state)
    state[shared], state[pivot] = reversed(carriers)
    right = tuple(state)
    if not ef1(u, left) or not ef1(u, right) or not exchange(left, right):
        raise AssertionError("constructed crossing is not fair")
    return Crossing(pivot, anchors, tails, (left, right))


def attachment_boundary(r: int) -> tuple[Profile, int, tuple[int, int]]:
    """Opposite carrier rankings defeat a common safe-tail anchor certificate.

    All doubles strictly rank the first r residual goods above the rest.
    The unique feasible crossing pivot is the middle residual good. Hence
    every serial anchor order leaves all the last r goods as tails, and the
    second carrier ranks every tail strictly above the pivot.
    """
    if type(r) is not int or r < 1:
        raise ValueError("need a positive number of pairs")
    m = 2*r+2
    descending = (0,) + tuple(range(2*r+1, 0, -1))
    first = (m,) + descending[1:]
    second = (m,) + tuple(range(1, m))
    return (descending,)*r + (first, second), 0, (r, r+1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=3)
    args = parser.parse_args()
    u, shared, carriers = attachment_boundary(args.pairs)
    crossing = common_crossing(u, shared, carriers)
    print(json.dumps({"pairs": args.pairs, "pivot": crossing.pivot,
                      "anchors": crossing.anchors, "tails": crossing.tails,
                      "path": crossing.sides,
                      "pivot_dominates_all_tails": [
                          all(u[i][crossing.pivot] >= u[i][g] for _, g in crossing.tails)
                          for i in carriers],
                      "scope": "one fair crossing; attachment to specified endpoints unproved"}, indent=2))


if __name__ == "__main__":
    main()
