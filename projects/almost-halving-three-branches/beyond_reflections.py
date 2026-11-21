"""All-colouring restrictions beyond the reflection template; standard library.

See BEYOND_REFLECTIONS.md. This does not construct the requested infinite family.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
from math import gcd

from progression_partitions import root_elimination_residuals
from published_cases import check_pair, validate_lengths


def full_partition_obstruction(lengths: object) -> dict:
    """A necessary residue-parity condition, never an existence certificate."""
    lengths = validate_lengths(lengths)
    order = 1 + sum(lengths)
    modulus = gcd(lengths[0] - lengths[1], lengths[1] - lengths[2])
    # Equal lengths admit every modulus; this one gives a useful obstruction.
    modulus = modulus or lengths[0] + 1
    residue = lengths[0] % modulus
    common = gcd(residue, modulus)
    quotient_sum = sum(n // modulus for n in lengths)
    reason = None
    if order % 2:
        reason = "odd order"
    elif residue and common > 1:
        reason = "equal residue sums would have opposite parities"
    elif residue and (residue != modulus - 1 or quotient_sum % 2 == 0):
        reason = "a required zero residue sum contains an odd number of signs"
    return {
        "lengths": lengths, "order": order, "modulus": modulus,
        "residue": residue, "residue_gcd": common,
        "quotient_sum": quotient_sum, "full_partition_ruled_out": reason is not None,
        "reason": reason, "existence_certified": False,
    }


def family_certificate(t: int) -> dict:
    if type(t) is not int or t < 0:
        raise ValueError("t must be a nonnegative integer")
    lengths = tuple(n + 5320 * t for n in (91, 71, 15))
    prefixes = []
    for trim in product(range(3), repeat=3):
        if sum(trim) not in (0, 2):
            continue
        retained = tuple(n - d for n, d in zip(lengths, trim))
        prefixes.append({"trim": trim, **full_partition_obstruction(retained)})
    upper_bound = 88 + 7980 * t
    return {
        "parameter": t, "lengths": lengths, "target": upper_bound,
        "upper_bound_over_all_pairs": upper_bound,
        "target_existence": "proved at t=0; unresolved here for t>0",
        "necessary_two_hole_condition": "both depths have the same parity",
        "prefixes": prefixes,
        "prefixes_not_ruled_out": [p["trim"] for p in prefixes
                                  if not p["full_partition_ruled_out"]],
    }


def seed_witness() -> dict:
    """Mallow's finite t=0 witness, independently recounted by this module's tests."""
    words = (
        "++---++++------++++------++---++-----++------++++"
        "--------++---++---++------++++---++---++-",
        "+++++----+++--+++--++++++----++++++++--+++--+++--++++++----+++--+++--+",
        "----++++++--+++",
    )
    left, right = [(0, 0)], []
    for arm, word in enumerate(words, 1):
        for depth, sign in enumerate(word, 1):
            (left if sign == "+" else right).append((arm, depth))
    lengths = (91, 71, 15)
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or checked["size"] != 88:
        raise ArithmeticError("the finite seed failed its exact distance check")
    return {**checked, "lengths": lengths, "left": left, "right": right,
            "construction": "Mallow's finite t=0 witness; no extrapolation"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", nargs="?", type=int)
    parser.add_argument("--witness", action="store_true")
    parser.add_argument("--prove", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.t is not None or args.witness:
            parser.error("--prove takes no parameter or --witness")
        if any(root_elimination_residuals()):
            raise ArithmeticError("root elimination identity failed")
        print("PASS: exact root elimination; universal arguments in BEYOND_REFLECTIONS.md")
        return 0
    if args.t is None:
        parser.error("give a nonnegative t, or --prove")
    if args.t < 0 or (args.witness and args.t != 0):
        parser.error("t must be nonnegative; a witness is available only for t=0")
    print(json.dumps(seed_witness() if args.witness else family_certificate(args.t),
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
