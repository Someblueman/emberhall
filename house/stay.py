"""Keep a resident at research or project building for a real stretch.

Nearly every run used to end when its resident finished one small task and
slept: a median of eight minutes, about two fifths of it spent waking and
reading. From the Steward's deep-runs decision (shelf.DEEP_RUNS) a sleep asked
for early in a research or building run is answered with what is left to do
instead of being accepted. The answer is a mailbox refusal, never a journal
event, so history replays unchanged.

A resident is never trapped. Research ends by publishing or by giving the
round up with a reason. Building ends by saying what blocks further progress
(a sleep note containing "BLOCKED:"). Either way the run's 45 minutes passing,
or three refusals, lets the sleep through. Helpers, reviews, votes and upkeep
are not held at all.
"""
from __future__ import annotations

import time

from . import shelf, staffing

BUDGET_SECONDS = 2700
REFUSALS = 3
MARK = "BLOCKED:"
LOG = "stay.json"


class NotYet(ValueError):
    """A sleep asked for before the stretch is over; the text says what to do next."""


def stretch(state: dict, events: list[dict], run: str) -> dict | None:
    """The deep work this run is on, if any: a research round or an active project."""
    item = state.get("life", {}).get("runs", {}).get(run)
    if (shelf.deep_since(state) is None or item is None or item.get("status") != "active"
            or staffing.helper(item)):
        return None
    resident, record = item["resident"], state.get("shelf", {})
    key = record.get("explorer")
    expedition = record.get("rounds", {}).get(key) if key else None
    if expedition and expedition["owner"] == resident and expedition["status"] == "active":
        return {"kind": "research", "round": key, "started_at": expedition.get("started_at")}
    touched = [item["task"]] if "task" in item else []
    touched += [event["data"].get("task") for event in events[item["started_sequence"]:]
                if event["op"] == "claim" and event["actor"] == resident]
    for task_id in touched:
        task = state["tasks"].get(task_id, {})
        project = record.get("projects", {}).get(task.get("project"))
        # A helper-marked task is a bounded build or review for the helper lane.
        if project and project["status"] == "active" and "helper" not in task and "ballot_choice" not in task:
            return {"kind": "project", "project": task["project"], "milestone": project.get("milestone", "")}
    return None


def refusal(state: dict, events: list[dict], run: str, note: str, now: float, refused: int) -> str | None:
    """Why this run should not sleep yet, or None when the sleep may go through."""
    work = stretch(state, events, run)
    if work is None or refused >= REFUSALS:
        return None
    spent = now - state["life"]["runs"][run]["started_at"]
    if spent >= BUDGET_SECONDS:
        return None
    minutes, budget = int(spent // 60), BUDGET_SECONDS // 60
    if work["kind"] == "research":
        since = work["started_at"]
        age = "" if since is None else f", {int(max(0, now - since) // 60)} minutes old"
        return (f"Not yet. You hold research round {work['round']}{age}; research is this run's whole job and "
                f"you have used {minutes} of its {budget} minutes. Keep reading until the round's 30-minute "
                "floor, then publish; or give the round up with shelf kind explore-release and your reason. "
                "After that, sleep under a new request ID.")
    if MARK in note:
        return None
    milestone = " ".join(work["milestone"].split())
    milestone = milestone if len(milestone) <= 260 else milestone[:257] + "..."
    return (f"Not yet. This is a building stretch on project {work['project']} and you have used {minutes} of "
            f"its {budget} minutes. One small task is not the stretch. Milestone: {milestone} Choose the next "
            "piece that moves it, create and claim that task, and build it. If nothing more can move, "
            f"sleep under a new request ID with a note that contains {MARK} followed by exactly what blocks it "
            "(if only the Steward can unblock it, raise a need first).")


def gate(state: dict, events: list[dict], run: str, note: str, receipts: int) -> None:
    """Refuse an early sleep, remembering privately how often this run was refused."""
    from .mailbox import read_json, write_json
    try:
        log = read_json(receipts, LOG, 64_000)
        refused = log["refused"] if type(log.get("refused")) is int else REFUSALS
    except FileNotFoundError:
        log, refused = {"refused": 0, "at": []}, 0
    now = time.time()
    message = refusal(state, events, run, note, now, refused)
    if message is None:
        return
    log = {"refused": refused + 1, "kind": (stretch(state, events, run) or {}).get("kind"),
           "at": [*log.get("at", [])[-8:], now]}
    write_json(receipts, LOG, log, 64_000)
    raise NotYet(message)
