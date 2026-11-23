"""Check the browser witness bench against this project's reference construction.

The bench page (``witness_bench.html``) rebuilds this project's construction in
JavaScript and recounts both distance profiles in the browser.  Nothing in the
house had ever compared that page with the project's own Python, so its
agreement with the reference construction rested on the author reading a
recorded log.  This command is that comparison.

It is a thin layer: the reference witness comes from ``gap_99_79_23`` and the
recount comes from ``bfs_verify``, the project's own independent breadth-first
verifier, which imports nothing from the construction.  Nothing here
re-implements either of them.

Standard library only; Python 3.10+.

One command, from a clone of Emberhall at the repository root::

    python3 projects/almost-halving-three-branches/bench_check.py --self-test

Other modes::

    python3 projects/almost-halving-three-branches/bench_check.py --scale 3
    python3 projects/almost-halving-three-branches/bench_check.py --compare page.json
    python3 projects/almost-halving-three-branches/bench_check.py --compare -   (stdin)

``--scale T`` prints the reference witness for that scale as JSON: the payload
the project's ``bfs_verify.py`` reads, and the payload the bench page exports.
``--compare FILE`` reads such a payload and checks it.

Every mode prints one PASS or FAIL line per check, with the reason for any
failure, and exits 1 unless every check passes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bfs_verify  # noqa: E402  the project's independent breadth-first recount
import gap_99_79_23 as gap  # noqa: E402  the project's reference construction

# The project's own recorded run, RUN_LOG_20261124.md, 24 November 2026.
RECORDED = {
    1: {"size": 100, "target": 100, "pairs_per_side": 4950},
    3: {"size": 301, "target": 301},
}


def pairs(count: int) -> int:
    """Number of unordered pairs in a set of ``count`` vertices."""
    return count * (count - 1) // 2


def target_for(lengths: list[int]) -> int:
    """The project's target size for a tree with these arm lengths."""
    return (1 + sum(lengths)) // 2 - 1


def reference_payload(scale: int) -> dict:
    """The reference witness for a scale, as the payload bfs_verify reads."""
    result = gap.witness(scale)
    return {"lengths": list(result["lengths"]),
            "left": [list(v) for v in result["left"]],
            "right": [list(v) for v in result["right"]]}


