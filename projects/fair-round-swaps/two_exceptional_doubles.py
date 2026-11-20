"""Exact protected graphs, two-value paths and a favorite-singleton construction."""

from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import random

from swaps import ef1, exchange, validate_profile


DONOR_FAILURE = ((0, 100, 1, 1, 0, 0), (0, 100, 0, 10, 0, 0),
                 (10, 0, 0, 0, 0, 0), (10, 2, 2, 0, 0, 1))
DONOR_PATH = ((2, 1, 0, 0, 1, 3), (2, 1, 0, 1, 0, 3), (2, 0, 1, 1, 0, 3))


class Graph:
    """Every protected fixed-size allocation for two or three double recipients."""

    def __init__(self, r: int):
        if type(r) is not int or r not in (2, 3):
            raise ValueError("bounded checker supports two or three double recipients")
        self.r, self.n, self.m = r, r+2, 2*r+2
        states = []

        def assign(agent, remaining, state):
            if agent == r:
                states.append(tuple(state))
                return
            for pair in combinations(remaining, 2):
                next_state = state[:]
                for g in pair:
                    next_state[g] = agent
                assign(agent+1, tuple(g for g in remaining if g not in pair), next_state)

        for holder in (r, r+1):
            for singleton in range(1, self.m):
                state = [-1]*self.m
                state[0], state[singleton] = holder, 2*r+1-holder
                assign(0, tuple(g for g in range(1, self.m) if g != singleton), state)
        self.states = tuple(sorted(states))
        self.index = {state: i for i, state in enumerate(self.states)}
        self.bundles = tuple(tuple(tuple(g for g, owner in enumerate(s) if owner == i)
                                   for i in range(self.n)) for s in self.states)
        self.adjacency = []
        for state in self.states:
            edges = 0
            for a, b in combinations(range(self.m), 2):
                if state[a] == state[b] or (a == 0 and state[b] < r):
                    continue
                next_state = list(state)
                next_state[a], next_state[b] = next_state[b], next_state[a]
                edges |= 1 << self.index[tuple(next_state)]
            self.adjacency.append(edges)

    @lru_cache(maxsize=20000)
    def observer_mask(self, observer: int, row: tuple) -> int:
        """An exact EF1 row predicate over all states, with singleton targets deleted."""
        mask = 0
        for k, bundles in enumerate(self.bundles):
            own = sum(row[g] for g in bundles[observer])
            if all(own >= min(row[g] for g in bundles[j]) for j in range(self.r)):
                mask |= 1 << k
        return mask

    def fair_mask(self, u: tuple) -> int:
        validate_profile(u)
        if len(u) != self.n or len(u[0]) != self.m:
            raise ValueError("profile does not match this graph")
        if any(row[0] != max(row) for row in u[-2:]):
            raise ValueError("good zero must be a favorite of both singleton carriers")
        for i in range(2, self.r):
            ordered = sorted(u[i][1:])
            if ordered[0]+ordered[1] < ordered[-2]:
                raise ValueError("all but the first two doubles must be automatically fair")
        mask = (1 << len(self.states))-1
        for i in (0, 1, self.r, self.r+1):
            mask &= self.observer_mask(i, u[i])
        return mask

    @lru_cache(maxsize=20000)
    def components(self, fair: int) -> tuple[int, ...]:
        todo, groups = fair, []
        while todo:
            frontier = todo & -todo
            reached = frontier
            todo ^= frontier
            while frontier:
                bit = frontier & -frontier
                frontier ^= bit
                fresh = self.adjacency[bit.bit_length()-1] & todo
                todo ^= fresh
                reached |= fresh
                frontier |= fresh
            groups.append(reached)
        return tuple(groups)

    def certificate(self, u: tuple) -> dict:
        fair = self.fair_mask(u)
        if not fair:
            raise AssertionError("valid shared-favorite domain unexpectedly has no fair state")
        groups = self.components(fair)
        result = {"all_states": len(self.states), "fair_states": fair.bit_count(),
                  "component_sizes": sorted(g.bit_count() for g in groups)}
        if len(groups) > 1:
            result["separated_endpoints"] = [
                self.states[(g & -g).bit_length()-1] for g in groups[:2]]
        return result


def _nonautomatic(row):
    values = sorted(row[1:])
    return values[0]+values[1] < values[-2]


