#!/usr/bin/env python3
"""Squared-distance residue checker for one tripod.

Q = sum over pairs of dist^2. Homometric sets need equal Q, hence
equal Q mod 4. Cross-arm dist = du+dv; same-arm dist = |du-dv| =
du+dv-2*min, so dist^2 = (du+dv)^2 - 4*du*dv on one arm and
(du+dv)^2 across. Hence Q = P - 4*M2 with
P = sum (du+dv)^2 = (K-2)*sum(d^2) + sum(d)^2 over the set, so
Q mod 4 = (K-2)*sum(d^2) + sum(d)^2 mod 4 from depths alone.
Depths with the same d mod 4 contribute identically mod 4
(d mod 4, d^2 mod 4 = 0,1,0,1), so exact feasibility reduces to
counting vertices per d mod 4 class. This searches all allocations
of the unused slack and one side; the other side is forced.

Usage: python3 q_residue_check.py          (six resistant triples)
       python3 q_residue_check.py A B C   (one triple)
Requires: Python 3.10+, standard library only.
"""
from __future__ import annotations

import sys

RESISTANT = [(45, 20, 8), (55, 20, 5), (45, 30, 8),
             (40, 30, 14), (55, 50, 35), (55, 50, 23)]


def type_counts(a: int, b: int, c: int) -> list[int]:
    depths = [0] + list(range(1, a + 1)) + list(range(1, b + 1)) \
        + list(range(1, c + 1))
    total = [0, 0, 0, 0]
    for d in depths:
        total[d % 4] += 1
    return total


def target(a: int, b: int, c: int) -> int:
    return (1 + a + b + c) // 2 - 1


def q_mod4(counts: list[int], k: int) -> int:
    r1 = sum(i * counts[i] for i in range(4)) % 4
    r2 = sum(counts[i] for i in (1, 3)) % 4
    return ((k - 2) * r2 + r1 * r1) % 4


def _unused(counts: list[int], slack: int) -> list[list[int]]:
    out = []
    for u0 in range(min(slack, counts[0]) + 1):
        for u1 in range(min(slack - u0, counts[1]) + 1):
            for u2 in range(min(slack - u0 - u1, counts[2]) + 1):
                u3 = slack - u0 - u1 - u2
                if 0 <= u3 <= counts[3]:
                    out.append([u0, u1, u2, u3])
    return out


def find_equal_pair(total: list[int], k: int) -> tuple[bool, dict | None]:
    """Exact search for two disjoint K-sets with equal Q mod 4."""
    slack = sum(total) - 2 * k
    if slack < 0:
        return False, None
    for u in _unused(total, slack):
        rem = [total[i] - u[i] for i in range(4)]
        for n0 in range(min(k, rem[0]) + 1):
            for n1 in range(min(k - n0, rem[1]) + 1):
                for n2 in range(min(k - n0 - n1, rem[2]) + 1):
                    n3 = k - n0 - n1 - n2
                    if n3 < 0 or n3 > rem[3]:
                        continue
                    n = [n0, n1, n2, n3]
                    r = [rem[i] - n[i] for i in range(4)]
                    if q_mod4(n, k) == q_mod4(r, k):
                        return True, {"unused": u, "left": n,
                                      "right": r, "Q": q_mod4(n, k)}
    return False, None


def analyse(a: int, b: int, c: int) -> dict:
    total = type_counts(a, b, c)
    k = target(a, b, c)
    found, witness = find_equal_pair(total, k)
    return {"lengths": (a, b, c), "K": k, "counts": total,
            "pair": found, "witness": witness}


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        triples: list[tuple[int, int, int]] = list(RESISTANT)
    elif len(argv) == 4:
        triples = [(int(argv[1]), int(argv[2]), int(argv[3]))]
    else:
        print("usage: q_residue_check.py [A B C]", file=sys.stderr)
        return 2
    for a, b, c in triples:
        r = analyse(a, b, c)
        print(f"{tuple(map(int, (a, b, c)))} K {r['K']} "
              f"counts {r['counts']} pair {r['pair']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
