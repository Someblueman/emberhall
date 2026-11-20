"""Reproduce the calibration and exercise the general fair-exchange construction."""

from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random

from swaps import (allocation, components, ef1, exchange, picking_outcomes,
                   rounds_for, states_with_sizes, validate_profile, validate_witness)
from two_agents import path


def four_goods():
    # Strict rankings of Proposition 3.4, encoded by one exact representative.
    u = ((4, 3, 2, 1), (3, 1, 2, 4), (2, 3, 1, 4))
    outcomes = picking_outcomes(u, rounds_for(3, 4, (0,)))
    expected = {(0, 2, 0, 1), (0, 0, 1, 2), (1, 0, 0, 2)}
    assert set(outcomes) == expected
    states = states_with_sizes((2, 1, 1))
    fair = tuple(a for a in states if ef1(u, a))
    route = [(0, 2, 0, 1), (2, 0, 0, 1), (1, 0, 0, 2), (0, 0, 1, 2)]
    assert all(a in fair for a in route)
    assert all(exchange(a, b) for a, b in zip(route, route[1:]))
    assert route[1] not in outcomes
    restricted = components(tuple(outcomes))
    full = components(fair)
    assert sorted(map(len, restricted)) == [1, 2]
    assert len(full) == 1
    # Also prove the bridge for EVERY nonnegative utility consistent with the
    # rankings: each singleton must dominate at least one good in the big bundle.
    ranks = [tuple(sorted(range(4), key=lambda g: -row[g])) for row in u]
    for a in route:
        big = [g for g in range(4) if a[g] == 0]
        for i in (1, 2):
            singleton = next(g for g in range(4) if a[g] == i)
            assert any(ranks[i].index(singleton) < ranks[i].index(g) for g in big)
    print(f"four goods: {len(states)} fixed-size states, {len(fair)} EF1 states, "
          f"picking components {[len(c) for c in restricted]}, EF1 components {[len(c) for c in full]}")
    print("four-good bridge (owners of g1,g2,g3,g4; agents numbered 1..3):")
    print(" -> ".join("".join(str(i + 1) for i in a) for a in route))
    print("bridge inequalities: verified by strict rankings, independent of their magnitudes")


def weak_orders(m):
    """Every labelled weak order, once, represented by consecutive integer ranks."""
    for row in product(range(m), repeat=m):
        if set(row) == set(range(max(row) + 1)):
            yield row


def exercise(u, last, all_pairs=True, rng=None):
    rounds = rounds_for(2, len(u[0]), (last,) if len(u[0]) % 2 else ())
    outcomes = picking_outcomes(u, rounds)
    witnesses = list(outcomes.values())
    pairs = list(combinations(range(len(witnesses)), 2))
    if not all_pairs and len(pairs) > 20:
        pairs = rng.sample(pairs, 20)
    biggest = 0
    for a, b in pairs:
        result = path(u, rounds, witnesses[a], witnesses[b])
        assert allocation(result[0], len(u[0])) == allocation(witnesses[a], len(u[0]))
        assert allocation(result[-1], len(u[0])) == allocation(witnesses[b], len(u[0]))
        # Independent membership in exhaustive set of ALL tie/order outcomes.
        assert all(allocation(w, len(u[0])) in outcomes for w in result)
        biggest = max(biggest, len(result) - 1)
    return len(pairs), biggest


def two_agent_checks():
    pairs = profiles = longest = 0
    # This finite check includes ALL two-agent ordinal profiles on three goods,
    # all tie choices, both possible extra-good recipients, all endpoint pairs.
    orders = tuple(weak_orders(3))
    assert len(orders) == 13
    for u in product(orders, repeat=2):
        for last in (0, 1):
            count, biggest = exercise(u, last)
            pairs += count
            longest = max(longest, biggest)
            profiles += 1
    print(f"three goods: {profiles} profile/final-agent cases, {pairs} constructed endpoint pairs")
    # Strict profiles through five goods: label symmetry fixes agent 0's order.
    count5 = 0
    for row in permutations(range(5)):
        for last in (0, 1):
            count, biggest = exercise((tuple(range(5)), row), last)
            count5 += count
            longest = max(longest, biggest)
    print(f"five goods: 240 strict profile/final-agent cases, {count5} constructed endpoint pairs")
    rng = Random(20261120)
    larger = larger_pairs = 0
    for m in (4, 5, 6, 7, 9):
        for trial in range(24):
            # Include all-zero ties and long common-ranking profiles deliberately.
            if trial == 0:
                u = ((0,) * m,) * 2
            elif trial == 1:
                u = (tuple(range(m)),) * 2
            else:
                u = tuple(tuple(rng.choice((0, 1, 2, 4, 9)) for _ in range(m)) for _ in range(2))
            for last in ((0, 1) if m % 2 else (0,)):
                count, biggest = exercise(u, last, all_pairs=False, rng=rng)
                larger_pairs += count
                longest = max(longest, biggest)
                larger += 1
    print(f"seed 20261120: {larger} larger profile/final-agent cases, "
          f"{larger_pairs} constructed endpoint pairs, longest tested path {longest} swaps")
    # Exact rational scaling preserves all comparisons in the construction.
    u = ((Fraction(1, 3), Fraction(2, 7), 0), (0, Fraction(2, 7), Fraction(1, 3)))
    exercise(u, 0)
    print("rational utilities: passed")


