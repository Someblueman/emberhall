#!/usr/bin/env python3
"""Exact labeled stamp stacks; Python 3.10+, no third-party dependencies.

The tuple is the left-to-right layer list, NOT the inverse position map used
in the paper's inequalities. Face zero's labeled side points right.
"""
from __future__ import annotations

import argparse
from collections.abc import Iterator

Stack = tuple[int, ...]


def check_assignment(assignment: str) -> None:
    if any(crease not in "MV" for crease in assignment):
        raise ValueError("assignment must contain only M and V")


def positions(stack: Stack) -> list[int]:
    if sorted(stack) != list(range(len(stack))) or not stack:
        raise ValueError("stack must be a permutation of 0 through n-1")
    result = [0] * len(stack)
    for rank, face in enumerate(stack):
        result[face] = rank
    return result


def crosses(a: int, b: int, c: int, d: int) -> bool:
    """Strictly interleaved endpoints; containment and disjointness are legal."""
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    return a < c < b < d or c < a < d < b


def violations(stack: Stack, assignment: str) -> list[str]:
    """Direct Definition 2.1 check, independent of the insertion search."""
    check_assignment(assignment)
    pos = positions(stack)
    if len(stack) != len(assignment) + 1:
        raise ValueError("n faces require n-1 crease directions")
    failures = []
    for i, crease in enumerate(assignment):
        if (pos[i] > pos[i + 1]) != ((crease == "M") == (i % 2 == 0)):
            failures.append(f"orientation at crease {i}-{i + 1} ({crease})")
    for i in range(len(assignment)):
        for j in range(i + 2, len(assignment), 2):
            if crosses(pos[i], pos[i + 1], pos[j], pos[j + 1]):
                side = "top" if i % 2 == 0 else "bottom"
                failures.append(f"{side} crossing: {i}-{i + 1} with {j}-{j + 1}")
    return failures


def insertions(stack: Stack, crease: str) -> Iterator[Stack]:
    """Extend a legal prefix by one face, testing only the new arc.

    Deleting the largest label is unique and preserves legality. Hence every
    stack is reached exactly once. This deliberately simple search tries all
    gaps; it is not the authors' constant-amortized-time algorithm.
    """
    check_assignment(crease)
    if len(crease) != 1:
        raise ValueError("one new crease is required")
    n = len(stack)
    i = n - 1
    pos = positions(stack)
    for gap in range(n + 1):
        shifted = [rank + (rank >= gap) for rank in pos]
        if (shifted[i] > gap) != ((crease == "M") == (i % 2 == 0)):
            continue
        if any(crosses(shifted[i], gap, shifted[j], shifted[j + 1])
               for j in range(i % 2, i, 2)):
            continue
        yield stack[:gap] + (n,) + stack[gap:]


def extensions(stack: Stack, remaining: str) -> Iterator[Stack]:
    """All completions of a known legal prefix, in insertion-gap order."""
    check_assignment(remaining)
    positions(stack)
    if not remaining:
        yield stack
        return
    for child in insertions(stack, remaining[0]):
        yield from extensions(child, remaining[1:])


def stacks(assignment: str) -> Iterator[Stack]:
    check_assignment(assignment)
    yield from extensions((0,), assignment)


def nested_prefix(mountain: Stack, valley_length: int) -> Stack:
    """Replace the final face by a tightly nested valley run in its next gap.

    Precondition: mountain is a legal M-only stack. All new faces stay in the
    gap adjacent to its endpoint on the required side; old orders are fixed.
    """
    if valley_length < 1:
        raise ValueError("valley length must be positive")
    a = len(mountain) - 1
    if a < 1 or violations(mountain, "M" * a):
        raise ValueError("prefix must be a legal nonempty mountain run")
    block = (a,) + tuple(a + i for i in range(2, valley_length + 1, 2))
    last_odd = valley_length if valley_length % 2 else valley_length - 1
    block += tuple(a + i for i in range(last_odd, 0, -2))
    if a % 2:
        block = block[::-1]
    at = mountain.index(a)
    return mountain[:at] + block + mountain[at + 1:]


def first_inward(mountain: Stack) -> int | None:
    """First label that was inserted internally; None means outward throughout."""
    for face in range(2, len(mountain)):
        prefix = tuple(i for i in mountain if i <= face)
        if prefix[0] != face and prefix[-1] != face:
            return face
    return None


