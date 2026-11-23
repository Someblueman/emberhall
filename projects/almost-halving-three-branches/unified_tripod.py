#!/usr/bin/env python3
"""Unified dispatcher, proof runner, and coverage auditor for all proved tripod families.

Combines published_cases, ratio_51_33_10, interior_transfer, fixed_difference_family,
corrected_subdivision, ratio_50_33_9, interior_hole_three_param, two_row_subdivision,
interior_hole_c_plus_4, and even_sum_euler_bound into one standard-library tool.
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

import corrected_subdivision as cs  # noqa: E402
import even_sum_euler_bound as esb  # noqa: E402
import fixed_difference_family as fdf  # noqa: E402
import interior_hole_c_plus_4 as ihc4  # noqa: E402
import interior_hole_three_param as ih3  # noqa: E402
import interior_transfer as it  # noqa: E402
import published_cases as pc  # noqa: E402
import ratio_50_33_9 as r50  # noqa: E402
import ratio_51_33_10 as r51  # noqa: E402
import two_row_subdivision as trs  # noqa: E402

check_pair = ih3.check_pair
target_size = ih3.target_size
validate_lengths = ih3.validate_lengths


def _relabel_vertices(verts: list, perm: tuple[int, int, int]) -> list[list[int]]:
    return sorted([0 if arm == 0 else perm[arm - 1], d] for arm, d in verts)


def _finalize(
    lengths: tuple[int, int, int],
    family: str,
    left: list,
    right: list,
    summary: bool,
) -> dict:
    left_norm = sorted([int(a), int(d)] for a, d in left)
    right_norm = sorted([int(a), int(d)] for a, d in right)
    checked = check_pair(lengths, left_norm, right_norm)
    if not checked["homometric"] or not checked["meets_target"]:
        raise ArithmeticError(f"{family} failed independent check_pair on {lengths}")
    out: dict = {"family": family, **checked}
    if summary:
        out.pop("left_profile", None)
        out.pop("right_profile", None)
        return out
    out["left"] = left_norm
    out["right"] = right_norm
    return out


def _try_corrected_subdivision(lengths: tuple[int, int, int]) -> tuple[str, list, list] | None:
    if sum(lengths) % 2 == 0:
        return None
    for d1, d2, d3 in ((2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1)):
        trimmed = (lengths[0] - d1, lengths[1] - d2, lengths[2] - d3)
        if min(trimmed) < 1:
            continue
        g = gcd(gcd(trimmed[0], trimmed[1]), trimmed[2])
        if g < 3 or g % 2 == 0:
            continue
        for div in range(3, g + 1, 2):
            if g % div != 0:
                continue
            coarse = (trimmed[0] // div, trimmed[1] // div, trimmed[2] // div)
            if sum(coarse) % 2 == 0 or not r51.classify((coarse[0] + 1, coarse[1] + 1, coarse[2] + 1))["admitted"]:
                continue
            for order in permutations((0, 1, 2)):
                li, lj, lk = coarse[order[0]], coarse[order[1]], coarse[order[2]]
                if li <= lj:
                    continue
                diff = li - lj
                if lk % (2 * diff) == 0 or (diff % 2 == 1 and lj % diff == 0 and lk % 2 == 0):
                    base = r51.original_tree(coarse)
                    lifted = cs.corrected_lift(coarse, base["left"], base["right"], div, order)
                    return f"corrected_subdivision(g={div})", lifted["left"], lifted["right"]
    return None


def _try_two_row_lift(lengths: tuple[int, int, int]) -> tuple[str, list, list] | None:
    if sum(lengths) % 2 == 0:
        return None
    for d1, d2, d3 in ((2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1)):
        trimmed = (lengths[0] - d1, lengths[1] - d2, lengths[2] - d3)
        if min(trimmed) < 1:
            continue
        g = gcd(gcd(trimmed[0], trimmed[1]), trimmed[2])
        if g < 3 or g % 2 == 0:
            continue
        for div in range(3, g + 1, 2):
            if g % div != 0:
                continue
            coarse = (trimmed[0] // div, trimmed[1] // div, trimmed[2] // div)
            for perm in permutations((1, 2, 3)):
                p_coarse = (coarse[perm[0] - 1], coarse[perm[1] - 1], coarse[perm[2] - 1])
                if p_coarse in trs.LIFT_FAMILIES:
                    w = trs.construct_lifted_tree(p_coarse, div, summary=False)
                    return (
                        f"two_row_subdivision(g={div})",
                        _relabel_vertices(w["left"], perm),
                        _relabel_vertices(w["right"], perm),
                    )
    return None


def construct_best(lengths: object, summary: bool = False) -> dict:
    """Construct and verify a target-meeting pair across all proved tripod families."""
    lens = validate_lengths(lengths)
    tgt = target_size(lens)

    # 1. published_cases default menu
    name, pair = pc.construct(lens, "best")
    if len(pair[0]) >= tgt:
        return _finalize(lens, f"published_cases:{name}", pair[0], pair[1], summary)

    # 2. ratio_51_33_10 Euler-cell trimming
    try:
        w = r51.original_tree(lens)
        if w["size"] >= tgt:
            return _finalize(lens, "ratio_51_33_10", w["left"], w["right"], summary)
    except ValueError:
        pass

    # 3. interior_transfer path-transfer family
    for perm in permutations((1, 2, 3)):
        p_lens = (lens[perm[0] - 1], lens[perm[1] - 1], lens[perm[2] - 1])
        try:
            w = it.path_transfer_pair(*p_lens)
            if len(w["left"]) >= tgt:
                return _finalize(
                    lens,
                    "interior_transfer",
                    _relabel_vertices(w["left"], perm),
                    _relabel_vertices(w["right"], perm),
                    summary,
                )
        except ValueError:
            pass

    # 4. fixed_difference_family T(c+76, c+56, c)
    for perm in permutations((1, 2, 3)):
        a, b, c = lens[perm[0] - 1], lens[perm[1] - 1], lens[perm[2] - 1]
        if a - c == 76 and b - c == 56:
            w = fdf.construct(c)
            return _finalize(
                lens,
                "fixed_difference_family",
                _relabel_vertices(w["left"], perm),
                _relabel_vertices(w["right"], perm),
                summary,
            )

    # 5. ratio_50_33_9 T(15p+5q, 10p+3q, 3p)
    for perm in permutations((1, 2, 3)):
        a, b, c = lens[perm[0] - 1], lens[perm[1] - 1], lens[perm[2] - 1]
        if c % 3 == 0:
            p = c // 3
            if a >= 15 * p and (a - 15 * p) % 5 == 0:
                q = (a - 15 * p) // 5
                if b == 10 * p + 3 * q:
                    w = r50.parameter_witness(p, q)
                    return _finalize(
                        lens,
                        "ratio_50_33_9",
                        _relabel_vertices(w["left"], perm),
                        _relabel_vertices(w["right"], perm),
                        summary,
                    )

    # 6. corrected_subdivision
    cs_hit = _try_corrected_subdivision(lens)
    if cs_hit is not None:
        return _finalize(lens, *cs_hit, summary)

    # 7. two_row_subdivision lifts
    trs_hit = _try_two_row_lift(lens)
    if trs_hit is not None:
        return _finalize(lens, *trs_hit, summary)

    # 8. interior_hole_three_param
    try:
        w = ih3.solve_tree(lens, summary=False)
        return _finalize(lens, "interior_hole_three_param", w["left"], w["right"], summary)
    except ValueError:
        pass

    # 9. interior_hole_c_plus_4 (and period-7 c=15)
    try:
        w = ihc4.solve_tree(lens, summary=False)
        return _finalize(lens, "interior_hole_c_plus_4", w["left"], w["right"], summary)
    except ValueError:
        pass

    # 10. two_row_subdivision unrestricted k=0 family T(2r+c, r+c-1, c)
    for perm in permutations((1, 2, 3)):
        a, b, c = lens[perm[0] - 1], lens[perm[1] - 1], lens[perm[2] - 1]
        r = a - b - 1
        if r >= 1 and r % 2 == 1 and c >= 1 and c % 2 == 1 and b == r + c - 1:
            w = trs.construct_k0(r, c, summary=False)
            return _finalize(
                lens,
                "two_row_subdivision:k0",
                _relabel_vertices(w["left"], perm),
                _relabel_vertices(w["right"], perm),
                summary,
            )

    # 11. even_sum_euler_bound c in {1, 2}
    if sum(lens) % 2 == 0:
        for perm in permutations((1, 2, 3)):
            a, b, c = lens[perm[0] - 1], lens[perm[1] - 1], lens[perm[2] - 1]
            if c in (1, 2):
                w = esb.construct_c12_even_sum(a, b, c, summary=False)
                return _finalize(
                    lens,
                    "even_sum_euler_bound:c12",
                    _relabel_vertices(w["left"], perm),
                    _relabel_vertices(w["right"], perm),
                    summary,
                )

    raise ValueError(f"triple {list(lens)} is outside all proved families in unified_tripod")


def prove_all_families() -> dict:
    """Run symbolic/arithmetic proof checks across all integrated family modules."""
    results = {}
    r51_tpl = r51.template()
    results["ratio_51_33_10"] = (
        "PASS" if (r51_tpl.get("status") == "constructed" and not r51_tpl.get("identity_residual")) else "FAIL"
    )
    results["fixed_difference_family"] = "PASS" if all(
        not fdf.identity_residual(base) for base in fdf.FAMILIES
    ) else "FAIL"
    results["corrected_subdivision"] = "PASS" if not cs.edge_filler_residual() else "FAIL"
    results["ratio_50_33_9"] = "PASS" if not r50.general_identity_residual() else "FAIL"
    results["interior_hole_three_param"] = ih3.prove_symbolic_identity()["proof"]
    results["two_row_subdivision"] = trs.prove_all()["proof"]
    results["interior_hole_c_plus_4"] = (
        "PASS"
        if (ihc4.prove_c_plus_4_laurent()["proof"] == "PASS"
            and ihc4.prove_period7_laurent()["proof"] == "PASS")
        else "FAIL"
    )
    results["even_sum_euler_bound"] = esb.prove_prime_shift_bound()["proof"]
    overall = "PASS" if all(v == "PASS" for v in results.values()) else "FAIL"
    if overall != "PASS":
        raise ArithmeticError(f"proof audit failed: {results}")
    return {"proof": overall, "families": results}


def audit_coverage(max_a: int = 300) -> dict:
    """Audit exact arithmetic coverage over 1<=c<=b<=a<=max_a and the 346-triple grid."""
    total = 0
    open_triples: list[list[int]] = []
    for a in range(1, max_a + 1):
        for b in range(1, a + 1):
            for c in range(1, b + 1):
                total += 1
                if a == b == c or ih3._euler_trims_admitted(a, b, c):
                    continue
                if (a + b + c) % 2 == 0 and c in (1, 2):
                    continue
                if a - c == 76 and b - c == 56:
                    continue
                if ih3._aster_subdivision_admits(a, b, c):
                    continue
                if ih3._three_param_admits(a, b, c):
                    continue
                r = a - b - 1
                if r >= 5 and r % 2 == 1 and c == r + 4 and (b - 3) % r == 0 and (b - 3) // r - 2 >= 0:
                    continue
                if c == 15 and a - b == 8 and (b - 14) % 7 == 0 and b >= 14:
                    continue
                if r >= 1 and r % 2 == 1 and c >= 1 and c % 2 == 1 and b == r + c - 1:
                    continue
                open_triples.append([a, b, c])

    grid_total = 0
    grid_settled = 0
    for a in range(5, 56, 5):
        for b in range(5, a, 5):
            for c in range(2, b, 3):
                grid_total += 1
                w = construct_best((a, b, c), summary=True)
                if w["homometric"] and w["meets_target"]:
                    grid_settled += 1

    return {
        "max_a": max_a,
        "total_triples": total,
        "settled": total - len(open_triples),
        "open_count": len(open_triples),
        "refuted_in_open_list": [227, 67, 11] if [227, 67, 11] in open_triples else None,
        "open_triples": open_triples,
        "grid_total": grid_total,
        "grid_settled": grid_settled,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tree", type=int, nargs=3, metavar=("A", "B", "C"))
    mode.add_argument("--prove-all", action="store_true")
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--check", metavar="FILE")
    parser.add_argument("--max-a", type=int, default=300)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.tree is not None:
            result = construct_best(args.tree, summary=args.summary)
        elif args.prove_all:
            result = prove_all_families()
        elif args.audit:
            result = audit_coverage(max_a=args.max_a)
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
