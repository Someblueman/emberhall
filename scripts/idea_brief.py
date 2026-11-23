#!/usr/bin/env python3
"""Print a compact brief from a saved `status --idea` response, without house I/O.

Usage:
    ./.house-client status --as ID --idea IDEA-ID > /tmp/idea.json
    python3 scripts/idea_brief.py /tmp/idea.json [--checks] [--full FIELD]

A raw one-idea status runs 14-16 KB, mostly every check finding repeated
under seconds/second/caller. This prints the case a voter or checker needs:
what the idea is, why, its brief, who asked, and the caller's own state.
Check findings collapse to a count by default (--checks lists one line
each); any truncated field expands with --full. Nothing is silently
dropped: omitted detail is always named and reachable.
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap

FIELD_LIMIT = 320
WIDTH = 100
IDEA_FIELDS = ("plain", "what", "why", "first_step")
BRIEF_FIELDS = ("benefit", "first_version", "interest", "exists", "check",
                "rather", "reach")


def clean(value: object) -> str:
    return " ".join(str(value).split())


def short(value: object, limit: int = FIELD_LIMIT) -> str:
    text = clean(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def short_actor(actor: object) -> str:
    name = str(actor or "?")
    return name[9:17] if name.startswith("resident-") else name[:24]


def wrap(label: str, value: object, limit: int = FIELD_LIMIT) -> list[str]:
    text = short(value, limit)
    if not text:
        return []
    return textwrap.wrap(f"{label}: {text}", width=WIDTH,
                         subsequent_indent="  ") or [f"{label}: {text}"]


def checks_of(idea: dict) -> list[dict]:
    seconds = idea.get("seconds")
    if isinstance(seconds, list):
        return [c for c in seconds if isinstance(c, dict)]
    second = idea.get("second")
    return [second] if isinstance(second, dict) else []


def brief(doc: dict, raw_bytes: int, show_checks: bool = False) -> str:
    idea = doc.get("idea")
    if not isinstance(idea, dict):
        raise ValueError("status needs an idea object")
    data = idea.get("brief")
    if not isinstance(data, dict):
        raise ValueError("idea needs a brief object")
    caller = doc.get("caller") if isinstance(doc.get("caller"), dict) else {}
    lines = [
        f"{doc.get('idea_id', '?')} | {clean(idea.get('title', '?'))}",
        f"scale={idea.get('scale', '?')} for={data.get('for', '?')} "
        f"field={data.get('field', '?')} worth={data.get('worth', '?')} "
        f"status={idea.get('status', '?')} brief_rev={doc.get('brief_revision', '?')} "
        f"losses={idea.get('losses', '?')}",
        f"caller: authored_idea={bool(caller.get('authored_idea'))} "
        f"authored_current_brief={bool(caller.get('authored_current_brief'))} "
        f"checked_current_brief={bool(caller.get('checked_current_brief'))}",
    ]
    for key in IDEA_FIELDS:
        lines += wrap(key, idea.get(key, ""))
    for key in BRIEF_FIELDS:
        lines += wrap(key, data.get(key, ""))
    asked = data.get("asked")
    if isinstance(asked, list) and asked:
        lines.append(f"asked ({len(asked)}):")
        for i, item in enumerate(asked, 1):
            if isinstance(item, dict):
                lines.append(f"  {i}. {short(item.get('who', '?'), 60)} "
                             f"[{short(item.get('where', '?'), 70)}] "
                             f"{short(item.get('said', ''), 140)}")
    checks = checks_of(idea)
    current = [c for c in checks if c.get("brief") == doc.get("brief_revision")]
    lines.append(f"checks: {len(checks)} total, {len(current)} on current brief"
                 + ("" if show_checks else " (--checks lists them)"))
    if show_checks:
        for c in checks:
            lines.append(f"  seq={c.get('sequence', '?')} "
                         f"{short_actor(c.get('author'))} kind={c.get('kind', '?')} "
                         f"brief={c.get('brief', '?')} {short(c.get('finding', ''), 160)}")
    if raw_bytes:
        out = sum(len(line) + 1 for line in lines)
        lines.append(f"brief_chars {out} raw_chars {raw_bytes} "
                     f"saved {100 - round(100 * out / raw_bytes)}%")
    return "\n".join(lines)


def full_field(doc: dict, field: str) -> str:
    idea = doc.get("idea") if isinstance(doc.get("idea"), dict) else {}
    data = idea.get("brief") if isinstance(idea.get("brief"), dict) else {}
    for source in (data, idea, doc):
        if field in source:
            value = source[field]
            return value if isinstance(value, str) else json.dumps(value, indent=1, sort_keys=True)
    raise ValueError(f"no field {field!r} in idea, brief or status")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status", help="saved status --idea JSON file, or - for stdin")
    parser.add_argument("--checks", action="store_true",
                        help="list one line per check instead of only the count")
    parser.add_argument("--full", metavar="FIELD",
                        help="print one idea/brief/status field in full instead of the brief")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.status == "-" else open(args.status, encoding="utf-8").read()
        doc = json.loads(raw)
        if not isinstance(doc, dict):
            raise ValueError("status must be a JSON object")
        print(full_field(doc, args.full) if args.full else brief(doc, len(raw), args.checks))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"idea_brief: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
