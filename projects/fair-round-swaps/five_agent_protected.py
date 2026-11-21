"""A common protected crossing and an exact obstruction to freezing two anchors.

This does not assert connectivity of arbitrary protected EF1 states. The SMT
export is a research question over all nonnegative real braid valuations;
running its exporter is not a mathematical acceptance of a solver's answer.
"""

from __future__ import annotations

import argparse
from collections import deque
from itertools import combinations
import json

from swaps import (Allocation, Profile, components, ef1, exchange,
                   states_with_sizes, validate_profile)


BOUNDARY: Profile = (
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 3, 3, 3, 1, 0, 2, 0),
    (3, 3, 3, 0, 3, 1, 1, 2),
    (3, 3, 3, 0, 1, 3, 1, 2),
)
START: Allocation = (3, 0, 1, 2, 0, 4, 1, 2)
TARGET: Allocation = (4, 0, 1, 2, 3, 0, 1, 2)


def common_crossing(u: Profile, g: int, carriers: tuple[int, int]
                    ) -> tuple[Allocation, Allocation]:
    """Construct a fair exchange of g between the two singleton carriers.

    The other n-2 agents each receive two goods, one from each of two
    categories picked in opposite orders. This supplies a crossing, not
    paths to that crossing from particular endpoints.
    """
    validate_profile(u)
    n, m = len(u), len(u[0])
    if (n < 3 or m != 2 * n - 2 or len(carriers) != 2 or len(set(carriers)) != 2
            or any(i not in range(n) for i in carriers) or g not in range(m)):
        raise ValueError("need two distinct singleton carriers and 2n-2 goods")
    i, j = carriers
    if any(u[k][g] != max(u[k]) for k in carriers):
        raise ValueError("g must be a global favorite for both carriers")
    r = n - 2
    goods = set(range(m)) - {g}
    top = [set(sorted(goods, key=lambda h: (-u[k][h], h))[:r + 1]) for k in carriers]
    t = min(top[0] & top[1])
    while True:
        better = [h for h in sorted(goods) if u[i][h] > u[i][t] and u[j][h] > u[j][t]]
        if not better:
            break
        t = better[0]
    high_i = {h for h in goods if u[i][h] > u[i][t]}
    high_j = {h for h in goods if u[j][h] > u[j][t]}
    if high_i & high_j or len(high_i) > r or len(high_j) > r:
        raise AssertionError("common pivot construction failed")
    first = set(high_i)
    for h in sorted(goods - {t} - high_i - high_j):
        if len(first) == r:
            break
        first.add(h)
    second = goods - {t} - first
    doubles = [k for k in range(n) if k not in carriers]
    state = [-1] * m
    state[g], state[t] = i, j
    for category, order in ((first, doubles), (second, doubles[::-1])):
        pool = set(category)
        for k in order:
            h = max(sorted(pool), key=lambda h: u[k][h])
            state[h] = k
            pool.remove(h)
    a = tuple(state)
    state[g], state[t] = j, i
    b = tuple(state)
    if not ef1(u, a) or not ef1(u, b) or not exchange(a, b):
        raise AssertionError("invalid common protected crossing")
    return a, b


def protected_path(u: Profile, start: Allocation, target: Allocation,
                   fixed: tuple[int, ...] = ()) -> list[Allocation] | None:
    """Exact search for this five-agent size case; None means no such path.

    g=0 stays with singleton 3 or 4. Goods in fixed retain their start
    owners. Intermediate states include non-picking allocations.
    """
    validate_profile(u)
    sizes = (2, 2, 2, 1, 1)
    if len(u) != 5 or len(u[0]) != 8 or any(g not in range(8) for g in fixed):
        raise ValueError("this search requires five agents and eight goods")
    def allowed(a: Allocation) -> bool:
        return (len(a) == 8 and tuple(a.count(i) for i in range(5)) == sizes
                and a[0] in (3, 4) and all(a[g] == start[g] for g in fixed))
    if not all(allowed(a) and ef1(u, a) for a in (start, target)):
        raise ValueError("endpoints must be fair and satisfy the restrictions")
    previous: dict[Allocation, Allocation | None] = {start: None}
    queue = deque([start])
    while queue:
        a = queue.popleft()
        if a == target:
            route = [a]
            while previous[route[-1]] is not None:
                route.append(previous[route[-1]])
            return route[::-1]
        for x, y in combinations(range(8), 2):
            if a[x] == a[y] or x in fixed or y in fixed:
                continue
            b = list(a)
            b[x], b[y] = b[y], b[x]
            b = tuple(b)
            if b not in previous and allowed(b) and ef1(u, b):
                previous[b] = a
                queue.append(b)
    return None


