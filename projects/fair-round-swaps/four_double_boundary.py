"""Complete finite graphs for the next two-exceptional-double boundary.

Samples are explicitly bounded. No sampled connectivity result is a theorem
about all utility profiles. Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
from array import array
from itertools import combinations, product
import json
import math
import random
import time

from swaps import ef1, validate_profile


ESCAPE_MOVES = ((4, 6), (4, 7)) + tuple((a, b) for a in range(4) for b in range(4, 8))


def escape_cover(moves=ESCAPE_MOVES):
    """Exhaust an overapproximation of all real EF1 threshold patterns.

    Slots 0,1 belong to A; 2,3 to B; 4,5 and 6,7 to automatic doubles.
    The three rows are A's total threshold, B's total, and the singleton's.
    A and B own only low goods; every other pair has at most one high good.
    """
    choices = ((0, 0), (1, 0), (0, 1))
    a_rows, b_rows = [], []
    for parts in product(choices, repeat=3):
        a_rows.append((0, 0)+sum(parts, ()))
        b_rows.append(parts[0]+(0, 0)+parts[1]+parts[2])
    checked = 0
    for a, b, parts in product(a_rows, b_rows, product(choices, repeat=4)):
        rows = (a, b, sum(parts, ()))
        for x, y in moves:
            changed_owner = x//2 if x < 4 else None
            if changed_owner is not None and not rows[changed_owner][y]:
                continue  # Only the owner receiving a strict above-total good may be ignored.
            matching = tuple(y if g == x else x if g == y else g for g in range(8))
            if all(i == changed_owner or all(not (row[matching[p]] and row[matching[p+1]])
                                             for p in range(0, 8, 2))
                   for i, row in enumerate(rows)):
                break
        else:
            raise AssertionError(('uncovered threshold pattern', rows))
        checked += 1
    return checked


def fair_neighbor(u, state):
    """Give one fair exchange for any r>=4 in the two-exceptional domain.

    The singleton goods stay fixed. This proves no isolation, not connectivity.
    The universal existence argument is the complete escape_cover check.
    """
    validate_profile(u)
    r, m = len(u)-2, len(u[0])
    state = tuple(state)
    if (r < 4 or m != 2*r+2 or len(state) != m
            or any(type(i) is not int or i not in range(r+2) for i in state)
            or tuple(state.count(i) for i in range(r+2)) != (2,)*r+(1, 1)
            or state[0] not in (r, r+1) or not ef1(u, state)):
        raise ValueError('need a fair protected allocation with at least four doubles')
    if any(row[0] != max(row) for row in u[-2:]):
        raise ValueError('good zero must be a favorite of both carriers')
    for row in u[2:r]:
        values = sorted(row[1:])
        if values[0]+values[1] < values[-2]:
            raise ValueError('remaining doubles must be automatically fair')
    pairs = tuple(tuple(g for g, owner in enumerate(state) if owner == i) for i in range(4))
    goods = sum(pairs, ())
    for x, y in ESCAPE_MOVES:
        if x < 4:
            row = u[x//2]
            if row[goods[y]] <= sum(row[g] for g in pairs[x//2]):
                continue
        following = list(state)
        a, b = goods[x], goods[y]
        following[a], following[b] = following[b], following[a]
        if ef1(u, following):
            return tuple(following)
    raise AssertionError('complete threshold cover supplied no fair neighbor')


class FullGraph:
    """Every fixed-size state, with the shared favorite protected on a carrier."""

    def __init__(self, doubles=4):
        if type(doubles) is not int or doubles not in (2, 3, 4):
            raise ValueError("the complete checker supports two through four doubles")
        self.r, self.m = doubles, 2*doubles+2
        states = []

        def allocate(agent, remaining, owners):
            if agent == self.r:
                states.append(tuple(owners))
                return
            for pair in combinations(remaining, 2):
                following = owners[:]
                for good in pair:
                    following[good] = agent
                allocate(agent+1, tuple(g for g in remaining if g not in pair), following)

        for holder in (self.r, self.r+1):
            for singleton in range(1, self.m):
                owners = [-1]*self.m
                owners[0], owners[singleton] = holder, 2*self.r+1-holder
                allocate(0, tuple(g for g in range(1, self.m) if g != singleton), owners)
        self.states = tuple(sorted(states))
        index = {state: k for k, state in enumerate(self.states)}
        self.pairs = tuple(combinations(range(1, self.m), 2))
        pair_index = {pair: k for k, pair in enumerate(self.pairs)}
        self.bundles = []
        self.singletons = []
        self.adjacency = []
        for state in self.states:
            self.bundles.append(tuple(pair_index[tuple(g for g, owner in enumerate(state) if owner == i)]
                                      for i in range(self.r)))
            active = 2*self.r+1-state[0]
            self.singletons.append((active, state.index(active)))
            adjacent = array('I')
            for a, b in combinations(range(self.m), 2):
                if state[a] == state[b] or (a == 0 and state[b] < self.r):
                    continue
                following = list(state)
                following[a], following[b] = following[b], following[a]
                adjacent.append(index[tuple(following)])
            self.adjacency.append(adjacent)

    def fair_vertices(self, u):
        validate_profile(u)
        if len(u) != self.r+2 or len(u[0]) != self.m:
            raise ValueError("profile does not match the graph")
        if any(row[0] != max(row) for row in u[-2:]):
            raise ValueError("good zero must be a favorite of both carriers")
        for row in u[2:self.r]:
            values = sorted(row[1:])
            if values[0]+values[1] < values[-2]:
                raise ValueError("remaining doubles must be automatically fair")
        minimum = [[min(row[a], row[b]) for a, b in self.pairs] for row in u]
        totals = [[row[a]+row[b] for a, b in self.pairs] for row in u[:2]]
        allowed = set()
        for k, pairs in enumerate(self.bundles):
            if any(any(minimum[i][p] > totals[i][pairs[i]] for p in pairs) for i in (0, 1)):
                continue
            active, good = self.singletons[k]
            if all(minimum[active][p] <= u[active][good] for p in pairs):
                allowed.add(k)
        return allowed

    def components(self, allowed):
        unseen, result = set(allowed), []
        while unseen:
            first = min(unseen)
            unseen.remove(first)
            queue = [first]
            for vertex in queue:
                for other in self.adjacency[vertex]:
                    if other in unseen:
                        unseen.remove(other)
                        queue.append(other)
            result.append(queue)
        return result

    def certificate(self, u):
        fair = self.fair_vertices(u)
        if not fair:
            raise AssertionError("serial anchors and a favorite singleton give a fair state")
        groups = self.components(fair)
        sides = [self.components(k for k in fair if self.states[k][0] == holder)
                 for holder in (self.r, self.r+1)]
        result = {'fair_states': len(fair), 'components': sorted(map(len, groups)),
                  'owner_components': [sorted(map(len, side)) for side in sides]}
        if len(groups) > 1:
            result['separated_endpoints'] = [self.states[group[0]] for group in groups[:2]]
        elif any(len(side) > 1 for side in sides):
            side = next(side for side in sides if len(side) > 1)
            result['owner_separated_endpoints'] = [self.states[group[0]] for group in side[:2]]
        return result


def profiles(doubles, seed, count):
    """A fixed mixture of integer, skewed and positive strict profiles."""
    if type(count) is not int or count < 0:
        raise ValueError("sample count must be nonnegative")
    rng = random.Random(seed)
    m = 2*doubles+2
    for sample in range(count):
        mode = sample % 3
        rows = []
        for i in (0, 1):
            values = [rng.choice((0, 0, 1, 2, 8, 64)) if mode == 1 else rng.randrange(8)
                      for _ in range(m-1)]
            if mode == 2:
                ranks = rng.sample(range(1, m), m-1)
                values = [100*v+rank for v, rank in zip(values, ranks)]
            if i == 0:
                values.sort()
            rows.append((0,)+tuple(values))
        rows.extend((0,)+(1,)*(m-1) for _ in range(doubles-2))
        for _ in (0, 1):
            values = (rng.sample(range(1, m), m-1) if mode else
                      [rng.randrange(8) for _ in range(m-1)])
            rows.append((max(m, 8),)+tuple(values))
        yield tuple(rows)


def search(graph, seed, count, seconds):
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("time budget must be positive and finite")
    started = time.monotonic()
    result = {'all_states': len(graph.states), 'degree': len(graph.adjacency[0]),
              'seed': seed, 'requested_profiles': count, 'seconds_limit': seconds,
              'checked': 0, 'largest_fair_graph': 0, 'full_separations': 0,
              'owner_separations': 0, 'stop': 'all requested profiles',
              'scope': 'only completed sampled profiles; every graph traversal is complete'}
    for u in profiles(graph.r, seed, count):
        if time.monotonic()-started >= seconds:
            result['stop'] = 'time limit between profiles'
            break
        checked = graph.certificate(u)
        result['checked'] += 1
        result['largest_fair_graph'] = max(result['largest_fair_graph'], checked['fair_states'])
        if 'owner_separated_endpoints' in checked:
            result['owner_separations'] += 1
            if 'first_owner_separation' not in result:
                result['first_owner_separation'] = {'utilities': u, 'certificate': checked}
        if 'separated_endpoints' in checked:
            result['full_separations'] += 1
            result['utilities'], result['certificate'] = u, checked
            result['stop'] = 'full separating witness'
            break
    result['elapsed_seconds'] = time.monotonic()-started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=int, default=100)
    parser.add_argument('--seed', type=int, default=2026112074)
    parser.add_argument('--seconds', type=float, default=900)
    parser.add_argument('--escape-cover', action='store_true',
                        help='verify the complete ordinal no-isolation proof')
    args = parser.parse_args()
    if args.samples < 0 or not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('need nonnegative samples and a positive finite time budget')
    if args.escape_cover:
        print(json.dumps({'threshold_patterns': escape_cover(), 'candidate_exchanges': 18,
                          'scope': 'no isolated state for r>=4; not a connectivity theorem'}))
        return
    started = time.monotonic()
    graph = FullGraph()
    build_seconds = time.monotonic()-started
    result = search(graph, args.seed, args.samples, args.seconds)
    result['build_seconds'] = build_seconds
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
