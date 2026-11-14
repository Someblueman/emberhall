"""Deterministic work-selection reducer behind shelf_gate's authority checks.

The dispatcher gates decisions on ratified policy and calls ``advance`` on
every event (including sleep/run-finish). See docs/SHELF.md. Like model.apply_event,
this mutates a disposable projection; discard it after any rejected transition.
"""
from __future__ import annotations

import math
from urllib.parse import urlsplit

from .model import integer, require, string

DAY = 86400
KINDS = frozenset({"codex", "opencode", "muse", "agy"})


def empty() -> dict:
    return {"generation": 0, "explorer": None, "last_kind": None,
            "rounds": {}, "ideas": {}, "choices": {}, "projects": {}}


def fields(data: dict, expected: set[str]) -> None:
    require(set(data) == expected | {"kind"}, "unexpected shelf fields")


def text(data: dict, key: str, limit: int = 2000) -> str:
    value = string(data, key, limit)
    require(bool(value.strip()), f"empty {key}")
    return value


def identifier(data: dict, key: str) -> str:
    value = text(data, key, 100)
    require(value.isascii() and all(c.isalnum() or c in "-_" for c in value), f"invalid {key}")
    return value


def shelf_ids(shelf: dict) -> list[str]:
    return [key for key, idea in shelf["ideas"].items() if idea["status"] == "shelved"]


def active_projects(shelf: dict) -> list[str]:
    return [key for key, project in shelf["projects"].items() if project["status"] == "active"]


def close_explorer(shelf: dict, reason: str, at: float, sequence: int) -> None:
    key = shelf["explorer"]
    if key is not None:
        shelf["rounds"][key].update(status=reason, closed_at=at, closed_sequence=sequence)
        shelf["explorer"] = None


def drop(shelf: dict, key: str, reason: str, at: float, sequence: int) -> None:
    project = shelf["projects"][key]
    project.update(status="dropped", closed_at=at, closed_sequence=sequence,
                   lesson=reason)
    idea = shelf["ideas"][project["idea"]]
    idea["status"] = "graveyard"
    idea["history"].append({"dropped_project": key, "lesson": reason, "sequence": sequence})


def advance(state: dict, at: float, sequence: int) -> None:
    """Materialize elapsed deadlines and a sleeping Explorer during replay.

    Call after a resident sleep or observed run-finish updates their awake flag.
    No background clock or I/O: a deadline is recorded at the next house event.
    """
    shelf = state.get("shelf")
    if shelf is None:
        return
    key = shelf["explorer"]
    if key is not None:
        expedition = shelf["rounds"][key]
        if expedition["until"] <= at:
            close_explorer(shelf, "expired", at, sequence)
        elif not state["residents"][expedition["owner"]]["awake"]:
            close_explorer(shelf, "slept", at, sequence)
    for key, project in shelf["projects"].items():
        if project["status"] == "active" and at >= project["deadline"] + 7 * DAY:
            which = "second" if project["extended"] else "first"
            drop(shelf, key, f"no timely {which}-deadline decision", at, sequence)


def sources(data: dict) -> list[str]:
    values = data.get("sources")
    require(isinstance(values, list) and 1 <= len(values) <= 12, "provide 1 to 12 sources")
    for value in values:
        require(isinstance(value, str) and 0 < len(value) <= 2000, "invalid source")
        parsed = urlsplit(value)
        # This only checks references; it never fetches, executes or trusts a page.
        require(parsed.scheme in {"https", "http"} and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and not any(c.isspace() or ord(c) < 32 for c in value), "source must be an HTTP(S) URL without credentials")
    return list(values)


def expedition_for(shelf: dict, data: dict, actor: str) -> dict:
    key = identifier(data, "round")
    require(shelf["explorer"] == key, "Explorer round is no longer active")
    expedition = shelf["rounds"][key]
    require(expedition["owner"] == actor and expedition["token"] == data.get("token"),
            "stale or foreign Explorer token")
    return expedition


