"""Read-only work outcomes from contiguous pages of the house journal."""

import argparse
from collections import Counter, defaultdict
import json
import re

from .digest import _extract_events_and_meta, _parse_telemetry, load_inputs
from .life import CONTROLLER

MEASURES = ("dispatches", "taken_dispatches", "eligible_dispatches", "eligible_taken_dispatches",
            "claims", "finishes", "eligible_claims", "eligible_finishes", "quota_claims",
            "open_run_claims", "unattributed_claims", "reviewed_runs", "first_pass",
            "no_review_receipt", "quota_runs", "open_runs")
PUBLIC_WINDOW = 1000


def task_area(tags):
    """Use the association in force at claim or dispatch, never the outcome."""
    if tags.get("review_run"):
        return "source review"
    if tags.get("ballot_choice"):
        return "project selection"
    if tags.get("project"):
        return "project/" + tags["project"]
    if tags.get("helper") in ("build", "review"):
        return "helper/" + tags["helper"]
    return "unclassified"


def record_review(event, data, runs):
    # The integrator appends a system-generated ID. Scheduled Hearth speech
    # carries a mailbox request ID even when it quotes an integration report.
    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                        event.get("id", "")):
        return False
    run = runs.get(data.get("run")) if isinstance(data.get("run"), str) else None
    if (not run or run["exit"] is None or event["actor"] == run["resident"]
            or event["actor"] != data.get("actor") or not all(
                isinstance(data.get(k), str) and re.fullmatch(r"[0-9a-f]{40}", data[k])
                for k in ("base", "contribution"))):
        return False
    status = data.get("status")
    if status in ("reviewed", "integrated"):
        if type(data.get("test_exit")) is not int or data["test_exit"] != 0:
            return False
    elif status not in ("rejected", "tests-failed", "conflict"):
        return False
    run["reviews"].append({"sequence": event["sequence"], "status": status})
    return True


def measure(pages):
    events, interval = _extract_events_and_meta(pages)
    if not events or interval["gaps"]:
        raise ValueError("supply a nonempty contiguous interval of journal events")
    return measure_events(events)


def measure_events(events):
    """Measure ordered, contiguous, numbered events from a verified read."""
    tasks, runs, active, held = {}, {}, {}, {}
    attempts, unmatched_finishes, unmatched_reviews = [], [], []

    for event in events:
        op, data, seq, actor = event["op"], event["data"], event["sequence"], event["actor"]
        task = data.get("task")
        if op == "task":
            tasks[task] = dict(data)
        elif op == "ready":
            tags = tasks.setdefault(task, {})
            tags.update({k: data[k] for k in ("project", "helper", "ballot_choice") if k in data})
            for k in ("project", "ballot_choice"):
                if data.get("clear_" + k):
                    tags.pop(k, None)
        elif op == "life" and actor == CONTROLLER and data["kind"] == "run-start":
            resident, run_id = data["resident"], data["run"]
            active[resident] = run_id
            runs[run_id] = {"family": data["agent"], "resident": resident, "start": seq,
                            "exit": None, "outcome": None, "reviews": [], "areas": set(),
                            "lane": "exploration" if "explore_generation" in data else data["mode"]}
            if task:
                area = task_area(tasks.get(task, {}))
                runs[run_id]["areas"].add(area)
                runs[run_id]["dispatch"] = {"task": task, "area": area,
                                            "generation": data.get("task_generation"), "claim": None}
        elif op == "life" and actor == CONTROLLER and data["kind"] == "run-finish":
            run = runs.get(data["run"])
            if run:
                run.update(exit=seq, outcome=data["outcome"])
                active.pop(run["resident"], None)
        elif op == "claim":
            area, run_id = task_area(tasks.get(task, {})), active.get(actor)
            if run_id:
                runs[run_id]["areas"].add(area)
                dispatch = runs[run_id].get("dispatch")
                if (dispatch and dispatch["task"] == task and dispatch["claim"] is None
                        and (dispatch["generation"] is None or dispatch["generation"] == data.get("expect"))):
                    dispatch["claim"] = seq
            attempt = {"task": task, "area": area, "run": run_id, "claim": seq, "finish": None}
            attempts.append(attempt)
            held[task] = attempt
        elif op == "release":
            held.pop(task, None)
        elif op == "finish":
            attempt = held.pop(task, None)
            if attempt is None:
                unmatched_finishes.append(seq)
            else:
                attempt["finish"] = seq
        elif op == "say" and data["text"].startswith("house-integration-v1 "):
            report = _parse_telemetry(event)
            if report is None or not record_review(event, report[1], runs):
                unmatched_reviews.append(seq)

    counts = defaultdict(Counter)
    for attempt in attempts:
        run = runs.get(attempt["run"], {})
        family = run.get("family", "unattributed")
        row = counts[family, attempt["area"]]
        row["claims"] += 1
        row["finishes"] += int(attempt["finish"] is not None)
        if not run:
            row["unattributed_claims"] += 1
        elif run["outcome"] is None:
            row["open_run_claims"] += 1
        elif run["outcome"] == "quota":
            row["quota_claims"] += 1
        else:
            row["eligible_claims"] += 1
            row["eligible_finishes"] += int(attempt["finish"] is not None)

    for run in runs.values():
        dispatch = run.get("dispatch")
        if dispatch:
            assigned = counts[run["family"], dispatch["area"]]
            taken = int(dispatch["claim"] is not None)
            assigned["dispatches"] += 1
            assigned["taken_dispatches"] += taken
            if run["outcome"] not in (None, "quota"):
                assigned["eligible_dispatches"] += 1
                assigned["eligible_taken_dispatches"] += taken
        areas = sorted(run.pop("areas"))
        if len(areas) > 1:
            run["area"] = "mixed"
        elif areas:
            run["area"] = areas[0]
        else:
            run["area"] = "no claim/" + run["lane"]
        run["work_areas"] = areas
        row = counts[run["family"], run["area"]]
        if run["outcome"] == "quota":
            row["quota_runs"] += 1
        elif run["outcome"] is None:
            row["open_runs"] += 1
        elif not run["reviews"]:
            row["no_review_receipt"] += 1
        else:
            row["reviewed_runs"] += 1
            row["first_pass"] += int(run["reviews"][0]["status"] in ("reviewed", "integrated"))

    return {"first": events[0]["sequence"], "through": events[-1]["sequence"],
            "rows": [dict(family=f, area=a, **{k: counts[f, a][k] for k in MEASURES})
                     for f, a in sorted(counts)],
            "attempts": attempts, "runs": runs, "unmatched_finishes": unmatched_finishes,
            "unmatched_reviews": unmatched_reviews}


