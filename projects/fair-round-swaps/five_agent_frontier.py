"""An obstruction to unrestricted EF1 induction, plus an exact endpoint recognizer."""

from __future__ import annotations

from itertools import combinations, product
import json

from swaps import (Allocation, Profile, Witness, components, ef1,
                   states_with_sizes, validate_profile)


def _order(u: Profile, picks: dict[int, int]) -> tuple[int, ...] | None:
    """Topologically order picks so every strictly preferred assigned good goes first."""
    before = {i: {j for j in picks if u[i][picks[j]] > u[i][picks[i]]}
              for i in picks}
    result = []
    while before:
        ready = [i for i, predecessors in before.items() if not predecessors]
        if not ready:
            return None
        i = min(ready)
        result.append(i)
        del before[i]
        for predecessors in before.values():
            predecessors.discard(i)
    return tuple(result)


def greedy_witness(u: Profile, owners: Allocation) -> Witness | None:
    """Recognize one complete greedy round followed by a possibly partial round.

    Bundle sizes must be one or two, with fewer goods than two full rounds.
    The search considers 2**r final-good choices and two precedence graphs;
    it does not enumerate picking orders or discretize utility gaps.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (len(owners) != m or any(type(i) is not int or i not in range(n) for i in owners)
            or not n <= m < 2 * n):
        raise ValueError("need a valid allocation between one and two full rounds")
    bundles = {i: tuple(g for g, a in enumerate(owners) if a == i) for i in range(n)}
    if any(len(goods) not in (1, 2) for goods in bundles.values()):
        raise ValueError("each bundle must contain one or two goods")
    doubled = tuple(i for i in range(n) if len(bundles[i]) == 2)
    for final_goods in product(*(bundles[i] for i in doubled)):
        final = dict(zip(doubled, final_goods))
        first = {i: next(g for g in bundles[i] if g != final.get(i)) for i in range(n)}
        if any(u[i][first[i]] < u[i][g] for i in range(n) for g in final.values()):
            continue
        early, late = _order(u, first), _order(u, final)
        if early is not None and late is not None:
            return tuple((i, first[i]) for i in early) + tuple((i, final[i]) for i in late)
    return None


EXAMPLE: Profile = (
    (0, 8, 10, 6, 2, 3, 0),
    (0, 1, 6, 2, 0, 4, 0),
    (4, 0, 3, 4, 2, 1, 5),
    (3, 1, 4, 2, 0, 4, 0),
    (1, 1, 1, 1, 0, 1, 2),
)
ISOLATED: Allocation = (3, 1, 1, 0, 2, 0, 4)
TWO_STATE_PROFILE: Profile = (
    (6, 2, 1, 7, 12, 4), (2, 7, 1, 12, 4, 6),
    (3, 1, 1, 2, 0, 4), (0, 1, 2, 1, 3, 4),
)
TWO_STATE_COMPONENT = ((1, 0, 2, 3, 1, 0), (1, 0, 3, 2, 1, 0))


def certificate() -> dict:
    states = states_with_sizes((2, 2, 1, 1, 1))
    fair = tuple(a for a in states if ef1(EXAMPLE, a))
    groups = components(fair)
    protected = tuple(a for a in fair if a[6] in (2, 4))
    protected_groups = components(protected)
    greedy = {a for a in states if greedy_witness(EXAMPLE, a) is not None}
    rejected = []
    for x, y in combinations(range(7), 2):
        if ISOLATED[x] == ISOLATED[y]:
            continue
        changed = list(ISOLATED)
        changed[x], changed[y] = changed[y], changed[x]
        if ef1(EXAMPLE, tuple(changed)):
            raise AssertionError("claimed isolated state has a fair neighbor")
        rejected.append((x, y))
    second_fair = tuple(a for a in states_with_sizes((2, 2, 1, 1)) if ef1(TWO_STATE_PROFILE, a))
    second_groups = components(second_fair)
    second_greedy = {a for a in second_fair if greedy_witness(TWO_STATE_PROFILE, a) is not None}
    return {"states": len(states), "ef1_states": len(fair),
            "component_sizes": sorted(map(len, groups)),
            "protected_states": len(protected),
            "protected_component_sizes": sorted(map(len, protected_groups)),
            "isolated_owners": ISOLATED, "rejected_exchanges": len(rejected),
            "isolated_is_greedy": ISOLATED in greedy,
            "greedy_states": len(greedy),
            "greedy_per_component": sorted(len(set(group) & greedy) for group in groups),
            "nonisolated_boundary": {
                "ef1_states": len(second_fair),
                "component_sizes": sorted(map(len, second_groups)),
                "two_state_component": TWO_STATE_COMPONENT,
                "greedy_per_component": sorted(len(set(group) & second_greedy) for group in second_groups)}}


if __name__ == "__main__":
    print(json.dumps(certificate(), indent=2))
