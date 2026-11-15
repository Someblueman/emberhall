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
only on recorded completed projects, pointing at real ``projects/<idea>/``
directories via GitHub; closed choices have no project link until completion,
and evidence task IDs are never guessed into evidence directories.
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
# Direct-owner enactment: house/maintenance.py enact_selection_repair enacts
# this exact rule on an owner-migrate with this scope (mirrors the verifier).
OWNER_SELECTION_SCOPE = "work-selection-repair-20261114"
OWNER_SELECTION_RULE_ID = "work-selection-003"
OWNER_SELECTION_TITLE = "Choose worthwhile work, or reject the shortlist"


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
                    "candidates": candidates,
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

    # Project completions: shelf project-done keyed by choice ID.
    project_dones: dict[str, dict[str, Any]] = {}
    for ev in ordered:
        if ev["op"] != "shelf":
            continue
        data = _event_data(ev)
        if data.get("kind") != "project-done":
            continue
        choice_id = _safe_id(data.get("project"))
        if choice_id is None or choice_id not in choices:
            continue
        choice = choices[choice_id]
        if choice["status"] != "closed" or choice["winner"] is None:
            continue
        if choice_id not in project_dones:
            project_dones[choice_id] = ev

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
        selected.append({
            "category": category,
            "category_key": category_key,
            "sequence": choice["closed_sequence"],
            "at": choice["closed_at"],
            "timestamp": _format_timestamp(choice["closed_at"]),
            "actor": _safe_actor(choice["closed_actor"]),
            "title": title,
            "summary": f"Winner: {winner_title}." if winner else "No candidate earned two of three votes.",
            "links": links,
        })

    for choice_id, ev in project_dones.items():
        choice = choices[choice_id]
        winner = choice["winner"]
        assert winner is not None
        winner_title = idea_titles.get(winner, winner)
        selected.append({
            "category": "Completed Project",
            "category_key": "project",
            "sequence": ev["sequence"],
            "at": ev.get("at"),
            "timestamp": _format_timestamp(ev.get("at")),
            "actor": _safe_actor(ev.get("actor")),
            "title": winner_title,
            "summary": f"Project {choice_id} marked done.",
            "links": [(f"projects/{winner}/", _project_url(winner))],
        })

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
            # Direct-owner enactment (house/maintenance.py enact_selection_repair):
            # only this exact scope enacts a rule; other migrations are runtime work.
            data = _event_data(ev)
            if data.get("scope") != OWNER_SELECTION_SCOPE:
                continue
            selected.append({
                "category": "Enacted Rule",
                "category_key": "rule",
                "sequence": ev["sequence"],
                "at": ev.get("at"),
                "timestamp": _format_timestamp(ev.get("at")),
                "actor": _safe_actor(ev.get("actor")),
                "title": OWNER_SELECTION_TITLE,
                "summary": f"Rule {OWNER_SELECTION_RULE_ID} enacted by direct-owner migration.",
                "links": [],
            })

    selected.sort(key=lambda item: (item["sequence"], float(item["at"] or 0.0), item["title"]))
    return selected


def render_html(
    milestones: list[dict[str, Any]],
    through: int | None = None,
    house_id: str | None = None,
) -> str:
    """Render deterministic, zero-JS static HTML for the Chronicle Room."""
    counts = {
        "project": sum(1 for m in milestones if m["category_key"] == "project"),
        "rule": sum(1 for m in milestones if m["category_key"] == "rule"),
        "choice": sum(1 for m in milestones if m["category_key"] == "choice"),
        "rejected": sum(1 for m in milestones if m["category_key"] == "rejected"),
    }
    through_label = str(through) if through is not None else (
        str(milestones[-1]["sequence"]) if milestones else "0"
    )
    house_label = html.escape(house_id) if house_id else "Emberhall"

    rows_html: list[str] = []
    for item in milestones:
        links_html = ""
        if item["links"]:
            anchors = " ".join(
                f'<a href="{html.escape(href)}">{html.escape(label)}</a>'
                for label, href in item["links"]
            )
            links_html = f'<div class="links">{anchors}</div>'
        links_line = f'  {links_html}\n' if links_html else ''
        rows_html.append(
            f'<article class="entry entry-{html.escape(item["category_key"])}">\n'
            f'  <div class="meta">\n'
            f'    <span class="badge">{html.escape(item["category"])}</span>\n'
            f'    <span class="seq">seq {item["sequence"]}</span>\n'
            f'    <span class="time">{html.escape(item["timestamp"])}</span>\n'
            f'    <span class="actor">{html.escape(item["actor"])}</span>\n'
            f'  </div>\n'
            f'  <h3>{html.escape(item["title"])}</h3>\n'
            f'  <p>{html.escape(item["summary"])}</p>\n'
            f'{links_line}'
            f'</article>'
        )

    entries_block = "\n".join(rows_html) if rows_html else (
        '<p class="empty">No allowlisted milestones found in this exported prefix.</p>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Emberhall Chronicle Room</title>
  <style>
    :root {{
      --bg: #f6f2ea;
      --card: #fffdf9;
      --ink: #221f1a;
      --muted: #665e52;
      --border: #dfd6c7;
      --accent: #9b3d1e;
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
    h1 {{
      margin: 0 0 0.4rem;
      font-size: 1.9rem;
    }}
    .note {{
      color: var(--muted);
      font-size: 0.95rem;
      margin: 0.4rem 0;
    }}
    .stats {{
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin: 1rem 0 1.5rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.85rem;
    }}
    .stat {{
      background: var(--card);
      border: 1px solid var(--border);
      padding: 0.35rem 0.65rem;
      border-radius: 4px;
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
    .links a {{
      color: var(--accent);
      margin-right: 0.9rem;
      font-size: 0.9rem;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Emberhall Chronicle Room</h1>
      <p class="note">
        Curated static milestone index for <strong>{house_label}</strong> through sequence
        <code>{html.escape(through_label)}</code>. Complements
        <a href="../index.html">site/index.html</a> (per-event history scrubber) and
        <code>site/house.js</code> (live project and council records).
      </p>
      <p class="note">
        <strong>Under construction:</strong> this Chronicle Room is not yet an opened
        room. The generated page is not an enacted room-construction or room-open
        lifecycle event. Independent source acceptance and a non-author browser
        inspection are still required before the project owner assesses the milestone.
      </p>
      <p class="note">
        Rendered from a caller-provided exported journal prefix. Provenance is the
        caller's responsibility; this generator validates shapes and replays actual
        choice and council transitions under work-selection-003, rendering only the
        public-field allowlist (choice, idea titles, sequence, time, actor,
        completed-project links). Raw message bodies, vote reasons and evidence
        task IDs are never rendered.
      </p>
    </header>
    <section class="stats" aria-label="Milestone summary">
      <div class="stat">Completed projects: {counts["project"]}</div>
      <div class="stat">Enacted rules: {counts["rule"]}</div>
      <div class="stat">Closed choices: {counts["choice"]}</div>
      <div class="stat">Rejected shortlists: {counts["rejected"]}</div>
    </section>
    <section aria-label="Chronological milestones">
      {entries_block}
    </section>
  </main>
</body>
</html>
"""


def generate(input_path: Path, output_dir: Path) -> Path:
    """Read exported journal prefix and write site/chronicle/index.html."""
    events, through, house_id = load_export(input_path)
    milestones = select_milestones(events)
    html_text = render_html(milestones, through=through, house_id=house_id)
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
    args = parser.parse_args(argv)
    out_file = generate(args.input, args.output_dir)
    print(f"Wrote {out_file} ({out_file.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
