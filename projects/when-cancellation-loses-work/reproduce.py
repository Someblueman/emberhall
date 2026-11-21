#!/usr/bin/env python3
"""Reproduce the frozen finite gate; no dependencies, random seeds or network."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import unittest

from admission_model import Run, execute
from native_witness import witnesses
from ownership_oracle import violations


def errors(run: Run) -> tuple[str, ...]:
    return tuple(sorted({e for row in run.trace for e in violations(run.weights, row["state"])}))


def signature(run: Run) -> tuple:
    return (tuple(sorted(run.final["completed"])), tuple(sorted(run.final["returned"])),
            tuple(sorted(run.final["queue"])), errors(run), run.stopped)


def prestart_only(run: Run) -> bool:
    """Attribute a failure only if every affected job never entered its body."""
    never_started = {j for j, w in run.final["workers"].items() if not w["started"]}
    failures = errors(run)
    if not failures:
        return False
    stranded = set(run.final["held"])
    if not stranded or not stranded <= never_started:
        return False
    expected = {f"lost:{j}" for j in stranded} | {f"stranded:{j}" for j in stranded}
    expected.add("unsettled-terminal")
    return set(failures) <= expected


def bounded_comparison() -> tuple[dict, Run, tuple[Run, Run]]:
    counts = {"workloads": 0, "uncancelled_controls": 0, "pairs": 0,
              "owner_failure_runs": 0, "worker_failure_runs": 0,
              "known_prestart_failure_runs": 0, "direction_splits": 0,
              "safety_splits": 0, "max_transitions": 0, "bound_hits": 0,
              "stuck_runs": 0, "unexpected_failures": 0}
    first_failure = None
    first_split = None
    for size in range(1, 4):
        for weights in itertools.product((1, 2, 3), repeat=size):
            counts["workloads"] += 1
            for cleanup, consume in itertools.product(("owner", "worker"), (False, True)):
                baseline = execute(weights, cleanup=cleanup, consume=consume)
                # Matched no-cancellation control: changing policy must do nothing.
                other = execute(weights, "simultaneous", cleanup, consume)
                assert baseline.trace == other.trace
                assert not errors(baseline) and baseline.stopped == "finished"
                assert sorted(baseline.final["completed"]) == list(range(size))
                counts["uncancelled_controls"] += 2
                for cut in range(len(baseline.trace)):
                    pair = tuple(execute(weights, p, cleanup, consume, cut)
                                 for p in ("bottom_up", "simultaneous"))
                    counts["pairs"] += 1
                    for run in pair:
                        counts["max_transitions"] = max(counts["max_transitions"], len(run.trace) - 1)
                        counts["bound_hits"] += run.stopped == "bound"
                        counts["stuck_runs"] += run.stopped == "stuck"
                        if errors(run):
                            counts[f"{cleanup}_failure_runs"] += 1
                            if prestart_only(run):
                                counts["known_prestart_failure_runs"] += 1
                            else:
                                counts["unexpected_failures"] += 1
                            if first_failure is None:
                                first_failure = run
                    if signature(pair[0]) != signature(pair[1]):
                        counts["direction_splits"] += 1
                        if errors(pair[0]) != errors(pair[1]):
                            counts["safety_splits"] += 1
                        if first_split is None and cleanup == "owner":
                            first_split = pair
    assert counts["workloads"] == 39
    assert counts["owner_failure_runs"] == 0, counts
    assert counts["unexpected_failures"] == counts["bound_hits"] == 0, counts
    assert first_split is not None, counts
    counts["prestart_control_observed"] = first_failure is not None
    # The frozen schedule is not widened to rescue a failed control.
    counts["decision"] = "STOP-KNOWN-ONLY" if first_failure else "STOP-CONFOUNDED"
    witness = first_failure or execute((2,), "bottom_up", "worker", False, 1)
    return counts, witness, first_split


def compact_run(run: Run) -> dict:
    return {"weights": run.weights, "direction": run.direction,
            "cleanup": run.cleanup, "consume": run.consume, "cut": run.cut,
            "stopped": run.stopped, "violations": errors(run),
            "final": run.final, "trace": run.trace}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full representative traces as JSON")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_gate.py")
    test_result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
    summary, failure, split = bounded_comparison()
    native = witnesses()
    assert native["cases"][0]["violations"]
    assert all(not case["violations"] for case in native["cases"][1:])
    protocol = Path(__file__).with_name("PROTOCOL.md").read_bytes()
    report = {"protocol_sha256": hashlib.sha256(protocol).hexdigest(),
              "tests": {"run": test_result.testsRun, "failures": len(test_result.failures),
                        "errors": len(test_result.errors)}, "controlled_model": summary,
              "prestart_control": compact_run(failure),
              "direction_split": [compact_run(run) for run in split],
              "native_asyncio": native}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps({"protocol_sha256": report["protocol_sha256"],
                          "tests": report["tests"], **summary}, indent=2))
        print("\nPre-start control trace (controlled model; inspect observed violations):")
        print(f"weights={failure.weights}, policy={failure.direction}, cleanup={failure.cleanup}, cut={failure.cut}")
        for i, row in enumerate(failure.trace):
            state = row["state"]
            print(f"{i:02} {row['action']}; queue={state['queue']}, live={state['live']}, "
                  f"returned={state['returned']}, done={state['completed']}, held={state['held']}")
        print("violations:", ", ".join(errors(failure)))
        print("\nDirection sensitivity with conserved ownership (controlled model):")
        for run in split:
            print(f"{run.direction}: weights={run.weights}, consume={run.consume}, cut={run.cut}, "
                  f"done={run.final['completed']}, returned={run.final['returned']}, "
                  f"queued={run.final['queue']}, violations={errors(run)}")
        print(f"\nNative asyncio {native['implementation']} {native['python']}, {native['loop']}:")
        for case in native["cases"]:
            print(case["case"] + ": " + " | ".join(case["events"]))
            print("violations:", case["violations"])
        print("\n" + summary["decision"] + ": no new ownership consequence established.")
        if not summary["prestart_control_observed"]:
            print("Frozen control failed: dispatcher cancellation did not reach a worker before start.")
        print("Corpus expansion remains closed. See RESULTS.md for the failed preregistered control.")
    return 0 if test_result.wasSuccessful() and summary["prestart_control_observed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
