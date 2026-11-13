"""Steward-approved additive rules. Mutates only disposable journal projections.

The GitHub adapter authenticates and exhaustively fetches the pinned control issue;
this deterministic layer validates the recorded receipt and enforces the gates.
A raw shell writer is outside the cooperative-resident threat model.
"""
from __future__ import annotations

import math
import re

from .governance import canonical, digest

APPROVED_HOUSE = "9c5a77af-0f1a-4995-8e52-e91c0d814569"
APPROVED_SOURCE_SHA256 = "863718c175674f9e5c1dff7274a6067a1d497928a27e9388ca67162f5875690d"
REPOSITORY = "Someblueman/longhouse"
ISSUE = 1
OWNER_ID = 131497840
WAIT_SECONDS = 86400
SYNC_MAX_AGE = 60
OPS = {"council-authorize", "council-propose", "council-trial", "council-endorse",
       "council-notice", "council-sync", "council-enact"}
RESERVED = {"founding-charter", "ratification-process", "steward-process"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fields(data: dict, names: set[str]) -> None:
    require(isinstance(data, dict) and set(data) == names, "invalid council fields")


def text(data: dict, key: str, limit: int = 20000) -> str:
    value = data.get(key)
    require(isinstance(value, str) and 0 < len(value) <= limit, f"invalid {key}")
    return value


def identifier(data: dict, key: str) -> str:
    value = text(data, key, 100)
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", value) is not None,
            f"invalid {key}")
    return value


def positive_integer(value: object, name: str) -> int:
    require(type(value) is int and 0 < value <= 2**63 - 1, f"invalid {name}")
    return value


def clock(value: object, name: str) -> float:
    require(type(value) in (int, float) and math.isfinite(value) and value > 0,
            f"invalid {name}")
    return value


def binding(data: dict) -> None:
    require(data["repository"] == REPOSITORY and type(data["issue"]) is int
            and data["issue"] == ISSUE, "wrong council control issue")
    if "owner_id" in data:
        require(type(data["owner_id"]) is int and data["owner_id"] == OWNER_ID,
                "wrong Steward identity")


def pending(state: dict, data: dict) -> dict:
    proposal = state["proposals"].get(identifier(data, "proposal"))
    require(proposal is not None and proposal.get("mode") == "rule", "not a council rule proposal")
    require(proposal["status"] == "pending", "proposal is not pending")
    require(proposal["base"] == state["rule_revision"], "stale rule revision")
    return proposal


def render(state: dict, event: dict, target: str) -> None:
    council = state["council"]
    parts = [council["base_charter"]] if council["base_active"] else []
    for rule_id, rule in council["rules"].items():
        if rule["status"] == "active":
            parts.append(f"## Rule {rule_id}: {rule['title']}\n\n{rule['text']}")
    rules = "\n\n".join(parts)
    revision = digest(canonical({"parent": state["rule_revision"], "event": event["id"],
                                 "operation": event["op"], "target": target,
                                 "text": digest(rules)}).decode())
    state.update(rules=rules, rule_revision=revision)


def owner_decision(state: dict, event: dict, comment: dict, command: str, target: str) -> str:
    council = state["council"]
    if command == "VETO":
        proposal = state["proposals"].get(target)
        if proposal and proposal.get("mode") == "rule" and proposal["status"] == "pending":
            proposal.update(status="vetoed", veto={"comment_id": comment["id"],
                            "created_at": comment["created_at"], "recorded_at": event["at"]})
            return "vetoed"
        rule = council["rules"].get(target)
        if rule is None:
            return "veto-retained"
        if rule["status"] != "active":
            return "not-active-rule"
        if comment["created_at"] > rule["enacted_at"]:
            return "post-enactment-use-repeal"
        # A fresh poll cannot make fetching and enactment atomic with GitHub.
        # Honor a pre-enactment veto seen later by undoing only its named rule.
        proposal["veto"] = {"comment_id": comment["id"], "created_at": comment["created_at"],
                            "recorded_at": event["at"]}
    if target == "founding-charter":
        if not council["base_active"]:
            return "already-repealed"
        council["base_active"] = False
    else:
        rule = council["rules"].get(target)
        if rule is None or rule["status"] != "active":
            return "not-active-rule"
        rule.update(status="repealed", repealed_at=event["at"], decision_id=comment["id"])
        state["proposals"][target]["status"] = "repealed"
    render(state, event, target)
    return "late-veto-repealed" if command == "VETO" else "repealed"


