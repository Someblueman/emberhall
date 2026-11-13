"""Private source rooms and reviewable contributions; never a shared worker index."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from .record import Record
from .resident_client import client
from .watch_recovery import capture, save_rescue, source_head


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def room(record: Record, private: Path, run: str, base: str) -> Path:
    target = private / "residents" / run
    target.parent.mkdir(mode=0o700, exist_ok=True)
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


def contribution(workspace: Path, base: str, destination: Path) -> dict:
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
    destination.write_text(json.dumps(report, indent=2) + "\n")
    destination.chmod(0o600)
    return report
