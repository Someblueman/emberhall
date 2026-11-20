"""Exact four-agent paths after an incomplete final round; read FOUR_AGENTS.md."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

from four_agent_lift import path as two_final_path
from four_agent_one_final import path as one_final_path
from near_complete import path as near_complete_path
from swaps import allocation, ef1, exchange, rounds_for, validate_profile


def read_instance(data):
    if not isinstance(data, dict) or set(data) != {"utilities", "final_recipients", "start", "target"}:
        raise ValueError("expected utilities, final_recipients, start and target")
    rows = data["utilities"]
    if not isinstance(rows, list) or len(rows) != 4 or any(not isinstance(row, list) for row in rows):
        raise ValueError("utilities must contain four lists")
    u = []
    for row in rows:
        values = []
        for value in row:
            if type(value) is int:
                values.append(value)
            elif isinstance(value, str):
                values.append(Fraction(value))
            else:
                raise ValueError("use exact integers or fraction strings, not JSON decimals")
        u.append(tuple(values))
    u = tuple(u)
    validate_profile(u)
    m = len(u[0])
    if m < 5 or m % 4 == 0:
        raise ValueError("need at least one complete round and an incomplete final round")
    final = data["final_recipients"]
    if (not isinstance(final, list) or len(final) != m % 4
            or any(type(i) is not int or i not in range(4) for i in final)
            or len(set(final)) != len(final)):
        raise ValueError("final_recipients must name the distinct agents receiving extra goods")
    witnesses = []
    for name in ("start", "target"):
        w = data[name]
        if not isinstance(w, list) or any(not isinstance(p, list) or len(p) != 2
                                        or any(type(x) is not int for x in p) for p in w):
            raise ValueError(f"{name} must contain integer [agent, good] pairs")
        witnesses.append(tuple(tuple(p) for p in w))
    return u, tuple(sorted(final)), *witnesses


def construct(data):
    u, final, start, target = read_instance(data)
    m = len(u[0])
    order = final + tuple(i for i in range(4) if i not in final)
    labels = {old: new for new, old in enumerate(order)}
    mapped_u = tuple(u[i] for i in order)
    try:
        a = tuple((labels[i], g) for i, g in start)
        b = tuple((labels[i], g) for i, g in target)
    except KeyError as error:
        raise ValueError("witness names an unknown agent") from error
    if len(final) == 1:
        result = one_final_path(mapped_u, a, b)
        method = "four-agent 4q+1 proof; finite graph reference constructor"
    elif len(final) == 2:
        result = two_final_path(mapped_u, a, b)
        method = "four-agent 4q+2 proof; recursive constructor"
    else:
        rounds = rounds_for(4, m, (0, 1, 2))
        result = [allocation(w, m) for w in near_complete_path(mapped_u, rounds, a, b)]
        method = "near-complete-round proof; recursive constructor"
    result = [tuple(order[i] for i in state) for state in result]
    if (result[0] != allocation(start, m) or result[-1] != allocation(target, m)
            or not all(ef1(u, state) for state in result)
            or not all(exchange(a, b) for a, b in zip(result, result[1:]))):
        raise AssertionError("constructed route failed endpoint, fairness or exchange validation")
    return {"agents_and_goods_are_zero_based": True, "swaps": len(result) - 1,
            "owners": result, "method": method,
            "sizes": [result[0].count(i) for i in range(4)],
            "verified": ["greedy endpoints", "fixed sizes", "EF1", "single exchanges"]}


def example(remainder):
    m = 4 + remainder
    final = {1: [2], 2: [1, 3], 3: [0, 2, 3]}[remainder]
    def witness(first, last):
        return [[i, g] for g, i in enumerate(first + last)]
    return {"utilities": [list(range(m, 0, -1)) for _ in range(4)],
            "final_recipients": final, "start": witness([0, 1, 2, 3], final),
            "target": witness([3, 2, 1, 0], list(reversed(final)))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="JSON with utilities, final recipients and two witnesses")
    source.add_argument("--example", type=int, choices=(1, 2, 3), help="run a built-in exact example")
    args = parser.parse_args()
    try:
        data = example(args.example) if args.example is not None else json.loads(args.input.read_text())
        result = construct(data)
    except (OSError, ValueError, ZeroDivisionError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