def binary_profiles(r=2, first_ones=None):
    """Binary profiles needing two exceptions, up to non-g relabeling.

    The first double's high set can be the first 2 through 2r-1 non-g goods.
    All choices of the other three rows are retained, including tied carriers.
    Values on g for the doubles have no effect, so they are normalized to zero.
    """
    if r not in (2, 3) or (first_ones is not None and first_ones not in range(2, 2*r)):
        raise ValueError("invalid binary slice")
    length = 2*r+1
    rows = tuple((0,)+bits for bits in product((0, 1), repeat=length))
    exceptional = tuple(row for row in rows if _nonautomatic(row))
    carrier = tuple((1,)+row[1:] for row in rows)
    for count in range(2, 2*r) if first_ones is None else (first_ones,):
        first = (0,) + (1,)*count + (0,)*(length-count)
        for second in exceptional:
            for left in carrier:
                for right in carrier:
                    yield (first, second) + ((0,)+(1,)*length,)*(r-2) + (left, right)


def two_level_orbits(r=3):
    """Every four-binary-row column multiset, including automatic boundaries."""
    if r not in (2, 3):
        raise ValueError("need two or three double recipients")
    length = 2*r+1
    for columns in combinations_with_replacement(range(16), length):
        rows = tuple((int(i >= 2),)+tuple((column >> i) & 1 for column in columns)
                     for i in range(4))
        yield rows[:2] + ((0,)+(1,)*length,)*(r-2) + rows[2:]


def two_level_representative(u):
    """Preserve the full protected graph; low/high values need not be 0/1."""
    validate_profile(u)
    r = len(u)-2
    if r not in (2, 3) or len(u[0]) != 2*r+2:
        raise ValueError("need two or three doubles and two singleton carriers")
    if any(row[0] < max(row) for row in u[-2:]):
        raise ValueError("good zero must be a favorite of both carriers")
    result = []
    for i, row in enumerate(u):
        if 2 <= i < r:
            values = sorted(row[1:])
            if values[0]+values[1] < values[-2]:
                raise ValueError("the third double must be automatically fair")
            result.append((0,)+(1,)*(2*r+1))
            continue
        levels = sorted(set(row[1:]))
        if len(levels) > 2:
            raise ValueError("each exceptional double and carrier needs at most two non-g values")
        if i < r and (len(levels) == 1 or levels[-1] <= 2*levels[0]):
            result.append((0,)+(0,)*(2*r+1))
        else:
            result.append((int(i >= r),)+tuple(int(len(levels) == 2 and v == levels[-1])
                                              for v in row[1:]))
    return tuple(result)


def connect_two_level(u, start, target):
    """Search the entire finite graph for the stated two-level input class."""
    converted = two_level_representative(u)
    graph = Graph(len(u)-2)
    fair = graph.fair_mask(converted)
    start, target = tuple(start), tuple(target)
    if (start not in graph.index or target not in graph.index
            or not fair & (1 << graph.index[start]) or not fair & (1 << graph.index[target])):
        raise ValueError("endpoints must be fair protected allocations of the prescribed sizes")
    if start[0] == target[0]:
        fair &= sum(1 << k for k, state in enumerate(graph.states) if state[0] == start[0])
    source, goal = graph.index[start], graph.index[target]
    previous, queue = {source: None}, deque([source])
    while queue:
        a = queue.popleft()
        if a == goal:
            indices = [a]
            while previous[indices[-1]] is not None:
                indices.append(previous[indices[-1]])
            route = [graph.states[k] for k in reversed(indices)]
            if (not all(ef1(u, state) for state in route)
                    or not all(exchange(a, b) for a, b in zip(route, route[1:]))):
                raise AssertionError("binary reduction did not preserve the original path")
            return route
        neighbors = graph.adjacency[a] & fair
        while neighbors:
            bit = neighbors & -neighbors
            neighbors ^= bit
            b = bit.bit_length()-1
            if b not in previous:
                previous[b] = a
                queue.append(b)
    raise AssertionError("the complete two-level graph separated these fair endpoints")


