"""Exact optima for the smallest three-branched trees, by exhaustive search.

For a three-armed tree T(a, b, c) the project's target size is
``floor((1 + a + b + c) / 2) - 1``: half the tree, less one.  This command
computes the true optimum - the largest pair of disjoint vertex sets of equal
size with identical distance profiles - by exhausting every possibility.  There
is no construction menu, no heuristic and no randomness in it: every subset of
the tree is enumerated, its distance profile is computed, subsets are grouped by
profile, and the largest disjoint equal-sized pair inside a group is the optimum
for that profile.  The optimum is the largest over all groups.

Standard library only; Python 3.10+.

One command, from a clone of Emberhall at the repository root::

    python3 projects/almost-halving-three-branches/small_triples.py --limit 12

It prints one line per triple,

    a b c optimum target attained

and a final ``TOTAL <triples> attained <count>`` line, and exits 0.

The census is finite, so it settles neither the universal target nor the open
class ``t = 1 (mod 2660)``; see SMALL_TRIPLES.md for what it does and does not
show, and COVERAGE_MAP.md for the project's own account of the open region.
"""

from __future__ import annotations

import argparse


def arm_of(vertex: int, a: int, b: int) -> int:
    """Which arm a vertex is on; 0 is the centre."""
    if vertex == 0:
        return 0
    if vertex <= a:
        return 1
    if vertex <= a + b:
        return 2
    return 3


def depth_of(vertex: int, a: int, b: int) -> int:
    """The distance from the centre; 0 for the centre itself."""
    if vertex == 0:
        return 0
    if vertex <= a:
        return vertex
    if vertex <= a + b:
        return vertex - a
    return vertex - a - b


def distance(u: int, v: int, a: int, b: int) -> int:
    """The distance between two vertices of the tree."""
    if u == 0:
        return depth_of(v, a, b)
    if v == 0:
        return depth_of(u, a, b)
    if arm_of(u, a, b) == arm_of(v, a, b):
        return abs(depth_of(u, a, b) - depth_of(v, a, b))
    return depth_of(u, a, b) + depth_of(v, a, b)


def optimum(a: int, b: int, c: int) -> int:
    """The exact largest equal-sized disjoint pair with identical profiles."""
    total = 1 + a + b + c
    groups: dict[str, list[int]] = {}
    for mask in range(1 << total):
        members = [vertex for vertex in range(total) if mask & (1 << vertex)]
        counts: dict[int, int] = {}
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                gap = distance(members[i], members[j], a, b)
                counts[gap] = counts.get(gap, 0) + 1
        signature = ",".join(f"{gap}:{counts[gap]}" for gap in sorted(counts))
        groups.setdefault(signature, []).append(mask)
    best = 0
    for masks in groups.values():
        for i in range(len(masks)):
            for j in range(i + 1, len(masks)):
                if masks[i] & masks[j]:
                    continue
                size = bin(masks[i]).count("1")
                if size != bin(masks[j]).count("1"):
                    continue
                if size > best:
                    best = size
    return best


def target(a: int, b: int, c: int) -> int:
    """The project's target size: half the tree, less one."""
    return (1 + a + b + c) // 2 - 1


def triples(limit: int):
    """Every triple with a >= b >= c >= 1 and a + b + c <= limit."""
    for a in range(1, limit + 1):
        for b in range(1, a + 1):
            for c in range(1, b + 1):
                if a + b + c > limit:
                    continue
                yield a, b, c


def rows(limit: int) -> list[tuple[int, int, int, int, int, str]]:
    """One row per triple: arms, exact optimum, target, and whether it is met."""
    result = []
    for a, b, c in triples(limit):
        best = optimum(a, b, c)
        goal = target(a, b, c)
        result.append((a, b, c, best, goal, "yes" if best >= goal else "no"))
    return result


def table(limit: int) -> str:
    """The census as text, one line per triple plus the summary line."""
    lines = []
    attained = 0
    for a, b, c, best, goal, met in rows(limit):
        lines.append(f"{a} {b} {c} {best} {goal} {met}")
        if met == "yes":
            attained += 1
    lines.append(f"TOTAL {len(lines)} attained {attained}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=12,
                        help="census every triple with a + b + c <= LIMIT (default 12)")
    args = parser.parse_args(argv)
    if args.limit < 3:
        parser.error("--limit must be at least 3")
    print(table(args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
