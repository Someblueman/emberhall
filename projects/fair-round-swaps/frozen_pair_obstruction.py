"""Exact obstruction to freezing a pair; not an unrestricted counterexample.

Run with --pairs 4 --enumerate. FROZEN_PAIR_OBSTRUCTION.md proves the family
for every r>=2, with strictly positive values and no maximizing ties.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import json
from math import factorial

from swaps import (Allocation, Profile, Witness, allocation, components, ef1,
                   exchange, rounds_for, validate_profile, validate_witness)


def example(pairs: int = 4) -> tuple[Profile, Witness, Witness]:
    """Return the r-pair family in canonical agent and good labels."""
    if type(pairs) is not int or pairs < 2:
        raise ValueError("need at least two pair recipients")
    r, m = pairs, 2 * pairs + 2
    rows = [tuple(2 * m - g for g in range(m)) for _ in range(r)]
    for favorite in (r + 1, r + 2):
        row = list(range(1, m + 1))
        row[0], row[r], row[m - 1], row[favorite] = 5*m, 3*m+1, 3*m, 4*m
        rows.append(tuple(row))
    anchors = tuple((i, i + 1) for i in range(r))
    tails = tuple((i, r + 2 + i) for i in range(1, r))
    left = ((r, 0),) + anchors + ((r + 1, r + 2), (0, r + 1)) + tails
    right = ((r + 1, 0),) + anchors + ((r, r + 1), (0, r + 2)) + tails
    return tuple(rows), left, right


def _bundles(u: Profile, state: Allocation) -> tuple[tuple[int, ...], ...]:
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (len(state) != m or any(type(i) is not int or i not in range(n) for i in state)):
        raise ValueError("state must assign every good to a known integer agent")
    return tuple(tuple(g for g, owner in enumerate(state) if owner == i) for i in range(n))


def separation_certificate(u: Profile, start: Allocation, target: Allocation,
                           frozen: int, favorite: int,
                           carriers: tuple[int, int]) -> dict | None:
    """Certify a cut when no nonfrozen pivot satisfies both singleton thresholds.

    None means this sufficient separation test failed, not that a path exists.
    The proof covers ALL allocations of the fixed sizes, not just pick outcomes.
    """
    a, b = _bundles(u, start), _bundles(u, target)
    n, m = len(u), len(start)
    if (len(carriers) != 2 or len(set(carriers)) != 2
            or any(type(i) is not int or i not in range(n) for i in carriers)
            or type(frozen) is not int or frozen not in range(n) or frozen in carriers
            or type(favorite) is not int or favorite not in range(m)
            or any(len(a[i]) != (1 if i in carriers else 2) for i in range(n))
            or tuple(map(len, a)) != tuple(map(len, b))):
        raise ValueError("need two singleton carriers, paired others and identical sizes")
    if (a[frozen] != b[frozen] or start[favorite] not in carriers
            or target[favorite] not in carriers or start[favorite] == target[favorite]
            or any(u[i][favorite] != max(u[i]) for i in carriers)
            or not ef1(u, start) or not ef1(u, target)):
        raise ValueError("need fair opposite favorite holders and the same frozen pair")
    pair = a[frozen]
    thresholds = {i: min(u[i][g] for g in pair) for i in carriers}
    exclusions = []
    for g in range(m):
        if g == favorite or g in pair:
            continue
        observer = next((i for i in carriers if u[i][g] < thresholds[i]), None)
        if observer is None:
            return None
        exclusions.append({"good": g, "observer": observer,
                           "value": u[observer][g], "threshold": thresholds[observer]})
    return {"favorite": favorite, "carriers": carriers, "frozen_owner": frozen,
            "frozen_pair": pair, "excluded_pivots": exclusions,
            "scope": "all fixed-size EF1 states with this pair fixed and favorite on carriers"}


def omitted_pair_failures(u: Profile, state: Allocation, frozen: int) -> list[dict]:
    """The exact additional inequalities when restoring a removed pair/agent.

    If the reduced allocation is EF1, the full allocation is EF1 iff this
    list is empty. Values and deletions here concern the restored pair only.
    """
    bundles = _bundles(u, state)
    if type(frozen) is not int or frozen not in range(len(u)) or len(bundles[frozen]) != 2:
        raise ValueError("frozen agent must hold exactly two goods")
    failures = []
    for i, row in enumerate(u):
        for j, goods in enumerate(bundles):
            if i == j or frozen not in (i, j):
                continue
            own = sum(row[g] for g in bundles[i])
            remainder = sum(row[g] for g in goods) - max((row[g] for g in goods), default=0)
            if own < remainder:
                failures.append({"observer": i, "target": j,
                                 "own": own, "after_best_deletion": remainder})
    return failures


def uniform_lift_guard(u: Profile, state: Allocation, frozen: int) -> bool:
    """Sufficient guard for lifting every EF1 reduced allocation of these sizes.

    The pair remains fixed, but all other goods may move. This is sufficient,
    not necessary; omitted_pair_failures gives the exact test on a chosen state.
    """
    bundles = _bundles(u, state)
    if (type(frozen) is not int or frozen not in range(len(u))
            or len(bundles[frozen]) != 2 or any(len(b) not in (1, 2) for b in bundles)):
        raise ValueError("need positive bundle sizes at most two and a frozen pair")
    pair = bundles[frozen]
    residual = tuple(g for g in range(len(state)) if g not in pair)
    for i, row in enumerate(u):
        if i != frozen:
            least_own = sum(sorted(row[g] for g in residual)[:len(bundles[i])])
            if least_own < min(row[g] for g in pair):
                return False
    has_other_pair = any(i != frozen and len(b) == 2 for i, b in enumerate(bundles))
    bound = sorted((u[frozen][g] for g in residual), reverse=True)[1] if has_other_pair else 0
    return sum(u[frozen][g] for g in pair) >= bound


def repair(pairs: int = 4) -> list[Allocation]:
    """The explicit four-exchange repair, permitting one frozen anchor to move."""
    u, left, right = example(pairs)
    m = len(u[0])
    rounds = rounds_for(len(u), m, tuple(range(pairs)))
    validate_witness(u, rounds, left)
    validate_witness(u, rounds, right)
    route = [allocation(left, m)]
    for g, h in ((pairs + 2, pairs), (0, pairs),
                 (pairs, pairs + 1), (pairs, pairs + 2)):
        state = list(route[-1])
        state[g], state[h] = state[h], state[g]
        route.append(tuple(state))
    if (route[-1] != allocation(right, m) or not all(ef1(u, a) for a in route)
            or not all(exchange(a, b) for a, b in zip(route, route[1:]))):
        raise AssertionError("explicit repair failed its exact checks")
    return route


def connect_guarded(u: Profile, start: Allocation, target: Allocation,
                    favorite: int, carriers: tuple[int, int], pivot: int) -> list[Allocation]:
    """Connect ALL protected fair states under the common-top-two/pair guard.

    Each double must value its two cheapest non-favorite goods together at
    least its most expensive non-favorite good. The pivot is top-two among
    non-favorite goods for both carriers. This is not a general constructor.
    """
    a, b = _bundles(u, start), _bundles(u, target)
    n, m = len(u), len(start)
    if (len(carriers) != 2 or len(set(carriers)) != 2
            or any(type(i) is not int or i not in range(n) for i in carriers)
            or type(favorite) is not int or favorite not in range(m)
            or type(pivot) is not int or pivot not in range(m) or pivot == favorite
            or any(len(a[i]) != (1 if i in carriers else 2) for i in range(n))
            or tuple(map(len, a)) != tuple(map(len, b))
            or any(state[favorite] not in carriers for state in (start, target))):
        raise ValueError("need two singleton carriers and a distinct favorite and pivot")
    doubles = tuple(i for i in range(n) if i not in carriers)
    goods = tuple(g for g in range(m) if g != favorite)
    for i, row in enumerate(u):
        if i in carriers:
            if (row[favorite] != max(row)
                    or sum(row[g] > row[pivot] for g in goods) > 1):
                raise ValueError("need a shared favorite and a common top-two pivot")
        else:
            values = sorted(row[g] for g in goods)
            if values[0] + values[1] < values[-1]:
                raise ValueError("double-recipient automatic-fairness guard fails")
    if not ef1(u, start) or not ef1(u, target):
        raise ValueError("endpoints must be EF1")
    if start == target:
        return [start]

    def swap(state, g, h):
        following = list(state)
        following[g], following[h] = following[h], following[g]
        return tuple(following)

    def normalize(state):
        other = next(i for i in carriers if i != state[favorite])
        held = state.index(other)
        return state if held == pivot else swap(state, held, pivot)

    route, goal = [start], normalize(target)
    normalized = normalize(start)
    if normalized != start:
        route.append(normalized)
    if route[-1][favorite] != goal[favorite]:
        route.append(swap(route[-1], favorite, pivot))
    for i in doubles:
        for g in range(m):
            if goal[g] == i and route[-1][g] != i:
                h = next(h for h in range(m) if route[-1][h] == i and goal[h] != i)
                route.append(swap(route[-1], g, h))
    if route[-1] != goal:
        raise AssertionError("pair reassignment missed the normalized target")
    if goal != target:
        route.append(target)
    if (len(route)-1 > 2*len(doubles)+2 or not all(ef1(u, state) for state in route)
            or not all(exchange(x, y) for x, y in zip(route, route[1:]))):
        raise AssertionError("guarded connectivity construction failed")
    return route


def restricted_census(u: Profile, start: Allocation, target: Allocation,
                      frozen: int, favorite: int, carriers: tuple[int, int]) -> dict:
    """Exhaust the entire restricted graph for at most four pairs (ten goods)."""
    certificate = separation_certificate(u, start, target, frozen, favorite, carriers)
    if certificate is None:
        raise ValueError("this census requires a valid separation certificate")
    if len(start) > 10:
        raise ValueError("exhaustive census is limited to ten goods")
    pair = certificate["frozen_pair"]
    doubles = tuple(i for i in range(len(u)) if i not in (*carriers, frozen))
    fair, total = [], 0

    def assign(agents, goods, state):
        if not agents:
            yield tuple(state)
            return
        for chosen in combinations(goods, 2):
            next_state = state[:]
            for g in chosen:
                next_state[g] = agents[0]
            yield from assign(agents[1:], tuple(g for g in goods if g not in chosen), next_state)

    pool = tuple(g for g in range(len(start)) if g not in (*pair, favorite))
    for holder, other in (carriers, carriers[::-1]):
        for singleton in pool:
            state = [frozen] * len(start)
            state[favorite], state[singleton] = holder, other
            for a in assign(doubles, tuple(g for g in pool if g != singleton), state):
                total += 1
                if ef1(u, a):
                    fair.append(a)
    groups = components(tuple(fair))
    return {"all_restricted_states": total, "ef1_states": len(fair),
            "component_sizes": sorted(map(len, groups)),
            "endpoints_separated": not any(start in group and target in group for group in groups)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=4)
    parser.add_argument("--enumerate", action="store_true", help="exhaust up to ten goods")
    args = parser.parse_args()
    try:
        u, left, right = example(args.pairs)
        route = repair(args.pairs)
        carriers = (args.pairs, args.pairs + 1)
        proof = separation_certificate(u, route[0], route[-1], args.pairs-1, 0, carriers)
        result = {"pairs": args.pairs, "utilities": u, "greedy_start": left,
                  "greedy_target": right, "certificate": proof, "repair": route,
                  "proved_component_sizes": [factorial(2*args.pairs-2)//2**(args.pairs-1)]*2,
                  "scope": "frozen-pair obstruction; the original endpoints ARE connected"}
        if args.enumerate:
            result["census"] = restricted_census(u, route[0], route[-1], args.pairs-1, 0, carriers)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
