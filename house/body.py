"""Publish a bounded, public dollhouse projection at every verified journal event."""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import re
import subprocess
import time

from .council import lapsed, veto_window
from .model import apply_event
from .record import Record
from .work_metrics import public_observation

ROOMS = {"door": "The door", "hearth": "Hearth", "workshop": "Workshop",
         "archive": "Archive", "council": "Council"}
KINDS = {"codex", "opencode", "muse", "agy"}
WATCH_PREFIX = "house-watch-v1 "


def label(value: object, limit: int = 180) -> str:
    """Public labels are plain, bounded strings, never rendered as HTML."""
    return " ".join(str(value).split())[:limit]


HEARTH_VOICES = 12
# Residents' words stay private unless the Steward installs this scope. Only
# speech recorded after that is published; nothing said before it ever is.
PUBLIC_HEARTH = "upgrade-20261115-public-hearth"
_LOCAL_PATH = re.compile(r"(?:/Users|/private|/var|/tmp|/home|/opt|/Volumes)/[^\s\"',;)\]]*")
_ADDRESS = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_RECEIPT = re.compile(r"\s*(?:house-[a-z0-9-]+-v[0-9]+\b|[{\[])")


def voiced(actor: object, value: object) -> bool:
    """A resident's own remark: not the coordinator's or the Steward's operator notes, not a machine receipt."""
    return (isinstance(actor, str) and actor.startswith("resident-") and isinstance(value, str)
            and bool(value.strip()) and _RECEIPT.match(value) is None)


def spoken(value: object, limit: int = 600) -> str:
    """What a resident said at the hearth, without local paths or addresses."""
    text = _ADDRESS.sub("[address]", _LOCAL_PATH.sub("[path]", " ".join(str(value).split())))
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def usage(value: object) -> dict:
    """Never publish arbitrary provider responses, credentials or log text."""
    if not isinstance(value, dict):
        return {}
    allowed = {"input_tokens", "output_tokens", "total_tokens", "cached_tokens", "cached_input_tokens",
               "requests", "remaining", "limit", "used"}
    return {k: v for k, v in value.items() if k in allowed and
            type(v) in (int, float) and math.isfinite(v) and v >= 0}


def _stage_views(stages: list[dict]) -> list[dict]:
    """Sanitize ordered milestone stage descriptors."""
    return [{"milestone": label(stage["milestone"], 20000),
             "seconds": stage["seconds"]} for stage in stages]


def _project_view(key: str, shelf: dict, project: dict) -> dict:
    """Format one public project record, keeping legacy shapes intact."""
    item = {"id": key, "title": label(shelf["ideas"][project["idea"]]["title"], 2000),
            **{k: label(project[k], 2000) if isinstance(project[k], str) else project[k]
               for k in ("idea", "owner", "status", "slot", "stage", "milestone", "deadline", "extended", "lesson")
               if k in project}}
    if "milestones" in project:
        item["milestones"] = _stage_views(project["milestones"])
    if "completed" in project:
        item["completed"] = [{
            k: label(v, 20000 if k == "milestone" else 2000) if isinstance(v, str) else v
            for k, v in entry.items()} for entry in project["completed"]]
    return item


def _brief_view(brief: dict) -> dict:
    from . import shelf as shelf_model
    item = {k: label(brief[k], 2000) for k in (
        *shelf_model.BRIEF_FIELDS, *shelf_model.WORTH_FIELDS, "field", "worth", "author") if k in brief}
    if "asked" in brief:
        item["asked"] = [{k: label(entry[k], 600) for k in ("who", "where", "said")} for entry in brief["asked"]]
    return item


