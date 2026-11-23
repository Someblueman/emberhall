#!/usr/bin/env python3
"""Two infinite two-parameter E1=E2=0 subdivision lift families.

1. Family 1: T(2m*g, (2m-2)*g, g) for every m >= 2 and odd g >= 3,
   proved over Z[Z,Z^-1, M,M^-1] (M = Z^(2m)) together with Z[z,z^-1,H,H^-1].
2. Family 2: T((4m+3)*g, 4g, 2g) for every m >= 1 and odd g >= 3,
   proved over Z[Z,Z^-1, M,M^-1] (M = Z^(4m)).
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

from interior_hole_three_param import check_pair  # noqa: E402
import ratio_51_33_10 as r51  # noqa: E402


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


def _apply_lift(base: tuple[int, int, int], words: tuple[tuple[str, str], ...], g: int, summary: bool) -> dict:
    if type(g) is not int or g < 3 or g % 2 == 0:
        raise ValueError("g must be an odd integer >= 3")
    coarse = r51.original_tree(base)
    if not coarse["homometric"] or coarse["size"] != (1 + sum(base)) // 2:
        raise ArithmeticError("coarse partition failed")
    h = (g - 1) // 2
    left = [[arm, d * g] for arm, d in coarse["left"]]
    right = [[arm, d * g] for arm, d in coarse["right"]]
    for arm, (xs, ys) in enumerate(words, 1):
        for k, (xc, yc) in enumerate(zip(xs, ys)):
            for j in range(1, h + 1):
                (left if xc == "+" else right).append([arm, k * g + j])
            for j in range(h + 1, 2 * h + 1):
                (left if yc == "+" else right).append([arm, k * g + j])
    lengths = [n * g for n in base]
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or checked["size"] != (1 + sum(lengths)) // 2:
        raise ArithmeticError("lifted witness failed recount")
    out: dict = {"base": list(base), "g": g, **checked}
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = sorted(left)
    out["right"] = sorted(right)
    return out


def construct_family1(m: int, g: int, summary: bool = False) -> dict:
    """Construct T(2m*g, (2m-2)*g, g) for m >= 2 and odd g >= 3."""
    if type(m) is not int or m < 2:
        raise ValueError("m must be an integer >= 2")
    base = (2 * m, 2 * m - 2, 1)
    words = (("-" * (2 * m), "+-" * m), ("+" * (2 * m - 2), "-+" * (m - 1)), ("+", "+"))
    return {"family": "two_param_family1", "m": m, **_apply_lift(base, words, g, summary)}


def construct_family2(m: int, g: int, summary: bool = False) -> dict:
    """Construct T((4m+3)*g, 4g, 2g) for m >= 1 and odd g >= 3."""
    if type(m) is not int or m < 1:
        raise ValueError("m must be an integer >= 1")
    base = (4 * m + 3, 4, 2)
    words = (("--+" + "+--+" * m, "+--+" * m + "+--"), ("+-+-", "++++"), ("-+", "--"))
    return {"family": "two_param_family2", "m": m, **_apply_lift(base, words, g, summary)}


def _eval_cleared_e1_e2(
    A: list[dict],
    NX: list[dict],
    NY: list[dict],
    d_deg: int,
) -> tuple[dict, dict]:
    """Compute D*E1 and D*E2 when D = 1 - Z^d_deg (so D* = -Z^-d_deg * D)."""
    ONE = {(0, 0): 1}
    Z_shift = {(d_deg - 1, 0): 1}  # (A_i / Z) * Z^d_deg = A_i * Z^(d_deg - 1)
    e1: dict = {}
    e2: dict = {}
    for i in range(3):
        j, l = (i + 1) % 3, (i + 2) % 3
        factor = _l_add(ONE, _l_neg(A[j]), _l_neg(A[l]))
        ai_shift = _l_mul(A[i], Z_shift)
        e1 = _l_add(e1, _l_mul(NX[i], factor), _l_mul(ai_shift, _l_star(NY[i])))
        e2 = _l_add(e2, _l_mul(NY[i], factor), _l_mul(ai_shift, _l_star(NX[i])))
    return e1, e2


def family1_certificate() -> tuple:
    """Return A_i, D X_i, D Y_i and deg D; M = Z^(2m)."""
    ONE = {(0, 0): 1}
    Z = {(1, 0): 1}
    Z2 = {(2, 0): 1}
    ZINV2 = {(-2, 0): 1}
    M = {(0, 1): 1}
    opz = _l_add(ONE, Z)
    omz = _l_add(ONE, _l_neg(Z))
    D = _l_add(ONE, _l_neg(Z2))
    one_minus_M = _l_add(ONE, _l_neg(M))
    one_minus_MZ2 = _l_add(ONE, _l_neg(_l_mul(M, ZINV2)))

    A = [M, _l_mul(M, ZINV2), Z]
    NX = [_l_neg(_l_mul(opz, one_minus_M)), _l_mul(opz, one_minus_MZ2), D]
    NY = [_l_mul(omz, one_minus_M), _l_neg(_l_mul(omz, one_minus_MZ2)), D]
    return A, NX, NY, 2


def prove_family1_symbolic() -> dict:
    """Verify the parameter identity, including a nonzero corruption control."""
    A, NX, NY, degree = family1_certificate()
    D = {(0, 0): 1, (2, 0): -1}
    e1, e2 = _eval_cleared_e1_e2(A, NX, NY, degree)
    bad_e1, _ = _eval_cleared_e1_e2(A, [NX[0], NX[1], _l_neg(D)], NY, 2)
    if e1 or e2 or not bad_e1:
        raise ArithmeticError("Family 1 symbolic proof or corruption control failed")
    return {
        "proof": "PASS",
        "ring": "Z[Z,Z^-1,M,M^-1]",
        "e1_terms": len(e1),
        "e2_terms": len(e2),
        "corrupt_x3_terms": len(bad_e1),
    }


def family2_certificate() -> tuple:
    """Return A_i, D X_i, D Y_i and deg D; M = Z^(4m)."""
    ONE = {(0, 0): 1}
    Z = {(1, 0): 1}
    Z2 = {(2, 0): 1}
    Z3 = {(3, 0): 1}
    Z4 = {(4, 0): 1}
    M = {(0, 1): 1}
    D = _l_add(ONE, _l_neg(Z4))
    one_minus_M = _l_add(ONE, _l_neg(M))
    block = {(0, 0): 1, (1, 0): -1, (2, 0): -1, (3, 0): 1}  # +--+

    A = [_l_mul(Z3, M), Z4, Z2]
    nx1 = _l_add(
        _l_mul(D, {(0, 0): -1, (1, 0): -1, (2, 0): 1}),
        _l_mul(Z3, _l_mul(block, one_minus_M)),
    )
    ny1 = _l_add(
        _l_mul(block, one_minus_M),
        _l_mul(M, _l_mul(D, {(0, 0): 1, (1, 0): -1, (2, 0): -1})),
    )
    NX = [
        nx1,
        _l_mul(D, {(0, 0): 1, (1, 0): -1, (2, 0): 1, (3, 0): -1}),
        _l_mul(D, {(0, 0): -1, (1, 0): 1}),
    ]
    NY = [
        ny1,
        _l_mul(D, {(0, 0): 1, (1, 0): 1, (2, 0): 1, (3, 0): 1}),
        _l_mul(D, {(0, 0): -1, (1, 0): -1}),
    ]
    return A, NX, NY, 4


def prove_family2_symbolic() -> dict:
    """Verify the parameter identity, including a nonzero corruption control."""
    A, NX, NY, degree = family2_certificate()
    e1, e2 = _eval_cleared_e1_e2(A, NX, NY, degree)
    bad_e1, _ = _eval_cleared_e1_e2(A, [NX[0], NX[1], _l_neg(NX[2])], NY, 4)
    if e1 or e2 or not bad_e1:
        raise ArithmeticError("Family 2 symbolic proof or corruption control failed")
    return {
        "proof": "PASS",
        "ring": "Z[Z,Z^-1,M,M^-1]",
        "e1_terms": len(e1),
        "e2_terms": len(e2),
        "corrupt_x3_terms": len(bad_e1),
    }



def prove_subdivision_symbolic() -> dict:
    """Verify the universal reflection/factorization in Z[z^+-1,H^+-1].

    H=z^h, B=z H^2=z^(2h+1). J1=sum(z^j,1<=j<=h),
    J2=sum(z^j,h+1<=j<=2h). Independent H makes this an identity,
    rather than a finite check of subdivision factors.
    """
    one, z, H, B = ({(0, 0): 1}, {(1, 0): 1},
                     {(0, 1): 1}, {(1, 2): 1})
    j1 = _l_mul(z, _l_add(one, _l_neg(H)))  # (1-z) J1
    j2 = _l_mul(H, j1)                     # (1-z) J2
    reflected = [
        _l_add(_l_mul(_l_mul(z, B), _l_star(j1)), j2),
        _l_add(_l_mul(_l_mul(z, B), _l_star(j2)), j1),
    ]
    # Q_inserted=J1 E1(B)+J2 E2(B). Check its coefficients
    # of the independent formal symbols X_i,Y_i,X_i*,Y_i*.
    # The forward coefficients agree by definition. Reflection requires
    # -J1*=-J2/B and -J2*=-J1/B; the numerators above prove both.
    if any(reflected):
        raise ArithmeticError("subdivision reflection failed")
    corrupt = _l_add(_l_mul(_l_mul(z, B), _l_star(j1)), _l_neg(j2))
    if not corrupt:
        raise ArithmeticError("subdivision corruption control failed")
    return {"proof": "PASS", "ring": "Z[z,z^-1,H,H^-1]",
            "reflection_terms": [len(p) for p in reflected],
            "corrupt_reflection_terms": len(corrupt),
            "identity": "Q_inserted = J1 E1(B) + J2 E2(B)",
            "scope": "every odd g=2h+1>=3"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--family1", type=int, nargs=2, metavar=("M", "G"))
    mode.add_argument("--family2", type=int, nargs=2, metavar=("M", "G"))
    mode.add_argument("--check", metavar="FILE")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.prove:
            result = {
                "proof": "PASS",
                "family1": prove_family1_symbolic(),
                "family2": prove_family2_symbolic(),
                "subdivision": prove_subdivision_symbolic(),
            }
        elif args.family1 is not None:
            result = construct_family1(*args.family1, summary=args.summary)
        elif args.family2 is not None:
            result = construct_family2(*args.family2, summary=args.summary)
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
