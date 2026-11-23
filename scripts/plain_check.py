#!/usr/bin/env python3
"""Check whether a task plain sentence is ready to send.

Usage:
    python3 scripts/plain_check.py "A helper tells you whether a task line is ready to send."
    ./.house-client task ... --plain "$PLAIN" ... | python3 -c ...
    printf '%s' "$PLAIN" | python3 scripts/plain_check.py -

The Steward's rule for --plain: one everyday sentence, 30 to 200
characters, saying what a person will notice. No file names, function
names, abbreviations or record numbers. A rejected line costs a full
mailbox round trip; this prints the problems first, locally.

Exit 0 when ready, 1 when problems are found, 2 on usage or read errors.
"""
from __future__ import annotations

import argparse
import re
import sys

EXTENSIONS = (".py", ".md", ".json", ".js", ".css", ".html", ".txt",
              ".yml", ".yaml", ".toml", ".git", ".sh")
RECORD = re.compile(r"(?i)\b(?:seq\s*\d+|#\d+|\d{4,})\b|\b[0-9a-f]{7,}\b")
SHOUT = re.compile(r"\b[A-Z]{2,}\b")


def problems(sentence: str) -> list[str]:
    text = " ".join(sentence.split())
    found: list[str] = []
    if not 30 <= len(text) <= 200:
        found.append(f"length {len(text)} is outside 30 to 200 characters")
    marks = [c for c in text if c in ".!?"]
    if len(marks) != 1 or (text and text[-1] not in ".!?"):
        found.append("needs exactly one sentence")
    if "`" in text:
        found.append("no code spans (backticks)")
    words = text.replace(",", " ").split()
    for word in words:
        stripped = word.rstrip(".!?")
        if "/" in stripped or "\\" in stripped:
            found.append(f"file name {word!r}")
        elif stripped.lower().endswith(EXTENSIONS) and "." in stripped:
            found.append(f"file name {word!r}")
    if RECORD.search(text):
        found.append("no record numbers")
    if SHOUT.search(text):
        found.append("no abbreviations in capitals")
    if text.lower().startswith(("e.g.", "i.e.")) or " e.g." in text or " i.e." in text:
        found.append("no e.g./i.e. abbreviations")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", help="plain sentence, or - for stdin (default stdin)")
    args = parser.parse_args(argv)
    try:
        if args.text is None or args.text == "-":
            text = sys.stdin.read()
        else:
            text = args.text
    except OSError as exc:
        print(f"plain_check: {exc}", file=sys.stderr)
        return 2
    text = text.strip()
    if not text:
        print("plain_check: empty input", file=sys.stderr)
        return 2
    issues = problems(text)
    if issues:
        print("not ready:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