def _closure(state: dict, key: str, proposal: dict, closed: str) -> dict:
    """Say plainly what became of a pending proposal that can no longer proceed."""
    since = proposal.get("proposed_at", 0)
    files = set(proposal.get("renovation", {}).get("files", {}))
    for name, rule in state.get("council", {}).get("rules", {}).items():
        if (files and files <= set(rule.get("renovation", {}).get("files", {}))
                and rule["status"] in {"approved", "installed"} and rule["enacted_at"] > since):
            return {"how": "delivered", "by": name}
    stem, number = re.fullmatch(r"(.*?)(?:-(\d+))?", key).groups()
    later = [name for name in state["proposals"] if (match := re.fullmatch(re.escape(stem) + r"-(\d+)", name))
             and int(match.group(1)) > int(number or 0)]
    if later:
        return {"how": "replaced", "by": max(later, key=lambda name: int(name.rsplit("-", 1)[1]))}
    return {"how": "overtaken", "by": closed} if closed else {"how": "lapsed", "by": None}


def _candidate_view(shelf: dict, choice: dict, idea: str, person) -> dict:
    """Format one frozen-shelf alternative, flattening multi-stage plans."""
    plan = choice["milestones"][idea]
    raw_stages = plan.get("milestones")
    if isinstance(raw_stages, list) and raw_stages:
        stages = _stage_views(raw_stages)
        milestone = stages[0]["milestone"]
        seconds = sum(stage["seconds"] for stage in stages)
    else:
        stages = None
        milestone = label(plan["milestone"], 20000)
        seconds = plan["seconds"]
    item = {"id": idea, "title": label(shelf["ideas"][idea]["title"], 200),
            "author": person(shelf["ideas"][idea]["author"]),
            "milestone": milestone, "seconds": seconds}
    if stages is not None:
        item["stages"] = stages
    return item


def shelf_view(state: dict) -> dict:
    """Public real work only; never publish Explorer tokens or isolated trials."""
    from . import shelf as shelf_model, shelf_gate
    shelf = state.get("shelf", {})
    asked = shelf_model.asked_since(state) is not None
    ideas = []
    for key, idea in shelf.get("ideas", {}).items():
        history = []
        for entry in idea["history"]:
            public = {k: label(v, 2000) if isinstance(v, str) else v
                      for k, v in entry.items()}
            if "choice" in entry:
                choice = shelf["choices"][entry["choice"]]
                public["reasons"] = [label(v["reason"], 2000) for v in choice["votes"].values()
                                     if v["counted"]]
            history.append(public)
        due = shelf_model.brief_due(state, idea)
        ideas.append({"id": key, **{k: label(idea[k], 2000) for k in
            ("title", "what", "why", "first_step", "author", "status")},
            **({"scale": label(idea["scale"], 20)} if "scale" in idea else {}),
            **({"brief": _brief_view(idea["brief"])} if "brief" in idea else {}),
            **({"brief_due": due} if due is not None else {}),
            **({"second": {"author": label(idea["second"]["author"], 200),
                           "finding": label(idea["second"]["finding"], 2000), "at": idea["second"]["at"]}}
               if asked and "second" in idea and idea["second"]["brief"] == idea.get("brief", {}).get("sequence") else {}),
            **({"grounded": shelf_model.grounded(state, idea)} if asked and idea["status"] == "shelved" else {}),
            "sources": list(idea["sources"]), "losses": idea["losses"], "history": history})
    projects = []
    for key, project in shelf.get("projects", {}).items():
        item = _project_view(key, shelf, project)
        if asked:
            if "brief" in project:
                item["brief"] = _brief_view(project["brief"])
            if shelf_model.checked_since(state) is not None:
                # Whether a second resident has opened the quoted pages, and every brief one of them rejected.
                if shelf_model.project_kept(project):
                    item["second"] = {"author": label(project["second"]["author"], 200),
                                      "finding": label(project["second"]["finding"], 2000),
                                      "at": project["second"]["at"]}
                elif "brief" in project and project["status"] == "active":
                    item["brief_unchecked"] = True
                if project.get("rejected"):
                    item["rejected"] = [{"author": label(entry["author"], 200), "by": label(entry["by"], 200),
                                         "finding": label(entry["finding"], 2000), "at": entry["at"]}
                                        for entry in project["rejected"][-5:]]
            brief_due = shelf_model.project_due(state, project)
            if brief_due is not None:
                item["brief_due"] = brief_due
        projects.append(item)
    expedition = shelf.get("rounds", {}).get(shelf.get("explorer"))
    policy = shelf_gate.policy(state)
    view = {"enabled": shelf_gate.enabled(state), "policy": policy,
            "ideas": ideas, "projects": projects, "explorer": {
                "resident": expedition["owner"], "agent": expedition["agent"],
                "until": expedition["until"]} if expedition else None}
    if policy == shelf_gate.GREAT_POLICY_ID:
        view["great_wanted"] = shelf_model.great_wanted(shelf_model.empty() | shelf)
    if shelf.get("needs"):
        titles = {key: idea["title"] for key, idea in shelf.get("ideas", {}).items()}
        titles |= {key: titles.get(project["idea"], key) for key, project in shelf.get("projects", {}).items()}
        needs = [{"id": key, "for_title": label(titles.get(need["for"], need["for"]), 200),
                  **{k: label(need[k], 2000) for k in ("author", "status", "kind", "for", "plain", "ask", "cost",
                                                       "unlocks", "without", "tried", "note") if k in need},
                  "raised_at": need["raised_at"], **({"closed_at": need["closed_at"]} if "closed_at" in need else {})}
                 for key, need in shelf["needs"].items()]
        view["needs"] = [need for need in needs if need["status"] == "open"] + [
            need for need in needs if need["status"] != "open"][-10:]
    if shelf_model.open_since(state) is not None:
        last = shelf.get("research_at")
        view["research"] = {"last": last, "ceiling": shelf_model.SHELF_CEILING, "next": max(
            shelf_model.open_since(state), (last or 0) + shelf_model.RESEARCH_GAP_SECONDS)}
    return view


