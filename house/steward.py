"""The Steward's phone bell and the approved resident council commands."""
from __future__ import annotations

import argparse
import datetime as dt
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

from . import council
from .record import ANCHOR, Record

FOUNDATION = "74339de5dda84c799fe43650ba273a84de31ba8a"
ISSUE_PATH = f"repos/{council.REPOSITORY}/issues/{council.ISSUE}"
BELL_URL = f"https://github.com/{council.REPOSITORY}/issues/{council.ISSUE}"


def github(path: str, payload: dict | None = None) -> tuple[object, float]:
    argv = ["gh", "api", "--include", "--method", "GET" if payload is None else "POST", path]
    if payload is not None:
        argv += ["--input", "-"]
    result = subprocess.run(argv, input=None if payload is None else json.dumps(payload),
                            capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise ValueError("GitHub request failed; no rule can be enacted without a fresh bell check")
    parts = re.split(r"\r?\n\r?\n", result.stdout, maxsplit=1)
    if len(parts) != 2:
        raise ValueError("GitHub response has no verified server date")
    dates = [line.split(":", 1)[1].strip() for line in parts[0].splitlines()
             if line.lower().startswith("date:")]
    if len(dates) != 1:
        raise ValueError("GitHub response must contain one server date")
    checked = parsedate_to_datetime(dates[0]).timestamp()
    if abs(time.time() - checked) > 60:
        raise ValueError("local clock and GitHub server date differ; council remains closed")
    return json.loads(parts[1]), checked


def context() -> None:
    repo, _ = github(f"repos/{council.REPOSITORY}")
    issue, _ = github(ISSUE_PATH)
    if (repo.get("full_name") != council.REPOSITORY
            or repo.get("owner", {}).get("id") != council.OWNER_ID
            or issue.get("number") != council.ISSUE
            or issue.get("html_url") != BELL_URL
            or issue.get("locked") is not False):
        raise ValueError("Steward bell identity or availability changed")


def comments() -> tuple[list[dict], float]:
    result = []
    seen = set()
    for page in range(1, 12):
        batch, checked = github(f"{ISSUE_PATH}/comments?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("invalid GitHub comment page")
        for item in batch:
            comment_id = item.get("id")
            if type(comment_id) is not int or comment_id in seen:
                raise ValueError("invalid or repeated GitHub comment identity")
            seen.add(comment_id)
            if item.get("user", {}).get("id") == council.OWNER_ID:
                result.append(item)
        if len(batch) < 100:
            return result, checked
    raise ValueError("bell exceeds bounded comment scan; no activation performed")


def sync(record: Record, actor: str, request: str | None = None) -> dict:
    context()
    items, checked = comments()
    normalized = [{"id": item["id"], "actor_id": item["user"]["id"],
                   "created_at": dt.datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")).timestamp(),
                   "body": item["body"]} for item in items]
    return record.append("council-sync", actor,
                         {"repository": council.REPOSITORY, "issue": council.ISSUE,
                          "owner_id": council.OWNER_ID, "checked_at": checked,
                          "comments": normalized}, request)


def notice_body(proposal: str, item: dict) -> str:
    sha = hashlib.sha256(item["text"].encode()).hexdigest()
    return (f"<!-- emberhall-notice {proposal} {sha} -->\n"
            f"## Proposed rule: {item['title']}\n\n"
            f"ID: `{proposal}`\n\nAuthor: `{item['author']}`\n\n"
            f"Base revision: `{item['base']}`\n\nText SHA-256: `{sha}`\n\n"
            "The following is the exact proposed rule text:\n\n"
            + item["text"] + "\n\n"
            "The full 24-hour veto window begins only when this notice is accepted in the journal. "
            "Recorded trial evidence and two independent non-author endorsements are also required. "
            f"To veto from your phone, comment `VETO {proposal}` in this issue. "
            "Only the Steward's authenticated account counts. This notice does not enact the rule.\n")


def publish_notice(record: Record, actor: str, proposal: str) -> dict:
    state, _, _ = record.read()
    item = state["proposals"][proposal]
    if item.get("mode") != "rule" or item["status"] != "pending":
        raise ValueError("only a pending named rule can be noticed")
    context()
    body = notice_body(proposal, item)
    marker = body.splitlines()[0]
    items, _ = comments()
    matches = [comment for comment in items if marker in comment["body"]]
    if matches:
        if any(comment["body"] != body for comment in matches):
            raise ValueError("existing notice changed; inspect before retry")
        comment = min(matches, key=lambda value: value["id"])
    else:
        comment, _ = github(f"{ISSUE_PATH}/comments", {"body": body})
    if (comment.get("user", {}).get("id") != council.OWNER_ID
            or comment.get("body") != body or type(comment.get("id")) is not int):
        raise ValueError("notice publication receipt did not match; inspect before retry")
    return record.append("council-notice", actor,
                         {"proposal": proposal, "repository": council.REPOSITORY,
                          "issue": council.ISSUE, "comment_id": comment["id"],
                          "text_sha256": hashlib.sha256(item["text"].encode()).hexdigest()},
                         f"council-notice-{proposal}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--as", dest="actor", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("authorize")
    sub.add_parser("sync")
    sub.add_parser("status")
    propose = sub.add_parser("propose")
    propose.add_argument("proposal")
    propose.add_argument("--title", required=True)
    propose.add_argument("--file", required=True, type=Path)
    propose.add_argument("--reason", required=True)
    for name in ("trial", "endorse", "notice", "enact"):
        action = sub.add_parser(name)
        action.add_argument("proposal")
        if name in ("trial", "endorse"):
            action.add_argument("--evidence", required=True)
        if name == "trial":
            action.add_argument("--task", required=True)
    args = parser.parse_args(argv)
    try:
        record = Record(args.repo)
        state, _, _ = record.read()
        if args.command == "authorize":
            if record.ref(ANCHOR) != FOUNDATION:
                raise ValueError("this approval is pinned to Emberhall's existing foundation")
            context()
            identity, _ = github("user")
            if identity.get("id") != council.OWNER_ID:
                raise ValueError("the authenticated account must be the approved Steward")
            result = record.append("council-authorize", args.actor,
                                   {"source_sha256": council.APPROVED_SOURCE_SHA256,
                                    "source": "Owner-supplied goal-objective.md, attachment 640ada57-3cda-4207-b39f-a325ced64344; preserved in evidence/steward-process/owner-objective.md",
                                    "repository": council.REPOSITORY, "issue": council.ISSUE,
                                    "owner_id": council.OWNER_ID}, "steward-authorization-2026-11-13")
        elif args.command == "sync":
            result = sync(record, args.actor)
        elif args.command == "status":
            result = {"bell": BELL_URL, "council": state.get("council"),
                      "proposals": {k: v for k, v in state["proposals"].items() if v.get("mode") == "rule"}}
        elif args.command == "notice":
            result = publish_notice(record, args.actor, args.proposal)
        elif args.command == "enact":
            # No caller-supplied snapshot: every attempted enactment refreshes the bell.
            sync(record, args.actor)
            result = record.append("council-enact", args.actor, {"proposal": args.proposal},
                                   f"council-enact-{args.proposal}")
        else:
            data = {"proposal": args.proposal}
            if args.command == "propose":
                data.update(mode="rule", title=args.title, text=args.file.read_text(),
                            reason=args.reason, base=state["rule_revision"])
            else:
                data["evidence"] = args.evidence
                if args.command == "trial":
                    data["task"] = args.task
            result = record.append("council-" + args.command, args.actor, data,
                                   f"council-{args.command}-{args.proposal}-{args.actor}")
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error), "bell": BELL_URL}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
