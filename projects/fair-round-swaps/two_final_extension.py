"""Four agents, six goods: exact EF1 paths and two constructive local lemmas.

The proof in TWO_FINAL_EXTENSION.md covers greedy endpoints, including ties.
The finite graph search constructs paths; it is not the universal proof.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations

from swaps import (Allocation, Profile, Witness, allocation, ef1, exchange,
                   rounds_for, validate_profile, validate_witness)

# D=0, E=1, i=2, j=3; g=0, k=1, l=2, x=3, y=4, z=5.
LEFT = (2, 0, 1, 0, 3, 1)
RIGHT = (3, 0, 1, 2, 0, 1)
EXAMPLE: Profile = (
    (0, 10, 9, 8, 7, 6),
    (0, 20, 10, 8, 7, 6),
    (100, 90, 80, 60, 0, 1),
    (100, 90, 80, 0, 60, 1),
)


def _profile(u: Profile) -> None:
    validate_profile(u)
    if len(u) != 4 or len(u[0]) != 6:
        raise ValueError("need four agents and six goods")


def _swap(a: Allocation, g: int, h: int) -> Allocation:
    b = list(a)
    b[g], b[h] = b[h], b[g]
    return tuple(b)


def _checked(u: Profile, route: list[Allocation]) -> list[Allocation]:
    compact = [route[0]]
    for a in route[1:]:
        if a != compact[-1]:
            compact.append(a)
    if not all(ef1(u, a) for a in compact):
        raise AssertionError("constructed state is not EF1")
    if not all(exchange(a, b) for a, b in zip(compact, compact[1:])):
        raise AssertionError("constructed step is not one exchange")
    return compact


def bridge(u: Profile) -> list[Allocation]:
    """Connect LEFT to RIGHT without the earlier common-final-good guard.

    Check the local inequalities in the proof, including the case where
    D already took k before the shared favorite g was chosen. The final two
    assignments may be arbitrary: D's first good stays fixed.
    """
    _profile(u)
    required = ((0, 1, (2, 3, 4, 5)), (1, 2, (3, 4, 5)),
                (2, 0, (2, 3, 4, 5)), (3, 0, (2, 3, 4, 5)),
                (2, 3, (4, 5)), (3, 4, (3, 5)))
    if any(u[i][g] < u[i][h] for i, g, rest in required for h in rest):
        raise ValueError("the first-round braid inequalities do not hold")

    def loan(start: Allocation, x: int, y: int):
        route = [start]

        def move(a, b):
            route.append(_swap(route[-1], a, b))

        # E keeps the more valuable of x,z before lending l for g.
        t = min((x, 5), key=lambda h: (u[1][h], h))
        if t != x:
            move(x, 5)
        move(0, 2)
        move(0, y)
        # With l held by i and g by j, put x into E's pair safely.
        wanted = min((y, 5), key=lambda h: (u[1][h], h))
        current = next(h for h in (x, y, 5) if route[-1][h] == 0)
        if current != wanted:
            move(current, wanted)
        move(2, x)
        if wanted != y:
            move(wanted, y)
        return route

    if u[2][2] >= u[2][3]:
        result = loan(LEFT, 3, 4)
    elif u[3][2] >= u[3][4]:
        result = list(reversed(loan(RIGHT, 4, 3)))
    else:
        result = [LEFT]
        for g, h in ((3, 5), (0, 3), (0, 4), (5, 4)):
            result.append(_swap(result[-1], g, h))
    if result[-1] != RIGHT:
        raise AssertionError("bridge missed its target")
    return _checked(u, result)


def residual_path(u: Profile, start: Allocation, target: Allocation,
                  *, double: int, anchor: int, single: int, favorite: int
                  ) -> list[Allocation]:
    """Connect any fair states fixing a double anchor and a safe singleton.

    Both fixed goods must dominate all four variable goods for their owner.
    The other double and singleton may have arbitrary nonnegative utilities.
    """
    _profile(u)
    if (type(double) is not int or type(single) is not int
            or double not in range(4) or single not in range(4) or double == single
            or type(anchor) is not int or type(favorite) is not int
            or anchor not in range(6) or favorite not in range(6) or anchor == favorite):
        raise ValueError("invalid fixed agents or goods")
    variable = tuple(h for h in range(6) if h not in (anchor, favorite))
    if any(u[a][g] < u[a][h] for a, g in ((double, anchor), (single, favorite))
           for h in variable):
        raise ValueError("fixed goods must dominate the variable goods")
    for a in (start, target):
        if (len(a) != 6 or not ef1(u, a) or a[anchor] != double
                or a[favorite] != single or a.count(double) != 2
                or a.count(single) != 1 or sorted(a.count(i) for i in range(4)) != [1, 1, 2, 2]):
            raise ValueError("need fair endpoints with the same fixed goods and sizes")
    if any(start.count(i) != target.count(i) for i in range(4)):
        raise ValueError("different size vectors")
    e = next(i for i in range(4) if i != double and start.count(i) == 2)
    j = next(i for i in range(4) if i != single and start.count(i) == 1)
    best = max(variable, key=lambda h: (u[j][h], -h))

    def normalize(a):
        route = [a]

        def move(g, h):
            route.append(_swap(route[-1], g, h))

        b = route[-1].index(j)
        if sum(u[j][h] > u[j][b] for h in variable) > 1:
            t = next(h for h in variable if route[-1][h] == double)
            f = next(h for h in variable if route[-1][h] == e and u[j][h] > u[j][b])
            first, second = _swap(route[-1], b, f), _swap(route[-1], b, t)
            if ef1(u, first):
                route.append(first)
            else:
                route.append(second)
            b = route[-1].index(j)
        if b != best:
            others = [h for h in variable if h not in (b, best)]
            tail = min(others, key=lambda h: (u[e][h], h))
            current = next(h for h in variable if route[-1][h] == double)
            if current != tail:
                move(current, tail)
            move(b, best)
        # One canonical fair assignment of the three remaining goods.
        tail = min((h for h in variable if h != best), key=lambda h: (u[e][h], h))
        current = next(h for h in variable if route[-1][h] == double)
        if current != tail:
            move(current, tail)
        return _checked(u, route)

    left, right = normalize(start), normalize(target)
    if left[-1] != right[-1]:
        raise AssertionError("normal forms differ")
    return _checked(u, left + list(reversed(right))[1:])


def path(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Shortest EF1 path for greedy endpoints with final recipients 0 and 1."""
    _profile(u)
    rounds = rounds_for(4, 6, (0, 1))
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    a, b = allocation(start, 6), allocation(target, 6)
    parents: dict[Allocation, Allocation | None] = {a: None}
    queue = deque([a])
    while queue and b not in parents:
        current = queue.popleft()
        for g, h in combinations(range(6), 2):
            if current[g] == current[h]:
                continue
            neighbor = _swap(current, g, h)
            if neighbor not in parents and ef1(u, neighbor):
                parents[neighbor] = current
                queue.append(neighbor)
    if b not in parents:
        raise AssertionError("four-agent six-good theorem violated")
    result = [b]
    while parents[result[-1]] is not None:
        result.append(parents[result[-1]])
    return _checked(u, list(reversed(result)))


if __name__ == "__main__":
    route = bridge(EXAMPLE)
    print("Four agents, six goods: unguarded first-round braid")
    for index, state in enumerate(route):
        print(f"{index}: {''.join(map(str, state))}")
    print(f"Verified: {len(route)-1} exchanges; every state EF1")
    print("Both old guards fail: the common final good is worth 1, below 60")
    print("Scope: all four-agent six-good greedy endpoints; longer rounds remain open")
