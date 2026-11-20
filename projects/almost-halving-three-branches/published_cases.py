#!/usr/bin/env python3
"""Exact witnesses for published and proved tripod families; no search oracle.

Vertices are (arm, depth), with centre (0, 0) and arms numbered 1, 2, 3.
Only Python's standard library is used. See PUBLISHED_CASES.md for proofs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations, permutations, product
import json
from math import gcd
from pathlib import Path
import sys

Vertex = tuple[int, int]
Lengths = tuple[int, int, int]
Pair = tuple[list[Vertex], list[Vertex]]
CENTRE = (0, 0)


def validate_lengths(lengths: object) -> Lengths:
    if (not isinstance(lengths, (list, tuple)) or len(lengths) != 3
            or any(type(n) is not int or n < 1 for n in lengths)):
        raise ValueError("lengths must contain three positive integers")
    return tuple(lengths)


def validate_vertices(lengths: Lengths, vertices: object) -> list[Vertex]:
    if not isinstance(vertices, (list, tuple)):
        raise ValueError("a vertex set must be a list")
    result = []
    for vertex in vertices:
        if (not isinstance(vertex, (list, tuple)) or len(vertex) != 2
                or any(type(n) is not int for n in vertex)):
            raise ValueError("each vertex must be an integer [arm, depth]")
        arm, depth = vertex
        if (arm, depth) != CENTRE and not (
                1 <= arm <= 3 and 1 <= depth <= lengths[arm - 1]):
            raise ValueError(f"vertex {vertex} is outside the tree")
        result.append((arm, depth))
    if len(result) != len(set(result)):
        raise ValueError("duplicate vertex in a set")
    return result


def distance(u: Vertex, v: Vertex) -> int:
    """Unique tree path: subtract on one arm, add across the centre."""
    return abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]


def profile(vertices: list[Vertex]) -> Counter[int]:
    return Counter(distance(u, v) for u, v in combinations(vertices, 2))


def certified_upper_bound(lengths: Lengths) -> int:
    """Disjointness, improved by the proved full-partition residue obstruction."""
    bound = (1 + sum(lengths)) // 2
    period = gcd(*(n + 1 for n in lengths))
    if period % 2 == 0 and sum((n + 1) // period for n in lengths) % 2 == 1:
        bound -= 1
    return bound


def check_pair(lengths: object, left: object, right: object) -> dict:
    lengths = validate_lengths(lengths)
    left = validate_vertices(lengths, left)
    right = validate_vertices(lengths, right)
    if set(left) & set(right):
        raise ValueError("the two sets overlap")
    if len(left) != len(right):
        raise ValueError("the two sets have different sizes")
    lp, rp = profile(left), profile(right)
    # Signed differences, including multiplicities missing from either side.
    difference = {d: lp[d] - rp[d] for d in sorted(lp.keys() | rp.keys())
                  if lp[d] != rp[d]}
    target = (1 + sum(lengths)) // 2 - 1
    bound = certified_upper_bound(lengths)
    return {"homometric": not difference, "size": len(left), "target": target,
            "meets_target": not difference and len(left) >= target,
            "upper_bound": bound, "attains_bound": not difference and len(left) == bound,
            "left_profile": dict(sorted(lp.items())),
            "right_profile": dict(sorted(rp.items())), "difference": difference}


def path_pair(lengths: Lengths) -> Pair:
    i, j = sorted(range(1, 4), key=lambda k: lengths[k - 1], reverse=True)[:2]
    path = ([(i, d) for d in range(lengths[i - 1], 0, -1)] + [CENTRE]
            + [(j, d) for d in range(1, lengths[j - 1] + 1)])
    k = len(path) // 2
    return path[:k], path[k:2 * k]


def separated_path_pair(lengths: Lengths) -> Pair:
    """One path inside the longest arm; one through the other arms and centre."""
    i, j, k = sorted(range(1, 4), key=lambda arm: lengths[arm - 1], reverse=True)
    size = min(lengths[i - 1], 1 + lengths[j - 1] + lengths[k - 1])
    other = ([(j, d) for d in range(lengths[j - 1], 0, -1)] + [CENTRE]
             + [(k, d) for d in range(1, lengths[k - 1] + 1)])
    return [(i, d) for d in range(1, size + 1)], other[:size]


def alternating_pair(lengths: Lengths, order: tuple[int, int, int]) -> Pair:
    i, j, t = order
    a, b, c = (lengths[k - 1] for k in order)
    if a < b:
        raise ValueError("alternating construction requires first arm >= second")
    left = [CENTRE] + [(i, d) for d in range(1, b)]
    left += [(t, d) for d in range(2, 2 * (c // 2) + 1, 2)]
    right = [(j, d) for d in range(1, b + 1)]
    right += [(t, d) for d in range(1, 2 * (c // 2), 2)]
    return left, right


def block_pair(lengths: Lengths, order: tuple[int, int, int]) -> Pair:
    i, j, t = order
    a, b, c = (lengths[k - 1] for k in order)
    if not a >= b > c:
        raise ValueError("printed block construction requires first >= second > third")
    x = b - c
    quotient, remainder = divmod(a + 1, x)
    last_block = quotient - 1 if quotient % 2 else quotient
    last_depth = (last_block + 1) * x - 1
    if last_depth > a:
        raise ValueError(f"printed Construction 16 overruns arm: endpoint {last_depth} > {a}"
                         f" (quotient={quotient}, remainder={remainder})")
    left, right = [], []
    for block in range(last_block + 1):
        for depth in range(block * x, (block + 1) * x):
            vertex = CENTRE if depth == 0 else (i, depth)
            (left if block % 2 == 0 else right).append(vertex)
    left += [(t, d) for d in range(1, c + 1)]
    right += [(j, d) for d in range(1, b + 1)]
    return left, right


def _base_candidates(lengths: Lengths, kind: str) -> list[tuple[str, Pair]]:
    candidates = []
    if kind in {"best", "path"}:
        candidates.append(("path", path_pair(lengths)))
    if kind in {"best", "separated-path"}:
        candidates.append(("separated-path", separated_path_pair(lengths)))
    order = sorted(range(1, 4), key=lambda arm: lengths[arm - 1], reverse=True)
    a, b, c = (lengths[i - 1] for i in order)
    if kind == "best" and c >= 2 and (a, b) == (4 * c - 1, 2 * c):
        family = gap_family_witness(c)
        pair = tuple([CENTRE if v == CENTRE else (order[v[0] - 1], v[1]) for v in part]
                     for part in (family["left"], family["right"]))
        candidates.append((family["construction"], pair))
    t = (c + 1) // 2
    if kind == "best" and t >= 2 and t % 2 == 0 and (a, b, c) == (
            4 * t - 1, 3 * t - 1, 2 * t - 1):
        family = sharp_family_witness(t)
        pair = tuple([CENTRE if v == CENTRE else (order[v[0] - 1], v[1]) for v in part]
                     for part in (family["left"], family["right"]))
        candidates.append((family["construction"], pair))
    for order in permutations((1, 2, 3)):
        for name, builder in (("alternating", alternating_pair), ("block", block_pair)):
            if kind not in {"best", name}:
                continue
            try:
                pair = builder(lengths, order)
            except ValueError:
                continue
            candidates.append((f"{name}{order}", pair))
    return candidates


def construct(lengths: object, kind: str = "best") -> tuple[str, Pair]:
    lengths = validate_lengths(lengths)
    if kind == "best":
        candidates = []
        # A target pair can omit at most three vertices. Every prefix subtree
        # is isometric in the original tree; no repaired formula is introduced.
        for trim in product(range(4), repeat=3):
            if sum(trim) > 3:
                continue
            reduced = tuple(n - d for n, d in zip(lengths, trim))
            if min(reduced) < 1:
                continue
            for name, pair in _base_candidates(reduced, kind):
                label = name if not any(trim) else f"trim {trim}: {name}"
                candidates.append((label, pair))
    else:
        candidates = _base_candidates(lengths, kind)
    if not candidates:
        raise ValueError(f"no supported {kind} construction for {lengths}; no endpoint repair used")
    return max(candidates, key=lambda item: len(item[1][0]))


def witness(lengths: object, kind: str = "best") -> dict:
    lengths = validate_lengths(lengths)
    name, (left, right) = construct(lengths, kind)
    result = check_pair(lengths, left, right)
    if not result["homometric"]:
        raise ValueError(f"construction failed its exact check: {result['difference']}")
    return {"lengths": lengths, "construction": name, "left": left, "right": right,
            **result}


def gap_family_witness(t: int) -> dict:
    """A separate proved maximum pair for (4t-1, 2t, t), t >= 2.

    This is not an endpoint repair of Construction 16. See the signed-shell
    proof in PUBLISHED_CASES.md; priority remains provisional.
    """
    if type(t) is not int or t < 2:
        raise ValueError("gap-family parameter must be an integer >= 2")
    h, e = divmod(t, 2)
    lengths = (4 * t - 1, 2 * t, t)
    a_minus = (set(range(h + 1 + e, 2 * h + e))
               | set(range(2 * h + 1 + e, 3 * h + e))
               | set(range(5 * h + 2 * e, 6 * h - 1 + 2 * e))
               | set(range(6 * h + 2 * e, 7 * h - 1 + 2 * e)))
    b_plus = set(range(1, h)) | set(range(2 * h + 1 + e, 3 * h + e))
    c_plus = set(range(h + 1 + e, 2 * h + e))
    left, right = [], [CENTRE]
    for arm, length in enumerate(lengths, 1):
        for d in range(1, length + 1):
            if e and arm == 1 and d == length:
                continue  # Omit only the longest-arm tip when t is odd.
            positive = d not in a_minus if arm == 1 else d in (b_plus if arm == 2 else c_plus)
            (left if positive else right).append((arm, d))
    result = check_pair(lengths, left, right)
    if not result["homometric"] or result["size"] != (7 * t) // 2:
        raise ValueError("signed-shell family failed its exact check")
    return {"lengths": lengths, "construction": f"signed-shell family t={t}",
            "left": left, "right": right, **result}


def sharp_family_witness(t: int) -> dict:
    """Optimal half-minus-one sets for (4t-1, 3t-1, 2t-1), positive even t."""
    if type(t) is not int or t < 2 or t % 2:
        raise ValueError("sharp-family parameter must be a positive even integer")
    lengths = (4 * t - 1, 3 * t - 1, 2 * t - 1)
    left, right = [], [CENTRE]
    for arm, length in enumerate(lengths, 1):
        for depth in range(1, length + 1):
            if arm == 1:
                if depth in (t - 1, 4 * t - 1):
                    continue
                positive = not (t <= depth <= 3 * t) and depth % 2 == 1
            elif arm == 2:
                positive = depth % 2 == 1 or depth in (t, 2 * t)
            else:
                positive = depth != t
            (left if positive else right).append((arm, depth))
    result = check_pair(lengths, left, right)
    if not result["homometric"] or not result["attains_bound"]:
        raise ValueError("sharp family failed its exact check")
    return {"lengths": lengths, "construction": f"sharp family t={t}",
            "left": left, "right": right, **result}


def demo() -> None:
    examples = [((8, 5, 2), "path"), ((9, 7, 4), "alternating"),
                ((9, 7, 5), "alternating"), ((11, 7, 3), "block"),
                ((13, 7, 3), "block"), ((14, 7, 3), "block"),
                ((23, 12, 6), "path")]
    for lengths, kind in examples:
        result = witness(lengths, kind)
        print(json.dumps(result, sort_keys=True))
    try:
        block_pair((15, 7, 3), (1, 2, 3))
    except ValueError as error:
        print(f"EXPECTED REJECTION: {error}")
    left, right = alternating_pair((10, 7, 5), (1, 2, 3))
    left[left.index(CENTRE)] = (1, 10)
    result = check_pair((10, 7, 5), left, right)
    if result["homometric"]:
        raise ValueError("the deliberately altered pair unexpectedly passed")
    print("ALTERED PAIR REJECTED: " + json.dumps(result, sort_keys=True))
    print("PASS: 7 supported witnesses; printed overrun and altered pair rejected.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lengths", nargs="*", type=int, metavar="LENGTH")
    parser.add_argument("--construction",
                        choices=("best", "path", "separated-path", "alternating", "block"),
                        default="best")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--check", metavar="JSON", help="read a witness JSON file, or - for stdin")
    mode.add_argument("--gap-family", type=int, metavar="T",
                      help="maximum pair for the proved family (4T-1, 2T, T), T >= 2")
    mode.add_argument("--sharp-family", type=int, metavar="T",
                      help="optimal pair for (4T-1, 3T-1, 2T-1), positive even T")
    args = parser.parse_args()
    if (args.demo or args.check or args.gap_family is not None
            or args.sharp_family is not None) and args.lengths:
        parser.error("lengths cannot accompany a named mode")
    try:
        if args.demo:
            demo()
        elif args.gap_family is not None:
            print(json.dumps(gap_family_witness(args.gap_family), sort_keys=True))
        elif args.sharp_family is not None:
            print(json.dumps(sharp_family_witness(args.sharp_family), sort_keys=True))
        elif args.check:
            raw = sys.stdin.read() if args.check == "-" else Path(args.check).read_text()
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("witness JSON must be an object")
            result = check_pair(payload["lengths"], payload["left"], payload["right"])
            print(json.dumps(result, sort_keys=True))
            return 0 if result["homometric"] else 1
        else:
            print(json.dumps(witness(args.lengths, args.construction), sort_keys=True))
    except (ValueError, KeyError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
