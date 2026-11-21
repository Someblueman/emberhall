"""Signed-reflection partitions beyond arithmetic progressions; standard library only.

See UNEQUAL_SPACING.md for the gcd criterion and its exact template scope.
"""
from __future__ import annotations

import argparse
from itertools import permutations, product
import json
from math import gcd
import sys

from middle_prefix import formal_identity
from published_cases import check_pair, validate_lengths


def parameters(a: int, m: int, c: int) -> tuple[int, int]:
    validate_lengths((a, m, c))
    if a % 2 == m % 2 or c % 2 or a <= m:
        raise ValueError("require a > m of opposite parity and positive even c")
    period = a - m
    return period, gcd(period, c - m)


def reflection_word(a: int, m: int, c: int) -> tuple[int, ...]:
    """Solve the two reflection equations, including disconnected components."""
    period, divisor = parameters(a, m, c)
    if (m + 1) % divisor:
        raise ValueError("gcd does not divide m+1: no word in this reflection template")
    word = [0] * period
    for root in range(period):
        if word[root]:
            continue
        word[root] = -1
        pending = [root]
        while pending:
            j = pending.pop()
            neighbours = (((m - j) % period, 1),
                          ((c - j) % period, -1 if ((c - j) // period) % 2 else 1))
            for k, factor in neighbours:
                value = factor * word[j]
                if word[k] == 0:
                    word[k] = value
                    pending.append(k)
                elif word[k] != value:
                    raise ArithmeticError("gcd criterion admitted inconsistent reflections")
    return tuple(word)


def full_partition(a: int, m: int, c: int) -> dict:
    """Construct a full partition when a,m have opposite parity and c is even."""
    period, divisor = parameters(a, m, c)
    word = reflection_word(a, m, c)
    signs = {(0, 0): 1}
    signs.update({(1, p): word[p % period] for p in range(1, a + 1)})
    signs.update({(2, p): -word[p % period] for p in range(1, m + 1)})
    signs.update({(3, p): (1 if (p // period) % 2 else -1) * word[p % period]
                  for p in range(1, c + 1)})
    left = sorted(v for v, s in signs.items() if s == 1)
    right = sorted(v for v, s in signs.items() if s == -1)
    result = check_pair((a, m, c), left, right)
    if not result["homometric"] or 2 * result["size"] != 1 + a + m + c:
        raise ArithmeticError("signed-reflection partition failed its exact check")
    return {**result, "lengths": (a, m, c), "left": left, "right": right,
            "period": period, "gcd": divisor,
            "construction": "unequal-spacing signed reflections"}


def prefix_witness(lengths: object) -> dict:
    """Choose the largest supported prefix pair with at most three tip omissions.

    This enumerates 20 prefix shapes and six arm orders, never vertex subsets.
    A refusal is only a limitation of this constructor.
    """
    lengths = validate_lengths(lengths)
    for omitted_count in range(4):
        for trim in product(range(4), repeat=3):
            if sum(trim) != omitted_count:
                continue
            retained = tuple(n - t for n, t in zip(lengths, trim))
            if min(retained) < 1:
                continue
            for order in permutations(range(3)):
                a, m, c = (retained[i] for i in order)
                if a % 2 == m % 2 or c % 2 or a <= m:
                    continue
                if (m + 1) % gcd(a - m, c - m):
                    continue
                full = full_partition(a, m, c)
                left, right = ([v if v == (0, 0) else (order[v[0] - 1] + 1, v[1])
                                for v in full[side]] for side in ("left", "right"))
                result = check_pair(lengths, left, right)
                omitted = [(i + 1, p) for i, (n, t) in enumerate(zip(lengths, trim))
                           for p in range(n - t + 1, n + 1)]
                return {**result, "lengths": lengths, "retained_lengths": retained,
                        "left": sorted(left), "right": sorted(right), "omitted": omitted,
                        "template_order": tuple(i + 1 for i in order),
                        "period": full["period"], "gcd": full["gcd"],
                        "construction": full["construction"]}
    raise ValueError("no supported reflection prefix; this is not a bound on other pairs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lengths", nargs="*", type=int)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--prove", action="store_true")
    args = parser.parse_args()
    if args.prove:
        if args.lengths or args.summary:
            parser.error("--prove takes no lengths or --summary")
        if formal_identity():
            raise ArithmeticError("nonzero universal Laurent residual")
        print("PASS: universal Laurent reduction; gcd existence proof in UNEQUAL_SPACING.md")
        return 0
    if len(args.lengths) != 3:
        parser.error("give three arm lengths, or --prove")
    try:
        result = prefix_witness(args.lengths)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.summary:
        result = {k: v for k, v in result.items()
                  if k not in {"left", "right", "left_profile", "right_profile", "difference"}}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