def favorite_singleton_path(u, start, target):
    """Connect arbitrary real-valued endpoints with the same favorite singleton.

    Good zero stays with one carrier; the other keeps its favorite nonzero good.
    The first two doubles are unrestricted and every other double is automatic.
    This constructive subcase permits any number of double recipients >= 2.
    """
    validate_profile(u)
    r, m = len(u)-2, len(u[0])
    start, target = tuple(start), tuple(target)
    if r < 2 or m != 2*r+2:
        raise ValueError("need at least two doubles and two singleton carriers")
    if any(row[0] != max(row) for row in u[-2:]):
        raise ValueError("good zero must be a favorite of both singleton carriers")
    for row in u[2:r]:
        ordered = sorted(row[1:])
        if ordered[0]+ordered[1] < ordered[-2]:
            raise ValueError("other doubles must be automatically fair")
    for state in (start, target):
        if (len(state) != m or any(type(i) is not int or i not in range(r+2) for i in state)
                or tuple(state.count(i) for i in range(r+2)) != (2,)*r+(1, 1)
                or state[0] not in (r, r+1) or not ef1(u, state)):
            raise ValueError("endpoints must be fair protected allocations")
    holder, active = start[0], 2*r+1-start[0]
    h = start.index(active)
    if target[0] != holder or target[h] != active or u[active][h] != max(u[active][1:]):
        raise ValueError("endpoints must keep the same favorite nonzero singleton")
    goods = tuple(g for g in range(1, m) if g != h)
    w = max(goods, key=lambda g: (u[0][g], -g))
    z = max((g for g in goods if g != w), key=lambda g: (u[1][g], -g))

    def normalize(initial):
        route = [initial]

        def move(x, y):
            state = list(route[-1])
            state[x], state[y] = state[y], state[x]
            route.append(tuple(state))

        state = route[-1]
        if state[w] != 0:
            a = [g for g in goods if state[g] == 0]
            if state[w] == 1:
                x = max(a, key=lambda g: (u[1][g], -g))
                v = next(g for g in goods if state[g] == 1 and g != w)
                buffers = [[g for g in goods if state[g] == i] for i in range(2, r)]
                if buffers:
                    pair = max(buffers, key=lambda pair: min(u[1][g] for g in pair))
                    if u[1][x]+u[1][v] < min(u[1][g] for g in pair):
                        own = sum(u[0][g] for g in a)
                        p = next(g for g in pair if u[0][g] <= own)
                        move(v, p)
                move(w, x)
            else:
                own = sum(u[1][g] for g in goods if state[g] == 1)
                high = [g for g in a if u[1][g] > own]
                x = high[0] if u[1][w] > own and high else next(
                    g for g in a if u[1][w] > own or u[1][g] <= own)
                move(w, x)
        if route[-1][z] != 1:
            move(z, next(g for g in goods if route[-1][g] == 1))
        return route

    left, right = normalize(start), normalize(target)
    route = left[:]
    # Fix ordinary pairs, then A's tail. B's one remaining tail is forced.
    for agent in (*range(2, r), 0):
        for g in goods:
            if right[-1][g] == agent and route[-1][g] != agent:
                spare = next(t for t in goods if route[-1][t] == agent
                             and right[-1][t] != agent)
                state = list(route[-1])
                state[g], state[spare] = state[spare], state[g]
                route.append(tuple(state))
    route.extend(reversed(right[:-1]))
    if (route[-1] != target or len(route)-1 > 2*r+3
            or any(a[0] != holder or a[h] != active or not ef1(u, a) for a in route)
            or any(not exchange(a, b) for a, b in zip(route, route[1:]))):
        raise AssertionError("favorite-singleton normalization failed")
    return route


