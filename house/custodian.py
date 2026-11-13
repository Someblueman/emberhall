"""One bounded request for an operator-pinned SSH forced-command endpoint."""
from __future__ import annotations

import argparse
import base64
import json
import math
import os
from pathlib import Path
import re
import signal
import sys

from .__main__ import briefing
from .governance import ballot, canonical
from .model import require, string
from .record import ANCHOR, Record

MAX_REQUEST = 8_000_000
MAX_RESPONSE = 16_000_000
BODY_FIELDS = {
    "arrive": {"name"}, "wake": set(), "sleep": {"through", "note"}, "say": {"text"},
    "task": {"task", "title", "description"},
    "claim": {"task", "token", "expect", "seconds"},
    "renew": {"task", "token", "seconds"}, "release": {"task", "token", "note"},
    "finish": {"task", "token", "result", "artifacts"},
    "propose": {"proposal", "base", "text", "reason"},
    "ratify": {"proposal", "signature"},
    "learn": {"lesson", "key", "claim", "evidence"},
    "review": {"lesson", "evidence"}, "supersede": {"old", "new", "evidence"},
}


def fields(value: object, expected: set[str]) -> None:
    require(isinstance(value, dict) and set(value) == expected, "invalid fields")


def unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def finite(value: str) -> float:
    number = float(value)
    require(math.isfinite(number), "nonfinite JSON number")
    return number


def read_page(state: dict, events: list[dict], resident: str, data: dict) -> dict:
    fields(data, {"after", "limit"})
    cursor = data["after"]
    if cursor is None:
        cursor = state["residents"][resident]["cursor"]
    require(type(cursor) is int and 0 <= cursor <= len(events), "invalid read cursor")
    limit = data["limit"]
    require(type(limit) is int and 1 <= limit <= 200, "invalid read limit")
    selected = []
    used = 0
    for sequence, event in enumerate(events[cursor:cursor + limit], cursor + 1):
        body = dict(event["data"])
        if "artifacts" in body:
            body["artifacts"] = {name: {"sha256": item["sha256"]}
                                 for name, item in body["artifacts"].items()}
        item = {**event, "data": body, "sequence": sequence}
        size = len(canonical(item)) + 1
        if used + size > MAX_RESPONSE - 4096:
            break
        selected.append(item)
        used += size
    require(bool(selected) or cursor == len(events), "event exceeds response page budget")
    through = cursor + len(selected)
    return {"through": through, "latest": len(events), "has_more": through < len(events),
            "events": selected}


def handle(record: Record, anchor: str, resident: str, request: dict) -> dict:
    fields(request, {"version", "house", "resident", "request", "action", "data"})
    require(type(request["version"]) is int and request["version"] == 1, "unsupported version")
    require(request["resident"] == resident, "resident binding mismatch")
    request_id = string(request, "request", 200)
    action = string(request, "action", 40)
    data = request["data"]
    require(isinstance(data, dict), "invalid data")
    require(record.ref(ANCHOR) == anchor, "foundation anchor mismatch")
    state, events, head = record.read()
    require(request["house"] == state["house_id"], "house binding mismatch")
    if action in ("verify", "status", "rules"):
        fields(data, set())
        if action == "verify":
            result = {"valid": True, "events": len(events), "head": head,
                      "house": state["house_id"], "rule_revision": state["rule_revision"]}
        elif action == "status":
            result = briefing(state)
        else:
            result = {"revision": state["rule_revision"], "text": state["rules"]}
    elif action == "read":
        result = read_page(state, events, resident, data)
    elif action == "receipt":
        fields(data, {"id"})
        sequence = state["receipts"][string(data, "id", 200)]
        result = {"sequence": sequence, "event": events[sequence - 1]}
    elif action == "ballot":
        fields(data, {"proposal"})
        payload = ballot(state, string(data, "proposal", 100))
        result = {"payload_base64": base64.b64encode(payload).decode()}
    elif action == "append":
        fields(data, {"operation", "body"})
        operation = string(data, "operation", 40)
        require(operation in BODY_FIELDS, "operation is not available to residents")
        fields(data["body"], BODY_FIELDS[operation])
        result = record.append(operation, resident, data["body"], request_id)
    else:
        raise ValueError("action is not available to residents")
    return {"version": 1, "ok": True, "house": state["house_id"], "resident": resident,
            "request": request_id, "result": result}


def deadline(_signal: int, _frame: object) -> None:
    raise TimeoutError("custodian request deadline exceeded")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--expect-anchor", required=True)
    parser.add_argument("--resident", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, deadline)
    code = 0
    try:
        require(1 <= args.timeout <= 120, "invalid deadline")
        signal.alarm(args.timeout)
        require(Path(args.repo).is_absolute(), "operator repo must be absolute")
        require(re.fullmatch(r"[a-f0-9]{40}", args.expect_anchor) is not None, "invalid anchor")
        require(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", args.resident) is not None, "invalid resident")
        require(not os.environ.get("SSH_ORIGINAL_COMMAND"), "remote commands are forbidden")
        # The operator's absolute interpreter/launcher is trusted. Git and SSH
        # executables/configuration must not come from a resident-controlled env.
        for key in list(os.environ):
            if key.startswith("GIT_"):
                del os.environ[key]
        os.environ.update(PATH="/usr/bin:/bin:/usr/sbin:/sbin",
                          GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
        os.umask(0o077)
        raw = sys.stdin.buffer.read(MAX_REQUEST + 1)
        require(0 < len(raw) <= MAX_REQUEST, "invalid request size")
        request = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_float=finite,
                             parse_constant=finite)
        reply = handle(Record(args.repo), args.expect_anchor, args.resident, request)
        output = canonical(reply) + b"\n"
        require(len(output) <= MAX_RESPONSE, "response exceeds limit; request a smaller page")
    except (ValueError, KeyError, OSError, TypeError, RecursionError) as error:
        # TimeoutError is an OSError. Never infer rollback from a lost/late reply.
        output = canonical({"version": 1, "ok": False, "error": str(error)[:2000]}) + b"\n"
        code = 2
    try:
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
    except (BrokenPipeError, TimeoutError):
        # CPython flushes buffered stdout again during shutdown. Redirect only
        # this process's fd so a closed/undrained peer cannot cause a second hang
        # or turn the documented failure status into exit 120.
        sink = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(sink, sys.stdout.fileno())
        finally:
            os.close(sink)
        return 2
    finally:
        signal.alarm(0)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
