#!/usr/bin/env python3
"""Read-only auditor for Emberhall source reviews, integrations, and deliveries."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

LEDGER_REF = "refs/heads/house-ledger"
INTEGRATION_PREFIX = "house-integration-v1 "
DELIVERY_PREFIX = "house-source-delivery-v1 "
ASSIGNMENT_PREFIX = "house-assignment-v1 "
TERMINAL_STATUSES = {"integrated", "rejected", "conflict", "tests-failed"}


def _parse_prefixed_json(text: object, prefix: str) -> dict[str, Any] | None:
    if not isinstance(text, str) or not text.startswith(prefix):
        return None
    try:
        payload = json.loads(text[len(prefix):])
    except (ValueError, TypeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_ledger_events(repo: Path) -> list[dict[str, Any]]:
    ref_check = subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--hash", LEDGER_REF],
        capture_output=True,
        text=True,
        check=False,
    )
    if ref_check.returncode != 0 or not ref_check.stdout.strip():
        raise ValueError(
            f"No {LEDGER_REF} ref found in {repo}; pass --events-file for offline/private inspection."
        )
    head = ref_check.stdout.strip()
    commits = subprocess.run(
        ["git", "-C", str(repo), "rev-list", "--reverse", "--first-parent", head],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    if not commits:
        return []
    queries = "".join(f"{oid}:event.json\n" for oid in commits).encode("utf-8")
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        input=queries,
        capture_output=True,
        check=True,
    )
    raw = proc.stdout
    offset = 0
    events: list[dict[str, Any]] = []
    for seq, _ in enumerate(commits, 1):
        nl = raw.find(b"\n", offset)
        if nl < 0:
            raise ValueError("Unexpected end of git cat-file output")
        header = raw[offset:nl].decode("utf-8", errors="replace").split()
        offset = nl + 1
        if len(header) < 3 or header[1] != "blob":
            raise ValueError(f"Missing event.json blob at sequence {seq}")
        size = int(header[2])
        body = raw[offset:offset + size]
        offset += size + 1  # trailing LF
        event = json.loads(body.decode("utf-8"))
        if isinstance(event, dict):
            event.setdefault("sequence", seq)
            events.append(event)
    return events


def _read_events_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            loaded = json.loads(stripped)
            if isinstance(loaded, list):
                return [item for item in loaded if isinstance(item, dict)]
            if isinstance(loaded, dict) and isinstance(loaded.get("events"), list):
                return [item for item in loaded["events"] if isinstance(item, dict)]
        except ValueError:
            pass
    events: list[dict[str, Any]] = []
    for index, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            item.setdefault("sequence", index)
            events.append(item)
    return events


def build_assay_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize review independence, integration verdicts, and deliveries from journal events."""
    residents: dict[str, dict[str, str]] = {}
    runs: dict[str, dict[str, Any]] = {}
    active_run_by_resident: dict[str, str] = {}
    help_requests: dict[str, dict[str, Any]] = {}
    deliveries: dict[str, dict[str, Any]] = {}
    raw_verdicts: list[dict[str, Any]] = []
    nonterminal_statuses: dict[str, str] = {}
    run_scars: dict[str, str] = {}

    for index, event in enumerate(events, 1):
        seq = event.get("sequence", index)
        at = event.get("at")
        actor = str(event.get("actor") or "")
        op = str(event.get("op") or "")
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        watch = (_parse_prefixed_json(data.get("text"), "house-watch-v1 ")
                 if op == "say" and actor == "watch-keeper" else None)

        if op in {"arrive", "rename"} and actor:
            entry = residents.setdefault(actor, {"name": actor, "agent": "unrecorded"})
            if isinstance(data.get("name"), str) and data["name"].strip():
                entry["name"] = data["name"].strip()

        elif op == "life" or watch is not None:
            if watch is not None:
                data = watch
            kind = data.get("kind")
            if kind == "identity" and actor:
                entry = residents.setdefault(actor, {"name": actor, "agent": "unrecorded"})
                if isinstance(data.get("agent"), str) and data["agent"].strip():
                    entry["agent"] = data["agent"].strip()
            elif kind in {"start", "run-start"}:
                run_id = str(data.get("run") or "")
                resident = str(data.get("resident") or "")
                agent = str(data.get("agent") or ("codex" if data.get("executable") == "codex" else "unrecorded"))
                if resident:
                    res = residents.setdefault(resident, {"name": resident, "agent": agent})
                    if agent and agent != "unrecorded":
                        res["agent"] = agent
                    active_run_by_resident[resident] = run_id
                if run_id:
                    runs[run_id] = {
                        "id": run_id,
                        "resident": resident,
                        "agent": agent,
                        "model": str(data.get("model") or ""),
                        "lane": "review" if data.get("mode") == "review" else "work",
                        "help_request": data.get("help_request"),
                        "finished_tasks": [],
                        "outcome": "running",
                        "started_at": at,
                        "started_sequence": seq,
                    }
            elif kind in {"finish", "run-finish", "recovered-interruption", "execution-result"}:
                run_id = str(data.get("run") or "")
                if run_id in runs:
                    outcome = ("unconfirmed" if kind == "recovered-interruption"
                               else str(data.get("outcome") or "unconfirmed"))
                    runs[run_id]["outcome"] = outcome
                    if outcome in {"failed", "interrupted", "unconfirmed"}:
                        # Like the house body, preserve the first scar even if
                        # a later receipt confirms a different process outcome.
                        run_scars.setdefault(run_id, outcome)
                    resident = runs[run_id].get("resident") or ""
                    if active_run_by_resident.get(resident) == run_id:
                        active_run_by_resident.pop(resident, None)
            elif kind == "help":
                req_id = str(data.get("request") or "")
                review_run = data.get("review_run")
                if req_id and (isinstance(review_run, str) or req_id.startswith("source-review-")):
                    target_run = review_run if isinstance(review_run, str) else req_id[len("source-review-"):]
                    help_requests[req_id] = {
                        "request": req_id,
                        "review_run": target_run,
                        "reason": str(data.get("reason") or ""),
                        "opened_sequence": seq,
                        "opened_at": at,
                        "resolved": False,
                        "resolved_sequence": None,
                        "resolved_reason": None,
                    }
            elif kind == "help-resolved":
                req_id = str(data.get("request") or "")
                if req_id in help_requests:
                    help_requests[req_id]["resolved"] = True
                    help_requests[req_id]["resolved_sequence"] = seq
                    help_requests[req_id]["resolved_reason"] = str(data.get("reason") or "")

        elif op == "finish" and actor:
            run_id = active_run_by_resident.get(actor)
            task_id = data.get("task")
            if run_id and run_id in runs and isinstance(task_id, str) and task_id:
                runs[run_id]["finished_tasks"].append(task_id)

        elif op == "say":
            text = data.get("text")
            if actor == "watch-keeper":
                assign = _parse_prefixed_json(text, ASSIGNMENT_PREFIX)
                if assign and isinstance(assign.get("run"), str) and assign["run"] in runs:
                    run = runs[assign["run"]]
                    if isinstance(assign.get("lane"), str):
                        run["lane"] = assign["lane"]
                    if isinstance(assign.get("help_request"), str):
                        run["help_request"] = assign["help_request"]
                delivery = _parse_prefixed_json(text, DELIVERY_PREFIX)
                if delivery and isinstance(delivery.get("commit"), str):
                    commit = delivery["commit"]
                    deliveries[commit] = {
                        "commit": commit,
                        "remote_main": delivery.get("remote_main"),
                        "repository": delivery.get("repository"),
                        "sequence": seq,
                        "at": at,
                    }
            integ = _parse_prefixed_json(text, INTEGRATION_PREFIX)
            if integ and isinstance(integ.get("run"), str) and isinstance(integ.get("status"), str):
                if integ["status"] in {"reviewed", "prepared"}:
                    nonterminal_statuses[integ["run"]] = integ["status"]
                if integ["status"] not in TERMINAL_STATUSES:
                    continue
                reviewer_id = str(integ.get("actor") or actor)
                raw_verdicts.append({
                    "run": integ["run"],
                    "reviewer": reviewer_id,
                    "status": integ["status"],
                    "base": integ.get("base"),
                    "contribution": integ.get("contribution"),
                    "candidate_head": integ.get("candidate_head"),
                    "reason": integ.get("reason"),
                    "test_scope": integ.get("test_scope"),
                    "test_exit": integ.get("test_exit"),
                    "sequence": seq,
                    "at": at,
                })

    verdicts: list[dict[str, Any]] = []
    verdict_runs: set[str] = set()
    for item in raw_verdicts:
        run_id = item["run"]
        verdict_runs.add(run_id)
        work_run = runs.get(run_id, {})
        author_id = str(work_run.get("resident") or "")
        author_info = residents.get(author_id, {"name": author_id or "unrecorded", "agent": "unrecorded"})
        author_agent = work_run.get("agent") or author_info.get("agent") or "unrecorded"

        reviewer_id = item["reviewer"]
        reviewer_info = residents.get(reviewer_id, {"name": reviewer_id or "unrecorded", "agent": "unrecorded"})
        reviewer_agent = reviewer_info.get("agent") or "unrecorded"

        independent_resident = bool(author_id and reviewer_id and author_id != reviewer_id)
        cross_family = bool(
            author_agent not in ("", "unrecorded")
            and reviewer_agent not in ("", "unrecorded")
            and author_agent != reviewer_agent
        )
        candidate_head = item.get("candidate_head")
        delivery = deliveries.get(candidate_head) if isinstance(candidate_head, str) else None

        verdicts.append({
            **item,
            "author": author_id or None,
            "author_name": author_info["name"] if author_id else "unrecorded",
            "author_agent": author_agent,
            "reviewer_name": reviewer_info["name"],
            "reviewer_agent": reviewer_agent,
            "finished_tasks": list(work_run.get("finished_tasks") or []),
            "independent_resident": independent_resident,
            "cross_family": cross_family,
            "delivered": delivery is not None,
            "remote_main": delivery["remote_main"] if delivery else None,
            "delivery_sequence": delivery["sequence"] if delivery else None,
        })

    pending_reviews: list[dict[str, Any]] = []
    for req in help_requests.values():
        if req["resolved"] or req["review_run"] in verdict_runs:
            continue
        work_run = runs.get(req["review_run"], {})
        author_id = str(work_run.get("resident") or "")
        author_info = residents.get(author_id, {"name": author_id or "unrecorded", "agent": "unrecorded"})
        pending_reviews.append({
            **req,
            "integration_status": nonterminal_statuses.get(req["review_run"]),
            "author": author_id or None,
            "author_name": author_info["name"] if author_id else "unrecorded",
            "author_agent": work_run.get("agent") or author_info.get("agent") or "unrecorded",
            "finished_tasks": list(work_run.get("finished_tasks") or []),
        })

    integrated = [v for v in verdicts if v["status"] == "integrated"]
    by_family: dict[str, dict[str, int]] = {}
    for v in verdicts:
        author_fam = v["author_agent"]
        reviewer_fam = v["reviewer_agent"]
        if author_fam not in ("", "unrecorded"):
            entry = by_family.setdefault(author_fam, {
                "authored_verdicts": 0,
                "reviewed_verdicts": 0,
                "cross_family_reviews": 0,
                "rejections_issued": 0,
            })
            entry["authored_verdicts"] += 1
        if reviewer_fam not in ("", "unrecorded"):
            entry = by_family.setdefault(reviewer_fam, {
                "authored_verdicts": 0,
                "reviewed_verdicts": 0,
                "cross_family_reviews": 0,
                "rejections_issued": 0,
            })
            entry["reviewed_verdicts"] += 1
            if v["cross_family"]:
                entry["cross_family_reviews"] += 1
            if v["status"] != "integrated":
                entry["rejections_issued"] += 1

    failed_runs = sum(outcome == "failed" for outcome in run_scars.values())
    interrupted_runs = sum(outcome == "interrupted" for outcome in run_scars.values())
    unconfirmed_runs = sum(outcome == "unconfirmed" for outcome in run_scars.values())

    summary = {
        "total_verdicts": len(verdicts),
        "integrated": len(integrated),
        "rejected": sum(1 for v in verdicts if v["status"] == "rejected"),
        "conflict": sum(1 for v in verdicts if v["status"] == "conflict"),
        "tests_failed": sum(1 for v in verdicts if v["status"] == "tests-failed"),
        "delivered": sum(1 for v in integrated if v["delivered"]),
        "undelivered_integrated": sum(1 for v in integrated if not v["delivered"]),
        "cross_family_integrated": sum(1 for v in integrated if v["cross_family"]),
        "same_family_integrated": sum(
            1 for v in integrated if not v["cross_family"] and v["author_agent"] != "unrecorded" and v["reviewer_agent"] != "unrecorded"
        ),
        "unrecorded_family_integrated": sum(
            1 for v in integrated if "unrecorded" in (v["author_agent"], v["reviewer_agent"])
        ),
        "pending_reviews": len(pending_reviews),
        "failed_runs": failed_runs,
        "interrupted_runs": interrupted_runs,
        "unconfirmed_runs": unconfirmed_runs,
    }
    return {
        "summary": summary,
        "by_family": dict(sorted(by_family.items())),
        "verdicts": verdicts,
        "pending_reviews": pending_reviews,
    }