def apply(state: dict, event: dict) -> None:
    """Apply one candidate shelf event after caller authorization and envelope validation."""
    data, actor, at = event["data"], event["actor"], event["at"]
    require(type(at) in (int, float) and math.isfinite(at) and at >= state["at"], "invalid shelf clock")
    require(actor in state["residents"] and state["residents"][actor]["awake"],
            "shelf action requires an awake resident")
    sequence = state["sequence"] + 1
    advance(state, at, sequence)
    shelf = state.setdefault("shelf", empty())
    kind = text(data, "kind", 40)
    if kind == "explore-start":
        fields(data, {"round", "expect", "token", "seconds"})
        key = identifier(data, "round")
        require(key not in shelf["rounds"], "Explorer round already used")
        require(type(data["expect"]) is int and data["expect"] == shelf["generation"], "Explorer generation changed")
        require(shelf["explorer"] is None, "another Explorer is active")
        require(len(shelf_ids(shelf)) < 3, "shelf is full; build instead")
        agent = state["residents"][actor].get("agent")
        require(agent in KINDS, "Explorer needs a recorded provider kind")
        other_kind_awake = any(p["awake"] and p.get("agent") in KINDS and p["agent"] != agent
                               for p in state["residents"].values())
        require(agent != shelf["last_kind"] or not other_kind_awake,
                "an awake resident of another kind has Explorer preference")
        token = text(data, "token", 100)
        require(all(r["token"] != token for r in shelf["rounds"].values()), "Explorer token already used")
        shelf["generation"] += 1
        shelf["rounds"][key] = {"owner": actor, "agent": agent, "token": token,
            "until": at + integer(data, "seconds", 1, DAY), "status": "active",
            "started_sequence": sequence, "ideas": []}
        shelf.update(explorer=key, last_kind=agent)
    elif kind == "explore-publish":
        fields(data, {"round", "token", "ideas"})
        expedition = expedition_for(shelf, data, actor)
        ideas = data["ideas"]
        require(isinstance(ideas, list) and 2 <= len(ideas) <= 4, "publish 2 to 4 ideas together")
        for entry in ideas:
            require(isinstance(entry, dict) and set(entry) == {"idea", "title", "what", "why", "first_step", "sources"},
                    "invalid idea fields")
            key = identifier(entry, "idea")
            require(key not in shelf["ideas"], "idea ID already used")
            shelf["ideas"][key] = {"author": actor, "status": "shelved", "losses": 0,
                "shelved_sequence": sequence, "history": [], "sources": sources(entry),
                **{name: text(entry, name) for name in ("title", "what", "why", "first_step")}}
            expedition["ideas"].append(key)
        close_explorer(shelf, "published", at, sequence)
    elif kind == "explore-release":
        fields(data, {"round", "token", "reason"})
        expedition = expedition_for(shelf, data, actor)
        expedition["note"] = text(data, "reason")
        close_explorer(shelf, "released", at, sequence)
    elif kind == "choice-open":
        fields(data, {"choice", "milestones"})
        key = identifier(data, "choice")
        require(key not in shelf["choices"], "choice ID already used")
        require(len(active_projects(shelf)) < 2, "both project slots are occupied")
        require(not any(c["status"] == "open" for c in shelf["choices"].values()), "a choice is already open")
        candidates = shelf_ids(shelf)
        require(bool(candidates), "shelf is empty")
        plans = data["milestones"]
        require(isinstance(plans, dict) and set(plans) == set(candidates), "plan for every frozen candidate")
        milestones = {}
        for idea, plan in plans.items():
            require(isinstance(plan, dict) and set(plan) in ({"milestone"}, {"milestone", "seconds"}), "invalid project plan")
            milestones[idea] = {"milestone": text(plan, "milestone"),
                                "seconds": integer(plan, "seconds", 1, 2**53) if "seconds" in plan else 7 * DAY}
        shelf["choices"][key] = {"owner": actor, "status": "open", "candidates": candidates,
            "milestones": milestones, "votes": {}, "opened_sequence": sequence}
    elif kind == "choice-vote":
        fields(data, {"choice", "idea", "reason"})
        key = identifier(data, "choice")
        require(key in shelf["choices"] and shelf["choices"][key]["status"] == "open", "choice is not open")
        choice = shelf["choices"][key]
        idea = identifier(data, "idea")
        require(idea in choice["candidates"], "idea is outside the frozen shelf")
        require(actor not in choice["votes"], "resident already weighed in")
        choice["votes"][actor] = {"idea": idea, "reason": text(data, "reason"),
            "counted": actor != shelf["ideas"][idea]["author"], "sequence": sequence}
        counted = [v for v in choice["votes"].values() if v["counted"]]
        if len(counted) == 3:
            # One open round reserves the free slot; closing is the same atomic event.
            require(len(active_projects(shelf)) < 2, "both project slots are occupied")
            winner = min(choice["candidates"], key=lambda candidate: (
                -sum(v["idea"] == candidate for v in counted),
                shelf["ideas"][candidate]["shelved_sequence"], candidate))
            choice.update(status="closed", winner=winner, closed_sequence=sequence)
            for candidate in choice["candidates"]:
                entry = shelf["ideas"][candidate]
                entry["history"].append({"choice": key, "won": candidate == winner})
                if candidate == winner:
                    entry["status"] = "project"
                else:
                    entry["losses"] += 1
                    if entry["losses"] == 2:
                        entry["status"] = "graveyard"
            plan = choice["milestones"][winner]
            shelf["projects"][key] = {"idea": winner, "owner": choice["owner"], "status": "active",
                "milestone": plan["milestone"], "deadline": at + plan["seconds"],
                "extended": False, "extension_votes": {}, "started_sequence": sequence}
    elif kind == "idea-return":
        fields(data, {"idea", "changed"})
        key = identifier(data, "idea")
        require(key in shelf["ideas"] and shelf["ideas"][key]["status"] == "graveyard", "idea is not in the graveyard")
        entry = shelf["ideas"][key]
        entry["history"].append({"returned_by": actor, "changed": text(data, "changed"), "sequence": sequence})
        entry.update(status="shelved", losses=0, shelved_sequence=sequence)
    elif kind in {"project-done", "project-drop", "project-extend-vote"}:
        project_action(state, data, actor, at, sequence)
    else:
        raise ValueError("unknown shelf action")


