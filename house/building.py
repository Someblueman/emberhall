"""Evidence-backed room construction; existing rooms and their past are retained.

Callers dispatch only after the explicit room-growth migration. Like model.apply,
these helpers mutate a disposable projection: discard it after rejected input.
Floor descriptors come from enacted council rules, never from resident room data.
"""
from __future__ import annotations

import math
import re

from .model import require, string

KINDS = frozenset({"room-plan", "room-open", "room-repurpose", "room-close"})


def enabled(state: dict) -> float:
    maintenance = state.get("maintenance", {})
    require(maintenance.get("room_growth") is True, "room growth is not authorized")
    at = maintenance.get("at")
    require(type(at) in (int, float) and math.isfinite(at) and at > 0,
            "room growth requires its migration observation time")
    return at


def initialize(state: dict) -> None:
    observed = enabled(state)
    from .life import empty
    life = state.setdefault("life", empty())
    life.setdefault("floors", {}).setdefault("0", {"level": 0, "name": "Ground floor",
        "purpose": "The existing household", "proposal": None,
        "enacted_at": None, "enacted_sequence": None})
    for room in life["rooms"].values():
        defaults = {"generation": 0, "status": "open", "floor": 0, "purpose": None,
            "builder": None, "task": None, "task_generation": None,
            "planned_at": None, "planned_sequence": None, "opened_at": None,
            "opened_sequence": None, "last_used_at": None, "last_used_sequence": None,
            "last_used_by": None, "observed_since": observed, "legacy": True, "history": []}
        for name, value in defaults.items():
            room.setdefault(name, value)


def floor_descriptor(data: dict) -> dict:
    require(isinstance(data, dict) and set(data) == {"level", "name", "purpose"}, "invalid floor descriptor")
    require(type(data["level"]) is int and data["level"] > 0, "new floor level must be positive")
    name, purpose = string(data, "name", 100), string(data, "purpose", 2000)
    require(name.strip() and purpose.strip(), "floor needs a name and purpose")
    return {"level": data["level"], "name": name, "purpose": purpose}


def install_floor(state: dict, descriptor: dict, proposal: str, at: float, sequence: int) -> None:
    initialize(state)
    descriptor = floor_descriptor(descriptor)
    rule = state.get("council", {}).get("rules", {}).get(proposal, {})
    require(rule.get("status") == "active" and rule.get("mode") == "floor"
            and rule.get("floor") == descriptor, "floor needs its matching enacted council rule")
    floors = state["life"]["floors"]
    require(descriptor["level"] == max(int(key) for key in floors) + 1,
            "a floor must be the unique next contiguous level")
    require(type(at) in (int, float) and math.isfinite(at) and at >= enabled(state)
            and type(sequence) is int and sequence == state["sequence"] + 1,
            "invalid floor enactment observation")
    floors[str(descriptor["level"])] = {**descriptor, "proposal": proposal,
                                       "enacted_at": at, "enacted_sequence": sequence}


def approved_floor(state: dict, level: int) -> None:
    require(type(level) is int and level >= 0, "invalid room floor")
    floor = state["life"]["floors"].get(str(level))
    require(floor is not None, "room floor has not been approved")
    if level:
        rule = state.get("council", {}).get("rules", {}).get(floor["proposal"], {})
        require(rule.get("status") == "active" and rule.get("mode") == "floor" and
                rule.get("floor") == {key: floor[key] for key in ("level", "name", "purpose")},
                "room floor authorization is no longer active")


def live_task(state: dict, task_id: str, actor: str, at: float) -> dict:
    task = state["tasks"].get(task_id, {})
    require(task.get("status") == "claimed" and task.get("owner") == actor and task["until"] > at,
            "construction requires the builder's current owned live task")
    return task


def named(data: dict, key: str, limit=2000) -> str:
    value = string(data, key, limit)
    require(bool(value.strip()), f"{key} must not be blank")
    return value


def remember(room: dict, kind: str, actor: str, at: float, sequence: int, **details) -> None:
    room["history"].append({"kind": kind, "actor": actor, "at": at, "sequence": sequence,
                            "generation": room["generation"], **details})


def occupants(state: dict, room_id: str, actor: str, at: float) -> list[str]:
    uncertain = []
    for resident, presence in state["life"]["presence"].items():
        if resident == actor or presence["room"] != room_id or not state["residents"][resident]["awake"]:
            continue
        task = state["tasks"].get(presence.get("task"), {})
        supervised = any(run["resident"] == resident and run["status"] == "active"
                         for run in state["life"]["runs"].values())
        working = task.get("status") == "claimed" and task.get("owner") == resident and task.get("until", 0) > at
        require(not (supervised or working), "another confirmed awake occupant is still using this room")
        uncertain.append(resident)
    return sorted(uncertain)


