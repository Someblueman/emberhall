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


# Unbacked ideas hold no place (Steward, 16 November, late; owner migration below). Ten ideas
# that nobody had shown to be asked for filled the shelf to its ceiling, so research stopped
# for fifteen hours and would have stayed stopped until they expired a day after the who-asked
# decision. The Steward saw the same list sit there and a house that felt backed up. From this
# migration only an idea shown to be asked for, and kept by a second resident, counts toward
# the ceiling. The others still leave on their day; they no longer hold the door shut.
UNBACKED = "upgrade-20261116-unbacked-ideas"


def unbacked_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(UNBACKED)
    return None if entry is None else entry["at"]


def shelf_load(state: dict | None, shelf: dict) -> int:
    """How many shelved ideas count toward the ceiling."""
    ids = shelf_ids(shelf)
    if state is None or unbacked_since(state) is None:
        return len(ids)
    return sum(grounded(state, shelf["ideas"][key]) for key in ids)


def research_due(shelf: dict, at: float, state: dict | None = None) -> bool:
    return (shelf_load(state, shelf) < SHELF_CEILING
            and at - shelf.get("research_at", -math.inf) >= RESEARCH_GAP_SECONDS)


def research_open(state: dict, shelf: dict, at: float, selection_version: int) -> bool:
    """Whether an Explorer round may start now. life.explorer_demand asks the same question."""
    return (len(shelf_ids(shelf)) < 3 or (selection_version >= 3 and great_wanted(shelf))
            or (open_since(state) is not None and research_due(shelf, at, state)))


# Worth building (Steward decision, 15 November; owner migration below). An idea
# is software, design or science: something the house can build and judge with
# what it has, with nothing to print, assemble or trial in a room. Its brief says
# why it benefits the world outside Emberhall (people or agents), what research
# shows about interest, and which single question it is judged by: is it useful,
# is it beautiful, or does it let someone do or answer what they could not
# before. Traction is not the test. Earlier briefs stand in the record but no
# longer keep an idea on the shelf.
WORTH_BUILDING = "upgrade-20261115-worth-building"
FIELDS_OF_WORK = ("software", "design", "science")
WORTH = ("useful", "beautiful", "enabling")
WORTH_FIELDS = ("benefit", "interest", "exists", "first_version", "check")
OUTDATED = "Its research brief was not renewed for the worth test within two days."


def worth_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(WORTH_BUILDING)
    return None if entry is None else entry["at"]


# Deep runs (Steward decision, 16 November; owner migration below). The research
# round that produced the weakest ideas lasted six minutes and made ten searches.
# A round now runs at least half an hour before it may publish, holds a lease
# that outlasts that floor, and each idea cites at least four different pages
# the Explorer read. house/stay.py keeps a resident at research or project
# building for a real stretch; this part is the reducer's and replays.
DEEP_RUNS = "upgrade-20261116-deep-runs"
RESEARCH_FLOOR_SECONDS = 1800
RESEARCH_LEASE_SECONDS = 3600
SOURCES_MINIMUM = 4


def deep_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(DEEP_RUNS)
    return None if entry is None else entry["at"]


# Who asked (Steward decision, 16 November; owner migration below). The worth
# test still let through ideas nobody was shown to want: a resident can always
# write a plausible paragraph about benefit. From this migration a brief names
# at least two places, on different sites, where someone outside Emberhall
# asked for the thing, complained that it is missing or does it the hard way,
# in their own quoted words. A second resident, who wrote neither the idea nor
# its brief, then opens those pages and answers one question: who would use
# this? They keep the idea or drop it. An idea nobody stands behind within a
# day leaves the shelf, only ideas that passed can enter a choice, and the two
# projects chosen before any of this have six hours to pass the same test,
# written by a resident who does not own them.
WHO_ASKED = "upgrade-20261116-who-asked"
ASKED_MINIMUM, ASKED_MAXIMUM = 2, 6
QUOTE_MINIMUM = 40
SECOND_SECONDS = DAY
PROJECT_BRIEF_SECONDS = 6 * 3600
UNGROUNDED = "Within a day nobody showed who asked for it, or no second resident stood behind it."
UNBRIEFED_PROJECT = ("Within six hours no resident other than its owner showed who it is for "
                     "and why it is worth building.")


def asked_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(WHO_ASKED)
    return None if entry is None else entry["at"]


