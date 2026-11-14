#!/usr/bin/env python3
"""Bounded lifecycle views over the house's existing verified Git reader."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

# Run from any working directory, using this checkout's existing verifier.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from house.record import Record
from house.model import apply_event


REPORT_PREFIXES = (
    "house-home-result-v1 ", "house-integration-v1 ",
    "house-assignment-v1 ", "house-mailbox-time-v1 ",
)
FIELDS = (
    "kind", "task", "project", "run", "resident", "request", "help_request",
    "review_run", "agent", "model", "outcome", "exit_code", "status", "ready",
    "through", "expect", "target_resident",
)


def event_data(event: dict) -> dict:
    """Recognize typed supervisor reports; ordinary speech stays ordinary speech."""
    data = event["data"]
    if event["op"] == "say":
        text = data.get("text", "")
        for prefix in REPORT_PREFIXES:
            if text.startswith(prefix):
                try:
                    report = json.loads(text[len(prefix):])
                except ValueError:
                    break
                if isinstance(report, dict):
                    return report
                break
    return data


def links(events: list[dict], *, task: str | None, resident: str | None) -> tuple[set, set]:
    """Follow explicit task -> help -> run edges, never matches in prose/IDs."""
    requests = set()
    runs = set()
    while True:
        previous = (len(requests), len(runs))
        for event in events:
            data = event["data"]
            if event["op"] != "life":
                continue
            if data.get("kind") == "help" and (
                    (task is not None and data.get("task") == task)
                    or (resident is not None and event["actor"] == resident)
                    or data.get("review_run") in runs):
                requests.add(data["request"])
            if data.get("kind") == "run-start" and (
                    (task is not None and data.get("task") == task)
                    or (resident is not None and data.get("resident") == resident)
                    or data.get("help_request") in requests):
                runs.add(data["run"])
                if data.get("help_request"):
                    requests.add(data["help_request"])
        if previous == (len(requests), len(runs)):
            break
    return requests, runs


def utc(at: float) -> str:
    try:
        return datetime.fromtimestamp(at, timezone.utc).isoformat(timespec="seconds")
    except (ValueError, OverflowError, OSError):
        return "outside datetime range"


def row(event: dict, sequence: int, data: dict) -> dict:
    result = {"sequence": sequence, "id": event["id"], "at": event["at"],
              "time_utc": utc(event["at"]), "op": event["op"], "actor": event["actor"]}
    # Do not expose artifact contents, fencing tokens, paths or arbitrary report keys.
    result["fields"] = {}
    for key in FIELDS:
        value = data.get(key)
        if isinstance(value, str):
            result["fields"][key] = value[:180]
            if len(value) > 180:
                result.setdefault("fields_truncated", []).append(key)
        elif value is None or type(value) in (bool, int) or (type(value) is float and math.isfinite(value)):
            if key in data:
                result["fields"][key] = value
    if event["op"] in ("claim", "ready"):
        result["fields"]["generation"] = data["expect"] + 1
    if event["op"] in ("claim", "renew"):
        result["fields"]["lease_until"] = event["at"] + data["seconds"]
    for key in ("title", "text", "note", "result", "reason"):
        if isinstance(data.get(key), str):
            text = data[key]
            result["detail"] = text[:180]
            result["detail_truncated"] = len(text) > 180
            break
    return result


def build_trace(state: dict, events: list[dict], head: str, *, task: str | None = None,
                resident: str | None = None, limit: int = 40, before: int | None = None) -> dict:
    """Format events already verified by Record.read; before pages rows, not state."""
    if (task is None) == (resident is None):
        raise ValueError("select exactly one task or resident")
    if not 1 <= limit <= 200 or (before is not None and before < 1):
        raise ValueError("limit must be 1..200 and before must be positive")
    requests, runs = links(events, task=task, resident=resident)
    matches = []
    projection = None
    for sequence, event in enumerate(events, 1):
        # Reuse the reducer for the state *before* a claim. A released claim
        # must not become an inferred expiry merely because its old clock passed.
        prior = ((projection or {}).get("tasks", {}).get(event["data"]["task"], {})
                 if event["op"] == "claim" else {})
        expiry = None
        if (event["op"] == "claim" and prior.get("status") == "claimed"
                and prior["until"] <= event["at"]):
            expiry = {"kind": "expired lease before reclaim", "generation": prior["generation"],
                      "lease_until": prior["until"], "compared_at": event["at"],
                      "basis": "clock inference, not a recorded expiry event or process observation"}
        projection = apply_event(projection, event)
        data = event_data(event)
        direct = ((task is not None and data.get("task") == task)
                  or (resident is not None and event["actor"] == resident))
        linked = any(isinstance(data.get(key), str) and data[key] in values
                     for key, values in (("run", runs), ("request", requests),
                                         ("help_request", requests), ("review_run", runs)))
        if direct or linked:
            item = row(event, sequence, data)
            if expiry is not None:
                item["inference"] = expiry
            matches.append(item)
    eligible = [item for item in matches if before is None or item["sequence"] < before]
    shown = eligible[-limit:]
    omitted = len(eligible) - len(shown)
    summary = None
    if task is not None and task in state["tasks"]:
        item = state["tasks"][task]
        status = item["status"]
        if status == "claimed":
            status = ("lease expired; fate unconfirmed" if item["until"] <= state["at"]
                      else "recorded claim")
        summary = {"title": item["title"], "status": status, "owner": item["owner"],
                   "generation": item["generation"], "lease_until": item["until"]}
        if "ready" in item:
            summary["declared_ready"] = item["ready"]
    if resident is not None and resident in state["residents"]:
        item = state["residents"][resident]
        summary = {"name": item["name"], "recorded_awake": item["awake"],
                   "saved_cursor": item["cursor"]}
    return {
        "selector": {"task" if task is not None else "resident": task or resident},
        "source": {"journal_head": head, "house_id": state["house_id"],
                   "verified_events": len(events), "observation_at": state["at"],
                   "observation_utc": utc(state["at"])},
        "summary_at_head": summary,
        "page": {"matching_total": len(matches), "matching_before": len(eligible),
                 "shown": len(shown), "omitted_earlier": omitted,
                 "excluded_at_or_after_before": len(matches) - len(eligible),
                 "next_before": shown[0]["sequence"] if omitted else None},
        "events": shown,
        "limitations": [
            "Snapshot of recorded events, not live process or task availability proof.",
            "Summary and lease expiry use the full verified head time, even on older pages.",
            "Explicit task/help/run links only; prose mentions and implicit relationships are excluded.",
            "Speech is a report, not an accepted operation. Details may be shortened; use raw event IDs.",
            "A filtered view does not acknowledge omitted or unseen events or change a saved cursor.",
        ],
    }


def format_text(trace: dict) -> str:
    source, page = trace["source"], trace["page"]
    lines = ["Hearth Lens " + json.dumps(trace["selector"]),
             f"Verified head {source['journal_head']} through {source['verified_events']} "
             f"at {source['observation_utc']}",
             "Summary at that head: " + json.dumps(trace["summary_at_head"], ensure_ascii=True),
             f"Showing {page['shown']} of {page['matching_before']} matching rows before this bound; "
             f"{page['omitted_earlier']} earlier omitted; "
             f"{page['excluded_at_or_after_before']} excluded by --before."]
    if page["next_before"] is not None:
        lines.append(f"Older matching rows: --before {page['next_before']}")
    for item in trace["events"]:
        lines.append(json.dumps(item, ensure_ascii=True, separators=(",", ":")))
    lines.extend("Note: " + note for note in trace["limitations"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="existing house repository; never restores or founds one")
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--task")
    selector.add_argument("--resident")
    parser.add_argument("--limit", type=int, default=40, help="newest matching rows, 1..200")
    parser.add_argument("--before", type=int, help="exclusive sequence bound for older matching rows")
    parser.add_argument("--json", action="store_true", help="structured bounded output")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.limit <= 200 or (args.before is not None and args.before < 1):
            raise ValueError("limit must be 1..200 and before must be positive")
        if args.task == "" or args.resident == "":
            raise ValueError("selector must not be empty")
        state, events, head = Record(args.repo).read()
        trace = build_trace(state, events, head, task=args.task, resident=args.resident,
                            limit=args.limit, before=args.before)
        print(json.dumps(trace, ensure_ascii=True) if args.json else format_text(trace))
    except (ValueError, OSError, KeyError) as error:
        print("Hearth Lens: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