def voting_view(state: dict, identities: dict, event_times: dict, origins: dict | None = None) -> dict:
    """Allowlisted decisions as known at this frame, never trial votes or raw logs."""
    def person(actor):
        resident = state["residents"].get(actor, {})
        identity = identities.get(actor, {})
        return {"id": actor, "name": label(resident.get("name", actor), 100),
                "agent": label(identity.get("agent", "unrecorded"), 30)}

    shelf = state.get("shelf", {})
    choices = []
    for key, choice in shelf.get("choices", {}).items():
        candidates = [_candidate_view(shelf, choice, idea, person) for idea in choice["candidates"]]
        votes = [{"resident": person(actor), "idea": vote["idea"],
                  "reason": label(vote["reason"], 20000), "counted": vote["counted"],
                  "sequence": vote["sequence"], "at": event_times[vote["sequence"]]}
                 for actor, vote in choice["votes"].items()]
        item = {"id": key, "status": choice["status"], "owner": person(choice["owner"]),
                "opened_sequence": choice["opened_sequence"],
                "closed_sequence": choice.get("closed_sequence"),
                "selection_version": choice.get("selection_version", 1),
                "winner": choice.get("winner"), "candidates": candidates, "votes": votes}
        if "slot" in choice:
            item["slot"] = label(choice["slot"], 20)
        choices.append(item)
    proposals = []
    origins = origins or {}
    for key, proposal in state["proposals"].items():
        notice = proposal.get("notice")
        trial = proposal.get("trial")
        rule = state.get("council", {}).get("rules", {}).get(key, {})
        closed = lapsed(state, key, proposal) if proposal["status"] == "pending" else None
        proposals.append({"id": key, "title": label(proposal.get("title", key), 200),
            "mode": proposal.get("mode", "legacy"), "author": person(proposal.get("author", origins.get(key, {}).get("actor", "unrecorded"))),
            "status": proposal["status"], "rule_status": rule.get("status"),
            "stale": closed is not None,
            **({"closure": _closure(state, key, proposal, closed)} if closed is not None else {}),
            "reason": label(proposal.get("reason", ""), 20000),
            "text": proposal["text"][:100000],
            "proposed_at": proposal.get("proposed_at", origins.get(key, {}).get("at")),
            "ratification": proposal.get("ratification", {}).get("method"),
            "endorsements": [{"resident": person(actor), "reason": label(v["evidence"], 20000),
                              "at": v["at"]} for actor, v in proposal.get("endorsements", {}).items()],
            "trial": {"task": trial["task"], "at": trial["at"],
                      "evidence": label(trial["evidence"], 20000)} if trial else None,
            "notice": {"at": notice["at"], "until": notice["at"] + veto_window(state, proposal),
                       "url": "https://github.com/Someblueman/emberhall/issues/1#issuecomment-"
                              + str(notice["comment_id"])} if notice else None})
    return {"choices": choices, "proposals": proposals}


