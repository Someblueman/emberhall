"""Collect consecutive fixed-channel pages at a single status cutoff and read the trial."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import tempfile

from cohort import read_pages
from historical_rotation import journal
from trial import assess, baseline_anchor, baseline_option, display


def store(path, data, *, page_bounds=None):
    """Make a complete file visible only after it passes validation."""
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".collect-", mode="w", delete=False) as out:
        temporary = Path(out.name)
        try:
            json.dump(data, out, separators=(",", ":"))
            out.flush()
            events = check_page(temporary, *page_bounds) if page_bounds else None
            os.replace(temporary, path)
            return events
        finally:
            temporary.unlink(missing_ok=True)


def check_page(path, cursor, end, horizon):
    events, through = read_pages([path], cursor)
    if through != end or len(events) != end - cursor:
        raise ValueError(f"expected events {cursor + 1}–{end} in {path.name}")
    if json.loads(path.read_text())["latest"] < horizon:
        raise ValueError(f"page at {cursor + 1} predates the frozen status")
    return events


def collect(directory, resident, baseline, after=None, reader=journal):
    anchor = baseline_anchor(baseline)
    after = anchor - 1 if after is None else after
    if not 0 <= after < anchor:
        raise ValueError(f"context must start at or before event {anchor}")
    directory.mkdir(mode=0o700, exist_ok=True)
    info = directory.lstat()
    if directory.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("use a private directory owned by the current user")
    lock = os.open(directory, os.O_RDONLY)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another reader is collecting into this directory") from exc
        plan_path = directory / "collection.json"
        selection = {"baseline": baseline, "after": after}
        if plan_path.exists():
            plan = json.loads(plan_path.read_text())
            if not isinstance(plan, dict) or any(plan.get(key) != value for key, value in selection.items()):
                raise ValueError("saved baseline or context differs; use its original arguments")
        else:
            if any(not p.name.startswith(".collect-") for p in directory.iterdir()):
                raise ValueError("start in an empty private directory")
            plan = selection
            store(plan_path, plan)

        status_path = directory / "status.json"
        if status_path.exists():
            status = json.loads(status_path.read_text())
        else:
            if "through" in plan or any(directory.glob("page-*.json")):
                raise ValueError("saved pages are missing their covering status")
            status = reader("status")
        horizon = status["sequence"]
        if type(horizon) is not int or horizon <= after:
            raise ValueError("status does not reach the requested interval")
        frozen = selection | {"through": horizon, "house_id": status["house_id"]}
        if "through" in plan and plan != frozen:
            raise ValueError("saved status differs from the frozen collection")
        if not status_path.exists():
            store(status_path, status)
        if plan != frozen:
            store(plan_path, frozen)

        pages = {directory / f"page-{seq + 1:010d}.json": seq for seq in range(after, horizon, 200)}
        if set(directory.glob("page-*.json")) - pages.keys():
            raise ValueError("saved page lies outside the frozen collection")
        events = []
        for page, cursor in pages.items():
            end = min(cursor + 200, horizon)
            if page.exists():
                rows = check_page(page, cursor, end, horizon)
            else:
                data = reader("read", "--as", resident, "--after", str(cursor), "--limit", str(end - cursor))
                rows = store(page, data, page_bounds=(cursor, end, horizon))
            events.extend(rows)
        return assess(events, horizon, baseline)
    finally:
        os.close(lock)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="fresh private directory, or the collection to resume")
    parser.add_argument("--as", dest="resident", required=True, help="identity assigned to this room")
    parser.add_argument("--after", type=int, help="include earlier context after this event")
    parser.add_argument("--json", action="store_true", help="print receipt references and counts")
    baseline_option(parser)
    args = parser.parse_args()
    try:
        report = collect(args.directory, args.resident, args.baseline, args.after)
    except (KeyError, TypeError, OSError, ValueError) as exc:
        parser.exit(2, f"Cannot collect trial: {exc}\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        display(report)


if __name__ == "__main__":
    main()
