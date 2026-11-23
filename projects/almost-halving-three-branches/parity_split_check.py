#!/usr/bin/env python3
"""Even/odd parity-split checker for one tripod.

For lengths (a, b, c) the tree has depths 0 (centre) and 1..length per
arm. dist(u, v) mod 2 = (depth(u) + depth(v)) mod 2, so a k-set with
E even-depth and K-E odd-depth vertices has C(E,2)+C(K-E,2) even
distance pairs. Two k-sets can be homometric only if their even-pair
counts agree, i.e. their splits are equal or complementary, and they
fit disjointly. This prints whether a disjoint parity-matching pair
exists; True means parity does not rule out a witness, False would be
a proved parity obstruction (none occurs on the resistant set).

Usage: python3 parity_split_check.py          (six resistant triples)
       python3 parity_split_check.py A B C   (one triple)
Requires: Python 3.10+, standard library only.
"""
from __future__ import annotations

import sys

RESISTANT = [(45, 20, 8), (55, 20, 5), (45, 30, 8),
             (40, 30, 14), (55, 50, 35), (55, 50, 23)]


def parity_counts(a: int, b: int, c: int) -> tuple[int, int]:
    depths = [0] + list(range(1, a + 1)) + list(range(1, b + 1)) \
        + list(range(1, c + 1))
    ne = sum(1 for d in depths if d % 2 == 0)
    return ne, len(depths) - ne


def target(a: int, b: int, c: int) -> int:
    return (1 + a + b + c) // 2 - 1


def analyse(a: int, b: int, c: int) -> dict:
    ne, no = parity_counts(a, b, c)
    k = target(a, b, c)
    lo, hi = max(0, k - no), min(k, ne)

    def even(e: int) -> int:
        return e * (e - 1) // 2 + (k - e) * (k - e - 1) // 2

    same = [e for e in range(lo, hi + 1) if 2 * e <= ne and 2 * (k - e) <= no]
    pair = any(
        e1 + e2 <= ne and (k - e1) + (k - e2) <= no and even(e1) == even(e2)
        for e1 in range(lo, hi + 1) for e2 in range(lo, hi + 1)
    )
    return {"lengths": (a, b, c), "K": k, "Ne": ne, "No": no,
            "same": same, "pair": pair}


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        triples: list[tuple[int, int, int]] = list(RESISTANT)
    elif len(argv) == 4:
        triples = [(int(argv[1]), int(argv[2]), int(argv[3]))]
    else:
        print("usage: parity_split_check.py [A B C]", file=sys.stderr)
        return 2
    for a, b, c in triples:
        r = analyse(a, b, c)
        print(f"{tuple(map(int, (a, b, c)))} K {r['K']} Ne {r['Ne']} "
              f"No {r['No']} same {r['same']} pair {r['pair']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
