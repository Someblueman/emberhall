#!/usr/bin/env python3
"""Three-parameter interior-hole family and Euler-cell escape taxonomy.

Proves in the 4-variable Laurent ring Z[z,z^-1, R,R^-1, C,C^-1, W,W^-1] that
for every odd r >= c >= 1 (c odd) and every integer k >= 0, the tripod
T(r*(k+2)+c, r*(k+1)+c-1, c) admits disjoint equal-size homometric sets of
size floor((1+a+b+c)/2)-1 = r*(k+1) + (r+c-1) + ... (exact half-minus-one),
omitting interior vertex (1, r) and long-arm tip (1, a).
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations, permutations
import json
from math import gcd
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def validate_parameters(r: int, c: int, k: int) -> tuple[int, int, int]:
    """Require odd r >= c >= 1 (c odd) and integer k >= 0."""
    for name, val in (("r", r), ("c", c), ("k", k)):
        if type(val) is not int:
            raise ValueError(f"{name} must be an integer")
    if r < 1 or r % 2 == 0:
        raise ValueError("r must be a positive odd integer")
    if c < 1 or c % 2 == 0 or c > r:
        raise ValueError("c must be a positive odd integer with 1 <= c <= r")
    if k < 0:
        raise ValueError("k must be nonnegative")
    return r, c, k


def validate_lengths(lengths: object) -> tuple[int, int, int]:
    """Validate a triple of positive integer arm lengths."""
    if not isinstance(lengths, (list, tuple)) or len(lengths) != 3:
        raise ValueError("lengths must be a triple of positive integers")
    out = tuple(lengths)
    if any(type(v) is not int or v < 1 for v in out):
        raise ValueError("all three arm lengths must be positive integers")
    return out  # type: ignore[return-value]


def target_size(lengths: tuple[int, int, int] | list[int]) -> int:
    """Return the project half-minus-one target floor((1+a+b+c)/2) - 1."""
    return (1 + sum(lengths)) // 2 - 1


def _validate_side(lengths: tuple[int, int, int], raw: object, label: str) -> list[tuple[int, int]]:
    if not isinstance(raw, list):
        raise ValueError(f"{label} must be a list of [arm, depth] vertices")
    verts: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"invalid vertex in {label}: {item!r}")
        arm, depth = item
        if type(arm) is not int or type(depth) is not int:
            raise ValueError(f"vertex coordinates must be integers: {item!r}")
        if arm == 0:
            if depth != 0:
                raise ValueError(f"centre must be [0, 0], got {item!r}")
        elif arm in (1, 2, 3):
            if not (1 <= depth <= lengths[arm - 1]):
                raise ValueError(f"vertex {item!r} out of range for {lengths}")
        else:
            raise ValueError(f"invalid arm index in {item!r}")
        v = (arm, depth)
        if v in seen:
            raise ValueError(f"duplicate vertex {item!r} in {label}")
        seen.add(v)
        verts.append(v)
    return verts


def _distance_profile(verts: list[tuple[int, int]]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for i, (a1, d1) in enumerate(verts):
        for a2, d2 in verts[i + 1 :]:
            d = abs(d1 - d2) if a1 == a2 else d1 + d2
            counts[d] += 1
    return counts


def check_pair(lengths: object, left: object, right: object) -> dict:
    """Validate disjointness, equality of sizes, and original-tree distances."""
    lens = validate_lengths(lengths)
    left_v = _validate_side(lens, left, "left")
    right_v = _validate_side(lens, right, "right")
    if set(left_v) & set(right_v):
        raise ValueError("left and right sets must be disjoint")
    if len(left_v) != len(right_v):
        raise ValueError("left and right sets must have equal size")
    lp = _distance_profile(left_v)
    rp = _distance_profile(right_v)
    diff = {str(d): lp[d] - rp[d] for d in sorted(lp.keys() | rp.keys()) if lp[d] != rp[d]}
    tgt = target_size(lens)
    return {
        "lengths": list(lens),
        "size": len(left_v),
        "target": tgt,
        "homometric": not diff,
        "meets_target": (not diff) and len(left_v) >= tgt,
        "left_profile": {str(d): lp[d] for d in sorted(lp)},
        "right_profile": {str(d): rp[d] for d in sorted(rp)},
        "difference": diff,
    }


def _arm_words(r: int, c: int, k: int, flip_block: bool = False) -> tuple[str, str, str]:
    alt = "+-" * ((r - 1) // 2)
    b1 = ("-" * c) + ("+-" * ((r - c) // 2))
    if flip_block:
        b1 = "+" + b1[1:]
    b2 = "".join("-" if ch == "+" else "+" for ch in b1)
    t1 = "+-" * ((c - 1) // 2)
    t2 = "-+" * ((c - 1) // 2)
    w1 = alt + "0" + b1 * (k + 1) + t1 + "0"
    w2 = alt + "+" + b2 * k + t2
    w3 = "+" * c
    return w1, w2, w3


def construct_three_param(r: int, c: int, k: int, summary: bool = False) -> dict:
    """Construct and verify the (r, c, k) witness on T(r*(k+2)+c, r*(k+1)+c-1, c)."""
    r, c, k = validate_parameters(r, c, k)
    w1, w2, w3 = _arm_words(r, c, k)
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
        raise ArithmeticError("three-parameter construction failed distance recount")
    out = {
        "r": r,
        "c": c,
        "k": k,
        "omitted": omitted,
        **checked,
    }
    if summary:
        for key in ("left_profile", "right_profile"):
            out.pop(key, None)
        return out
    out["left"] = left
    out["right"] = right
    return out


def _relabel_arm(arm: int, perm: tuple[int, int, int]) -> int:
    return 0 if arm == 0 else perm[arm - 1]


def solve_tree(lengths: object, summary: bool = False) -> dict:
    """Match an arbitrary triple (up to arm permutation) to the (r, c, k) family."""
    lens = validate_lengths(lengths)
    for perm in permutations((1, 2, 3)):
        a = lens[perm[0] - 1]
        b = lens[perm[1] - 1]
        c = lens[perm[2] - 1]
        r = a - b - 1
        if r < 1 or r % 2 == 0 or c < 1 or c % 2 == 0 or c > r:
            continue
        if (b - c + 1) % r != 0:
            continue
        k = (b - c + 1) // r - 1
        if k < 0:
            continue
        w = construct_three_param(r, c, k, summary=False)
        relabelled_left = sorted([_relabel_arm(arm, perm), d] for arm, d in w["left"])
        relabelled_right = sorted([_relabel_arm(arm, perm), d] for arm, d in w["right"])
        relabelled_omitted = sorted([_relabel_arm(arm, perm), d] for arm, d in w["omitted"])
        checked = check_pair(lens, relabelled_left, relabelled_right)
        out = {
            "r": r,
            "c": c,
            "k": k,
            "arm_order": list(perm),
            "omitted": relabelled_omitted,
            **checked,
        }
        if summary:
            for key in ("left_profile", "right_profile"):
                out.pop(key, None)
            return out
        out["left"] = relabelled_left
        out["right"] = relabelled_right
        return out
    raise ValueError(f"triple {list(lens)} is outside the three-parameter interior-hole family")


# --- 4-variable Laurent ring Z[z,z^-1, R,R^-1, C,C^-1, W,W^-1] ---

Laurent = dict[tuple[int, int, int, int], int]


def _l_add(*polys: Laurent) -> Laurent:
    out: Counter[tuple[int, int, int, int]] = Counter()
    for p in polys:
        for mon, coeff in p.items():
            if coeff:
                out[mon] += coeff
    return {mon: coeff for mon, coeff in out.items() if coeff}


def _l_neg(p: Laurent) -> Laurent:
    return {mon: -coeff for mon, coeff in p.items()}


def _l_mul(a: Laurent, b: Laurent) -> Laurent:
    out: Counter[tuple[int, int, int, int]] = Counter()
    for (za, ra, ca, wa), va in a.items():
        for (zb, rb, cb, wb), vb in b.items():
            out[(za + zb, ra + rb, ca + cb, wa + wb)] += va * vb
    return {mon: coeff for mon, coeff in out.items() if coeff}


def _l_star(p: Laurent) -> Laurent:
    return {(-z, -r, -c, -w): coeff for (z, r, c, w), coeff in p.items()}


def _laurent_residual(
    s0_val: int = -1,
    include_hole: bool = True,
    corrupt_block: bool = False,
) -> Laurent:
    """Compute D(z,R)*E(z) in Z[z,z^-1,R,R^-1,C,C^-1,W,W^-1], D=(1-z^2)(1-R)."""
    ONE: Laurent = {(0, 0, 0, 0): 1}
    Z: Laurent = {(1, 0, 0, 0): 1}
    ZINV: Laurent = {(-1, 0, 0, 0): 1}
    R: Laurent = {(0, 1, 0, 0): 1}
    RINV: Laurent = {(0, -1, 0, 0): 1}
    C: Laurent = {(0, 0, 1, 0): 1}
    W: Laurent = {(0, 0, 0, 1): 1}
    Z2R: Laurent = {(2, 1, 0, 0): 1}

    one_minus_z = _l_add(ONE, _l_neg(Z))
    one_plus_z = _l_add(ONE, Z)
    one_minus_R = _l_add(ONE, _l_neg(R))
    one_minus_C = _l_add(ONE, _l_neg(C))
    D = _l_mul(_l_mul(one_minus_z, one_plus_z), one_minus_R)

    N_alt = _l_mul(one_minus_z, _l_mul(one_minus_R, _l_add(Z, _l_neg(R))))
    B1_num = _l_add(
        _l_neg(_l_mul(Z, _l_mul(one_plus_z, one_minus_C))),
        _l_mul(Z, _l_mul(one_minus_z, _l_add(C, _l_neg(R)))),
    )
    if corrupt_block:
        # Flip first letter of B1 from -1 to +1 (add +2*z*(1-z^2) to B1_num).
        B1_num = _l_add(B1_num, _l_mul({(1, 0, 0, 0): 2}, _l_mul(one_minus_z, one_plus_z)))

    N_tail1 = _l_mul(_l_mul(_l_mul(R, R), W), _l_mul(one_minus_z, _l_mul(one_minus_R, _l_add(Z, _l_neg(C)))))
    N_tail2 = _l_neg(_l_mul(_l_mul(R, W), _l_mul(one_minus_z, _l_mul(one_minus_R, _l_add(Z, _l_neg(C))))))

    N1 = _l_add(N_alt, _l_mul(R, _l_mul(B1_num, _l_add(ONE, _l_neg(_l_mul(R, W))))), N_tail1)
    N2 = _l_add(N_alt, _l_mul(D, R), _l_neg(_l_mul(R, _l_mul(B1_num, _l_add(ONE, _l_neg(W))))), N_tail2)
    N3 = _l_mul(Z, _l_mul(one_plus_z, _l_mul(one_minus_R, one_minus_C)))

    E1 = _l_mul(_l_mul(R, R), _l_mul(W, C))
    E2 = _l_mul(_l_mul(R, W), _l_mul(C, ZINV))
    E3 = C
    s0: Laurent = {(0, 0, 0, 0): s0_val}

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


def _eval_laurent_z(poly: Laurent, r: int, c: int, k: int) -> dict[int, int]:
    out: Counter[int] = Counter()
    for (ez, er, ec, ew), coeff in poly.items():
        deg = ez + er * r + ec * c + ew * (r * k)
        out[deg] += coeff
    return {d: v for d, v in out.items() if v}


def prove_symbolic_identity() -> dict:
    """Verify D*E(z) == 0 over Z[z,z^-1,R,R^-1,C,C^-1,W,W^-1] and check corruptions."""
    res = _laurent_residual()
    bad_s0 = _laurent_residual(s0_val=1)
    bad_hole = _laurent_residual(include_hole=False)
    bad_block = _laurent_residual(corrupt_block=True)

    # Verify concrete specialization at (r=7, c=3, k=1) with corrupted block:
    # D(z) = (1 - z^2)(1 - z^7), and D*E(z) must equal 2*(1-z)*D(z)*(D_A - D_B)/z.
    r, c, k = 7, 3, 1
    w1, w2, w3 = _arm_words(r, c, k, flip_block=True)
    left, right = [], [(0, 0)]
    for arm, word in ((1, w1), (2, w2), (3, w3)):
        for d, ch in enumerate(word, 1):
            if ch == "+":
                left.append((arm, d))
            elif ch == "-":
                right.append((arm, d))
    lp = _distance_profile(left)
    rp = _distance_profile(right)
    # 2*(1-z)/z * (lp - rp)
    e_direct: Counter[int] = Counter()
    for d in set(lp) | set(rp):
        diff = 2 * (lp[d] - rp[d])
        if diff:
            e_direct[d - 1] += diff
            e_direct[d] -= diff
    # Multiply by D(z) = 1 - z^2 - z^r + z^(r+2), including the exact
    # signed-balance offset -2*(|L|-|R|)*D(z).
    balance_sum = len(left) - len(right)
    de_direct: Counter[int] = Counter()
    for d, v in e_direct.items():
        for sd, sv in ((0, 1), (2, -1), (r, -1), (r + 2, 1)):
            de_direct[d + sd] += v * sv
    for sd, sv in ((0, 1), (2, -1), (r, -1), (r + 2, 1)):
        de_direct[sd] -= 2 * balance_sum * sv
    de_direct_clean = {d: v for d, v in de_direct.items() if v}
    de_spec = _eval_laurent_z(bad_block, r, c, k)

    if res or not bad_s0 or not bad_hole or not bad_block or de_spec != de_direct_clean:
        raise ArithmeticError("symbolic identity or corruption control failed")
    return {
        "proof": "PASS",
        "ring": "Z[z,z^-1,R,R^-1,C,C^-1,W,W^-1]",
        "residual_terms": len(res),
        "corrupt_s0_terms": len(bad_s0),
        "corrupt_hole_terms": len(bad_hole),
        "corrupt_block_terms": len(bad_block),
        "specialization_matches_difference": de_spec == de_direct_clean,
    }


# --- Euler-cell escape taxonomy ---

def _cell_admitted(n1: int, n2: int, n3: int) -> bool:
    if (n1 + n2 + n3) % 2 != 0 or n1 == n2 == n3:
        return False
    g = gcd(n1 - n2, n2 - n3)
    return (n1 % g == 0) and (((n1 + n2 + n3) // g) % 2 == 0)


def _euler_trims_admitted(a: int, b: int, c: int) -> bool:
    order = a + b + c + 1
    budget = 2 if order % 2 == 0 else 3
    for d1 in range(budget + 1):
        for d2 in range(budget + 1 - d1):
            for d3 in range(budget + 1 - d1 - d2):
                if (order - d1 - d2 - d3) % 2 == 0 and d1 <= a and d2 <= b and d3 <= c:
                    if _cell_admitted(a - d1 + 1, b - d2 + 1, c - d3 + 1):
                        return True
    return False


def _root_residue_obstructs(l1: int, l2: int, l3: int) -> bool:
    if (1 + l1 + l2 + l3) % 2 != 0:
        return True
    diff_gcd = gcd(l1 - l2, l2 - l3)
    if diff_gcd == 0:
        return True
    for g in range(2, diff_gcd + 1):
        if diff_gcd % g != 0:
            continue
        r = l1 % g
        if r == 0:
            continue
        h = gcd(r, g)
        if h > 1:
            return True
        q = l1 // g + l2 // g + l3 // g
        if r != g - 1 or q % 2 == 0:
            return True
    return False


def _has_surviving_prefix_trim(a: int, b: int, c: int) -> bool:
    order = 1 + a + b + c
    budget = 2 if order % 2 == 0 else 3
    for d1 in range(budget + 1):
        for d2 in range(budget + 1 - d1):
            for d3 in range(budget + 1 - d1 - d2):
                if (order - d1 - d2 - d3) % 2 == 0 and d1 <= a and d2 <= b and d3 <= c:
                    if not _root_residue_obstructs(a - d1, b - d2, c - d3):
                        return True
    return False


def _aster_subdivision_admits(a: int, b: int, c: int) -> bool:
    for d1, d2, d3 in ((2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1)):
        aa, bb, cc = a - d1, b - d2, c - d3
        g = gcd(gcd(aa, bb), cc)
        if g < 3 or g % 2 == 0:
            continue
        for div in range(3, g + 1, 2):
            if g % div != 0:
                continue
            coarse = (aa // div, bb // div, cc // div)
            if sum(coarse) % 2 == 0 or not _cell_admitted(coarse[0] + 1, coarse[1] + 1, coarse[2] + 1):
                continue
            for p1, p2, p3 in permutations(coarse):
                if p1 <= p2:
                    continue
                d = p1 - p2
                if p3 % (2 * d) == 0 or (d % 2 == 1 and p2 % d == 0 and p3 % 2 == 0):
                    return True
    return False


def _three_param_admits(a: int, b: int, c: int) -> bool:
    for perm in permutations((a, b, c)):
        pa, pb, pc = perm
        r = pa - pb - 1
        if r >= 1 and r % 2 == 1 and 1 <= pc <= r and pc % 2 == 1 and (pb - pc + 1) % r == 0:
            if (pb - pc + 1) // r - 1 >= 0:
                return True
    return False


def classify_euler_escapes(max_a: int = 300) -> dict:
    """Audit Euler-cell prefix coverage across 1<=c<=b<=a<=max_a and the 346-triple grid."""
    import interior_transfer as it
    import published_cases as pc

    total = 0
    even_esc = 0
    odd_esc: list[tuple[int, int, int]] = []
    r0_surviving = 0
    all_prefix_dead = 0
    after_known: list[list[int]] = []
    newly_settled_by_three_param: list[list[int]] = []

    for a in range(1, max_a + 1):
        for b in range(1, a + 1):
            for c in range(1, b + 1):
                total += 1
                if a == b == c or _euler_trims_admitted(a, b, c):
                    continue
                if (a + b + c) % 2 == 0:
                    even_esc += 1
                    continue
                odd_esc.append((a, b, c))
                if _has_surviving_prefix_trim(a, b, c):
                    r0_surviving += 1
                else:
                    all_prefix_dead += 1
                if (a - c == 76 and b - c == 56) or _aster_subdivision_admits(a, b, c):
                    continue
                if _three_param_admits(a, b, c):
                    newly_settled_by_three_param.append([a, b, c])
                else:
                    after_known.append([a, b, c])

    grid_total = 0
    grid_settled = 0
    for a in range(5, 56, 5):
        for b in range(5, a, 5):
            for c in range(2, b, 3):
                grid_total += 1
                tgt = target_size((a, b, c))
                _, pair = pc.construct((a, b, c), "best")
                ok = len(pair[0]) >= tgt
                if not ok and _euler_trims_admitted(a, b, c):
                    ok = True
                if not ok:
                    for p in permutations((a, b, c)):
                        try:
                            if len(it.path_transfer_pair(*p)["left"]) >= tgt:
                                ok = True
                                break
                        except ValueError:
                            pass
                if ok:
                    grid_settled += 1

    return {
        "max_a": max_a,
        "total_triples": total,
        "even_sum_euler_escapes": even_esc,
        "odd_sum_euler_escapes": len(odd_esc),
        "r0_surviving_prefix_escapes": r0_surviving,
        "all_prefix_dead_escapes": all_prefix_dead,
        "newly_settled_by_three_param": newly_settled_by_three_param,
        "remaining_open_count": len(after_known),
        "remaining_open_triples": after_known,
        "grid_total": grid_total,
        "grid_settled": grid_settled,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prove", action="store_true")
    mode.add_argument("--witness", type=int, nargs=3, metavar=("R", "C", "K"))
    mode.add_argument("--tree", type=int, nargs=3, metavar=("A", "B", "C"))
    mode.add_argument("--check", metavar="FILE")
    mode.add_argument("--audit-escapes", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--max-a", type=int, default=300)
    args = parser.parse_args(argv)
    try:
        if args.prove:
            result = prove_symbolic_identity()
        elif args.witness is not None:
            result = construct_three_param(*args.witness, summary=args.summary)
        elif args.tree is not None:
            result = solve_tree(args.tree, summary=args.summary)
        elif args.check is not None:
            raw = sys.stdin.read() if args.check == "-" else Path(args.check).read_text(encoding="utf-8")
            data = json.loads(raw)
            result = check_pair(data["lengths"], data["left"], data["right"])
        else:
            result = classify_euler_escapes(max_a=args.max_a)
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as err:
        print(json.dumps({"error": str(err)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("homometric", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
