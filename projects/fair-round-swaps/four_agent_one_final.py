"""The protected five-good bridge for the four-agent 4q+1 theorem.

The full endpoint constructor enumerates EF1 states and is intended for small
inputs. The bridge and padding operations work at arbitrary round lengths.
"""

from __future__ import annotations

from four_agent_lift import _search
from swaps import (Allocation, Profile, Witness, allocation, ef1, favorites,
                   rounds_for, validate_profile, validate_witness)


def carrier_path(u: Profile, start: Allocation, target: Allocation,
                 carriers: tuple[int, int] = (1, 2)) -> list[Allocation]:
    """Connect fair five-good states keeping good 0 with two singleton agents."""
    validate_profile(u)
    if len(u) != 4 or len(u[0]) != 5:
        raise ValueError("need four agents and five goods")
    if (len(carriers) != 2 or len(set(carriers)) != 2
            or any(type(i) is not int or i not in (1, 2, 3) for i in carriers)):
        raise ValueError("need two distinct singleton carriers")
    if any(u[i][0] < max(u[i]) for i in carriers):
        raise ValueError("good 0 must be a favorite of both carriers")
    if any(tuple(a.count(i) for i in range(4)) != (2, 1, 1, 1) for a in (start, target)):
        raise ValueError("need size vector (2,1,1,1)")
    return _search(u, start, target, lambda a: a[0] in carriers)


def padded_path(u: Profile, prefix: Witness, tail: tuple[int, ...],
                start: Allocation, target: Allocation,
                carriers: tuple[int, int] = (1, 2)) -> list[Allocation]:
    """Lift a protected five-good bridge, checking the padding hypotheses."""
    validate_profile(u)
    m = len(u[0])
    if (len(u) != 4 or m < 5 or m % 4 != 1 or len(tail) != 5
            or len(set(tail)) != 5 or any(type(g) is not int or g not in range(m) for g in tail)
            or len(prefix) != m - 5):
        raise ValueError("need a complete-round prefix and five distinct tail goods")
    if (len(carriers) != 2 or len(set(carriers)) != 2
            or any(type(i) is not int or i not in (1, 2, 3) for i in carriers)):
        raise ValueError("need two distinct singleton carriers")
    remaining = tuple(g for g in range(m) if g != tail[0])
    eligible = set(range(4))
    common = [[] for _ in range(4)]
    for i, g in prefix:
        if i not in eligible or g not in remaining or g not in favorites(u, i, remaining):
            raise ValueError("prefix is not greedy with the protected good omitted")
        common[i].append(g)
        eligible.remove(i)
        if not eligible:
            eligible = set(range(4))
        remaining = tuple(h for h in remaining if h != g)
    if set(remaining) != set(tail[1:]) or eligible != set(range(4)):
        raise ValueError("prefix does not leave the declared tail")
    if any(sum(u[a][g] for g in common[a]) < sum(u[a][g] for g in common[b])
           for a in range(4) for b in carriers if a != b):
        raise ValueError("common bundles do not dominate carrier bundles")
    small = tuple(tuple(row[g] for g in tail) for row in u)
    result = []
    for a in carrier_path(small, start, target, carriers):
        full = list(allocation(prefix, m))
        for g, owner in zip(tail, a):
            full[g] = owner
        full = tuple(full)
        if not ef1(u, full):
            raise AssertionError("protected padding failed")
        result.append(full)
    return result


def path(u: Profile, start: Witness, target: Witness) -> list[Allocation]:
    """Full EF1 graph search for greedy 4q+1 endpoints; final recipient is 0.

    This finite reference constructor has exponential memory requirements.
    Use the protected bridge for large local braid instances.
    """
    validate_profile(u)
    m = len(u[0])
    if len(u) != 4 or m < 5 or m % 4 != 1:
        raise ValueError("need four agents and 4q+1 goods, q>=1")
    rounds = rounds_for(4, m, (0,))
    validate_witness(u, rounds, start)
    validate_witness(u, rounds, target)
    return _search(u, allocation(start, m), allocation(target, m))


EXAMPLE: Profile = ((0, 10, 9, 1, 2), (10, 9, 8, 5, 0),
                    (10, 9, 8, 0, 5), (10, 9, 8, 2, 1))
LEFT, RIGHT = (1, 0, 3, 0, 2), (2, 0, 3, 1, 0)


if __name__ == "__main__":
    result = carrier_path(EXAMPLE, LEFT, RIGHT)
    print("Four agents, one final recipient: protected five-good bridge")
    for index, a in enumerate(result):
        print(f"{index}: {''.join(map(str, a))}")
    print(f"Verified: {len(result)-1} exchanges; good 0 stays with a carrier; every state EF1")
    print("Candidate theorem: four agents, 4q+1 goods; independent reconstruction pending")
