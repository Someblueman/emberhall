"""Private source rooms and reviewable contributions; never a shared worker index."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

from .record import Record
from .resident_client import client
from .watch_recovery import FILE_LIMIT, TOTAL_LIMIT, capture, file_identity, save_rescue, source_head
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


FALLBACK_MESSAGE = "Preserve resident contribution"
SUBJECT_LIMIT = 72


def finished_titles(state: dict, events: list[dict], run: dict) -> list[str]:
    """Titles of tasks this run's resident finished during this launch, in finish order."""
    launched = run.get("launched_sequence")
    if not launched:
        return []
    end = run.get("ended_sequence", len(events) + 1)
    titles: list[str] = []
    for event in events[launched:end - 1]:
        if event["op"] == "finish" and event["actor"] == run["resident"]:
            task = state.get("tasks", {}).get(event["data"]["task"], {})
            title = " ".join(str(task.get("title") or event["data"]["task"]).split())
            if title and title not in titles:
                titles.append(title)
    return titles


def contribution_message(titles: list[str]) -> str:
    """A commit message naming the finished work; residents no longer write their own."""
    if not titles:
        return FALLBACK_MESSAGE
    subject = titles[0]
    if len(subject) > SUBJECT_LIMIT:
        subject = subject[:SUBJECT_LIMIT - 3].rstrip() + "..."
    if len(titles) == 1:
        return subject
    return subject + "\n\nAlso finished in this run:\n" + "".join(f"- {t}\n" for t in titles[1:])


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


def _git_bytes(workspace: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(workspace), *args], check=True,
                          capture_output=True).stdout


def _working_changed(workspace: Path) -> list[str]:
    """Changed paths in the working tree versus HEAD, without staging anything.

    Uses diff/ls-files enumeration mirroring watch_recovery.capture so a
    pre-existing room .git/index.lock does not block discovery; status
    porcelain is avoided because it may try to refresh the room index.
    """
    changed: set[str] = set()
    for args in (("diff", "--no-renames", "--name-only", "-z", "HEAD"),
                 ("diff", "--cached", "--no-renames", "--name-only", "-z", "HEAD"),
                 ("ls-files", "--others", "--exclude-standard", "-z")):
        out = _git_bytes(workspace, *args)
        for raw in out.split(b"\0"):
            if raw:
                changed.add(raw.decode("utf-8"))
    return sorted(changed)


def _classify_working(workspace: Path, changed: list[str],
                      journal_artifacts: dict[str, dict]) -> tuple[list[str], list[dict]]:
    """Split working changes into safe-to-commit and excluded with a bounded reason.

    Finish-referenced artifacts are examined first so the total budget cannot
    starve them; the remainder follow in path order. Safety mirrors
    watch_recovery.capture bounds without aborting the whole worktree.
    """
    safe: list[str] = []
    excluded: list[dict] = []
    total = 0
    ordered = sorted(changed, key=lambda p: (p not in journal_artifacts, p))
    for name in ordered:
        path = workspace / name
        unsafe_parent = False
        for parent in path.parents:
            if parent == workspace:
                break
            if parent.is_symlink():
                unsafe_parent = True
                break
        if unsafe_parent:
            excluded.append({"path": name, "reason": "symlink parent"})
            continue
        try:
            before = path.lstat()
        except FileNotFoundError:
            safe.append(name)
            continue
        except OSError:
            excluded.append({"path": name, "reason": "unreadable"})
            continue
        if not stat.S_ISREG(before.st_mode):
            reason = "symlink" if stat.S_ISLNK(before.st_mode) else "not a regular file"
            excluded.append({"path": name, "reason": reason})
            continue
        if before.st_size > FILE_LIMIT:
            excluded.append({"path": name, "reason": "exceeds file limit"})
            continue
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except OSError:
            excluded.append({"path": name, "reason": "unreadable"})
            continue
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                excluded.append({"path": name, "reason": "not a regular file"})
                continue
        finally:
            os.close(descriptor)
        try:
            if file_identity(path.lstat()) != file_identity(before):
                excluded.append({"path": name, "reason": "changed"})
                continue
        except OSError:
            excluded.append({"path": name, "reason": "unreadable"})
            continue
        if total + before.st_size > TOTAL_LIMIT:
            excluded.append({"path": name, "reason": "exceeds total limit"})
            continue
        total += before.st_size
        safe.append(name)
    return sorted(safe), sorted(excluded, key=lambda e: e["path"])


