"""Assignment opportunities and measured mailbox intervals, never inferred effort."""
from __future__ import annotations

import json
import math
import os
import re

from . import mailbox
from .life import CONTROLLER

WINDOW = 32
ASSIGNMENT_PREFIX = "house-assignment-v1 "
WAIT_PREFIX = "house-mailbox-time-v1 "
LANES = {"work", "review", "explore"}
REASONS = {"balanced", "requested-provider", "preferred-unavailable", "direct"}


def lane(run: dict, requests: dict) -> str:
    if "explore_generation" in run:
        return "explore"
    request = requests.get(run.get("help_request"), {})
    return "review" if "review_run" in request else "work"


def counts(state: dict, selected_lane: str, kinds: tuple) -> dict:
    life = state.get("life", {})
    recent = sorted((r for r in life.get("runs", {}).values()
                     if lane(r, life.get("requests", {})) == selected_lane),
                    key=lambda r: r["started_sequence"])[-WINDOW:]
    return {kind: sum(r["agent"] == kind for r in recent) for kind in kinds}


def seconds(intervals: list[tuple[float, float]]) -> float:
    """Union overlapping requests so parallel calls cannot double-count a run."""
    total, end = 0.0, float("-inf")
    for start, stop in sorted(intervals):
        total += max(0, stop - max(start, end))
        end = max(end, stop)
    return total


def finite(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def waiting(private, run: str, start: float, end: float) -> dict:
    """Only completed, timestamped receipts; old/pending requests remain unknown."""
    intervals, voluntary = [], []
    measured = unknown = 0
    try:
        with mailbox.directory(private, run, "mailbox") as directory:
            for name in os.listdir(directory):
                if not name.endswith(".json") or not mailbox.ID.fullmatch(name[:-5]):
                    continue
                try:
                    item = mailbox.read_json(directory, name, mailbox.MAX_REQUEST + mailbox.MAX_RESPONSE)
                    if not isinstance(item, dict):
                        raise ValueError("invalid saved mailbox receipt")
                    begin, stop = item.get("queued_at"), item.get("response_ready_at")
                    if (not finite(begin) or not finite(stop) or stop < begin or "response" not in item):
                        unknown += 1
                        continue
                    measured += 1
                    interval = (max(start, begin), min(end, stop))
                    if interval[1] >= interval[0]:
                        intervals.append(interval)
                        request = item.get("request", {})
                        argv = request.get("argv") if isinstance(request, dict) else None
                        if isinstance(argv, list) and argv[:1] == ["wait"]:
                            voluntary.append(interval)
                except mailbox.ERRORS:
                    unknown += 1
    except FileNotFoundError:
        pass
    except OSError:
        return {"run": run, "unavailable": True}
    return {"run": run, "mailbox_seconds": seconds(intervals),
            "voluntary_seconds": seconds(voluntary), "measured_requests": measured,
            "unmeasured_requests": unknown}


def observe_wait(record, private, run: str, item: dict, elapsed: float) -> None:
    request = f"home-{run}-mailbox-time"
    if request in record.read()[0]["receipts"]:
        return
    observation = waiting(private, run, item["started_at"], item["started_at"] + elapsed)
    record.append("say", CONTROLLER, {"text": WAIT_PREFIX + json.dumps(observation, sort_keys=True)}, request)


def public_observation(event: dict, runs: dict) -> None:
    """Whitelist controller metrics only; arbitrary messages never enter the page."""
    if event["op"] != "say" or event["actor"] != CONTROLLER:
        return
    text = event["data"].get("text", "")
    prefix = next((p for p in (ASSIGNMENT_PREFIX, WAIT_PREFIX) if text.startswith(p)), None)
    if prefix is None:
        return
    try:
        value = json.loads(text[len(prefix):])
        if not isinstance(value, dict) or not isinstance(value.get("run"), str):
            return
        run = runs.get(value["run"])
        if run is None:
            return
        if prefix == ASSIGNMENT_PREFIX:
            if value.get("lane") in LANES and value.get("reason") in REASONS:
                run["assignment"] = {k: value[k] for k in ("lane", "reason")}
                if value.get("requested_agent") in {"codex", "opencode", "muse", "agy"}:
                    run["assignment"]["requested_agent"] = value["requested_agent"]
                request = value.get("help_request")
                if isinstance(request, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", request):
                    run["assignment"]["help_request"] = request
        else:
            keys = ("mailbox_seconds", "voluntary_seconds", "measured_requests", "unmeasured_requests")
            if (all(finite(value.get(k)) for k in keys) and
                    value["voluntary_seconds"] <= value["mailbox_seconds"] and
                    all(type(value[k]) is int for k in keys[2:])):
                run["waiting"] = {k: value[k] for k in keys}
    except (ValueError, TypeError):
        return
