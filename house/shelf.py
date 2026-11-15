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


# Selection version 3 (Steward course correction, 15 November): one slot is
# reserved for a weeks-long great work with several milestones; one slot holds
# a small project. Ideas carry a scale; each choice fills exactly one slot.
GREAT_MILESTONES = (2, 8)


def scale(idea: dict) -> str:
    return idea.get("scale", "small")


def slot(project: dict) -> str:
    return project.get("slot", "small")


def slot_free(shelf: dict, which: str) -> bool:
    return not any(slot(shelf["projects"][key]) == which for key in active_projects(shelf))


def great_ideas(shelf: dict) -> list[str]:
    return [key for key in shelf_ids(shelf) if scale(shelf["ideas"][key]) == "great"]


def great_wanted(shelf: dict) -> bool:
    """The great slot is free and the shelf lacks a real great-work choice."""
    return slot_free(shelf, "great") and len(great_ideas(shelf)) < 2


# Open research (Steward decision, 15 November; owner migration below). Research
# no longer stops at a full shelf: one round may start every few hours while the
# shelf is under its ceiling. An idea needs a research brief; a shelved idea
# with none after two days moves to the graveyard. Before the migration every
# transition is exactly as it was, so the journal replays unchanged.
OPEN_RESEARCH = "upgrade-20261115-open-research"
RESEARCH_GAP_SECONDS = 4 * 3600
SHELF_CEILING = 10
BRIEF_SECONDS = 2 * DAY
BRIEF_FIELDS = ("audience", "exists", "first_version", "risks")
BRIEF_MINIMUM = 120
EXPIRED = "No research brief was recorded within two days of shelving."


def open_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(OPEN_RESEARCH)
    return None if entry is None else entry["at"]


def research_due(shelf: dict, at: float) -> bool:
    return (len(shelf_ids(shelf)) < SHELF_CEILING
            and at - shelf.get("research_at", -math.inf) >= RESEARCH_GAP_SECONDS)


def research_open(state: dict, shelf: dict, at: float, selection_version: int) -> bool:
    """Whether an Explorer round may start now. life.explorer_demand asks the same question."""
    return (len(shelf_ids(shelf)) < 3 or (selection_version >= 3 and great_wanted(shelf))
            or (open_since(state) is not None and research_due(shelf, at)))


def brief_due(state: dict, idea: dict) -> float | None:
    """When a shelved idea without a brief expires; None if it does not."""
    since = open_since(state)
    if since is None or idea["status"] != "shelved" or "brief" in idea:
        return None
    return max(idea.get("shelved_at", since), since) + BRIEF_SECONDS


def brief(data: dict, key: str, actor: str, sequence: int) -> dict:
    value = data.get(key)
    require(isinstance(value, dict) and set(value) == set(BRIEF_FIELDS),
            "a brief states audience, exists, first_version and risks")
    parts = {name: text(value, name) for name in BRIEF_FIELDS}
    require(all(len(part.strip()) >= BRIEF_MINIMUM for part in parts.values()),
            f"each part of a brief needs at least {BRIEF_MINIMUM} characters")
    return parts | {"author": actor, "sequence": sequence}


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
    if open_since(state) is not None:
        frozen = {idea for choice in shelf["choices"].values() if choice["status"] == "open"
                  for idea in choice["candidates"]}
        for key, idea in shelf["ideas"].items():
            due = brief_due(state, idea)
            if due is not None and at >= due and key not in frozen:
                idea["status"] = "graveyard"
                idea["history"].append({"expired": True, "lesson": EXPIRED, "sequence": sequence})


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


