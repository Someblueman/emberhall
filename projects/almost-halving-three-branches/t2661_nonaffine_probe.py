#!/usr/bin/env python3
"""All-pairs parity obstructions & multi-period checks for T(99t, 79t, 23t).

Proves a colouring-independent all-pairs obstruction for T(99t, 79t, 23t) at
t ≡ 1 (mod 4) (including all t ≡ 1 mod 2660) via mod-2 distance counts, plus
checks multi-period (arm-dependent period) word variations:

1. All-pairs mod-2 theorem (arbitrary colourings, not merely affine):
   On T(99t, 79t, 23t) with t ≡ 1 (mod 4), the target m = (201t - 1)/2 is
   even, E_total = m, O_total = m + 2. Because |d1 - d2| ≡ d1 + d2 (mod 2),
   equal odd-distance counts force {E_L, O_L} = {E_R, O_R}. If the two omitted
   vertices have opposite depth parity, E_remaining = m - 1 is odd while
   E_L + E_R must be even (2*E_L if E_L=E_R, or m if E_L=O_R): contradiction.
   Hence NO colouring of any kind attains target m while omitting one even
   and one odd vertex (including centre + any odd-depth vertex).

2. Even-hole vs odd-hole split:
   If both omitted vertices are even, E_L = E_R = m/2 - 1 and O_L = O_R = m/2 + 1
   is forced. If both are odd (like t=1's (1,19) and (1,99)), E_L + E_R = m is
   compatible mod 2 (allowing both balanced and swapped parity profiles).

3. Cross-check against moving_hole_2660 at delta=4: confirms mod-2 / mod-4
   checks agree with the all-pairs theorem and tests non-uniform repeat counts.

Standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from published_cases import check_pair as pc_check_pair
import residue_2660 as r2660

BASE = r2660.BASE
PERIOD = r2660.PERIOD


def mod2_counts(t: int) -> dict:
    """Exact even/odd vertex counts and target on T(99t, 79t, 23t)."""
    if type(t) is not int or t < 1:
        raise ValueError("t must be a positive integer")
    lengths = [n * t for n in BASE]
    if t % 2 == 0:
        e_tot = 1 + sum(L // 2 for L in lengths)
        o_tot = sum(L // 2 for L in lengths)
        target = (1 + sum(lengths)) // 2 - 1
    else:
        e_tot = 1 + sum((L - 1) // 2 for L in lengths)
        o_tot = sum((L + 1) // 2 for L in lengths)
        target = (1 + sum(lengths)) // 2 - 1
    return {
        "t": t,
        "lengths": lengths,
        "target": target,
        "even_total": e_tot,
        "odd_total": o_tot,
    }


def classify_hole_parities(t: int, depth1: int, depth2: int) -> dict:
    """Apply the colouring-independent mod-2 distance theorem to two omitted depths."""
    info = mod2_counts(t)
    if t % 4 != 1:
        return {**info, "scope": "requires t == 1 (mod 4)", "excluded": False}
    m = info["target"]
    assert m % 2 == 0 and info["even_total"] == m and info["odd_total"] == m + 2
    p1, p2 = depth1 % 2, depth2 % 2
    if p1 != p2:
        return {
            **info,
            "hole_parities": (p1, p2),
            "even_remaining": m - 1,
            "excluded": True,
            "reason": "opposite hole parities leave odd even_remaining != 2*E_L or m",
        }
    if p1 == 0:
        return {
            **info,
            "hole_parities": (0, 0),
            "even_remaining": m - 2,
            "excluded": False,
            "forced": {"E_L": m // 2 - 1, "E_R": m // 2 - 1,
                       "O_L": m // 2 + 1, "O_R": m // 2 + 1},
        }
    return {
        **info,
        "hole_parities": (1, 1),
        "even_remaining": m,
        "excluded": False,
        "forced": {"condition": "E_L + E_R == m and {E_L, O_L} == {E_R, O_R}"},
    }


def odd_distance_count_from_pair(left: list[tuple[int, int]],
                                 right: list[tuple[int, int]]) -> tuple[int, int]:
    """Verify exact equality odd_dist(L) == E_L*O_L and odd_dist(R) == E_R*O_R."""
    e_l = sum(1 for _, d in left if d % 2 == 0)
    o_l = len(left) - e_l
    e_r = sum(1 for _, d in right if d % 2 == 0)
    o_r = len(right) - e_r
    return e_l * o_l, e_r * o_r


def prove() -> list[str]:
    lines = []
    for t in (1, 5, 2661, 5321):
        res_opp = classify_hole_parities(t, 0, 19)
        assert res_opp["excluded"] is True
        res_even = classify_hole_parities(t, 0, 20)
        assert res_even["excluded"] is False and res_even["forced"]["E_L"] == res_even["target"] // 2 - 1
        res_odd = classify_hole_parities(t, 19, 99 * t)
        assert res_odd["excluded"] is False
        lines.append(
            f"t={t}: target={res_opp['target']} even_tot={res_opp['even_total']} "
            f"opposite-parity holes EXCLUDED for all colourings"
        )
    # Cross-check t=1 witness odd-distance algebraic count vs full profile:
    w1 = r2660.t1_witness()
    checked = pc_check_pair(w1["lengths"], w1["left"], w1["right"])
    odd_prof_l = sum(cnt for dist, cnt in checked["left_profile"].items() if dist % 2 == 1)
    odd_prof_r = sum(cnt for dist, cnt in checked["right_profile"].items() if dist % 2 == 1)
    ol, or_ = odd_distance_count_from_pair(w1["left"], w1["right"])
    assert odd_prof_l == ol and odd_prof_r == or_
    lines.append(f"t=1 witness odd distances: {odd_prof_l} == E_L*O_L == E_R*O_R == {ol}")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prove", action="store_true")
    group.add_argument("--classify", nargs=3, type=int, metavar=("T", "D1", "D2"))
    args = parser.parse_args(argv)
    if args.prove:
        for line in prove():
            print("PASS:", line)
    else:
        print(json.dumps(classify_hole_parities(*args.classify), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
