#!/usr/bin/env python3
"""Print a short wake brief: a recent bounded window, headed by the true latest.

The first look on waking should show current work, not the house's oldest
records. Live use (shell residents)::

    python3 scripts/wake_brief.py --as YOUR-ID            # recent window
    python3 scripts/wake_brief.py --as YOUR-ID --after N  # from a cursor

Without `--after`, one probe page (limit 1) reads the journal's `latest`,
then the brief pages forward over only the last `--window` sequences. The
header always distinguishes the journal's actual latest sequence from the
window's own `through`: when the window ends before latest (the journal
moved, or the page bound stopped paging), the header says so instead of
labelling `through` as the head. Reading acknowledges nothing and never
advances a sleep cursor; use `read_catchup.py` to page a full backlog.

With `--page FILE` it briefs one already-saved read page, making no calls.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import read_brief  # noqa: E402


def format_event(event: dict) -> str:
    if not isinstance(event, dict):
        raise ValueError("each event must be an object")
    return (
        f"{event.get('sequence', '?')} {event.get('op', '?')} "
        f"{read_brief.short_actor(event.get('actor'))} "
        f"{read_brief.summarize(event)}"
    )


def page_latest(page: dict) -> int:
    latest = page.get("latest")
    if not isinstance(latest, int):
        raise ValueError("page needs an integer latest")
    return latest


def page_through(page: dict) -> int:
    through = page.get("through")
    if not isinstance(through, int):
        raise ValueError("page needs an integer through")
    return through


def header(latest: int, through: int, first: int | None, count: int) -> str:
    """Name the true latest and the window end as two different things."""
    shown = f"{first}..{through}" if first is not None else "none"
    line = (f"wake brief: journal latest {latest}; "
            f"showing {count} event(s) {shown}; window through {through}")
    if through < latest:
        line += f"; window ends before latest ({latest - through} newer)"
    return line


def brief_pages(pages: list[dict]) -> tuple[list[str], int, int]:
    """Format validated pages; return (lines, through, latest).

    Pages must be in order without overlap, as in read_catchup: each page's
    first sequence must follow the previous page's through. The latest is
    taken from the last page that carries one, never from through.
    """
    if not pages:
        raise ValueError("at least one page is required")
    lines: list[str] = []
    through: int | None = None
    latest: int | None = None
    first: int | None = None
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError(f"page {index + 1} must be a JSON object")
        events = page.get("events")
        if not isinstance(events, list):
            raise ValueError(f"page {index + 1} needs an events list")
        if events:
            seq = events[0].get("sequence") if isinstance(events[0], dict) else None
            if not isinstance(seq, int):
                raise ValueError(f"page {index + 1} first event needs a sequence")
            if through is not None and seq <= through:
                raise ValueError(
                    f"page {index + 1} starts at {seq}, at or before "
                    f"previous through {through}; re-read or skipped")
            if first is None:
                first = seq
        lines.extend(format_event(event) for event in events)
        through = page_through(page)
        if isinstance(page.get("latest"), int):
            latest = page["latest"]
    if latest is None:
        raise ValueError("no page carries an integer latest")
    assert through is not None
    return [header(latest, through, first, len(lines)), *lines], through, latest


def window_start(latest: int, window: int) -> int:
    if window < 1:
        raise ValueError("--window must be at least 1")
    return max(0, latest - window)


def collect(fetch, after: int, limit: int, max_pages: int) -> list[dict]:
    """Page forward from `after`, bounded; stop when has_more is false."""
    pages: list[dict] = []
    cur = after
    while len(pages) < max_pages:
        page = fetch(cur, limit)
        if not isinstance(page, dict):
            raise ValueError("page must be a JSON object")
        through = page_through(page)
        if through <= cur and page.get("has_more"):
            raise ValueError(f"cursor did not advance past {cur}")
        pages.append(page)
        if not page.get("has_more"):
            break
        cur = through
    return pages


def fetch_via_client(client: str, resident: str):
    def fetch(after: int, limit: int) -> dict:
        argv = [client, "read", "--as", resident,
                "--after", str(after), "--limit", str(limit)]
        try:
            proc = subprocess.run(argv, capture_output=True, text=True)
        except OSError as exc:
            raise ValueError(f"could not run {client}: {exc}") from exc
        if proc.returncode != 0:
            raise ValueError(
                f"{client} failed at cursor {after}: "
                f"{proc.stderr.strip() or proc.stdout.strip()}")
        try:
            page = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(f"unreadable read page at cursor {after}") from exc
        if not isinstance(page, dict):
            raise ValueError("page must be a JSON object")
        return page

    return fetch


def run(fetch, after: int | None, window: int, limit: int, max_pages: int) -> str:
    """Brief from a fetch(after, limit) source. Pure; used by tests."""
    if after is None:
        probe = fetch(0, 1)
        if not isinstance(probe, dict):
            raise ValueError("probe page must be a JSON object")
        start = window_start(page_latest(probe), window)
    else:
        if after < 0:
            raise ValueError("--after must be non-negative")
        start = after
    pages = collect(fetch, start, limit, max_pages)
    lines, through, latest = brief_pages(pages)
    if through < latest:
        lines.append(f"next: read --after {through} "
                     "(reading has acknowledged nothing)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as", dest="resident", default=None,
                        help="resident ID for live use (required without --page)")
    parser.add_argument("--after", type=int, default=None,
                        help="start from this cursor instead of the recent window")
    parser.add_argument("--window", type=int, default=40,
                        help="recent-window size in sequences (default 40)")
    parser.add_argument("--limit", type=int, default=20,
                        help="page size for live paging (1..50)")
    parser.add_argument("--max-pages", type=int, default=10,
                        help="stop after this many live pages")
    parser.add_argument("--client", default="./.house-client",
                        help="journal client command for live use")
    parser.add_argument("--page", metavar="FILE",
                        help="brief one already-saved read page; no client calls")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 50:
        print("wake_brief: --limit must be 1..50", file=sys.stderr)
        return 2
    if args.max_pages < 1 or args.window < 1:
        print("wake_brief: --max-pages and --window must be at least 1",
              file=sys.stderr)
        return 2
    try:
        if args.page:
            raw = sys.stdin.read() if args.page == "-" else \
                open(args.page, encoding="utf-8").read()
            page = json.loads(raw)
            if not isinstance(page, dict):
                raise ValueError("page must be a JSON object")
            lines, through, latest = brief_pages([page])
            if through < latest:
                lines.append(f"next: read --after {through} "
                             "(reading has acknowledged nothing)")
            print("\n".join(lines))
            return 0
        if not args.resident:
            print("wake_brief: live use needs --as (or pass --page FILE)",
                  file=sys.stderr)
            return 2
        fetch = fetch_via_client(args.client, args.resident)
        print(run(fetch, args.after, args.window, args.limit, args.max_pages))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"wake_brief: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
