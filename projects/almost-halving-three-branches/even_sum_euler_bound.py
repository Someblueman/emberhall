#!/usr/bin/env python3
"""Universal c=1,2 even-sum halving and CRT structure of 13-trim Euler-cell escapes.

1. For every positive triple (a, b, c) with a + b + c even and c in {1, 2},
   omitting arm 3 (and one endpoint when c = 2) yields two isometric path halves
   of size (a + b + c) // 2 - 1 + ... = floor((1 + a + b + c) / 2) - 1.
2. For c >= 3 and even a + b + c, proves that no prime p >= 5 can cover two of
   the 13 shifted difference pairs (u + du, v + dv), that {2, 3} leaves at least
   6 shifts uncovered (forcing at least 6 distinct primes >= 5 and CRT modulus
   >= 9,699,690), and verifies zero escapes for 1 <= u, v <= max_uv.
3. Exhibits and checks T(1932211, 1377448, 7), where all 13 Euler-cell trims fail.
"""
from __future__ import annotations

import argparse
from itertools import permutations
import json
from math import gcd
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from interior_hole_three_param import check_pair, validate_lengths  # noqa: E402

TRIMS_13 = tuple(
    (d1, d2, d3)
    for d1 in range(4)
    for d2 in range(4)
    for d3 in range(4)
    if d1 + d2 + d3 in (1, 3)
)
SHIFTS_13 = tuple((-d1 + d2, -d2 + d3) for d1, d2, d3 in TRIMS_13)
SMALLEST_FOUND_ESCAPE = (1932211, 1377448, 7)


def construct_c12_even_sum(a: int, b: int, c: int, summary: bool = False) -> dict:
    """Construct target-sized isometric path halves when a+b+c is even and c in {1, 2}."""
    lengths = validate_lengths((a, b, c))
    if (a + b + c) % 2 != 0:
        raise ValueError("a + b + c must be even")
    if c not in (1, 2):
        raise ValueError("c must be 1 or 2")
    # Build the path along arms 1 and 2, omitting arm 3 (and (1, a) when c == 2).
    a_used = a if c == 1 else a - 1
    path = [[1, d] for d in range(a_used, 0, -1)] + [[0, 0]] + [[2, d] for d in range(1, b + 1)]
    half = len(path) // 2
    if len(path) != 2 * half:
        raise ArithmeticError("expected even retained path length")
    left = path[:half]
    right = path[half:]
    omitted = [[3, d] for d in range(1, c + 1)] + ([[1, a]] if c == 2 else [])
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or not checked["meets_target"]:
        raise ArithmeticError("c=1,2 path-halving failed recount")
    out: dict = {"omitted": omitted, **checked}
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = left
    out["right"] = right
    return out


def _crt_pair(a1: int, m1: int, a2: int, m2: int) -> tuple[int, int]:
    inv = pow(m1, -1, m2)
    return (a1 + m1 * (((a2 - a1) * inv) % m2)) % (m1 * m2), m1 * m2