def apply(state: dict, event: dict) -> None:
    initialize(state)
    data, actor, at = event["data"], event["actor"], event["at"]
    kind, sequence = data.get("kind"), state["sequence"] + 1
    require(kind in KINDS, "unknown room lifecycle operation")
    required = {"kind", "room", "expect"}
    required |= ({"name", "purpose", "reason", "floor", "task"} if kind == "room-plan" else
                 {"name", "purpose", "reason", "task"} if kind == "room-repurpose" else
                 {"evidence"} if kind == "room-open" else {"reason"})
    require(set(data) == required, "invalid room lifecycle fields")
    room_id = string(data, "room", 100)
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", room_id) is not None, "invalid room identifier")
    require(state["residents"].get(actor, {}).get("awake") is True, "room work requires an awake resident")
    rooms = state["life"]["rooms"]
    room = rooms.get(room_id)
    require(type(data["expect"]) is int and data["expect"] == (room["generation"] if room else 0),
            "room generation changed")
    if kind in {"room-plan", "room-repurpose"}:
        uncertain = []
        name, purpose, reason = (named(data, key, 100 if key == "name" else 2000)
                                 for key in ("name", "purpose", "reason"))
        task_id = string(data, "task", 100)
        task = live_task(state, task_id, actor, at)
        if kind == "room-plan":
            approved_floor(state, data["floor"])
            if room is not None:
                require(room["status"] == "construction", "existing room needs explicit repurpose")
                require(room["task"] == task_id and task["generation"] > room["task_generation"],
                        "takeover needs the same construction task at a newer claimed generation")
                require(data["floor"] == room["floor"], "takeover cannot silently move its room")
            else:
                room = {"generation": 0, "floor": data["floor"], "legacy": False,
                        "observed_since": at, "last_used_at": None, "last_used_sequence": None,
                        "last_used_by": None, "history": []}
                rooms[room_id] = room
        else:
            require(room is not None and room["status"] in {"open", "closed"},
                    "only an open or closed room can be repurposed")
            approved_floor(state, room["floor"])
            uncertain = occupants(state, room_id, actor, at)
        previous = {key: room.get(key) for key in ("name", "purpose", "builder", "task", "task_generation", "status")}
        room.update(name=name, purpose=purpose, reason=reason, builder=actor, task=task_id,
            task_generation=task["generation"], status="construction", planned_at=at,
            planned_sequence=sequence, opened_at=None, opened_sequence=None, closed_at=None, closed_sequence=None,
            generation=room["generation"] + 1)
        remember(room, kind, actor, at, sequence, reason=reason, name=name, purpose=purpose,
                 builder=actor, task=task_id, task_generation=task["generation"], previous=previous,
                 unconfirmed_occupants=uncertain)
    elif kind == "room-open":
        require(room is not None and room["status"] == "construction", "room is not under construction")
        approved_floor(state, room["floor"])
        require(room["builder"] == actor, "only the recorded builder can open this construction")
        task = state["tasks"].get(room["task"], {})
        require(task.get("status") == "done" and task.get("owner") == actor and
                task.get("generation") == room["task_generation"] and
                task.get("finished_at", 0) > room["planned_sequence"] and bool(task.get("artifacts")),
                "opening requires this builder's completed construction task with later immutable artifacts")
        evidence = named(data, "evidence")
        hashes = {name: value["sha256"] for name, value in task["artifacts"].items()}
        room.update(status="open", opened_at=at, opened_sequence=sequence, generation=room["generation"] + 1)
        remember(room, kind, actor, at, sequence, reason=evidence, evidence=evidence,
                 task=room["task"], artifacts=hashes)
    else:
        require(room is not None and room["status"] != "closed", "room is missing or already closed")
        reason = named(data, "reason")
        construction = state["tasks"].get(room.get("task"), {})
        require(not (room["status"] == "construction" and construction.get("status") == "claimed"
                    and construction.get("owner") != actor and construction.get("until", 0) > at),
                "another builder still owns live construction")
        uncertain = occupants(state, room_id, actor, at)
        room.update(status="closed", closed_at=at, closed_sequence=sequence, generation=room["generation"] + 1)
        remember(room, kind, actor, at, sequence, reason=reason, unconfirmed_occupants=uncertain)


def activity(state: dict, actor: str, room_id: str, at: float, sequence: int) -> None:
    initialize(state)
    room = state["life"]["rooms"].get(room_id)
    require(room is not None and room["status"] != "closed", "room is unavailable for activity")
    require(state["residents"].get(actor, {}).get("awake") is True, "room activity requires an awake resident")
    require(type(at) in (int, float) and math.isfinite(at) and at >= room["observed_since"] and
            (room["last_used_at"] is None or at >= room["last_used_at"]) and type(sequence) is int and
            sequence > (room["last_used_sequence"] or 0),
            "invalid room use observation")
    if room["status"] == "construction":
        require(actor == room["builder"], "construction activity belongs to its recorded builder")
        task = live_task(state, room["task"], actor, at)
        require(task["generation"] == room["task_generation"], "construction builder generation changed")
    room.update(last_used_at=at, last_used_sequence=sequence, last_used_by=actor)