def watch_item(event: dict) -> dict | None:
    if event["op"] != "say" or event["actor"] != "watch-keeper":
        return None
    text = event["data"].get("text", "")
    if not text.startswith(WATCH_PREFIX):
        return None
    try:
        item = json.loads(text[len(WATCH_PREFIX):])
    except (ValueError, TypeError):
        return None
    return item if isinstance(item, dict) and isinstance(item.get("kind"), str) else None



def room_view(room_id: str, name: str, state: dict, uses: dict) -> dict:
    """Only recorded building facts; dust is a labelled view-time inference."""
    public = {"id": room_id, "name": name}
    room = state.get("life", {}).get("rooms", {}).get(room_id, {})
    if "status" not in room:
        return public
    for key in ("status", "purpose", "reason", "builder", "task", "last_used_by"):
        value = room.get(key)
        public[key] = None if value is None else label(value, 500 if key in {"purpose", "reason"} else 100)
    for key in ("generation", "floor", "planned_at", "opened_at", "closed_at",
                "last_used_at", "observed_since", "legacy"):
        public[key] = room.get(key)
    use = uses.get(room_id)
    if use and use["at"] > (public["last_used_at"] or 0):
        public.update(last_used_at=use["at"], last_used_by=use["actor"])
    public["history"] = [{key: (label(value, 500) if isinstance(value, str) else value)
        for key, value in item.items() if key in {"kind", "actor", "at", "sequence", "generation",
                                                "reason", "name", "purpose", "builder", "task"}}
                         for item in room.get("history", [])]
    return public


def floor_views(state: dict) -> list[dict]:
    floors = []
    for floor in state.get("life", {}).get("floors", {}).values():
        public = {key: (label(value, 500) if isinstance(value, str) else value)
                  for key, value in floor.items() if key in {"level", "name", "purpose", "proposal",
                                                            "enacted_at", "enacted_sequence"}}
        public["authorization"] = (state.get("council", {}).get("rules", {}).get(floor["proposal"], {})
                                   .get("status", "unknown") if floor["level"] else "original")
        floors.append(public)
    return floors


def public_task(task_id: str, task: dict) -> dict:
    """Public unfinished task; readiness/project only when recorded, never inferred."""
    item = {"id": task_id, "title": label(task["title"], 160), "owner": task["owner"],
            "status": task["status"], "until": task["until"], "generation": task["generation"]}
    ready = task.get("ready")
    if ready is True or ready is False:
        item["ready"] = ready
    project = task.get("project")
    if isinstance(project, str) and project.strip():
        item["project"] = label(project, 100)
    if task.get("plain"):
        item["plain"] = label(task["plain"], 200)
    return item


WORK_SECONDS, WORK_LIMIT = 86400, 80
CHECKING = re.compile(r"\b(reviews?|independent(ly)?|trial|audit|inspect|check|verify|try)\b", re.I)


def work_view(state: dict, event_times: dict, at: float) -> list[dict]:
    """What was finished in the last day, for a reader who follows the house by its work.

    Each entry says whether it was a check of someone else's work: marked so by
    its author (helper review), or called a review, trial, audit or check.
    """
    found = []
    for key, task in state["tasks"].items():
        when = event_times.get(task.get("finished_at"))
        if task["status"] != "done" or when is None or when < at - WORK_SECONDS:
            continue
        found.append(public_task(key, task) | {
            "at": when, "check": task.get("helper") == "review" or "review_run" in task
            or bool(CHECKING.search(task["title"]))})
    found.sort(key=lambda item: item["at"])
    return found[-WORK_LIMIT:]