def separation_query(*, bounded_integers=False, favorite_attachment=False):
    """Full eight-good cut, or one owner side with a normalized favorite root."""
    graph = Graph(3)
    included = {k for k, state in enumerate(graph.states)
                if not favorite_attachment or state[0] == 3}
    lines = ['(set-logic QF_LIA)' if bounded_integers else '(set-logic QF_LRA)']
    gauge = '<=' if favorite_attachment else '='  # The new query includes zero rows.
    for i in (0, 1, 3, 4):
        for g in range(8):
            sort = 'Int' if bounded_integers else 'Real'
            lower = 1 if bounded_integers and not (i < 2 and g == 0) else 0
            lines += [f'(declare-fun u{i}_{g} () {sort})', f'(assert (>= u{i}_{g} {lower}))']
            if bounded_integers:
                lines.append(f'(assert (<= u{i}_{g} 256))')
        if i < 2:
            lines.append(f'(assert (= u{i}_0 0))')
            if not bounded_integers:
                lines.append(f'(assert ({gauge} (+ {" ".join(f"u{i}_{g}" for g in range(1, 8))}) 1))')
        else:
            if not bounded_integers:
                lines.append(f'(assert ({gauge} (+ {" ".join(f"u{i}_{g}" for g in range(8))}) 1))')
            lines += [f'(assert (>= u{i}_0 u{i}_{g}))' for g in range(1, 8)]
    if favorite_attachment:
        # Relabel a favorite singleton to 1, then serial anchors to 2 and 4.
        # These anchor comparisons concern the initial favorite fiber only.
        lines += [f'(assert (>= u4_1 u4_{g}))' for g in range(2, 8)]
        lines += [f'(assert (>= u0_2 u0_{g}))' for g in range(2, 8)]
        lines += [f'(assert (>= u1_4 u1_{g}))' for g in range(3, 8)]
    # The third double is identically zero and therefore always fair.
    for k, state in enumerate(graph.states):
        if k not in included:
            continue
        lines += [f'(declare-fun f{k} () Bool)', f'(declare-fun r{k} () Bool)']
        terms = []
        for i in (0, 1, 3, 4):
            if state[0] == i:
                continue  # Its favorite makes this singleton observer safe.
            own = f'(+ {" ".join(f"u{i}_{g}" for g in graph.bundles[k][i])})'
            for j in range(3):
                if i != j:
                    terms.append(f'(or {" ".join(f"(>= {own} u{i}_{g})" for g in graph.bundles[k][j])})')
        lines.append(f'(assert (= f{k} (and {" ".join(terms)})))')
    for k, adjacent in enumerate(graph.adjacency):
        if k not in included:
            continue
        for j in range(k):
            if j in included and adjacent & (1 << j):
                lines.append(f'(assert (=> (and f{k} f{j}) (= r{k} r{j})))')
    root = graph.index[(3, 4, 0, 0, 1, 1, 2, 2)] if favorite_attachment else graph.index[(3, 0, 0, 1, 1, 2, 2, 4)]
    lines += [f'(assert f{root})', f'(assert r{root})',
              f'(assert (or {" ".join(f"(and f{k} (not r{k}))" for k in sorted(included))}))',
              '(check-sat)']
    return '\n'.join(lines)+'\n'


def sampled_profiles(r: int, seed: int, count: int, levels: int, spiky=False):
    """A deterministic finite search, not coverage of all cardinal valuations."""
    if type(count) is not int or count < 0 or levels < 2:
        raise ValueError("need nonnegative samples and at least two utility levels")
    rng = random.Random(seed)
    m = 2*r+2
    for _ in range(count):
        special = []
        for i in range(2):
            values = [rng.choice((0, 0, 1, 2, 8, 64)) if spiky else rng.randrange(levels)
                      for _ in range(m-1)]
            if i == 0:
                values.sort()  # simultaneous non-g relabeling symmetry
            special.append((0,)+tuple(values))
        ordinary = ((0,)+(levels,)*(m-1),)*(r-2)
        carriers = tuple((m,)+tuple(rng.sample(range(1, m), m-1)) if spiky else
                         (levels,)+tuple(rng.randrange(levels) for _ in range(m-1))
                         for _ in range(2))
        yield tuple(special) + ordinary + carriers


