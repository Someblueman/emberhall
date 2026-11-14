"""Queue independent reviews and deliver accepted commits, never private drafts."""
from __future__ import annotations

import fcntl
import json
from pathlib import Path
import re
import subprocess

from .life import CONTROLLER
from .model import require

SOURCE_REPOSITORY = "Someblueman/emberhall"  # Current source URL; council history retains the former name.


def enabled(state: dict) -> bool:
    from .maintenance import DELIVERY_SCOPE
    return DELIVERY_SCOPE in state.get("maintenance", {}).get("migrations", {})


def review_result(private: Path, run: str) -> dict | None:
    path = private / run / "integration.json"
    if not path.exists():
        return None
    try:
        result = json.loads(path.read_text())
        candidate = json.loads((private / run / "contribution.json").read_text())
    except (OSError, ValueError):
        return None  # A partial receipt cannot complete review or authorize publication.
    if not isinstance(result, dict) or not isinstance(candidate, dict):
        return None
    if (result.get("run") == run and result.get("contribution") == candidate.get("commit")
            and result.get("status") in {"integrated", "conflict", "tests-failed"}):
        return result
    return None


def queue_review(record, private: Path) -> None:
    from .home import pending_contributions
    state = record.read()[0]
    if not enabled(state):
        return
    requests = state["life"]["requests"]
    if any("review_run" in r and r["status"] in {"pending", "assigned"} for r in requests.values()):
        return  # One review assignment at a time; keep capacity for building.
    candidates = sorted(pending_contributions(private), key=lambda c:
                        (not any(p.startswith("projects/") for p in c["paths"]), c["run"]))
    for candidate in candidates:
        run = candidate["run"]
        item = state["life"]["runs"].get(run)
        if not item or item["status"] != "completed" or review_result(private, run):
            continue
        key = "source-review-" + run
        if key in requests:
            continue
        reason = (
            f"Independently review stopped contribution {run}, commit {candidate['commit']}, "
            f"paths {json.dumps(candidate['paths'])}. You are not its author. "
            "Inspect the actual private contribution and its finished task artifacts before acceptance. "
            "Own no implementation paths for this review. Check correctness, task ownership, privacy, "
            "and relevant acceptance evidence. If acceptable, use your fixed journal channel "
            f"integrate {run} --publish; this tests and merges into shared source. "
            "The coordinator separately pushes accepted commits and records verified remote delivery. "
            "Do not claim publication from local integration. Preserve conflicts and failed checks; "
            "report concrete blockers and request bounded repairs with exclusive file ownership. "
            "If another reviewer already accepted it, replay the receipt rather than repeat tests. "
            "Leave a brief journal handoff and sleep after this bounded review; no redundant report file.")
        record.append("life", CONTROLLER, {"kind": "help", "request": key,
            "review_run": run, "reason": reason}, key)
        return


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          check=True, timeout=60).stdout.strip()


def ancestor(root: Path, earlier: str, later: str) -> bool:
    result = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", earlier, later],
                            capture_output=True, timeout=60)
    require(result.returncode in (0, 1), "source ancestry is unavailable")
    return result.returncode == 0


def accepted_target(record, private: Path, state: dict) -> str | None:
    history = git(record.root, "rev-list", "refs/heads/main").splitlines()
    candidates = []
    for run, item in state["life"]["runs"].items():
        if item["status"] != "completed":
            continue
        result = review_result(private, run)
        if not result or result["status"] != "integrated":
            continue
        require(result.get("actor") in state["residents"] and result["actor"] != item["resident"],
                "accepted source needs an independent resident")
        target = result.get("candidate_head", result.get("canonical_commit"))
        require(isinstance(target, str) and re.fullmatch(r"[0-9a-f]{40}", target),
                "invalid accepted source commit")
        require(target in history, "accepted source is outside main history")
        anchors = [result[key] for key in ("candidate_head", "canonical_commit") if key in result]
        require(all(anchor == target for anchor in anchors), "inconsistent accepted source anchors")
        candidates.append((target, result))
    # Only the newest acceptance can authorize a push. Older historical receipts
    # need not meet today's test-receipt format and must not strand newer work.
    if candidates:
        target, result = min(candidates, key=lambda item: history.index(item[0]))
        if "candidate_head" in result:
            require(result.get("test_exit") == 0 and ancestor(record.root, result["contribution"], target),
                    "accepted source lacks passing tests or contribution ancestry")
        else:
            require(result["actor"] == state.get("council", {}).get("authorized_by"),
                    "curated source requires the recorded owner operator")
        return target
    return None


def approved_remote(root: Path) -> str:
    allowed = {f"https://github.com/{SOURCE_REPOSITORY}", f"https://github.com/{SOURCE_REPOSITORY}.git",
               f"git@github.com:{SOURCE_REPOSITORY}.git"}
    require(git(root, "remote", "get-url", "--all", "origin") in allowed and
            git(root, "remote", "get-url", "--push", "--all", "origin") in allowed,
            "source publication remote differs from the approved repository")
    return SOURCE_REPOSITORY


def deliver(record, private: Path) -> dict | None:
    """A failed/lost push retries the same accepted SHA; never force or push HEAD."""
    state = record.read()[0]
    if not enabled(state):
        return None
    with (private / "integration.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(git(record.root, "symbolic-ref", "HEAD") == "refs/heads/main", "source branch is not main")
        target = accepted_target(record, private, state)
        if target is None:
            return None
        request = "source-delivered-" + target
        if request in state["receipts"]:
            return {"commit": target, "already_recorded": True}
        repository = approved_remote(record.root)
        def remote_head():
            values = git(record.root, "ls-remote", "origin", "refs/heads/main").split()
            require(len(values) == 2 and re.fullmatch(r"[0-9a-f]{40}", values[0])
                    and values[1] == "refs/heads/main", "remote main is unavailable")
            return values[0]
        remote = remote_head()
        if remote != target and not ancestor(record.root, target, remote):
            require(ancestor(record.root, remote, target), "remote main diverged; preserve both histories")
            git(record.root, "push", "origin", target + ":refs/heads/main")
            remote = remote_head()
        require(remote == target or ancestor(record.root, target, remote), "remote delivery was not verified")
        result = {"commit": target, "remote_main": remote, "repository": repository}
        record.append("say", CONTROLLER, {"text": "house-source-delivery-v1 " + json.dumps(result)}, request)
        return result
