"""Complete order-type certificate for EF1 exchanges with sizes (2, 1, 1)."""

from __future__ import annotations

from collections import Counter, deque
from hashlib import sha256
from itertools import combinations, permutations, product
import json

Rank = tuple[int, ...]
Allocation = tuple[int, ...]  # owner of each of the four labelled goods
STATES = tuple(sorted(set(permutations((0, 0, 1, 2)))))


def weak_orders() -> tuple[Rank, ...]:
    """All ordered partitions of four goods, encoded by consecutive ranks."""
    return tuple(r for r in product(range(4), repeat=4)
                 if set(r) == set(range(max(r) + 1)))


def fair(a: Allocation, b: Rank, c: Rank) -> bool:
    """Only singleton agents can envy after removing one good."""
    pair = [g for g, owner in enumerate(a) if owner == 0]
    return all(r[a.index(i)] >= min(r[g] for g in pair)
               for i, r in ((1, b), (2, c)))


def graph(b: Rank, c: Rank) -> dict[Allocation, tuple[Allocation, ...]]:
    vertices = {a for a in STATES if fair(a, b, c)}
    result = {}
    for a in sorted(vertices):
        neighbors = []
        for x, y in combinations(range(4), 2):
            if a[x] == a[y]:
                continue
            changed = list(a)
            changed[x], changed[y] = changed[y], changed[x]
            target = tuple(changed)
            if target in vertices:
                neighbors.append(target)
        result[a] = tuple(sorted(neighbors))
    return result


def distances(edges: dict[Allocation, tuple[Allocation, ...]],
              start: Allocation) -> dict[Allocation, int]:
    result = {start: 0}
    queue = deque([start])
    while queue:
        a = queue.popleft()
        for target in edges[a]:
            if target not in result:
                result[target] = result[a] + 1
                queue.append(target)
    return result


def shortest_path(b: Rank, c: Rank, start: Allocation,
                  target: Allocation) -> tuple[Allocation, ...]:
    edges = graph(b, c)
    if start not in edges or target not in edges:
        raise ValueError("both endpoints must be EF1 with sizes (2, 1, 1)")
    parents: dict[Allocation, Allocation | None] = {start: None}
    queue = deque([start])
    while queue and target not in parents:
        a = queue.popleft()
        for neighbor in edges[a]:
            if neighbor not in parents:
                parents[neighbor] = a
                queue.append(neighbor)
    if target not in parents:
        raise ValueError("endpoints are disconnected")
    path = [target]
    while parents[path[-1]] is not None:
        path.append(parents[path[-1]])
    return tuple(reversed(path))


def certificate() -> dict:
    orders = weak_orders()
    diameters: Counter[int] = Counter()
    sizes: Counter[int] = Counter()
    masks = set()
    digest = sha256()
    worst = None
    for b, c in product(orders, repeat=2):
        edges = graph(b, c)
        if not edges:
            raise AssertionError(("empty graph", b, c))
        diameter = 0
        for start in edges:
            reached = distances(edges, start)
            if len(reached) != len(edges):
                raise AssertionError(("disconnected graph", b, c, start, reached))
            diameter = max(diameter, max(reached.values()))
        if worst is None or diameter > worst[0]:
            worst = (diameter, b, c)
        mask = sum(1 << i for i, a in enumerate(STATES) if a in edges)
        masks.add(mask)
        sizes[len(edges)] += 1
        diameters[diameter] += 1
        digest.update((json.dumps([b, c, mask, diameter], separators=(",", ":"))
                       + "\n").encode("ascii"))
    return {"weak_orders": len(orders), "profiles": len(orders) ** 2,
            "allocations": len(STATES), "distinct_graphs": len(masks),
            "vertex_histogram": dict(sorted(sizes.items())),
            "diameter_histogram": dict(sorted(diameters.items())),
            "largest_diameter_witness": worst, "certificate_sha256": digest.hexdigest()}


if __name__ == "__main__":
    print(json.dumps(certificate(), indent=2, sort_keys=True))
