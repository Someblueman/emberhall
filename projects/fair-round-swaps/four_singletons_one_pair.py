"""Exact six-good EF1 graphs: one pair and four singleton recipients.

Only the singleton rows matter. Utilities reduce exactly to weak orders here;
this reduction must not be used when two or more bundles have two goods.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from random import Random
import time

from single_extra import isolated_family as prior_isolated_family


STATES = tuple(sorted(set(permutations((0, 0, 1, 2, 3, 4)))))
INDEX = {state: k for k, state in enumerate(STATES)}
PAIRS = tuple(tuple(g for g, owner in enumerate(state) if owner == 0)
              for state in STATES)
OWN = tuple(tuple(state.index(i) for state in STATES) for i in range(1, 5))


def neighbors(state):
    """All fourteen exchanges; moving inside the pair is not an edge."""
    for x, y in combinations(range(6), 2):
        if state[x] != state[y]:
            changed = list(state)
            changed[x], changed[y] = changed[y], changed[x]
            yield tuple(changed)


ADJACENCY = tuple(sum(1 << INDEX[other] for other in neighbors(state))
                  for state in STATES)


def ranks(row):
    if len(row) != 6 or any(type(v) not in (int, Fraction) or v < 0 for v in row):
        raise ValueError("each singleton needs six exact nonnegative values")
    levels = {v: k for k, v in enumerate(sorted(set(row)))}
    return tuple(levels[v] for v in row)


@lru_cache(maxsize=None)
def row_mask(row, observer):
    return sum(1 << k for k, (a, b) in enumerate(PAIRS)
               if row[OWN[observer][k]] >= min(row[a], row[b]))


def fair_mask(rows):
    if len(rows) != 4:
        raise ValueError("need four singleton utility rows")
    mask = (1 << len(STATES)) - 1
    for i, row in enumerate(rows):
        mask &= row_mask(ranks(row), i)
    return mask


def component(mask, start=None):
    """Complete component, represented by bits in the fixed state list."""
    if not mask:
        return 0
    frontier = mask & -mask if start is None else 1 << start
    if not frontier & mask:
        raise ValueError("component root must be a fair state")
    reached = frontier
    while frontier and reached != mask:
        expanded = 0
        while frontier:
            bit = frontier & -frontier
            expanded |= ADJACENCY[bit.bit_length() - 1]
            frontier ^= bit
        frontier = expanded & mask & ~reached
        reached |= frontier
    return reached


def components(mask):
    result = []
    while mask:
        part = component(mask)
        result.append(part)
        mask ^= part
    return tuple(result)


def shortest_path(rows, start, target):
    start, target = tuple(start), tuple(target)
    mask = fair_mask(rows)
    if start not in INDEX or target not in INDEX:
        raise ValueError("endpoints must have sizes (2,1,1,1,1)")
    first, last = INDEX[start], INDEX[target]
    if not ((mask >> first) & (mask >> last) & 1):
        raise ValueError("endpoints must be EF1")
    previous = {first: None}
    queue = deque([first])
    while queue and last not in previous:
        i = queue.popleft()
        next_bits = ADJACENCY[i] & mask
        while next_bits:
            bit = next_bits & -next_bits
            j = bit.bit_length() - 1
            next_bits ^= bit
            if j not in previous:
                previous[j] = i
                queue.append(j)
    if last not in previous:
        raise ValueError("fair endpoints are disconnected")
    path = [last]
    while previous[path[-1]] is not None:
        path.append(previous[path[-1]])
    return tuple(STATES[i] for i in reversed(path))


def sorted_orders():
    """One sorted representative of every six-good weak-order block shape."""
    return tuple((0,) + tuple(sum(bits[:j]) for j in range(1, 6))
                 for bits in product((0, 1), repeat=5))


def binary_orders():
    """One row per distinct binary fairness predicate (57 in total)."""
    by_mask = {}
    for row in product((0, 1), repeat=6):
        by_mask.setdefault(row_mask(row, 0), row)
    return tuple(sorted(by_mask.values()))


def census_profiles():
    """Cover one arbitrary observer and three observers with at most two values."""
    for first in sorted_orders():
        for others in combinations_with_replacement(binary_orders(), 3):
            yield (first,) + others


def sampled_profiles(count, seed):
    """Finite falsification only; cycles through strict, binary, and tied rows."""
    rng = Random(seed)
    for k in range(count):
        rows = []
        for _ in range(4):
            if k % 3 == 0:
                row = list(range(6))
                rng.shuffle(row)
            else:
                row = [rng.randrange(2 if k % 3 == 1 else 4) for _ in range(6)]
            rows.append(tuple(row))
        yield tuple(rows)


def deletion_failure(utilities, state):
    """Return an actual failed original EF1 comparison, or None."""
    bundles = [tuple(g for g, owner in enumerate(state) if owner == i)
               for i in range(len(utilities))]
    for i, row in enumerate(utilities):
        own = sum(row[g] for g in bundles[i])
        for j, bundle in enumerate(bundles):
            remainders = [sum(row[g] for g in bundle if g != removed)
                          for removed in bundle]
            if remainders and own < min(remainders):
                return {"observer": i, "target": j, "own": own,
                        "least_remainder": min(remainders)}
    return None


def fair_neighbor_or_cycle(utilities, state):
    """Find a fair neighbor or an alternating strict envy cycle of length >= 4.

    The cycle outcome is not by itself a claim of isolation. For an isolated
    state this algorithm must return a cycle, proving that it is nongreedy.
    Every cycle member has goods strictly below and above its current value.
    """
    k = len(utilities) - 1
    state = tuple(state)
    if (k < 1 or len(state) != k + 2 or any(len(r) != k + 2 for r in utilities)
            or any(type(v) not in (int, Fraction) or v < 0 for r in utilities for v in r)
            or sorted(state) != [0, 0] + list(range(1, k + 1))):
        raise ValueError("need exact nonnegative utilities and sizes (2,1,...,1)")
    if deletion_failure(utilities, state) is not None:
        raise ValueError("start must be EF1")
    pair = [g for g, owner in enumerate(state) if owner == 0]
    own = {i: state.index(i) for i in range(1, k + 1)}
    blocked_by, favorite = {}, {}
    for i in range(1, k + 1):
        h = max(pair, key=lambda g: (utilities[i][g], -g))
        favorite[i] = h
        changed = list(state)
        changed[h], changed[own[i]] = i, 0
        failure = deletion_failure(utilities, changed)
        if failure is None:
            return {"kind": "neighbor", "state": tuple(changed)}
        j = failure['observer']
        assert j not in (0, i) and failure['target'] == 0
        blocked_by[i] = j
    seen, route, i = {}, [], 1
    while i not in seen:
        seen[i] = len(route)
        route.append(i)
        i = blocked_by[i]
    cycle = route[seen[i]:]
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        changed = list(state)
        changed[own[a]], changed[own[b]] = b, a
        if deletion_failure(utilities, changed) is None:
            return {"kind": "neighbor", "state": tuple(changed)}
        assert utilities[a][own[b]] < min(utilities[a][g] for g in pair)
    assert len(cycle) >= 4 and len(cycle) % 2 == 0
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        assert favorite[a] != favorite[b]
        assert utilities[b][own[a]] > utilities[b][own[b]]
    return {"kind": "cycle", "recipients": tuple(cycle),
            "favorite_pair_goods": tuple(favorite[i] for i in cycle)}


def four_multivalued_family(singletons=4):
    """Extend Sorrel's four-agent core with genuinely binary singleton rows.

    Exactly four singleton rows have more than two values, for every k >= 4.
    The original construction already settles k=4; the binary padding is new.
    """
    if type(singletons) is not int or singletons < 4:
        raise ValueError("need at least four singleton recipients")
    k = singletons
    prior, start, target = prior_isolated_family(k + 1)
    rows = [list(row) for row in prior]
    for i in range(1, 5):
        for g in range(4, k):
            rows[i][g] = 3
    for i in range(5, k + 1):
        rows[i] = [int(g in (i - 1, k, k + 1)) for g in range(k + 2)]
    # All comparisons involve one good on each side; make every value positive.
    return tuple(tuple(v + 1 for v in row) for row in rows), start, target


def family_certificate(singletons=4):
    """Check the sharp four-multivalued-row family, including its blocker cycle."""
    utilities, start, target = four_multivalued_family(singletons)
    assert deletion_failure(utilities, start) is None
    assert deletion_failure(utilities, target) is None
    failures = []
    for x, y in combinations(range(len(start)), 2):
        if start[x] == start[y]:
            continue
        changed = list(start)
        changed[x], changed[y] = changed[y], changed[x]
        failure = deletion_failure(utilities, changed)
        assert failure is not None, (x, y)
        failures.append({"goods": (x, y), **failure})
    result = {"status": "isolated_EF1_state", "singletons": singletons,
              "utilities": utilities, "start": start, "other_fair_state": target,
              "multivalued_singleton_rows": sum(len(set(row)) > 2 for row in utilities[1:]),
              "excluded_exchanges": len(failures), "failures": failures}
    structure = fair_neighbor_or_cycle(utilities, start)
    assert structure['kind'] == 'cycle'
    result['alternating_cycle'] = structure
    if singletons == 4:
        mask = fair_mask(utilities[1:])
        parts = components(mask)
        result.update({"full_states": len(STATES), "fair_states": mask.bit_count(),
                       "component_sizes": sorted(p.bit_count() for p in parts),
                       "fair_edges": sum((ADJACENCY[i] & mask).bit_count()
                                         for i in range(len(STATES)) if mask >> i & 1) // 2})
    return result


def check_profiles(profiles):
    """Complete every finite graph; retain the first separating graph if found."""
    started = time.monotonic()
    seen = set()
    sizes = Counter()
    digest = sha256()
    count = 0
    for rows in profiles:
        count += 1
        mask = fair_mask(rows)
        digest.update(mask.to_bytes(45, "little"))
        sizes[mask.bit_count()] += 1
        if mask in seen:
            continue
        seen.add(mask)
        reached = component(mask)
        if not mask or reached != mask:
            parts = components(mask)
            return {"status": "separated" if mask else "empty", "profiles": count,
                    "rows": rows, "component_sizes": [p.bit_count() for p in parts],
                    "endpoints": [STATES[(p & -p).bit_length() - 1] for p in parts],
                    "stream_sha256": digest.hexdigest(),
                    "seconds": round(time.monotonic() - started, 3)}
    return {"status": "all_checked_graphs_connected", "profiles": count,
            "distinct_graphs": len(seen), "states": len(STATES),
            "edges": sum(a.bit_count() for a in ADJACENCY) // 2,
            "vertex_histogram": dict(sorted(sizes.items())),
            "stream_sha256": digest.hexdigest(),
            "seconds": round(time.monotonic() - started, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("witness", "census", "sample"), nargs="?", default="witness")
    parser.add_argument("--singletons", type=int, default=4)
    parser.add_argument("--count", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20261120119)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")
    if args.mode == "witness":
        try:
            result = family_certificate(args.singletons)
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    profiles = census_profiles() if args.mode == "census" else sampled_profiles(args.count, args.seed)
    result = check_profiles(profiles)
    result["domain"] = ("one arbitrary weak order and three binary orders, complete up to relabelling"
                        if args.mode == "census" else f"{args.count} sampled profiles, seed {args.seed}")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
