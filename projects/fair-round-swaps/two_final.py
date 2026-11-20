"""A conditional four-agent bridge, not a general connectivity theorem."""

from __future__ import annotations

from itertools import combinations

from swaps import (Allocation, Profile, allocation, components, ef1, exchange,
                   picking_outcomes, rounds_for, states_with_sizes, validate_profile,
                   validate_witness)

# Agents: D=0,E=1,i=2,j=3. Goods: g=0,k=1,l=2,x=3,y=4,z=5.
LEFT = ((2, 0), (0, 1), (1, 2), (3, 4), (0, 3), (1, 5))
RIGHT = ((3, 0), (0, 1), (1, 2), (2, 3), (0, 4), (1, 5))
EXAMPLE: Profile = (
    (0, 10, 9, 8, 7, 6),
    (20, 20, 10, 8, 7, 6),
    (100, 30, 20, 60, 0, 40),
    (100, 20, 30, 0, 60, 40),
)


def swap(a: Allocation, x: int, y: int) -> Allocation:
    b = list(a)
    b[x], b[y] = b[y], b[x]
    return tuple(b)


def bridge(u: Profile) -> list[Allocation]:
    """Return the four-exchange path when the common final good is safe enough.

    The precise inequalities, including endpoint greediness, are in TWO_FINAL.md.
    A refusal says nothing about existence of another path.
    """
    validate_profile(u)
    if len(u) != 4 or len(u[0]) != 6:
        raise ValueError("need four agents and six goods")
    rounds = rounds_for(4, 6, (0, 1))
    validate_witness(u, rounds, LEFT)
    validate_witness(u, rounds, RIGHT)
    if any(u[i][5] < min(u[i][1], u[i][3]) or
           u[i][5] < min(u[i][2], u[i][4]) for i in (2, 3)):
        raise ValueError("common final good does not satisfy the bridge guard")
    a = allocation(LEFT, 6)
    route = [a]
    for x, y in ((5, 4), (0, 5), (3, 5), (5, 4)):
        route.append(swap(route[-1], x, y))
    assert route[-1] == allocation(RIGHT, 6)
    assert all(ef1(u, state) for state in route)
    assert all(exchange(a, b) for a, b in zip(route, route[1:]))
    return route


def core_path(u: Profile, start: Allocation, target: Allocation) -> list[Allocation]:
    """Connect fair states fixing safe singleton goods, in at most two swaps."""
    validate_profile(u)
    if len(u) != 4 or len(u[0]) != 6 or any(len(a) != 6 for a in (start, target)):
        raise ValueError("need four agents and six goods")
    if any(sorted(a.count(i) for i in range(4)) != [1, 1, 2, 2] for a in (start, target)):
        raise ValueError("need two double bundles and two singletons")
    if any(start.count(i) != target.count(i) for i in range(4)):
        raise ValueError("different size vectors")
    singles = [i for i in range(4) if start.count(i) == 1]
    doubles = [i for i in range(4) if start.count(i) == 2]
    for i in singles:
        good = start.index(i)
        if target[good] != i or sum(v > u[i][good] for v in u[i]) > 1:
            raise ValueError("each fixed singleton must hold a top-two good")
    if not ef1(u, start) or not ef1(u, target):
        raise ValueError("endpoints must be EF1")
    if start == target:
        return [start]
    if exchange(start, target):
        return [start, target]
    goods = [g for g, owner in enumerate(start) if owner in doubles]
    for pair in combinations(goods, 2):
        middle = list(start)
        for g in goods:
            middle[g] = doubles[0] if g in pair else doubles[1]
        middle = tuple(middle)
        if ef1(u, middle) and exchange(start, middle) and exchange(middle, target):
            return [start, middle, target]
    raise AssertionError("at most two of the four common neighbors can be unfair")


def main() -> None:
    route = bridge(EXAMPLE)
    print("four agents, six goods: two final recipients")
    for index, state in enumerate(route):
        print(f"{index}: {''.join(map(str, state))}")
    print("Verified: four exchanges, greedy endpoints, every state EF1")
    wrong = swap(route[0], 1, 4)
    assert not ef1(EXAMPLE, wrong)
    print("Frozen-fourth-agent attempt: agent 3 gets 20 but envies agent 1 after deletion (30)")
    all_states = states_with_sizes((2, 2, 1, 1))
    fair = tuple(a for a in all_states if ef1(EXAMPLE, a))
    groups = components(fair)
    greedy = picking_outcomes(EXAMPLE, rounds_for(4, 6, (0, 1)))
    print(f"Example census only: {len(all_states)} states, {len(fair)} EF1, "
          f"component sizes {sorted(map(len, groups))}, {len(greedy)} greedy endpoints")
    print("Scope: sufficient guard only; failed guard does not refute connectivity")


if __name__ == "__main__":
    main()
