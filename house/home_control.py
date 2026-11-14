"""Finite owner admission pause: existing residents finish; no quota is changed."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def paused(state: dict, at: float) -> bool:
    return state.get("maintenance", {}).get("admissions", {}).get("until", 0) > at


def apply(state: dict, event: dict) -> None:
    from . import council, maintenance, windows
    from .model import integer, require, string
    maintenance._owner(state, event)
    data = event["data"]
    council.fields(data, {"house", "owner_id", "scope", "approval_sha256",
                          "expect", "seconds", "reason"})
    require(data["scope"] == maintenance.KEEP_MOVING_SCOPE and windows.enabled(state),
            "admission control runtime is not enabled")
    current = state["maintenance"].get("admissions", {})
    require(type(data["expect"]) is int and data["expect"] == current.get("generation", 0),
            "admission generation changed")
    seconds = integer(data, "seconds", 0, 3600)
    reason = string(data, "reason", 2000)
    require(bool(reason.strip()), "admission change needs a reason")
    state["maintenance"]["admissions"] = {
        "generation": data["expect"] + 1, "until": event["at"] + seconds,
        "reason": reason, "actor": event["actor"], "sequence": state["sequence"] + 1}


def main() -> None:
    from . import council, maintenance
    from .owner_upgrade import authenticate_owner
    from .record import Record
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--as", dest="actor", required=True)
    parser.add_argument("--expect", type=int, required=True)
    parser.add_argument("--seconds", type=int, required=True, help="0 resumes; at most 3600")
    parser.add_argument("--reason", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    authenticate_owner()
    record = Record(args.repo)
    state = record.read()[0]
    data = {"house": state["house_id"], "owner_id": council.OWNER_ID,
            "scope": maintenance.KEEP_MOVING_SCOPE,
            "approval_sha256": maintenance.KEEP_MOVING_SHA256,
            "expect": args.expect, "seconds": args.seconds, "reason": args.reason}
    print(json.dumps(record.append("owner-admissions", args.actor, data, args.request), indent=2))


if __name__ == "__main__":
    main()
