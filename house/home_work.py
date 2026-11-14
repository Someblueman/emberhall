"""Private source rooms and reviewable contributions; never a shared worker index."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .record import Record
from .resident_client import client
from .watch_recovery import capture, save_rescue, source_head
from .files import workspace_location


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def room(record: Record, private: Path, run: str, base: str) -> Path:
    from .mailbox import directory
    if private != record.common / "house-home":
        raise ValueError("invalid private room store")
    root, parts = workspace_location(record, run)
    target = root.joinpath(*parts)
    with directory(root, *parts[:-1], create=True):
        pass
    if target.exists() or target.is_symlink():
        raise ValueError("resident workspace already exists; preserve it")
    # Ordinary independent clone: no shared index/working tree or worktree registry.
    subprocess.run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--no-tags",
                    str(record.root), str(target)], check=True, capture_output=True)
    target.chmod(0o700)
    git(target, "checkout", "--quiet", "--detach", base)
    git(target, "remote", "remove", "origin")
    return target



def preserve(private: Path, run: str, workspace: Path) -> dict:
    """Store every partial source byte privately before considering integration."""
    record = Record(workspace)
    rescue = save_rescue(record, private, run)
    return {"workspace": "residents/" + run, "head": source_head(record), "rescue": rescue}


def finished_reports(events: list[dict], run: dict) -> dict[str, dict]:
    """References to the latest immutable artifacts finished during this launch."""
    launched = run.get("launched_sequence")
    if not launched:
        return {}
    result = {}
    end = run.get("ended_sequence", len(events) + 1)
    for sequence, event in enumerate(events[launched:end - 1], launched + 1):
        if event["op"] == "finish" and event["actor"] == run["resident"]:
            for name, artifact in event["data"]["artifacts"].items():
                result[name] = {"task": event["data"]["task"], "sequence": sequence,
                                "sha256": artifact["sha256"]}
    return result


def recorded_report_changes(workspace: Path, base: str, head: str,
                            journal_artifacts: dict[str, dict]) -> dict[str, dict]:
    """Classify scheduling only; never approve a report's claims or publish it."""
    changes = git(workspace, "diff", "--name-status", "--no-renames", "-z", base, head).split("\0")
    result = {}
    for status, name in zip(changes[0:-1:2], changes[1:-1:2]):
        if (status != "A" or not re.fullmatch(r"evidence/native-residents/[A-Za-z0-9_-]+\.(md|json)", name)
                or name not in journal_artifacts):
            return {}
        entry = git(workspace, "ls-tree", head, "--", name).split("\t", 1)[0].split()
        if len(entry) != 3 or entry[:2] != ["100644", "blob"]:
            return {}
        if int(git(workspace, "cat-file", "-s", entry[2])) > 1000000:
            return {}
        body = subprocess.run(["git", "-C", str(workspace), "cat-file", "blob", entry[2]],
                              check=True, capture_output=True).stdout
        if hashlib.sha256(body).hexdigest() != journal_artifacts[name]["sha256"]:
            return {}
        result[name] = dict(journal_artifacts[name])
    return result


def contribution(workspace: Path, base: str, destination: Path, *,
                 journal_artifacts: dict[str, dict]) -> dict:
    """Capture a standalone candidate commit without changing source or losing work."""
    # Reject symlinks/FIFOs/huge untracked data before Git follows/stages anything.
    capture(Record(workspace))
    changed = git(workspace, "status", "--porcelain", "--untracked-files=all")
    if changed:
        git(workspace, "add", "--all")
        git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Emberhall resident",
            "-c", "user.email=resident@local", "commit", "-m", "Preserve resident contribution")
    head = git(workspace, "rev-parse", "HEAD")
    paths = git(workspace, "diff", "--name-only", base, head).splitlines()
    report = {"base": base, "commit": head, "paths": paths, "status": "pending-review" if paths else "no-changes"}
    recorded = recorded_report_changes(workspace, base, head, journal_artifacts)
    if recorded:
        report.update(status="journal-recorded", journal_artifacts=recorded)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        with temporary.open("w") as output:
            os.chmod(temporary, 0o600)
            output.write(json.dumps(report, indent=2) + "\n")
            output.flush(); os.fsync(output.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return report