def apply(state: dict, event: dict, *, selection_version: int = 1) -> None:
    """Apply one candidate shelf event after caller authorization and envelope validation."""
    data, actor, at = event["data"], event["actor"], event["at"]
    require(type(at) in (int, float) and math.isfinite(at) and at >= state["at"], "invalid shelf clock")
    require(actor in state["residents"] and state["residents"][actor]["awake"],
            "shelf action requires an awake resident")
    sequence = state["sequence"] + 1
    advance(state, at, sequence)
    shelf = state.setdefault("shelf", empty())
    kind = text(data, "kind", 40)
    opened = open_since(state) is not None
    if kind == "explore-start":
        fields(data, {"round", "expect", "token", "seconds"})
        key = identifier(data, "round")
        require(key not in shelf["rounds"], "Explorer round already used")
        require(type(data["expect"]) is int and data["expect"] == shelf["generation"], "Explorer generation changed")
        require(shelf["explorer"] is None, "another Explorer is active")
        require(research_open(state, shelf, at, selection_version),
                "the shelf is full and a research round started recently; build instead" if opened
                else "shelf is full; build instead")
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
        if opened:
            shelf["rounds"][key]["started_at"] = at
            shelf["research_at"] = at
    elif kind == "explore-publish":
        fields(data, {"round", "token", "ideas"})
        expedition = expedition_for(shelf, data, actor)
        ideas = data["ideas"]
        require(isinstance(ideas, list) and 2 <= len(ideas) <= 4, "publish 2 to 4 ideas together")
        base = {"idea", "title", "what", "why", "first_step", "sources"}
        for entry in ideas:
            require(isinstance(entry, dict), "invalid idea fields")
            if opened:
                require("brief" in entry, "each idea needs a research brief: "
                        "audience, exists, first_version and risks")
            core = set(entry) - {"brief"} if opened else set(entry)
            require(core == base or (selection_version >= 3 and core == base | {"scale"}),
                    "invalid idea fields")
            key = identifier(entry, "idea")
            require(key not in shelf["ideas"], "idea ID already used")
            shelf["ideas"][key] = {"author": actor, "status": "shelved", "losses": 0,
                "shelved_sequence": sequence, "history": [], "sources": sources(entry),
                **{name: text(entry, name) for name in ("title", "what", "why", "first_step")}}
            if "scale" in entry:
                require(entry["scale"] in {"great", "small"}, "scale must be great or small")
                shelf["ideas"][key]["scale"] = entry["scale"]
            if opened:
                shelf["ideas"][key].update(shelved_at=at, brief=brief(entry, "brief", actor, sequence))
            expedition["ideas"].append(key)
        close_explorer(shelf, "published", at, sequence)
    elif kind == "explore-release":
        fields(data, {"round", "token", "reason"})
        expedition = expedition_for(shelf, data, actor)
        expedition["note"] = text(data, "reason")
        close_explorer(shelf, "released", at, sequence)
    elif kind == "choice-open":
        if selection_version >= 3:
            require(set(data) in ({"kind", "choice", "milestones"}, {"kind", "choice", "milestones", "slot"}),
                    "unexpected shelf fields")
            which = data.get("slot", "small")
            require(which in {"great", "small"}, "slot must be great or small")
        else:
            fields(data, {"choice", "milestones"})
            which = None
        key = identifier(data, "choice")
        require(key not in shelf["choices"], "choice ID already used")
        if which is None:
            require(len(active_projects(shelf)) < 2, "both project slots are occupied")
        else:
            require(slot_free(shelf, which), f"the {which} project slot is occupied")
        require(not any(c["status"] == "open" for c in shelf["choices"].values()), "a choice is already open")
        candidates = shelf_ids(shelf) if which is None else [
            idea for idea in shelf_ids(shelf) if scale(shelf["ideas"][idea]) == which]
        require(bool(candidates), "shelf is empty" if which is None else f"no shelved {which}-scale ideas")
        plans = data["milestones"]
        require(isinstance(plans, dict) and set(plans) == set(candidates), "plan for every frozen candidate")
        milestones = {}
        for idea, plan in plans.items():
            if which == "great":
                require(isinstance(plan, list) and GREAT_MILESTONES[0] <= len(plan) <= GREAT_MILESTONES[1],
                        "a great work needs 2 to 8 ordered milestones")
                stages = []
                for stage in plan:
                    require(isinstance(stage, dict) and set(stage) in ({"milestone"}, {"milestone", "seconds"}),
                            "invalid great-work milestone")
                    stages.append({"milestone": text(stage, "milestone"),
                                   "seconds": integer(stage, "seconds", DAY, 60 * DAY) if "seconds" in stage else 7 * DAY})
                milestones[idea] = {"milestones": stages}
                continue
            require(isinstance(plan, dict) and set(plan) in ({"milestone"}, {"milestone", "seconds"}), "invalid project plan")
            milestones[idea] = {"milestone": text(plan, "milestone"),
                                "seconds": integer(plan, "seconds", 1, 2**53) if "seconds" in plan else 7 * DAY}
        shelf["choices"][key] = {"owner": actor, "status": "open", "candidates": candidates,
            "milestones": milestones, "votes": {}, "opened_sequence": sequence}
        if selection_version >= 2:
            shelf["choices"][key]["selection_version"] = selection_version
        if which is not None:
            shelf["choices"][key]["slot"] = which
    elif kind == "choice-vote":
        fields(data, {"choice", "idea", "reason"})
        key = identifier(data, "choice")
        require(key in shelf["choices"] and shelf["choices"][key]["status"] == "open", "choice is not open")
        choice = shelf["choices"][key]
        revised = choice.get("selection_version", 1) >= 2
        idea = None if revised and data.get("idea") is None else identifier(data, "idea")
        require(idea is None or idea in choice["candidates"], "idea is outside the frozen shelf")
        require(actor not in choice["votes"], "resident already weighed in")
        choice["votes"][actor] = {"idea": idea, "reason": text(data, "reason"),
            "counted": idea is None or actor != shelf["ideas"][idea]["author"], "sequence": sequence}
        counted = [v for v in choice["votes"].values() if v["counted"]]
        if len(counted) == 3:
            # One open round reserves the free slot; closing is the same atomic event.
            if "slot" in choice:
                require(slot_free(shelf, choice["slot"]), f"the {choice['slot']} project slot is occupied")
            else:
                require(len(active_projects(shelf)) < 2, "both project slots are occupied")
            winner = min(choice["candidates"], key=lambda candidate: (
                -sum(v["idea"] == candidate for v in counted),
                shelf["ideas"][candidate]["shelved_sequence"], candidate))
            if revised and sum(v["idea"] == winner for v in counted) < 2:
                choice.update(status="rejected", winner=None, closed_sequence=sequence)
                for candidate in choice["candidates"]:
                    entry = shelf["ideas"][candidate]
                    entry["status"] = "graveyard"
                    entry["history"].append({"choice": key, "won": False, "rejected": True,
                        "lesson": "Shortlist rejected: no candidate earned two of three votes.",
                        "sequence": sequence})
                return
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
            if choice.get("slot") == "great":
                stages = plan["milestones"]
                shelf["projects"][key] = {"idea": winner, "owner": choice["owner"], "status": "active",
                    "slot": "great", "milestones": stages, "stage": 0, "completed": [],
                    "milestone": stages[0]["milestone"], "deadline": at + stages[0]["seconds"],
                    "extended": False, "extension_votes": {}, "started_sequence": sequence}
                return
            shelf["projects"][key] = {"idea": winner, "owner": choice["owner"], "status": "active",
                "milestone": plan["milestone"], "deadline": at + plan["seconds"],
                "extended": False, "extension_votes": {}, "started_sequence": sequence}
            if "slot" in choice:
                shelf["projects"][key]["slot"] = choice["slot"]
    elif kind == "idea-return":
        fields(data, {"idea", "changed"})
        key = identifier(data, "idea")
        require(key in shelf["ideas"] and shelf["ideas"][key]["status"] == "graveyard", "idea is not in the graveyard")
        entry = shelf["ideas"][key]
        entry["history"].append({"returned_by": actor, "changed": text(data, "changed"), "sequence": sequence})
        entry.update(status="shelved", losses=0, shelved_sequence=sequence)
        if opened:
            entry["shelved_at"] = at
    elif kind == "idea-brief":
        require(opened, "unknown shelf action")
        fields(data, {"idea", "brief"})
        key = identifier(data, "idea")
        require(key in shelf["ideas"] and shelf["ideas"][key]["status"] == "shelved", "idea is not on the shelf")
        shelf["ideas"][key]["brief"] = brief(data, "brief", actor, sequence)
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
        if slot(project) == "great" and project["stage"] + 1 < len(project["milestones"]):
            # A great work advances milestone by milestone; only the last closes it.
            project["completed"].append({"stage": project["stage"], "milestone": project["milestone"],
                                         "evidence": note, "sequence": sequence})
            project["stage"] += 1
            stage = project["milestones"][project["stage"]]
            project.update(milestone=stage["milestone"], deadline=at + stage["seconds"],
                           extended=False, extension_votes={})
            return
        if slot(project) == "great":
            project["completed"].append({"stage": project["stage"], "milestone": project["milestone"],
                                         "evidence": note, "sequence": sequence})
        project.update(status="done", evidence=note, closed_at=at, closed_sequence=sequence)
    else:
        drop(shelf, key, note, at, sequence)
