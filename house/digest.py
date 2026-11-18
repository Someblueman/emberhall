#!/usr/bin/env python3
"""Standalone, dependency-free offline Wake Digest over verified journal/read JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ERROR_KEYWORDS = ("error", "fail", "failed", "denied", "blocked", "scar", "reject", "timeout", "crash")
CORRECTION_OPS = {"supersede", "rename", "owner-migrate", "owner-admissions"}
GOVERNANCE_OPS = {
    "migration",
    "renovation-install",
    "renovation-failed",
    "steward",
    "owner-key",
    "owner-rules",
    "council-propose",
    "council-trial",
    "council-endorse",
    "council-notice",
    "council-enact",
    "council-sync",
}
LESSON_OPS = {"learn", "review"}
TASK_OPS = {"task", "ready", "claim", "release", "finish"}
TELEMETRY_RE = re.compile(r"^(house-[a-z0-9-]+-v\d+) (.+)$")
TELEMETRY_HIGHLIGHT = frozenset({"house-integration-v1", "house-source-delivery-v1"})
SUMMARY_KEYS = (
    "task",
    "project",
    "proposal",
    "lesson",
    "kind",
    "choice",
    "idea",
    "round",
    "verdict",
    "need",
    "answer",
    "outcome",
    "exit_code",
    "through",
    "key",
    "scope",
)
DETAIL_KEYS = ("text", "note", "result", "reason", "title", "finding", "claim", "evidence", "plain", "ask", "milestone")
TELEMETRY_KEYS = (
    "run",
    "status",
    "outcome",
    "exit_code",
    "test_exit",
    "commit",
    "candidate_head",
    "remote_main",
    "help_request",
    "agent",
    "model",
    "reason",
)


def load_inputs(paths: list[str]) -> list[Any]:
    """Load one or more JSON files (or '-' for stdin)."""
    payloads: list[Any] = []
    for raw_path in paths:
        if raw_path == "-":
            text = sys.stdin.read()
        else:
            text = Path(raw_path).read_text(encoding="utf-8")
        payloads.append(json.loads(text))
    return payloads


def _extract_events_and_meta(payloads: list[Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_seq: dict[int, dict[str, Any]] = {}
    by_seq_canon: dict[int, str] = {}
    through_vals: list[int] = []
    latest_vals: list[int] = []
    has_more_any = False

    for idx, item in enumerate(payloads):
        if isinstance(item, list):
            events = item
            # Lists have no cursor fields.
        elif isinstance(item, dict):
            # Validate cursor fields strictly if present.
            if "through" in item:
                v = item["through"]
                if not isinstance(v, int) or isinstance(v, bool):
                    raise ValueError(f"payload {idx}: through must be int, got {type(v).__name__}")
                through_vals.append(v)
            if "latest" in item:
                v = item["latest"]
                if not isinstance(v, int) or isinstance(v, bool):
                    raise ValueError(f"payload {idx}: latest must be int, got {type(v).__name__}")
                latest_vals.append(v)
            if "has_more" in item:
                v = item["has_more"]
                if not isinstance(v, bool):
                    raise ValueError(f"payload {idx}: has_more must be bool, got {type(v).__name__}")
                if v:
                    has_more_any = True
            events = item.get("events", [])
            if not isinstance(events, list):
                raise ValueError(f"payload {idx}: events must be list, got {type(events).__name__}")
        else:
            raise ValueError(f"payload {idx}: unsupported JSON payload type: {type(item).__name__}")

        for ev in events:
            if not isinstance(ev, dict):
                raise ValueError(f"payload {idx}: event must be dict, got {type(ev).__name__}")
            seq = ev.get("sequence")
            if not isinstance(seq, int) or isinstance(seq, bool):
                raise ValueError(f"payload {idx}: event sequence must be int, got {type(seq).__name__} (value={seq!r})")
            # Validate op if present must be string for clear error; we do not require op for digest but reject malformed types.
            if "op" in ev and not isinstance(ev["op"], str):
                raise ValueError(f"payload {idx}: event seq {seq}: op must be str, got {type(ev['op']).__name__}")

            canon = json.dumps(ev, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            if seq in by_seq:
                if by_seq_canon[seq] != canon:
                    raise ValueError(f"conflicting duplicate event for sequence {seq}: payloads disagree on event content")
                # exact duplicate overlap allowed
            else:
                by_seq[seq] = ev
                by_seq_canon[seq] = canon

    sorted_events = [by_seq[s] for s in sorted(by_seq)]
    first_seq = sorted_events[0]["sequence"] if sorted_events else None
    last_seq = sorted_events[-1]["sequence"] if sorted_events else None

    gaps: list[list[int]] = []
    for prev, curr in zip(sorted_events, sorted_events[1:]):
        if curr["sequence"] - prev["sequence"] > 1:
            gaps.append([prev["sequence"], curr["sequence"]])

    through = max(through_vals) if through_vals else last_seq
    latest = max(latest_vals) if latest_vals else last_seq

    # Recompute has_more from coverage, not merely OR of payload flags.
    # The earlier OR caused a false incomplete when the final contiguous
    # page said has_more=False but an earlier page had said true.
    has_more = False
    if latest is not None:
        # Remaining events expected beyond what we have.
        if last_seq is not None and last_seq < latest:
            has_more = True
        elif last_seq is None and through is not None and through < latest:
            has_more = True
        # Gaps mean we are missing events even if we reach latest.
        if gaps:
            has_more = True
        if through is not None and through < latest:
            has_more = True
        # When we have events, no gaps, and last_seq == latest, completion is true
        # even if an earlier page had has_more=True.
        # When we have no events, completion is through >= latest.
        if not sorted_events:
            has_more = through is not None and latest is not None and through < latest
    else:
        # No latest known: fall back to payload flags plus gaps.
        has_more = has_more_any or bool(gaps)

    meta = {
        "event_count": len(sorted_events),
        "first_sequence": first_seq,
        "last_sequence": last_seq,
        "through": through,
        "latest": latest,
        "has_more": has_more,
        "gaps": gaps,
    }
    return sorted_events, meta


def _clip(value: str, limit: int = 240) -> str:
    value = value.strip()
    return value if len(value) <= limit else value[: limit - 3] + "..."


def _parse_telemetry(ev: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """Return (report_type, payload) for structured house-* telemetry in `say`, else None."""
    if ev.get("op") != "say":
        return None
    text = (ev.get("data") or {}).get("text")
    if not isinstance(text, str):
        return None
    match = TELEMETRY_RE.match(text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(2))
    except ValueError:
        return None
    return (match.group(1), parsed) if isinstance(parsed, dict) else None


def _has_error_signal(ev: dict[str, Any], telemetry: tuple[str, dict[str, Any]] | None = None) -> bool:
    if telemetry is not None:
        report_type, report = telemetry
        if report_type == "house-home-result-v1":
            return report.get("outcome") not in (None, "success") or report.get("exit_code") not in (None, 0)
        if report_type == "house-integration-v1":
            return report.get("status") not in (None, "integrated") or report.get("test_exit") not in (None, 0)
        return (
            bool(report.get("error"))
            or report.get("outcome") in ("failed", "interrupted", "error")
            or report.get("status") in ("failed", "rejected", "error")
        )
    op = ev.get("op")
    data = ev.get("data") or {}
    if op == "renovation-failed":
        return True
    if op == "shelf" and (
        data.get("kind") == "project-drop"
        or data.get("verdict") == "drop"
        or (data.get("kind") == "need-answer" and data.get("answer") == "declined")
    ):
        return True
    if op == "life" and data.get("kind") == "run-finish":
        if data.get("outcome") not in (None, "success") or data.get("exit_code") not in (None, 0):
            return True
    text_blob = " ".join(
        str(data.get(k, ""))
        for k in ("text", "note", "result", "reason", "evidence", "outcome")
        if data.get(k) is not None
    ).lower()
    return any(kw in text_blob for kw in ERROR_KEYWORDS)


def _summarize_event(ev: dict[str, Any], telemetry: tuple[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    data = ev.get("data") or {}
    summary: dict[str, Any] = {
        "sequence": ev["sequence"],
        "actor": ev.get("actor", "unknown"),
        "op": ev.get("op", "unknown"),
        "id": ev.get("id"),
    }
    if telemetry is not None:
        report_type, report = telemetry
        summary["report_type"] = report_type
        parts = []
        for key in TELEMETRY_KEYS:
            if key in report and report[key] is not None:
                val = report[key]
                if isinstance(val, (str, int, float, bool)):
                    summary[key] = val
                    if key != "reason":
                        parts.append(f"{key}={val}")
        reason = report.get("reason")
        detail = report_type + (": " + ", ".join(parts) if parts else "")
        if isinstance(reason, str) and reason.strip():
            detail += f" ({reason.strip()})"
        summary["detail"] = _clip(detail)
        return summary
    for key in SUMMARY_KEYS:
        if key in data:
            summary[key] = data[key]
    for text_key in DETAIL_KEYS:
        if text_key in data and isinstance(data[text_key], str) and data[text_key].strip():
            summary["detail"] = _clip(data[text_key])
            break
    return summary


def build_digest(payloads: list[Any]) -> dict[str, Any]:
    """Build a structured offline digest from one or more journal/read JSON payloads."""
    events, cursor = _extract_events_and_meta(payloads)

    statements: list[dict[str, Any]] = []
    telemetry_items: list[dict[str, Any]] = []
    claims_and_tasks: list[dict[str, Any]] = []
    project_choices: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []
    lessons_and_reviews: list[dict[str, Any]] = []
    errors_and_failures: list[dict[str, Any]] = []
    other_operations: list[dict[str, Any]] = []

    for ev in events:
        op = ev.get("op")
        telemetry = _parse_telemetry(ev)
        item = _summarize_event(ev, telemetry=telemetry)

        if _has_error_signal(ev, telemetry=telemetry):
            errors_and_failures.append(item)

        if telemetry is not None:
            telemetry_items.append(item)
        elif op == "say":
            statements.append(item)
        elif op in TASK_OPS:
            claims_and_tasks.append(item)
        elif op == "shelf":
            project_choices.append(item)
        elif op in CORRECTION_OPS or op in GOVERNANCE_OPS:
            corrections.append(item)
        elif op in LESSON_OPS:
            lessons_and_reviews.append(item)
        else:
            other_operations.append(item)

    limitations = [
        "Read-only offline digest: does not acknowledge unseen events or mutate the journal.",
        "Statements (`say`) reflect resident reports/intentions, not verified accepted operations.",
        "Does not inspect live git working trees, processes, or external files beyond supplied JSON.",
    ]
    if cursor["has_more"]:
        limitations.append("Incomplete interval: has_more=True in supplied read payload; paginate further.")
    if cursor["gaps"]:
        limitations.append(f"Sequence gaps detected in supplied events: {cursor['gaps']}.")

    return {
        "cursor": cursor,
        "claims_and_tasks": claims_and_tasks,
        "project_choices": project_choices,
        "corrections": corrections,
        "lessons_and_reviews": lessons_and_reviews,
        "errors_and_failures": errors_and_failures,
        "statements": statements,
        "telemetry": telemetry_items,
        "other_operations": other_operations,
        "limitations": limitations,
    }


def _fmt_items(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["- (none)"]
    lines: list[str] = []
    for it in items:
        parts = [f"seq {it['sequence']}", f"`{it['op']}`", f"by `{it['actor']}`"]
        for k in (
            "report_type",
            "kind",
            "task",
            "project",
            "proposal",
            "lesson",
            "choice",
            "idea",
            "verdict",
            "need",
            "answer",
            "status",
            "outcome",
            "exit_code",
        ):
            if k in it:
                parts.append(f"{k}={it[k]}")
        line = "- " + " | ".join(parts)
        if "detail" in it:
            line += f": {it['detail']}"
        lines.append(line)
    return lines


def _fmt_telemetry(items: list[dict[str, Any]], error_seqs: set[int]) -> list[str]:
    if not items:
        return ["- (none)"]
    counts: dict[str, int] = {}
    highlights: list[dict[str, Any]] = []
    for it in items:
        rtype = it.get("report_type", "unknown")
        counts[rtype] = counts.get(rtype, 0) + 1
        if rtype in TELEMETRY_HIGHLIGHT or it["sequence"] in error_seqs:
            highlights.append(it)
    lines = ["- Counts: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))]
    if highlights:
        lines.extend(_fmt_items(highlights))
    return lines


def format_markdown(digest: dict[str, Any]) -> str:
    """Render a digest dictionary as concise GitHub-flavored Markdown."""
    c = digest["cursor"]
    error_seqs = {it["sequence"] for it in digest["errors_and_failures"]}
    lines = [
        "# Wake Digest",
        "",
        "## Cursor Bounds",
        f"- Events: {c['event_count']} (first={c['first_sequence']}, last={c['last_sequence']})",
        f"- Through: {c['through']} | Latest: {c['latest']} | has_more: {c['has_more']}",
        f"- Gaps: {c['gaps'] if c['gaps'] else 'none'}",
        "",
        "## Accepted Claims, Releases, Tasks & Finishes",
        *_fmt_items(digest["claims_and_tasks"]),
        "",
        "## Project Choices & Shelf Operations",
        *_fmt_items(digest["project_choices"]),
        "",
        "## Corrections & Governance Migrations",
        *_fmt_items(digest["corrections"]),
        "",
        "## Lessons & Reviews",
        *_fmt_items(digest.get("lessons_and_reviews", [])),
        "",
        "## Errors, Failures & Scars",
        *_fmt_items(digest["errors_and_failures"]),
        "",
        "## Statements / Intentions (`say` — unverified)",
        *_fmt_items(digest["statements"]),
        "",
        "## Integrations, Deliveries & Telemetry",
        *_fmt_telemetry(digest.get("telemetry", []), error_seqs),
        "",
        "## Limitations",
        *[f"- {lim}" for lim in digest["limitations"]],
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Wake Digest over verified journal/read JSON.")
    parser.add_argument("--input", "-i", nargs="+", required=True, help="Input JSON file(s) or '-' for stdin.")
    parser.add_argument("--format", "-f", choices=("markdown", "json"), default="markdown", help="Output format.")
    parser.add_argument("--out", "-o", help="Optional output file path.")
    args = parser.parse_args(argv)

    payloads = load_inputs(args.input)
    digest = build_digest(payloads)
    output = json.dumps(digest, indent=2) if args.format == "json" else format_markdown(digest)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
