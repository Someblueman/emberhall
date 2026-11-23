#!/usr/bin/env python3
"""Standalone BFS recount of a tripod witness; imports nothing from the project.

Reads a witness JSON object with keys "lengths", "left", "right"
(vertices [arm, depth], centre [0, 0]), builds the tree adjacency
graph, and recounts every pairwise distance by breadth-first search.
Exit 0 iff the sets are disjoint, equal-sized, and homometric.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, deque
from itertools import combinations
from pathlib import Path


def build_adjacency(lengths):
    adj = {}
    def link(u, v):
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    centre = (0, 0)
    adj.setdefault(centre, [])
    for arm, length in enumerate(lengths, 1):
        prev = centre
        for d in range(1, length + 1):
            v = (arm, d)
            adj.setdefault(v, [])
            link(prev, v)
            prev = v
    return adj


def bfs_distances(adj, source):
    dist = {source: 0}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def recount(lengths, vertices):
    adj = build_adjacency(lengths)
    verts = [tuple(v) for v in vertices]
    for v in verts:
        if v not in adj:
            raise ValueError(f"vertex {list(v)} outside tree")
    cache = {v: bfs_distances(adj, v) for v in verts}
    return Counter(cache[u][v] for u, v in combinations(verts, 2))


def verify(payload):
    lengths = payload["lengths"]
    left = [tuple(v) for v in payload["left"]]
    right = [tuple(v) for v in payload["right"]]
    if set(left) & set(right):
        return {"ok": False, "reason": "overlap"}
    if len(set(left)) != len(left) or len(set(right)) != len(right):
        return {"ok": False, "reason": "duplicate"}
    if len(left) != len(right):
        return {"ok": False, "reason": "size mismatch"}
    lp = recount(lengths, left)
    rp = recount(lengths, right)
    diff = {d: lp[d] - rp[d] for d in sorted(lp.keys() | rp.keys()) if lp[d] != rp[d]}
    return {"ok": not diff, "size": len(left), "difference": diff}


def main():
    if len(sys.argv) != 2:
        print("usage: bfs_verify.py WITNESS.json | -", file=sys.stderr)
        return 2
    raw = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text()
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        print("witness must be a JSON object", file=sys.stderr)
        return 1
    try:
        result = verify(payload)
    except (ValueError, KeyError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
