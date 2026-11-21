"""Connect all EF1 one-pair allocations with binary singleton preferences.

Normalization takes at most one exchange per singleton. The final connection
uses the existing one-extra-good greedy-endpoint theorem in single_extra.
"""
from __future__ import annotations

import json

from single_extra import one_extra_bundles, path as greedy_path
from swaps import allocation, ef1, exchange, validate_profile, validate_witness


def reduced_profile(utilities):
    """Preserve the full EF1 graph; pair recipient 0's row is immaterial."""
    validate_profile(utilities)
    n, m = len(utilities), len(utilities[0])
    if m != n + 1:
        raise ValueError("need exactly one extra good")
    if any(len(set(row)) > 2 for row in utilities[1:]):
        raise ValueError("singleton rows must have at most two values")
    return ((0,) * m,) + tuple(tuple(int(v > min(row)) for v in row)
                              for row in utilities[1:])


def _holdings(state, n):
    return (tuple(g for g, owner in enumerate(state) if owner == 0),
            {i: state.index(i) for i in range(1, n)})


def _swap(state, g, h):
    changed = list(state)
    changed[g], changed[h] = changed[h], changed[g]
    return tuple(changed)


def _satisfied(u, state):
    return sum(u[i][state.index(i)] for i in range(1, len(u)))


def normal_witness(utilities, state):
    """Greedy witness for a state with safe pair goods and no low-low envy."""
    u = reduced_profile(utilities)
    state = tuple(state)
    _, doubled = one_extra_bundles(u, state)
    if doubled != 0:
        raise ValueError("recipient zero must own the pair")
    pair, own = _holdings(state, len(u))
    high = [i for i in own if u[i][own[i]]]
    low = [i for i in own if not u[i][own[i]]]
    witness = ((0, pair[0]),) + tuple((i, own[i]) for i in high + low) + ((0, pair[1]),)
    validate_witness(u, (tuple(range(len(u))), (0,)), witness)
    assert allocation(witness, len(state)) == state
    return witness


def normalize(utilities, start):
    """Reach a greedy endpoint for the reduced profile in at most n-1 swaps."""
    u = reduced_profile(utilities)
    state = tuple(start)
    _, doubled = one_extra_bundles(u, state)
    if doubled != 0:
        raise ValueError("recipient zero must own the pair")
    if not ef1(u, state):
        raise ValueError("start must be EF1")
    route = [state]
    initial = _satisfied(u, state)

    def append(changed):
        nonlocal state
        assert exchange(state, changed) and ef1(u, changed)
        assert _satisfied(u, changed) > _satisfied(u, state)
        route.append(changed)
        state = changed

    # Make both pair goods safe. A blocked improvement supplies a low recipient
    # who strictly improves by receiving the original low good instead.
    while True:
        pair, own = _holdings(state, len(u))
        candidate = next(((i, h) for i in own if not u[i][own[i]]
                          for h in pair if u[i][h]), None)
        if candidate is None:
            break
        i, h = candidate
        changed = _swap(state, own[i], h)
        if ef1(u, changed):
            append(changed)
            continue
        other = next(g for g in pair if g != h)
        j = next(j for j in own if j != i and not u[j][own[j]]
                 and u[j][own[i]] and u[j][other])
        append(_swap(state, own[i], own[j]))

    # Pair goods now stay fixed. Exchanging two low holders cannot lower either
    # utility; if one desires the other's good, at least one becomes high.
    while True:
        _, own = _holdings(state, len(u))
        low = [i for i in own if not u[i][own[i]]]
        candidate = next(((i, j) for i in low for j in low if i != j and u[i][own[j]]), None)
        if candidate is None:
            break
        i, j = candidate
        append(_swap(state, own[i], own[j]))
    normal_witness(u, state)
    assert len(route) - 1 <= len(u) - 1 - initial
    return tuple(route)


def path(utilities, start, target):
    """Connect arbitrary fair binary endpoints, not just greedy endpoints."""
    u = reduced_profile(utilities)
    left, right = normalize(utilities, start), normalize(utilities, target)
    middle = greedy_path(u, left[-1], right[-1])
    result = left + tuple(middle[1:]) + right[-2::-1]
    assert result[0] == tuple(start) and result[-1] == tuple(target)
    assert all(ef1(utilities, state) for state in result)
    assert all(exchange(a, b) for a, b in zip(result, result[1:]))
    return result


def example(singletons=6):
    """A fair nongreedy start with opposing pair favorites and a strict cycle."""
    k = singletons
    if type(k) is not int or k < 2 or k % 2:
        raise ValueError("the example uses an even number of singletons")
    u = [tuple(range(k + 2))]
    for i in range(k):
        row = [2] * (k + 2)
        row[(i + 1) % k] = row[k + i % 2] = 7
        u.append(tuple(row))
    start = tuple(range(1, k + 1)) + (0, 0)
    target = (k,) + tuple(range(1, k)) + (0, 0)
    return tuple(u), start, target


def main():
    u, start, target = example()
    first, last = normalize(u, start), normalize(u, target)
    route = path(u, start, target)
    print(json.dumps({"singleton_recipients": len(u) - 1,
                      "start_normalization_swaps": len(first) - 1,
                      "target_normalization_swaps": len(last) - 1,
                      "path_swaps": len(route) - 1, "path": route,
                      "verified": "original EF1, fixed sizes, single exchanges"}, indent=2))


if __name__ == "__main__":
    main()