def boundary_counts() -> dict:
    states = states_with_sizes((2, 2, 2, 1, 1))
    fair = tuple(a for a in states if ef1(BOUNDARY, a))
    protected = tuple(a for a in fair if a[0] in (3, 4))
    fixed = tuple(a for a in protected if a[1] == 0 and a[2] == 1)
    route = protected_path(BOUNDARY, START, TARGET, (1,))
    if route is None:
        raise AssertionError("the recorded four-exchange route disappeared")
    return {"full_ef1": len(fair), "full_components": sorted(map(len, components(fair))),
            "protected_ef1": len(protected),
            "protected_components": sorted(map(len, components(protected))),
            "two_fixed_ef1": len(fixed),
            "two_fixed_components": sorted(map(len, components(fixed))),
            "route_fixing_only_first_anchor": ["".join(map(str, a)) for a in route],
            "two_fixed_path": protected_path(BOUNDARY, START, TARGET, (1, 2))}


def separation_formula(fixed: tuple[int, ...] = ()) -> str:
    """Export QF_LRA: satisfiable iff a canonical protected braid separates.

    No utility discretization or normalization. A Boolean labels the sides
    of a cut; every fair exchange edge must have equal labels at its ends.
    This exporter alone does not certify any solver's result.
    """
    if any(g not in (1, 2, 3) for g in fixed):
        raise ValueError("only canonical double anchors can be fixed")
    states = [a for a in states_with_sizes((2, 2, 2, 1, 1))
              if a[0] in (3, 4) and all(a[g] == START[g] for g in fixed)]
    index = {a: k for k, a in enumerate(states)}
    lines = ["; SAT means a separating valuation; UNSAT is a solver result to audit.",
             "; No fixed anchors" if not fixed else f"; Fixed anchors: {fixed}",
             "(set-logic QF_LRA)"]
    def v(i: int, g: int) -> str:
        return f"u{i}_{g}"
    for i in range(5):
        for g in range(8):
            lines.extend((f"(declare-const {v(i, g)} Real)", f"(assert (>= {v(i, g)} 0))"))
    for i, anchor in enumerate((1, 2, 3)):
        lines.extend(f"(assert (>= {v(i, anchor)} {v(i, h)}))" for h in range(anchor + 1, 8))
    for i, best in ((3, 4), (4, 5)):
        lines.extend(f"(assert (>= {v(i, 0)} {v(i, h)}))" for h in range(1, 8))
        lines.extend(f"(assert (>= {v(i, best)} {v(i, h)}))" for h in (4, 5, 6, 7))
    for k, a in enumerate(states):
        clauses = []
        for i in range(5):
            own = "(+ " + " ".join(v(i, g) for g in range(8) if a[g] == i) + ")"
            for j in range(3):
                if i == j:
                    continue
                p, q = (g for g in range(8) if a[g] == j)
                clauses.append(f"(or (>= {own} {v(i, p)}) (>= {own} {v(i, q)}))")
        lines.extend((f"(declare-const r{k} Bool)",
                      f"(define-fun f{k} () Bool (and {' '.join(clauses)}))"))
    for k, a in enumerate(states):
        for x, y in combinations(range(8), 2):
            if a[x] == a[y]:
                continue
            b = list(a)
            b[x], b[y] = b[y], b[x]
            j = index.get(tuple(b))
            if j is not None and j > k:
                lines.append(f"(assert (=> (and f{k} f{j}) (= r{k} r{j})))")
    left, right = index[START], index[TARGET]
    lines.extend((f"(assert (and f{left} f{right} r{left} (not r{right})))",
                  "(check-sat)", ""))
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smt", action="store_true", help="export the unresolved real-valued cut question")
    parser.add_argument("--fix-two", action="store_true", help="also freeze the first two double anchors")
    args = parser.parse_args()
    if args.smt:
        print(separation_formula((1, 2) if args.fix_two else ()), end="")
    else:
        print(json.dumps(boundary_counts(), indent=2))
