#!/usr/bin/env python3
"""Three-parameter interior-hole family with c = r + 4m (odd r >= 4m - 1, m >= 1, k >= 0).

Generalizes interior_hole_c_plus_4.py (m = 1) to T(r*(k+3)+4m, r*(k+2)+4m-1, r+4m),
proved identically in Z[z, z^-1, R, R^-1, M, M^-1, W, W^-1] with R = z^r, M = z^(4m),
W = z^(r*k). Settles open a <= 300 Euler-cell escapes (215, 191, 31) and (227, 203, 43)
in addition to (211, 187, 27) and (235, 223, 15). Standard library only.
"""
from __future__ import annotations

import argparse
from itertools import permutations
import json
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from interior_hole_c_plus_4 import (  # noqa: E402
    _l_add,
    _l_mul,
    _l_neg,
    _l_star,
    _words_to_pair,
)
from interior_hole_three_param import (  # noqa: E402
    _distance_profile,
    check_pair,
    classify_euler_escapes,
    validate_lengths,
)


def validate_c_plus_4m(r: int, m: int, k: int) -> tuple[int, int, int]:
    """Validate m >= 1, odd r >= 4*m - 1 (and r >= 5), k >= 0."""
    if type(m) is not int or m < 1:
        raise ValueError("m must be a positive integer")
    if type(r) is not int or r % 2 == 0 or r < max(5, 4 * m - 1):
        raise ValueError(f"r must be an odd integer >= {max(5, 4 * m - 1)}")
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    return r, m, k


