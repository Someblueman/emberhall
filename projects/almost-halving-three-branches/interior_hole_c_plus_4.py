#!/usr/bin/env python3
"""Interior-hole families with c = r + 4 (all odd r >= 5) and period-7 c = 15.

1. Two-parameter family T(r*(k+3)+4, r*(k+2)+3, r+4) for all odd r >= 5 and k >= 0,
   proved over Z[z,z^-1, R,R^-1, W,W^-1] (R = z^r, W = z^(r*k)), settling
   (211, 187, 27) and (235, 223, 15).
2. Companion period-7 family T(22+7k, 14+7k, 15) for all k >= 0, proved over
   Z[z,z^-1, W,W^-1] (W = z^(7k)).
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import permutations
import json
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from interior_hole_three_param import check_pair, validate_lengths  # noqa: E402


def _l_add(*polys: dict) -> dict:
    out: Counter = Counter()
    for p in polys:
        for mon, coeff in p.items():
            if coeff:
                out[mon] += coeff
    return {mon: coeff for mon, coeff in out.items() if coeff}


def _l_neg(p: dict) -> dict:
    return {mon: -coeff for mon, coeff in p.items()}


def _l_mul(a: dict, b: dict) -> dict:
    out: Counter = Counter()
    for ma, va in a.items():
        for mb, vb in b.items():
            out[tuple(x + y for x, y in zip(ma, mb))] += va * vb
    return {mon: coeff for mon, coeff in out.items() if coeff}


def _l_star(p: dict) -> dict:
    return {tuple(-x for x in mon): coeff for mon, coeff in p.items()}


def _words_to_pair(lengths_expected: list[int], words: tuple[str, str, str], summary: bool) -> dict:
    left: list[list[int]] = []
    right: list[list[int]] = [[0, 0]]
    omitted: list[list[int]] = []
    for arm, word in enumerate(words, 1):
        for depth, ch in enumerate(word, 1):
            if ch == "+":
                left.append([arm, depth])
            elif ch == "-":
                right.append([arm, depth])
            else:
                omitted.append([arm, depth])
    lengths = [len(w) for w in words]
    if lengths != lengths_expected:
        raise ArithmeticError(f"unexpected word lengths {lengths} vs {lengths_expected}")
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or not checked["meets_target"]:
        raise ArithmeticError("construction failed distance recount")
    out: dict = {"omitted": omitted, **checked}
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = left
    out["right"] = right
    return out


# --- 1. c = r + 4 family: T(r*(k+3)+4, r*(k+2)+3, r+4) ---

def construct_c_plus_4(r: int, k: int, summary: bool = False) -> dict:
    """Construct the (r, k) witness on T(r*(k+3)+4, r*(k+2)+3, r+4) for odd r>=5, k>=0."""
    if type(r) is not int or r < 5 or r % 2 == 0:
        raise ValueError("r must be an odd integer >= 5")
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    alt = "+-" * ((r - 1) // 2)
    rev_alt = "-+" * ((r - 1) // 2)
    b1 = "-+-" + "+" * (r - 3)
    b2s = "-+" + "-" * (r - 3) + "+"
    w1 = alt + "0" + b1 * (k + 1) + "-+--" + alt + "0"
    w2 = alt + "++" + b2s * k + "-++" + rev_alt
    w3 = "+-+" + "-" * (r - 2) + "+-+"
    res = _words_to_pair([r * (k + 3) + 4, r * (k + 2) + 3, r + 4], (w1, w2, w3), summary)
    return {"r": r, "c": r + 4, "k": k, **res}


def _c_plus_4_residual(
    s0_val: int = -1,
    include_hole: bool = True,
    corrupt_block: bool = False,
) -> dict:
    ONE = {(0, 0, 0): 1}
    Z = {(1, 0, 0): 1}
    ZINV = {(-1, 0, 0): 1}
    R = {(0, 1, 0): 1}
    RINV = {(0, -1, 0): 1}
    W = {(0, 0, 1): 1}
    Z2R = {(2, 1, 0): 1}

    omz = _l_add(ONE, _l_neg(Z))
    opz = _l_add(ONE, Z)
    omR = _l_add(ONE, _l_neg(R))
    D = _l_mul(_l_mul(omz, opz), omR)

    N_alt = _l_mul(omz, _l_mul(omR, _l_add(Z, _l_neg(R))))
    b1_num = _l_add(
        _l_mul({(1, 0, 0): -1, (2, 0, 0): 1, (3, 0, 0): -1}, _l_mul(omz, opz)),
        _l_mul(_l_add({(4, 0, 0): 1}, _l_neg(_l_mul(Z, R))), opz),
    )
    if corrupt_block:
        b1_num = _l_add(b1_num, _l_mul({(1, 0, 0): 2}, _l_mul(omz, opz)))

    N1 = _l_add(
        N_alt,
        _l_mul(R, _l_mul(b1_num, _l_add(ONE, _l_neg(_l_mul(R, W))))),
        _l_mul(_l_mul(_l_mul(R, R), W), _l_mul(D, {(1, 0, 0): -1, (2, 0, 0): 1, (3, 0, 0): -1, (4, 0, 0): -1})),
        _l_mul(_l_mul(_l_mul(R, R), W), _l_mul({(4, 0, 0): 1}, N_alt)),
    )

    b2s_num = _l_add(
        _l_mul({(1, 0, 0): -1, (2, 0, 0): 1}, _l_mul(omz, opz)),
        _l_neg(_l_mul(_l_add({(3, 0, 0): 1}, _l_neg(R)), opz)),
        _l_mul(R, _l_mul(omz, opz)),
    )
    if corrupt_block:
        # Flip corresponding shifted sign in b2s (-z^2? Keep single-side flip to test residual sensitivity).
        b2s_num = _l_add(b2s_num, _l_mul({(1, 0, 0): -2}, _l_mul(omz, opz)))

    rz = _l_mul(R, Z)
    N2 = _l_add(
        N_alt,
        _l_mul(D, _l_mul(R, _l_add(ONE, Z))),
        _l_mul(rz, _l_mul(b2s_num, _l_add(ONE, _l_neg(W)))),
        _l_mul(_l_mul(rz, W), _l_mul(D, {(1, 0, 0): -1, (2, 0, 0): 1, (3, 0, 0): 1})),
        _l_neg(_l_mul(_l_mul(rz, _l_mul({(3, 0, 0): 1}, W)), N_alt)),
    )

    N3 = _l_add(
        _l_mul(D, _l_add({(1, 0, 0): 1, (2, 0, 0): -1, (3, 0, 0): 1},
                         _l_mul(rz, {(1, 0, 0): 1, (2, 0, 0): -1, (3, 0, 0): 1}))),
        _l_neg(_l_mul(_l_mul(opz, omR), _l_add({(4, 0, 0): 1}, _l_neg(_l_mul(R, {(2, 0, 0): 1}))))),
    )

    E1 = _l_mul(_l_mul(R, R), _l_mul(W, _l_mul(R, {(4, 0, 0): 1})))
    E2 = _l_mul(_l_mul(R, R), _l_mul(W, {(3, 0, 0): 1}))
    E3 = _l_mul(R, {(4, 0, 0): 1})
    s0 = {(0, 0, 0): s0_val}

    DQ = _l_add(
        _l_mul(D, _l_mul(s0, _l_add(ONE, _l_neg(E1), _l_neg(E2), _l_neg(E3)))),
        _l_mul(N1, _l_add(ONE, _l_neg(E2), _l_neg(E3))),
        _l_mul(N2, _l_add(ONE, _l_neg(E1), _l_neg(E3))),
        _l_mul(N3, _l_add(ONE, _l_neg(E1), _l_neg(E2))),
        _l_neg(_l_mul(E1, _l_mul(Z2R, _l_star(N1)))),
        _l_neg(_l_mul(E2, _l_mul(Z2R, _l_star(N2)))),
        _l_neg(_l_mul(E3, _l_mul(Z2R, _l_star(N3)))),
    )
    DC_tip = _l_add(_l_mul(E1, _l_add(_l_mul(D, s0), N2, N3)), _l_mul(E1, _l_mul(Z2R, _l_star(N1))))
    DC_hole = _l_add(
        _l_mul(R, _l_add(_l_mul(D, s0), N2, N3)),
        _l_mul(R, _l_mul(Z2R, _l_star(N_alt))),
        _l_mul(RINV, _l_add(N1, _l_neg(N_alt))),
    )
    holes = _l_add(DC_tip, DC_hole) if include_hole else DC_tip
    return _l_add(DQ, _l_neg(_l_mul(_l_add(ZINV, _l_neg(ONE)), holes)))


def prove_c_plus_4_laurent() -> dict:
    """Verify D*E == 0 in Z[z,z^-1,R,R^-1,W,W^-1] for T(r*(k+3)+4, r*(k+2)+3, r+4)."""
    res = _c_plus_4_residual()
    bad_s0 = _c_plus_4_residual(s0_val=1)
    bad_hole = _c_plus_4_residual(include_hole=False)
    bad_block = _c_plus_4_residual(corrupt_block=True)
    if res or not bad_s0 or not bad_hole or not bad_block:
        raise ArithmeticError("c=r+4 Laurent proof or corruption control failed")
    return {
        "proof": "PASS",
        "ring": "Z[z,z^-1,R,R^-1,W,W^-1]",
        "residual_terms": len(res),
        "corrupt_s0_terms": len(bad_s0),
        "corrupt_hole_terms": len(bad_hole),
        "corrupt_block_terms": len(bad_block),
    }


# --- 2. Companion period-7 family: T(22+7k, 14+7k, 15) ---

def construct_period7_c15(k: int, summary: bool = False) -> dict:
    """Construct T(22+7k, 14+7k, 15) for any integer k >= 0."""
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    w1 = "-+-++-0" + ("--+-++-" * (k + 2)) + "0"
    w2 = "++-+--+" * (k + 2)
    w3 = "+--+-++-++-+--+"
    res = _words_to_pair([22 + 7 * k, 14 + 7 * k, 15], (w1, w2, w3), summary)
    return {"family": "period7_c15", "k": k, **res}


def _wpoly(word: str, offset: int = 1) -> dict:
    return {(offset + i, 0): (1 if ch == "+" else -1) for i, ch in enumerate(word) if ch in "+-"}


def _period7_residual(s0_val: int = -1, include_hole: bool = True) -> dict:
    ONE = {(0, 0): 1}
    ZINV = {(-1, 0): 1}
    W = {(0, 1): 1}
    Z7 = {(7, 0): 1}
    D = _l_add(ONE, _l_neg(Z7))

    P1 = _wpoly("-+-++-", 1)
    B1 = _wpoly("--+-++-", 1)
    B2 = _l_neg(B1)
    W3 = _wpoly("+--+-++-++-+--+", 1)

    N1 = _l_add(_l_mul(D, P1), _l_mul(Z7, _l_mul(B1, _l_add(ONE, _l_neg(_l_mul({(14, 0): 1}, W))))))
    N2 = _l_mul(B2, _l_add(ONE, _l_neg(_l_mul({(14, 0): 1}, W))))
    N3 = _l_mul(D, W3)

    E1 = _l_mul({(22, 0): 1}, W)
    E2 = _l_mul({(14, 0): 1}, W)
    E3 = {(15, 0): 1}
    s0 = {(0, 0): s0_val}

    DQ = _l_add(
        _l_mul(D, _l_mul(s0, _l_add(ONE, _l_neg(E1), _l_neg(E2), _l_neg(E3)))),
        _l_mul(N1, _l_add(ONE, _l_neg(E2), _l_neg(E3))),
        _l_mul(N2, _l_add(ONE, _l_neg(E1), _l_neg(E3))),
        _l_mul(N3, _l_add(ONE, _l_neg(E1), _l_neg(E2))),
        _l_mul(E1, _l_mul(Z7, _l_star(N1))),
        _l_mul(E2, _l_mul(Z7, _l_star(N2))),
        _l_mul(E3, _l_mul(Z7, _l_star(N3))),
    )
    DC_tip = _l_add(_l_mul(E1, _l_add(_l_mul(D, s0), N2, N3)), _l_neg(_l_mul(E1, _l_mul(Z7, _l_star(N1)))))
    DC_hole = _l_add(
        _l_mul(Z7, _l_add(_l_mul(D, s0), N2, N3)),
        _l_neg(_l_mul(Z7, _l_mul(Z7, _l_star(_l_mul(D, P1))))),
        _l_mul({(-7, 0): 1}, _l_add(N1, _l_neg(_l_mul(D, P1)))),
    )
    holes = _l_add(DC_tip, DC_hole) if include_hole else DC_tip
    return _l_add(DQ, _l_neg(_l_mul(_l_add(ZINV, _l_neg(ONE)), holes)))


def prove_period7_laurent() -> dict:
    """Verify D*E == 0 in Z[z,z^-1,W,W^-1] for T(22+7k, 14+7k, 15)."""
    res = _period7_residual()
    bad_s0 = _period7_residual(s0_val=1)
    bad_hole = _period7_residual(include_hole=False)
    if res or not bad_s0 or not bad_hole:
        raise ArithmeticError("period-7 c=15 Laurent proof or corruption check failed")
    return {
        "proof": "PASS",
        "ring": "Z[z,z^-1,W,W^-1]",
        "residual_terms": len(res),
        "corrupt_s0_terms": len(bad_s0),
        "corrupt_hole_terms": len(bad_hole),
    }


def _relabel_arm(arm: int, perm: tuple[int, int, int]) -> int:
    return 0 if arm == 0 else perm[arm - 1]


def solve_tree(lengths: object, summary: bool = False) -> dict:
    """Match an arbitrary triple (up to arm permutation) to c=r+4 or period-7 c=15."""
    lens = validate_lengths(lengths)
    for perm in permutations((1, 2, 3)):
        a, b, c = lens[perm[0] - 1], lens[perm[1] - 1], lens[perm[2] - 1]
        r = a - b - 1
        w = None
        if r >= 5 and r % 2 == 1 and c == r + 4 and (b - 3) % r == 0:
            k = (b - 3) // r - 2
            if k >= 0:
                w = construct_c_plus_4(r, k, summary=False)
        elif c == 15 and a - b == 8 and (b - 14) % 7 == 0 and b >= 14:
            k = (b - 14) // 7
            w = construct_period7_c15(k, summary=False)
        if w is None:
            continue
        relabelled_left = sorted([_relabel_arm(arm, perm), d] for arm, d in w["left"])
        relabelled_right = sorted([_relabel_arm(arm, perm), d] for arm, d in w["right"])
        relabelled_omitted = sorted([_relabel_arm(arm, perm), d] for arm, d in w["omitted"])
        checked = check_pair(lens, relabelled_left, relabelled_right)
        out = {
            **{key: val for key, val in w.items() if key in ("r", "c", "k", "family")},
            "arm_order": list(perm),
            "omitted": relabelled_omitted,
            **checked,
        }
        if summary:
            out.pop("left_profile", None)
            out.pop("right_profile", None)
            return out
        out["left"] = relabelled_left
        out["right"] = relabelled_right
        return out
    raise ValueError(f"triple {list(lens)} is outside c=r+4 and period-7 c=15 families")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--witness", type=int, nargs=2, metavar=("R", "K"))
    mode.add_argument("--period7", type=int, metavar="K")
    mode.add_argument("--tree", type=int, nargs=3, metavar=("A", "B", "C"))
    mode.add_argument("--check", metavar="FILE")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.prove:
            result = {
                "proof": "PASS",
                "c_plus_4": prove_c_plus_4_laurent(),
                "period7_c15": prove_period7_laurent(),
            }
        elif args.witness is not None:
            result = construct_c_plus_4(*args.witness, summary=args.summary)
        elif args.period7 is not None:
            result = construct_period7_c15(args.period7, summary=args.summary)
        elif args.tree is not None:
            result = solve_tree(args.tree, summary=args.summary)
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
