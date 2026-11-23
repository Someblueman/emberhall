#!/usr/bin/env python3
"""Print one short line per queued task from a saved `status --tasks` reply.

Usage:
    ./.house-client status --tasks --limit 20 | python3 scripts/task_brief.py -
    python3 scripts/task_brief.py saved-tasks.json

No house I/O: reads one saved paged reply and prints the open and
claimed tasks a resident needs to choose work, without the full
descriptions the paged reply carries. Empty pages and bad input
exit 2 with a short message.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def one_line(value: object, limit: int = 150) -> str:
    text = " ".join(str(value).split())
    text = "".join(c if c.isprintable() else "?" for c in text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def brief(page: dict) -> str:
    if not isinstance(page, dict):
        raise ValueError("page must be an object")
    tasks = page.get("tasks")
    if not isinstance(tasks, dict):
        raise ValueError("page needs a tasks object")
    pageinfo = page.get("page")
    if not isinstance(pageinfo, dict):
        raise ValueError("page needs a page object")
    lines: list[str] = []
    for name, row in sorted(tasks.items()):
        if not isinstance(row, dict):
            raise ValueError(f"task {name} must be an object")
        status = str(row.get("status") or "open")
        gen = row.get("generation")
        bits = [status]
        if isinstance(gen, int):
            bits.append(f"gen {gen}")
        if row.get("owner"):
            bits.append(f"owner {one_line(row['owner'], 48)}")
        title = one_line(row.get("plain") or row.get("title") or "")
        lines.append(f"{one_line(name, 80)} [{' '.join(bits)}]: {title}")
    total = pageinfo.get("total")
    shown = pageinfo.get("shown")
    nxt = pageinfo.get("next_offset")
    lines.append(
        f"tasks total {total if total is not None else '?'} "
        f"shown {shown if shown is not None else len(tasks)} "
        f"next_offset {nxt if nxt is not None else 'none'}"
    )
    if not tasks:
        lines.insert(0, "no queued tasks")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="saved status --tasks JSON, or - for stdin")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        page = json.loads(raw)
        print(brief(page), end="")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"task_brief: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
