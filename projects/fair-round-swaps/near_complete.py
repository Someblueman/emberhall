"""Candidate EF1 construction when exactly one agent misses the final round.

The complete rounds stay greedy. Final assignments may be arbitrary; the
free-final-round lemma in FRONTIER.md is essential, not an omitted tie rule.
"""

from __future__ import annotations

from swaps import (Profile, Rounds, Witness, after_pick, allocation, ef1,
                   exchange, favorites, validate_profile, validate_witness)


def validate_relaxed(u: Profile, rounds: Rounds, witness: Witness) -> None:
    """Check all picks, allowing non-maximizing picks only in the final round."""
    validate_profile(u)
    remaining = tuple(range(len(u[0])))
    for i, g in witness:
        if not rounds or i not in rounds[0] or g not in remaining:
            raise ValueError("illegal relaxed pick")
        if len(rounds) > 1 and g not in favorites(u, i, remaining):
            raise ValueError("non-maximizing pick before the final round")
        remaining = tuple(h for h in remaining if h != g)
        rounds = after_pick(rounds, i)
    if remaining or rounds:
        raise ValueError("incomplete relaxed witness")


def path(u: Profile, rounds: Rounds, start: Witness, target: Witness) -> list[Witness]:
    """Return an EF1 exchange path between greedy near-complete-round endpoints."""
    validate_profile(u)
    n, m = len(u), len(u[0])
    if m % n != n - 1 or not rounds:
        raise ValueError("this construction requires m mod n = n-1")
    if (any(r != tuple(range(n)) for r in rounds[:-1])
            or len(rounds[-1]) != n - 1
            or len(set(rounds[-1])) != n - 1
            or any(i not in range(n) for i in rounds[-1])):
        raise ValueError("need complete rounds followed by all but one agent")
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)

    def complete(rs: Rounds, goods: tuple[int, ...]) -> Witness:
        if not goods:
            return ()
        i = rs[0][0]
        g = favorites(u, i, goods)[0]
        return ((i, g),) + complete(after_pick(rs, i), tuple(h for h in goods if h != g))

    def permute(a: Witness, b: Witness, order: tuple[int, ...]) -> list[Witness]:
        """One good per agent. Fix agents in order, preserving earlier fixes."""
        current, goal = dict(a), dict(b)
        result = [a]
        for i in order:
            if current[i] == goal[i]:
                continue
            j = next(j for j in order if current[j] == goal[i])
            current[i], current[j] = current[j], current[i]
            result.append(tuple((j, current[j]) for j in order))
        return result

    def bridge(rs: Rounds, goods: tuple[int, ...], i: int, j: int, g: int):
        left, right = [(i, g)], [(j, g)]
        common = tuple(h for h in goods if h != g)
        eligible = rs[0]
        tail = rs[1:]
        while True:
            # In each greedy round the other eligible agents see the same pool.
            for a in eligible:
                if a not in (i, j):
                    h = favorites(u, a, common)[0]
                    left.append((a, h))
                    right.append((a, h))
                    common = tuple(k for k in common if k != h)
            x = favorites(u, i, common)[0]
            y = favorites(u, j, common)[0]
            left.append((j, y))
            right.append((i, x))
            common = tuple(h for h in common if h not in (x, y))
            if x == y:
                rest = complete(tail, common)
                return tuple(left) + rest, tuple(right) + rest
            if len(tail) == 1:
                # Only one agent is missing from F, so one active agent is in F.
                final = tail[0]
                carrier = i if i in final else j
                if carrier not in final:
                    raise AssertionError("neither active agent receives a final good")
                left.append((carrier, x))
                right.append((carrier, y))
                rest = tuple(zip((a for a in final if a != carrier), common))
                return tuple(left) + rest, tuple(right) + rest
            # Cross the two outstanding goods before the next round's middle.
            left.append((i, x))
            right.append((j, y))
            eligible = tail[0]
            tail = tail[1:]

    def connect(rs: Rounds, goods: tuple[int, ...], a: Witness, b: Witness) -> list[Witness]:
        if a == b:
            return [a]
        if len(rs) == 1:
            return permute(a, b, rs[0])
        (i, g), (j, h) = a[0], b[0]
        if (i, g) == (j, h):
            rest = connect(after_pick(rs, i), tuple(x for x in goods if x != g), a[1:], b[1:])
            return [((i, g),) + w for w in rest]
        if i == j and len(rs[0]) > 1:
            other = next(a for a in rs[0] if a != i)
            x = favorites(u, other, goods)[0]
            middle = ((other, x),) + complete(after_pick(rs, other), tuple(t for t in goods if t != x))
            return connect(rs, goods, a, middle) + connect(rs, goods, middle, b)[1:]
        if i == j:
            remaining = tuple(t for t in goods if t not in (g, h))
            if len(rs) > 2:
                rest = complete(after_pick(rs[1:], i), remaining)
            elif i in rs[-1]:
                rest = tuple(zip((a for a in rs[-1] if a != i), remaining))
            else:
                # This greedy pick is last; all agents receive one suffix good.
                # Both first goods maximize i's utility. Fix i first, then F.
                return permute(a, b, (i,) + rs[-1])
            left = ((i, g), (i, h)) + rest
            right = ((i, h), (i, g)) + rest
        elif g != h:
            rest = complete(after_pick(after_pick(rs, i), j),
                            tuple(t for t in goods if t not in (g, h)))
            left = ((i, g), (j, h)) + rest
            right = ((j, h), (i, g)) + rest
        else:
            left, right = bridge(rs, goods, i, j, g)
        return connect(rs, goods, a, left) + connect(rs, goods, right, b)

    result = connect(rounds, tuple(range(m)), start, target)
    compact = []
    previous = None
    for w in result:
        validate_relaxed(u, rounds, w)
        owners = allocation(w, m)
        if not ef1(u, owners):
            raise AssertionError("relaxed witness is not EF1")
        if owners == previous:
            continue
        if previous is not None and not exchange(previous, owners):
            raise AssertionError("constructed step is not a single exchange")
        compact.append(w)
        previous = owners
    return compact


if __name__ == "__main__":
    from swaps import rounds_for

    utilities = ((2, 2, 1, 1, 3), (0, 3, 3, 1, 0), (3, 3, 0, 3, 3))
    schedule = rounds_for(3, 5, (0, 1))
    initial = ((2, 0), (1, 1), (0, 4), (0, 2), (1, 3))
    target = ((2, 3), (1, 2), (0, 4), (1, 1), (0, 0))
    route = path(utilities, schedule, initial, target)
    print(f"near-complete demo: 3 agents, 5 goods, sizes (2,2,1), {len(route)-1} swaps")
    for index, witness in enumerate(route):
        owners = "".join(map(str, allocation(witness, 5)))
        print(f"{index}: {owners} | picks " + " ".join(f"{a}:{g}" for a, g in witness))
    print("Verified: greedy complete rounds, permitted final assignments, EF1, single exchanges")
