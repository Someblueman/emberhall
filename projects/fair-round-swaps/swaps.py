"""Exact finite allocation model; no external packages or floating-point arithmetic."""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations

Profile = tuple[tuple[int | Fraction, ...], ...]
Allocation = tuple[int, ...]  # owner of each labelled good
Rounds = tuple[tuple[int, ...], ...]  # permitted agents in each successive round
Witness = tuple[tuple[int, int], ...]  # (agent, good) in actual picking order


def validate_profile(u: Profile) -> None:
    if len(u) < 2 or not u[0] or any(len(row) != len(u[0]) for row in u):
        raise ValueError("need at least two agents and equally long nonempty utility rows")
    if any(type(v) not in (int, Fraction) or v < 0 for row in u for v in row):
        raise ValueError("utilities must be exact nonnegative integers or Fractions")


def rounds_for(n: int, m: int, final: tuple[int, ...]) -> Rounds:
    if n < 2 or m < 1 or len(final) != m % n or len(set(final)) != len(final):
        raise ValueError("final round must specify exactly the agents receiving an extra good")
    if any(i not in range(n) for i in final):
        raise ValueError("unknown agent")
    return (tuple(range(n)),) * (m // n) + ((tuple(sorted(final)),) if final else ())


def after_pick(rounds: Rounds, agent: int) -> Rounds:
    if not rounds or agent not in rounds[0]:
        raise ValueError("agent cannot pick now")
    rest = tuple(i for i in rounds[0] if i != agent)
    return (rest,) + rounds[1:] if rest else rounds[1:]


def favorites(u: Profile, agent: int, goods: tuple[int, ...]) -> tuple[int, ...]:
    best = max(u[agent][g] for g in goods)
    return tuple(g for g in goods if u[agent][g] == best)


def allocation(witness: Witness, m: int) -> Allocation:
    owners = [-1] * m
    for i, g in witness:
        if g not in range(m) or owners[g] != -1:
            raise ValueError("repeated or unknown good")
        owners[g] = i
    return tuple(owners)


def validate_witness(u: Profile, rounds: Rounds, witness: Witness) -> None:
    validate_profile(u)
    remaining = tuple(range(len(u[0])))
    if sum(map(len, rounds)) != len(remaining):
        raise ValueError("round lengths do not cover the goods")
    for i, g in witness:
        if g not in remaining or not rounds or i not in rounds[0]:
            raise ValueError("illegal pick")
        if g not in favorites(u, i, remaining):
            raise ValueError("pick is not a utility maximizer")
        remaining = tuple(h for h in remaining if h != g)
        rounds = after_pick(rounds, i)
    if remaining or rounds:
        raise ValueError("incomplete witness")


def ef1(u: Profile, a: Allocation) -> bool:
    if len(a) != len(u[0]) or any(i not in range(len(u)) for i in a):
        raise ValueError("allocation must assign each good exactly once")
    for i, row in enumerate(u):
        sums = [sum(row[g] for g, owner in enumerate(a) if owner == j)
                for j in range(len(u))]
        for j in range(len(u)):
            largest = max((row[g] for g, owner in enumerate(a) if owner == j), default=0)
            if sums[i] < sums[j] - largest:
                return False
    return True


def exchange(a: Allocation, b: Allocation) -> bool:
    if len(a) != len(b):
        return False
    changed = [g for g in range(len(a)) if a[g] != b[g]]
    return (len(changed) == 2
            and a[changed[0]] == b[changed[1]]
            and a[changed[1]] == b[changed[0]])


def states_with_sizes(sizes: tuple[int, ...]) -> tuple[Allocation, ...]:
    """Every fixed-size allocation, including those with no picking witness."""
    def build(i: int, remaining: tuple[int, ...], owners: Allocation):
        if i == len(sizes) - 1:
            a = list(owners)
            for g in remaining:
                a[g] = i
            yield tuple(a)
            return
        for chosen in combinations(remaining, sizes[i]):
            a = list(owners)
            for g in chosen:
                a[g] = i
            yield from build(i + 1, tuple(g for g in remaining if g not in chosen), tuple(a))

    if len(sizes) < 2 or any(type(s) is not int or s < 0 for s in sizes):
        raise ValueError("invalid size vector")
    m = sum(sizes)
    return tuple(build(0, tuple(range(m)), (-1,) * m))


def components(states: tuple[Allocation, ...]) -> tuple[tuple[Allocation, ...], ...]:
    todo = set(states)
    result = []
    while todo:
        start = min(todo)
        todo.remove(start)
        found = [start]
        queue = deque([start])
        while queue:
            a = queue.popleft()
            for x, y in combinations(range(len(a)), 2):
                if a[x] == a[y]:
                    continue
                b = list(a)
                b[x], b[y] = b[y], b[x]
                b = tuple(b)
                if b in todo:
                    todo.remove(b)
                    found.append(b)
                    queue.append(b)
        result.append(tuple(sorted(found)))
    return tuple(result)


def picking_outcomes(u: Profile, rounds: Rounds) -> dict[Allocation, Witness]:
    """Exhaust all agent orders AND all tied maximizers; retain one witness per outcome."""
    validate_profile(u)
    m = len(u[0])
    if sum(map(len, rounds)) != m:
        raise ValueError("round lengths do not cover the goods")

    @lru_cache(None)
    def visit(rs: Rounds, goods: tuple[int, ...]) -> dict[Allocation, Witness]:
        if not goods:
            return {(-1,) * m: ()}
        result = {}
        for i in rs[0]:
            for g in favorites(u, i, goods):
                for a, w in visit(after_pick(rs, i), tuple(h for h in goods if h != g)).items():
                    owners = list(a)
                    owners[g] = i
                    result[tuple(owners)] = ((i, g),) + w
        return result

    return visit(rounds, tuple(range(m)))