def family_prefix(k: int) -> Stack:
    """The exterior mountain spiral followed by a tightly nested valley run."""
    if k < 2:
        raise ValueError("family requires k >= 2")
    mountain = tuple(range(k if k % 2 else k - 1, 0, -2)) + (0,) + tuple(
        range(2, k + 1, 2))
    return nested_prefix(mountain, k)


def nested_family(k: int) -> Iterator[tuple[int | None, Stack]]:
    """All k M-only prefixes, each followed by a tightly nested V run."""
    if k < 2:
        raise ValueError("family requires k >= 2")
    for mountain in stacks("M" * k):
        yield first_inward(mountain), nested_prefix(mountain, k)


def nest_valleys(stack: Stack, number: int) -> Stack:
    """Add valley faces in the adjacent required gap of a legal prefix."""
    if number < 0:
        raise ValueError("number of additional valley faces cannot be negative")
    positions(stack)
    for _ in range(number):
        last = len(stack) - 1
        gap = stack.index(last) + (last % 2 == 0)
        stack = stack[:gap] + (last + 1,) + stack[gap:]
    return stack


def first_valley_family(k: int) -> Iterator[Stack]:
    """Any legal first V after M^k, then k-1 adjacent valley insertions."""
    if k < 2:
        raise ValueError("family requires k >= 2")
    for mountain in stacks("M" * k):
        for first in insertions(mountain, "V"):
            yield nest_valleys(first, k - 1)


def diagram(stack: Stack, assignment: str) -> str:
    """A terminal arc chart: each line identifies its crease and endpoints.

    Every arc gets a row. All top rows inhabit one half-plane, all bottom
    rows the other; endpoint interleaving, not row height, decides crossings.
    """
    pos = positions(stack)
    width = max(3, len(str(len(stack) - 1)) + 1)
    lines = []
    for side in (0, 1):
        if side == 1:
            lines.append("       " + "".join(f"{x:>{width}}" for x in stack))
        for i in range(side, len(assignment), 2):
            a, b = sorted((pos[i], pos[i + 1]))
            row = [" "] * (width * len(stack))
            left, right = width * a + width - 1, width * b + width - 1
            row[left:right + 1] = "+" + "-" * (right - left - 1) + "+"
            lines.append(f"{assignment[i]}{i:>2}-{i + 1:<2} " + "".join(row).rstrip())
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=2, help="equal run length (default 2)")
    parser.add_argument("--assignment", help="literal M/V string, overrides --k")
    parser.add_argument("--list", action="store_true", help="print every labeled stack")
    parser.add_argument("--draw", action="store_true", help="print terminal arc charts")
    family = parser.add_mutually_exclusive_group()
    family.add_argument("--family", action="store_true", help="complete the exterior prefix")
    family.add_argument("--nested-family", action="store_true", help="complete all k nested prefixes")
    family.add_argument("--first-valley-family", action="store_true",
                        help="allow every legal first valley gap, then nest")
    args = parser.parse_args()
    if args.k < 2:
        parser.error("--k must be at least 2")
    if (args.family or args.nested_family or args.first_valley_family) and args.assignment is not None:
        parser.error("family options cannot be combined with --assignment")
    assignment = args.assignment if args.assignment is not None else (
        "M" * args.k + "V" * args.k + "M" * args.k)
    try:
        check_assignment(assignment)
    except ValueError as exc:
        parser.error(str(exc))
    if args.family:
        prefix = family_prefix(args.k)
        print("prefix:", *prefix)
        found = extensions(prefix, "M" * args.k)
    elif args.nested_family:
        found = (order for _, prefix in nested_family(args.k)
                 for order in extensions(prefix, "M" * args.k))
    elif args.first_valley_family:
        found = (order for prefix in first_valley_family(args.k)
                 for order in extensions(prefix, "M" * args.k))
    else:
        found = stacks(assignment)
    count = 0
    for stack in found:
        count += 1
        if args.list or args.draw:
            print(f"{count}:", *stack)
        if args.draw:
            print(diagram(stack, assignment))
    print(f"{assignment or '(empty)'}: {count} legal labeled stacks")
    if args.assignment is None:
        if args.family:
            print(f"family theorem: {args.k} (see first-family.md)")
        elif args.nested_family:
            print(f"nested-family theorem: {args.k**2 + 1} (see first-family.md)")
        elif args.first_valley_family:
            expected = 5 if args.k == 2 else args.k**2 + args.k + 3
            print(f"first-valley-family theorem: {expected} (see first-family.md)")
        else:
            k = args.k
            print(f"published conjecture: {(9*k**3 - 25*k**2 + 30*k - 12)//2}")


if __name__ == "__main__":
    main()
