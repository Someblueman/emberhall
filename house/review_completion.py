"""Review-work completion via a durable terminal integration receipt.

A bounded review task owns no implementation files. Its ordinary ``finish``
cannot complete because no authored artifact exists. This module lets the
live reviewer close that task with a deterministic projection of the exact
terminal integration receipt that already exists for ``review_run``.

The projection omits private candidate and diagnostic fields, keeps the
receipt terminal status distinct, and is stored as the single immutable
``finish`` artifact. Ordinary ``finish`` semantics and historical events
are unchanged.
"""
from __future__ import annotations

import base64
import hashlib
import json
import time
from pathlib import Path

from .record import Record

TERMINAL_STATUSES = frozenset({"integrated", "rejected", "conflict", "tests-failed"})
# Private fields excluded from the journal and from the completion artifact.
_EXCLUDED_FIELDS = frozenset({"candidate", "diagnostics"})


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _artifact_name(task_id: str, review_run: str) -> str:
    # Deterministic fixed path, never caller-supplied.
    return f"evidence/review-completions/{task_id}-{review_run}.json"


def _safe_projection(receipt: dict, task_id: str, review_run: str, reviewer: str) -> dict:
    projection = {
        "format": "emberhall-review-completion-v1",
        "task": task_id,
        "review_run": review_run,
        "reviewer": reviewer,
    }
    # Keep only terminal-receipt fields, never candidate/diagnostics.
    for key in ("run", "contribution", "base", "status", "test_scope", "test_exit",
                "candidate_head", "actor", "reason"):
        if key in receipt and key not in _EXCLUDED_FIELDS:
            projection[key] = receipt[key]
    return projection


def _projection_bytes(projection: dict) -> bytes:
    return (json.dumps(projection, sort_keys=True, allow_nan=False, indent=2) + "\n").encode()


def _load_receipt(record: Record, review_run: str) -> dict:
    path = record.common / "house-home" / review_run / "integration.json"
    _require(path.is_file(), "integration receipt is absent")
    try:
        receipt = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("integration receipt is unreadable") from exc
    _require(isinstance(receipt, dict), "integration receipt is invalid")
    _require(receipt.get("run") == review_run, "integration receipt run mismatch")
    return receipt


def _validate_live_claim(state: dict, task_id: str, resident: str, token: str) -> dict:
    _require(isinstance(task_id, str) and bool(task_id), "invalid review task")
    _require(isinstance(resident, str) and str(resident), "invalid reviewer")
    _require(isinstance(token, str) and str(token), "invalid claim token")
    task = state["tasks"].get(task_id)
    _require(isinstance(task, dict), "review task not found")
    _require(task.get("helper") == "review", "task is not a review task")
    _require(isinstance(task.get("review_run"), str) and task["review_run"],
             "review task lacks typed review_run")
    _require(task.get("status") == "claimed", "review task is not live-claimed")
    _require(task.get("owner") == resident, "review task is not owned by reviewer")
    _require(task.get("token") == token, "review task token mismatch")
    # Mirror the ordinary finish fence: must be unexpired at both clocks.
    now = time.time()
    _require(task.get("until", 0) > now, "review task lease expired")
    _require(task.get("until", 0) > state["at"], "review task lease expired")
    _require(state["residents"].get(resident, {}).get("awake") is True,
             "reviewer must be awake")
    return task


def _validate_receipt_against_source(record: Record, receipt: dict, review_run: str, reviewer: str) -> tuple[str, str]:
    import os
    import re
    import subprocess
    from .integrate import git, source

    # Reuse the trusted source validation: stopped run, identity, author check.
    # The trusted channel already fenced the active run; admitted reflects
    # whether the reviewer is currently in a trusted worker.
    status = receipt.get("status")
    _require(status in TERMINAL_STATUSES,
             "integration receipt is not terminal (prepared/reviewed/absent)")
    admitted = bool(os.environ.get("EMBERHALL_ACTION_JOB"))
    # Like integration replay, a terminal decision can outlive its source room.
    # Existing rooms must still match the durable contribution report.
    _workspace, report = source(record, review_run, reviewer, admitted=admitted,
                                allow_absent_workspace=True)
    # Exact source identity: receipt.base is shared HEAD at review (may advance
    # past contribution source_head), while contribution must match report["commit"].
    base = receipt.get("base")
    _require(isinstance(base, str) and re.fullmatch(r"[0-9a-f]{40}", base) is not None,
             "integration receipt base is invalid")
    contribution = receipt.get("contribution")
    _require(isinstance(contribution, str) and re.fullmatch(r"[0-9a-f]{40}", contribution) is not None,
             "integration receipt contribution is invalid")
    _require(contribution == report["commit"],
             "integration receipt contribution mismatch")
    _require(receipt.get("run") == review_run, "integration receipt run mismatch")
    if status == "integrated":
        anchors = [receipt[key] for key in ("canonical_commit", "candidate_head") if key in receipt]
        _require(
            bool(anchors) and all(
                isinstance(anchor, str) and re.fullmatch(r"[0-9a-f]{40}", anchor) is not None
                and anchor == anchors[0]
                for anchor in anchors
            ),
            "accepted integration receipt anchor is inconsistent",
        )
        head = git(record.root, "rev-parse", "HEAD")
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", anchors[0], head],
            cwd=record.root,
            capture_output=True,
        )
        _require(ancestor.returncode == 0,
                 "accepted contribution is outside current source history")
        if "candidate_head" in receipt:
            contains = subprocess.run(
                ["git", "merge-base", "--is-ancestor", report["commit"], receipt["candidate_head"]],
                cwd=record.root,
                capture_output=True,
            )
            _require(contains.returncode == 0,
                     "accepted contribution is absent from its merge commit")
    # Independent reviewer: author of the stopped contribution cannot close it.
    state = record.read()[0]
    item = state.get("life", {}).get("runs", {}).get(review_run, {})
    author = item.get("resident")
    _require(isinstance(author, str) and reviewer != author,
             "reviewer must be independent of the contribution author")
    # Receipt actor (whoever integrated) must also be independent and terminal.
    # We do not require actor == reviewer: a prior independent acceptance
    # (e.g. a replay) remains valid for this reviewer so long as both are
    # independent; the task fence already proves the current reviewer is
    # independent and awake.
    if "actor" in receipt:
        _require(isinstance(receipt["actor"], str) and receipt["actor"] != author,
                 "integration receipt actor is not independent")
    return base, report["commit"]


