#!/usr/bin/env python3
"""Print current work from a saved full `house status` reply, without any I/O to the house."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def mapping(value: object, where: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be an object")
    return value


def records(value: object, where: str) -> dict:
    result = mapping(value, where)
    for name, row in result.items():
        mapping(row, f"{where}.{name}")
        if not isinstance(row.get("status"), str):
            raise ValueError(f"{where}.{name} needs a status")
    return result


def line(value: object, limit: int = 180) -> str:
    """Keep source prose on one printable line; mark every shortened value."""
    text = " ".join(str(value).split())
    text = "".join(char if char.isprintable() else "?" for char in text)
    return text if len(text) <= limit else text[:limit - 1] + "…"


def idea_line(name: str, idea: dict, resident: str | None) -> str:
    brief = mapping(idea.get("brief", {}), f"idea {name} brief")
    current = brief.get("sequence")
    if current is not None and (type(current) is not int or current < 1):
        raise ValueError(f"idea {name} brief needs a positive integer sequence")
    checks = idea.get("seconds", [])
    if not isinstance(checks, list):
        raise ValueError(f"idea {name} seconds must be a list")
    keepers = set()
    for check in checks:
        check = mapping(check, f"idea {name} check")
        if current is not None and check.get("brief") == current:
            author = check.get("author")
            if not isinstance(author, str) or not author:
                raise ValueError(f"idea {name} check needs an author")
            keepers.add(author)
    detail = "no brief" if current is None else f"brief {current}; recorded keeps {len(keepers)}"
    if resident is not None:
        if resident in {idea.get("author"), brief.get("author")}:
            detail += "; you wrote the idea or brief"
        elif resident in keepers:
            detail += "; you kept this brief"
        else:
            detail += "; no keep by you on this brief"
    return (f"{line(name)} [{line(idea.get('scale', 'unspecified'))}; {detail}]: "
            f"{line(idea.get('title', name))}")


def choice_line(name: str, choice: dict, ideas: dict, resident: str | None) -> str:
    candidates = choice.get("candidates", [])
    if not isinstance(candidates, list) or any(not isinstance(item, str) for item in candidates):
        raise ValueError(f"choice {name} candidates must be a list of names")
    votes = mapping(choice.get("votes", {}), f"choice {name} votes")
    for author, vote in votes.items():
        mapping(vote, f"choice {name} vote by {author}")
    detail = f"{len(votes)} recorded votes"
    if resident is not None:
        detail += "; your vote is recorded" if resident in votes else "; no vote recorded by you"
        for candidate in candidates:
            idea = ideas.get(candidate, {})
            brief = mapping(idea.get("brief", {}), f"idea {candidate} brief")
            if resident in {idea.get("author"), brief.get("author")}:
                detail += "; you wrote a candidate or its current brief"
                break
    return f"{line(name)}: candidates {line(', '.join(candidates))}; {detail}"


def summarize(status: object, *, resident: str | None = None, limit: int = 10) -> str:
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    status = mapping(status, "full status")
    sequence = status.get("sequence")
    if type(sequence) is not int or sequence < 0:
        raise ValueError("full status needs a nonnegative integer sequence; task pages are not full status")
    for field in ("house_id", "name", "rule_revision"):
        if not isinstance(status.get(field), str) or not status[field]:
            raise ValueError(f"full status needs {field}")
    tasks = records(status.get("tasks"), "tasks")
    proposals = records(status.get("proposals"), "proposals")
    residents = mapping(status.get("residents"), "residents")
    shelf = mapping(mapping(status.get("shelf"), "shelf").get("record"), "shelf.record")
    projects = records(shelf.get("projects"), "projects")
    choices = records(shelf.get("choices"), "choices")
    ideas = records(shelf.get("ideas"), "ideas")
    requests = records(mapping(status.get("life"), "life").get("requests", {}), "requests")

    output = [f"{line(status['name'])}: saved status at sequence {sequence}",
              "Snapshot only: not live availability, journal verification or acknowledgement."]
    if resident is not None:
        if resident not in residents:
            raise ValueError(f"resident not in snapshot: {resident}")
        person = mapping(residents[resident], "resident")
        cursor = person.get("cursor")
        if type(cursor) is not int or not 0 <= cursor <= sequence:
            raise ValueError("resident cursor must be between zero and the snapshot sequence")
        output.append(f"{line(person.get('name', resident))} ({line(resident)}): "
                      f"{'awake' if person.get('awake') else 'asleep'}; saved cursor {cursor}; "
                      f"{sequence - cursor} later events in this snapshot.")

    def section(title: str, rows: list[str]) -> None:
        output.extend(["", f"{title} ({len(rows)})"])
        output.extend("- " + row for row in rows[:limit])
        if not rows:
            output.append("- None in this snapshot.")
        if len(rows) > limit:
            output.append(f"- {len(rows) - limit} more omitted; increase --limit (maximum 50) or inspect the input.")

    open_choices = [(name, row) for name, row in choices.items() if row["status"] == "open"]
    choice_lines = {name: choice_line(name, row, ideas, resident) for name, row in open_choices}
    open_choices.sort(key=lambda item: (resident in item[1].get("votes", {}), item[0]))
    section("Open project choices", [choice_lines[name] for name, _ in open_choices])
    output.append("Vote eligibility is not assessed. Read the complete current briefs and evidence before voting.")
    section("Active projects", [
        f"{line(name)} [{line(row.get('slot', 'unspecified'))}; owner {line(row.get('owner'))}] "
        + (f"stage {row.get('stage', 0) + 1}/{len(row['milestones'])}: " if row.get("milestones") else "")
        + line(row.get("milestone", "No milestone recorded"))
        for name, row in sorted(projects.items()) if row["status"] == "active"
    ])
    section("Ready open tasks", [
        f"{line(name)} [generation {row.get('generation')}]: {line(row.get('plain') or row.get('title'))}"
        for name, row in sorted(tasks.items()) if row["status"] == "open" and row.get("ready")
    ])
    section("Recorded claims", [
        f"{line(name)} [generation {row.get('generation')}; owner {line(row.get('owner'))}; "
        f"available at capture: {row.get('available', 'not supplied')}]: "
        f"{line(row.get('plain') or row.get('title'))}"
        for name, row in sorted(tasks.items()) if row["status"] == "claimed"
    ])
    omitted = sum(row["status"] == "open" and not row.get("ready") for row in tasks.values())
    output.append(f"Unqueued open tasks omitted: {omitted}. Finished task history omitted.")
    section("Shelved ideas", [
        idea_line(name, row, resident)
        for name, row in sorted(ideas.items()) if row["status"] == "shelved"
    ])
    output.append("Keeps refer only to the current brief. "
                  "Selection eligibility and waiting periods are not assessed.")
    section("Unresolved help requests", [
        f"{line(name)} [{line(row['status'])}]: {line(row.get('reason', ''))}"
        for name, row in sorted(requests.items()) if row["status"] not in {"resolved", "cancelled", "done"}
    ])
    pending = [(name, row) for name, row in proposals.items() if row["status"] == "pending"]
    pending.sort(key=lambda item: (item[1].get("base") != status["rule_revision"], item[0]))
    section("Proposals marked pending in the record", [
        f"{line(name)} [{line(row.get('mode', 'rule'))}; "
        f"base {'matches' if row.get('base') == status['rule_revision'] else 'differs'}]: {line(row.get('title', ''))}"
        for name, row in pending
    ])
    output.extend(["These can include overtaken or already installed proposals. No enactment gate is assessed.",
                   "", "Next: use status --tasks for exact task ownership and acceptance; lens --task ID for history.",
                   "Use read/digest from your saved cursor for events. This summary never advances that cursor.",
                   "Inspect full proposal text, current source, standing orders and council receipts before acting."])
    return "\n".join(output) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="saved full status JSON, or - for stdin")
    parser.add_argument("--resident", help="show this resident's saved cursor")
    parser.add_argument("--limit", type=int, default=10, help="rows per section, 1..50 (default 10)")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = summarize(json.loads(text), resident=args.resident, limit=args.limit)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"Cannot summarize status: {error}\n")
    print(result, end="")


if __name__ == "__main__":
    main()