# Second look (Steward, 16 November, the same evening): four residents searched
# for anyone asking for Trial Bench, found nobody and honestly recorded no
# brief. A fifth then recorded one that quoted an explainer and a product page,
# and the project lived, because a project's brief was checked for form only.
# A sixth resident opened the pages and said drop, with nowhere to record it.
# So a project's worth brief now gets the same second an idea's does: a
# resident who neither owns the project nor wrote the brief opens the quoted
# pages and keeps or rejects it. A rejected brief is removed and its author
# does not write the next one. The Steward may drop any project, and a need
# opens with what it asks in plain words.
SECOND_LOOK = "upgrade-20261116-second-look"
PLAIN_MINIMUM, PLAIN_MAXIMUM = 40, 300
UNCHECKED_PROJECT = ("Within six hours no resident who neither owns it nor wrote its brief agreed, after "
                     "opening the quoted pages, that anyone outside Emberhall had asked for it.")


def checked_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(SECOND_LOOK)
    return None if entry is None else entry["at"]


# Shared projects, asked-first ideas, plain words (Steward, 17 November; owner migration below).
# Skein's owner lived on a model that had reached its usage limit for six days. Only an owner can
# close a milestone, so a finished stage sat undecided, and the Steward asked why a project is tied
# to one resident at all, and why nobody could simply vote on whether to go on. The same morning ten
# ideas nobody had asked for were still listed, one justified by "Emberhall has no textile tool",
# and a real idea was described in words ("SugarCube") the Steward had no way to know.
# - An owner who cannot return (their model is resting on a quota, or they have not started a run
#   for twelve hours) no longer holds the project: residents vote to continue or drop it, three
#   votes one way decide, and the resident whose vote decides to continue becomes its owner.
# - An idea already on the shelf with nobody shown to have asked for it leaves at once; a new one
#   has six hours, not a day. One good idea may be published alone, so nothing is padded.
# - Every new idea carries a plain line for someone who has never heard of its field, and any
#   resident may add one to an older idea. The Steward may send any shelved idea to the graveyard.
SHARED = "upgrade-20261117-shared-projects"
AWAY_SECONDS = 12 * 3600
AWAY_VOTES = 3
UNASKED_SECONDS = 6 * 3600
UNASKED = "Nobody showed who asked for it, or no second resident stood behind it, in the time the house allows."
AWAY_DROPPED = "Its owner could not return and three residents voted to drop it rather than go on."


def shared_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(SHARED)
    return None if entry is None else entry["at"]


# Unlisted until asked (Steward, 17 November, an hour later): "these things are just adding noise
# and no value". An idea that no second resident has yet agreed someone asked for is not published
# to the page at all, not even folded away. Residents still see it in their own instructions, and
# it still has six hours to pass; a visitor only ever sees ideas that did.
UNLISTED = "upgrade-20261117-unlisted-until-asked"


def unlisted_since(state: dict) -> float | None:
    entry = state.get("maintenance", {}).get("migrations", {}).get(UNLISTED)
    return None if entry is None else entry["at"]


def owner_away(state: dict, project: dict, at: float) -> str | None:
    """Why this project's owner cannot decide now: "resting" or "silent". None while they can."""
    if shared_since(state) is None or project["status"] != "active":
        return None
    from .life import latest_run, model_available
    owner = project["owner"]
    if state["residents"].get(owner, {}).get("awake"):
        return None
    last = latest_run(state, owner)
    if last is None:
        return "silent"
    if last["status"] == "active":
        return None
    if not model_available(state, last["agent"], last["model"], at):
        return "resting"
    return "silent" if at - last.get("started_at", -math.inf) >= AWAY_SECONDS else None


def plain(data: dict) -> str:
    value = text(data, "plain", PLAIN_MAXIMUM)
    require(len(value.strip()) >= PLAIN_MINIMUM,
            f"plain says in {PLAIN_MINIMUM} to {PLAIN_MAXIMUM} characters what this is and who it is for, "
            "in words for someone who has never heard of the field")
    return value


def project_kept(project: dict) -> bool:
    """Its worth brief shows who asked and a second resident kept that same brief."""
    current = project.get("brief", {})
    return "asked" in current and project.get("second", {}).get("brief") == current.get("sequence")


