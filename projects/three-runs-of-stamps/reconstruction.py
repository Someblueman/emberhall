#!/usr/bin/env python3
"""Independent checks of Sorrel's nested stamp family; Python 3.10+."""
from __future__ import annotations

import argparse
from collections.abc import Iterator
from itertools import permutations

Stack = tuple[int, ...]


def legal(order: Stack, directions: str) -> bool:
    """Check directions, then recognize each side's noncrossing matching.

    Scanning a side's arc endpoints left to right must be a well-nested
    push/pop word. This uses no interval-pair test or author implementation.
    """
    n = len(directions) + 1
    if len(order) != n or set(order) != set(range(n)):
        return False
    if any(d not in "MV" for d in directions):
        return False
    rank = {face: i for i, face in enumerate(order)}
    for edge, direction in enumerate(directions):
        expected_right = (edge % 2 == 1) == (direction == "M")
        if (rank[edge + 1] > rank[edge]) != expected_right:
            return False
    for side in (0, 1):
        opened: set[int] = set()
        nested: list[int] = []
        for face in order:
            edge = face if face % 2 == side else face - 1
            if edge < 0 or edge >= n - 1:
                continue
            if edge not in opened:
                opened.add(edge)
                nested.append(edge)
            elif not nested or nested.pop() != edge:
                return False
        if nested:
            return False
    return True


def extend(prefix: Stack, directions: str) -> Iterator[Stack]:
    """Recheck the complete matching after every insertion of the next label."""
    if not legal(prefix, directions[:len(prefix) - 1]):
        raise ValueError("prefix is not legal for the supplied directions")
    if len(prefix) == len(directions) + 1:
        yield prefix
        return
    label = len(prefix)
    for gap in range(label + 1):
        child = prefix[:gap] + (label,) + prefix[gap:]
        if legal(child, directions[:label]):
            yield from extend(child, directions)


def brute(directions: str) -> set[Stack]:
    """Full permutation oracle, for genuinely small instances only."""
    return {p for p in permutations(range(len(directions) + 1)) if legal(p, directions)}


def adjacent_valley(prefix: Stack) -> Stack:
    """Insert the next valley in the immediate permitted gap."""
    last = len(prefix) - 1
    gap = prefix.index(last) + (last % 2 == 0)
    return prefix[:gap] + (last + 1,) + prefix[gap:]


def nested_prefix(mountain: Stack, depth: int) -> Stack:
    if depth < 1 or not legal(mountain, "M" * (len(mountain) - 1)):
        raise ValueError("a legal mountain prefix and positive depth are required")
    for _ in range(depth):
        mountain = adjacent_valley(mountain)
    return mountain


def inward_step(mountain: Stack) -> int | None:
    for label in range(2, len(mountain)):
        old = tuple(x for x in mountain if x <= label)
        if old[0] != label and old[-1] != label:
            return label
    return None


def collar_reduce(order: Stack, prefix_size: int) -> Stack:
    """Erase the added valley and first mountain, then close the labels."""
    n = prefix_size
    return tuple(x if x < n else x - 2 for x in order if x not in (n, n + 1))


def collar_expand(order: Stack, prefix_size: int) -> Stack:
    """Inverse of collar_reduce on the continuing branch."""
    n = prefix_size
    a, b = n - 2, n - 1
    relabeled = tuple(x if x < n else x + 2 for x in order)
    at_b = relabeled.index(b)
    # The inserted pair lies between B and A, immediately beside B.
    if relabeled.index(a) > at_b:
        return relabeled[:at_b + 1] + (n, n + 1) + relabeled[at_b + 1:]
    return relabeled[:at_b] + (n + 1, n) + relabeled[at_b:]


def is_stopped(order: Stack, prefix_size: int) -> bool:
    """The second mountain enters the short gap between C and D."""
    n = prefix_size
    positions = {x: i for i, x in enumerate(order)}
    return min(positions[n], positions[n + 1]) < positions[n + 2] < max(
        positions[n], positions[n + 1])


def collar_check(prefix: Stack, directions: str, remaining: int) -> tuple[int, int]:
    """Check the actual bijection, never just an equality of two counts."""
    n = len(prefix)
    if remaining < 1 or not legal(prefix, directions):
        raise ValueError("a legal prefix and positive remaining length are required")
    if not directions.endswith("V") or abs(prefix.index(n - 1) - prefix.index(n - 2)) != 1:
        raise ValueError("the final valley must have adjacent endpoints")
    short = set(extend(prefix, directions + "M" * remaining))
    long = set(extend(adjacent_valley(prefix), directions + "V" + "M" * (remaining + 1)))
    stops = {p for p in long if is_stopped(p, n)}
    continuations = long - stops
    reduced = {collar_reduce(p, n) for p in continuations}
    expanded = {collar_expand(p, n) for p in short}
    if len(stops) != 1 or len(reduced) != len(continuations) or reduced != short:
        raise AssertionError((prefix, directions, remaining, "deletion", len(stops)))
    if expanded != continuations:
        raise AssertionError((prefix, directions, remaining, "insertion"))
    return len(short), len(long)


def census(a: int, b: int) -> list[tuple[int | None, int]]:
    """Count each nested-family member without using the claimed formula."""
    if a < 2 or b < 1:
        raise ValueError("mountain length >= 2 and valley length >= 1 required")
    result = []
    directions = "M" * a + "V" * b + "M" * b
    for mountain in extend((0,), "M" * a):
        count = sum(1 for _ in extend(nested_prefix(mountain, b), directions))
        result.append((inward_step(mountain), count))
    return sorted(result, key=lambda row: -1 if row[0] is None else row[0])


def first_valley_census(a: int, b: int) -> list[tuple[Stack, bool, int]]:
    """Any legal first V placement; every later V is adjacent."""
    if a < 2 or b < 2:
        raise ValueError("this enlarged family requires both lengths >= 2")
    result = []
    directions = "M" * a + "V" * b + "M" * b
    for mountain in extend((0,), "M" * a):
        adjacent = adjacent_valley(mountain)
        for first in extend(mountain, "M" * a + "V"):
            prefix = first
            for _ in range(b - 1):
                prefix = adjacent_valley(prefix)
            count = sum(1 for _ in extend(prefix, directions))
            result.append((prefix, first != adjacent, count))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mountains", type=int, default=4)
    parser.add_argument("--valleys", type=int, default=4)
    parser.add_argument("--first-valley", action="store_true",
                        help="also allow the first valley to skip old faces")
    args = parser.parse_args()
    try:
        if args.first_valley:
            rows = first_valley_census(args.mountains, args.valleys)
            for prefix, skipped, count in rows:
                print(f"{'skipped' if skipped else 'adjacent'} first valley: "
                      f"{count} completions | {' '.join(map(str, prefix))}")
            total = sum(row[2] for row in rows)
            expected = (args.mountains * args.valleys + 1 if args.mountains == 2
                        else (args.mountains + 1) * args.valleys + 3)
            name = "first-valley"
        else:
            rows = census(args.mountains, args.valleys)
            for turn, count in rows:
                print(f"first inward step {turn if turn is not None else 'none'}: {count}")
            total = sum(count for _, count in rows)
            expected = args.mountains * args.valleys + 1
            name = "nested"
    except ValueError as exc:
        parser.error(str(exc))
    print(f"{name} family total: {total}")
    print(f"reconstructed formula: {expected}")
    print("Restricted family only; the full three-run cubic is not proved.")


if __name__ == "__main__":
    main()