def filter_report(
    report: dict[str, Any],
    status: str = "all",
    limit: int = 20,
    family: str | None = None,
) -> dict[str, Any]:
    verdicts = report["verdicts"]
    pending = report["pending_reviews"]
    if family:
        verdicts = [v for v in verdicts if v["author_agent"] == family or v["reviewer_agent"] == family]
        pending = [p for p in pending if p["author_agent"] == family]
    if status == "pending":
        verdicts = []
    elif status == "integrated":
        verdicts = [v for v in verdicts if v["status"] == "integrated"]
        pending = []
    elif status == "undelivered":
        verdicts = [v for v in verdicts if v["status"] == "integrated" and not v["delivered"]]
        pending = []
    elif status == "rejected":
        verdicts = [v for v in verdicts if v["status"] in {"rejected", "conflict", "tests-failed"}]
        pending = []
    if limit > 0:
        verdicts = verdicts[-limit:]
        pending = pending[-limit:]
    return {
        "summary": report["summary"],
        "by_family": report.get("by_family", {}),
        "verdicts": verdicts,
        "pending_reviews": pending,
    }


def _fmt_time(ts: object) -> str:
    if isinstance(ts, (int, float)) and ts > 0:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return "time unknown"


def format_text(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "Emberhall Assay Report",
        f"Verdicts: {s['total_verdicts']} total ({s['integrated']} integrated, {s['rejected']} rejected, "
        f"{s['conflict']} conflict, {s['tests_failed']} tests-failed)",
        f"Delivered: {s['delivered']}/{s['integrated']} integrated · "
        f"Undelivered integrated: {s.get('undelivered_integrated', 0)} · "
        f"Cross-family integrated: {s['cross_family_integrated']}/{s['integrated']} · "
        f"Family unrecorded integrated: {s['unrecorded_family_integrated']} · "
        f"Pending reviews: {s['pending_reviews']}",
        f"Run scars: {s.get('failed_runs', 0)} failed, {s.get('interrupted_runs', 0)} interrupted, "
        f"{s.get('unconfirmed_runs', 0)} unconfirmed",
    ]
    by_family = report.get("by_family") or {}
    if by_family:
        parts = [
            f"{fam} (authored={counts['authored_verdicts']}, reviewed={counts['reviewed_verdicts']}, "
            f"cross={counts['cross_family_reviews']}, rejected={counts['rejections_issued']})"
            for fam, counts in sorted(by_family.items())
        ]
        lines.append("Family cross-review: " + "; ".join(parts))
    if report["pending_reviews"]:
        lines.append("\nPending reviews:")
        for item in report["pending_reviews"]:
            tasks = ", ".join(item["finished_tasks"]) or "unrecorded task"
            lines.append(
                f"  - [{item['integration_status'] or 'awaiting verdict'}] "
                f"{item['review_run']} ({item['author_name']} / {item['author_agent']}) "
                f"tasks=[{tasks}] opened seq {item['opened_sequence']} ({_fmt_time(item['opened_at'])})"
            )
    if report["verdicts"]:
        lines.append("\nIntegration verdicts:")
        for item in report["verdicts"]:
            tasks = ", ".join(item["finished_tasks"]) or "no recorded task"
            pair = f"{item['author_name']} ({item['author_agent']}) -> {item['reviewer_name']} ({item['reviewer_agent']})"
            cross = "cross-family" if item["cross_family"] else "family-unverified/same"
            extra = (
                f"head {str(item['candidate_head'])[:8]} {'delivered' if item['delivered'] else 'local'}"
                if item["status"] == "integrated" and item.get("candidate_head")
                else (item.get("reason") or "")
            )
            lines.append(
                f"  - seq {item['sequence']} [{item['status']}] {item['run']} · {pair} ({cross}) · "
                f"tasks=[{tasks}] · {extra}".rstrip()
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."), help="Git repo containing refs/heads/house-ledger")
    parser.add_argument("--events-file", type=Path, help="Read journal events from a JSON or JSONL file instead of Git")
    parser.add_argument("--status", choices=("all", "pending", "integrated", "undelivered", "rejected"), default="all")
    parser.add_argument("--family", help="Filter verdicts and pending reviews by agent family (e.g. codex, opencode, muse, agy)")
    parser.add_argument("--limit", type=int, default=20, help="Maximum entries per section (0 for all)")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args(argv)

    try:
        events = _read_events_file(args.events_file) if args.events_file else _read_ledger_events(args.repo)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"assay: {error}", file=sys.stderr)
        return 2

    filtered = filter_report(build_assay_report(events), status=args.status, limit=args.limit, family=args.family)
    if args.json:
        print(json.dumps(filtered, indent=2, sort_keys=True))
    else:
        print(format_text(filtered))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
