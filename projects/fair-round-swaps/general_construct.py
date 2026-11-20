"""Construct or recheck an EF1 exchange path for supplied greedy endpoints."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

from swaps import allocation, ef1, exchange, rounds_for, validate_profile, validate_witness


def read_instance(data):
    """Decode the exact JSON input; validate both complete picking witnesses."""
    if not isinstance(data, dict) or set(data) != {
        "utilities", "final_recipients", "start", "target"
    }:
        raise ValueError("expected utilities, final_recipients, start and target")
    rows = data["utilities"]
    if not isinstance(rows, list) or any(not isinstance(row, list) for row in rows):
        raise ValueError("utilities must be a list of equally long lists")
    utilities = []
    for row in rows:
        values = []
        for value in row:
            if type(value) is int:
                values.append(value)
            elif isinstance(value, str):
                values.append(Fraction(value))
            else:
                raise ValueError("use integers or exact strings such as '2/7', never JSON decimals")
        utilities.append(tuple(values))
    u = tuple(utilities)
    validate_profile(u)
    final = data["final_recipients"]
    if not isinstance(final, list) or any(type(i) is not int for i in final):
        raise ValueError("final_recipients must list integer agent labels")
    final = tuple(final)
    rounds = rounds_for(len(u), len(u[0]), final)
    witnesses = []
    for name in ("start", "target"):
        witness = data[name]
        if not isinstance(witness, list) or any(
            not isinstance(pick, list) or len(pick) != 2
            or any(type(x) is not int for x in pick) for pick in witness
        ):
            raise ValueError(f"{name} must list integer [agent, good] pairs")
        witness = tuple(tuple(pick) for pick in witness)
        validate_witness(u, rounds, witness)
        witnesses.append(witness)
    return u, final, *witnesses


def check_route(u, final, start, target, owners):
    """Recompute the path's properties without consulting the constructor."""
    n, m = len(u), len(u[0])
    if not isinstance(owners, (list, tuple)) or not owners:
        raise ValueError("owners must be a nonempty list of allocations")
    if any(not isinstance(state, (list, tuple)) or len(state) != m
           or any(type(i) is not int or i not in range(n) for i in state)
           for state in owners):
        raise ValueError("each allocation must give one valid integer owner per good")
    route = [tuple(state) for state in owners]
    if route[0] != allocation(start, m) or route[-1] != allocation(target, m):
        raise ValueError("path endpoints do not match the supplied picking witnesses")
    sizes = tuple(m // n + (i in final) for i in range(n))
    trades = []
    for index, state in enumerate(route):
        if tuple(state.count(i) for i in range(n)) != sizes:
            raise ValueError(f"allocation {index} changes the bundle sizes")
        if not ef1(u, state):
            raise ValueError(f"allocation {index} is not EF1")
        if index:
            before = route[index - 1]
            if not exchange(before, state):
                raise ValueError(f"step {index} is not a single exchange")
            goods = [g for g in range(m) if before[g] != state[g]]
            trades.append({"goods": goods, "agents": [before[g] for g in goods]})
    return {
        "agents_and_goods_are_zero_based": True,
        "final_recipients": final,
        "sizes": sizes,
        "swaps": len(trades),
        "owners": route,
        "exchanges": trades,
        "verified": ["greedy input endpoints", "same size vector", "single exchanges", "EF1"],
        "scope": "Intermediate allocations need not be picking outcomes; no shortest-path guarantee.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="preferences and two complete picking orders")
    parser.add_argument("--verify", type=Path, help="recheck the owners in a saved output instead of constructing")
    args = parser.parse_args()
    try:
        u, final, start, target = read_instance(json.loads(args.instance.read_text(encoding="utf-8")))
        if args.verify is not None:
            saved = json.loads(args.verify.read_text(encoding="utf-8"))
            if not isinstance(saved, dict) or "owners" not in saved:
                raise ValueError("saved output must contain owners")
            owners = saved["owners"]
        else:
            from arbitrary_few_final import path
            owners = path(u, start, target, final)
        result = check_route(u, final, start, target, owners)
    except (OSError, ValueError, ZeroDivisionError, RecursionError) as error:
        parser.error(str(error))
    except ModuleNotFoundError as error:
        parser.error(f"missing constructor prerequisite {error.name}; see GENERAL_INPUT.md")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