def search(graph: Graph, profiles, *, fixed_owners=False) -> dict:
    checked, largest = 0, 0
    sides = [sum(1 << k for k, a in enumerate(graph.states) if a[0] == holder)
             for holder in (graph.r, graph.r+1)] if fixed_owners else []
    for u in profiles:
        result = graph.certificate(u)
        checked += 1
        largest = max(largest, result["fair_states"])
        if len(result["component_sizes"]) > 1:
            return {"checked": checked, "separated": True, "utilities": u,
                    "certificate": result}
        for side in sides:
            groups = graph.components(graph.fair_mask(u) & side)
            if len(groups) > 1:
                return {"checked": checked, "separated": False, "fixed_owner_separated": True,
                        "utilities": u, "component_sizes": [g.bit_count() for g in groups]}
    result = {"checked": checked, "separated": False, "largest_fair_graph": largest,
              "scope": "only the explicitly generated finite profiles"}
    if fixed_owners:
        result["fixed_owner_separated"] = False
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", action="store_true", help="all 40960 reduced six-good profiles")
    parser.add_argument("--binary-eight", action="store_true", help="an exhaustive eight-good binary slice")
    parser.add_argument("--first-ones", type=int, help="fix the first double's binary high-set size")
    parser.add_argument("--pairs", type=int, choices=(2, 3), default=3)
    parser.add_argument("--seed", type=int, default=20261120)
    parser.add_argument("--samples", type=int, default=10000)
    parser.add_argument("--levels", type=int, default=4)
    parser.add_argument("--spiky", action="store_true",
                        help="special values in 0,0,1,2,8,64; strict carrier orders")
    parser.add_argument("--example", action="store_true", help="the failed direct-acquisition rule")
    parser.add_argument("--two-level", action="store_true", help="all binary representative classes")
    parser.add_argument("--two-level-input", help="JSON matrix of integers or rational strings")
    parser.add_argument("--start", help="comma-separated owner vector for --two-level-input")
    parser.add_argument("--target", help="comma-separated owner vector for --two-level-input")
    parser.add_argument("--write-separation-query", type=Path,
                        help="write the full real-linear cut query; no solver verdict implied")
    parser.add_argument("--integer-cut", action="store_true",
                        help="use the complete positive integer domain 1..256 in the cut query")
    parser.add_argument("--favorite-attachment", action="store_true",
                        help="one complete owner side with a normalized favorite-singleton root")
    args = parser.parse_args()
    if args.integer_cut and not args.write_separation_query:
        parser.error("--integer-cut requires --write-separation-query")
    if args.favorite_attachment and not args.write_separation_query:
        parser.error("--favorite-attachment requires --write-separation-query")
    if args.write_separation_query:
        text = separation_query(bounded_integers=args.integer_cut,
                                favorite_attachment=args.favorite_attachment)
        args.write_separation_query.write_text(text)
        scope = 'unverified full-owner-side attachment input' if args.favorite_attachment else 'unverified full-graph solver input'
        print(json.dumps({'bytes': len(text.encode()), 'scope': scope}))
        return
    if ((args.two_level or args.two_level_input)
            and (args.binary or args.binary_eight or args.example)
            or args.two_level and args.two_level_input):
        parser.error("choose one graph input mode")
    if (args.start or args.target) and not args.two_level_input:
        parser.error("--start and --target require --two-level-input")
    if args.two_level_input:
        with open(args.two_level_input) as stream:
            data = json.load(stream)
        if (not isinstance(data, list) or not all(isinstance(row, list) for row in data)
                or any(type(v) not in (int, str) for row in data for v in row)):
            parser.error("expected a matrix of integers or rational strings")
        u = tuple(tuple(Fraction(v) for v in row) for row in data)
        converted = two_level_representative(u)
        result = {"binary_representative": converted,
                  "complete_graph": Graph(len(u)-2).certificate(converted)}
        if bool(args.start) != bool(args.target):
            parser.error("provide both --start and --target")
        if args.start:
            result["path"] = connect_two_level(u, tuple(map(int, args.start.split(','))),
                                                tuple(map(int, args.target.split(','))))
        print(json.dumps(result))
        return
    if args.two_level:
        graph = Graph(args.pairs)
        result = search(graph, two_level_orbits(args.pairs), fixed_owners=True)
        result["scope"] = "all column-permutation orbits of the stated two-level class"
        print(json.dumps(result))
        return
    if args.binary and args.binary_eight:
        parser.error("choose one binary domain")
    if args.first_ones is not None and not (args.binary or args.binary_eight):
        parser.error("--first-ones requires a binary domain")
    if args.example:
        graph = Graph(2)
        fair = graph.fair_mask(DONOR_FAILURE)
        blocked = []
        for other in (2, 3):
            candidate = list(DONOR_PATH[0])
            candidate[1], candidate[other] = candidate[other], candidate[1]
            candidate = tuple(candidate)
            blocked.append({"swap": [1, other], "state": candidate,
                            "fair": bool(fair & (1 << graph.index[candidate]))})
        result = {"utilities": DONOR_FAILURE, "direct_attempts": blocked,
                  "repair": DONOR_PATH, "complete_graph": graph.certificate(DONOR_FAILURE),
                  "scope": "failed direct rule, not a separating counterexample"}
        print(json.dumps(result, indent=2))
        return
    binary = args.binary or args.binary_eight
    graph = Graph(2 if args.binary else 3 if args.binary_eight else args.pairs)
    profiles = binary_profiles(graph.r, args.first_ones) if binary else sampled_profiles(
        args.pairs, args.seed, args.samples, args.levels, args.spiky)
    result = search(graph, profiles)
    result.update({"pairs": graph.r, "all_states": len(graph.states),
                   "seed": None if binary else args.seed,
                   "levels": 2 if binary else args.levels,
                   "first_ones": args.first_ones if binary else None,
                   "spiky": args.spiky and not binary})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
