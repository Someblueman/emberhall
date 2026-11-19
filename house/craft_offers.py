"""Follow ordinary project offers to the claim, finish and source review they actually received."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from .craft_replay import assignment_receipts
from .digest import _extract_events_and_meta, load_inputs
from .home import KINDS
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
                     "generation_unrecorded": dispositions["generation unrecorded"],
                     "reviewed_receiver_runs": len(reviews), "finished_without_review": len(finished) - len(reviews),
                     "first_pass": sum(r["status"] in ("integrated", "reviewed") for r in reviews)})
    return rows


def binding(data, seq, requests, tasks, receipts):
    """Follow the association known at admission. Old help requests carry no generation."""
    request_id = data.get("help_request")
    request = requests.get(request_id, {})
    receipt, observation = receipts.get(data["run"], (0, {}))
    task = data.get("task") or request.get("task")
    if not task:
        if request_id and request_id not in requests and observation.get("task"):
            return None, "help request outside supplied history"
        return None, None
    tags = tasks.get(task, {})
    if (helper(data) or "explore_generation" in data or "ballot_open" in data or data["mode"] != "work"
            or {"target_resident", "agent", "model", "review_run"} & request.keys()
            or tags.get("ballot_choice") or tags.get("review_run") or tags.get("helper") in ("build", "review")):
        return None, "reserved route"
    if request_id and request_id not in requests:
        return None, "help request outside supplied history"
    if request_id and request.get("task") != task:
        return None, "conflicting help association"
    if (receipt <= seq or observation.get("reason") != "balanced" or observation.get("lane") != "work"
            or observation.get("helper") is not False or observation.get("requested_agent") is not None
            or observation.get("help_request") != request_id or not (data.get("backlog") or request_id)):
        return None, "ordinary dispatch unconfirmed"

    generation = data.get("task_generation")
    tied = observation.get("tied_families")
    if {"task", "task_generation", "tied_families"} & observation.keys():
        recorded = observation.get("task_generation")
        if (observation.get("task") != task or type(recorded) is not int or recorded < 0
                or ("task_generation" in data and generation != recorded)):
            return None, "assignment names a different task or generation"
        if not isinstance(tied, list) or tied != [k for k in KINDS if k in tied] or data["agent"] not in tied:
            return None, "invalid recorded shortlist"
        generation = recorded
    elif not tags:
        return None, "project association unavailable"
    area = "project/" + tags["project"] if tags.get("project") else "unclassified"
    return {"task": task, "generation": generation, "area": area, "assignment": receipt,
            "binding": "help" if request_id else "backlog", "tied_families": tied}, None


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
    tasks, requests, offers, skipped = {}, {}, [], Counter()
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
        elif e["op"] == "life" and data["kind"] == "help":
            requests[data["request"]] = data
        elif seq > after and e["op"] == "life" and e["actor"] == CONTROLLER and data["kind"] == "run-start":
            bound, reason = binding(data, seq, requests, tasks, receipts)
            if reason:
                skipped[reason] += 1
            if bound is None:
                continue
            run = outcomes["runs"][data["run"]]
            if run["start"] != seq or run["family"] != data["agent"] or run["resident"] != data["resident"]:
                raise ValueError(f"outcome report and admission disagree at {seq}")
            key = bound["task"], bound["generation"]
            claim = trace_claim(run, resolutions.get(key), attempts, outcomes["runs"], indexed)
            if bound["generation"] is None:
                claim["disposition"] = "generation unrecorded"
            final = finishes.get(bound["task"])
            finisher = finishers.get(final, {})
            offers.append({"offer": seq, "launch": launches.get(data["run"]), "family": run["family"],
                           "exit": run["exit"], "outcome": run["outcome"], "task_finish": final,
                           "task_finisher_start": finisher.get("start"), "task_finisher_family": finisher.get("family"),
                           **bound, **claim})
    return {"first": outcomes["first"], "after": after, "through": outcomes["through"],
            "excluded_bound_starts": dict(sorted(skipped.items())), "offers": offers, "rows": summarize(offers),
            "distinct_eligible_tasks": len({r["task"] for r in offers
                                            if r["launch"] is not None and r["outcome"] not in (None, "quota")})}


def join_roster(report, roster):
    """Attach the independent reader's enrollment to already observed offer outcomes."""
    if (report["after"], report["through"]) != (roster["after"], roster["through"]):
        raise ValueError("roster and offer report have different cutoffs")
    by_start = {r["offer"]: r for r in report["offers"]}
    matched, missing, enrolled = set(), [], []
    for item in roster["offers"]:
        seq = item["start"]
        if seq in matched or seq in missing:
            raise ValueError(f"duplicate roster admission {seq}")
        offer = by_start.get(seq)
        if offer is None:
            if item["disposition"] == "enrolled":
                raise ValueError(f"enrolled admission {seq} has no matching offer")
            missing.append(seq)
            continue
        fields = ("assignment", "task", "family", "exit", "outcome", "tied_families")
        if (any(offer[k] != item.get(k) for k in fields)
                or ("generation" in item and
                    (type(item["generation"]) is not int or offer["generation"] != item["generation"]))):
            raise ValueError(f"roster and offer disagree at admission {seq}")
        matched.add(seq)
        if item["disposition"] == "enrolled":
            if "generation" not in item or offer["tied_families"] is None or offer["outcome"] in (None, "quota"):
                raise ValueError(f"enrolled admission {seq} lacks a closed non-quota shortlist")
            enrolled.append(offer)
    starts = [r["offer"] for r in enrolled]
    if (starts != roster["enrolled_starts"] or len(starts) != roster["enrolled_tasks"]
            or len({r["task"] for r in enrolled}) != len(starts)):
        raise ValueError("roster enrollment disagrees with the distinct enrolled offers")
    return {"matched_offers": len(matched), "unmatched_roster_starts": missing,
            "offers_outside_roster": sorted(by_start.keys() - matched),
            "enrolled_starts": starts, "enrolled_outcomes": summarize(enrolled)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcomes", required=True, help="craft_outcomes --json from the same pages")
    parser.add_argument("--after", required=True, type=int, help="count admissions strictly after this sequence")
    parser.add_argument("--roster", help="optional prospective cohort JSON with the same cutoffs")
    parser.add_argument("pages", nargs="+", help="contiguous saved fixed-channel read pages")
    args = parser.parse_args()
    try:
        result = audit(load_inputs(args.pages), json.loads(Path(args.outcomes).read_text()), args.after)
        if args.roster:
            result["roster_join"] = join_roster(result, json.loads(Path(args.roster).read_text()))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"Cannot audit offers: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