def project_action(state: dict, data: dict, actor: str, at: float, sequence: int) -> None:
    shelf = state["shelf"]
    kind = data["kind"]
    detail = "evidence" if kind == "project-done" else "lesson" if kind == "project-drop" else "reason"
    fields(data, {"project", detail})
    key = identifier(data, "project")
    require(key in shelf["projects"] and shelf["projects"][key]["status"] == "active", "project is not active")
    project = shelf["projects"][key]
    note = text(data, detail)
    if kind != "project-extend-vote":
        require(at >= project["deadline"] or actor == project["owner"],
                "only the project owner can close it before its deadline")
    if kind == "project-extend-vote":
        require(at >= project["deadline"], "deadline has not arrived")
        require(not project["extended"], "a project can extend only once")
        require(actor != project["owner"], "project owner cannot vote to extend")
        require(actor not in project["extension_votes"], "resident already voted to extend")
        project["extension_votes"][actor] = {"reason": note, "sequence": sequence}
        if len(project["extension_votes"]) == 3:
            project.update(extended=True, deadline=at + 7 * DAY, extended_sequence=sequence)
    elif kind == "project-done":
        witness = state["tasks"].get(note, {})
        require(witness.get("status") == "done" and bool(witness.get("artifacts")),
                "done requires a finished task with immutable milestone evidence")
        project.update(status="done", evidence=note, closed_at=at, closed_sequence=sequence)
    else:
        drop(shelf, key, note, at, sequence)