def synchronize(state: dict, event: dict) -> None:
    data = event["data"]
    fields(data, {"repository", "issue", "owner_id", "checked_at", "comments"})
    binding(data)
    checked = clock(data["checked_at"], "checked_at")
    require(0 <= event["at"] - checked <= SYNC_MAX_AGE, "sync is future-dated or stale")
    council = state["council"]
    previous = council["last_sync"]
    require(previous is None or checked >= previous["checked_at"], "sync clock moved backwards")
    comments = data["comments"]
    require(isinstance(comments, list) and len(comments) <= 10000, "invalid comments")
    seen = set()
    for comment in comments:
        fields(comment, {"id", "actor_id", "created_at", "body"})
        comment_id = positive_integer(comment["id"], "comment ID")
        positive_integer(comment["actor_id"], "comment actor")
        created = clock(comment["created_at"], "comment clock")
        require(created <= checked, "future comment clock")
        require(isinstance(comment["body"], str) and len(comment["body"]) <= 100000,
                "invalid comment body")
        require(comment_id not in seen, "duplicate comment ID in sync")
        seen.add(comment_id)
        old = council["decisions"].get(str(comment_id))
        if old is not None:
            require(old["comment"] == comment, "previously recorded Steward decision was edited")
            continue
        if comment["actor_id"] != OWNER_ID:
            continue
        # The adapter posts proposal notices through the same GitHub account.
        # Their resident-supplied rule text is quoted material, never an owner
        # command, including after a lost notice receipt before journal acceptance.
        if re.match(r"\A<!-- emberhall-notice [A-Za-z0-9][A-Za-z0-9_-]{0,99} [0-9a-f]{64} -->\n",
                    comment["body"]):
            continue
        matches = [match.groups() for line in comment["body"].splitlines()
                   if (match := re.fullmatch(r"(VETO|REPEAL) ([A-Za-z0-9][A-Za-z0-9_-]{0,99})", line))]
        require(len(matches) <= 1, "one decision per owner comment is required")
        if not matches:
            continue
        command, target = matches[0]
        require(target not in {"ratification-process", "steward-process"},
                "ratification process changes require new Steward authorization")
        outcome = owner_decision(state, event, comment, command, target)
        council["decisions"][str(comment_id)] = {
            "comment": dict(comment), "command": command, "target": target,
            "outcome": outcome, "recorded_at": event["at"]}
    council["last_sync"] = {"checked_at": checked, "recorded_at": event["at"],
                            "sequence": state["sequence"] + 1, "comment_count": len(comments)}


