#!/usr/bin/env python3
"""Exact parity completion for one fresh tripod triple, with BFS recount.

Tries fixed omitted sets in a stated order using
``long_frontier.complete_support`` (solve the shell equations modulo
two, enumerate parity solutions, check the exact integer equations).
Any witness found is recounted by ``bfs_verify`` -- breadth-first
distances on the tree graph, importing nothing from the solvers --
before it is reported or written.

Exit 0: a BFS-verified witness at target size was found.
Exit 1: no witness on the supports tried. This is never an
all-omissions verdict: an obstructed or inconclusive support excludes
only pairs omitting exactly those vertices, and supports outside the
pool are untried.

Usage: python3 exact_completion.py A B C [--max-free N] [--no-pool]
       [--per-support SECONDS] [--out WITNESS.json]

``--per-support`` caps the wall-clock time spent on any one support
(SIGALRM, main thread only); an overrun support is counted
``timed_out`` and skipped. That is inconclusive for that support,
never an obstruction. Without the flag behaviour is unchanged.
Standard library only. See EXACT_COMPLETION_TOOL.md.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
import signal
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bfs_verify import verify
from long_frontier import complete_support
from published_cases import validate_lengths


def target_size(lengths):
    return (1 + sum(lengths)) // 2 - 1


def supports_in_order(lengths, use_pool=True):
    """Yield omitted sets: arm tips first, then the small stated pool."""
    lengths = validate_lengths(lengths)
    k = target_size(lengths)
    omissions = 1 + sum(lengths) - 2 * k
    tips = [(arm, n) for arm, n in enumerate(lengths, 1)]
    yield tips[:omissions]
    if not use_pool:
        return
    pool = ([(0, 0)] + tips
            + [(arm, n - 1) for arm, n in enumerate(lengths, 1) if n > 1]
            + [(arm, 1) for arm in (1, 2, 3)]
            + [(arm, 2) for arm, n in enumerate(lengths, 1) if n >= 2])
    pool = list(dict.fromkeys(pool))
    seen = {tuple(tips[:omissions])}
    for holes in combinations(pool, omissions):
        if holes not in seen:
            seen.add(holes)
            yield list(holes)


class _SupportTimeout(Exception):
    pass


def _validate_cap(per_support_seconds):
    if per_support_seconds is None:
        return
    if (isinstance(per_support_seconds, bool)
            or not isinstance(per_support_seconds, (int, float))
            or not per_support_seconds > 0):
        raise ValueError("per-support cap must be a positive number of seconds")
    if not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise ValueError("per-support cap requires SIGALRM (unsupported here)")
    if threading.current_thread() is not threading.main_thread():
        raise ValueError("per-support cap requires the main thread")


def _complete(lengths, omitted, cap_free, per_support_seconds):
    """complete_support under the optional cap; None means timed out."""
    if per_support_seconds is None:
        return complete_support(lengths, omitted, cap_free)

    def raise_timeout(signum, frame):
        raise _SupportTimeout

    previous = signal.signal(signal.SIGALRM, raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, per_support_seconds)
    try:
        return complete_support(lengths, omitted, cap_free)
    except _SupportTimeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def attempt(lengths, max_free=40, use_pool=True, pool_max_free=22,
            per_support_seconds=None):
    """Return a summary dict; witness summaries include the payload."""
    lengths = validate_lengths(lengths)
    _validate_cap(per_support_seconds)
    k = target_size(lengths)
    if k < 1:
        raise ValueError("lengths too small: target size is not positive")
    tried = 0
    verdicts = {"support_obstructed": 0, "inconclusive": 0}
    if per_support_seconds is not None:
        verdicts["timed_out"] = 0
    for index, omitted in enumerate(supports_in_order(lengths, use_pool)):
        tried += 1
        report = _complete(
            lengths, omitted, max_free if index == 0 else pool_max_free,
            per_support_seconds)
        if report is None:
            verdicts["timed_out"] += 1
            continue
        status = report.get("status")
        if status == "witness":
            payload = {"lengths": list(lengths),
                       "left": [list(v) for v in report["left"]],
                       "right": [list(v) for v in report["right"]]}
            bfs = verify(payload)
            if not bfs.get("ok") or bfs.get("size") != k:
                raise ArithmeticError(
                    f"solver witness failed BFS recount: {bfs}")
            return {"status": "witness", "lengths": list(lengths),
                    "size": k, "omitted": [list(v) for v in omitted],
                    "parity_rank": report.get("independent_parity_rows"),
                    "free_bits": report.get("free_bits_after_complement"),
                    "supports_tried": tried, "bfs_ok": True,
                    "payload": payload}
        if status in verdicts:
            verdicts[status] += 1
    return {"status": "no_witness_on_tried_supports",
            "lengths": list(lengths), "size": k,
            "supports_tried": tried, "verdicts": verdicts,
            "all_omissions_obstructed": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lengths", nargs=3, type=int, metavar=("A", "B", "C"))
    parser.add_argument("--max-free", type=int, default=40,
                        help="free-bit cap for the tip support (default 40)")
    parser.add_argument("--pool-max-free", type=int, default=22,
                        help="free-bit cap for pool supports (default 22)")
    parser.add_argument("--no-pool", action="store_true",
                        help="try only the tip-omitted support")
    parser.add_argument("--per-support", type=float, default=None,
                        metavar="SECONDS",
                        help="wall-clock cap per support; an overrun support "
                             "is counted timed_out and skipped")
    parser.add_argument("--out", type=Path, metavar="WITNESS.json",
                        help="write the witness payload here on success")
    args = parser.parse_args(argv)
    try:
        summary = attempt(args.lengths, args.max_free,
                          not args.no_pool, args.pool_max_free,
                          args.per_support)
    except (ValueError, ArithmeticError) as error:
        parser.error(str(error))
    payload = summary.pop("payload", None)
    if payload is not None and args.out is not None:
        args.out.write_text(json.dumps(payload, indent=1) + "\n")
        summary["wrote"] = str(args.out)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "witness" else 1


if __name__ == "__main__":
    raise SystemExit(main())