def public_window(events, through, head, source_head):
    """The verified publication's trailing interval, with sequence-only public examples."""
    from .craft_offers import audit

    start = through - len(events) + 1
    numbered = [event | {"sequence": i} for i, event in enumerate(events, start)]
    result = measure_events(numbered)
    offered = audit([numbered], result, start - 1)
    receiving = {(row["family"], row["area"]): dict(row, examples=[])
                 for row in offered["rows"]}
    for offer in offered["offers"]:
        if offer["launch"] is None or offer["outcome"] in (None, "quota"):
            continue
        review = offer["receiver_first_review"]
        examples = receiving[offer["family"], offer["area"]]["examples"]
        examples.append({"offer": offer["offer"], "assignment": offer["assignment"],
                         "claim": offer["claim"], "finish": offer["claim_finish"],
                         "first_review": review["sequence"] if review else None,
                         "disposition": offer["disposition"]})
        del examples[:-3]
    rows = {(row["family"], row["area"]): {**row, "examples": {}} for row in result["rows"]}
    for attempt in result["attempts"]:
        run = result["runs"].get(attempt["run"], {})
        examples = rows[run.get("family", "unattributed"), attempt["area"]]["examples"]
        examples["claim"] = attempt["claim"]
        if attempt["finish"] is not None:
            examples["finish"] = attempt["finish"]
        else:
            examples.pop("finish", None)
    for run in result["runs"].values():
        dispatch = run.get("dispatch")
        if dispatch:
            rows[run["family"], dispatch["area"]]["examples"]["dispatch"] = run["start"]
        if run["reviews"] and run["outcome"] != "quota":
            examples = rows[run["family"], run["area"]]["examples"]
            seq = run["reviews"][0]["sequence"]
            examples["first_review"] = max(seq, examples.get("first_review", 0))
    return {"journal_head": head, "source_head": source_head, "first": result["first"],
            "through": result["through"], "rows": list(rows.values()),
            "receiving": {"rows": list(receiving.values()),
                          "distinct_eligible_tasks": offered["distinct_eligible_tasks"],
                          "excluded_reserved": offered["excluded_bound_starts"].get("reserved route", 0),
                          "unconfirmed": sum(n for reason, n in offered["excluded_bound_starts"].items()
                                             if reason != "reserved route")},
            "unmatched_finishes": len(result["unmatched_finishes"]),
            "unmatched_reviews": len(result["unmatched_reviews"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", nargs="+", help="saved journal read pages, or - for standard input")
    parser.add_argument("--json", action="store_true", help="include each contributing receipt sequence")
    args = parser.parse_args()
    try:
        result = measure(load_inputs(args.pages))
    except (OSError, KeyError, TypeError, ValueError) as exc:
        parser.exit(1, f"Cannot measure interval: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Journal {result['first']}–{result['through']}")
    print("Family | Work area | Taken/assigned to same run | Eligible taken/assigned | All finishes/claims | Eligible finishes/claims | Quota/open/unattributed claims"
          " | First pass/reviewed runs | Closed runs without review | Quota/open runs")
    for row in result["rows"]:
        print(f"{row['family']} | {row['area']} | {row['taken_dispatches']}/{row['dispatches']}"
              f" | {row['eligible_taken_dispatches']}/{row['eligible_dispatches']} | {row['finishes']}/{row['claims']}"
              f" | {row['eligible_finishes']}/{row['eligible_claims']}"
              f" | {row['quota_claims']}/{row['open_run_claims']}/{row['unattributed_claims']}"
              f" | {row['first_pass']}/{row['reviewed_runs']} | {row['no_review_receipt']}"
              f" | {row['quota_runs']}/{row['open_runs']}")
    print(f"Finishes without a claim in the interval: {len(result['unmatched_finishes'])}. "
          f"Review messages without a usable run or outcome: {len(result['unmatched_reviews'])}.")


if __name__ == "__main__":
    main()