def export(record: Record, observed_at: float | None = None) -> dict:
    final, events, head, source_head, commits, observed_at = export_inputs(record, observed_at)
    context = replay_context()
    frames = replay(events, context)
    return projection(final, head, source_head, observed_at, commits, frames, context["scars"])


def export_inputs(record: Record, observed_at: float | None = None) -> tuple:
    final, events, head = record.read()
    observed_at = time.time() if observed_at is None else observed_at
    if not math.isfinite(observed_at) or observed_at < final["at"]:
        raise ValueError("observation must be finite and at or after the latest journal event")
    # Pin source and journal separately. Neither working files nor later commits
    # are presented as part of an earlier event's source history.
    result = subprocess.run(["git", "-C", str(record.root), "rev-parse", "--verify", "--quiet",
                             "HEAD^{commit}"], capture_output=True, check=False)
    if result.returncode not in (0, 1):
        raise ValueError("cannot read source HEAD")
    source_head = result.stdout.decode().strip() or None
    commits = []
    if source_head:
        raw = record.git("log", "--reverse", "--format=%H%x00%ct%x00%s", source_head)
        for row in raw.decode(errors="replace").splitlines():
            fields = row.split("\0", 2)
            if len(fields) == 3:
                commits.append({"id": fields[0], "at": int(fields[1]), "title": label(fields[2])})
    return final, events, head, source_head, commits, observed_at


def replay_context() -> dict:
    """Everything the frame replay carries from one event to the next (plain data only)."""
    return {"state": None, "rooms": dict(ROOMS), "places": {}, "identities": {}, "runs": {},
            "scars": {}, "ambitions": {}, "budgets": {}, "event_times": {}, "inbox_checked_at": None,
            "proposal_origins": {}, "room_uses": {}, "sleeping": set(), "awakened": {},
            "name_history": {}, "hearth": [], "replayed": 0}


def projection(final: dict, head: str, source_head: str | None, observed_at: float, commits: list,
               frames: list, scars: dict) -> dict:
    # Store immutable scar descriptions once; each frame retains the exact set
    # and changing review/repair state. This keeps the public checkpoint compact.
    scar_catalog = {key: {k: v for k, v in scar.items()
                         if k not in {"mended", "reviews", "lesson_status"}}
                    for key, scar in scars.items()}
    return {"version": 1, "name": label(final["name"], 80), "house_id": final["house_id"],
            "journal_head": head, "source_head": source_head, "observed_at": observed_at,
            "timezone": "Europe/London", "commits": commits, "frames": frames, "scars": scar_catalog,
            "limits": "Recorded state, not a live heartbeat. Quota remaining is unknown unless explicitly reported."}


