#!/usr/bin/env python3
"""Heuristic search for a target-size equal-profile pair on one tripod.

For lengths (a, b, c) the tree has a centre and three arms. We look for two
disjoint vertex sets of equal size k whose multisets of pairwise distances
agree at every distance. Vertices are signed +1 (left), -1 (right) or
0 (unused), with exactly k of each sign; the energy of an assignment is
sum_d |#left pairs at distance d - #right pairs at distance d|, and a
witness is an assignment of energy 0. Simulated annealing with
sign-preserving swaps, incremental profile updates.

A failed search proves nothing: report the best energy reached.

Usage: python3 open_triple_search.py A B C K SECONDS SEED
On success writes witness_A_B_C.json in this directory (the payload
bfs_verify.py reads) and prints FOUND; otherwise prints the best energy.
"""
import json
import math
import random
import sys
import time
from pathlib import Path


def vertices(a, b, c):
    vs = [(0, 0)]
    for arm, length in enumerate((a, b, c), 1):
        vs.extend((arm, d) for d in range(1, length + 1))
    return vs


def dist(u, v):
    if u == (0, 0):
        return v[1]
    if v == (0, 0):
        return u[1]
    if u[0] == v[0]:
        return abs(u[1] - v[1])
    return u[1] + v[1]


def main():
    a, b, c, k = (int(x) for x in sys.argv[1:5])
    seconds = float(sys.argv[5])
    seed = int(sys.argv[6])
    rng = random.Random(seed)
    vs = vertices(a, b, c)
    n = len(vs)
    D = [[dist(vs[i], vs[j]) for j in range(n)] for i in range(n)]
    dmax = a + b  # largest distance is between the two longest arms

    best_overall = None
    deadline = time.time() + seconds
    restart = 0
    while time.time() < deadline:
        restart += 1
        sign = [0] * n
        idx = list(range(n))
        rng.shuffle(idx)
        for i in idx[:k]:
            sign[i] = 1
        for i in idx[k:2 * k]:
            sign[i] = -1
        # diff[d] = left pairs at d minus right pairs at d
        diff = [0] * (dmax + 1)
        for i in range(n):
            if sign[i] == 0:
                continue
            for j in range(i + 1, n):
                if sign[j] == sign[i]:
                    diff[D[i][j]] += sign[i]
        energy = sum(abs(x) for x in diff)

        def delta_swap(i, j):
            """Energy change from swapping the signs of i and j (sign[i] != sign[j])."""
            si, sj = sign[i], sign[j]
            change = {}
            for m in range(n):
                if m in (i, j) or sign[m] == 0:
                    continue
                # pair (i, m): contributes si if sign[m]==si, else 0; after swap sj if sign[m]==sj
                d = D[i][m]
                before = si if sign[m] == si else 0
                after = sj if sign[m] == sj else 0
                if before != after:
                    change[d] = change.get(d, 0) + after - before
                d = D[j][m]
                before = sj if sign[m] == sj else 0
                after = si if sign[m] == si else 0
                if before != after:
                    change[d] = change.get(d, 0) + after - before
            # pair (i, j) never contributes: signs differ before and after
            de = 0
            for d, delta in change.items():
                de += abs(diff[d] + delta) - abs(diff[d])
            return de, change

        steps = 0
        while time.time() < deadline and energy > 0:
            steps += 1
            frac = steps / 200000.0
            temp = 2.5 * (0.02 / 2.5) ** min(frac, 1.0)
            i = rng.randrange(n)
            j = rng.randrange(n)
            if i == j or sign[i] == sign[j]:
                continue
            de, change = delta_swap(i, j)
            if de <= 0 or rng.random() < math.exp(-de / temp):
                for d, delta in change.items():
                    diff[d] += delta
                sign[i], sign[j] = sign[j], sign[i]
                energy += de
            if steps % 200000 == 0:
                break  # restart with a fresh shuffle
        if best_overall is None or energy < best_overall[0]:
            best_overall = (energy, list(sign))
        if energy == 0:
            break

    energy, sign = best_overall
    print(f"restarts={restart} best_energy={energy}")
    if energy == 0:
        left = [list(vs[i]) for i in range(n) if sign[i] == 1]
        right = [list(vs[i]) for i in range(n) if sign[i] == -1]
        payload = {"lengths": [a, b, c], "left": left, "right": right}
        out = Path(__file__).with_name(f"witness_{a}_{b}_{c}.json")
        out.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"FOUND size={len(left)} wrote {out.name}")
    return 0 if energy == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
