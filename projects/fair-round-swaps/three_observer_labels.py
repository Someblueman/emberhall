"""Exact labelled lifts of unlabelled pairing components; standard library only.

See THREE_OBSERVER_LABELS.md. Goods are indices into ``marks``; each set bit
means that observer values the good above its fixed threshold. A state lists
one unordered pair per *fixed recipient*. The algorithm enumerates unlabelled
pairings, not their factorially many assignments to recipients. It is exact,
but its worst-case cost is still exponential in the number of goods.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import factorial, prod

Pair = tuple[int, int]
Pairing = tuple[Pair, ...]
Swap = tuple[int, int]


def validate(marks: tuple[int, ...], state: Pairing) -> Pairing:
    if len(marks) % 2 or any(type(x) is not int or x < 0 for x in marks):
        raise ValueError("marks must be an even-length sequence of nonnegative integers")
    if (len(state) * 2 != len(marks) or any(len(p) != 2 for p in state)
            or any(type(g) is not int for p in state for g in p)
            or sorted(g for p in state for g in p) != list(range(len(marks)))):
        raise ValueError("each good must occur in exactly one pair")
    if any(marks[a] & marks[b] for a, b in state):
        raise ValueError("a pair exceeds a fixed observer threshold")
    return tuple(tuple(sorted(p)) for p in state)


def unlabelled(state: Pairing) -> Pairing:
    return tuple(sorted(state))


def swap_goods(state: Pairing, move: Swap) -> Pairing:
    a, b = move
    i = next(i for i, p in enumerate(state) if a in p)
    j = next(i for i, p in enumerate(state) if b in p)
    if i == j:
        raise ValueError("a move must exchange goods belonging to different recipients")
    out = list(state)
    out[i] = tuple(sorted(b if g == a else g for g in state[i]))
    out[j] = tuple(sorted(a if g == b else g for g in state[j]))
    return tuple(out)


def _switches(marks: tuple[int, ...], state: Pairing):
    for i, j in combinations(range(len(state)), 2):
        a, b = state[i]
        c, d = state[j]
        for x, y in ((c, d), (d, c)):
            if not (marks[b] & marks[x] or marks[a] & marks[y]):
                yield swap_goods(state, (a, x)), i, j, (a, x), (b, y)


def _groups(neighbors: list[set[int]]) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(len(neighbors)))
    groups = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        found, queue = [root], deque([root])
        while queue:
            for j in sorted(neighbors[queue.popleft()] & unseen):
                unseen.remove(j)
                found.append(j)
                queue.append(j)
        groups.append(tuple(sorted(found)))
    return tuple(groups)


@dataclass
class Component:
    """One entire unlabelled component, with constructive transposition witnesses."""

    marks: tuple[int, ...]
    root: Pairing
    representatives: dict[Pairing, Pairing]
    parent: dict[Pairing, tuple[Pairing, Swap] | None]
    loops: dict[Pair, tuple[Pairing, Swap, Swap]]
    groups: tuple[tuple[int, ...], ...]

    def root_path(self, key: Pairing) -> list[Swap]:
        moves = []
        while self.parent[key] is not None:
            key, move = self.parent[key]
            moves.append(move)
        return moves[::-1]

    def blocks(self) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(sorted(g for i in group for g in self.root[i]))
                     for group in self.groups)

    def statistics(self) -> dict:
        permutations = prod(factorial(len(group)) for group in self.groups)
        return {"unlabelled_states": len(self.representatives),
                "goods_blocks": self.blocks(),
                "labelled_components": factorial(len(self.root)) // permutations,
                "states_per_labelled_component": len(self.representatives) * permutations}


def explore(marks: tuple[int, ...], start: Pairing) -> Component:
    """Exhaust one unlabelled component and retain exact root-loop witnesses."""
    start = validate(marks, start)
    key = unlabelled(start)
    reps, parent = {key: start}, {key: None}
    neighbors = [set() for _ in start]
    loops = {}
    queue = deque([key])
    while queue:
        key = queue.popleft()
        for nxt, i, j, first, second in _switches(marks, reps[key]):
            neighbors[i].add(j)
            neighbors[j].add(i)
            loops.setdefault((i, j), (key, first, second))
            nxt_key = unlabelled(nxt)
            if nxt_key not in reps:
                reps[nxt_key] = nxt
                parent[nxt_key] = (key, first)
                queue.append(nxt_key)
    return Component(tuple(marks), start, reps, parent, loops, _groups(neighbors))


def connect(component: Component, target: Pairing) -> tuple[Pairing, ...] | None:
    """Construct a labelled path, or prove disconnection within this component.

    None also covers targets in a different unlabelled component. There is no
    state/time cutoff: an interrupted exploration is not a negative answer.
    """
    target = validate(component.marks, target)
    key = unlabelled(target)
    if key not in component.representatives:
        return None
    representative = component.representatives[key]
    target_slots = {p: i for i, p in enumerate(target)}
    wanted = [target_slots[p] for p in representative]
    group_of = {i: group for group in component.groups for i in group}
    if any(wanted[i] not in group_of[i] for i in range(len(wanted))):
        return None

    adjacency = [set() for _ in wanted]
    for i, j in component.loops:
        adjacency[i].add(j)
        adjacency[j].add(i)
    route = [component.root]
    current = list(range(len(wanted)))

    def append(moves: list[Swap]) -> None:
        for move in moves:
            route.append(swap_goods(route[-1], move))

    def transpose(i: int, j: int) -> None:
        prefix_key, first, second = component.loops[tuple(sorted((i, j)))]
        prefix = component.root_path(prefix_key)
        append(prefix + [first, second] + prefix[::-1])
        current[i], current[j] = current[j], current[i]

    for i in range(len(wanted)):
        if current[i] == wanted[i]:
            continue
        j = current.index(wanted[i])
        # This search is only in the small graph of recipient transpositions.
        previous, queue = {i: None}, deque([i])
        while j not in previous:
            u = queue.popleft()
            for v in sorted(adjacency[u]):
                if v not in previous:
                    previous[v] = u
                    queue.append(v)
        vertices = [j]
        while vertices[-1] != i:
            vertices.append(previous[vertices[-1]])
        edges = list(zip(vertices[::-1], vertices[-2::-1]))
        for a, b in edges + edges[-2::-1]:
            transpose(a, b)
    append(component.root_path(key))
    assert route[-1] == target
    return tuple(route)


def buffer_transpose(marks: tuple[int, ...], start: Pairing,
                     i: int, j: int) -> tuple[Pairing, ...]:
    """Transpose two recipient bundles in at most six swaps using a zero pair."""
    start = validate(marks, start)
    if any(type(k) is not int or k not in range(len(start)) for k in (i, j)):
        raise ValueError("unknown recipient")
    zero = next((k for k in (i, j) + tuple(range(len(start)))
                 if all(marks[g] == 0 for g in start[k])), None)
    if zero is None:
        raise ValueError("a pair of zero-marked goods is required")
    route = [start]
    steps = [] if i == j else ([(i, j)] if zero in (i, j)
                               else [(i, zero), (i, j), (j, zero)])
    for u, v in steps:
        a, b = route[-1][u]
        c, d = route[-1][v]
        for x, y in ((c, d), (d, c)):
            if not (marks[b] & marks[x] or marks[a] & marks[y]):
                route.append(swap_goods(route[-1], (a, x)))
                route.append(swap_goods(route[-1], (b, y)))
                break
        else:
            raise AssertionError("zero-buffer transposition lost its zero pair")
    return tuple(route)


def buffer_permute(marks: tuple[int, ...], start: Pairing,
                   target: Pairing) -> tuple[Pairing, ...]:
    """Sort pair labels with a moving zero pair in <= 2 floor(3(r-1)/2) swaps."""
    start, target = validate(marks, start), validate(marks, target)
    if unlabelled(start) != unlabelled(target):
        raise ValueError("buffer permutation requires the same unlabelled pairing")
    if start == target:
        return (start,)
    zero_pair = next((p for p in start if all(marks[g] == 0 for g in p)), None)
    if zero_pair is None:
        raise ValueError("a pair of zero-marked goods is required")
    route = [start]
    while route[-1] != target:
        current = route[-1]
        i = current.index(zero_pair)
        if target[i] == zero_pair:
            j = next(j for j, p in enumerate(current) if p != target[j])
        else:
            j = current.index(target[i])
        route.extend(buffer_transpose(marks, current, i, j)[1:])
    return tuple(route)


def connect_with_zero_pair(marks: tuple[int, ...], start: Pairing,
                           target: Pairing) -> tuple[Pairing, ...]:
    """Connect arbitrary legal matchings when the start contains a zero pair.

    This works for any number of observer bits, in at most
    3 floor(3(r-1)/2) exchanges. No matching graph is enumerated.
    """
    start, target = validate(marks, start), validate(marks, target)
    if start == target:
        return (start,)
    zero = next((pair for pair in start if all(marks[g] == 0 for g in pair)), None)
    if zero is None:
        raise ValueError("the start must contain a pair of zero-marked goods")
    p, q = zero
    old = {g: h for a, b in start for g, h in ((a, b), (b, a))}
    new = {g: h for a, b in target for g, h in ((a, b), (b, a))}
    unseen = {g for g in old if old[g] != new[g]}
    moves = []
    while unseen:
        first = a = min(unseen)
        cycle = []
        while True:
            b = old[a]
            cycle.append((a, b))
            unseen.difference_update((a, b))
            a = new[b]
            if a == first:
                break
        if any(p in pair for pair in cycle):
            continue  # the cycle containing both zero goods is performed last
        a = cycle[0][0]
        moves.append((p, a))
        moves.extend((p, x) for x, _ in cycle[1:])
        moves.append((p, a))
    a = new[p]
    while a != q:
        moves.append((q, a))
        a = new[old[a]]

    reached = start
    for move in moves:
        reached = swap_goods(reached, move)
    assert unlabelled(reached) == unlabelled(target)
    # Pre-permute root labels, then replay the same good exchanges. Good
    # exchanges commute with renaming recipients, so the endpoint is exact.
    slots = {pair: i for i, pair in enumerate(target)}
    desired = [None] * len(start)
    for i, pair in enumerate(reached):
        desired[slots[pair]] = start[i]
    route = list(buffer_permute(marks, start, tuple(desired)))
    for move in moves:
        route.append(swap_goods(route[-1], move))
    assert route[-1] == target
    return tuple(route)


def maximum_labelled_components(pairs: int) -> int:
    """Sharp bound above ONE unlabelled component for three-bit marks."""
    if type(pairs) is not int or pairs < 0:
        raise ValueError("the number of pairs must be a nonnegative integer")
    q, remainder = divmod(pairs, 4)
    return factorial(pairs) // (factorial(q + 1) ** remainder
                                * factorial(q) ** (4 - remainder))


def complementary_family(counts: tuple[int, int, int, int]) -> tuple[tuple[int, ...], Pairing]:
    """Four complementary type classes of the specified sizes; no enumeration."""
    if len(counts) != 4 or any(type(n) is not int or n < 0 for n in counts):
        raise ValueError("four nonnegative complementary-class sizes are required")
    marks, pairs = [], []
    for low, count in enumerate(counts):
        for _ in range(count):
            pairs.append((len(marks), len(marks) + 1))
            marks.extend((low, 7 ^ low))
    return tuple(marks), tuple(pairs)


def connect_complementary(marks: tuple[int, ...], start: Pairing,
                          target: Pairing) -> tuple[Pairing, ...] | None:
    """Linear-length path for saturated three-bit complementary families.

    Each pair must contain complementary three-bit types. A recipient's
    unordered pair of types is invariant. Subject to it, exchanging goods
    of the same type reaches the target in at most 2r exchanges.
    """
    start, target = validate(marks, start), validate(marks, target)
    if any(marks[a] ^ marks[b] != 7 for state in (start, target) for a, b in state):
        raise ValueError("every pair must have complementary three-bit marks")
    types = lambda state: tuple(tuple(sorted(marks[g] for g in pair)) for pair in state)
    if types(start) != types(target):
        return None
    route = [start]
    for i, pair in enumerate(target):
        for good in pair:
            if good not in route[-1][i]:
                old = next(g for g in route[-1][i] if marks[g] == marks[good])
                route.append(swap_goods(route[-1], (old, good)))
    assert route[-1] == target
    return tuple(route)


def realize_fixed_observers(marks: tuple[int, ...]) -> tuple[tuple[Fraction, ...], ...]:
    """Positive strict utilities whose fixed-observer EF1 fiber is exactly marks.

    Goods 0,1,2 belong to the three singleton observers. Remaining goods go
    in pairs to len(marks)//2 automatic recipients. This does not assert
    anything about the full graph after the three observer goods can move.
    """
    if len(marks) % 2 or any(type(m) is not int or m not in range(8) for m in marks):
        raise ValueError("need an even number of three-bit marks")
    n = len(marks)
    observers = tuple(
        tuple(Fraction(10) if i == j else Fraction(j + 1, 10) for j in range(3))
        + tuple(Fraction(11 if mark & (1 << i) else 1) + Fraction(g + 1, n + 1)
                for g, mark in enumerate(marks))
        for i in range(3))
    # Every pair, including a pair of former observer goods, is automatic.
    automatic = tuple(Fraction(3) + Fraction(g + 1, n + 4) for g in range(n + 3))
    return observers + (automatic,) * (n // 2)


def _with_observers(state: Pairing, loans: dict[int, int] | None = None) -> tuple[int, ...]:
    loans = {} if loans is None else loans
    owners = [0, 1, 2] + [-1] * (2 * len(state))
    for good, observer in loans.items():
        owners[good + 3] = observer
    for i, pair in enumerate(state):
        for g in pair:
            actual = loans.get(g, g + 3)
            owners[actual] = i + 3
    return tuple(owners)


def connect_realized(marks: tuple[int, ...], start: Pairing, target: Pairing,
                     observer_order: tuple[int, int, int] = (0, 1, 2)) -> tuple[tuple[int, ...], ...]:
    """EF1 path for any legal endpoints under realize_fixed_observers(marks).

    Borrow at most two observer goods to create a zero pair, connect all
    free pairs, then repay the loans. At most 4+3 floor(3(r-1)/2) exchanges
    for r>=1; zero free goods have a single allocation. This is a theorem
    for the explicit positive strict realization, not arbitrary utilities.
    """
    start, target = validate(marks, start), validate(marks, target)
    if (any(m not in range(8) for m in marks) or sorted(observer_order) != [0, 1, 2]
            or any(type(i) is not int for i in observer_order)):
        raise ValueError("need three-bit marks and a permutation of the three observers")
    if start == target:
        return (_with_observers(start),)
    loans, route = {}, [_with_observers(start)]
    for good in start[0]:
        if marks[good]:
            loans[good] = next(i for i in observer_order if marks[good] & (1 << i))
            route.append(_with_observers(start, loans))
    relaxed = tuple(0 if g in loans else mark for g, mark in enumerate(marks))
    partial = connect_with_zero_pair(relaxed, start, target)
    route.extend(_with_observers(state, loans) for state in partial[1:])
    for good in tuple(loans)[::-1]:
        del loans[good]
        route.append(_with_observers(target, loans))
    return tuple(route)


BOUNDARY_MARKS = (1, 6, 2, 5)
BOUNDARY_PROFILE = (
    (10, 1, 2, 14, 3, 4, 15),
    (1, 10, 2, 3, 14, 15, 4),
    (1, 2, 10, 3, 14, 4, 15),
    (1, 2, 3, 11, 12, 13, 14),
    (3, 2, 1, 14, 13, 12, 11),
)
BOUNDARY_START = (0, 1, 2, 3, 3, 4, 4)
BOUNDARY_TARGET = (0, 1, 2, 4, 4, 3, 3)


def boundary_census() -> dict:
    """Full fixed-size EF1 graph, including allocations outside picking outcomes."""
    from swaps import components, ef1, states_with_sizes

    all_states = states_with_sizes((1, 1, 1, 2, 2))
    fair = tuple(a for a in all_states if ef1(BOUNDARY_PROFILE, a))
    allowed = set(fair)
    previous, queue = {BOUNDARY_START: None}, deque([BOUNDARY_START])
    while BOUNDARY_TARGET not in previous:
        state = queue.popleft()
        for a, b in combinations(range(7), 2):
            if state[a] == state[b]:
                continue
            nxt = list(state)
            nxt[a], nxt[b] = nxt[b], nxt[a]
            nxt = tuple(nxt)
            if nxt in allowed and nxt not in previous:
                previous[nxt] = state
                queue.append(nxt)
    route, state = [], BOUNDARY_TARGET
    while state is not None:
        route.append(state)
        state = previous[state]
    fiber = tuple(a for a in fair if a[:3] == (0, 1, 2))
    return {"all_states": len(all_states), "fair_states": len(fair),
            "component_sizes": tuple(map(len, components(fair))),
            "fixed_observer_component_sizes": tuple(map(len, components(fiber))),
            "escape": tuple(route[::-1])}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-pairs", type=int, default=100,
                        help="size of the sharp complementary-family demonstration")
    args = parser.parse_args()
    if args.family_pairs < 0:
        parser.error("--family-pairs must be nonnegative")
    root = ((0, 1), (2, 3))
    blocked = explore(BOUNDARY_MARKS, root)
    print("four free goods:", blocked.statistics())
    print("interchanging recipients:", connect(blocked, root[::-1]))
    marks = (0, 1, 2, 5, 3, 4)
    root = ((0, 1), (2, 3), (4, 5))
    connected = explore(marks, root)
    path = connect(connected, root[::-1])
    print("dynamic three-pair component:", connected.statistics())
    print("constructed labelled swaps:", len(path) - 1)
    for n, state in enumerate(path):
        print(f"  {n}: {state}")
    census = boundary_census()
    print("strict positive EF1 census:", {k: v for k, v in census.items() if k != "escape"})
    print("full-graph escape:", " -> ".join("".join(map(str, a)) for a in census["escape"]))
    q, extra = divmod(args.family_pairs, 4)
    counts = tuple(q + (i < extra) for i in range(4))
    marks, root = complementary_family(counts)
    target, offset = [], 0
    for n in counts:
        block = root[offset:offset + n]
        target.extend(block[1:] + block[:1])
        offset += n
    path = connect_complementary(marks, root, tuple(target))
    print("sharp complementary family:", counts)
    print("labelled components:", maximum_labelled_components(args.family_pairs))
    print("within-component swaps:", len(path) - 1)
    target = root[::-1]
    print("reversed-label target in same fixed-observer component:",
          connect_complementary(marks, root, target) is not None)
    loan_path = connect_realized(marks, root, target)
    print("reversed-label EF1 loan swaps:", len(loan_path) - 1)


if __name__ == "__main__":
    main()