def replay(events: list, context: dict) -> list:
    """Build the public frames for events after context["replayed"], updating context.

    A frame depends only on the events up to it, so a saved context lets a later
    publication replay only the new events.
    """
    state = context["state"]
    rooms, places, identities, runs = context["rooms"], context["places"], context["identities"], context["runs"]
    scars, ambitions, budgets = context["scars"], context["ambitions"], context["budgets"]
    event_times, inbox_checked_at = context["event_times"], context["inbox_checked_at"]
    proposal_origins, room_uses, sleeping = context["proposal_origins"], context["room_uses"], context["sleeping"]
    awakened, name_history = context["awakened"], context["name_history"]
    hearth = context.setdefault("hearth", [])
    frames = []
    start = context["replayed"]
    for seq, event in enumerate(events[start:], start + 1):
        at, actor, op, data = event["at"], event["actor"], event["op"], event["data"]
        for task_id, task in (state["tasks"].items() if state else []):
            if task["status"] == "claimed" and task["until"] <= at:
                key = f'lease:{task_id}:{task["generation"]}'
                scars.setdefault(key, {"id": key, "room": "workshop", "kind": "expired",
                    "title": "A lease ran out", "detail": label(task["title"]), "task": task_id,
                    "resident": task["owner"], "at": task["until"], "sequence": seq,
                    "basis": "Inferred from lease time; process fate unconfirmed", "mended": False})
        event_times[seq] = at
        if op in {"propose", "council-propose"}:
            proposal_origins[data["proposal"]] = {"actor": actor, "at": at}
        if op == "say" and actor == "watch-keeper" and data.get("text", "").startswith("house-inbox-v1 "):
            try:
                checked = json.loads(data["text"][len("house-inbox-v1 "):]).get("checked_through")
                if type(checked) in (int, float) and math.isfinite(checked) and 0 < checked <= at:
                    inbox_checked_at = max(inbox_checked_at or 0, checked)
            except (ValueError, TypeError, AttributeError):
                pass
        former_name = state["residents"].get(actor, {}).get("name") if state else None
        state = apply_event(state, event)
        if op == "rename":
            name_history.setdefault(actor, []).append({"from": label(former_name, 100),
                "to": label(state["residents"][actor]["name"], 100), "sequence": seq, "at": at})
        if state.get("maintenance", {}).get("room_growth"):
            rooms.update({key: label(room["name"], 60) for key, room in state["life"]["rooms"].items()})
        if op == "owner-provider-release":
            accepted = state["life"]["budgets"][data["agent"]]
            budgets[data["agent"]] = {"agent": data["agent"], "until": accepted["until"],
                "reason": "Owner authorized one early attempt; original cooldown retained.",
                "usage": {}, "sequence": seq}
        if op == "owner-migrate":
            restored = state.get("maintenance", {}).get("provider_restored", {}).get("opencode", {})
            if restored.get("sequence") == seq:
                budgets.pop("opencode", None)
        if op in {"arrive", "wake"}:
            awakened[actor] = seq
            sleeping.discard(actor)
            places[actor] = "door"
        elif op == "sleep":
            sleeping.add(actor)
            rooms.setdefault("bedroom", "Quiet loft")
            places[actor] = "bedroom"
        elif op in {"claim", "renew", "finish", "release", "task"}:
            places[actor] = "workshop"
        elif op in {"learn", "review", "supersede"}:
            places[actor] = "archive"
        elif op in {"propose", "ratify"} or op.startswith("council-"):
            places[actor] = "council"
        elif op == "say" and actor != "watch-keeper":
            places[actor] = "hearth"
            if (PUBLIC_HEARTH in state.get("maintenance", {}).get("migrations", {})
                    and voiced(actor, data.get("text"))):
                hearth.append({"resident": actor, "name": label(state["residents"].get(actor, {}).get("name", actor), 100),
                               "text": spoken(data.get("text", "")), "seq": seq, "at": at})
                del hearth[:-HEARTH_VOICES]

        # These existing figure movements are also actual recorded room use.
        # Keep this view-derived observation out of the replayed protocol state.
        mapped = op in {"arrive", "wake", "sleep", "claim", "renew", "finish", "release", "task",
                        "learn", "review", "supersede", "propose", "ratify", "say"} or op.startswith("council-")
        if mapped and actor != "watch-keeper" and state.get("maintenance", {}).get("room_growth"):
            room_id = places.get(actor)
            if state["life"]["rooms"].get(room_id, {}).get("status") == "open":
                room_uses[room_id] = {"at": at, "actor": actor}

        item = watch_item(event)
        life = op == "life"
        if life:
            item = data
            for room_id, room in state["life"]["rooms"].items():
                rooms.setdefault(room_id, label(room["name"], 60))
        if item:
            kind = item.get("kind")
            run_id = str(item.get("run", ""))
            if kind == "identity" and life:
                identities[actor] = {"agent": label(item.get("agent", "unrecorded"), 30),
                                     "model": label(item.get("model", ""), 100)}
            elif kind == "room" and life:
                rooms[str(item["room"])] = label(item["name"], 60)
            elif kind == "activity" and life:
                places[actor] = str(item["room"])
            elif kind == "ambition" and life:
                key = str(item["ambition"])
                ambitions[key] = {"id": key, **{k: label(item.get(k, ""), 350)
                    for k in ("title", "description", "status", "next_step")}, "sequence": seq}
            elif kind == "budget" and life:
                agent = str(item["agent"])
                accepted = state["life"]["budgets"][agent]
                budgets[agent] = {"agent": agent, "until": accepted["until"],
                    "reason": label(accepted["reason"]), "usage": {},
                    "sequence": accepted["sequence"]}
            elif kind in {"start", "run-start"}:
                if life and item.get("agent") == "opencode":
                    permits = state.get("maintenance", {}).get("releases", {}).values()
                    if any(permit.get("consumed_run") == run_id for permit in permits) and "opencode" in budgets:
                        budgets["opencode"]["reason"] = "Owner's single early attempt used; original cooldown retained."
                        budgets["opencode"]["sequence"] = seq
                resident = str(item.get("resident", ""))
                agent = item.get("agent", "codex" if item.get("executable") == "codex" else "unrecorded")
                runs[run_id] = {"id": run_id, "resident": resident, "agent": label(agent, 30),
                    "model": label(item.get("model", ""), 100), "start": at, "sequence": seq,
                    "status": "started", "outcome": "unconfirmed", "usage": {}, "elapsed_seconds": None,
                    "finished_tasks": []}
                if resident:
                    identities[resident] = {"agent": label(agent, 30), "model": label(item.get("model", ""), 100)}
            elif run_id in runs:
                run = runs[run_id]
                if kind in {"launched", "run-launched"}:
                    run["status"] = "launched"
                elif kind in {"finish", "run-finish", "recovered-interruption", "execution-result"}:
                    outcome = item.get("outcome", "unconfirmed")
                    if kind == "recovered-interruption":
                        outcome = "unconfirmed"
                    run.update(outcome=label(outcome, 40), last_sequence=seq, end=at,
                               status="result-saved" if kind == "execution-result" else "ended",
                               usage=usage(item.get("usage")),
                               elapsed_seconds=item.get("elapsed_seconds"))
                    if outcome in {"failed", "interrupted", "unconfirmed"}:
                        key = "run:" + run_id
                        held = [k for k, t in state["tasks"].items()
                                if t["owner"] == run["resident"] and t["status"] == "claimed"]
                        if life:
                            held += state["life"]["runs"][run_id].get("released_tasks", [])
                        scars.setdefault(key, {"id": key, "room": places.get(run["resident"], "door"),
                            "kind": "interrupted" if outcome == "interrupted" else "unconfirmed" if outcome == "unconfirmed" else "failure",
                            "title": "Interrupted mid-task" if outcome == "interrupted" and held else "Run " + outcome,
                            "detail": ", ".join(held) if held else "No unfinished claim at this receipt",
                            "resident": run["resident"], "at": at, "sequence": seq,
                            "basis": "Supervisor receipt", "mended": False})

        public_observation(event, runs)
        if op == "finish":
            active_run = next((r for r in reversed(list(runs.values()))
                               if r["resident"] == actor and r["status"] == "launched"), None)
            if active_run is not None:
                active_run["finished_tasks"].append({"task": label(data["task"], 100), "sequence": seq})

        for key, lesson in state["lessons"].items():
            if lesson["status"] == "observed" and lesson["reviews"] and re.search(
                    r"repair|repaired|fix|regression", lesson["evidence"], re.I):
                scar_id = "repair:" + key
                scars.setdefault(scar_id, {"id": scar_id, "room": "archive", "kind": "repair",
                    "title": label(lesson["key"].replace("-", " "), 90),
                    "detail": label(lesson["claim"], 300), "sequence": seq, "at": at,
                    "basis": "Reviewed lesson; shown in archive because location was not recorded",
                    "mended": True, "lesson": key})
            scar = scars.get("repair:" + key)
            if scar:
                scar["lesson_status"] = lesson["status"]
                scar["reviews"] = len(lesson["reviews"])
        for scar in scars.values():
            if scar.get("task"):
                task = state["tasks"][scar["task"]]
                scar["mended"] = task["status"] == "done" or task["generation"] > int(scar["id"].rsplit(":", 1)[1])

        public_residents = []
        for resident_id, resident in state["residents"].items():
            if resident_id == "watch-keeper":  # An actual supervisor, not a model mind.
                continue
            identity = identities.get(resident_id, {"agent": "unrecorded", "model": ""})
            claims = [k for k, t in state["tasks"].items()
                      if t["owner"] == resident_id and t["status"] == "claimed"]
            latest_run = next((r for r in reversed(list(runs.values())) if r["resident"] == resident_id), None)
            is_asleep = resident_id in sleeping
            room = "bedroom" if is_asleep else places.get(resident_id, "door")
            pose = "sleeping" if is_asleep else "sitting" if room == "hearth" else "standing"
            presence = "asleep" if is_asleep else "recorded awake"
            if (latest_run and latest_run["status"] == "ended" and not is_asleep
                    and latest_run["last_sequence"] > awakened.get(resident_id, 0)):
                presence = latest_run["outcome"] + "; no sleep event"
                pose = "unconfirmed"
            public_residents.append({"id": resident_id, "name": label(resident["name"], 60),
                **identity, "room": room, "pose": pose, "presence": presence,
                "tasks": claims, **({"name_history": copy.deepcopy(name_history[resident_id])}
                                     if resident_id in name_history else {})})
        tasks = [public_task(key, t)
                 for key, t in state["tasks"].items() if t["status"] != "done"]
        title = label(data.get("plain" if op == "task" and data.get("plain") else "title",
                               data.get("task", data.get("lesson", ""))), 140)
        council = state.get("council", {})
        proposals = council.get("proposals", {})
        frame = {"seq": seq, "at": at, "event": {"op": op, "actor": actor, "title": title},
            "rooms": [room_view(k, v, state, room_uses) for k, v in rooms.items()],
            "floors": floor_views(state), "residents": public_residents,
            "tasks": tasks, "scars": list(scars.values()), "ambitions": list(ambitions.values()),
            "budgets": list(budgets.values()), "runs": list(runs.values()),
            "lessons": len(state["lessons"]),
            # The latest things residents said at the hearth (the coordinator's own notes are left out).
            "hearth": list(hearth),
            # The Archive's shelves: each lesson's claim, never its evidence text.
            "archive": [{"key": label(lesson["key"], 100), "claim": label(lesson["claim"], 900),
                         "author": label(state["residents"].get(lesson["author"], {}).get("name", lesson["author"]), 100),
                         "status": label(lesson["status"], 20), "reviews": len(lesson["reviews"])}
                        for lesson in state["lessons"].values()],
            "council": {"pending": sum(p["status"] == "pending" for p in state["proposals"].values()) +
                                     sum(p.get("status") == "pending" for p in proposals.values()),
                        "enacted": sum(p["status"] in {"ratified", "enacted"} for p in state["proposals"].values()) +
                                   sum(p.get("status") == "enacted" for p in proposals.values())}}
        # Preserve historical frames exactly before this owner activation (or
        # before the first real shelf event in an unpinned disposable house).
        from .windows import enabled as windows_enabled
        if windows_enabled(state) or "shelf" in state:
            frame["shelf"] = shelf_view(state)
        from .shelf import SECOND_LOOK
        if SECOND_LOOK in state.get("maintenance", {}).get("migrations", {}):
            frame["work"] = work_view(state, event_times, at)
        frame["voting"] = voting_view(state, identities, event_times, proposal_origins)
        frame["voting"]["inbox_checked_at"] = inbox_checked_at
        frame = copy.deepcopy(frame)
        frame["scars"] = [{k: v for k, v in scar.items()
                           if k in {"id", "mended", "reviews", "lesson_status"}}
                          for scar in frame["scars"]]
        frames.append(frame)
    context.update(state=state, inbox_checked_at=inbox_checked_at, replayed=start + len(frames))
    return frames


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("site/history.json"))
    parser.add_argument("--at", type=float)
    args = parser.parse_args()
    try:
        data = export(Record(args.repo), args.at)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, ensure_ascii=True, separators=(",", ":")) + "\n")
    except (ValueError, OSError, OverflowError) as error:
        parser.exit(2, f"house body: {error}\n")
    print(f'Wrote {len(data["frames"])} moments to {args.output}; head {data["journal_head"]}')


if __name__ == "__main__":
    main()