def _commit_safe(workspace: Path, parent: str, safe: list[str], destination: Path,
                 message: str = FALLBACK_MESSAGE) -> tuple[str, bool]:
    """Build the candidate commit with a private temporary index.

    The room index bytes and any pre-existing index.lock stay untouched.
    Returns (head, moved).
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_index = destination.parent / f".contribution-index-{os.getpid()}.tmp"
    temp_index.unlink(missing_ok=True)
    (destination.parent / (temp_index.name + ".lock")).unlink(missing_ok=True)
    env = {**os.environ, "GIT_INDEX_FILE": str(temp_index)}
    try:
        subprocess.run(["git", "-C", str(workspace), "read-tree", parent],
                       check=True, capture_output=True, env=env)
        if safe:
            # -- ends options; literal pathspecs also disable glob/magic matching.
            subprocess.run(["git", "--literal-pathspecs", "-C", str(workspace),
                            "add", "-A", "--", *safe],
                           check=True, capture_output=True, env=env)
        tree = subprocess.run(["git", "-C", str(workspace), "write-tree"],
                              check=True, capture_output=True, env=env,
                              text=True).stdout.strip()
        parent_tree = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", parent + "^{tree}"],
            check=True, capture_output=True, text=True).stdout.strip()
        if tree == parent_tree:
            return parent, False
        commit = subprocess.run(
            ["git", "-C", str(workspace), "-c", "commit.gpgsign=false",
             "-c", "user.name=Emberhall resident", "-c", "user.email=resident@local",
             "commit-tree", tree, "-p", parent, "-m", message],
            check=True, capture_output=True, text=True, env=env).stdout.strip()
        subprocess.run(["git", "-C", str(workspace), "update-ref", "HEAD", commit],
                       check=True, capture_output=True)
        return commit, True
    finally:
        temp_index.unlink(missing_ok=True)
        (destination.parent / (temp_index.name + ".lock")).unlink(missing_ok=True)


def contribution(workspace: Path, base: str, destination: Path, *,
                 journal_artifacts: dict[str, dict], message: str = FALLBACK_MESSAGE) -> dict:
    """Capture a standalone candidate commit without changing source or losing work.

    Safe finished bytes are queued even when unrelated worktree state is
    unsafe/oversized/symlinked or the room index is locked. Unsafe content is
    never committed; each excluded path is recorded with a bounded reason. If
    no safe changed path remains the receipt is explicit ``blocked`` (never
    queued as pending-review) rather than missing. The candidate is built with
    a private temporary index so a resident-created or stale .git/index.lock
    cannot block it and the room index bytes stay untouched.
    watch_recovery.capture stays strict where watch.py depends on it; this
    path filters instead of aborting the whole worktree.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    parent = git(workspace, "rev-parse", "HEAD")
    scan_error: str | None = None
    try:
        working = _working_changed(workspace)
    except (OSError, subprocess.SubprocessError) as exc:
        working = []
        scan_error = f"working-tree-scan-failed: {type(exc).__name__}: {exc}"[:240]
    safe, excluded = _classify_working(workspace, working, journal_artifacts)
    head = parent
    if safe:
        head, _moved = _commit_safe(workspace, parent, safe, destination, message)
    paths_text = git(workspace, "diff", "--name-only", base, head)
    paths = paths_text.splitlines() if paths_text else []
    if paths:
        status = "pending-review"
    elif working or scan_error:
        status = "blocked"
    else:
        status = "no-changes"
    report: dict = {"base": base, "commit": head, "paths": paths, "status": status}
    if excluded:
        report["excluded"] = excluded
    if scan_error:
        report["error"] = scan_error
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
