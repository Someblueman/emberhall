"""Exact search for anchored windows and periodic packings that beat b/(5b+4).

Run: python3 projects/five-marks/counterexample.py

For positive odd b, S_b = {0, b+2, 2b+4, 3b+4, 4b+4}. A set of starts is legal
when no two differ by an element of M (the ten pair differences). This module
computes, exactly:

1. the maximum size of a legal subset of [0, n-1] with n=5b+4 that contains 0
   (the anchored window), for odd b = 1,3,5,7,9,11; and
2. the maximum density |A|/L of a legal periodic set modulo L, for
   L = n and L = 2n, for odd b = 1,3,5,7 (and 9,11 if the slice completes).

Any anchored window exceeding b, or any periodic density exceeding b/n, is
reported verbatim as a candidate refutation of the Fern upper bound. Finite
computation supports the argument only; it proves no infinite-family claim.
No third-party code; solver is an exact branch-and-bound maximum-clique search
on the complement of the conflict graph (Tomita-style coloring bound).
"""
from itertools import combinations


def shape(b: int) -> tuple[int, ...]:
    a = b + 2
    return (0, a, 2 * a, 2 * a + b, 2 * a + 2 * b)


def differences(s: tuple[int, ...]) -> set[int]:
    return {y - x for x, y in combinations(s, 2)}


def conflict_bitmasks(vertices: list[int], forbidden: set[int]) -> list[int]:
    """adj[i] = bitmask of conflict neighbours of vertices[i] (excluding self)."""
    pos = {v: i for i, v in enumerate(vertices)}
    adj = [0] * len(vertices)
    for i, x in enumerate(vertices):
        mask = 0
        for j, y in enumerate(vertices):
            if i != j and abs(x - y) in forbidden:
                mask |= 1 << j
        adj[i] = mask
    return adj


def legal(points: tuple[int, ...], forbidden: set[int]) -> bool:
    return len(points) == len(set(points)) and all(
        abs(x - y) not in forbidden for x, y in combinations(points, 2)
    )


def greedy_independent_set(adj: list[int], n: int) -> list[int]:
    """Low-degree greedy independent set; returns vertex indices."""
    remaining = set(range(n))
    chosen: list[int] = []
    while remaining:
        v = min(remaining, key=lambda u: bin(adj[u] & sum(1 << r for r in remaining)).count("1"))
        chosen.append(v)
        nb = adj[v]
        remaining -= {v}
        remaining = {u for u in remaining if not (nb >> u) & 1}
    return chosen


def max_independent_set(adj: list[int], n: int) -> list[int]:
    """Exact maximum independent set via max-clique on the complement.

    Complement graph H: distinct i,j adjacent in H iff not adjacent in adj.
    Tomita MCQ with greedy color sort bounds the clique search in H.
    """
    if n == 0:
        return []
    # complement adjacency (excluding self)
    full = (1 << n) - 1
    hadj = [full & ~(adj[i] | (1 << i)) for i in range(n)]

    best = greedy_independent_set(adj, n)
    best_size = len(best)

    def color_sort(candidates: list[int]) -> tuple[list[int], list[int]]:
        """Greedy color sort for max clique: returns (order, color_number)."""
        order: list[int] = []
        colors: list[int] = []
        remaining = list(candidates)
        color = 0
        while remaining:
            color += 1
            available = list(remaining)
            while available:
                v = available.pop(0)
                order.append(v)
                colors.append(color)
                remaining.remove(v)
                # keep only vertices non-adjacent in H (independent in H)
                available = [u for u in available if not (hadj[v] >> u) & 1]
            # next color class over what is left of remaining
        return order, colors

    def expand(depth: int, current: list[int], candidates: list[int]) -> None:
        nonlocal best, best_size
        order, colors = color_sort(candidates)
        for idx in range(len(order) - 1, -1, -1):
            if depth + colors[idx] <= best_size:
                return
            v = order[idx]
            new_candidates = [u for u in candidates if u != v and (hadj[v] >> u) & 1]
            new_current = current + [v]
            if not new_candidates:
                if depth + 1 > best_size:
                    best_size = depth + 1
                    best = list(new_current)
            else:
                expand(depth + 1, new_current, new_candidates)
            candidates = [u for u in candidates if u != v]

    expand(0, [], list(range(n)))
    return best


