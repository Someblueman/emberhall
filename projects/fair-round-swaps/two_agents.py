"""Construct the exchange path proved in proof.md, retaining every picking witness."""

from __future__ import annotations

from swaps import (Allocation, Profile, Rounds, Witness, after_pick, allocation,
                   ef1, exchange, favorites, validate_profile, validate_witness)


def path(u: Profile, rounds: Rounds, start: Witness, target: Witness) -> list[Witness]:
    """Connect two valid two-agent witnesses with these complete/partial rounds.

    Public inputs are full recursively balanced schedules, optionally with a final
    singleton. The proof also uses suffix schedules internally. No shortest-path
    or polynomial-running-time claim is made.
    """
    validate_profile(u)
    if len(u) != 2 or not rounds:
        raise ValueError("need two agents and at least one round")
    if any(r != (0, 1) for r in rounds[:-1]) or rounds[-1] not in ((0,), (1,), (0, 1)):
        raise ValueError("need complete rounds and at most one final singleton")
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)

    def complete(rs: Rounds, goods: tuple[int, ...]) -> Witness:
        if not goods:
            return ()
        i = rs[0][0]
        g = favorites(u, i, goods)[0]
        return ((i, g),) + complete(after_pick(rs, i), tuple(h for h in goods if h != g))

    def bridge(rs: Rounds, goods: tuple[int, ...], i: int, j: int, g: int) -> tuple[Witness, Witness]:
        """Shared-favorite bridge: opposite orders until they coalesce or reach the tail."""
        left, right = [(i, g)], [(j, g)]
        pool = tuple(h for h in goods if h != g)
        # First round has only the other agent's pick left in each run.
        y = favorites(u, j, pool)[0]
        x = favorites(u, i, pool)[0]
        left.append((j, y))
        right.append((i, x))
        tail = rs[1:]
        common = tuple(h for h in pool if h not in (x, y))
        while x != y and tail and len(tail[0]) == 2:
            # x and y were maximizers in a superset of the current pools.
            left.append((i, x))
            right.append((j, y))
            y = favorites(u, j, common)[0]
            x = favorites(u, i, common)[0]
            left.append((j, y))
            right.append((i, x))
            common = tuple(h for h in common if h not in (x, y))
            tail = tail[1:]
        if x == y:
            rest = complete(tail, common)
            left.extend(rest)
            right.extend(rest)
        else:
            # Exactly one good remains in each run, and the same agent gets it.
            if len(tail) != 1 or len(tail[0]) != 1 or common:
                raise AssertionError("unclosed braid must end at a single final pick")
            last = tail[0][0]
            left.append((last, x))
            right.append((last, y))
        return tuple(left), tuple(right)

    def connect(rs: Rounds, goods: tuple[int, ...], a: Witness, b: Witness) -> list[Witness]:
        if a == b:
            return [a]
        if len(goods) <= 2:
            # One possible allocation, or a single exchange; covers two singleton rounds.
            return [a, b]
        (i, g), (j, h) = a[0], b[0]
        if (i, g) == (j, h):
            rest = connect(after_pick(rs, i), tuple(x for x in goods if x != g), a[1:], b[1:])
            return [((i, g),) + w for w in rest]
        if i == j and len(rs[0]) == 2:
            other = 1 - i
            x = favorites(u, other, goods)[0]
            middle = ((other, x),) + complete(after_pick(rs, other), tuple(t for t in goods if t != x))
            # Both recursive calls immediately enter the different-first-agent case.
            return connect(rs, goods, a, middle) + connect(rs, goods, middle, b)[1:]
        if i == j:
            # Singleton first round; i takes both tied goods before anyone else moves.
            next_round = after_pick(rs, i)
            if not next_round or next_round[0] != (0, 1):
                raise AssertionError("a long singleton suffix has a complete next round")
            rest = complete(after_pick(next_round, i), tuple(t for t in goods if t not in (g, h)))
            left = ((i, g), (i, h)) + rest
            right = ((i, h), (i, g)) + rest
        elif g != h:
            # Distinct favorite goods can be taken in either order.
            rest = complete(rs[1:], tuple(t for t in goods if t not in (g, h)))
            left = ((i, g), (j, h)) + rest
            right = ((j, h), (i, g)) + rest
        else:
            left, right = bridge(rs, goods, i, j, g)
        # Each end now agrees on its first pick with its bridge endpoint. Thus
        # each recursive call below fixes one good before doing any further work.
        return connect(rs, goods, a, left) + connect(rs, goods, right, b)

    result = connect(rounds, tuple(range(len(u[0]))), start, target)
    # Do not trust the construction to certify itself: independently check each
    # maximizing pick, EF1 inequality, and exact exchange in the returned path.
    previous: Allocation | None = None
    compact = []
    for w in result:
        validate_witness(u, rounds, w)
        owners = allocation(w, len(u[0]))
        if not ef1(u, owners):
            raise AssertionError("constructed picking outcome failed EF1")
        if previous == owners:
            continue
        if previous is not None and not exchange(previous, owners):
            raise AssertionError("constructed path step is not one exchange")
        compact.append(w)
        previous = owners
    return compact
