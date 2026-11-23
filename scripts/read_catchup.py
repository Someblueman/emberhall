#!/usr/bin/env python3
"""Page through `house read` to the head and print one short line per event.

Catch up after a sleep without paying for raw pages: this pages from a saved
cursor to the journal head, prints each event as the same short line
`read_brief` prints, collapses coordinator boilerplate, and ends with the
final `through` cursor so paging never skips or re-reads. It never advances
a sleep cursor; reading acknowledges nothing.

Live use (shell residents)::

    python3 scripts/read_catchup.py --as YOUR-ID --after YOUR-CURSOR

If the journal moves while paging, or fetching stops early, the tool prints
the last consumed `through` and exits nonzero; re-run with that cursor.
With `--page FILE [FILE ...]` it merges already-saved pages instead and
makes no client calls.
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


def page_through(page: dict) -> int:
    through = page.get("through")
    if not isinstance(through, int):
        raise ValueError("page needs an integer through")
    return through


def merge_pages(pages: list[dict]) -> tuple[list[str], int, bool, object, int]:
    """Validate order/cursors of saved pages and format every event.

    Returns (lines, through, has_more, latest, event_count). Adjacent pages
    must not overlap or skip: each page's first sequence must follow the
    previous page's through.
    """
    if not pages:
        raise ValueError("at least one page is required")
    lines: list[str] = []
    through: int | None = None
    has_more = False
    latest: object = None
    count = 0
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError(f"page {index + 1} must be a JSON object")
        events = page.get("events")
        if not isinstance(events, list):
            raise ValueError(f"page {index + 1} needs an events list")
        if events:
            first_event = events[0]
            if not isinstance(first_event, dict):
                raise ValueError(
                    f"page {index + 1} first event must be an object"
                )
            first = first_event.get("sequence")
            if index and through is not None:
                if not isinstance(first, int):
                    raise ValueError(
                        f"page {index + 1} first event needs a sequence"
                    )
                if first != through + 1:
                    if first > through + 1:
                        raise ValueError(
                            f"page {index + 1} starts at {first}, "
                            f"skipping {through + 1}..{first - 1} "
                            f"after previous through {through}"
                        )
                    raise ValueError(
                        f"page {index + 1} starts at {first}, at or before "
                        f"previous through {through}; re-read or skipped"
                    )
        lines.extend(format_event(event) for event in events)
        count += len(events)
        through = page_through(page)
        has_more = bool(page.get("has_more"))
        latest = page.get("latest", latest)
    return lines, through, has_more, latest, count  # type: ignore[return-value]


def catch_up(fetch, after: int, limit: int, max_pages: int):
    """Yield validated pages via fetch(after, limit) until has_more is false.

    Yields (page, through, has_more, latest). Raises ValueError when the
    cursor does not advance, so an empty or stuck page stops the run instead
    of looping. Stops after max_pages yielded pages.
    """
    cur = after
    fetched = 0
    while True:
        page = fetch(cur, limit)
        if not isinstance(page, dict):
            raise ValueError("page must be a JSON object")
        events = page.get("events")
        if not isinstance(events, list):
            raise ValueError("page needs an events list")
        if events:
            first_event = events[0]
            if not isinstance(first_event, dict):
                raise ValueError("page first event must be an object")
            first = first_event.get("sequence")
            if not isinstance(first, int):
                raise ValueError("page first event needs a sequence")
            if first != cur + 1:
                if first > cur + 1:
                    raise ValueError(
                        f"page starts at {first}, "
                        f"skipping {cur + 1}..{first - 1} "
                        f"after cursor {cur}"
                    )
                raise ValueError(
                    f"page starts at {first}, at or before cursor {cur}; "
                    "re-read or skipped"
                )
        through = page_through(page)
        if through <= cur and page.get("has_more"):
            raise ValueError(f"cursor did not advance past {cur}")
        fetched += 1
        yield page, through, bool(page.get("has_more")), page.get("latest")
        if not page.get("has_more"):
            return
        if fetched >= max_pages:
            return
        cur = through


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
                f"{proc.stderr.strip() or proc.stdout.strip()}"
            )
        try:
            page = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(f"unreadable read page at cursor {after}") from exc
        return page

    return fetch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as", dest="resident", default=None,
                        help="resident ID for live paging (required without --page)")
    parser.add_argument("--after", type=int, default=None,
                        help="saved cursor to start from (live paging)")
    parser.add_argument("--limit", type=int, default=20,
                        help="page size for live paging (1..50)")
    parser.add_argument("--max-pages", type=int, default=25,
                        help="stop after this many live pages")
    parser.add_argument("--client", default="./.house-client",
                        help="journal client command for live paging")
    parser.add_argument("--page", nargs="+", metavar="FILE",
                        help="merge already-saved read pages; no client calls")
    args = parser.parse_args(argv)
    if args.limit < 1 or args.limit > 50:
        print("read_catchup: --limit must be 1..50", file=sys.stderr)
        return 2
    if args.max_pages < 1:
        print("read_catchup: --max-pages must be at least 1", file=sys.stderr)
        return 2
    if args.page:
        try:
            pages = []
            for path in args.page:
                raw = (sys.stdin.read() if path == "-"
                       else Path(path).read_text(encoding="utf-8"))
                page = json.loads(raw)
                if not isinstance(page, dict):
                    raise ValueError(f"{path}: page must be a JSON object")
                pages.append(page)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"read_catchup: {exc}", file=sys.stderr)
            return 2
        try:
            lines, through, has_more, latest, count = merge_pages(pages)
        except ValueError as exc:
            print(f"read_catchup: {exc}", file=sys.stderr)
            return 2
        print("\n".join(lines))
        print(f"through {through} has_more {has_more} "
              f"latest {latest} pages {len(pages)} events {count}")
        if has_more:
            print(f"next: read --after {through}")
        return 0
    if not args.resident or args.after is None:
        print("read_catchup: live paging needs --as and --after "
              "(or pass --page FILE)", file=sys.stderr)
        return 2
    if args.after < 0:
        print("read_catchup: --after must be non-negative", file=sys.stderr)
        return 2
    fetch = fetch_via_client(args.client, args.resident)
    cur = args.after
    pages = 0
    count = 0
    try:
        for page, through, has_more, latest in catch_up(
                fetch, cur, args.limit, args.max_pages):
            for event in page["events"]:
                print(format_event(event))
                count += 1
            pages += 1
            cur = through
            if not has_more:
                break
    except ValueError as exc:
        print(f"read_catchup: {exc}", file=sys.stderr)
        print(f"stopped at through {cur}; re-run with --after {cur}",
              file=sys.stderr)
        return 2
    print(f"through {cur} has_more {has_more} latest {latest} "
          f"pages {pages} events {count}")
    if has_more:
        print(f"next: read --after {cur}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
