"""Recorded places, continuing ambitions and supervised resident lifetimes.

This is a projection, not a process monitor. Only the supervisor's observed
receipts establish process starts/stops; an arrival alone is not proof of liveness.
"""
from __future__ import annotations

import math
import re

from .model import require, string

CONTROLLER = "watch-keeper"
KINDS = {"codex", "opencode", "muse", "agy"}
ROOMS = {"door": "The Door", "hearth": "The Hearth", "workshop": "The Workshop",
         "archive": "The Archive", "council": "The Council", "bedroom": "The Beds"}


def number(value, name, minimum=0):
    require(type(value) in (int, float) and math.isfinite(value) and value >= minimum,
            f"invalid {name}")
    return value


def fields(data, required, optional=()):
    require(set(required) <= data.keys() <= set(required) | set(optional), "invalid life fields")


def identifier(data, key):
    value = string(data, key, 100)
    require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", value) is not None, f"invalid {key}")
    return value


def empty():
    return {"rooms": {key: {"name": name} for key, name in ROOMS.items()},
            "ambitions": {}, "runs": {}, "budgets": {}, "requests": {}, "presence": {}}


def apply(state, event):
    data, actor, at = event["data"], event["actor"], event["at"]
    seq = state["sequence"] + 1
    life = state.setdefault("life", empty())
    kind = string(data, "kind", 40)
    if kind == "identity":
        fields(data, {"kind", "agent", "model"})
        from .providers import validate_model
        validate_model(data["agent"], data["model"])
        resident = state["residents"][actor]
        require("agent" not in resident, "resident kind already recorded")
        resident.update(agent=data["agent"], model=data["model"])
    elif kind == "room":
        fields(data, {"kind", "room", "name"})
        room = identifier(data, "room")
        require(room not in life["rooms"], "room already exists")
        life["rooms"][room] = {"name": string(data, "name", 100), "sequence": seq}
    elif kind == "activity":
        fields(data, {"kind", "room"}, {"task"})
        require(data["room"] in life["rooms"], "unknown room")
        if "task" in data:
            task = state["tasks"].get(data["task"], {})
            require(task.get("owner") == actor and task.get("status") == "claimed"
                    and task["until"] > at, "activity requires own live task")
        life["presence"][actor] = {**data, "at": at, "sequence": seq}
    elif kind == "ambition":
        fields(data, {"kind", "ambition", "title", "description", "status", "next_step", "expect"})
        key = identifier(data, "ambition")
        old = life["ambitions"].get(key, {})
        require(type(data["expect"]) is int and data["expect"] == old.get("generation", 0),
                "ambition generation changed")
        require(data["status"] in {"growing", "resting", "fulfilled"}, "invalid ambition status")
        for name in ("title", "description", "next_step"):
            string(data, name)
        life["ambitions"][key] = {**data, "generation": data["expect"] + 1,
                                  "resident": actor, "sequence": seq, "at": at}
    elif kind == "help":
        fields(data, {"kind", "request", "reason"}, {"task", "agent"})
        key = identifier(data, "request")
        require(key not in life["requests"], "help request exists")
        string(data, "reason")
        if "task" in data:
            require(data["task"] in state["tasks"], "unknown help task")
        if "agent" in data:
            require(data["agent"] in KINDS, "unknown agent kind")
        life["requests"][key] = {**data, "resident": actor, "status": "pending", "at": at}
    else:
        require(actor == CONTROLLER, "only the supervisor records process observations")
        if kind == "run-start":
            fields(data, {"kind", "run", "resident", "agent", "model", "source_head",
                          "workspace", "policy_revision", "mode"}, {"help_request"})
            from .providers import validate_model
            validate_model(data["agent"], data["model"])
            run = identifier(data, "run")
            resident = identifier(data, "resident")
            require(run not in life["runs"], "run already exists")
            require(resident not in state["residents"], "run resident already exists")
            active = [r for r in life["runs"].values() if r["status"] == "active"]
            require(len(active) < 3, "three residents are already home")
            require(all(r["resident"] != resident for r in active), "resident already running")
            require(life["budgets"].get(data["agent"], {}).get("until", 0) <= at,
                    "provider is cooling down")
            require(data["mode"] in {"work", "review"}, "invalid work mode")
            require(re.fullmatch("[0-9a-f]{40}", data["source_head"]) is not None,
                    "invalid source head")
            string(data, "policy_revision", 100)
            require(data["workspace"] == "residents/" + run, "invalid private workspace")
            if "help_request" in data:
                request = life["requests"].get(data["help_request"], {})
                require(request.get("status") == "pending", "help already taken")
                request.update(status="assigned", run=run)
            life["runs"][run] = {**data, "status": "active", "started_at": at,
                                 "started_sequence": seq}
        elif kind == "run-launched":
            fields(data, {"kind", "run", "pgid"})
            run = life["runs"][data["run"]]
            require(run["status"] == "active" and "pgid" not in run, "run already launched/ended")
            require(type(data["pgid"]) is int and data["pgid"] > 1, "invalid process group")
            run.update(pgid=data["pgid"], launched_sequence=seq)
        elif kind == "run-finish":
            fields(data, {"kind", "run", "outcome", "exit_code", "usage", "elapsed_seconds"})
            run = life["runs"][data["run"]]
            require(run["status"] == "active", "run already ended")
            require(data["outcome"] in {"success", "quota", "interrupted", "failed"}, "invalid outcome")
            require(data["exit_code"] is None or type(data["exit_code"]) is int, "invalid exit code")
            require(isinstance(data["usage"], dict), "invalid usage")
            for key, value in data["usage"].items():
                require(key in {"input_tokens", "output_tokens", "cached_input_tokens", "total_tokens"},
                        "unknown usage field")
                number(value, key)
            number(data["elapsed_seconds"], "elapsed seconds")
            run.update(outcome=data["outcome"], exit_code=data["exit_code"], usage=dict(data["usage"]),
                       elapsed_seconds=data["elapsed_seconds"], status="completed", ended_at=at,
                       ended_sequence=seq)
            if run["resident"] in state["residents"]:
                state["residents"][run["resident"]]["awake"] = False
            # The supervisor has confirmed the entire process group stopped.
            # Fence its old tokens immediately, preserving the generation and
            # token history. Unconfirmed/manual disappearances still use expiry.
            released = []
            for task_id, task in state["tasks"].items():
                if task["owner"] == run["resident"] and task["status"] == "claimed":
                    released.append(task_id)
                    task.update(status="open", owner=None, token=None, until=0,
                                interrupted_run=data["run"])
            run["released_tasks"] = released
            if "help_request" in run and data["outcome"] != "success":
                request = life["requests"][run["help_request"]]
                if request.get("run") == data["run"] and request["status"] == "assigned":
                    request.update(status="pending")
                    request.pop("run", None)
        elif kind == "budget":
            fields(data, {"kind", "agent", "until", "reason"})
            require(data["agent"] in KINDS, "unknown agent kind")
            number(data["until"], "cooldown", at)
            string(data, "reason", 1000)
            life["budgets"][data["agent"]] = {**data, "at": at, "sequence": seq}
        elif kind == "help-resolved":
            fields(data, {"kind", "request", "reason"})
            request = life["requests"][data["request"]]
            string(data, "reason")
            require(request["status"] != "resolved", "request already resolved")
            request.update(status="resolved", resolution=data["reason"], resolved_at=at)
        else:
            raise ValueError("unknown life operation")
