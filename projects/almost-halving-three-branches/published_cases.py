#!/usr/bin/env python3
"""Exact witnesses for supported published tripod constructions; no search oracle.

Vertices are (arm, depth), with centre (0, 0) and arms numbered 1, 2, 3.
Only Python's standard library is used. See PUBLISHED_CASES.md for proofs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations, permutations
import json
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
    return {"homometric": not difference, "size": len(left), "target": target,
            "meets_target": not difference and len(left) >= target,
            "left_profile": dict(sorted(lp.items())),
            "right_profile": dict(sorted(rp.items())), "difference": difference}


def path_pair(lengths: Lengths) -> Pair:
    i, j = sorted(range(1, 4), key=lambda k: lengths[k - 1], reverse=True)[:2]
    path = ([(i, d) for d in range(lengths[i - 1], 0, -1)] + [CENTRE]
            + [(j, d) for d in range(1, lengths[j - 1] + 1)])
    k = len(path) // 2
    return path[:k], path[k:2 * k]


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


def construct(lengths: object, kind: str = "best") -> tuple[str, Pair]:
    lengths = validate_lengths(lengths)
    candidates = []
    if kind in {"best", "path"}:
        candidates.append(("path", path_pair(lengths)))
    for order in permutations((1, 2, 3)):
        for name, builder in (("alternating", alternating_pair), ("block", block_pair)):
            if kind not in {"best", name}:
                continue
            try:
                pair = builder(lengths, order)
            except ValueError:
                continue
            candidates.append((f"{name}{order}", pair))
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


def demo() -> None:
    examples = [((8, 5, 2), "path"), ((9, 7, 4), "alternating"),
                ((9, 7, 5), "alternating"), ((11, 7, 3), "block"),
                ((13, 7, 3), "block"), ((14, 7, 3), "block"),
                ((23, 12, 6), "best")]
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
    parser.add_argument("--construction", choices=("best", "path", "alternating", "block"),
                        default="best")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--check", metavar="JSON", help="read a witness JSON file, or - for stdin")
    args = parser.parse_args()
    if (args.demo or args.check) and args.lengths:
        parser.error("lengths cannot accompany --demo or --check")
    try:
        if args.demo:
            demo()
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
