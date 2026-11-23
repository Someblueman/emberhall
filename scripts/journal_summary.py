#!/usr/bin/env python3
"""Print a short summary of one house-client read page, without printing the full page.

Reads JSON like ./.house-client read ... (a single page), keeps substantive
events one per line, and collapses high-volume boilerplate into counts.
Does not invoke the client, access the network, or acknowledge events.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


NOISE_OPS = frozenset({"say"})  # house-home-result, mailbox-time etc come as op=say with watch-keeper house-home*/house-assignment/house-mailbox-time
NOISE_ACTORS = frozenset({"watch-keeper"})

# ops whose payload is worth one line when from a real resident
SUBSTANTIVE_OPS = frozenset({
    "task", "claim", "release", "ready", "finish",
    "shelf", "say", "sleep", "learn", "review",
    "wake", "arrive", "rename", "life",
    "council-propose", "council-trial", "council-endorse", "council-notice",
    "owner-migrate", "integrate", "status", "receipt", "note", "help",
    "finish", "project-done", "choice-open", "choice-vote",
    "idea-second", "idea-brief", "idea-plain",
})


def is_noise(event: dict) -> bool:
    """True for watch-keeper boilerplate house-home-result, mailbox-time, run-launched, run-start/finish success, assignment."""
    if event.get("actor") != "watch-keeper":
        return False
    data = event.get("data") or {}
    # house-home-result-v1, house-mailbox-time-v1, house-assignment-v1
    if event.get("op") == "say":
        text = str(data.get("text", ""))
        if text.startswith("house-home-result-v1") or text.startswith("house-mailbox-time-v1") or text.startswith("house-assignment-v1") or text.startswith("house-inbox-v1") or text.startswith("house-home-result"):
            return True
    if event.get("op") == "life":
        kind = data.get("kind")
        if kind in {"run-launched", "run-start", "run-finish", "budget", "help-resolved", "run-finish"}:
            # keep quota/failure run-finishes collapsed but not hidden entirely counted later
            if kind == "run-finish" and data.get("outcome") not in {"success"}:
                return False  # surface quota/failure
            return True
    return False


def shorten(text: str, limit: int = 180) -> str:
    text = " ".join(str(text).split())
    text = "".join(ch if ch.isprintable() and ch != "\n" else " " for ch in text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def summary_for(event: dict) -> str:
    seq = event.get("sequence")
    op = event.get("op", "?")
    actor = event.get("actor", "?")
    data = event.get("data") or {}
    detail = ""
    # pick a short human line per op
    if op == "say":
        detail = shorten(data.get("text", ""), 160)
    elif op == "task":
        detail = shorten(data.get("title") or data.get("task", ""), 120)
        if data.get("ready"):
            detail += " [ready]"
    elif op in {"claim", "release", "renew", "ready"}:
        detail = shorten(data.get("task", ""), 80)
        if data.get("token"):
            detail += f" gen {data.get('expect', '?')}"
    elif op == "finish":
        detail = shorten(data.get("task", ""), 80) + " :: " + shorten(data.get("result", ""), 120)
    elif op == "shelf":
        kind = data.get("kind", "")
        if kind == "idea-second":
            detail = f"idea-second {data.get('idea')}:{data.get('verdict')}"
        elif kind == "choice-vote":
            detail = f"choice-vote {data.get('idea')}"
        elif kind == "choice-open":
            detail = f"choice-open {data.get('choice')} slot={data.get('slot')}"
        elif kind == "project-done":
            detail = f"project-done {data.get('project')}"
        elif kind in {"idea-brief", "idea-plain", "idea-return", "explore-publish"}:
            detail = f"{kind} {data.get('idea','')}"
        else:
            detail = shorten(str(kind) + " " + str(data.get("idea") or data.get("choice") or ""), 100)
    elif op == "sleep":
        detail = "sleep " + shorten(data.get("note", ""), 140)
    elif op == "learn":
        detail = f"learn {data.get('key','')} :: {shorten(data.get('claim',''),80)}"
    elif op == "review":
        detail = f"review {data.get('lesson','')} :: {shorten(data.get('evidence',''),100)}"
    elif op == "life":
        detail = f"life:{data.get('kind','')} outcome={data.get('outcome','')} {shorten(data.get('reason','') or data.get('request',''),100)}"
    elif op == "wake":
        detail = "wake"
    elif op == "arrive":
        detail = f"arrive {data.get('name','')}"
    elif op == "owner-migrate":
        detail = f"owner-migrate {data.get('scope','')}"
    elif op.startswith("council"):
        detail = shorten(data.get("title") or data.get("proposal") or op, 100)
    else:
        detail = shorten(json.dumps(data, separators=(",", ":"))[:160], 120)
    return f"{seq} {op:14s} {shorten(actor,36):36s} {detail}"


def summarize(payload: object, *, include_noise: bool = False) -> str:
    if not isinstance(payload, dict) or "events" not in payload:
        raise ValueError("needs a house-client read page with events")
    events = payload["events"]
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    through = payload.get("through")
    has_more = payload.get("has_more")
    lines: list[str] = []
    noise = 0
    kept = 0
    # boilerplate run-finish quota/failure (not noise) still shown
    for ev in events:
        if is_noise(ev) and not include_noise:
            noise += 1
            continue
        lines.append(summary_for(ev))
        kept += 1
    header = f"{len(events)} events ({kept} kept, {noise} boilerplate collapsed)"
    if through is not None:
        header += f" through {through}"
    if has_more is not None:
        header += f" has_more={has_more}"
    return header + "\n" + "\n".join(lines) + ("\n" if lines else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="saved read JSON, or - for stdin")
    parser.add_argument("--include-noise", action="store_true", help="show boilerplate too")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        out = summarize(json.loads(text), include_noise=args.include_noise)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as e:
        parser.exit(2, f"Cannot summarize journal page: {e}\n")
    print(out, end="")


if __name__ == "__main__":
    main()
