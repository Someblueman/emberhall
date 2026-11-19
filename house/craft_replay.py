"""Count historical dispatches with earlier same-field outcome evidence.

This is a necessary-evidence screen, not an alternative-routing estimator.
Inputs are saved verified journal pages and a covering verified status.
"""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from .digest import _extract_events_and_meta, load_inputs
from .home import KINDS
from .life import CONTROLLER
from .staffing import helper
from .work_metrics import ASSIGNMENT_PREFIX

FIELDS = {"software", "design", "science", "art", "mathematics", "language"}


def assignment_receipts(events):
    """Read controller receipts, also consumed by the separate offer audit."""
    receipts = {}
    for event in events:
        text = event["data"].get("text", "")
        if (event["actor"] != CONTROLLER or event["op"] != "say"
                or not text.startswith(ASSIGNMENT_PREFIX)):
            continue
        value = json.loads(text[len(ASSIGNMENT_PREFIX):])
        run = value["run"]
        if event["id"] == f"home-{run}-assignment":
            if run in receipts:
                raise ValueError(f"duplicate assignment receipt for {run}")
            receipts[run] = (event["sequence"], value)
    return receipts


def field_at(status, events, project, before):
    """Use explicit brief fields and their provenance, never titles or paths."""
    record = status["shelf"]["record"]
    project_info = record["projects"].get(project)
    if project_info is None:
        return {"field": None, "reason": "project missing from status"}
    start = project_info["started_sequence"]
    if start >= before:
        return {"field": None, "reason": "project not yet started"}
    idea_id = project_info["idea"]
    idea = record["ideas"].get(idea_id, {})
    versions = []
    # Latest status facts seed history only when that version is already known.
    for scope, info in (("idea", idea), ("project", project_info)):
        brief = info.get("brief", {})
        seq = brief.get("sequence")
        if type(seq) is int and seq < before:
            versions.append((seq, scope, brief.get("field")))
    for event in events:
        seq, data = event["sequence"], event["data"]
        if seq >= before or event["op"] != "shelf":
            continue
        if data.get("kind") == "idea-brief" and data.get("idea") == idea_id:
            versions.append((seq, "idea", data["brief"].get("field")))
        elif data.get("kind") == "project-brief" and data.get("project") == project:
            versions.append((seq, "project", data["brief"].get("field")))
        elif data.get("kind") == "explore-publish":
            for item in data.get("ideas", []):
                if item.get("idea") == idea_id and "brief" in item:
                    versions.append((seq, "idea", item["brief"].get("field")))
    if (project_info.get("brief", {}).get("sequence", 0) >= before
            and not any(v[1] == "project" for v in versions)):
        return {"field": None, "reason": "earlier project brief unavailable"}
    # A project brief supersedes the idea brief, including an unknown field.
    scoped = [v for v in versions if v[1] == "project"] or versions
    if not scoped:
        return {"field": None, "reason": "no earlier field-bearing brief"}
    latest = max(v[0] for v in scoped)
    values = {v[2] for v in scoped if v[0] == latest}
    if len(values) != 1:
        return {"field": None, "reason": "conflicting brief field"}
    field = values.pop()
    if field not in FIELDS:
        return {"field": None, "reason": "brief has no supported field"}
    return {"field": field, "project": project, "project_start": start,
            "idea": idea_id, "brief": latest, "reason": None}


def update_tags(tasks, event):
    data = event["data"]
    if event["op"] == "task":
        tasks[data["task"]] = dict(data)
    elif event["op"] == "ready":
        tags = tasks.setdefault(data["task"], {})
        tags.update({k: data[k] for k in ("project", "helper", "ballot_choice") if k in data})
        for key in ("project", "ballot_choice"):
            if data.get("clear_" + key):
                tags.pop(key, None)