def apply(state: dict, event: dict) -> None:
    """Validate one council operation; discard the entire state on any exception."""
    op, data = event["op"], event["data"]
    require(op in OPS, "unknown council operation")
    at = clock(event["at"], "event clock")
    require(at >= state["at"], "clock moved backwards")
    actor = event["actor"]
    require(actor in state["residents"], "unknown council resident")
    require(state["house_id"] == APPROVED_HOUSE, "Steward approval is for a different house")
    if op == "council-authorize":
        fields(data, {"source_sha256", "source", "repository", "issue", "owner_id"})
        require("council" not in state, "council process already authorized")
        require(data["source_sha256"] == APPROVED_SOURCE_SHA256, "wrong Steward approval source")
        binding(data)
        state["council"] = {"source_sha256": APPROVED_SOURCE_SHA256,
            "source": text(data, "source"), "repository": REPOSITORY, "issue": ISSUE,
            "owner_id": OWNER_ID, "authorized_by": actor, "authorized_at": at,
            "endorsements_required": 2, "veto_window_seconds": WAIT_SECONDS,
            "base_charter": state["rules"], "base_active": True,
            "rules": {}, "decisions": {}, "last_sync": None}
        return
    require("council" in state, "council process is not authorized")
    council = state["council"]
    if op == "council-propose":
        fields(data, {"proposal", "mode", "title", "text", "reason", "base"})
        proposal_id = identifier(data, "proposal")
        require(proposal_id not in RESERVED, "reserved rule ID; process changes need Steward approval")
        require(proposal_id not in state["proposals"], "proposal already exists")
        require(not any(decision["command"] == "VETO" and decision["target"] == proposal_id
                        for decision in council["decisions"].values()),
                "proposal ID was already vetoed by the Steward")
        require(data["mode"] == "rule", "only additive rules may use the council process")
        require(data["base"] == state["rule_revision"], "stale rule revision")
        title = text(data, "title", 200)
        require("\n" not in title and "\r" not in title, "rule title must be one line")
        state["proposals"][proposal_id] = {"mode": "rule", "author": actor, "title": title,
            "text": text(data, "text", 100000), "reason": text(data, "reason"),
            "base": data["base"], "status": "pending", "proposed_at": at,
            "trial": None, "endorsements": {}, "notice": None}
    elif op == "council-trial":
        fields(data, {"proposal", "task", "evidence"})
        proposal = pending(state, data)
        require(proposal["trial"] is None, "trial already recorded")
        task_id = text(data, "task", 100)
        task = state["tasks"].get(task_id)
        require(task is not None and task["status"] == "done" and bool(task.get("artifacts")),
                "trial requires a completed task with immutable artifacts")
        proposal["trial"] = {"task": task_id, "finished_at": task["finished_at"],
            "artifacts": {name: item["sha256"] for name, item in task["artifacts"].items()},
            "evidence": text(data, "evidence"), "actor": actor, "at": at}
    elif op == "council-endorse":
        fields(data, {"proposal", "evidence"})
        proposal = pending(state, data)
        require(proposal["trial"] is not None, "record a trial before endorsement")
        require(actor != proposal["author"], "author cannot independently endorse own rule")
        require(actor not in proposal["endorsements"], "resident already endorsed")
        proposal["endorsements"][actor] = {"evidence": text(data, "evidence"), "at": at}
    elif op == "council-notice":
        fields(data, {"proposal", "repository", "issue", "comment_id", "text_sha256"})
        binding(data)
        proposal = pending(state, data)
        require(proposal["notice"] is None, "public notice already recorded")
        comment_id = positive_integer(data["comment_id"], "notice comment ID")
        require(data["text_sha256"] == digest(proposal["text"]), "notice text hash mismatch")
        require(not any(p.get("notice", {}).get("comment_id") == comment_id
                        for p in state["proposals"].values() if p.get("notice")),
                "notice comment already used")
        proposal["notice"] = {"repository": REPOSITORY, "issue": ISSUE,
                              "comment_id": comment_id, "text_sha256": data["text_sha256"], "at": at}
    elif op == "council-sync":
        synchronize(state, event)
    elif op == "council-enact":
        fields(data, {"proposal"})
        proposal = pending(state, data)
        require(proposal["trial"] is not None, "proposal has no trial")
        require(len(proposal["endorsements"]) >= 2, "two independent endorsements required")
        require(proposal["notice"] is not None, "proposal has no public notice")
        elapsed = proposal["notice"]["at"] + WAIT_SECONDS
        require(at >= elapsed, "full 24-hour veto window has not elapsed")
        sync = council["last_sync"]
        require(sync is not None and 0 <= at - sync["checked_at"] <= SYNC_MAX_AGE,
                "fresh successful Steward sync required")
        require(sync["checked_at"] >= elapsed, "Steward sync predates the end of the veto window")
        proposal_id = data["proposal"]
        council["rules"][proposal_id] = {"title": proposal["title"], "text": proposal["text"],
            "status": "active", "enacted_at": at, "enacted_sequence": state["sequence"] + 1}
        proposal.update(status="enacted", enacted_at=at, enacted_sequence=state["sequence"] + 1)
        render(state, event, proposal_id)
