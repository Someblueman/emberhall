#!/usr/bin/env python3
"""Static Chronicle Room generator for Emberhall verified journal prefixes.

Reads an explicitly exported journal prefix (JSON) and emits a deterministic,
zero-JavaScript static HTML milestone index at site/chronicle/.

Repair notes (chronicle-real-record-repair, chronicle-counted-votes): choice
closures are derived by replaying actual choice-open/choice-vote transitions
under the current work-selection-003 revision. A weigh-in counts exactly as
house/shelf.py records it: a vote is counted unless its actor is the author
of the voted idea; authorship comes from the actor of the explore-publish
event (the reducer records that actor as each idea's author). Three counted
weigh-ins close the round atomically, the winner is the candidate with the
most counted votes (ties broken by shelved sequence, then idea ID as in the
reducer), and the shortlist is rejected when no candidate reaches two of
three counted votes. There is no ``choice-close`` event; trial fixture rounds
marked with ``trial`` are excluded. Enacted rules come from actual transitions
only: ``council-enact``, plus the single direct-owner enactment (owner-migrate
with scope ``work-selection-repair-20261114`` enacting work-selection-003,
mirroring house/maintenance.py). ``council-authorize`` and
``council-wake-authorize`` delegate process authority and are ignored. Only an
explicit public-field allowlist is rendered; raw message fields (summary,
source, reason, text, evidence) are never read or emitted. Project links appear
only on recorded completed projects: source directories via GitHub and, when
a public catalogue supplies a shipped entry page, a direct browser action; closed choices have no project link until completion,
and evidence task IDs are never guessed into evidence directories. Great-work
plans from work-selection-004 pass one stage per project-done; intermediate
passes are milestones, and only the final pass completes the project.

This is the house's copy of projects/emberhall-chronicle-room/chronicle.py. The
publisher runs it on every publication, so it lives with the house code and
changes only by renovation; keep the two in step.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
from typing import Any

GITHUB_BASE = "https://github.com/Someblueman/emberhall/tree/main"
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
# Direct-owner enactments: house/maintenance.py enacts these exact rules on
# owner-migrate events with these scopes; other migrations are runtime work.
OWNER_SELECTION_SCOPE = "work-selection-repair-20261114"
OWNER_SELECTION_RULE_ID = "work-selection-003"
OWNER_SELECTION_TITLE = "Choose worthwhile work, or reject the shortlist"
OWNER_MIGRATION_RULES = {
    OWNER_SELECTION_SCOPE: (OWNER_SELECTION_RULE_ID, OWNER_SELECTION_TITLE),
    "course-correction-20261115": (
        "work-selection-004",
        "Choose worthwhile work: one great work and one small project",
    ),
}


def _is_verified_event(event: Any) -> bool:
    """Shape-check one exported event; explicitly unverified events are excluded.

    Shape validation only. Input provenance (that the export is a genuinely
    verified prefix) remains the caller's responsibility; this function does
    not re-verify the journal.
    """
    if not isinstance(event, dict):
        return False
    if event.get("verified") is False:
        return False
    seq = event.get("sequence")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
        return False
    if not isinstance(event.get("op"), str) or not event.get("op"):
        return False
    if not isinstance(event.get("id"), str) or not event.get("id"):
        return False
    return True


def _safe_id(value: Any) -> str | None:
    """Return a safe identifier, or None if unsafe."""
    if not isinstance(value, str):
        return None
    text = value.strip().strip("/")
    if not text or ".." in text or "/" in text or "\\" in text:
        return None
    if not SAFE_ID_RE.match(text):
        return None
    return text


def _safe_title(value: Any, fallback: str) -> str:
    """Return a bounded plain title; never renders raw message bodies."""
    if isinstance(value, str):
        text = value.strip()
        if text and len(text) <= 300 and "\n" not in text and "\r" not in text:
            return text
    return fallback


def _safe_actor(value: Any) -> str:
    """Return a safe actor label; anything unsafe becomes unknown."""
    candidate = _safe_id(value)
    if candidate is not None and len(candidate) <= 64:
        return candidate
    return "unknown"


def _format_timestamp(at_val: Any) -> str:
    """Format a POSIX timestamp deterministically in UTC."""
    if isinstance(at_val, (int, float)) and not isinstance(at_val, bool):
        dt = datetime.fromtimestamp(float(at_val), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return "unknown-time"


def _project_url(idea: str) -> str:
    return f"{GITHUB_BASE}/projects/{idea}/"


def load_export(path: Path) -> tuple[list[dict[str, Any]], int | None, str | None]:
    """Load an exported journal prefix JSON file; reject malformed shapes."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw, None, None
    if isinstance(raw, dict) and isinstance(raw.get("events"), list):
        through = raw.get("through")
        house_id = raw.get("house_id")
        return (
            raw["events"],
            through if isinstance(through, int) and not isinstance(through, bool) else None,
            str(house_id) if isinstance(house_id, str) else None,
        )
    raise ValueError("Export must be a JSON object with 'events' list or a JSON list.")


