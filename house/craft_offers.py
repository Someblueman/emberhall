"""Follow ordinary project offers to the claim, finish and source review they actually received."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from .craft_replay import assignment_receipts
from .digest import _extract_events_and_meta, load_inputs
from .life import CONTROLLER
from .staffing import helper


def trace_claim(receiver, decision, attempts, runs, events):
    row = {"claim": None, "claimant_start": None, "claimant_family": None,
           "claim_finish": None, "receiver_first_review": None}
    if decision is None:
        return row | {"disposition": "no claim at cutoff"}
    if decision["sequence"] <= receiver["start"]:
        raise ValueError(f"generation already changed before offer {receiver['start']}")
    if decision["op"] == "ready":
        return row | {"disposition": "readiness changed", "change": decision["sequence"]}

    claim = decision["sequence"]
    attempt = attempts[claim]
    if attempt["task"] != decision["data"]["task"]:
        raise ValueError(f"outcome report and claim disagree at {claim}")
    claimant = runs.get(attempt["run"])
    finish = attempt["finish"]
    if finish is not None:
        saved = events[finish]
        if (saved["op"] != "finish" or saved["data"]["task"] != decision["data"]["task"]
                or saved["data"]["token"] != decision["data"]["token"]
                or saved["actor"] != decision["actor"] or finish <= claim):
            raise ValueError(f"finish does not belong to claim {claim}")
    row.update(claim=claim, claim_finish=finish)
    if not claimant:
        if decision["actor"] != receiver["resident"] or (receiver["exit"] and claim >= receiver["exit"]):
            return row | {"disposition": "claimed elsewhere"}
        return row | {"disposition": "claimant run unavailable"}
    row.update(claimant_start=claimant["start"], claimant_family=claimant["family"])
    if claimant["start"] != receiver["start"]:
        return row | {"disposition": "claimed elsewhere"}
    if decision["actor"] != receiver["resident"] or (receiver["exit"] and (finish or claim) >= receiver["exit"]):
        raise ValueError(f"claim or finish outside receiving run for offer {receiver['start']}")
    if finish is None:
        return row | {"disposition": "receiver claimed"}
    # One source decision covers the contribution, potentially including other tasks.
    review = next(iter(receiver["reviews"]), None)
    if review and (not receiver["exit"] or review["sequence"] <= receiver["exit"] or review["sequence"] not in events):
        raise ValueError(f"source review outside observed history for offer {receiver['start']}")
    return row | {"disposition": "receiver finished", "receiver_first_review": review}


def summarize(offers):
    groups = defaultdict(list)
    for row in offers:
        groups[row["family"], row["area"]].append(row)
    rows = []
    for (family, area), entries in sorted(groups.items()):
        closed = [r for r in entries if r["outcome"] not in (None, "quota")]
        eligible = [r for r in closed if r["launch"] is not None]
        dispositions = Counter(r["disposition"] for r in eligible)
        claimed = [r for r in eligible if r["disposition"] in ("receiver claimed", "receiver finished")]
        finished = [r for r in claimed if r["claim_finish"] is not None]
        reviews = [r["receiver_first_review"] for r in finished if r["receiver_first_review"]]
        rows.append({"family": family, "area": area, "offers": len(entries),
                     "quota": sum(r["outcome"] == "quota" for r in entries),
                     "open": sum(r["outcome"] is None for r in entries),
                     "closed_without_launch": len(closed) - len(eligible),
                     "eligible_offers": len(eligible), "unique_eligible_tasks": len({r["task"] for r in eligible}),
                     "receiver_claimed": len(claimed), "receiver_finished": len(finished),
                     "claimed_elsewhere": dispositions["claimed elsewhere"],
                     "readiness_changed": dispositions["readiness changed"],
                     "unclaimed": dispositions["no claim at cutoff"],
                     "claimant_unknown": dispositions["claimant run unavailable"],
                     "reviewed_receiver_runs": len(reviews), "finished_without_review": len(finished) - len(reviews),
                     "first_pass": sum(r["status"] in ("integrated", "reviewed") for r in reviews)})
    return rows


def audit(pages, outcomes, after):
    events, meta = _extract_events_and_meta(pages)
    if (not events or meta["gaps"] or outcomes["first"] != events[0]["sequence"]
            or outcomes["through"] != events[-1]["sequence"]
            or not outcomes["first"] - 1 <= after < outcomes["through"]):
        raise ValueError("journal pages and outcome report must cover the same contiguous interval")
    indexed = {e["sequence"]: e for e in events}
    receipts = assignment_receipts(events)
    launches = {e["data"]["run"]: e["sequence"] for e in events if e["op"] == "life"
                and e["actor"] == CONTROLLER and e["data"]["kind"] == "run-launched"}
    attempts = {a["claim"]: a for a in outcomes["attempts"]}
    finishers = {a["finish"]: outcomes["runs"].get(a["run"], {}) for a in attempts.values() if a["finish"]}
    resolutions = {(e["data"]["task"], e["data"]["expect"]): e for e in events if e["op"] in ("claim", "ready")}
    finishes = {e["data"]["task"]: e["sequence"] for e in events if e["op"] == "finish"}
    tasks, offers, skipped = {}, [], Counter()
    for e in events:
        data, seq = e["data"], e["sequence"]
        task = data.get("task")
        if e["op"] == "task":
            tasks[task] = dict(data)
        elif e["op"] == "ready" and task in tasks:
            tags = tasks[task]
            tags.update({k: data[k] for k in ("project", "ballot_choice", "helper") if k in data})
            for k in ("project", "ballot_choice"):
                if data.get("clear_" + k):
                    tags.pop(k, None)
        elif (seq > after and e["op"] == "life" and e["actor"] == CONTROLLER
              and data["kind"] == "run-start" and task):
            tags = tasks.get(task, {})
            receipt, observation = receipts.get(data["run"], (0, {}))
            if (helper(data) or "explore_generation" in data or "help_request" in data or "ballot_open" in data
                    or data["mode"] != "work" or tags.get("ballot_choice") or tags.get("review_run")):
                skipped["reserved route"] += 1
            elif not tags.get("project"):
                skipped["project association unavailable"] += 1
            elif (receipt <= seq or observation.get("reason") != "balanced" or observation.get("lane") != "work"
                  or observation.get("helper") is not False or observation.get("requested_agent") is not None
                  or observation.get("help_request") is not None or not data.get("backlog")):
                skipped["ordinary dispatch unconfirmed"] += 1
            elif ({"task", "task_generation", "tied_families"} & observation.keys() and
                  (observation.get("task") != task or type(observation.get("task_generation")) is not int
                   or observation["task_generation"] != data["task_generation"])):
                skipped["assignment names a different task or generation"] += 1
            else:
                run = outcomes["runs"][data["run"]]
                if run["start"] != seq or run["family"] != data["agent"] or run["resident"] != data["resident"]:
                    raise ValueError(f"outcome report and admission disagree at {seq}")
                generation = data["task_generation"]
                claim = trace_claim(run, resolutions.get((task, generation)), attempts, outcomes["runs"], indexed)
                final = finishes.get(task)
                finisher = finishers.get(final, {})
                offers.append({"offer": seq, "assignment": receipt, "launch": launches.get(data["run"]),
                               "family": run["family"], "area": "project/" + tags["project"], "task": task,
                               "generation": generation, "exit": run["exit"], "outcome": run["outcome"],
                               "task_finish": final, "task_finisher_start": finisher.get("start"),
                               "task_finisher_family": finisher.get("family"), **claim})
    return {"first": outcomes["first"], "after": after, "through": outcomes["through"],
            "excluded_bound_starts": dict(sorted(skipped.items())), "offers": offers, "rows": summarize(offers),
            "distinct_eligible_tasks": len({r["task"] for r in offers
                                            if r["launch"] is not None and r["outcome"] not in (None, "quota")})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcomes", required=True, help="craft_outcomes --json from the same pages")
    parser.add_argument("--after", required=True, type=int, help="count admissions strictly after this sequence")
    parser.add_argument("pages", nargs="+", help="contiguous saved fixed-channel read pages")
    args = parser.parse_args()
    try:
        result = audit(load_inputs(args.pages), json.loads(Path(args.outcomes).read_text()), args.after)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"Cannot audit offers: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