def anchored_maximum(b: int) -> tuple[int, tuple[int, ...]]:
    s = shape(b)
    m = differences(s)
    n = 5 * b + 4
    vertices = [x for x in range(1, n) if x not in m]
    adj = conflict_bitmasks(vertices, m)
    chosen = max_independent_set(adj, len(vertices))
    points = tuple(sorted([0] + [vertices[i] for i in chosen]))
    assert legal(points, m)
    return len(points), points


def periodic_maximum(b: int, period: int) -> tuple[int, tuple[int, ...]]:
    """Exact maximum |A|/period of a legal set periodic modulo period.

    If some forbidden distance is a multiple of period, every start
    conflicts with its own period-translate, so only the empty set is
    legal. Return that empty maximum explicitly rather than searching
    a conflict graph that drops the self-loop.
    """
    s = shape(b)
    m = differences(s)
    if any(d % period == 0 for d in m):
        return 0, ()
    vertices = list(range(period))
    pos = {v: i for i, v in enumerate(vertices)}
    adj = [0] * period
    for x in vertices:
        mask = 0
        for d in m:
            for y in ((x + d) % period, (x - d) % period):
                j = pos[y]
                if j != pos[x]:
                    mask |= 1 << j
        adj[pos[x]] = mask
    chosen = max_independent_set(adj, period)
    residues = tuple(sorted(vertices[i] for i in chosen))
    # verify on the cycle: no residue may reach a chosen residue,
    # including its own repeats (period-multiples return early above)
    residue_set = set(residues)
    for x in residues:
        for d in m:
            assert (x + d) % period not in residue_set, (b, period, x, d)
    return len(residues), residues


def check_bruteforce_solver() -> None:
    """Cross-check the exact solver against enumeration on tiny graphs."""
    import random
    rng = random.Random(20261117)
    for n in (8, 10, 12):
        for _ in range(12):
            adj = [0] * n
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.3:
                        adj[i] |= 1 << j
                        adj[j] |= 1 << i
            got = max_independent_set(adj, n)
            best = 0
            for mask in range(1 << n):
                idx = [i for i in range(n) if mask >> i & 1]
                ok = all(not (adj[i] >> j) & 1 for i, j in combinations(idx, 2))
                if ok:
                    best = max(best, len(idx))
            assert len(got) == best, (n, len(got), best)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O: this research check requires assertions')
    check_bruteforce_solver()
    print('Solver check: exact optima match brute force on 36 tiny graphs')
    target = {}
    for parameter in (1, 3, 5, 7, 9, 11):
        size, points = anchored_maximum(parameter)
        target[parameter] = size
        flag = 'BEATS BOUND' if size > parameter else 'matches bound b'
        print(f'anchored b={parameter}: maximum {size} ({flag}); example {points}')
        assert size == parameter, (parameter, size, points)
    print('Anchored windows: all maxima equal b for odd b=1,3,5,7,9,11')
    for parameter in (1, 3, 5, 7, 9, 11):
        n = 5 * parameter + 4
        for period in (n, 2 * n):
            size, residues = periodic_maximum(parameter, period)
            density = size / period
            bound = parameter / n
            flag = 'BEATS BOUND' if size * n > parameter * period else 'at/below bound'
            print(f'periodic b={parameter} L={period}: {size}/{period} = {density:.6f} '
                  f'vs {bound:.6f} ({flag})')
            assert size * n <= parameter * period, (parameter, period, size, residues)
    print('Periodic search: no density beats b/(5b+4) in the searched range')
    print('Finite search passed; read PROOF.md for the all-parameter argument.')