def failure_boundaries():
    rejected = 0
    for u in (((-1, 0), (0, 1)), ((0.5, 0), (0, 1)), ((1,), (1, 2))):
        try:
            validate_profile(u)
        except ValueError:
            rejected += 1
    u = ((3, 2, 1), (1, 2, 3))
    rounds = rounds_for(2, 3, (0,))
    for bad in (((0, 1), (1, 2), (0, 0)), ((0, 0), (0, 1), (1, 2)), ((0, 0),)):
        try:
            validate_witness(u, rounds, bad)
        except ValueError:
            rejected += 1
    assert rejected == 6
    assert not ef1(((10, 9, 1), (0, 0, 0)), (1, 1, 0))
    assert not exchange((0, 0, 1), (0, 0, 1))
    assert not exchange((0, 0, 1), (0, 1, 1))
    print("failure boundaries: 6 invalid inputs rejected; unfair state and non-exchanges rejected")


def general_checks():
    from arbitrary_few_final import braid_example, path as general_path
    from general_construct import check_route, read_instance

    rng = Random(2026112057)
    cases = [json.loads(Path(__file__).with_name("general_example.json").read_text())]
    for n, q, r in ((4, 0, 2), (4, 2, 0), (5, 2, 1), (5, 2, 2),
                    (4, 1, 3), (8, 2, 5), (10, 3, 8)):
        u, a, b, final = braid_example(n, q, r)
        labels = rng.sample(range(n), n)
        cases.append({
            "utilities": [[str(Fraction(v, 7)) for v in u[labels.index(i)]] for i in range(n)],
            "final_recipients": [labels[i] for i in final],
            "start": [[labels[i], g] for i, g in a],
            "target": [[labels[i], g] for i, g in b],
        })

    for n, q, r in ((3, 2, 1), (4, 2, 0), (4, 2, 2), (5, 1, 2),
                    (5, 2, 1), (5, 2, 3)):
        m = n*q+r
        u = [[rng.randrange(9) for _ in range(m)] for _ in range(n)]
        final = rng.sample(range(n), r)

        def witness():
            order = []
            for _ in range(q):
                order.extend(rng.sample(range(n), n))
            order.extend(rng.sample(final, r))
            remaining, result = set(range(m)), []
            for i in order:
                best = max(u[i][g] for g in remaining)
                g = rng.choice([g for g in sorted(remaining) if u[i][g] == best])
                remaining.remove(g)
                result.append([i, g])
            return result

        cases.append({"utilities": u, "final_recipients": final,
                      "start": witness(), "target": witness()})

    states = swaps = longest = 0
    for index, data in enumerate(cases):
        u, final, a, b = read_instance(data)
        route = general_path(u, a, b, final)
        result = check_route(u, final, a, b, route)
        states += len(route)
        swaps += result["swaps"]
        longest = max(longest, result["swaps"])
        if index == 0:
            assert result["swaps"] == 2
            greedy = picking_outcomes(u, rounds_for(len(u), len(u[0]), final))
            assert any(state not in greedy for state in route)
            print("supplied general example: " + " -> ".join("".join(map(str, state)) for state in route))
    print(f"general endpoints: {len(cases)} cases, {states} states, {swaps} exchanges, "
          f"longest tested path {longest}; no/full/five/eight-final and rational labelled cases")


if __name__ == "__main__":
    four_goods()
    two_agent_checks()
    failure_boundaries()
    general_checks()
    print("PASS: exact finite checks support the implementations; the universal theorem rests on proof.md")
