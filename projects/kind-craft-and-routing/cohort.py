"""List the first twenty observed ordinary task offers from fixed Emberhall read pages."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys

CONTROLLER = "watch-keeper"
PREFIX = "house-assignment-v1 "
FAMILIES = ("codex", "opencode", "muse", "agy")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}")
PARITY_FIELDS = {"task", "task_generation", "tied_families"}
TARGET = 20


def read_pages(paths, after):
    """Accept a continuous interval covering the chosen start, with optional earlier context."""
    events = []
    through = None
    for path in paths:
        page = json.loads(Path(path).read_text())
        if not isinstance(page, dict) or not isinstance(page.get("events"), list):
            raise ValueError("expected a journal read page")
        end, latest = page.get("through"), page.get("latest")
        if type(end) is not int or type(latest) is not int or not 0 <= end <= latest:
            raise ValueError("invalid journal page bounds")
        if page.get("has_more") is not (end < latest):
            raise ValueError("inconsistent journal page cursor")
        begin = end - len(page["events"])
        if begin < 0 or (through is None and begin > after) or (through is not None and begin != through):
            raise ValueError("gap or overlap in journal pages")
        for seq, event in enumerate(page["events"], begin + 1):
            if (not isinstance(event, dict) or type(event.get("sequence")) is not int
                    or event["sequence"] != seq or not isinstance(event.get("data"), dict)
                    or not isinstance(event.get("op"), str) or not isinstance(event.get("actor"), str)):
                raise ValueError(f"invalid journal event at {seq}")
            events.append(event)
        through = end
    if through is None or through < after or after < 0:
        raise ValueError("pages do not cover the requested start")
    return events, through


@dataclass
class Admission:
    seq: int
    start: dict
    request: dict | None
    special_task: bool
    assignment: dict | None = None
    assignment_seq: int | None = None
    outcome: str | None = None
    exit_seq: int | None = None


def admissions(events, after):
    requests, runs, roles = {}, {}, {}
    for e in events:
        seq, data = e["sequence"], e["data"]
        kind = data.get("kind") if e["op"] == "life" else None
        if kind == "help":
            requests[data["request"]] = data
        if e["op"] in ("task", "ready"):
            task_roles = roles.setdefault(data["task"], set())
            task_roles.update({"helper", "review_run", "ballot_choice"}.intersection(data))
            if data.get("helper") == "none":
                task_roles.discard("helper")
            if data.get("clear_ballot_choice"):
                task_roles.discard("ballot_choice")
        if seq <= after or e["actor"] != CONTROLLER:
            continue
        if kind == "run-start":
            run = data["run"]
            if run in runs:
                raise ValueError(f"duplicate admission at {seq}")
            request = requests.get(data.get("help_request"))
            task = data.get("task", (request or {}).get("task"))
            runs[run] = Admission(seq, data, request, bool(roles.get(task)))
        elif kind == "run-finish" and (item := runs.get(data["run"])) is not None:
            if item.exit_seq is not None or data.get("outcome") not in ("success", "failed", "interrupted", "quota"):
                raise ValueError(f"invalid run finish at {seq}")
            item.exit_seq, item.outcome = seq, data["outcome"]
        elif e["op"] == "say" and data.get("text", "").startswith(PREFIX):
            observation = json.loads(data["text"][len(PREFIX):])
            if not isinstance(observation, dict) or not isinstance(observation.get("run"), str):
                raise ValueError(f"invalid assignment at {seq}")
            run = observation["run"]
            item = runs.get(run)
            if item is None:
                continue  # A start before the interval cannot enter this roster.
            if e.get("id") != f"home-{run}-assignment" or item.assignment is not None or item.exit_seq is not None:
                raise ValueError(f"assignment conflicts with run history at {seq}")
            item.assignment, item.assignment_seq = observation, seq
    return runs.values()


def safe_task(value):
    return isinstance(value, str) and IDENTIFIER.fullmatch(value) is not None


def offer(item):
    """Return the safe evidence for one bound offer, or None for a known out-of-scope start."""
    start, request, obs = item.start, item.request or {}, item.assignment or {}
    family, help_id = start["agent"], start.get("help_request")
    task = start.get("task", request.get("task"))
    has_parity = not PARITY_FIELDS.isdisjoint(obs)
    if obs and (type(obs.get("helper")) is not bool or obs.get("lane") not in ("work", "review", "explore")
                or obs.get("reason") not in ("balanced", "direct", "preferred-unavailable", "requested-provider")):
        raise ValueError(f"invalid routing fields at start {item.seq}")
    excluded = ("explore_generation" in start or "ballot_open" in start
                or not {"target_resident", "agent", "model", "review_run"}.isdisjoint(request)
                or (obs and (obs.get("helper") is not False or obs.get("lane") != "work"
                             or obs.get("reason") != "balanced" or obs.get("requested_agent") is not None)))
    if excluded or (item.special_task and ("task" in start or not has_parity)):
        if has_parity:
            raise ValueError(f"shortlist on excluded start {item.seq}")
        return None
    if obs and obs.get("help_request") != help_id:
        raise ValueError(f"help association conflicts at start {item.seq}")
    row = {"start": item.seq, "assignment": item.assignment_seq, "exit": item.exit_seq,
           "outcome": item.outcome, "family": family}
    if family not in FAMILIES:
        raise ValueError(f"unknown family at start {item.seq}")
    if has_parity:
        tied, generation = obs.get("tied_families"), obs.get("task_generation")
        if (not safe_task(obs.get("task")) or type(generation) is not int or generation < 0
                or not isinstance(tied, list) or tied != [k for k in FAMILIES if k in tied]
                or family not in tied or (task is not None and obs["task"] != task)
                or ("task" in start and (type(start.get("task_generation")) is not int
                                         or start["task_generation"] != generation))
                or (task is None and (help_id is None or item.request is not None))):
            raise ValueError(f"shortlist conflicts with admission {item.seq}")
        row.update(task=obs["task"], generation=generation, tied_families=tied)
    elif task is not None and safe_task(task):
        row["task"] = task
    elif help_id is None or item.request is not None:
        return None
    if help_id and item.request is None:
        row["gap"] = "help request before supplied history"
    elif not has_parity:
        row["gap"] = "shortlist missing"
    return row


def roster(events, after, through):
    runs = list(admissions(events, after))
    rows = []
    enrolled, seen, first_offer = [], set(), {}
    blocker = cutoff = None
    genuine_ties = 0
    for item in runs:  # Insertion order is run-start order, including interleaved finishes.
        row = offer(item)
        if row is None:
            continue
        rows.append(row)
        if "task" in row:
            first = first_offer.setdefault(row["task"], item.seq)
            if first != item.seq:
                row["repeat_of"] = first
        if row["outcome"] == "quota":
            disposition = "quota"
        elif row.get("task") in seen:
            disposition = "repeat"
        elif "gap" in row or row["outcome"] is None:
            disposition = row.get("gap", "pending exit")
            if cutoff is None and blocker is None:
                blocker = item.seq
        elif cutoff is not None:
            disposition = "after cutoff"
        elif blocker is not None:
            disposition = "behind unresolved start"
        else:
            disposition = "enrolled"
            seen.add(row["task"])
            enrolled.append(item.seq)
            genuine_ties += len(row["tied_families"]) > 1
            if len(enrolled) == TARGET:
                cutoff = item.seq
        row["disposition"] = disposition
    return {"after": after, "through": through, "target": TARGET, "starts": len(runs), "offers": rows,
            "distinct_named_tasks": len(first_offer), "repeat_offers": sum("repeat_of" in r for r in rows),
            "quota_exits": sum(r["outcome"] == "quota" for r in rows),
            "pending_exits": sum(r["outcome"] is None for r in rows),
            "missing_shortlists": sum("tied_families" not in r for r in rows),
            "enrolled_starts": enrolled, "enrolled_tasks": len(enrolled), "genuine_ties": genuine_ties,
            "singletons": len(enrolled) - genuine_ties, "first_unresolved": blocker,
            "twentieth_start": cutoff}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after", type=int, required=True, help="exclusive trial start sequence")
    parser.add_argument("pages", nargs="+", type=Path, help="journal read pages, in order")
    args = parser.parse_args()
    try:
        events, through = read_pages(args.pages, args.after)
        print(json.dumps(roster(events, args.after, through), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as err:
        print(f"Cannot read roster: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
