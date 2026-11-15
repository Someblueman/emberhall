#!/usr/bin/env python3
"""Stdlib checker for Trial Bench JSON reports.

Validates structure and integrity only. It does not judge whether a
prediction was honest or correct: a passing report means the pre-reveal
block still matches the receipt hash, the exposure declaration is
present, and the post-reveal observation is non-empty.

Hash contract (shared with the page script in index.html):
    canonical = JSON of {"exposure":..., "prediction":..., "reasoning":...}
    with sorted keys, compact separators, raw UTF-8, hashed with SHA-256.
The page builds the same object in that key order and uses
crypto.subtle.digest('SHA-256', ...).

Usage:
    python3 checker.py path/to/report.json
Exit 0 = valid, 1 = invalid, 2 = unreadable/invalid JSON/usage.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def compute_receipt_hash(phase1: dict) -> str:
    """Return the SHA-256 hex of the canonical pre-reveal block."""
    canonical = json.dumps(
        {
            "exposure": phase1["exposure"],
            "prediction": phase1["prediction"],
            "reasoning": phase1["reasoning"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_report(report) -> list:
    """Return a list of error strings; empty means valid."""
    errors = []
    if not isinstance(report, dict):
        return ["report must be a JSON object"]

    if report.get("version") != 1:
        errors.append("version must be 1")

    trial_id = report.get("trial_id")
    if not isinstance(trial_id, str) or not trial_id.strip():
        errors.append("trial_id must be a non-empty string")

    phase1 = report.get("phase1")
    if not isinstance(phase1, dict):
        errors.append("phase1 must be an object")
        phase1 = {}

    # Exposure declaration must be present and non-empty. A missing key
    # and an empty/whitespace-only value both fail.
    exposure = phase1.get("exposure")
    if not isinstance(exposure, str) or not exposure.strip():
        errors.append("missing exposure declaration")

    for field in ("prediction", "reasoning"):
        value = phase1.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append("phase1 %s must be a non-empty string" % field)

    receipt = report.get("receipt")
    if not isinstance(receipt, dict):
        errors.append("receipt must be an object")
        receipt = {}
    receipt_hash = receipt.get("hash")
    if not isinstance(receipt_hash, str):
        errors.append("receipt hash must be a string")
    elif len(receipt_hash) != 64 or any(
        c not in "0123456789abcdef" for c in receipt_hash
    ):
        errors.append("receipt hash must be 64 lowercase hex characters")

    phase2 = report.get("phase2")
    if not isinstance(phase2, dict):
        errors.append("phase2 must be an object")
        phase2 = {}
    if "edit" not in phase2 or not isinstance(phase2.get("edit"), str):
        errors.append("phase2 edit must be a string")
    observation = phase2.get("observation")
    if not isinstance(observation, str) or not observation.strip():
        errors.append("observation must be a non-empty string")

    # Integrity: the pre-reveal block in the report must still hash to the
    # receipt. Any later edit of phase1 therefore fails here, as does a
    # tampered receipt hash.
    if (
        isinstance(exposure, str)
        and isinstance(phase1.get("prediction"), str)
        and isinstance(phase1.get("reasoning"), str)
        and isinstance(receipt_hash, str)
        and len(receipt_hash) == 64
        and all(c in "0123456789abcdef" for c in receipt_hash)
    ):
        expected = compute_receipt_hash(phase1)
        if expected != receipt_hash:
            errors.append("hash mismatch: phase1 no longer matches receipt")

    return errors


def main(argv) -> int:
    if len(argv) != 2:
        print("usage: checker.py path/to/report.json", file=sys.stderr)
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print("cannot read report: %s" % exc, file=sys.stderr)
        return 2
    try:
        report = json.loads(text)
    except (ValueError, UnicodeDecodeError) as exc:
        print("invalid JSON: %s" % exc, file=sys.stderr)
        return 2
    errors = validate_report(report)
    if errors:
        for error in errors:
            print("INVALID: %s" % error, file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