def reserved(data, request, tags):
    if helper(data) or tags.get("helper") in ("build", "review"):
        return "helper"
    if "explore_generation" in data:
        return "Explorer"
    if "ballot_open" in data or tags.get("ballot_choice"):
        return "ballot"
    if data.get("mode") != "work" or tags.get("review_run") or request.get("review_run"):
        return "review"
    if {"agent", "model", "target_resident"} & request.keys():
        return "explicit request"
    return None


def earlier_evidence(status, events, before):
    """Rebuild the outcome ledger strictly before admission, including exits."""
    from .craft_outcomes import measure

    prefix = [e for e in events if e["sequence"] < before]
    if not prefix:
        return {}, {}
    ledger = measure([prefix])
    raw_runs, requests, tasks, claim_fields = {}, {}, {}, {}
    for event in prefix:
        data, seq = event["data"], event["sequence"]
        update_tags(tasks, event)
        if event["op"] == "life":
            if data["kind"] == "help":
                requests[data["request"]] = data
            elif data["kind"] == "run-start" and event["actor"] == CONTROLLER:
                raw_runs[data["run"]] = dict(data)
        elif event["op"] == "claim":
            tags = tasks.get(data["task"], {})
            project = tags.get("project")
            claim_fields[seq] = (dict(tags), field_at(status, prefix, project, seq)
                                 if project else {"field": None, "reason": "no project at claim"})
    counts = defaultdict(lambda: {"claims": [], "finishes": [], "first_reviews": [],
                                  "without_field_review": []})
    missing = Counter()
    run_fields = defaultdict(set)
    for attempt in ledger["attempts"]:
        run_id = attempt["run"]
        run = ledger["runs"].get(run_id)
        tags, provenance = claim_fields[attempt["claim"]]
        if not run or run["outcome"] in (None, "quota"):
            missing["unattributed, open or quota claim"] += 1
            continue
        raw = raw_runs[run_id]
        reason = reserved(raw, requests.get(raw.get("help_request"), {}), tags)
        if not reason and raw.get("help_request") and raw["help_request"] not in requests:
            reason = "help request outside supplied history"
        field = provenance["field"]
        if reason or field is None:
            run_fields[run_id].add(None)
            missing[reason or provenance["reason"]] += 1
            continue
        run_fields[run_id].add(field)
        bucket = counts[field, run["family"]]
        bucket["claims"].append({"claim": attempt["claim"], "run_start": run["start"],
                                 "exit": run["exit"], "outcome": run["outcome"]})
        if attempt["finish"] is not None:
            bucket["finishes"].append(attempt["finish"])
    for run_id, fields in run_fields.items():
        run = ledger["runs"][run_id]
        if len(fields) != 1 or None in fields:
            missing["mixed or unclassified reviewed contribution"] += bool(run["reviews"])
            for field in fields - {None}:
                counts[field, run["family"]]["without_field_review"].append(run["start"])
            continue
        field = next(iter(fields))
        if run["reviews"]:
            counts[field, run["family"]]["first_reviews"].append(
                {"run_start": run["start"], **run["reviews"][0]})
        else:
            counts[field, run["family"]]["without_field_review"].append(run["start"])
    missing["finishes without observed claims"] = len(ledger["unmatched_finishes"])
    missing["unmatched review receipts"] = len(ledger["unmatched_reviews"])
    return counts, dict(missing)