def known_result(record: Record, task_id: str, resident: str, token: str, requestid: str) -> dict | None:
    """Recognize a lost-reply completion without re-executing or re-validating."""
    state, events, _ = record.read()
    if not isinstance(requestid, str) or not requestid:
        return None
    if requestid not in state["receipts"]:
        return None
    seq = state["receipts"][requestid]
    event = events[seq - 1]
    _require(event["actor"] == resident, "review completion request belongs to another resident")
    _require(event["op"] == "finish", "review completion request is not a finish")
    data = event["data"]
    _require(data.get("task") == task_id, "review completion request task mismatch")
    _require(data.get("token") == token, "review completion request token mismatch")
    task = state["tasks"].get(task_id, {})
    review_run = task.get("review_run")
    _require(isinstance(review_run, str) and bool(review_run),
             "review task binding is invalid")
    # Verify the bound immutable artifact directly without rereading mutable integration.json.
    artifacts = data.get("artifacts", {})
    _require(len(artifacts) == 1, "review completion must have exactly one artifact")
    name, saved = next(iter(artifacts.items()))
    _require(name == _artifact_name(task_id, review_run),
             "review completion artifact name mismatch")
    stored = base64.b64decode(saved["base64"], validate=True)
    _require(hashlib.sha256(stored).hexdigest() == saved.get("sha256"),
             "review completion artifact drift")
    try:
        projection = json.loads(stored.decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("review completion artifact is unreadable") from exc
    _require(
        isinstance(projection, dict)
        and projection.get("task") == task_id
        and projection.get("review_run") == review_run
        and projection.get("reviewer") == resident,
        "review completion artifact content drift",
    )
    return {"request": requestid, "sequence": seq, "replayed": True,
            "task": task_id, "review_run": review_run, "status": projection.get("status")}


def complete(record: Record, task_id: str, resident: str, token: str, requestid: str) -> dict:
    # Preserve a lost-reply retry before any fence that would see a done task.
    previous = known_result(record, task_id, resident, token, requestid)
    if previous is not None:
        return previous
    # Fresh attempt: strict live-claim and receipt fences.
    state = record.read()[0]
    task = _validate_live_claim(state, task_id, resident, token)
    review_run: str = task["review_run"]
    receipt = _load_receipt(record, review_run)
    _validate_receipt_against_source(record, receipt, review_run, resident)
    # Build the safe immutable projection and close via the ordinary finish
    # transition, preserving historical event semantics.
    projection = _safe_projection(receipt, task_id, review_run, resident)
    body = _projection_bytes(projection)
    _require(len(body) <= 1000000, "review completion projection exceeds bound")
    # No private candidate/diagnostic fields may reach the artifact.
    for key in _EXCLUDED_FIELDS:
        _require(key not in projection, "review completion projection leaks private field")
    name = _artifact_name(task_id, review_run)
    digest = hashlib.sha256(body).hexdigest()
    artifact = {"sha256": digest, "base64": base64.b64encode(body).decode()}
    result = (
        f"Review completed via durable terminal integration receipt for {review_run} "
        f"({receipt['status']}, contribution {receipt['contribution'][:12]}). "
        f"Projection at {name} preserves the exact receipt status without asserting "
        f"source acceptance or project completion."
    )
    receipt_id = record.append("finish", resident,
                               {"task": task_id, "token": token, "result": result,
                                "artifacts": {name: artifact}}, requestid)
    return receipt_id
