"""Greedy Pareto improvements can require a sharp temporary utility loss.

The endpoints are connected by an explicit EF1 path. This is an obstruction
only to paths preserving every recipient's initial utility, not to connectivity.
Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
import heapq
from itertools import combinations
import json

from swaps import (Allocation, Profile, allocation, ef1, exchange, rounds_for,
                   states_with_sizes, validate_profile, validate_witness)


def family(doubles: int = 4, scale: int = 100) -> tuple[Profile, Allocation]:
    """Positive strict examples, with two exceptional and r-2 automatic doubles."""
    if type(doubles) is not int or doubles < 2:
        raise ValueError("need at least two double recipients")
    m = 2 * doubles + 2
    if type(scale) is not int or scale <= m:
        raise ValueError("scale must be an integer larger than the good count")
    offsets = list(range(1, m + 1))
    offsets[3], offsets[4] = offsets[4], offsets[3]
    rows = [tuple(scale * v + t for v, t in zip(base + [0] * (m - 6), offsets))
            for base in ([0, 0, 3, 2, 2, 0], [0, 0, 5, 2, 2, 0])]
    for a in range(2, doubles):
        anchor, tail = 2 * a + 2, 2 * a + 3
        row = [0] * m
        row[anchor], row[tail], row[5] = 2 * m, 2 * m - 1, 2 * m - 2
        for rank, g in enumerate((g for g in range(m) if g not in (anchor, tail, 5)), 1):
            row[g] = m + rank
        rows.append(tuple(row))
    rows.extend([tuple(scale * v + g + 1 for g, v in
                       enumerate([30, 20] + [0] * (m - 2))) for _ in range(2)])
    start = (doubles, doubles + 1, 0, 1, 1, 0)
    start += tuple(a for a in range(2, doubles) for _ in range(2))
    return tuple(rows), start


def swap(state: Allocation, x: int, y: int) -> Allocation:
    changed = list(state)
    changed[x], changed[y] = changed[y], changed[x]
    return tuple(changed)


def path(start: Allocation) -> list[Allocation]:
    """A two-swap optimum for r=2; a four-swap optimum using one buffer otherwise."""
    moves = ((2, 3), (4, 5)) if len(start) == 6 else (
        (5, len(start) - 1), (2, 3), (4, len(start) - 1), (5, len(start) - 1))
    result = [start]
    for x, y in moves:
        result.append(swap(result[-1], x, y))
    return result


def witnesses(doubles: int):
    """Two complete greedy witnesses, including all automatically fair recipients."""
    anchors = tuple((a, 2 * a + 2) for a in range(2, doubles))
    tails = tuple((a, 2 * a + 3) for a in range(2, doubles))
    source = ((0, 2), (doubles, 0), (doubles + 1, 1), (1, 3))
    target = ((1, 2), (doubles, 0), (doubles + 1, 1), (0, 3))
    return (source + anchors + ((1, 4),) + tails + ((0, 5),),
            target + anchors + ((0, 4),) + tails + ((1, 5),))


def totals(u: Profile, state: Allocation) -> tuple:
    return tuple(sum(row[g] for g, owner in enumerate(state) if owner == a)
                 for a, row in enumerate(u))


def deficit(initial: tuple, current: tuple):
    return max((0,) + tuple(a - b for a, b in zip(initial, current)))


def proportional_deficit(initial: tuple, current: tuple):
    return max(Fraction(max(0, a - b), a) for a, b in zip(initial, current))


def barrier_certificate(u: Profile, start: Allocation) -> dict:
    """Numeric bounds for the first change of a nucleus owner (goods 0..4).

    Only low goods 5,...,m-1 may move before that first change. Thus A's other
    good is low, both of B's original goods are fixed, and both carriers are
    fixed. The bounds include unfair states and changes of good zero's owner.
    """
    validate_profile(u)
    r, m = len(u) - 2, len(u[0])
    if (r < 2 or m != 2 * r + 2 or len(start) != m
            or start[:6] != (r, r + 1, 0, 1, 1, 0)
            or sorted(start[6:]) != [a for a in range(2, r) for _ in range(2)]):
        raise ValueError("need the stated nucleus and buffer allocation")
    original = totals(u, start)
    low_a, low_b = max(u[0][5:]), max(u[1][5:])
    bounds = {
        "A_receives_one_of_Bs_goods": original[0] - max(u[0][3:5]) - low_a,
        "B_receives_a_low_good": original[1] - max(u[1][3:5]) - low_b,
        "A_receives_a_low_good": original[0] - 2 * low_a,
        "I_loses_good_zero": original[r] - max(u[r][1:]),
        "J_loses_good_one_without_getting_zero": original[r + 1] - max(u[r + 1][2:]),
    }
    bound = min(bounds.values())
    if bound <= 0:
        raise ValueError("nucleus bounds do not prove a positive temporary loss")
    observers = (0, 1, 0, r, r + 1)
    proportional = [Fraction(value, original[a]) for value, a in zip(bounds.values(), observers)]
    return {"nucleus": [0, 1, 2, 3, 4], "lower_bound": bound, "bounds": bounds,
            "proportional_lower_bound": str(min(proportional))}


def verify(doubles: int = 4, scale: int = 100) -> dict:
    u, start = family(doubles, scale)
    route = path(start)
    initial, final = totals(u, start), totals(u, route[-1])
    for row in u:
        if min(row) <= 0 or len(set(row)) != len(row):
            raise AssertionError("the profile is not positive and strict")
    for row in u[2:doubles]:
        if sum(sorted(row)[:2]) <= max(row):
            raise AssertionError("an ordinary recipient is not globally automatic")
    schedule = rounds_for(doubles + 2, len(start), tuple(range(doubles)))
    for witness, state in zip(witnesses(doubles), (start, route[-1])):
        validate_witness(u, schedule, witness)
        if allocation(witness, len(start)) != state:
            raise AssertionError("greedy witness has the wrong endpoint")
    if any(not ef1(u, state) for state in route):
        raise AssertionError("an intermediate allocation is unfair")
    if any(not exchange(a, b) for a, b in zip(route, route[1:])):
        raise AssertionError("a step is not one exchange")
    if any(b < a for a, b in zip(initial, final)) or not all(final[a] > initial[a] for a in (0, 1)):
        raise AssertionError("the endpoint is not an all-recipient Pareto improvement")
    certificate = barrier_certificate(u, start)
    expected = scale + 4 - len(start)
    actual = max(deficit(initial, totals(u, state)) for state in route)
    proportional = max(proportional_deficit(initial, totals(u, state)) for state in route)
    if certificate["lower_bound"] != expected or actual != expected:
        raise AssertionError("the lower bound and constructive upper bound disagree")
    if (Fraction(certificate["proportional_lower_bound"]) != proportional
            or proportional != Fraction(expected, 3 * scale + 9)):
        raise AssertionError("the proportional lower and upper bounds disagree")
    return {"double_recipients": doubles, "goods": len(start), "scale": scale,
            "optimal_maximum_temporary_loss": expected,
            "optimal_maximum_proportional_loss": str(proportional), **certificate,
            "utilities": u, "states": route, "totals": [totals(u, state) for state in route],
            "greedy_witnesses": witnesses(doubles)}


def audit(doubles: int = 3, scale: int = 100) -> dict:
    """Exhaust the unrestricted graph, then independently minimize path cost."""
    if doubles not in (2, 3):
        raise ValueError("full graph audits support only two or three doubles")
    u, start = family(doubles, scale)
    target = path(start)[-1]
    states = states_with_sizes((2,) * doubles + (1, 1))
    fair = {state for state in states if ef1(u, state)}
    initial = totals(u, start)
    costs = {state: deficit(initial, totals(u, state)) for state in fair}

    def neighbors(state):
        for x, y in combinations(range(len(state)), 2):
            if state[x] != state[y]:
                other = swap(state, x, y)
                if other in fair:
                    yield other

    floor_seen, todo = {start}, deque([start])
    while todo:
        for other in neighbors(todo.popleft()):
            if costs[other] == 0 and other not in floor_seen:
                floor_seen.add(other)
                todo.append(other)
    def minimize(vertex_cost):
        best, queue = {start: 0}, [(0, start)]
        while queue:
            value, state = heapq.heappop(queue)
            if value != best[state]:
                continue
            if state == target:
                return value
            for other in neighbors(state):
                candidate = max(value, vertex_cost[other])
                if other not in best or candidate < best[other]:
                    best[other] = candidate
                    heapq.heappush(queue, (candidate, other))
        raise AssertionError("target is unreachable even without utility floors")

    proportional = {state: proportional_deficit(initial, totals(u, state)) for state in fair}
    return {"all_states": len(states), "fair_states": len(fair),
            "source_floor_component": len(floor_seen),
            "target_in_source_floor_component": target in floor_seen,
            "independent_minimax_loss": minimize(costs),
            "independent_minimax_proportional_loss": str(minimize(proportional))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=4)
    parser.add_argument("--scale", type=int, default=100)
    parser.add_argument("--audit", action="store_true", help="full graph; only 2..3 pairs")
    args = parser.parse_args()
    try:
        report = verify(args.pairs, args.scale)
        if args.audit:
            report["complete_graph"] = audit(args.pairs, args.scale)
    except ValueError as error:
        parser.error(str(error))
    report["scope"] = "all-recipient greedy Pareto improvement; temporary-loss obstruction only"
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