def _c_plus_4m_words(r: int, m: int, k: int) -> tuple[str, str, str]:
    alt = "+-" * ((r - 1) // 2)
    rev_alt = "-+" * ((r - 1) // 2)
    b1 = "-+" * (2 * m - 1) + "-" + "+" * (r - (4 * m - 1))
    b2 = "-+" * (2 * m - 1) + "-" * (r - (4 * m - 1)) + "+"
    t1 = "-+" * (2 * m - 1) + "--"
    t2 = "-+" * (2 * m - 1) + "+"
    w1 = alt + "0" + b1 * (k + 1) + t1 + alt + "0"
    w2 = alt + "++" + b2 * k + t2 + rev_alt
    w3 = "+-" * (2 * m - 1) + "+" + "-" * (r - (4 * m - 2)) + "+-" * (2 * m - 1) + "+"
    return w1, w2, w3


def construct_c_plus_4m(r: int, m: int, k: int, summary: bool = False) -> dict:
    """Construct and recount the (r, m, k) witness on T(r*(k+3)+4m, r*(k+2)+4m-1, r+4m)."""
    r, m, k = validate_c_plus_4m(r, m, k)
    w1, w2, w3 = _c_plus_4m_words(r, m, k)
    expected = [r * (k + 3) + 4 * m, r * (k + 2) + 4 * m - 1, r + 4 * m]
    res = _words_to_pair(expected, (w1, w2, w3), summary)
    return {"r": r, "m": m, "c": r + 4 * m, "k": k, **res}


def _c_plus_4m_residual(
    s0_val: int = -1,
    include_hole: bool = True,
    corrupt_block: bool = False,
) -> dict:
    ONE = {(0, 0, 0, 0): 1}
    Z = {(1, 0, 0, 0): 1}
    ZINV = {(-1, 0, 0, 0): 1}
    R = {(0, 1, 0, 0): 1}
    RINV = {(0, -1, 0, 0): 1}
    M = {(0, 0, 1, 0): 1}
    W = {(0, 0, 0, 1): 1}
    Z2R = {(2, 1, 0, 0): 1}

    omz = _l_add(ONE, _l_neg(Z))
    opz = _l_add(ONE, Z)
    omR = _l_add(ONE, _l_neg(R))
    D = _l_mul(_l_mul(omz, opz), omR)

    N_alt = _l_mul(omz, _l_mul(omR, _l_add(Z, _l_neg(R))))
    b1_num = {(1, 0, 0, 0): -1, (2, 0, 0, 0): 1, (1, 0, 1, 0): 2, (1, 1, 0, 0): -1, (2, 1, 0, 0): -1}
    if corrupt_block:
        b1_num = _l_add(b1_num, _l_mul({(1, 0, 0, 0): 2}, _l_mul(omz, opz)))
    t1_num = _l_mul(omR, {(1, 0, 0, 0): -1, (2, 0, 0, 0): 1, (0, 0, 1, 0): -2, (1, 0, 1, 0): 1, (2, 0, 1, 0): 1})
    N1 = _l_add(
        N_alt,
        _l_mul(R, _l_mul(b1_num, _l_add(ONE, _l_neg(_l_mul(R, W))))),
        _l_mul(_l_mul(R, R), _l_mul(W, t1_num)),
        _l_mul(_l_mul(R, R), _l_mul(M, _l_mul(W, N_alt))),
    )

    b2_num = {(1, 0, 0, 0): -1, (2, 0, 0, 0): 1, (0, 0, 1, 0): -2, (0, 1, 0, 0): 2, (1, 1, 0, 0): 1, (2, 1, 0, 0): -1}
    if corrupt_block:
        b2_num = _l_add(b2_num, _l_mul({(1, 0, 0, 0): -2}, _l_mul(omz, opz)))
    t2_num = _l_mul(omR, {(1, 0, 0, 0): -1, (2, 0, 0, 0): 1, (-1, 0, 1, 0): 2, (0, 0, 1, 0): -1, (1, 0, 1, 0): -1})
    rz = _l_mul(R, Z)
    N2 = _l_add(
        N_alt,
        _l_mul(D, _l_mul(R, _l_add(ONE, Z))),
        _l_mul(rz, _l_mul(b2_num, _l_add(ONE, _l_neg(W)))),
        _l_mul(rz, _l_mul(W, t2_num)),
        _l_neg(_l_mul(_l_mul(R, _l_mul(M, W)), N_alt)),
    )

    N3 = _l_mul(omR, {(1, 0, 0, 0): 1, (2, 0, 0, 0): -1, (1, 0, 1, 0): -2, (2, 1, 0, 0): 2, (1, 1, 1, 0): 1, (2, 1, 1, 0): -1})

    E1 = _l_mul(_l_mul(R, _l_mul(R, R)), _l_mul(M, W))
    E2 = _l_mul(_l_mul(R, R), _l_mul(M, _l_mul(W, ZINV)))
    E3 = _l_mul(R, M)
    s0 = {(0, 0, 0, 0): s0_val}

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


def _specialize_4var(poly: dict, r: int, m: int, k: int) -> dict:
    out: dict[int, int] = {}
    for (ez, er, em, ew), c in poly.items():
        e = ez + er * r + em * (4 * m) + ew * (r * k)
        out[e] = out.get(e, 0) + c
    return {e: c for e, c in out.items() if c}


def prove_c_plus_4m_laurent() -> dict:
    """Verify D*E == 0 in Z[z,z^-1,R,R^-1,M,M^-1,W,W^-1] and check corruptions."""
    clean = _c_plus_4m_residual(s0_val=-1, include_hole=True, corrupt_block=False)
    corrupt_s0 = _c_plus_4m_residual(s0_val=1, include_hole=True, corrupt_block=False)
    corrupt_hole = _c_plus_4m_residual(s0_val=-1, include_hole=False, corrupt_block=False)
    corrupt_block = _c_plus_4m_residual(s0_val=-1, include_hole=True, corrupt_block=True)

    # Check specialization of corrupt_s0 at (r=7, m=2, k=1) against actual distance profile difference
    r_val, m_val, k_val = 7, 2, 1
    w1, w2, w3 = _c_plus_4m_words(r_val, m_val, k_val)
    lengths = [len(w1), len(w2), len(w3)]
    left: list[tuple[int, int]] = [(0, 0)]
    right: list[tuple[int, int]] = []
    for arm, w in ((1, w1), (2, w2), (3, w3)):
        for d, ch in enumerate(w, 1):
            if ch == '+':
                left.append((arm, d))
            elif ch == '-':
                right.append((arm, d))
    lp = _distance_profile(left)
    rp = _distance_profile(right)
    spec = _specialize_4var(corrupt_s0, r_val, m_val, k_val)
    D_1d = {0: 1, 2: -1, r_val: -1, r_val + 2: 1}
    diff_poly = {d: lp[d] - rp[d] for d in lp.keys() | rp.keys() if lp[d] != rp[d]}
    # Compare against 2 * (z^-1 - 1) * (D_left - D_right) * D - 2 * (|L| - |R|) * D
    rhs_poly: dict[int, int] = {}
    for e_d, c_d in diff_poly.items():
        for e_z, c_z in ((-1, 2), (0, -2)):
            for e_D, c_D in D_1d.items():
                e = e_d + e_z + e_D
                rhs_poly[e] = rhs_poly.get(e, 0) + c_d * c_z * c_D
    imb = len(left) - len(right)
    for e_D, c_D in D_1d.items():
        rhs_poly[e_D] = rhs_poly.get(e_D, 0) - 2 * imb * c_D
    rhs_poly = {e: c for e, c in rhs_poly.items() if c}
    spec_ok = (spec == rhs_poly)

    if clean or not corrupt_s0 or not corrupt_hole or not corrupt_block or not spec_ok:
        raise ArithmeticError("Laurent proof or sensitivity check failed")

    return {
        "proof": "PASS",
        "residual_terms": len(clean),
        "corrupt_s0_terms": len(corrupt_s0),
        "corrupt_hole_terms": len(corrupt_hole),
        "corrupt_block_terms": len(corrupt_block),
        "specialization_matches_difference": spec_ok,
    }


def _relabel_arm(arm: int, perm: tuple[int, int, int]) -> int:
    return 0 if arm == 0 else perm[arm - 1]


def c_plus_4m_params(lengths: list[int]) -> tuple[tuple[int, int, int], int, int, int] | None:
    """Return (perm, r, m, k) if lengths match T(r*(k+3)+4m, r*(k+2)+4m-1, r+4m)."""
    for perm in permutations((1, 2, 3)):
        a, b, c = (lengths[i - 1] for i in perm)
        r = a - b - 1
        if r < 5 or r % 2 == 0:
            continue
        diff_c = c - r
        if diff_c < 4 or diff_c % 4 != 0:
            continue
        m = diff_c // 4
        if r < 4 * m - 1:
            continue
        if (b - c + 1) % r != 0:
            continue
        k = (b - c + 1) // r - 1
        if k < 0:
            continue
        return perm, r, m, k
    return None


def solve_tree(lengths: object, summary: bool = False) -> dict:
    """Match an arbitrary triple (up to arm permutation) to the (r, m, k) family."""
    lens = validate_lengths(lengths)
    matched = c_plus_4m_params(lens)
    if matched is None:
        raise ValueError(f"lengths {lens} do not belong to the c = r + 4m family")
    perm, r, m, k = matched
    w = construct_c_plus_4m(r, m, k, summary=False)
    left = sorted([_relabel_arm(arm, perm), d] for arm, d in w["left"])
    right = sorted([_relabel_arm(arm, perm), d] for arm, d in w["right"])
    omitted = sorted([_relabel_arm(arm, perm), d] for arm, d in w["omitted"])
    checked = check_pair(lens, left, right)
    out = {
        "r": r,
        "m": m,
        "c": r + 4 * m,
        "k": k,
        "arm_order": list(perm),
        "omitted": omitted,
        **checked,
    }
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = left
    out["right"] = right
    return out


def audit_escapes(max_a: int = 300) -> dict:
    """Filter interior_hole_three_param's Euler-cell escapes by the c = r + 4m family."""
    base = classify_euler_escapes(max_a=max_a)
    settled = []
    still_open = []
    for triple in base["remaining_open_triples"]:
        if c_plus_4m_params(triple) is not None:
            settled.append(triple)
        else:
            still_open.append(triple)
    return {
        "max_a": max_a,
        "prior_remaining_count": base["remaining_open_count"],
        "newly_settled_by_c_plus_4m": settled,
        "remaining_open_count": len(still_open),
        "remaining_open_triples": still_open,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--witness", nargs=3, type=int, metavar=("R", "M", "K"))
    mode.add_argument("--tree", nargs=3, type=int, metavar=("A", "B", "C"))
    mode.add_argument("--audit-escapes", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--max-a", type=int, default=300)
    args = parser.parse_args()
    try:
        if args.prove:
            out = prove_c_plus_4m_laurent()
        elif args.witness is not None:
            out = construct_c_plus_4m(*args.witness, summary=args.summary)
        elif args.tree is not None:
            out = solve_tree(args.tree, summary=args.summary)
        else:
            out = audit_escapes(max_a=args.max_a)
        print(json.dumps(out, sort_keys=True))
        return 0
    except ValueError as err:
        parser.error(str(err))


if __name__ == "__main__":
    raise SystemExit(main())
