"""Close the one-short case (99,79,23) and its scaling family T(99t,79t,23t).

The default construction menu gives size 99 on T(99,79,23), one below the
target 100.  Size 100 is in fact attained and optimal.  For the scaling
family, every scale except t == 1 (mod 2660) attains the target by a
full-prefix Euler-cell construction (see RATIO_51_33_10.md for that
method's proof); scales t == 1 (mod 2660) with t > 1 admit no full-prefix
target pair at all (root-residue obstruction, GAP_99_79_23.md) and remain
open.  The t = 1 witness is the interior-hole certificate of
FIXED_DIFFERENCE_FAMILY.md at c = 23, recounted independently here.

Standard library only.  Constructions reuse two proved project modules:
ratio_51_33_10 (Euler-cell words) and fixed_difference_family (t = 1).
Distance recounting in this file is separate code from both.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
from math import gcd
import sys

from fixed_difference_family import construct as _fixed_difference
from ratio_51_33_10 import cell_identity, template

BASE = (99, 79, 23)
RESISTANT_MODULUS = 2660  # 4 * 5 * 7 * 19


class OpenScale(ValueError):
    """t == 1 (mod 2660), t > 1: no full-prefix pair exists; case open."""


def target(t: int) -> int:
    """floor((1 + 99t + 79t + 23t) / 2) - 1."""
    return (1 + 201 * t) // 2 - 1


def _validate_t(t: object) -> int:
    if type(t) is not int or t < 1:
        raise ValueError("the scale must be a positive integer")
    return t


def cells_admissible(cells: tuple[int, int, int]) -> bool:
    """Exact Euler-cell admission (RATIO_51_33_10.md): with
    g = gcd of cell differences, g divides every cell and sum/g is even."""
    if len(set(cells)) == 1 or min(cells) < 1:
        return False
    g = gcd(cells[0] - cells[1], cells[1] - cells[2])
    return (g > 0 and sum(cells) % 2 == 0
            and all(n % g == 0 for n in cells)
            and (sum(cells) // g) % 2 == 0)


def choose_cells(t: int) -> tuple[str, tuple[int, int, int], tuple[int, int, int]]:
    """Return (branch, tip deletions, cell counts) for scale t >= 2.

    Cell counts are prefix lengths + 1.  The congruence conditions are
    proved in GAP_99_79_23.md; admissibility is re-asserted arithmetically.
    """
    t = _validate_t(t)
    lengths = tuple(n * t for n in BASE)
    if t % 2 == 0:
        branch, deletions = "even", (1, 0, 2)
    elif t % 19 != 1:
        branch, deletions = "odd-19", (1, 0, 1)
    elif t % 7 != 1:
        branch, deletions = "odd-7", (0, 1, 1)
    elif t % 5 != 1:
        branch, deletions = "odd-5", (1, 1, 0)
    elif t % 4 == 3:
        branch, deletions = "odd-4", (0, 0, 2)
    else:
        raise OpenScale(
            f"t={t} is 1 mod {RESISTANT_MODULUS}: no full-prefix target "
            "pair exists (proved); interior-hole pairs are open")
    cells = tuple(lengths[i] - deletions[i] + 1 for i in range(3))
    if not cells_admissible(cells):
        raise ArithmeticError(f"branch {branch} cells {cells} not admissible")
    return branch, deletions, cells


def classify(t: int) -> dict:
    """Arithmetic-only status of T(99t,79t,23t); allocates no graph."""
    t = _validate_t(t)
    result = {"t": t, "lengths": [n * t for n in BASE], "target": target(t)}
    if t == 1:
        return {**result, "status": "attained-optimal",
                "branch": "interior-certificate",
                "size": 100, "optimal": True}
    try:
        branch, deletions, cells = choose_cells(t)
    except OpenScale:
        return {**result, "status": "open-no-full-prefix",
                "branch": None, "size": None,
                "upper_bound": target(t),
                "note": "target is the best possible size for odd t; "
                        "attainment is open"}
    size = (sum(cells) - 2) // 2
    return {**result, "status": "attained", "branch": branch,
            "deletions": list(deletions), "cells": list(cells),
            "size": size, "optimal": (size == target(t) if t % 2 == 1
                                      else None)}


def distance(u: tuple[int, int], v: tuple[int, int]) -> int:
    return abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]


def profile(vertices: list[tuple[int, int]]) -> Counter:
    return Counter(distance(u, v) for u, v in combinations(vertices, 2))


def _validate_vertices(lengths, vertices):
    result = []
    for vertex in vertices:
        if (not isinstance(vertex, (list, tuple)) or len(vertex) != 2
                or type(vertex[0]) is not int or type(vertex[1]) is not int):
            raise ValueError(f"malformed vertex {vertex!r}")
        arm, depth = vertex
        if not ((arm == 0 and depth == 0)
                or (1 <= arm <= 3 and 1 <= depth <= lengths[arm - 1])):
            raise ValueError(f"vertex {vertex} is outside the tree")
        result.append((arm, depth))
    if len(result) != len(set(result)):
        raise ValueError("duplicate vertex in a set")
    return result


def check_pair(lengths, left, right) -> dict:
    """Independent recount: validate, then count every pairwise distance."""
    if (not isinstance(lengths, (list, tuple)) or len(lengths) != 3
            or any(type(n) is not int or n < 1 for n in lengths)):
        raise ValueError("lengths must be three positive integers")
    lengths = list(lengths)
    left = _validate_vertices(lengths, left)
    right = _validate_vertices(lengths, right)
    if set(left) & set(right):
        raise ValueError("the two sets overlap")
    if len(left) != len(right):
        raise ValueError("the two sets have different sizes")
    lp, rp = profile(left), profile(right)
    difference = {d: lp[d] - rp[d] for d in sorted(lp.keys() | rp.keys())
                  if lp[d] != rp[d]}
    return {"lengths": lengths, "size": len(left), "homometric": not difference,
            "difference": difference,
            "left_profile": {str(d): lp[d] for d in sorted(lp)},
            "right_profile": {str(d): rp[d] for d in sorted(rp)},
            "pairs_per_side": sum(lp.values())}


def witness(t: int) -> dict:
    """Explicit disjoint homometric pair on T(99t,79t,23t) at the target."""
    t = _validate_t(t)
    lengths = [n * t for n in BASE]
    if t == 1:
        base = _fixed_difference(23)
        left = [tuple(v) for v in base["left"]]
        right = [tuple(v) for v in base["right"]]
        checked = check_pair(lengths, left, right)
        info = {"branch": "interior-certificate",
                "source": "fixed_difference_family.construct(23)"}
    else:
        branch, deletions, cells = choose_cells(t)
        certified = template(cells)
        if certified["status"] != "constructed":
            raise ArithmeticError("Euler-cell template obstructed "
                                  "despite admissible cells")
        # At cell scale 1, word sign j (j >= 1) sits at depth j; the
        # centre carries center_sign.  Tips at depth cells[i] are omitted,
        # which are exactly the deleted terminal vertices of T(99t,...).
        left, right = [], ([(0, 0)] if certified["center_sign"] == -1 else [])
        if certified["center_sign"] != -1:
            left.append((0, 0))
        for arm, word in enumerate(certified["words"], 1):
            for depth, sign in enumerate(word):
                if depth == 0:
                    continue
                (left if sign == "+" else right).append((arm, depth))
        checked = check_pair(lengths, left, right)
        info = {"branch": branch, "deletions": list(deletions),
                "cells": list(cells)}
    if not checked["homometric"] or checked["size"] < target(t):
        raise ArithmeticError("constructed pair failed its independent recount")
    return {"t": t, "lengths": lengths, "target": target(t),
            "meets_target": checked["size"] >= target(t),
            "left": [list(v) for v in left], "right": [list(v) for v in right],
            **info, **checked}


def _smallest_odd_prime_factor(t: int) -> int:
    p = 3
    while p * p <= t:
        if t % p == 0:
            return p
        p += 2
    return t


def obstruction_data(t: int) -> list[dict]:
    """Root-residue data excluding every full-prefix target pair at
    odd resistant t.  Each row: a modulus g dividing both prefix-length
    differences, common residue r, h = gcd(r,g), Q = sum floor(l_i/g)."""
    t = _validate_t(t)
    if t % 2 == 0 or t % RESISTANT_MODULUS != 1 or t == 1:
        raise ValueError("obstruction data is stated for odd t = 1 mod 2660, t > 1")
    p = _smallest_odd_prime_factor(t)
    rows = []
    shapes = [(0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2),
              (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    moduli = {(0, 0, 0): 4 * p, (1, 1, 0): 5, (1, 0, 1): 19, (0, 1, 1): 7}
    for deletions in shapes:
        lengths = tuple(BASE[i] * t - deletions[i] for i in range(3))
        g = moduli.get(deletions, 2)
        assert (lengths[0] - lengths[1]) % g == 0
        assert (lengths[1] - lengths[2]) % g == 0
        r = lengths[0] % g
        rows.append({"deletions": list(deletions), "g": g, "r": r,
                     "h": gcd(r, g),
                     "Q": sum(n // g for n in lengths)})
    return rows


def prove() -> list[str]:
    """Finite exact audit of the arithmetic used in GAP_99_79_23.md.

    The infinite claims rest on the algebra in the document (each
    pattern's gcd divides a fixed integer, so its admissibility is the
    stated congruence condition).  This audit checks that arithmetic
    over two full periods and verifies constructed words against the
    independent cell identity at one scale per branch.
    """
    lines = []
    for t in range(2, 2 * RESISTANT_MODULUS + 2):
        info = classify(t)
        if t % RESISTANT_MODULUS == 1:
            assert info["status"] == "open-no-full-prefix", t
        else:
            assert info["status"] == "attained" and info["size"] >= target(t), t
    lines.append("branch audit: every 2 <= t <= 5321 attains the target "
                 "except t = 2661, 5321 (1 mod 2660)")
    for t in (2661, 5321, 7981):
        for row in obstruction_data(t):
            g, r, h, q = row["g"], row["r"], row["h"], row["Q"]
            assert r > 0 and (h > 1 or r != g - 1 or q % 2 == 0), (t, row)
    lines.append("residue audit: all seven prefix shapes obstructed at "
                 "t = 2661, 5321, 7981")
    representatives = {2: "even", 3: "odd-19", 39: "odd-7",
                       267: "odd-5", 1331: "odd-4"}
    for t, branch in representatives.items():
        got, _, cells = choose_cells(t)
        assert got == branch, (t, got)
        certified = template(cells)
        assert certified["status"] == "constructed"
        assert cell_identity(certified["words"]) == {}
        assert all(w == w[::-1] for w in certified["words"])
    lines.append("word audit: palindromic words satisfy the cell identity "
                 "at t = 2, 3, 39, 267, 1331 (one per branch)")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--witness", type=int, metavar="T")
    group.add_argument("--classify", type=int, metavar="T")
    group.add_argument("--prove", action="store_true")
    group.add_argument("--check", metavar="FILE")
    parser.add_argument("--summary", action="store_true",
                        help="with --witness, omit vertex lists and profiles")
    args = parser.parse_args(argv)
    try:
        if args.witness is not None:
            result = witness(args.witness)
            if args.summary:
                result = {k: v for k, v in result.items() if k not in
                          ("left", "right", "left_profile", "right_profile")}
            print(json.dumps(result, indent=1, sort_keys=True))
        elif args.classify is not None:
            print(json.dumps(classify(args.classify), indent=1, sort_keys=True))
        elif args.prove:
            for line in prove():
                print("PASS:", line)
        else:
            text = (sys.stdin.read() if args.check == "-"
                    else open(args.check, encoding="utf-8").read())
            data = json.loads(text)
            result = check_pair(data["lengths"], data["left"], data["right"])
            print(json.dumps(result, indent=1, sort_keys=True))
            return 0 if result["homometric"] else 1
    except (ValueError, ArithmeticError, KeyError, OSError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