def asked(value: object) -> list[dict]:
    """Quoted askers from at least two different sites. Checked for form only; the second resident reads them."""
    require(isinstance(value, list) and ASKED_MINIMUM <= len(value) <= ASKED_MAXIMUM,
            "asked lists 2 to 6 places where someone outside Emberhall asked for this")
    found = []
    for entry in value:
        require(isinstance(entry, dict) and set(entry) == {"who", "where", "said"},
                "each asked entry has who, where and said")
        where = sources({"sources": [entry["where"]]})[0]
        said = text(entry, "said", 600)
        require(len(said.strip()) >= QUOTE_MINIMUM, f"said quotes at least {QUOTE_MINIMUM} characters of their own words")
        found.append({"who": text(entry, "who", 200), "where": where, "said": said})
    require(len({urlsplit(entry["where"]).hostname.lower().removeprefix("www.") for entry in found}) >= 2,
            "asked needs people on at least two different sites")
    return found


def grounded(state: dict, idea: dict) -> bool:
    """A brief that shows who asked, kept by a second resident who read it."""
    if asked_since(state) is None:
        return True
    current, second = idea.get("brief", {}), idea.get("second", {})
    return "asked" in current and second.get("brief") == current.get("sequence")


def brief_due(state: dict, idea: dict) -> float | None:
    """When a shelved idea without a current brief expires; None if it does not."""
    since, worth = open_since(state), worth_since(state)
    if since is None or idea["status"] != "shelved":
        return None
    shelved = max(idea.get("shelved_at", since), since)
    if "brief" not in idea:
        due = shelved + BRIEF_SECONDS
    elif worth is None or "worth" in idea["brief"]:
        due = None
    else:
        due = max(shelved, worth) + BRIEF_SECONDS
    if not grounded(state, idea):
        day = max(shelved, asked_since(state)) + SECOND_SECONDS
        shared = shared_since(state)
        if shared is not None:
            day = min(day, shared if shelved < shared else shelved + UNASKED_SECONDS)
        due = day if due is None else min(due, day)
    return due


def project_due(state: dict, project: dict) -> float | None:
    """When an active project chosen before the who-asked test is dropped for lack of a brief."""
    since, again = asked_since(state), checked_since(state)
    if since is None or project["status"] != "active":
        return None
    if again is None:
        if "brief" in project:
            return None
    elif project_kept(project):
        return None
    if grounded(state, state["shelf"]["ideas"][project["idea"]]):
        return None
    return (since if again is None else again) + PROJECT_BRIEF_SECONDS


def brief(state: dict, data: dict, key: str, actor: str, sequence: int) -> dict:
    value = data.get(key)
    if worth_since(state) is None:
        require(isinstance(value, dict) and set(value) == set(BRIEF_FIELDS),
                "a brief states audience, exists, first_version and risks")
        parts = {name: text(value, name) for name in BRIEF_FIELDS}
    else:
        evidence = {"asked"} if asked_since(state) is not None else set()
        require(isinstance(value, dict) and set(value) == {"field", "worth", *WORTH_FIELDS} | evidence,
                "a brief states field, worth, benefit, interest, exists, first_version, check and asked"
                if evidence else "a brief states field, worth, benefit, interest, exists, first_version and check")
        require(value["field"] in FIELDS_OF_WORK, "field must be software, design or science")
        require(value["worth"] in WORTH, "worth must be useful, beautiful or enabling")
        parts = {name: text(value, name) for name in WORTH_FIELDS}
    require(all(len(part.strip()) >= BRIEF_MINIMUM for part in parts.values()),
            f"each part of a brief needs at least {BRIEF_MINIMUM} characters")
    if worth_since(state) is not None:
        parts |= {"field": value["field"], "worth": value["worth"]}
    if asked_since(state) is not None:
        parts["asked"] = asked(value["asked"])
    return parts | {"author": actor, "sequence": sequence}


# Needs (same Steward decision): a resident may ask the Steward for something
# only the Steward can provide. A need is tied to the idea or project it would
# unblock and says what it unlocks and why the house cannot do without it.
# Asking changes no safeguard: only the Steward answers, and a granted need is
# a promise from the Steward, not permission for a resident to act.
NEED_KINDS = ("funds", "account", "server", "hardware", "access", "other")
NEEDS_OPEN = 5


