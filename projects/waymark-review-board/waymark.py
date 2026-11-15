#!/usr/bin/env python3
"""Read-only suggestions for a named reviewer from an existing verified journal."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from house import project_work, work_metrics
from house.model import apply_event
from house.record import Record

TERMINAL = {"integrated", "rejected", "conflict", "tests-failed"}
KINDS = ("codex", "opencode", "muse", "agy")
SHA = re.compile(r"[0-9a-f]{40}")
MAX_PATHS = 16


def reference(events: list[dict], sequence: int) -> dict:
    return {"sequence": sequence, "id": events[sequence - 1]["id"]}


def path_names(names: list[str]) -> dict:
    """Output exact safe relative names, with explicit omissions, never contents."""
    safe = []
    for name in names:
        if (isinstance(name, str) and 0 < len(name) <= 240 and "\\" not in name
                and not name.startswith("/") and name.isprintable()
                and all(p not in {"", ".", ".."} for p in name.split("/"))
                and PurePosixPath(name).as_posix() == name):
            safe.append(name)
    return {"names": safe[:MAX_PATHS], "omitted": len(names) - len(safe[:MAX_PATHS])}


def request_metadata(request: dict, run: str) -> tuple[str, list[str]] | None:
    """Recognize the existing dispatcher template; this is recorded testimony."""
    prefix = f"Independently review stopped contribution {run}, commit "
    reason = request["reason"]
    if not reason.startswith(prefix):
        return None
    commit, separator, remainder = reason[len(prefix):].partition(", paths ")
    if not separator or SHA.fullmatch(commit) is None:
        return None
    try:
        paths, end = json.JSONDecoder().raw_decode(remainder)
    except ValueError:
        return None
    if (not isinstance(paths, list) or not paths or len(paths) > 1000
            or not all(isinstance(p, str) for p in paths) or not remainder[end:].startswith(".")):
        return None
    return commit, paths


def announcements(events: list[dict], runs: dict) -> tuple[dict, int]:
    """A journaled integration announcement is not its private acceptance receipt."""
    reports: dict[str, list[dict]] = {}
    ignored = 0
    prefix = "house-integration-v1 "
    for sequence, event in enumerate(events, 1):
        if event["op"] != "say" or not event["data"]["text"].startswith(prefix):
            continue
        try:
            value = json.loads(event["data"]["text"][len(prefix):])
        except ValueError:
            ignored += 1
            continue
        if not isinstance(value, dict):
            ignored += 1
            continue
        run = value.get("run")
        source = runs.get(run, {}) if isinstance(run, str) else {}
        commit = value.get("contribution")
        if (source.get("status") != "completed" or value.get("actor") != event["actor"]
                or event["actor"] == source.get("resident")
                or not isinstance(commit, str) or SHA.fullmatch(commit) is None
                or not isinstance(value.get("status"), str) or value["status"] not in TERMINAL
                or sequence <= source["ended_sequence"]):
            ignored += 1
            continue
        reports.setdefault(run, []).append({"status": value["status"], "commit": commit,
            "event": reference(events, sequence), "basis": "journal announcement; private receipt unverified"})
    return reports, ignored


def task_assignments(state: dict, events: list[dict], source: str) -> tuple[list, list]:
    """Bound task claims and finite hints follow current generations, not titles."""
    active, stale = [], []
    runs = state.get("life", {}).get("runs", {})
    at = state["at"]
    for task_id, task in state["tasks"].items():
        if task.get("review_run") != source or task["status"] == "done":
            continue
        lease = task["status"] == "claimed" and task["until"] > at
        unended_owner = task["status"] == "claimed" and any(
            run["status"] == "active" and run["resident"] == task["owner"] for run in runs.values())
        if lease or unended_owner:
            sequence = next(n for n in range(len(events), 0, -1)
                            if events[n - 1]["op"] in {"claim", "renew"}
                            and events[n - 1]["data"].get("task") == task_id)
            active.append({"task": task_id, "generation": task["generation"],
                           "event": reference(events, sequence),
                           "basis": ("recorded live task lease" if lease else
                                     "recorded unended owner after lease expiry; not process liveness")})
        for run_id, run in runs.items():
            if run["status"] != "active" or run.get("task") != task_id:
                continue
            row = {"task": task_id, "run": run_id, "generation": run.get("task_generation"),
                   "current_generation": task["generation"],
                   "event": reference(events, run["started_sequence"])}
            if (lease or unended_owner) and task["owner"] == run["resident"]:
                # Claim increments the admission generation; this is not a stale hint.
                continue
            if project_work.reserved(run, at, task):
                active.append(row | {"basis": "finite recorded task reservation"})
            else:
                stale.append(row | {"basis": "stale generation or expired finite reservation"})
    return active, stale


def board(state: dict, events: list[dict], reviewer: str, *, limit: int = 20,
          offset: int = 0, include_excluded: bool = False) -> dict:
    """Format only a Record.read-verified full history or its replayed prefix."""
    if reviewer not in state["residents"]:
        raise ValueError("reviewer must be a recorded resident in this prefix")
    if not 1 <= limit <= 50 or offset < 0:
        raise ValueError("limit must be 1..50 and offset must be nonnegative")
    life = state.get("life", {})
    runs, requests = life.get("runs", {}), life.get("requests", {})
    reports, ignored = announcements(events, runs)
    help_refs = {e["data"]["request"]: reference(events, n)
                 for n, e in enumerate(events, 1)
                 if e["op"] == "life" and e["data"].get("kind") == "help"}
    rows = []
    for run_id, run in runs.items():
        if run["status"] != "completed":
            continue
        finishes = []
        launched = run.get("launched_sequence")
        if launched is not None:
            for sequence in range(launched + 1, run["ended_sequence"]):
                event = events[sequence - 1]
                if event["op"] == "finish" and event["actor"] == run["resident"]:
                    finishes.append({"task": event["data"]["task"],
                        "event": reference(events, sequence),
                        "paths": path_names(list(event["data"]["artifacts"]))})
        reviews = [(key, request) for key, request in requests.items()
                   if request.get("review_run") == run_id]
        if not (finishes or reviews or run_id in reports):
            continue  # Stopped processes alone do not establish contributions.
        metadata = [(request_metadata(request, run_id), help_refs[key])
                    for key, request in reviews]
        known = [(value, ref) for value, ref in metadata if value is not None]
        commits = {value[0] for value, _ in known}
        commits.update(report["commit"] for report in reports.get(run_id, []))
        paths = sorted({p for value, _ in known for p in value[1]})
        active = []
        for key, request in reviews:
            assigned = runs.get(request.get("run"), {})
            if request["status"] == "assigned" and assigned.get("status") == "active":
                active.append({"request": key, "run": request["run"], "event": help_refs[key],
                               "basis": "recorded assigned help with unended run; not process liveness"})
        bound, stale = task_assignments(state, events, run_id)
        active.extend(bound)
        reasons, unknown = [], []
        if run["resident"] == reviewer:
            reasons.append("source-author")
        if run_id in reports:
            reasons.append("recorded-terminal-review")
        if active:
            reasons.append("active-assignment")
        if not commits:
            unknown.append("contribution commit unavailable in this journal prefix")
        if len(commits) > 1:
            unknown.append("conflicting recorded contribution commits")
        if len({tuple(sorted(value[1])) for value, _ in known}) > 1:
            unknown.append("conflicting recorded changed paths")
        if not paths:
            unknown.append("changed paths unavailable in recognized review request")
        names = path_names(paths)
        if names["omitted"]:
            unknown.append("changed paths omitted by output safety/size bounds")
        if not finishes:
            unknown.append("no immutable finish observed within launched run")
        rows.append({"run": run_id, "author": run["resident"],
            "decision": "excluded" if reasons else ("unknown" if unknown else "suggested"),
            "reasons": reasons, "unknown": unknown,
            "metadata_basis": "unverified review-request prose and/or journal announcement",
            "private_pending_and_receipt_status": "unknown; private stores not read",
            "commit": next(iter(commits)) if len(commits) == 1 else None,
            "paths": names, "start": reference(events, run["started_sequence"]),
            "stop": reference(events, run["ended_sequence"]),
            "finishes": finishes[:8], "finishes_omitted": max(0, len(finishes) - 8),
            "review_requests": [help_refs[key] for key, _ in reviews][:8],
            "review_requests_omitted": max(0, len(reviews) - 8),
            "metadata_events": [ref for _, ref in known][:8],
            "terminal": reports.get(run_id, [])[-1:],
            "assignments": active[:8], "assignments_omitted": max(0, len(active) - 8),
            "stale_assignments": stale[:8], "stale_assignments_omitted": max(0, len(stale) - 8)})
    # Matches source_delivery.queue_review's project-path-first, run-ID ordering.
    rows.sort(key=lambda row: (not any(p.startswith("projects/") for p in row["paths"]["names"]), row["run"]))
    totals = {decision: sum(row["decision"] == decision for row in rows)
              for decision in ("suggested", "unknown", "excluded")}
    visible = [row for row in rows if include_excluded or row["decision"] != "excluded"]
    return {"reviewer": reviewer, "totals": totals,
        "page": {"offset": offset, "limit": limit, "matching": len(visible),
                 "next_offset": offset + limit if offset + limit < len(visible) else None},
        "rows": visible[offset:offset + limit],
        "ordinary_rotation": {"window": work_metrics.WINDOW,
            "work": work_metrics.counts(state, "work", KINDS),
            "review": work_metrics.counts(state, "review", KINDS),
            "basis": "helpers excluded before last-32 slice, independently per lane; context only, not row ranking"},
        "ignored_integration_announcements": ignored,
        "limitations": [
            "Suggestion from recorded events only; claim/integration gates remain required.",
            "Private contribution.json/integration.json not read: pending bytes and authenticated acceptance unknown.",
            "Terminal announcements exclude conservatively, including receipt replay; they are testimony, not receipt verification.",
            "Absent review metadata stays unknown; finish-only runs may contain no reviewable source.",
            "Recorded active assignments are blockers, not proof of a running process; clocks use prefix event time.",
            "Ordering: recognized project paths first, then run ID; no value/urgency or provider preference ranking.",
            "No automatic acknowledgement; later events, private failures and unannounced contributions may be absent.",
        ]}


def read_board(repo: str, reviewer: str, *, through: int | None = None, **options) -> dict:
    state, events, head = Record(repo).read()  # Verify whole supplied history before any output.
    total = len(events)
    if through is not None:
        if not 1 <= through <= total:
            raise ValueError("through must name a sequence inside the verified journal")
        events = events[:through]
        state = None
        for event in events:
            state = apply_event(state, event)
    result = board(state, events, reviewer, **options)
    result["source"] = {"house_id": state["house_id"], "verified_repository_head": head,
        "verified_repository_events": total, "through": len(events),
        "through_event": reference(events, len(events)), "observation_at": state["at"],
        "incomplete_prefix": len(events) < total,
        "scope": "complete only relative to supplied repository; canonical freshness unknown"}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="existing verified Git house; never restore/found here")
    parser.add_argument("--reviewer", required=True, help="recorded resident ID")
    parser.add_argument("--through", type=int, help="replay this prefix after verifying entire supplied journal")
    parser.add_argument("--limit", type=int, default=20, help="rows per page, 1..50")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--include-excluded", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = read_board(args.repo, args.reviewer, through=args.through, limit=args.limit,
                            offset=args.offset, include_excluded=args.include_excluded)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2))
    except (ValueError, OSError, KeyError) as error:
        print("Waymark: " + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