def scale_of(lengths: list[int]) -> int | None:
    """The scale t of T(99t, 79t, 23t), or None if the lengths are not of that shape."""
    if len(lengths) != 3 or lengths[0] % 99 or lengths[1] % 79 or lengths[2] % 23:
        return None
    scales = {lengths[0] // 99, lengths[1] // 79, lengths[2] // 23}
    return scales.pop() if len(scales) == 1 else None


def check_payload(payload: dict, scale: int | None = None) -> list[tuple[str, bool, str]]:
    """Every check a candidate witness must pass, as (name, ok, detail)."""
    checks: list[tuple[str, bool, str]] = []
    try:
        lengths = [int(n) for n in payload["lengths"]]
        left = [[int(v[0]), int(v[1])] for v in payload["left"]]
        right = [[int(v[0]), int(v[1])] for v in payload["right"]]
    except (KeyError, IndexError, TypeError, ValueError) as error:
        return [("payload is readable", False, f"malformed payload: {error}")]

    checks.append(("payload is readable", True, "lengths, left and right present"))

    try:
        verdict = bfs_verify.verify({"lengths": lengths, "left": left, "right": right})
    except (KeyError, IndexError, TypeError, ValueError) as error:
        verdict = {"ok": False, "reason": f"the recount refused this witness: {error}"}
    if verdict.get("ok"):
        detail = f"identical distance profiles over {verdict['size']} vertices per side"
    else:
        detail = verdict.get("reason") or f"profiles differ: {verdict.get('difference')}"
    checks.append(("independent breadth-first recount", bool(verdict.get("ok")), detail))

    checks.append(("both sides the same size",
                   len(left) == len(right),
                   f"{len(left)} and {len(right)}"))

    goal = target_for(lengths)
    size = len(left)
    checks.append(("meets the target", size >= goal,
                   f"size {size} against target {goal}"))

    if scale is None:
        scale = scale_of(lengths)
    if scale is not None:
        try:
            reference = reference_payload(scale)
        except Exception as error:  # the reference refuses open scales
            checks.append(("matches the reference construction", False,
                           f"the reference does not build this scale: {error}"))
        else:
            same = (sorted(map(tuple, reference["left"])) == sorted(map(tuple, left))
                    and sorted(map(tuple, reference["right"])) == sorted(map(tuple, right)))
            swapped = (sorted(map(tuple, reference["left"])) == sorted(map(tuple, right))
                       and sorted(map(tuple, reference["right"])) == sorted(map(tuple, left)))
            checks.append(("matches the reference construction", same or swapped,
                           f"scale {scale}: the vertex sets are the reference's"
                           if (same or swapped) else
                           f"scale {scale}: different vertex sets"))
    return checks


def report(checks: list[tuple[str, bool, str]], stream=sys.stdout) -> bool:
    ok = True
    for name, passed, detail in checks:
        ok = ok and passed
        print(f"{'PASS' if passed else 'FAIL'}: {name} ({detail})", file=stream)
    return ok


def self_test() -> int:
    """Check the checker against the project's recorded runs and its own alarms."""
    checks: list[tuple[str, bool, str]] = []

    for scale, recorded in sorted(RECORDED.items()):
        payload = reference_payload(scale)
        counted = bfs_verify.verify(payload)
        ok = (counted.get("ok")
              and counted.get("size") == recorded["size"]
              and gap.target(scale) == recorded["target"]
              and (recorded.get("pairs_per_side") is None
                   or pairs(recorded["size"]) == recorded["pairs_per_side"]))
        detail = (f"size {counted.get('size')}, target {gap.target(scale)}, "
                  f"{pairs(recorded['size'])} pairs per side"
                  if counted.get("ok") else f"recount failed: {counted}")
        checks.append((f"scale {scale} matches the project's recorded run", ok, detail))

    payload = reference_payload(1)
    checks.append(("the reference witness passes every check",
                   all(ok for _, ok, _ in check_payload(payload, 1)),
                   "scale 1"))

    altered = {
        "a vertex moved across": {"lengths": payload["lengths"],
                                  "left": payload["left"][:-1],
                                  "right": payload["right"]},
        "a duplicated vertex": {"lengths": payload["lengths"],
                                "left": payload["left"] + [payload["left"][0]],
                                "right": payload["right"]},
        "the centre replaced by an unused interior vertex": {
            "lengths": payload["lengths"],
            "left": payload["left"],
            "right": [[1, 19] if list(v) == [0, 0] else list(v) for v in payload["right"]]},
    }
    for name, candidate in altered.items():
        try:
            verdict = bfs_verify.verify(candidate)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            verdict = {"ok": False, "reason": f"the recount refused this witness: {error}"}
        checks.append((f"an altered witness is rejected: {name}", not verdict.get("ok"),
                       verdict.get("reason") or "profiles differ"))

    ok = report(checks)
    print("SELF-TEST " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--self-test", action="store_true",
                        help="check the checker against the project's recorded runs")
    parser.add_argument("--scale", type=int,
                        help="build the reference witness for this scale and print it as JSON")
    parser.add_argument("--compare", metavar="FILE",
                        help="check a witness payload from FILE ('-' for standard input)")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.compare is not None:
        text = sys.stdin.read() if args.compare == "-" else Path(args.compare).read_text(encoding="utf-8")
        payload = json.loads(text)
        ok = report(check_payload(payload, args.scale))
        print("COMPARE " + ("PASSED" if ok else "FAILED"))
        return 0 if ok else 1

    if args.scale is not None:
        payload = reference_payload(args.scale)
        # The payload goes to stdout alone, so it can be piped into --compare;
        # the check report goes to stderr.
        print(json.dumps(payload, indent=2, sort_keys=True))
        ok = report(check_payload(payload, args.scale), sys.stderr)
        print("SCALE " + ("PASSED" if ok else "FAILED"), file=sys.stderr)
        return 0 if ok else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