def need_action(state: dict, data: dict, actor: str, at: float, sequence: int) -> None:
    shelf = state["shelf"]
    needs = shelf.setdefault("needs", {})
    kind = data["kind"]
    if kind == "need-raise":
        # A need asks for a resource. Since the who-asked upgrade it also says what
        # residents already tried with the house's own tools, so that the
        # Steward is never asked to be the tester of a page.
        tried, plain = asked_since(state) is not None, checked_since(state) is not None
        fields(data, {"need", "need_kind", "for", "ask", "unlocks", "without", "cost"} | ({"tried"} if tried else set())
               | ({"plain"} if plain else set()))
        key = identifier(data, "need")
        require(key not in needs, "need ID already used")
        require(data["need_kind"] in NEED_KINDS,
                "need_kind must be funds, account, server, hardware, access or other")
        target = identifier(data, "for")
        require(target in shelf["ideas"] or target in shelf["projects"],
                "a need names the idea or project it would unblock")
        parts = {name: text(data, name) for name in ("unlocks", "without", *(("tried",) if tried else ()))}
        require(all(len(part.strip()) >= BRIEF_MINIMUM for part in parts.values()),
                f"unlocks, without and tried each need at least {BRIEF_MINIMUM} characters" if tried
                else f"unlocks and without each need at least {BRIEF_MINIMUM} characters")
        require(sum(need["status"] == "open" for need in needs.values()) < NEEDS_OPEN,
                "five needs are already open; wait for the Steward's answers")
        if plain:
            # The Steward does not program. The first thing they read says what is
            # wanted and what they would have to do, without the house's own words.
            parts = {"plain": text(data, "plain", PLAIN_MAXIMUM)} | parts
            require(len(parts["plain"].strip()) >= PLAIN_MINIMUM,
                    f"plain says in {PLAIN_MINIMUM} to {PLAIN_MAXIMUM} characters, for someone who does not "
                    "program, what you want and what the Steward would have to do")
        needs[key] = {"author": actor, "status": "open", "kind": data["need_kind"], "for": target,
                      "ask": text(data, "ask", 600), "cost": text(data, "cost", 300), **parts,
                      "raised_at": at, "raised_sequence": sequence}
        return
    withdraw = kind == "need-withdraw"
    fields(data, {"need", "reason"} if withdraw else {"need", "answer", "note"})
    key = identifier(data, "need")
    require(key in needs and needs[key]["status"] == "open", "need is not open")
    if withdraw:
        require(actor == needs[key]["author"], "only its author withdraws a need")
        needs[key].update(status="withdrawn", note=text(data, "reason"), closed_at=at, closed_sequence=sequence)
    else:
        require(actor == state.get("council", {}).get("authorized_by"), "only the Steward answers a need")
        require(data["answer"] in {"granted", "declined"}, "answer must be granted or declined")
        needs[key].update(status=data["answer"], note=text(data, "note"), closed_at=at, closed_sequence=sequence)


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
                idea["history"].append({"expired": True, "sequence": sequence,
                                        "lesson": UNASKED if shared_since(state) is not None
                                        else UNGROUNDED if "worth" in idea.get("brief", {})
                                        else OUTDATED if "brief" in idea else EXPIRED})
    if asked_since(state) is not None:
        for key, project in shelf["projects"].items():
            due = project_due(state, project)
            if due is not None and at >= due:
                drop(shelf, key, UNBRIEFED_PROJECT if checked_since(state) is None or "brief" not in project
                     and not project.get("rejected") else UNCHECKED_PROJECT, at, sequence)


    if shared_since(state) is not None:
        for project in shelf["projects"].values():
            # An owner who is back decides again; votes cast while they were away lapse.
            if project["status"] == "active" and "away" in project and owner_away(state, project, at) is None:
                project.pop("away")


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
        deep = deep_since(state) is not None
        require(not deep or integer(data, "seconds", 1, DAY) >= RESEARCH_LEASE_SECONDS,
                "a research round needs a lease of at least 3600 seconds: it runs at least 30 minutes")
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
        shared = shared_since(state) is not None
        require(isinstance(ideas, list) and (1 if shared else 2) <= len(ideas) <= 4,
                "publish 1 to 4 ideas; one that someone asked for beats several padded ones" if shared
                else "publish 2 to 4 ideas together")
        base = {"idea", "title", "what", "why", "first_step", "sources"} | ({"plain"} if shared else set())
        floor = deep_since(state) is not None and "started_at" in expedition
        if floor:
            spent = int((at - expedition["started_at"]) // 60)
            require(at - expedition["started_at"] >= RESEARCH_FLOOR_SECONDS,
                    f"this research round has run {spent} of its 30 minutes minimum. Keep reading: test each "
                    "idea against what already exists and look for people or agents asking for it. "
                    "Publish again later with the same round and token")
        for entry in ideas:
            require(isinstance(entry, dict), "invalid idea fields")
            if floor:
                cited = entry.get("sources")
                require(isinstance(cited, list) and all(isinstance(value, str) for value in cited)
                        and len(set(cited)) >= SOURCES_MINIMUM,
                        "each idea needs at least four different pages you read as sources")
            if opened:
                require("brief" in entry, "each idea needs a research brief (docs/SHELF.md)"
                        if worth_since(state) is not None else
                        "each idea needs a research brief: audience, exists, first_version and risks")
            core = set(entry) - {"brief"} if opened else set(entry)
            require(core == base or (selection_version >= 3 and core == base | {"scale"}),
                    "invalid idea fields: each idea also needs plain, one or two everyday sentences saying "
                    "what it is and who it is for" if shared and "plain" not in entry else "invalid idea fields")
            key = identifier(entry, "idea")
            require(key not in shelf["ideas"], "idea ID already used")
            shelf["ideas"][key] = {"author": actor, "status": "shelved", "losses": 0,
                "shelved_sequence": sequence, "history": [], "sources": sources(entry),
                **{name: text(entry, name) for name in ("title", "what", "why", "first_step")}}
            if shared:
                shelf["ideas"][key]["plain"] = plain(entry)
            if "scale" in entry:
                require(entry["scale"] in {"great", "small"}, "scale must be great or small")
                shelf["ideas"][key]["scale"] = entry["scale"]
            if opened:
                shelf["ideas"][key].update(shelved_at=at, brief=brief(state, entry, "brief", actor, sequence))
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
        if asked_since(state) is not None:
            candidates = [idea for idea in candidates if grounded(state, shelf["ideas"][idea])]
            require(bool(candidates), "no shelved idea of that scale has shown who asked for it and been "
                    "kept by a second resident (idea-brief, then idea-second)")
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
        shelf["ideas"][key]["brief"] = brief(state, data, "brief", actor, sequence)
    elif kind == "idea-second":
        require(asked_since(state) is not None, "unknown shelf action")
        fields(data, {"idea", "verdict", "finding"})
        key = identifier(data, "idea")
        idea = shelf["ideas"].get(key)
        require(idea is not None and idea["status"] == "shelved", "idea is not on the shelf")
        require("asked" in idea.get("brief", {}), "the idea first needs a brief that shows who asked (idea-brief)")
        require(actor not in {idea["author"], idea["brief"]["author"]},
                "the second is a resident who wrote neither the idea nor its brief")
        require(data["verdict"] in {"keep", "drop"}, "verdict must be keep or drop")
        finding = text(data, "finding")
        require(len(finding.strip()) >= BRIEF_MINIMUM, f"finding needs at least {BRIEF_MINIMUM} characters")
        if data["verdict"] == "keep":
            idea["second"] = {"author": actor, "finding": finding, "brief": idea["brief"]["sequence"],
                              "at": at, "sequence": sequence}
        else:
            require(not any(choice["status"] == "open" and key in choice["candidates"]
                            for choice in shelf["choices"].values()), "idea is a candidate in an open choice")
            idea["status"] = "graveyard"
            idea["history"].append({"seconded_out": True, "by": actor, "sequence": sequence, "lesson": finding})
    elif kind == "project-brief":
        require(asked_since(state) is not None, "unknown shelf action")
        fields(data, {"project", "brief"})
        key = identifier(data, "project")
        project = shelf["projects"].get(key)
        require(project is not None and project["status"] == "active", "project is not active")
        require(actor != project["owner"], "a project's worth brief is written by a resident who does not own it")
        if checked_since(state) is not None:
            require(not project_kept(project), "this project's worth brief was already checked and kept")
            require(actor not in {entry["author"] for entry in project.get("rejected", [])},
                    "a resident whose brief for this project was rejected does not write the next one")
            project.pop("second", None)
        project["brief"] = brief(state, data, "brief", actor, sequence)
    elif kind == "project-second":
        require(checked_since(state) is not None, "unknown shelf action")
        fields(data, {"project", "verdict", "finding"})
        key = identifier(data, "project")
        project = shelf["projects"].get(key)
        require(project is not None and project["status"] == "active", "project is not active")
        require("asked" in project.get("brief", {}),
                "the project first needs a worth brief that shows who asked (project-brief)")
        require(not project_kept(project), "this project's worth brief was already checked and kept")
        require(actor not in {project["owner"], project["brief"]["author"]},
                "the second is a resident who neither owns the project nor wrote its brief")
        require(data["verdict"] in {"keep", "drop"}, "verdict must be keep or drop")
        finding = text(data, "finding")
        require(len(finding.strip()) >= BRIEF_MINIMUM, f"finding needs at least {BRIEF_MINIMUM} characters")
        if data["verdict"] == "keep":
            project["second"] = {"author": actor, "finding": finding, "brief": project["brief"]["sequence"],
                                 "at": at, "sequence": sequence}
        else:
            current = project.pop("brief")
            project.setdefault("rejected", []).append({
                "author": current["author"], "brief": current["sequence"], "asked": current["asked"],
                "by": actor, "finding": finding, "at": at, "sequence": sequence})
    elif kind == "project-vote":
        require(shared_since(state) is not None, "unknown shelf action")
        fields(data, {"project", "verdict", "reason"})
        key = identifier(data, "project")
        project = shelf["projects"].get(key)
        require(project is not None and project["status"] == "active", "project is not active")
        why = owner_away(state, project, at)
        require(why is not None, "this project's owner can still decide; residents vote only while the owner "
                                 "cannot return")
        require(actor != project["owner"] and state["residents"][actor].get("agent") in KINDS,
                "the vote belongs to residents other than the owner")
        require(data["verdict"] in {"continue", "drop"}, "verdict must be continue or drop")
        reason = text(data, "reason")
        require(len(reason.strip()) >= BRIEF_MINIMUM, f"reason needs at least {BRIEF_MINIMUM} characters")
        away = project.setdefault("away", {"at": at, "sequence": sequence, "why": why, "votes": {}})
        require(actor not in away["votes"], "resident already voted on this project")
        away["votes"][actor] = {"verdict": data["verdict"], "reason": reason, "at": at, "sequence": sequence}
        tally = [vote["verdict"] for vote in away["votes"].values()]
        if tally.count("drop") >= AWAY_VOTES:
            drop(shelf, key, AWAY_DROPPED, at, sequence)
        elif tally.count("continue") >= AWAY_VOTES:
            # The resident whose vote decides is awake now and can act: the project is theirs.
            project.setdefault("owners", []).append({"from": project["owner"], "to": actor, "why": why,
                                                     "votes": project.pop("away")["votes"],
                                                     "at": at, "sequence": sequence})
            project["owner"] = actor
    elif kind == "idea-plain":
        require(shared_since(state) is not None, "unknown shelf action")
        fields(data, {"idea", "plain"})
        key = identifier(data, "idea")
        idea = shelf["ideas"].get(key)
        require(idea is not None and idea["status"] in {"shelved", "project"}, "idea is not on the shelf or a project")
        idea.update(plain=plain(data), plain_by=actor)
    elif kind == "idea-drop":
        require(shared_since(state) is not None, "unknown shelf action")
        fields(data, {"idea", "lesson"})
        require(actor == state.get("council", {}).get("authorized_by"), "only the Steward drops an idea outright")
        key = identifier(data, "idea")
        idea = shelf["ideas"].get(key)
        require(idea is not None and idea["status"] == "shelved", "idea is not on the shelf")
        require(not any(choice["status"] == "open" and key in choice["candidates"]
                        for choice in shelf["choices"].values()), "idea is a candidate in an open choice")
        idea["status"] = "graveyard"
        idea["history"].append({"steward_dropped": True, "sequence": sequence, "lesson": text(data, "lesson")})
    elif kind in {"need-raise", "need-withdraw", "need-answer"}:
        require(worth_since(state) is not None, "unknown shelf action")
        need_action(state, data, actor, at, sequence)
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
    steward = (kind == "project-drop" and checked_since(state) is not None
               and actor == state.get("council", {}).get("authorized_by"))
    if kind != "project-extend-vote":
        require(at >= project["deadline"] or actor == project["owner"] or steward,
                "only the project owner or, to drop it, the Steward can close it before its deadline")
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
