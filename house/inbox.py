"""Read-only authenticated Steward issue bell. Never posts on the owner's behalf."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import time

from .council import OWNER_ID, REPOSITORY
from .life import CONTROLLER
from .record import Record


def pages(path: str) -> list[dict]:
    result = subprocess.run(["gh", "api", "--paginate", "--slurp", path],
                            capture_output=True, text=True, timeout=45, check=True)
    chunks = json.loads(result.stdout)
    if not isinstance(chunks, list) or not all(isinstance(page, list) for page in chunks):
        raise ValueError("unexpected GitHub page format")
    return [item for page in chunks for item in page]


def requests(issues: list[dict], comments: list[dict]) -> list[dict]:
    items = []
    for issue in issues:
        # PR updates and the generated control-issue body aren't wake commands.
        if issue.get("pull_request") or issue.get("number") == 1:
            continue
        items.append(("issue", issue, issue.get("html_url", ""), issue.get("title", "")))
    for comment in comments:
        body = comment.get("body") or ""
        if not isinstance(body, str):
            continue
        if body.startswith("<!-- emberhall-notice ") or body.strip().startswith(("VETO ", "REPEAL ")):
            continue
        items.append(("comment", comment, comment.get("html_url", ""), "Steward's bell"))
    result = []
    for kind, item, url, title in items:
        if item.get("user", {}).get("id") != OWNER_ID:
            continue
        body = item.get("body") or ""
        if type(item.get("id")) is not int or not isinstance(body, str) or not isinstance(title, str):
            continue
        digest = hashlib.sha256((title + "\n" + body).encode()).hexdigest()[:16]
        result.append({"kind": "help", "request": f"github-{kind}-{item['id']}-{digest}",
                       "reason": f"Authenticated Steward issue: {url}\n{title}\n{body}"[:19000]})
    return result


def poll(record: Record) -> dict:
    state, events, _ = record.read()
    # Poll a bounded recent window with idempotent request IDs. Re-fetching the
    # overlap covers edits and clock skew; a missed poll never advances a cursor.
    previous = [e for e in events if e["op"] == "say" and e["actor"] == CONTROLLER
                and e["data"]["text"].startswith("house-inbox-v1 ")]
    started = time.time()
    cursor = json.loads(previous[-1]["data"]["text"].split(" ", 1)[1])["checked_through"] if previous else started - 86400
    since = cursor - 60
    stamp = dt.datetime.fromtimestamp(since, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    issues = pages(f"repos/{REPOSITORY}/issues?state=all&since={stamp}&per_page=100")
    comments = pages(f"repos/{REPOSITORY}/issues/comments?since={stamp}&per_page=100")
    accepted = []
    known = state.get("life", {}).get("requests", {})
    for data in requests(issues, comments):
        if data["request"] not in known:
            record.append("life", CONTROLLER, data, data["request"])
            accepted.append(data["request"])
    # One successful cursor receipt per poll is not needed: only advance hourly
    # or on new work. This avoids filling the journal with empty minutes.
    if accepted or not previous or started - cursor >= 3600:
        record.append("say", CONTROLLER, {"text": "house-inbox-v1 " + json.dumps({
            "accepted": accepted, "checked_through": started})})
    return {"accepted": accepted}
