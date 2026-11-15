"""Tidy finished resident rooms and integration checkouts the house no longer needs.

Every run gets a full private clone (about 85 MB) and every integration
attempt another. Nothing removed them, so a busy day left hundreds behind.

A resident room is removed only when its run has been finished for a while,
its uncommitted bytes were already saved privately (preservation.json), its
contribution (if any) has a final review result, no action job for the run is
still open, and any commits not already on main were first kept as a verified
git bundle in the run's private folder. An integration checkout is removed
once the review receipt that names it is final, or, if no receipt names it,
once it is old and no integration is running. The sweep holds the integration
lock, so it never races an integration.

    python3 -m house.housekeeping            # report what would be removed
    python3 -m house.housekeeping --apply    # remove it
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from .files import workspace_path
from .record import Record

GRACE_SECONDS = 3600
FINAL = {"integrated", "rejected", "conflict", "tests-failed"}
CANDIDATE = re.compile(r"integration-[0-9a-f]{32}")


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=check, timeout=120)


def _json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _size(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for name in files:
            try:
                total += os.lstat(os.path.join(root, name)).st_size
            except OSError:
                pass
    return total


def _remove(path: Path) -> None:
    def retry(function, name, _):
        os.chmod(os.path.dirname(name), 0o700)
        if not os.path.islink(name):
            os.chmod(name, 0o700)
        function(name)
    shutil.rmtree(path, onexc=retry)


def open_jobs(private: Path) -> set[str]:
    runs = set()
    for path in (private / "jobs").glob("*/job.json"):
        job = _json(path)
        if job is None or job.get("status") != "done":
            runs.add(str(job.get("run")) if job else "*")
    return runs


def room_hold(record: Record, private: Path, run: str, item: dict, room: Path,
              jobs: set[str], now: float) -> str | None:
    """Why this finished room must stay, or None when it is safe to remove."""
    if item.get("status") != "completed":
        return "run is not finished"
    if now - item.get("ended_at", now) < GRACE_SECONDS:
        return "finished less than an hour ago"
    if "*" in jobs or run in jobs:
        return "an action job may still use it"
    folder = private / run
    if not (folder / "preservation.json").is_file():
        return "uncommitted work was never saved privately"
    if (folder / "preservation-error.json").exists() and (_json(folder / "preservation-error.json") or {}).get(
            "workspace_retained"):
        return "kept on purpose after a preservation error"
    contribution = _json(folder / "contribution.json") if (folder / "contribution.json").exists() else {}
    if contribution is None:
        return "contribution record unreadable"
    if contribution.get("status") == "pending-review":
        receipt = _json(folder / "integration.json") or {}
        if receipt.get("contribution") != contribution.get("commit") or receipt.get("status") not in FINAL:
            return "contribution still awaits a final review"
    return None


def keep_commits(record: Record, private: Path, run: str, item: dict, room: Path) -> str | None:
    """Bundle the room's commits that main does not already contain."""
    head = _git(room, "rev-parse", "--verify", "HEAD").stdout.decode().strip()
    base = item.get("source_head")
    if head == base:
        return None
    present = _git(record.root, "cat-file", "-e", head + "^{commit}", check=False).returncode == 0
    if present and _git(record.root, "merge-base", "--is-ancestor", head, "HEAD", check=False).returncode == 0:
        return None
    bundle = private / run / "room-commits.bundle"
    temporary = bundle.with_suffix(".tmp")
    exclude = ["^" + base] if base and _git(room, "cat-file", "-e", base + "^{commit}", check=False).returncode == 0 else []
    _git(room, "bundle", "create", "--quiet", str(temporary), "HEAD", *exclude)
    _git(room, "bundle", "verify", "--quiet", str(temporary))
    temporary.chmod(0o600)
    os.replace(temporary, bundle)
    return bundle.name


def candidates(private: Path) -> dict[str, str | None]:
    """Each integration checkout and the status of the receipt that names it."""
    named: dict[str, str | None] = {}
    for path in private.glob("*/integration.json"):
        receipt = _json(path) or {}
        if isinstance(receipt.get("candidate"), str):
            named[receipt["candidate"]] = receipt.get("status")
    return {path.name: named.get(path.name, None) if path.name in named else "unreferenced"
            for path in private.iterdir() if path.is_dir() and CANDIDATE.fullmatch(path.name)}


def sweep(record: Record, private: Path | None = None, *, apply: bool = False,
          now: float | None = None, limit: int | None = None) -> dict:
    private = record.common / "house-home" if private is None else private
    now = time.time() if now is None else now
    report = {"rooms": [], "checkouts": [], "kept": {}, "bytes": 0, "applied": apply}
    with (private / "integration.lock").open("a+b") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return report | {"skipped": "an integration is running"}
        state = record.read()[0]
        jobs = open_jobs(private)
        for run, item in state.get("life", {}).get("runs", {}).items():
            if limit is not None and len(report["rooms"]) + len(report["checkouts"]) >= limit:
                break
            try:
                room = workspace_path(record, run, state)
            except (OSError, ValueError):
                continue
            if not room.is_dir() or room.is_symlink():
                continue
            hold = room_hold(record, private, run, item, room, jobs, now)
            if hold:
                report["kept"][hold] = report["kept"].get(hold, 0) + 1
                continue
            size = _size(room)
            entry = {"run": run, "bytes": size}
            if apply:
                try:
                    entry["kept_commits"] = keep_commits(record, private, run, item, room)
                except (OSError, subprocess.SubprocessError) as error:
                    key = "could not bundle its commits"
                    report["kept"][key] = report["kept"].get(key, 0) + 1
                    continue
                _remove(room)
            report["rooms"].append(entry)
            report["bytes"] += size
        for name, status in sorted(candidates(private).items()):
            if limit is not None and len(report["rooms"]) + len(report["checkouts"]) >= limit:
                break
            path = private / name
            final = status in FINAL
            old = now - path.stat().st_mtime >= GRACE_SECONDS
            if not (final or (status == "unreferenced" and old)):
                key = "integration checkout still in use"
                report["kept"][key] = report["kept"].get(key, 0) + 1
                continue
            size = _size(path)
            if apply:
                _remove(path)
            report["checkouts"].append({"name": name, "status": status, "bytes": size})
            report["bytes"] += size
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--apply", action="store_true", help="remove what the report lists")
    args = parser.parse_args()
    try:
        report = sweep(Record(args.repo), apply=args.apply)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"housekeeping: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"applied": report["applied"], "rooms": len(report["rooms"]),
                      "integration_checkouts": len(report["checkouts"]),
                      "gigabytes": round(report["bytes"] / 1e9, 2), "kept": report["kept"],
                      **({"skipped": report["skipped"]} if "skipped" in report else {})}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
