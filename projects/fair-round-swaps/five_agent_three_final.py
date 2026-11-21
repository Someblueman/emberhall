"""Exact obstructions to full-graph lemmas for the three-final boundary.

These isolated allocations are not greedy outcomes. They do not refute
connectivity between greedy endpoints. See FIVE_AGENT_THREE_FINAL.md.
"""

from __future__ import annotations

from itertools import combinations
import json

from swaps import (Allocation, Profile, components, ef1, picking_outcomes,
                   rounds_for, states_with_sizes, validate_profile)

# Goods a,b,c,d,e,f,t (and g); agents A,B,C,S (and P).
SIDE: Profile = (
    (1, 0, 2, 0, 0, 2, 2),
    (2, 0, 1, 0, 2, 0, 2),
    (0, 0, 0, 1, 0, 0, 1),
    (0, 2, 2, 0, 2, 0, 1),
)
SIDE_STATE: Allocation = (0, 0, 1, 1, 2, 2, 3)
EIGHT: Profile = (
    SIDE[0] + (2,),
    SIDE[1] + (2,),
    SIDE[2] + (1,),
    SIDE[3] + (3,),
    (2, 2, 2, 0, 2, 0, 0, 3),
)
EIGHT_STATE: Allocation = SIDE_STATE + (4,)


def strict_refinement(u: Profile) -> Profile:
    """The proved positive, tie-free refinement of these two profiles only."""
    if u not in (SIDE, EIGHT):
        raise ValueError("refinement is certified only for the two stated profiles")
    return tuple(tuple(20 * value + good + 1 for good, value in enumerate(row))
                 for row in u)


def rejected_exchanges(u: Profile, a: Allocation) -> list[dict]:
    """Give an exact best-deletion violation for every cross-owner exchange.

    A successful exchange is an error: this function certifies isolation,
    rather than returning an incomplete list of failed moves.
    """
    validate_profile(u)
    if not ef1(u, a):
        raise ValueError("the alleged isolated allocation is not EF1")
    failures = []
    for x, y in combinations(range(len(a)), 2):
        if a[x] == a[y]:
            continue
        changed = list(a)
        changed[x], changed[y] = changed[y], changed[x]
        violation = None
        for i, row in enumerate(u):
            own = sum(row[g] for g, owner in enumerate(changed) if owner == i)
            for j in range(len(u)):
                goods = tuple(g for g, owner in enumerate(changed) if owner == j)
                residual = sum(row[g] for g in goods) - max(
                    (row[g] for g in goods), default=0)
                if own < residual:
                    violation = {"swap": [x, y], "observer": i, "envied": j,
                                 "own": own, "after_best_deletion": residual}
                    break
            if violation is not None:
                break
        if violation is None:
            raise ValueError(f"exchange {(x, y)} preserves EF1")
        failures.append(violation)
    return failures


def certificate(u: Profile, a: Allocation) -> dict:
    """Enumerate the entire fixed-size graph and every greedy outcome exactly."""
    rejected = rejected_exchanges(u, a)
    sizes = tuple(a.count(i) for i in range(len(u)))
    if sizes not in ((2, 2, 2, 1), (2, 2, 2, 1, 1)):
        raise ValueError("certificate requires the stated four- or five-agent size vector")
    states = states_with_sizes(sizes)
    fair = tuple(state for state in states if ef1(u, state))
    groups = components(fair)
    greedy = picking_outcomes(u, rounds_for(len(u), len(a), (0, 1, 2)))
    group_of = {state: i for i, group in enumerate(groups) for state in group}
    if not set(greedy) <= set(fair):
        raise AssertionError("greedy outcome failed the independent EF1 predicate")
    result = {
        "allocations": len(states), "ef1": len(fair),
        "component_sizes": sorted(map(len, groups)),
        "greedy_outcomes": len(greedy), "isolated_is_greedy": a in greedy,
        "greedy_component_sizes": sorted({len(groups[group_of[b]]) for b in greedy}),
        "isolated": "".join(map(str, a)), "rejected_exchanges": rejected,
    }
    if len(u) == 5:
        protected = tuple(state for state in fair if state[7] in (3, 4))
        result["favorite_protected"] = {
            "vertices": len(protected),
            "component_sizes": sorted(map(len, components(protected))),
        }
    return result


def main() -> None:
    result = {}
    for name, u, a in (("four_agents_seven_goods", SIDE, SIDE_STATE),
                       ("five_agents_eight_goods", EIGHT, EIGHT_STATE)):
        result[name] = certificate(u, a)
        result[name]["positive_strict_refinement"] = certificate(strict_refinement(u), a)
    result["scope"] = ("Exact nongreedy isolated states. Full-side and protected-graph "
                       "connectivity fail; the greedy-endpoint question stays open.")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