def replay(status, pages, first, through):
    events, interval = _extract_events_and_meta(pages)
    if (type(first) is not int or type(through) is not int or first > through or not events
            or interval["gaps"] or events[0]["sequence"] > first
            or events[-1]["sequence"] < through or status["sequence"] < through):
        raise ValueError("supply contiguous pages and a status covering the frozen interval")
    events = [e for e in events if e["sequence"] <= through]
    receipts = assignment_receipts(events)
    tasks, requests, decisions, exclusions, excluded = {}, {}, [], [], Counter()
    ordinary, quota = 0, 0
    for event in events:
        data, seq = event["data"], event["sequence"]
        update_tags(tasks, event)
        if event["op"] == "life" and data["kind"] == "help":
            requests[data["request"]] = data
        if not (first <= seq <= through and event["op"] == "life"
                and event["actor"] == CONTROLLER and data["kind"] == "run-start"):
            continue
        saved = status["life"]["runs"].get(data["run"], {})
        if saved.get("started_sequence") != seq or any(
                saved.get(k) != data.get(k) for k in ("agent", "resident", "model")):
            raise ValueError(f"status and admission disagree at {seq}")
        request = requests.get(data.get("help_request"), {})
        task = data.get("task") or request.get("task")
        tags = tasks.get(task, {})
        receipt, observation = receipts.get(data["run"], (0, {}))
        reason = reserved(data, request, tags)
        if not reason and data.get("help_request") and not request:
            reason = "help request outside supplied history"
        if not reason and (receipt <= seq or observation.get("reason") != "balanced"
                           or observation.get("lane") != "work"
                           or observation.get("helper") is not False
                           or observation.get("requested_agent") is not None
                           or observation.get("help_request") != data.get("help_request")):
            reason = "ordinary assignment unconfirmed"
        if reason:
            excluded[reason] += 1
            exclusions.append({"start": seq, "baseline": data["agent"], "task": task, "reason": reason})
            continue
        ordinary += 1
        # Censor the observed cohort, never an earlier choice's evidence.
        exits = [e for e in events if e["op"] == "life" and e["actor"] == CONTROLLER
                 and e["data"].get("kind") == "run-finish"
                 and e["data"].get("run") == data["run"]]
        if exits and exits[0]["data"]["outcome"] == "quota":
            quota += 1
            exclusions.append({"start": seq, "baseline": data["agent"], "task": task, "reason": "quota"})
            continue
        if not task or not tags.get("project"):
            excluded["ordinary start without known project task"] += 1
            exclusions.append({"start": seq, "baseline": data["agent"], "task": task,
                               "reason": "ordinary start without known project task"})
            continue
        provenance = field_at(status, events, tags["project"], seq)
        evidence, missing = earlier_evidence(status, events, seq)
        rows = {family: evidence.get((provenance["field"], family),
                {"claims": [], "finishes": [], "first_reviews": [],
                 "without_field_review": []}) for family in KINDS}
        supported = [family for family, row in rows.items() if row["claims"] and row["first_reviews"]]
        # Older receipts have no shortlist. Never infer one from current policy.
        shortlist = observation.get("tied_families")
        if shortlist is not None and (not isinstance(shortlist, list)
                or shortlist != [k for k in KINDS if k in shortlist]
                or data["agent"] not in shortlist):
            raise ValueError(f"invalid recorded shortlist at {receipt}")
        decisions.append({"start": seq, "assignment": receipt, "task": task,
                          "baseline": data["agent"], "field_provenance": provenance,
                          "earlier": rows, "supported_families": supported,
                          "covered": len(supported) >= 2, "recorded_shortlist": shortlist,
                          "missing_earlier": missing})
    covered = sum(d["covered"] for d in decisions)
    return {"first": first, "through": through, "evidence_first": events[0]["sequence"],
            "status_sequence": status["sequence"], "starts": len(decisions) + len(exclusions),
            "ordinary_balanced_starts": ordinary, "nonquota_ordinary_starts": ordinary - quota,
            "quota_excluded": quota, "task_bound_project_starts": len(decisions),
            "covered": covered, "uncovered": len(decisions) - covered,
            "excluded": dict(sorted(excluded.items())), "excluded_starts": exclusions, "decisions": decisions,
            "routing_finding": "NO-GO: this coverage screen does not establish a routing advantage",
            "alternative_outcomes_estimated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, help="covering verified fixed-channel status")
    parser.add_argument("--first", type=int, required=True, help="frozen first admission sequence")
    parser.add_argument("--through", type=int, required=True, help="frozen last admission sequence")
    parser.add_argument("pages", nargs="+", help="saved contiguous verified journal pages")
    args = parser.parse_args()
    try:
        result = replay(json.loads(Path(args.status).read_text()), load_inputs(args.pages),
                        args.first, args.through)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Cannot replay: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
