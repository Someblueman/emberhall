#!/usr/bin/env python3
"""Sweep every stored tripod witness and recheck it with the BFS counter.

One command, from a clone of Emberhall at the repository root::

    python3 projects/almost-halving-three-branches/witness_sweep.py --self-test

With no flag it only sweeps. ``--self-test`` additionally checks that a
deliberately altered pair is rejected, and is the form the recorded run
uses. The recount is ``bfs_verify.verify`` (breadth-first distances over
the tree graph, importing nothing from this project); this script adds
the directory sweep, the target-size report, and the altered-pair check.
Nothing here re-implements the distance count.

For every ``witness_*.json`` beside this script it reports both sets
disjoint, equal-sized, homometric (``ok``), the size, and whether the
size meets the target ``floor((1+a+b+c)/2)-1``. Exit 0 iff every stored
witness verifies (and, under ``--self-test``, the altered pair is
rejected).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NON_WITNESS = {"witness_bench_steps.json"}
sys.path.insert(0, str(HERE))

import bfs_verify


def target(lengths):
    a, b, c = lengths
    return (1 + a + b + c) // 2 - 1


def tree_vertices(lengths):
    verts = [(0, 0)]
    for arm, length in enumerate(lengths, 1):
        for d in range(1, length + 1):
            verts.append((arm, d))
    return verts


def check_file(path):
    payload = json.loads(path.read_text())
    try:
        result = bfs_verify.verify(payload)
    except (ValueError, KeyError) as err:
        return {"file": path.name, "ok": False, "reason": f"ERROR: {err}"}
    if not result.get("ok"):
        return {"file": path.name, "ok": False,
                "reason": result.get("reason", "not homometric")}
    size = result["size"]
    want = target(payload["lengths"])
    return {"file": path.name, "ok": True, "size": size,
            "meets_target": size >= want, "target": want}


def altered_pair_rejected():
    """Take the smallest stored witness and move one vertex elsewhere."""
    files = witness_files()[0]
    payload = json.loads(files.read_text())
    left = {tuple(v) for v in payload["left"]}
    right = {tuple(v) for v in payload["right"]}
    for v in tree_vertices(payload["lengths"]):
        if v not in left and v not in right:
            victim = payload["right"][-1]
            altered = dict(payload)
            altered["right"] = payload["right"][:-1] + [list(v)]
            verdict = bfs_verify.verify(altered)
            return {"file": files.name, "moved": [victim, list(v)],
                    "ok": not verdict.get("ok", False),
                    "verdict": verdict}
    return {"file": files.name, "ok": False, "reason": "no spare vertex"}


def witness_files():
    return [f for f in sorted(HERE.glob("witness_*.json"))
            if f.name not in NON_WITNESS]


def main(argv):
    self_test = "--self-test" in argv
    files = witness_files()
    rows = [check_file(f) for f in files]
    failed = [r for r in rows if not r["ok"]]
    met = sum(1 for r in rows if r.get("meets_target"))
    ok = not failed
    if ok:
        print(f"PASS {len(rows)}/{len(rows)} witnesses verified homometric "
              f"({met} meet target size)")
    else:
        for r in failed:
            print(f"FAIL {r['file']}: {r.get('reason')}")
        print(f"PASS {len(rows) - len(failed)}/{len(rows)} witnesses "
              "verified homometric")
    if self_test:
        alt = altered_pair_rejected()
        if alt["ok"]:
            print(f"PASS altered pair rejected ({alt['file']}, moved "
                  f"{alt['moved'][0]} -> {alt['moved'][1]})")
        else:
            print(f"FAIL altered pair on {alt['file']} was accepted")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
