#!/usr/bin/env python3
"""Print one short line per event from a saved `house read` page, without house I/O.

Usage:
    ./.house-client read --as ID --limit 40 | python3 scripts/read_brief.py -
    python3 scripts/read_brief.py page.json [--full SEQUENCE]

Every event gets exactly one line (nothing is silently dropped); coordinator
boilerplate collapses to a tag. The footer gives through/has_more and the exact
next --after cursor so paging never skips or re-reads a page.
"""
from __future__ import annotations

import argparse
import json
import sys

BOILERPLATE_PREFIXES = ("house-home-result-v1", "house-mailbox-time-v1", "house-assignment-v1")
BOILERPLATE_KINDS = {"run-start", "run-finish", "run-launched", "budget"}
SUMMARY_KEYS = ("text", "note", "claim", "result", "description", "title", "evidence")


def one_line(value: object, limit: int = 150) -> str:
    text = " ".join(str(value).split())
    text = "".join(c if c.isprintable() else "?" for c in text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def short_actor(actor: object) -> str:
    name = str(actor or "?")
    return name[9:17] if name.startswith("resident-") else name[:24]


def summarize(event: dict) -> str:
    data = event.get("data")
    if not isinstance(data, dict):
        return one_line(data)
    actor = str(event.get("actor") or "")
    kind = data.get("kind")
    text = data.get("text")
    if actor == "watch-keeper" and (
        kind in BOILERPLATE_KINDS
        or (isinstance(text, str) and text.startswith(BOILERPLATE_PREFIXES))
    ):
        tag = kind or (str(text).split(" ", 1)[0] if text else "life")
        parts = [f"[{tag}]"]
        if data.get("run"):
            parts.append(f"run={str(data['run'])[:8]}")
        if data.get("outcome"):
            parts.append(str(data["outcome"]))
        return " ".join(parts)
    parts = []
    for key in ("task", "lesson", "key", "kind"):
        if data.get(key):
            parts.append(f"{key}={one_line(data[key], 48)}")
    for key in SUMMARY_KEYS:
        if data.get(key):
            parts.append(one_line(data[key]))
            break
    if not parts:
        parts.append(one_line({k: v for k, v in list(data.items())[:4]}))
    return " ".join(parts)


def brief(page: dict, raw_bytes: int) -> str:
    events = page.get("events")
    if not isinstance(events, list):
        raise ValueError("page needs an events list")
    lines = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        lines.append(
            f"{event.get('sequence', '?')} {event.get('op', '?')} "
            f"{short_actor(event.get('actor'))} {summarize(event)}"
        )
    through = page.get("through")
    footer = f"through {through} has_more {bool(page.get('has_more'))} events {len(events)}"
    if raw_bytes:
        out_bytes = sum(len(line) + 1 for line in lines)
        footer += f" brief_chars {out_bytes} raw_chars {raw_bytes}"
    lines.append(footer)
    if page.get("has_more") and through is not None:
        lines.append(f"next: read --after {through}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", help="saved read JSON file, or - for stdin")
    parser.add_argument("--full", type=int, metavar="SEQUENCE",
                        help="print the full JSON of one event instead of the brief")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.page == "-" else open(args.page, encoding="utf-8").read()
        page = json.loads(raw)
        if not isinstance(page, dict):
            raise ValueError("page must be a JSON object")
        if args.full is not None:
            for event in page.get("events", []):
                if isinstance(event, dict) and event.get("sequence") == args.full:
                    print(json.dumps(event, indent=1, sort_keys=True))
                    return 0
            print(f"no event with sequence {args.full} in this page", file=sys.stderr)
            return 2
        print(brief(page, len(raw)))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"read_brief: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
