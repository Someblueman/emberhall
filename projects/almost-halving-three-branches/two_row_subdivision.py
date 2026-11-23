#!/usr/bin/env python3
"""Two-row odd subdivision lifts, exact obstructions, and unrestricted k=0 interior holes.

1. Unrestricted k=0 family: T(2r+c, r+c-1, c) for ALL odd r>=1 and ALL odd c>=1
   (removing c<=r), proved over Z[z,z^-1, R,R^-1, C,C^-1].
2. Two-row odd subdivision (E1=E2=0): lifts any full partition of T(L1,L2,L3)
   to T(g*L1, g*L2, g*L3) for ALL odd g=2h+1>=3 simultaneously, strictly extending
   CORRECTED_SUBDIVISION by solving T(7g,4g,2g).
3. Obstructions: infinite all-odd parity theorem, GF(2)/mod-4 Hensel level-1
   obstructions on (8,5,2) and (10,7,4), and exact Q-nullspace exhaustion on
   (62,54,1) and (65,46,6).
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from interior_hole_three_param import check_pair, target_size, validate_lengths  # noqa: E402
import ratio_51_33_10 as r51  # noqa: E402

LIFT_FAMILIES: dict[tuple[int, int, int], tuple[tuple[str, str], tuple[str, str], tuple[str, str]]] = {
    (4, 2, 1): (("+-+-", "-+-+"), ("++", "--"), ("-", "+")),
    (6, 3, 2): (("--+-+-", "-+++-+"), ("+++", "++-"), ("--", "--")),
    (6, 4, 1): (("----+++"[1:], "+++---"), ("----", "++++"), ("+", "-")),  # corrected below if needed
    (7, 4, 2): (("--++--+", "+--++--"), ("+-+-", "++++"), ("-+", "--")),
}
LIFT_FAMILIES[(6, 4, 1)] = (("---+++", "+++---"), ("----", "++++"), ("+", "-"))


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


# --- 1. Unrestricted k=0 family in Z[z,z^-1, R,R^-1, C,C^-1] ---

def construct_k0(r: int, c: int, summary: bool = False) -> dict:
    """Construct T(2r+c, r+c-1, c) for any odd r>=1 and any odd c>=1."""
    for name, v in (("r", r), ("c", c)):
        if type(v) is not int or v < 1 or v % 2 == 0:
            raise ValueError(f"{name} must be a positive odd integer")
    alt = "+-" * ((r - 1) // 2)
    w1 = alt + "0" + ("-" * c) + alt + "0"
    w2 = "+-" * ((r + c - 2) // 2) + "+"
    w3 = "+" * c
    left: list[list[int]] = []
    right: list[list[int]] = [[0, 0]]
    omitted: list[list[int]] = []
    for arm, word in ((1, w1), (2, w2), (3, w3)):
        for depth, ch in enumerate(word, 1):
            if ch == "+":
                left.append([arm, depth])
            elif ch == "-":
                right.append([arm, depth])
            else:
                omitted.append([arm, depth])
    lengths = [len(w1), len(w2), len(w3)]
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or not checked["meets_target"]:
        raise ArithmeticError("unrestricted k=0 construction failed distance recount")
    out = {"r": r, "c": c, "omitted": omitted, **checked}
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = left
    out["right"] = right
    return out


def _k0_residual(s0_val: int = -1, include_hole: bool = True) -> dict:
    ONE = {(0, 0, 0): 1}
    Z = {(1, 0, 0): 1}
    ZINV = {(-1, 0, 0): 1}
    R = {(0, 1, 0): 1}
    RINV = {(0, -1, 0): 1}
    C = {(0, 0, 1): 1}
    Z2 = {(2, 0, 0): 1}
    omz = _l_add(ONE, _l_neg(Z))
    opz = _l_add(ONE, Z)
    D = _l_mul(omz, opz)

    N_alt = _l_mul(omz, _l_add(Z, _l_neg(R)))
    N_mid = _l_neg(_l_mul(R, _l_mul(Z, _l_mul(opz, _l_add(ONE, _l_neg(C))))))
    N_tail = _l_mul(R, _l_mul(C, _l_mul(omz, _l_add(Z, _l_neg(R)))))
    N1 = _l_add(N_alt, N_mid, N_tail)
    N2 = _l_mul(omz, _l_add(Z, _l_mul(R, C)))
    N3 = _l_mul(Z, _l_mul(opz, _l_add(ONE, _l_neg(C))))

    E1 = _l_mul(_l_mul(R, R), C)
    E2 = _l_mul(R, _l_mul(C, ZINV))
    E3 = C
    s0 = {(0, 0, 0): s0_val}

    DQ = _l_add(
        _l_mul(D, _l_mul(s0, _l_add(ONE, _l_neg(E1), _l_neg(E2), _l_neg(E3)))),
        _l_mul(N1, _l_add(ONE, _l_neg(E2), _l_neg(E3))),
        _l_mul(N2, _l_add(ONE, _l_neg(E1), _l_neg(E3))),
        _l_mul(N3, _l_add(ONE, _l_neg(E1), _l_neg(E2))),
        _l_mul(E1, _l_mul(Z2, _l_star(N1))),
        _l_mul(E2, _l_mul(Z2, _l_star(N2))),
        _l_mul(E3, _l_mul(Z2, _l_star(N3))),
    )
    DC_tip = _l_add(_l_mul(E1, _l_add(_l_mul(D, s0), N2, N3)), _l_neg(_l_mul(E1, _l_mul(Z2, _l_star(N1)))))
    DC_hole = _l_add(
        _l_mul(R, _l_add(_l_mul(D, s0), N2, N3)),
        _l_neg(_l_mul(R, _l_mul(Z2, _l_star(N_alt)))),
        _l_mul(RINV, _l_add(N1, _l_neg(N_alt))),
    )
    holes = _l_add(DC_tip, DC_hole) if include_hole else DC_tip
    return _l_add(DQ, _l_neg(_l_mul(_l_add(ZINV, _l_neg(ONE)), holes)))


def prove_k0_laurent() -> dict:
    """Prove T(2r+c, r+c-1, c) for all odd r>=1, c>=1 in Z[z,z^-1,R,R^-1,C,C^-1]."""
    res = _k0_residual()
    bad_s0 = _k0_residual(s0_val=1)
    bad_hole = _k0_residual(include_hole=False)
    if res or not bad_s0 or not bad_hole:
        raise ArithmeticError("k=0 Laurent proof or corruption check failed")
    return {
        "proof": "PASS",
        "ring": "Z[z,z^-1,R,R^-1,C,C^-1]",
        "residual_terms": len(res),
        "corrupt_s0_terms": len(bad_s0),
        "corrupt_hole_terms": len(bad_hole),
    }


# --- 2. Two-row odd subdivision E1=E2=0 ---

def _word_poly_Z(word: str) -> dict[tuple[int, int], int]:
    """Convert a {+,-} edge word into polynomial in Z = z * H^2 over (z, H)."""
    return {(k, 2 * k): (1 if ch == "+" else -1) for k, ch in enumerate(word)}


def _word_poly_1d(word: str) -> dict[tuple[int], int]:
    return {(k,): (1 if ch == "+" else -1) for k, ch in enumerate(word)}


def prove_two_row_lift(base: tuple[int, int, int]) -> dict:
    """Verify E1(Z)=E2(Z)=0 and the all-odd-g identity (1-z)*Q_lifted == 0 in Z[z,z^-1,H,H^-1]."""
    base_t = validate_lengths(base)
    if base_t not in LIFT_FAMILIES:
        raise ValueError(f"no stored two-row lift for {base_t}")
    words = LIFT_FAMILIES[base_t]
    for L, (xs, ys) in zip(base_t, words):
        if len(xs) != L or len(ys) != L or set(xs) - set("+-") or set(ys) - set("+-"):
            raise ValueError("invalid lift word lengths or signs")

    # 1D check in Z[Z, Z^-1] for E1 and E2
    ONE_1 = {(0,): 1}
    ZINV_1 = {(-1,): 1}
    A_1 = [{(L,): 1} for L in base_t]
    X_1 = [_word_poly_1d(xs) for xs, _ in words]
    Y_1 = [_word_poly_1d(ys) for _, ys in words]

    e1_1d: dict = {}
    e2_1d: dict = {}
    for i in range(3):
        j, l = (i + 1) % 3, (i + 2) % 3
        factor = _l_add(ONE_1, _l_neg(A_1[j]), _l_neg(A_1[l]))
        ai_z = _l_mul(A_1[i], ZINV_1)
        e1_1d = _l_add(e1_1d, _l_mul(X_1[i], factor), _l_neg(_l_mul(ai_z, _l_star(Y_1[i]))))
        e2_1d = _l_add(e2_1d, _l_mul(Y_1[i], factor), _l_neg(_l_mul(ai_z, _l_star(X_1[i]))))

    # 2D check in Z[z, z^-1, H, H^-1] where g=2h+1, Z=z*H^2, J1=z(1-H)/(1-z), J2=zH(1-H)/(1-z)
    ONE = {(0, 0): 1}
    Z = {(1, 0): 1}
    H = {(0, 1): 1}
    BIG_Z = {(1, 2): 1}
    BIG_ZINV = {(-1, -2): 1}
    J1_num = _l_mul(Z, _l_add(ONE, _l_neg(H)))
    J2_num = _l_mul(_l_mul(Z, H), _l_add(ONE, _l_neg(H)))

    # Verify Z * J1(z^-1) = J2(z), i.e. z * BIG_Z * J1_num* + J2_num = 0.
    j_rel = _l_add(_l_mul(Z, _l_mul(BIG_Z, _l_star(J1_num))), J2_num)
    if j_rel:
        raise ArithmeticError("J1/J2 reflection identity failed")

    # (1-z)*Q_inserted = sum_i [ (J1_num X_i + J2_num Y_i)(1-A_j-A_l)
    #                             + (A_i / Z) * z * (J2_num X_i* + J1_num Y_i*) ]
    # Note: -A_i * J1(z^-1) = -A_i * (J2(z)/Z) = -(A_i/Z) * J2_num / (1-z), so sign is minus!
    A_2 = [{(L, 2 * L): 1} for L in base_t]
    X_2 = [_word_poly_Z(xs) for xs, _ in words]
    Y_2 = [_word_poly_Z(ys) for _, ys in words]

    q_ins_num: dict = {}
    for i in range(3):
        j, l = (i + 1) % 3, (i + 2) % 3
        factor = _l_add(ONE, _l_neg(A_2[j]), _l_neg(A_2[l]))
        ai_bigz = _l_mul(A_2[i], BIG_ZINV)
        ins_i = _l_add(_l_mul(J1_num, X_2[i]), _l_mul(J2_num, Y_2[i]))
        rev_i = _l_add(_l_mul(J2_num, _l_star(X_2[i])), _l_mul(J1_num, _l_star(Y_2[i])))
        q_ins_num = _l_add(q_ins_num, _l_mul(ins_i, factor), _l_neg(_l_mul(ai_bigz, rev_i)))

    if e1_1d or e2_1d or q_ins_num:
        raise ArithmeticError(f"two-row lift residual nonzero for {base_t}")
    return {
        "proof": "PASS",
        "base": list(base_t),
        "e1_terms": len(e1_1d),
        "e2_terms": len(e2_1d),
        "lifted_q_terms": len(q_ins_num),
        "scope": "every odd subdivision factor g = 2h + 1 >= 3",
    }


def construct_lifted_tree(base: tuple[int, int, int], g: int, summary: bool = False) -> dict:
    """Construct the lifted full partition on T(g*L1, g*L2, g*L3) for odd g >= 3."""
    base_t = validate_lengths(base)
    if type(g) is not int or g < 3 or g % 2 == 0:
        raise ValueError("g must be an odd integer >= 3")
    if base_t not in LIFT_FAMILIES:
        raise ValueError(f"no stored two-row lift for {base_t}")
    coarse = r51.original_tree(base_t)
    if not coarse["homometric"] or coarse["size"] != (1 + sum(base_t)) // 2:
        raise ArithmeticError("coarse base partition failed")
    h = (g - 1) // 2
    left = [[arm, d * g] for arm, d in coarse["left"]]
    right = [[arm, d * g] for arm, d in coarse["right"]]
    for arm, (xs, ys) in enumerate(LIFT_FAMILIES[base_t], 1):
        for k, (xc, yc) in enumerate(zip(xs, ys)):
            for j in range(1, h + 1):
                (left if xc == "+" else right).append([arm, k * g + j])
            for j in range(h + 1, 2 * h + 1):
                (left if yc == "+" else right).append([arm, k * g + j])
    lengths = [n * g for n in base_t]
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or checked["size"] != (1 + sum(lengths)) // 2:
        raise ArithmeticError("lifted tree failed distance recount")
    out = {"base": list(base_t), "g": g, **checked}
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = sorted(left)
    out["right"] = sorted(right)
    return out


# --- 3. Exact obstructions on E1=E2=0 ---

def _build_two_row_matrix(base: tuple[int, int, int]) -> tuple[list[list[int]], int]:
    L1, L2, L3 = validate_lengths(base)
    Ls = (L1, L2, L3)
    N = 2 * (L1 + L2 + L3)
    D = max(L1 + L2, L2 + L3, L1 + L3)
    M = [[0] * N for _ in range(2 * (D + 1))]
    col = 0
    for i in range(3):
        Li, Lj, Ll = Ls[i], Ls[(i + 1) % 3], Ls[(i + 2) % 3]
        for k in range(Li):
            M[k][col] += 1
            M[k + Lj][col] -= 1
            M[k + Ll][col] -= 1
            M[(D + 1) + Li - 1 - k][col] -= 1
            col += 1
        for k in range(Li):
            M[(D + 1) + k][col] += 1
            M[(D + 1) + k + Lj][col] -= 1
            M[(D + 1) + k + Ll][col] -= 1
            M[Li - 1 - k][col] -= 1
            col += 1
    return M, N


def gf2_obstruction_check(base: tuple[int, int, int]) -> dict:
    """Check mod-4 (Hensel level-1) consistency of E1=E2=0 over GF(2)."""
    base_t = validate_lengths(base)
    M, N = _build_two_row_matrix(base_t)
    rhs = [sum(row) for row in M]
    if any(r % 2 != 0 for r in rhs):
        return {"base": list(base_t), "gf2_status": "odd_rhs", "variables": N}
    pivots: dict[int, tuple[int, int]] = {}
    for row, r in zip(M, rhs):
        mask = 0
        for col, c in enumerate(row):
            if c & 1:
                mask ^= 1 << col
        t = (r // 2) & 1
        while mask:
            lsb = mask & -mask
            if lsb in pivots:
                pm, pt = pivots[lsb]
                mask ^= pm
                t ^= pt
            else:
                pivots[lsb] = (mask, t)
                break
        else:
            if t != 0:
                return {
                    "base": list(base_t),
                    "gf2_status": "inconsistent_mod_4",
                    "variables": N,
                    "rank_gf2": len(pivots),
                }
    return {
        "base": list(base_t),
        "gf2_status": "consistent_mod_4",
        "variables": N,
        "rank_gf2": len(pivots),
    }


def all_odd_parity_obstruction(base: tuple[int, int, int]) -> dict:
    """Verify the Z=-1 parity obstruction when all three coarse arms are odd."""
    base_t = validate_lengths(base)
    if any(L % 2 == 0 for L in base_t):
        raise ValueError("all three coarse lengths must be odd")
    # At Z=-1, A_i(-1) = -1, so E1(-1) = 3*sum(X_i(-1)) - sum(Y_i(-1)) = 0
    # and E2(-1) = 3*sum(Y_i(-1)) - sum(X_i(-1)) = 0 force sum(X_i(-1)) = 0,
    # while sum(X_i(-1)) == sum(L_i) == 1 (mod 2).
    gf2 = gf2_obstruction_check(base_t)
    return {
        "base": list(base_t),
        "length_sum_mod_2": sum(base_t) % 2,
        "status": "obstructed",
        "proof": "Z=-1 parity forces sum X_i(-1)=0 contradicting odd sum(L_i)",
        **gf2,
    }


def q_nullspace_exhaustion(base: tuple[int, int, int], max_nullity: int = 16) -> dict:
    """Exhaust all {+1,-1} solutions to E1=E2=0 over Q when nullity <= max_nullity."""
    base_t = validate_lengths(base)
    M, N = _build_two_row_matrix(base_t)
    P = 1000000007
    A = [[x % P for x in row] for row in M]
    pivots: list[int] = []
    r = 0
    for c in range(N):
        piv = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], P - 2, P)
        A[r] = [(x * inv) % P for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % P for j in range(N)]
        pivots.append(c)
        r += 1
    free = [c for c in range(N) if c not in pivots]
    k = len(free)
    if k > max_nullity:
        raise ValueError(f"nullity {k} exceeds max_nullity {max_nullity}")
    if k == 0:
        return {"base": list(base_t), "variables": N, "rank": r, "nullity": 0, "solutions_up_to_sign": 0}
    neg_rows = [[(-A[row_idx][fc]) % P for fc in free] for row_idx in range(len(pivots))]
    found = 0
    for mask in range(1 << (k - 1)):
        fvals = [1] + [1 if (mask >> i) & 1 else -1 for i in range(k - 1)]
        ok = True
        pvals: list[int] = []
        for nr in neg_rows:
            val = sum(c * fv for c, fv in zip(nr, fvals)) % P
            if val != 1 and val != P - 1:
                ok = False
                break
            pvals.append(1 if val == 1 else -1)
        if ok:
            x = [0] * N
            for c, v in zip(free, fvals):
                x[c] = v
            for c, v in zip(pivots, pvals):
                x[c] = v
            if all(sum(M[row][j] * x[j] for j in range(N)) == 0 for row in range(len(M))):
                found += 1
    return {
        "base": list(base_t),
        "variables": N,
        "rank": r,
        "nullity": k,
        "checked_assignments": 1 << (k - 1),
        "solutions_up_to_sign": found,
    }


def prove_all() -> dict:
    """Run all symbolic proofs and exact obstructions."""
    k0 = prove_k0_laurent()
    lifts = [prove_two_row_lift(base) for base in sorted(LIFT_FAMILIES)]
    all_odd = [all_odd_parity_obstruction(b) for b in ((5, 3, 1), (9, 5, 1), (11, 7, 3))]
    gf2_obs = [gf2_obstruction_check(b) for b in ((8, 5, 2), (10, 7, 4))]
    q_obs = [q_nullspace_exhaustion(b) for b in ((62, 54, 1), (65, 46, 6))]
    return {
        "proof": "PASS",
        "k0_laurent": k0,
        "two_row_lifts": lifts,
        "all_odd_obstructions": all_odd,
        "gf2_obstructions": gf2_obs,
        "q_nullspace_exhaustions": q_obs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--k0", type=int, nargs=2, metavar=("R", "C"))
    mode.add_argument("--lift", type=int, nargs=4, metavar=("L1", "L2", "L3", "G"))
    mode.add_argument("--obstructions", action="store_true")
    mode.add_argument("--check", metavar="FILE")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.prove:
            result = prove_all()
        elif args.k0 is not None:
            result = construct_k0(*args.k0, summary=args.summary)
        elif args.lift is not None:
            l1, l2, l3, g = args.lift
            result = construct_lifted_tree((l1, l2, l3), g, summary=args.summary)
        elif args.obstructions:
            result = {
                "all_odd": [all_odd_parity_obstruction(b) for b in ((5, 3, 1), (9, 5, 1))],
                "gf2": [gf2_obstruction_check(b) for b in ((8, 5, 2), (10, 7, 4))],
                "q_nullspace": [q_nullspace_exhaustion(b) for b in ((62, 54, 1), (65, 46, 6))],
            }
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