def prove_prime_shift_bound() -> dict:
    """Verify the 13-shift prime-covering bound and minimum 6-prime CRT uv sum."""
    # Any prime p >= 5 covering two shifts i != j must divide (du_i - du_j) and (dv_i - dv_j).
    # All |du_i - du_j| <= 6 and |dv_i - dv_j| <= 6, so only p = 5 can ever divide a nonzero diff.
    p_ge_5_pairs = []
    for i in range(len(SHIFTS_13)):
        for j in range(i + 1, len(SHIFTS_13)):
            dx = abs(SHIFTS_13[i][0] - SHIFTS_13[j][0])
            dy = abs(SHIFTS_13[i][1] - SHIFTS_13[j][1])
            if (dx == 0 or dx == 5) and (dy == 0 or dy == 5):
                p_ge_5_pairs.append((i, j, dx, dy))
    if p_ge_5_pairs:
        raise ArithmeticError(f"unexpected pair divisible by p>=5: {p_ge_5_pairs}")

    max_p2 = max(
        sum(1 for du, dv in SHIFTS_13 if (u + du) % 2 == 0 and (v + dv) % 2 == 0)
        for u in range(2)
        for v in range(2)
    )
    max_p3 = max(
        sum(1 for du, dv in SHIFTS_13 if (u + du) % 3 == 0 and (v + dv) % 3 == 0)
        for u in range(3)
        for v in range(3)
    )

    min_uncovered = len(SHIFTS_13)
    best_6_uv: tuple[int, int, int] | None = None
    primes = (5, 7, 11, 13, 17, 19)
    for u2 in range(2):
        for v2 in range(2):
            c2 = {i for i, (du, dv) in enumerate(SHIFTS_13) if (u2 + du) % 2 == 0 and (v2 + dv) % 2 == 0}
            for u3 in range(3):
                for v3 in range(3):
                    c3 = {i for i, (du, dv) in enumerate(SHIFTS_13) if (u3 + du) % 3 == 0 and (v3 + dv) % 3 == 0}
                    rem = sorted(set(range(len(SHIFTS_13))) - (c2 | c3))
                    min_uncovered = min(min_uncovered, len(rem))
                    if len(rem) == 6:
                        for ps in permutations(primes):
                            u, m = _crt_pair(u2, 2, u3, 3)
                            v, _ = _crt_pair(v2, 2, v3, 3)
                            for idx, p in zip(rem, ps):
                                du, dv = SHIFTS_13[idx]
                                u, m = _crt_pair(u, m, (-du) % p, p)
                                v, _ = _crt_pair(v, m // p, (-dv) % p, p)
                            if u == 0:
                                u += m
                            if v == 0:
                                v += m
                            if best_6_uv is None or (u + v) < best_6_uv[0]:
                                best_6_uv = (u + v, u, v)

    return {
        "proof": "PASS",
        "max_shifts_covered_by_p2": max_p2,
        "max_shifts_covered_by_p3": max_p3,
        "max_shifts_covered_by_p_ge_5": 1,
        "min_uncovered_after_2_and_3": min_uncovered,
        "min_crt_modulus_6_primes": 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19,
        "min_uv_sum_6_primes_5_to_19": best_6_uv[0],
        "min_uv_pair_6_primes_5_to_19": [best_6_uv[1], best_6_uv[2]],
    }


def _cell_admitted(n1: int, n2: int, n3: int) -> bool:
    if (n1 + n2 + n3) % 2 != 0 or n1 == n2 == n3:
        return False
    g = gcd(n1 - n2, n2 - n3)
    return (n1 % g == 0) and (((n1 + n2 + n3) // g) % 2 == 0)


def audit_small_range(max_uv: int = 1500) -> dict:
    """Check directly that all 1<=u,v<=max_uv fail to cover all 13 shifts."""
    if type(max_uv) is not int or max_uv < 1:
        raise ValueError("max_uv must be positive")
    escapes = 0
    for u in range(1, max_uv + 1):
        for v in range(1, max_uv + 1):
            all_gt1 = True
            for du, dv in SHIFTS_13:
                x, y = u + du, v + dv
                if x == 0 and y == 0:
                    continue
                if gcd(x, y) == 1:
                    all_gt1 = False
                    break
            if all_gt1:
                escapes += 1
    return {"max_uv": max_uv, "escapes_found": escapes}


def verify_thirteen_trim_escape(a: int, b: int, c: int) -> dict:
    """Verify in O(1) arithmetic whether all 13 Euler-cell trims fail on even-sum T(a,b,c)."""
    validate_lengths((a, b, c))
    if (a + b + c) % 2 != 0 or c < 3:
        raise ValueError("require even a+b+c and c >= 3")
    rows = []
    any_admitted = False
    for d1, d2, d3 in TRIMS_13:
        n1, n2, n3 = a - d1 + 1, b - d2 + 1, c - d3 + 1
        g = gcd(n1 - n2, n2 - n3)
        admitted = _cell_admitted(n1, n2, n3)
        if admitted:
            any_admitted = True
        if n1 == n2 == n3:
            reason = "equal_cells"
        elif n1 % g != 0:
            reason = f"{g}_not_dividing_{n1}"
        elif ((n1 + n2 + n3) // g) % 2 != 0:
            reason = f"odd_quotient_sum_over_{g}"
        else:
            reason = "admitted"
        rows.append({
            "trim": [d1, d2, d3],
            "cells": [n1, n2, n3],
            "gcd": g,
            "admitted": admitted,
            "reason": reason,
        })
    return {
        "lengths": [a, b, c],
        "order": 1 + a + b + c,
        "status": "admitted" if any_admitted else "all_13_trims_obstructed",
        "trims": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--verify-escape", action="store_true")
    mode.add_argument("--c12", type=int, nargs=3, metavar=("A", "B", "C"))
    mode.add_argument("--check", metavar="FILE")
    parser.add_argument("--max-uv", type=int, default=1500)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.prove:
            result = {
                "proof": "PASS",
                "prime_shift_bound": prove_prime_shift_bound(),
                "small_range_audit": audit_small_range(args.max_uv),
                "smallest_escape_check": verify_thirteen_trim_escape(*SMALLEST_FOUND_ESCAPE),
            }
        elif args.verify_escape:
            result = verify_thirteen_trim_escape(*SMALLEST_FOUND_ESCAPE)
        elif args.c12 is not None:
            result = construct_c12_even_sum(*args.c12, summary=args.summary)
        else:
            raw = sys.stdin.read() if args.check == "-" else Path(args.check).read_text(encoding="utf-8")
            data = json.loads(raw)
            result = check_pair(data["lengths"], data["left"], data["right"])
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as err:
        print(json.dumps({"error": str(err)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("homometric", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
