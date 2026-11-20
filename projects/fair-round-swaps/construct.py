"""Read two picking witnesses and print a certified, exact exchange path."""

import argparse
from fractions import Fraction
import json
from pathlib import Path

from swaps import allocation, rounds_for, validate_profile
from two_agents import path


def read_instance(data):
    if not isinstance(data, dict) or set(data) != {"utilities", "final_agent", "start", "target"}:
        raise ValueError("expected utilities, final_agent, start and target")
    rows = data["utilities"]
    if not isinstance(rows, list) or any(not isinstance(row, list) for row in rows):
        raise ValueError("utilities must be a list of two lists")
    utilities = []
    for row in rows:
        values = []
        for v in row:
            if type(v) is int:
                values.append(v)
            elif isinstance(v, str):
                values.append(Fraction(v))
            else:
                raise ValueError("use integers or strings such as '2/7', never JSON decimals")
        utilities.append(tuple(values))
    u = tuple(utilities)
    validate_profile(u)
    if len(u) != 2:
        raise ValueError("the constructor is proved for exactly two agents")
    m = len(u[0])
    last = data["final_agent"]
    if m % 2:
        if type(last) is not int or last not in (0, 1):
            raise ValueError("odd length requires final_agent 0 or 1")
        final = (last,)
    else:
        if last is not None:
            raise ValueError("even length requires final_agent null")
        final = ()
    witnesses = []
    for name in ("start", "target"):
        w = data[name]
        if not isinstance(w, list) or any(
            not isinstance(p, list) or len(p) != 2 or any(type(x) is not int for x in p)
            for p in w
        ):
            raise ValueError(f"{name} must list integer [agent, good] pairs")
        witnesses.append(tuple(tuple(p) for p in w))
    return u, rounds_for(2, m, final), *witnesses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()
    try:
        u, rounds, start, target = read_instance(json.loads(args.instance.read_text()))
        witnesses = path(u, rounds, start, target)
    except (OSError, ValueError, ZeroDivisionError) as error:
        parser.error(str(error))
    print(json.dumps({
        "agents_and_goods_are_zero_based": True,
        "swaps": len(witnesses) - 1,
        "owners": [allocation(w, len(u[0])) for w in witnesses],
        "picking_witnesses": witnesses,
        "verified": ["maximizing picks", "same size vector", "single exchanges", "EF1"],
    }, indent=2))


if __name__ == "__main__":
    main()
