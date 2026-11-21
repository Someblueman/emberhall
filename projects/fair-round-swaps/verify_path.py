"""Independently check a saved fair-exchange path using exact item deletions.

Standard library only: no constructor, shared allocation model, or search code.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path


def _profile(data: object) -> tuple[tuple[Fraction, ...], ...]:
    if (not isinstance(data, list) or len(data) < 2
            or any(not isinstance(row, list) or not row for row in data)
            or any(len(row) != len(data[0]) for row in data)):
        raise ValueError("utilities need at least two equally long nonempty rows")
    rows = []
    for row in data:
        values = []
        for value in row:
            if type(value) is not int and not isinstance(value, str):
                raise ValueError("utilities must be integers or exact rational strings")
            try:
                exact = Fraction(value)
            except (ValueError, ZeroDivisionError) as error:
                raise ValueError("invalid rational utility") from error
            if exact < 0:
                raise ValueError("utilities must be nonnegative")
            values.append(exact)
        rows.append(tuple(values))
    return tuple(rows)


def _witness(data: object, u: tuple[tuple[Fraction, ...], ...],
             final: list[int], name: str) -> list[int]:
    n, m = len(u), len(u[0])
    if not isinstance(data, list) or len(data) != m:
        raise ValueError(f"{name} must contain exactly one pick per good")
    remaining = set(range(m))
    owners = [-1] * m
    allowed: set[int] = set()
    for step, pick in enumerate(data):
        if not isinstance(pick, list) or len(pick) != 2 or any(type(x) is not int for x in pick):
            raise ValueError(f"{name} picks must be integer [agent, good] pairs")
        if not allowed:
            allowed = set(range(n)) if step < (m // n) * n else set(final)
        agent, good = pick
        if agent not in allowed:
            raise ValueError(f"{name} pick {step} violates the round schedule")
        if good not in remaining:
            raise ValueError(f"{name} pick {step} repeats or names an unknown good")
        if any(u[agent][other] > u[agent][good] for other in remaining):
            raise ValueError(f"{name} pick {step} is not a utility maximizer")
        owners[good] = agent
        allowed.remove(agent)
        remaining.remove(good)
    return owners


def _fair(u: tuple[tuple[Fraction, ...], ...], state: list[int], index: int) -> None:
    bundles = [[g for g, owner in enumerate(state) if owner == agent]
               for agent in range(len(u))]
    for observer, row in enumerate(u):
        own = sum((row[g] for g in bundles[observer]), Fraction(0))
        for target, bundle in enumerate(bundles):
            # Literal EF1 definition, without a largest-item formula or pair shortcut.
            if bundle and not any(
                own >= sum((row[g] for g in bundle if g != removed), Fraction(0))
                for removed in bundle
            ):
                raise ValueError(f"allocation {index} is not EF1: observer {observer}, target {target}")


def verify(instance: object, saved: object) -> dict:
    """Validate a finite certificate; return freshly computed facts or raise ValueError."""
    if not isinstance(instance, dict) or set(instance) != {
        "utilities", "final_recipients", "start", "target"
    }:
        raise ValueError("instance needs utilities, final_recipients, start and target")
    u = _profile(instance["utilities"])
    n, m = len(u), len(u[0])
    final = instance["final_recipients"]
    if (not isinstance(final, list) or len(final) != m % n
            or any(type(i) is not int or not 0 <= i < n for i in final)
            or len(set(final)) != len(final)):
        raise ValueError("final_recipients must name exactly m modulo n distinct agents")
    start = _witness(instance["start"], u, final, "start")
    target = _witness(instance["target"], u, final, "target")
    if not isinstance(saved, dict) or not isinstance(saved.get("owners"), list) or not saved["owners"]:
        raise ValueError("path needs a nonempty owners list")
    route = saved["owners"]
    for state in route:
        if (not isinstance(state, list) or len(state) != m
                or any(type(i) is not int or not 0 <= i < n for i in state)):
            raise ValueError("each allocation must give one valid integer owner per good")
    if route[0] != start or route[-1] != target:
        raise ValueError("path endpoints disagree with the picking witnesses")
    sizes = [m // n + (i in final) for i in range(n)]
    trades = []
    for index, state in enumerate(route):
        if [state.count(i) for i in range(n)] != sizes:
            raise ValueError(f"allocation {index} changes the labelled bundle sizes")
        _fair(u, state, index)
        if index:
            before = route[index - 1]
            changed = [g for g in range(m) if before[g] != state[g]]
            if len(changed) != 2:
                raise ValueError(f"step {index} must exchange exactly two goods")
            x, y = changed
            if before[x] != state[y] or before[y] != state[x]:
                raise ValueError(f"step {index} must exchange goods between their two owners")
            trades.append({"goods": changed, "agents": [before[x], before[y]]})
    if "exchanges" in saved:
        declared = saved["exchanges"]
        if not isinstance(declared, list) or len(declared) != len(trades):
            raise ValueError("exchanges must describe every step exactly once")
        for index, (given, actual) in enumerate(zip(declared, trades)):
            if (not isinstance(given, dict) or set(given) != {"goods", "agents"}
                    or any(not isinstance(given[k], list) or len(given[k]) != 2
                           or any(type(x) is not int for x in given[k]) for k in ("goods", "agents"))
                    or len(set(given["goods"])) != 2
                    or dict(zip(given["goods"], given["agents"]))
                    != dict(zip(actual["goods"], actual["agents"]))):
                raise ValueError(f"exchange {index} disagrees with the owner changes")
    return {
        "valid": True, "agents": n, "goods": m, "allocations": len(route),
        "swaps": len(trades), "sizes": sizes, "exchanges": trades,
        "supplied_exchanges_checked": "exchanges" in saved,
        "checked": ["both complete greedy endpoint witnesses", "labelled sizes",
                    "every EF1 allocation by literal item deletion", "every single exchange"],
        "scope": "This finite path only; no intermediate greedy or universal connectivity claim.",
    }


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read(path: Path) -> object:
    def nonfinite(value: str) -> None:
        raise ValueError(f"not a JSON number: {value}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
                      parse_constant=nonfinite)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path, help="instance JSON, or a combined certificate")
    parser.add_argument("path", type=Path, nargs="?", help="saved path JSON with owners")
    args = parser.parse_args()
    try:
        data = _read(args.instance)
        if args.path is None:
            if not isinstance(data, dict) or set(data) != {"instance", "path"}:
                raise ValueError("a combined certificate needs exactly instance and path")
            instance, saved = data["instance"], data["path"]
        else:
            instance, saved = data, _read(args.path)
        result = verify(instance, saved)
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
