"""Decision for the 320-letter repeated-word tripod template.

Period 320, base lengths (427,267,211), literal prefixes (213,133,105).
Every coefficient row from coupled_word_completion.compile_shape is kept
unmodified; this module only decides whether a {-1,+1} assignment exists.
A positive result carries a word checked by verify_word and audit_word.
A negative result is a deterministic exact replay of a standard-library
integer search. The general tripod target stays undecided.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import coupled_word_completion as coupled
import integer_template_decision as prior

FORMAT = "tripod-320-template-decision-v1"
PERIOD = 320
BASE = (427, 267, 211)
CUTS = (213, 133, 105)
SHAPES = [[("literal", cut), ("repeat", PERIOD),
           ("literal", length - (arm < 2) - cut)]
          for arm, (length, cut) in enumerate(zip(BASE, CUTS))]

if SHAPES != prior.SHAPES or PERIOD != prior.PERIOD:
    raise AssertionError("320 shape drifted from integer_template_decision")
if BASE != prior.BASE or CUTS != prior.CUTS:
    raise AssertionError("320 lengths drifted from integer_template_decision")


def rows_for_template():
    """Recompile the 1,981 unmodified integer rows."""
    rows, variables, base, growth = coupled.compile_shape(PERIOD, SHAPES)
    if base != list(BASE) or growth != [1, 1, 1]:
        raise AssertionError("recompiled base changed")
    if len(rows) != 1981 or len(variables) != 1864:
        raise AssertionError("row or variable count changed")
    return rows, variables, base, growth


def separating_repeat_count(rows):
    degrees = [z for z, _ in rows]
    return (max(degrees) - min(degrees)) // PERIOD + 1


def run_exact(engine, max_conflicts):
    """Drive an IntegerSearch to completion without the prior 1M cap."""
    if max_conflicts is not None and (
            type(max_conflicts) is not int or max_conflicts < 1):
        raise ValueError("max_conflicts must be a positive int or None")
    import heapq
    if engine.impossible_row:
        return False
    restart, next_restart = 100, 100
    while True:
        conflict = engine.propagate()
        if conflict is not None:
            engine.conflicts += 1
            if not engine.limits:
                return False
            if max_conflicts is not None and engine.conflicts >= max_conflicts:
                return None
            learned, back = engine.analyze(conflict)
            engine.backtrack(back)
            number = len(engine.clauses)
            engine.clauses.append(learned)
            if len(learned) > 1:
                engine.watches[learned[0]].append(number)
                engine.watches[learned[1]].append(number)
            engine.enqueue(learned[0], learned)
            engine.increment /= 0.95
            if engine.increment > 1e100:
                engine.activity = [a * 1e-100 for a in engine.activity]
                engine.increment *= 1e-100
                engine.retire_clauses()
            if engine.conflicts % 5000 == 0:
                engine.retire_clauses()
        else:
            if engine.conflicts >= next_restart:
                engine.backtrack(0)
                restart = int(restart * 1.5)
                next_restart = engine.conflicts + restart
            while engine.heap:
                activity, variable = heapq.heappop(engine.heap)
                if (not engine.values[variable]
                        and activity == -engine.activity[variable]):
                    break
            else:
                for row in engine.rows:
                    if sum(a * -engine.values[i + 1]
                           for i, a in row.items()):
                        raise AssertionError(
                            "candidate violates an original row")
                return True
            engine.decisions += 1
            engine.limits.append(len(engine.trail))
            engine.maximum_depth = max(engine.maximum_depth,
                                       len(engine.limits))
            engine.enqueue(variable * engine.phase[variable], None)


def solve_exact(max_conflicts=None):
    """Exact decision; None only when a finite max_conflicts is hit."""
    rows, variables, base, growth = rows_for_template()
    engine = prior.IntegerSearch(rows, len(variables))
    exists = run_exact(engine, max_conflicts)
    result = {"format": FORMAT, "period": PERIOD,
              "base_lengths": base, "prefix_lengths": list(CUTS),
              "growth": growth, "max_conflicts": max_conflicts,
              "sign_variables": len(variables),
              "coefficient_rows": len(rows),
              "conflicts": engine.conflicts,
              "decisions": engine.decisions,
              "maximum_depth": engine.maximum_depth,
              "integer_reasons": engine.integer_reasons,
              "status": ("resource_limit" if exists is None else "exact"),
              "template_existence_decided": exists is not None,
              "general_target_decided": False,
              "all_hole_supports_excluded": False}
    if exists is not None:
        result["exists"] = exists
    if exists:
        signs = {(a, s, k): "+" if engine.values[i + 1] < 0 else "-"
                 for i, (a, s, k) in enumerate(variables)}
        word = {"format": coupled.FORMAT, "centre": 1, "period": PERIOD,
                "arms": [[{kind: "".join(signs[a, s, k]
                                         for k in range(size))}
                          for s, (kind, size) in enumerate(arm)]
                         for a, arm in enumerate(SHAPES, 1)]}
        coupled.verify_word(word)
        result["word"] = word
    return result


def verify(saved):
    """Deterministically replay and reject any altered certificate."""
    if type(saved) is not dict or saved.get("format") != FORMAT:
        raise ValueError("expected a 320 template decision receipt")
    if (saved.get("period") != PERIOD or saved.get("base_lengths") != list(BASE)
            or saved.get("prefix_lengths") != list(CUTS)
            or saved.get("general_target_decided") is not False
            or saved.get("all_hole_supports_excluded") is not False):
        raise ValueError("certificate scope changed")
    expected = solve_exact(saved.get("max_conflicts"))
    if json.dumps(saved, sort_keys=True) != json.dumps(
            expected, sort_keys=True):
        raise ValueError("receipt differs from exact deterministic replay")
    if expected.get("exists") is True:
        report = coupled.verify_word(expected["word"])
        cutoff = separating_repeat_count(rows_for_template()[0])
        for count in (0, 1, cutoff):
            audit = coupled.audit_word(expected["word"], count)
            if not audit["equal_distance_multisets"]:
                raise AssertionError("original-tree audit failed")
    return {"valid": True, "status": expected["status"],
            "template_existence_decided":
                expected["template_existence_decided"],
            "general_target_decided": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--solve", action="store_true")
    group.add_argument("--verify", type=Path)
    parser.add_argument("--max-conflicts", type=int, default=None)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--audit-repeat", type=int, default=None)
    args = parser.parse_args(argv)
    try:
        saved = (json.loads(args.verify.read_text()) if args.verify
                 else solve_exact(args.max_conflicts))
        if args.verify:
            report = verify(saved)
            if args.audit_repeat is not None:
                if saved.get("exists") is not True:
                    raise ValueError("no word to audit")
                report["original_tree_audit"] = coupled.audit_word(
                    saved["word"], args.audit_repeat)
        else:
            report = {k: v for k, v in saved.items() if k != "word"}
            if saved.get("exists") is True and args.audit_repeat is not None:
                report["original_tree_audit"] = coupled.audit_word(
                    saved["word"], args.audit_repeat)
        if args.write:
            args.write.write_text(json.dumps(saved, indent=2) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 2 if saved.get("status") == "resource_limit" else 0
    except (ValueError, OSError, TypeError, AttributeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