def _event_data(event: dict[str, Any]) -> dict[str, Any]:
    data = event.get("data")
    return data if isinstance(data, dict) else {}


def _index_titles(events: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    """Collect idea titles and proposal titles from actual publish/propose shapes."""
    idea_titles: dict[str, str] = {}
    proposal_titles: dict[str, str] = {}
    for ev in events:
        if not _is_verified_event(ev):
            continue
        data = _event_data(ev)
        if ev["op"] == "shelf" and data.get("kind") == "explore-publish":
            ideas = data.get("ideas")
            if isinstance(ideas, list):
                for entry in ideas:
                    if not isinstance(entry, dict):
                        continue
                    idea_id = _safe_id(entry.get("idea"))
                    if idea_id is not None and idea_id not in idea_titles:
                        idea_titles[idea_id] = _safe_title(entry.get("title"), idea_id)
        elif ev["op"] == "council-propose":
            proposal_id = _safe_id(data.get("proposal"))
            if proposal_id is not None and proposal_id not in proposal_titles:
                proposal_titles[proposal_id] = _safe_title(data.get("title"), proposal_id)
    return idea_titles, proposal_titles


def _index_idea_authors(
    ordered: list[dict[str, Any]],
) -> dict[str, tuple[str, int]]:
    """Index idea -> (author, shelved sequence) from explore-publish events.

    house/shelf.py records the explore-publish actor as each idea's author and
    the publish sequence as its shelved sequence; the first publish wins
    because the reducer rejects duplicate idea IDs.
    """
    authors: dict[str, tuple[str, int]] = {}
    for ev in ordered:
        if ev["op"] != "shelf":
            continue
        data = _event_data(ev)
        if data.get("kind") != "explore-publish":
            continue
        actor = ev.get("actor")
        author = actor if isinstance(actor, str) else ""
        ideas = data.get("ideas")
        if not isinstance(ideas, list):
            continue
        for entry in ideas:
            if not isinstance(entry, dict):
                continue
            idea_id = _safe_id(entry.get("idea"))
            if idea_id is not None and idea_id not in authors:
                authors[idea_id] = (author, ev["sequence"])
    return authors


def _derive_choices(
    events: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Replay actual choice-open/choice-vote transitions under work-selection-003.

    A weigh-in is counted exactly as house/shelf.py records it: a vote for an
    idea is uncounted when the voter is that idea's author (authorship indexed
    from explore-publish), and a None vote is counted. Uncounted votes never
    close the round, so the author's own vote plus only two counted residents
    leaves the choice open. The round closes atomically on the third counted
    weigh-in; the winner has the most counted votes with ties broken by shelved
    sequence then idea ID (the reducer's winner rule), and the shortlist is
    rejected when no candidate reaches two of three counted votes. Repeats by
    an already-weighed resident are ignored, mirroring the reducer's
    one-weigh-in-per-resident rule. There is no choice-close event.
    """
    ordered = sorted(
        (e for e in events if _is_verified_event(e)),
        key=lambda e: e["sequence"],
    )
    authors = _index_idea_authors(ordered)
    choices: dict[str, dict[str, Any]] = {}
    for ev in ordered:
        if ev["op"] != "shelf":
            continue
        data = _event_data(ev)
        kind = data.get("kind")
        # Trial fixture rounds (work-selection-002 trial-choice-1) are isolated
        # demonstrations with a `trial` marker, not real shelf choices.
        if "trial" in data:
            continue
        if kind == "choice-open":
            choice_id = _safe_id(data.get("choice"))
            milestones = data.get("milestones")
            if choice_id is None or not isinstance(milestones, dict):
                continue
            candidates: list[str] = []
            for idea_key in milestones.keys():
                safe = _safe_id(idea_key)
                if safe is not None and safe not in candidates:
                    candidates.append(safe)
            if choice_id not in choices and candidates:
                choices[choice_id] = {
                    "choice": choice_id,
                    "slot": data.get("slot") if data.get("slot") in ("great", "small", "house") else None,
                    "candidates": candidates,
                    "milestones": milestones,
                    "votes": [],
                    "voters": set(),
                    "opened_sequence": ev["sequence"],
                    "status": "open",
                    "winner": None,
                    "closed_sequence": None,
                    "closed_at": None,
                    "closed_actor": None,
                }
        elif kind == "choice-vote":
            choice_id = _safe_id(data.get("choice"))
            if choice_id is None or choice_id not in choices:
                continue
            choice = choices[choice_id]
            if choice["status"] != "open":
                continue
            raw_idea = data.get("idea")
            if raw_idea is None:
                vote_idea: str | None = None
            else:
                vote_idea = _safe_id(raw_idea)
                # A vote naming a non-candidate is not a valid weigh-in; drop it.
                if vote_idea is None or vote_idea not in choice["candidates"]:
                    continue
            voter = ev.get("actor")
            voter_actor = voter if isinstance(voter, str) else ""
            # One weigh-in per resident (house/shelf.py rejects repeats); the
            # first recorded weigh-in stands.
            if voter_actor in choice["voters"]:
                continue
            choice["voters"].add(voter_actor)
            # Counted exactly as the reducer records it: a vote is counted
            # unless the voter is the author of the voted idea.
            counted = vote_idea is None or voter_actor != authors.get(vote_idea, ("", 0))[0]
            choice["votes"].append({"idea": vote_idea, "sequence": ev["sequence"], "counted": counted})
            counted_votes = [v for v in choice["votes"] if v["counted"]]
            if len(counted_votes) == 3:
                counts: dict[str, int] = {}
                for vote in counted_votes:
                    if vote["idea"] is not None:
                        counts[vote["idea"]] = counts.get(vote["idea"], 0) + 1
                # Winner: most counted votes; ties by shelved sequence then ID.
                winner = min(
                    choice["candidates"],
                    key=lambda candidate: (
                        -counts.get(candidate, 0),
                        authors.get(candidate, ("", 0))[1],
                        candidate,
                    ),
                )
                if counts.get(winner, 0) < 2:
                    choice["winner"] = None
                    choice["status"] = "rejected"
                else:
                    choice["winner"] = winner
                    choice["status"] = "closed"
                choice["closed_sequence"] = ev["sequence"]
                choice["closed_at"] = ev.get("at")
                choice["closed_actor"] = ev.get("actor")
    return choices


def select_milestones(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive allowlisted milestones from actual transitions; render no raw text."""
    ordered = sorted(
        (e for e in events if _is_verified_event(e)),
        key=lambda e: e["sequence"],
    )
    idea_titles, proposal_titles = _index_titles(events)
    choices = _derive_choices(events)

    # Each project-done passes one stage; only the last finishes a great work.
    project_steps: list[tuple[str, dict[str, Any], int, int]] = []
    dropped_projects: list[tuple[str, dict[str, Any]]] = []
    completed: dict[str, int] = {}
    terminal: set[str] = set()
    for ev in ordered:
        if ev["op"] != "shelf":
            continue
        data = _event_data(ev)
        kind = data.get("kind")
        if kind not in {"project-done", "project-drop"}:
            continue
        choice_id = _safe_id(data.get("project"))
        if choice_id is None or choice_id not in choices or choice_id in terminal:
            continue
        choice = choices[choice_id]
        if (choice["status"] != "closed" or choice["winner"] is None
                or ev["sequence"] <= choice["closed_sequence"]):
            continue
        if kind == "project-drop":
            terminal.add(choice_id)
            dropped_projects.append((choice_id, ev))
            continue
        plan = choice["milestones"][choice["winner"]]
        if not isinstance(plan, dict):
            continue
        total = 1
        if "milestones" in plan:
            stages = plan["milestones"]
            if not isinstance(stages, list) or not 2 <= len(stages) <= 8:
                continue
            total = len(stages)
        number = completed.get(choice_id, 0) + 1
        completed[choice_id] = number
        project_steps.append((choice_id, ev, number, total))
        if number == total:
            terminal.add(choice_id)

    selected: list[dict[str, Any]] = []

    for choice_id, choice in choices.items():
        if choice["status"] == "open":
            continue
        winner = choice["winner"]
        winner_title = idea_titles.get(winner, winner) if winner else "None of these"
        if choice["status"] == "closed" and winner is not None:
            category = "Closed Choice"
            category_key = "choice"
            title = f"{choice_id} — {winner_title}"
        else:
            category = "Rejected Shortlist"
            category_key = "rejected"
            title = f"{choice_id} — shortlist rejected, no winner"
        # No project link on a closed choice: the winning build may not exist
        # yet, and guessing projects/<idea>/ would point at unbuilt directories.
        # Links appear only on recorded completed projects below.
        links: list[tuple[str, str]] = []
        slot_prefix = {"great": "Great-work slot · ", "house": "House-work slot · "}.get(choice.get("slot"), "")
        base_summary = f"Winner: {winner_title}." if winner else "No candidate earned two of three votes."
        selected.append({
            "category": category,
            "category_key": category_key,
            "sequence": choice["closed_sequence"],
            "at": choice["closed_at"],
            "timestamp": _format_timestamp(choice["closed_at"]),
            "actor": _safe_actor(choice["closed_actor"]),
            "title": title,
            "summary": slot_prefix + base_summary,
            "links": links,
        })

    for choice_id, ev, number, total in project_steps:
        choice = choices[choice_id]
        winner = choice["winner"]
        assert winner is not None
        winner_title = idea_titles.get(winner, winner)
        finished = number == total
        title = winner_title if finished else f"{winner_title} — stage {number} of {total}"
        summary = (f"Project {choice_id} marked done." if finished
                   else f"Stage {number} of {total} passed; the project remains unfinished.")
        selected.append({
            "category": "Completed Project" if finished else "Passed Stage",
            "category_key": "project" if finished else "stage",
            "sequence": ev["sequence"],
            "at": ev.get("at"),
            "timestamp": _format_timestamp(ev.get("at")),
            "actor": _safe_actor(ev.get("actor")),
            "title": title,
            "idea": winner,
            "summary": summary,
            "links": [(f"projects/{winner}/", _project_url(winner))] if finished else [],
        })

    for choice_id, ev in dropped_projects:
        winner = choices[choice_id]["winner"]
        assert winner is not None
        winner_title = idea_titles.get(winner, winner)
        selected.append({
            "category": "Stopped Project",
            "category_key": "dropped",
            "sequence": ev["sequence"],
            "at": ev.get("at"),
            "timestamp": _format_timestamp(ev.get("at")),
            "actor": _safe_actor(ev.get("actor")),
            "title": winner_title,
            "summary": f"Project {choice_id} stopped before completion.",
            "links": [],
        })

    rooms: dict[str, dict[str, Any]] = {}
    for ev in ordered:
        if ev["op"] == "council-enact":
            data = _event_data(ev)
            proposal_id = _safe_id(data.get("proposal"))
            if proposal_id is None:
                continue
            title = proposal_titles.get(proposal_id, proposal_id)
            selected.append({
                "category": "Enacted Rule",
                "category_key": "rule",
                "sequence": ev["sequence"],
                "at": ev.get("at"),
                "timestamp": _format_timestamp(ev.get("at")),
                "actor": _safe_actor(ev.get("actor")),
                "title": title,
                "summary": f"Rule {proposal_id} enacted by the council.",
                "links": [],
            })
        elif ev["op"] == "owner-migrate":
            data = _event_data(ev)
            rule = OWNER_MIGRATION_RULES.get(data.get("scope"))
            if rule is None:
                continue
            rule_id, rule_title = rule
            selected.append({
                "category": "Enacted Rule",
                "category_key": "rule",
                "sequence": ev["sequence"],
                "at": ev.get("at"),
                "timestamp": _format_timestamp(ev.get("at")),
                "actor": _safe_actor(ev.get("actor")),
                "title": rule_title,
                "summary": f"Rule {rule_id} enacted by direct-owner migration.",
                "links": [],
            })
        elif ev["op"] == "life":
            data = _event_data(ev)
            kind = data.get("kind")
            room_id = _safe_id(data.get("room"))
            if room_id is None:
                continue
            if kind in {"room-plan", "room-repurpose"}:
                prior = rooms.get(room_id, {})
                raw_floor = data.get("floor") if kind == "room-plan" else prior.get("floor", 0)
                floor = raw_floor if type(raw_floor) is int and 0 <= raw_floor <= 99 else 0
                rooms[room_id] = {
                    "name": _safe_title(data.get("name"), room_id),
                    "floor": floor,
                    "builder": ev.get("actor"),
                    "status": "construction",
                }
            elif kind == "room-close" and room_id in rooms:
                rooms[room_id]["status"] = "closed"
            elif kind == "room-open":
                room = rooms.get(room_id)
                if room is None or room["status"] != "construction" or room["builder"] != ev.get("actor"):
                    continue
                room["status"] = "open"
                selected.append({
                    "category": "Opened Room",
                    "category_key": "room",
                    "sequence": ev["sequence"],
                    "at": ev.get("at"),
                    "timestamp": _format_timestamp(ev.get("at")),
                    "actor": _safe_actor(ev.get("actor")),
                    "title": room["name"],
                    "summary": f"Room {room_id} opened on floor {room['floor']}.",
                    "links": [],
                })

    selected.sort(key=lambda item: (item["sequence"], float(item["at"] or 0.0), item["title"]))
    return selected


def _browser_actions(catalog: dict[str, Any] | None) -> dict[str, tuple[str, str]]:
    """Use only catalogue routes whose entry page is in the public file list."""
    if not isinstance(catalog, dict) or type(catalog.get("version")) is not int or catalog["version"] != 1:
        return {}
    projects = catalog.get("projects")
    if not isinstance(projects, list):
        return {}
    actions = {}
    for entry in projects:
        if not isinstance(entry, dict):
            continue
        idea = entry.get("id")
        href = entry.get("href")
        action = entry.get("action")
        if (not isinstance(idea, str) or not re.fullmatch(r"[a-z0-9-]+", idea)
                or entry.get("category") != "creation" or action not in ("Open", "Play")
                or not isinstance(href, str)
                or not re.fullmatch(r"projects/" + re.escape(idea) + r"/(?:[a-z0-9-]+/)*(?:[a-z0-9-]+\.html)?", href)):
            continue
        target = href + "index.html" if href.endswith("/") else href
        if isinstance(entry.get("files"), list) and target in entry["files"]:
            actions[idea] = (action, "../" + target)
    return actions


def render_html(
    milestones: list[dict[str, Any]],
    through: int | None = None,
    house_id: str | None = None,
    catalog: dict[str, Any] | None = None,
) -> str:
    """Render deterministic, zero-JS static HTML for the Chronicle Room."""
    counts = {
        "project": sum(1 for m in milestones if m["category_key"] == "project"),
        "stage": sum(1 for m in milestones if m["category_key"] == "stage"),
        "dropped": sum(1 for m in milestones if m["category_key"] == "dropped"),
        "room": sum(1 for m in milestones if m["category_key"] == "room"),
        "rule": sum(1 for m in milestones if m["category_key"] == "rule"),
        "choice": sum(1 for m in milestones if m["category_key"] == "choice"),
        "rejected": sum(1 for m in milestones if m["category_key"] == "rejected"),
    }
    through_label = str(through) if through is not None else (
        str(milestones[-1]["sequence"]) if milestones else "0"
    )
    house_label = html.escape(house_id) if house_id else "Emberhall"

    actions = _browser_actions(catalog)
    rows_html: list[str] = []
    for position, item in enumerate(reversed(milestones)):
        title = item["title"]
        if item["category_key"] == "choice":
            title = title.partition(" — ")[2] or title
        elif item["category_key"] == "rejected":
            title = "No project selected"
        links_html = " ".join(
            f'<a href="{html.escape(href)}">View project files →</a>'
            for _, href in item["links"]
        )
        launch = actions.get(item.get("idea")) if item["category_key"] == "project" else None
        if launch:
            action, href = launch
            links_html = (f'<a class="launch" href="{html.escape(href)}">'
                          f'{action} {html.escape(title)} →</a> ' + links_html)
        rows_html.append(
            f'<article class="entry entry-{html.escape(item["category_key"])}{" earlier-entry" if position >= 8 else ""}">\n'
            f'  <div class="meta"><span class="badge">{html.escape(item["category"])}</span> '
            f'<span class="time">{html.escape(item["timestamp"])}</span></div>\n'
            f'  <h3>{html.escape(title)}</h3>\n'
            f'  <div class="links">{links_html}</div>\n'
            f'  <details class="record"><summary>View record</summary>\n'
            f'    <p>{html.escape(item["title"])} · event {item["sequence"]}</p>\n'
            f'    <p>{html.escape(item["summary"])}</p>\n'
            f'    <p>Recorded by {html.escape(item["actor"])}</p>\n'
            f'  </details>\n'
            f'</article>'
        )

    kinds = [("all", "All milestones", len(milestones)),
             ("project", "Finished creations", counts["project"]),
             ("stage", "Passed stages", counts["stage"]),
             ("dropped", "Stopped projects", counts["dropped"]),
             ("room", "Opened rooms", counts["room"]),
             ("rule", "Enacted rules", counts["rule"]),
             ("choice", "Closed choices", counts["choice"]),
             ("rejected", "None chosen", counts["rejected"])]
    controls = "\n".join(
        f'<label for="chronicle-{key}"><input type="radio" name="chronicle-kind" '
        f'id="chronicle-{key}" value="{key}"{" checked" if key == "all" else ""}> '
        f'{label} ({count})</label>' for key, label, count in kinds)
    headings = "\n".join(
        f'<h2 class="kind-heading heading-{key}">{label} ({count})</h2>'
        for key, label, count in kinds)
    empty_labels = {"all": "milestones", "rejected": "rejected shortlists"}
    empty_states = "\n".join(
        f'<p class="empty empty-{key}">No {empty_labels.get(key, label.lower())} recorded in this snapshot.</p>'
        for key, label, count in kinds if not count)
    entries_block = "\n".join(rows_html)
    # Without :has support, show the entire record and no inert controls.
    browse_css = "\n".join(
        f'main:has(#chronicle-{key}:checked) .entry:not(.entry-{key}), '
        f'main:has(#chronicle-{key}:checked) .heading-all, '
        f'main:has(#chronicle-{key}:checked) .empty-all, '
        f'main:has(#chronicle-{key}:checked) .earlier-control, '
        f'main:has(#chronicle-{key}:checked) .recent-note {{ display: none; }}\n'
        f'main:has(#chronicle-{key}:checked) .heading-{key}, '
        f'main:has(#chronicle-{key}:checked) .empty-{key} {{ display: block; }}'
        for key, _, _ in kinds if key != "all")
    earlier_control = (
        f'<label class="earlier-control" for="chronicle-earlier">'
        f'<input type="checkbox" id="chronicle-earlier"> '
        f'Show all {len(milestones)} milestones, including earlier history</label>'
        f'<p class="note recent-note">Showing the latest 8 of {len(milestones)}. '
        'Choosing a kind includes its earlier history.</p>' if len(milestones) > 8 else "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Emberhall Chronicle Room</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f6f2ea;
      --card: #fffdf9;
      --ink: #221f1a;
      --muted: #665e52;
      --border: #dfd6c7;
      --accent: #9b3d1e;
      --accent-wash: #f7e7db;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #171c22;
        --card: #202731;
        --ink: #f4eee3;
        --muted: #c4bbad;
        --border: #4b5058;
        --accent: #ffb387;
        --accent-wash: #2f251f;
      }}
    }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    main {{
      max-width: 860px;
      margin: 0 auto;
      padding: 2rem 1.25rem 3rem;
    }}
    header {{
      border-bottom: 2px solid var(--border);
      padding-bottom: 1rem;
      margin-bottom: 1.5rem;
    }}
    header a, .site-footer a {{
      color: var(--accent);
      text-underline-offset: 0.2em;
      display: inline-flex;
      align-items: center;
      box-sizing: border-box;
      min-height: 44px;
    }}
    h1 {{
      margin: 0 0 0.4rem;
      font-size: 1.9rem;
    }}
    .note {{
      color: var(--muted);
      font-size: 0.95rem;
      margin: 0.4rem 0;
    }}
    .browse-controls {{
      display: none;
      border: 0;
      padding: 0;
      margin: 1rem 0;
    }}
    .browse-options {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 0.5rem;
    }}
    .browse-options label {{
      background: var(--card);
      border: 1px solid var(--border);
      box-sizing: border-box;
      min-height: 44px;
      padding: 0.65rem;
      border-radius: 4px;
      cursor: pointer;
    }}
    legend {{ font-weight: bold; margin-bottom: 0.5rem; }}
    .earlier-control, .recent-note, .kind-heading, .empty {{ display: none; }}
    .heading-all, .empty-all {{ display: block; }}
    h2 {{ font-size: 1.2rem; }}
    @supports selector(main:has(input:checked)) {{
      .browse-controls, .earlier-control, .recent-note {{ display: block; }}
      .earlier-control {{ box-sizing: border-box; min-height: 44px; padding: 0.65rem 0; cursor: pointer; }}
      .browse-options label:has(input:checked) {{ border-color: var(--accent); background: var(--accent-wash); }}
      main:has(#chronicle-all:checked):not(:has(#chronicle-earlier:checked)) .earlier-entry {{ display: none; }}
      main:has(#chronicle-earlier:checked) .recent-note {{ display: none; }}
      {browse_css}
    }}
    .entry {{
      background: var(--card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      padding: 0.9rem 1rem;
      margin-bottom: 0.9rem;
      border-radius: 4px;
    }}
    .meta {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.8rem;
      color: var(--muted);
      margin-bottom: 0.35rem;
    }}
    .badge {{
      color: var(--accent);
      font-weight: 700;
    }}
    h3 {{
      margin: 0.2rem 0 0.35rem;
      font-size: 1.1rem;
    }}
    p {{
      margin: 0.2rem 0 0.4rem;
    }}
    details {{ overflow-wrap: anywhere; }}
    summary {{
      cursor: pointer;
      color: var(--muted);
      box-sizing: border-box;
      min-height: 44px;
      padding: 0.75rem 0;
    }}
    .record {{ margin-top: 0.8rem; font-size: 0.85rem; }}
    .earlier > summary {{ padding: 1rem 0; }}
    .snapshot {{ font-size: 0.85rem; margin-bottom: 1rem; }}
    .links a {{
      color: var(--accent);
      text-underline-offset: 0.2em;
      margin-right: 0.9rem;
      font-size: 0.9rem;
      display: inline-flex;
      align-items: center;
      box-sizing: border-box;
      min-height: 44px;
      padding: 0.5rem 0;
      overflow-wrap: anywhere;
    }}
    .links .launch {{ font-weight: bold; }}
    .site-footer {{
      border-top: 1px solid var(--border);
      margin-top: 2rem;
      padding-top: 1rem;
      color: var(--muted);
      font-size: 0.9rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem 1.2rem;
    }}
    a:focus-visible, summary:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
    @media (forced-colors: active) {{
      a:focus-visible, summary:focus-visible, input:focus-visible {{ outline-color: Highlight; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <a href="../index.html#house-view">← Return to the house</a>
      <h1>The Chronicle</h1>
      <p class="note">What Emberhall has made and decided. Latest milestones first.</p>
      <p class="note"><a href="../index.html#gallery-view">Explore the projects →</a></p>
      <p class="note">Browser creations open in their current published versions; source files stay available alongside them.</p>
      <details class="snapshot">
        <summary>About this snapshot</summary>
        <p>House {house_label}, recorded through event {html.escape(through_label)}.
        This is a dated snapshot; return to the house for current activity.</p>
        <p>Generated from an exported journal prefix. The generator checks event
        shapes and replays project choices and rule enactments; the caller verifies
        the source record. Only public milestone fields are shown.</p>
      </details>
    </header>
    <fieldset class="browse-controls">
      <legend>Browse milestones</legend>
      <div class="browse-options">{controls}</div>
    </fieldset>
    {earlier_control}
    <section aria-label="Chronological milestones">
      {headings}
      {empty_states}
      {entries_block}
    </section>
    <footer class="site-footer" aria-label="Emberhall rooms">
      <a href="../index.html#house-view">House</a>
      <a href="../index.html#projects-view">Projects</a>
      <a href="../index.html#gallery-view">Gallery</a>
      <a href="../index.html#council-view">Council</a>
    </footer>
  </main>
</body>
</html>
"""


def generate(input_path: Path, output_dir: Path, catalog_path: Path | None = None) -> Path:
    """Read exported journal prefix and write site/chronicle/index.html."""
    events, through, house_id = load_export(input_path)
    milestones = select_milestones(events)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path else None
    html_text = render_html(milestones, through=through, house_id=house_id, catalog=catalog)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "index.html"
    out_file.write_text(html_text, encoding="utf-8")
    return out_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate static Emberhall Chronicle Room HTML from an exported journal prefix."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to exported journal JSON")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory (e.g. site/chronicle)")
    parser.add_argument("--catalog", type=Path, help="Public project catalogue, for direct browser launch links")
    args = parser.parse_args(argv)
    out_file = generate(args.input, args.output_dir, args.catalog)
    print(f"Wrote {out_file} ({out_file.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
