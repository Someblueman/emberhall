"""A sharp temporary-loss barrier despite arbitrarily many automatic pairs.

This is a counterexample to value-preserving attachment, not to EF1 connectivity.
The two displayed paths are fair. Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
from itertools import combinations
import json
from math import factorial

from swaps import (Allocation, Profile, allocation, ef1, exchange, rounds_for,
                   validate_profile, validate_witness)


def family(doubles: int = 4, scale: int | None = 100) -> tuple[Profile, Allocation]:
    """Return the tied family, or a positive strict refinement when scale is set.

    Agents 0,1 are exceptional; 2,...,r-1 are automatic; r and r+1 are
    singletons. Good zero initially belongs to r. All source labels are explicit.
    """
    if type(doubles) is not int or doubles < 2:
        raise ValueError("need at least two double recipients")
    m = 2 * doubles + 2
    if scale is not None and (type(scale) is not int or scale <= m):
        raise ValueError("strict scale must be an integer larger than the good count")
    rows = [
        [0, 1, 2, 2, 1, 0] + [0] * (m - 6),
        [0, 1, 0, 2, 0, 1] + [0] * (m - 6),
    ]
    rows.extend([[1] * m for _ in range(doubles - 2)])
    rows.extend([[3, 2, 1, 0, 0, 0] + [0] * (m - 6) for _ in range(2)])
    if scale is not None:
        for i, row in enumerate(rows):
            offsets = list(range(1, m + 1))
            if i == 0:
                offsets[2], offsets[3] = offsets[3], offsets[2]
            rows[i] = [scale * value + offset for value, offset in zip(row, offsets)]
    start = (doubles, 1, doubles + 1, 0, 0, 1)
    start += tuple(i for i in range(2, doubles) for _ in range(2))
    return tuple(map(tuple, rows)), start


def swap(state: Allocation, x: int, y: int) -> Allocation:
    following = list(state)
    following[x], following[y] = following[y], following[x]
    return tuple(following)


def routes(start: Allocation) -> tuple[list[Allocation], ...]:
    """Absolute optimum, B-sacrifice shortcut, and proportional-loss route."""
    minimum_loss = [start]
    if len(start) == 6:
        moves = ((1, 4), (1, 2), (3, 4))
    else:
        buffer = len(start) - 1
        moves = ((1, buffer), (1, 2), (2, 3), (3, buffer))
    for x, y in moves:
        minimum_loss.append(swap(minimum_loss[-1], x, y))
    preserve_a = [start]
    for x, y in ((1, 2), (2, 3)):
        preserve_a.append(swap(preserve_a[-1], x, y))
    proportional = [start]
    for x, y in ((1, 3), (1, 2)):
        proportional.append(swap(proportional[-1], x, y))
    return minimum_loss, preserve_a, proportional


def totals(u: Profile, state: Allocation) -> tuple:
    """Totals of A, B, and both singleton recipients, in that order."""
    return tuple(sum(row[g] for g, owner in enumerate(state) if owner == a)
                 for a, row in ((0, u[0]), (1, u[1]),
                                (len(u) - 2, u[-2]), (len(u) - 1, u[-1])))


def deficit(initial: tuple, current: tuple):
    return max((0,) + tuple(a - b for a, b in zip(initial, current)))


def barrier_certificate(u: Profile, start: Allocation) -> dict:
    """Check every possible first core-changing exchange, including unfair ones.

    While core goods 0,...,5 retain their owners, low goods 6,...,m-1 can
    only permute among automatic recipients. Their owners do not affect a
    core recipient's value loss. One representative placement therefore
    covers every departure edge from that whole set, not just from start.
    """
    validate_profile(u)
    r, m = len(u) - 2, len(u[0])
    if (r < 2 or m != 2 * r + 2 or len(start) != m
            or start[:6] != (r, 1, r + 1, 0, 0, 1)
            or sorted(start[6:]) != [a for a in range(2, r) for _ in range(2)]):
        raise ValueError("need the stated core and automatic-pair placement")
    initial = totals(u, start)
    losses = []
    for x, y in combinations(range(m), 2):
        if start[x] == start[y] or x >= 6:
            continue
        losses.append(deficit(initial, totals(u, swap(start, x, y))))
    bound = min(losses)
    if bound <= 0:
        raise ValueError("this profile does not certify a positive departure barrier")
    return {"departure_exchanges": len(losses), "minimum_departure_loss": bound,
            "fixed_core_component_size": factorial(m - 6) // (2 ** (r - 2))}


def verify(doubles: int = 4, scale: int | None = 100) -> dict:
    u, start = family(doubles, scale)
    initial = totals(u, start)
    certificate = barrier_certificate(u, start)
    expected = (1 if scale is None else
                scale - 3 if doubles == 2 else scale + 2 - len(start))
    if certificate["minimum_departure_loss"] != expected:
        raise AssertionError("departure lower bound disagrees with the formula")
    for row in u[2:doubles]:
        ordered = sorted(row)
        if ordered[0] + ordered[1] < ordered[-2]:
            raise AssertionError("an ordinary double is not automatic")
    checked = []
    for path in routes(start):
        if any(not ef1(u, state) or state[0] != doubles for state in path):
            raise AssertionError("the displayed route is not a fair fixed-owner path")
        if any(not exchange(a, b) for a, b in zip(path, path[1:])):
            raise AssertionError("the displayed route contains a non-exchange")
        values = [totals(u, state) for state in path]
        if any(b < a for a, b in zip(initial, values[-1])):
            raise AssertionError("the target is not a weak Pareto improvement")
        checked.append({"exchanges": len(path) - 1, "states": path,
                        "totals": values,
                        "maximum_temporary_loss": max(deficit(initial, v) for v in values),
                        "maximum_proportional_loss": str(max(
                            Fraction(max(0, a - b), a) for v in values
                            for a, b in zip(initial, v)))})
    if checked[0]["maximum_temporary_loss"] != expected:
        raise AssertionError("the constructive upper bound is not sharp")
    return {"double_recipients": doubles, "goods": len(start), "scale": scale,
            **certificate, "optimal_maximum_temporary_loss": expected, "routes": checked}


def greedy_family(doubles: int = 4, scale: int | None = 100) -> tuple[Profile, Allocation]:
    """Strict greedy endpoints with an indispensable temporary sacrifice."""
    _, start = family(doubles, scale)
    if doubles < 3:
        raise ValueError("the greedy-endpoint family needs an automatic buffer pair")
    m = len(start)
    rows = [[0, 10, 19, 20, 10, 0, 12, 0] + [0] * (m - 8),
            [0, 10, 0, 20, 0, 10, 0, 0] + [0] * (m - 8)]
    for a in range(2, doubles):
        row = [10] * m
        row[2 * a + 2], row[2 * a + 3] = 11, 12
        rows.append(row)
    rows.extend([[30, 20, 10] + [0] * (m - 3) for _ in range(2)])
    if scale is not None:
        for a, row in enumerate(rows):
            offsets = list(range(1, m + 1))
            if a == 0:
                offsets[2], offsets[3] = offsets[3], offsets[2]
            elif a == 1:
                offsets[1], offsets[5] = offsets[5], offsets[1]
            rows[a] = [scale * value + offset for value, offset in zip(row, offsets)]
    return tuple(map(tuple, rows)), start


def greedy_route(start: Allocation) -> list[Allocation]:
    path = [start]
    for x, y in ((4, 6), (3, 4), (1, 3), (1, 2), (2, 4)):
        path.append(swap(path[-1], x, y))
    return path


def greedy_witnesses(doubles: int):
    anchors = tuple((a, 2 * a + 3) for a in range(2, doubles))
    tails = tuple((a, 2 * a + 2) for a in range(2, doubles))
    source = ((0, 3), (doubles, 0), (1, 1), (doubles + 1, 2))
    source += anchors + tails + ((0, 4), (1, 5))
    target = ((doubles, 0), (doubles + 1, 1), (1, 3), (0, 2))
    target += anchors + ((0, 6),) + tails[1:] + ((1, 5), (2, 4))
    return source, target


def greedy_barrier_certificate(u: Profile, start: Allocation) -> dict:
    """Numeric premises of the four-good nucleus proof, using exact values.

    Before the first change of owners of goods 0,1,2,3, a path staying
    strictly below the proposed deficit must also keep good 5 with B.
    The other four inequalities rule out every possible first change.
    """
    validate_profile(u)
    r, m = len(u) - 2, len(u[0])
    if (r < 3 or m != 2 * r + 2 or len(start) != m
            or start[:6] != (r, 1, r + 1, 0, 0, 1)):
        raise ValueError("need the stated greedy-endpoint core")
    a, b, inactive, active = totals(u, start)
    upper_a = sum(sorted(u[0][g] for g in range(m) if g not in (0, 2, 3))[-2:])
    bound = a - upper_a
    premises = {
        "A_without_good_3": bound,
        "I_loses_good_0": inactive - max(u[r][1:]),
        "S_loses_good_2_without_getting_0_or_1": active - max(u[-1][3:]),
        "B_without_good_5_before_nucleus_changes":
            b - u[1][1] - max(u[1][g] for g in range(m) if g not in (0, 1, 2, 3, 5)),
        "B_loses_good_1_while_keeping_5_without_getting_3":
            b - u[1][5] - max(u[1][g] for g in range(m) if g not in (0, 1, 3, 5)),
    }
    if bound <= 0 or any(value < bound for value in premises.values()):
        raise ValueError("nucleus inequalities do not establish a positive barrier")
    return {"minimum_nucleus_loss": bound, "premises": premises}


def verify_greedy(doubles: int = 4, scale: int | None = 100) -> dict:
    u, start = greedy_family(doubles, scale)
    path = greedy_route(start)
    initial = totals(u, start)
    certificate = greedy_barrier_certificate(u, start)
    expected = 8 if scale is None else 8 * scale - 4
    if certificate["minimum_nucleus_loss"] != expected:
        raise AssertionError("greedy nucleus bound disagrees with the formula")
    for row in u[2:doubles]:
        ordered = sorted(row)  # Automatic even if good zero enters a pair.
        if ordered[0] + ordered[1] < ordered[-2]:
            raise AssertionError("an ordinary double is not globally automatic")
    for witness, state in zip(greedy_witnesses(doubles), (start, path[-1])):
        validate_witness(u, rounds_for(doubles + 2, len(start), tuple(range(doubles))), witness)
        if allocation(witness, len(start)) != state:
            raise AssertionError("greedy witness has the wrong endpoint")
    if any(not ef1(u, state) for state in path):
        raise AssertionError("the greedy-endpoint path is not fair")
    if any(not exchange(a, b) for a, b in zip(path, path[1:])):
        raise AssertionError("the greedy-endpoint path contains a non-exchange")
    values = [totals(u, state) for state in path]
    if any(b < a for a, b in zip(initial, values[-1])):
        raise AssertionError("a constrained recipient loses value at the target")
    actual = max(deficit(initial, value) for value in values)
    if actual != expected:
        raise AssertionError("greedy-endpoint upper bound does not attain the lower bound")
    return {"double_recipients": doubles, "goods": len(start), "scale": scale,
            "optimal_maximum_temporary_loss": expected, **certificate,
            "path": path, "totals": values, "greedy_witnesses": greedy_witnesses(doubles)}


class OwnerGraph:
    """Complete graphs for audits: fixed-g through r=4, unrestricted through r=3."""

    def __init__(self, doubles: int, fixed_g: bool = True):
        if (type(doubles) is not int or doubles not in (2, 3, 4)
                or not fixed_g and doubles == 4):
            raise ValueError("complete audits support 2..4 doubles, full graphs only 2..3")
        self.r, self.m = doubles, 2 * doubles + 2
        states = []

        def assign(agent, remaining, state):
            if agent == doubles:
                states.append(tuple(state))
                return
            for x, y in combinations(remaining, 2):
                following = state[:]
                following[x] = following[y] = agent
                assign(agent + 1, tuple(g for g in remaining if g not in (x, y)), following)

        for inactive in ((0,) if fixed_g else range(self.m)):
            for singleton in range(self.m):
                if singleton == inactive:
                    continue
                state = [-1] * self.m
                state[inactive], state[singleton] = doubles, doubles + 1
                assign(0, tuple(g for g in range(self.m) if g not in (inactive, singleton)), state)
        self.states = tuple(states)
        self.index = {state: i for i, state in enumerate(self.states)}
        self.adjacency = tuple(tuple(self.index[swap(state, x, y)]
                                     for x, y in combinations(range(1 if fixed_g else 0, self.m), 2)
                                     if state[x] != state[y]) for state in self.states)

    def fair_vertices(self, u: Profile) -> set[int]:
        """Exact specialized EF1 predicate; automatic guard checked by verify."""
        result = set()
        for i, state in enumerate(self.states):
            bundles = [[g for g, a in enumerate(state) if a == j] for j in range(self.r)]
            if all(sum(row[g] for g, a in enumerate(state) if a == observer)
                   >= max(min(row[x], row[y]) for x, y in bundles)
                   for observer, row in ((0, u[0]), (1, u[1]),
                                         (self.r, u[-2]), (self.r + 1, u[-1]))):
                result.add(i)
        return result

    def reachable(self, allowed: set[int], start: int) -> set[int]:
        if start not in allowed:
            raise ValueError("start must belong to the induced graph")
        reached, queue = {start}, deque([start])
        while queue:
            for other in self.adjacency[queue.popleft()]:
                if other in allowed and other not in reached:
                    reached.add(other)
                    queue.append(other)
        return reached


def audit(doubles: int = 4, scale: int | None = 100) -> dict:
    u, start = family(doubles, scale)
    graph = OwnerGraph(doubles)
    fair = graph.fair_vertices(u)
    initial = totals(u, start)
    floors = {i for i in fair if deficit(initial, totals(u, graph.states[i])) == 0}
    component = graph.reachable(floors, graph.index[start])
    target = graph.index[routes(start)[0][-1]]
    certificate = barrier_certificate(u, start)
    if len(component) != certificate["fixed_core_component_size"] or target in component:
        raise AssertionError("finite graph disagrees with the general departure proof")
    return {"all_states": len(graph.states), "undirected_edges": sum(map(len, graph.adjacency)) // 2,
            "fair_states": len(fair), "floor_states": len(floors),
            "full_start_component": len(graph.reachable(fair, graph.index[start])),
            "floor_start_component": len(component), "target_meets_floors": target in floors,
            "target_in_floor_start_component": target in component}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=4)
    parser.add_argument("--scale", type=int, default=100)
    parser.add_argument("--ties", action="store_true")
    parser.add_argument("--greedy", action="store_true", help="use the greedy-endpoint family")
    parser.add_argument("--audit", action="store_true", help="complete graph; only 2..4 pairs")
    args = parser.parse_args()
    scale = None if args.ties else args.scale
    try:
        report = verify_greedy(args.pairs, scale) if args.greedy else verify(args.pairs, scale)
        if args.audit:
            if args.greedy:
                parser.error("--audit currently checks the smaller first-departure family")
            report["complete_graph"] = audit(args.pairs, scale)
    except ValueError as error:
        parser.error(str(error))
    report["scope"] = "temporary-loss barrier; not a disconnection of the full EF1 graph"
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
