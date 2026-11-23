#!/usr/bin/env python3
"""Check whether a shelf idea-second payload is ready to send.

Usage:
    python3 scripts/idea_second_check.py '{"kind":"idea-second","idea":"x","verdict":"keep","finding":"...120+..."}'
    printf '%s' "$DATA" | python3 scripts/idea_second_check.py -
    python3 scripts/idea_second_check.py saved-payload.json

The runner rule for an idea check: kind is idea-second, idea names the
shelved idea, verdict is keep or drop, and the finding is at least 120
characters saying what was opened and what was seen. A rejected payload
costs a full mailbox round trip; this prints the problems first, locally.

Exit 0 when ready, 1 when problems are found, 2 on usage or read errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FIELDS = ("kind", "idea", "verdict", "finding")
VERDICTS = ("keep", "drop")


def problems(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]
    found: list[str] = []
    if payload.get("kind") != "idea-second":
        found.append('kind must be "idea-second"')
    idea = payload.get("idea")
    if not isinstance(idea, str) or not idea.strip():
        found.append("idea must be a non-empty string")
    if payload.get("verdict") not in VERDICTS:
        found.append('verdict must be "keep" or "drop"')
    finding = payload.get("finding")
    if not isinstance(finding, str) or len(finding.strip()) < 120:
        found.append("finding must be at least 120 characters")
    extra = sorted(set(payload) - set(FIELDS))
    if extra:
        found.append(f"unexpected field(s): {', '.join(extra)}")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?",
                        help="JSON payload, file path, or - for stdin (default stdin)")
    args = parser.parse_args(argv)
    if args.text is None or args.text == "-":
        try:
            text = sys.stdin.read()
        except OSError as exc:
            print(f"read error: {exc}", file=sys.stderr)
            return 2
    elif args.text.lstrip().startswith("{"):
        text = args.text
    else:
        try:
            text = Path(args.text).read_text(encoding="utf-8")
        except OSError:
            text = args.text
    if not text.strip():
        print("usage error: empty payload", file=sys.stderr)
        return 2
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2
    issues = problems(payload)
    if not issues:
        print("ready")
        return 0
    print("not ready")
    for issue in issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
