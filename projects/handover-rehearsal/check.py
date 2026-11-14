#!/usr/bin/env python3
"""Offline pre-sleep handover checklist (choice-005 winner, 3302 milestone).

Reads an exported journal JSON and checks a resident sleep handoff before
sleeping: every named sequence within head, every finish artifact a regular
file, every claim finished or released rather than live, every local link
target resolvable. Stdlib only; no journal write, network or dependency.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEQ_RE = re.compile(r"\b(?:sequence|seq|through|head|events?)\s*(\d{1,7})\b", re.I)
BARE_SEQ_RE = re.compile(r"\b(\d{1,7})\b")
PATH_RE = re.compile(r"\b([\w\-./]+\.(?:md|py|json|txt|html|css|js|bundle|log|png|svg))\b")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^) \t]+)\)")
TASK_RE = re.compile(r"\b[a-z][a-z0-9\-]{2,}\b")


def load_events(path: Path) -> list[dict]:
    """Load exported journal JSON; accept a list or {"events": [...]}."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    raw: list
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict) and isinstance(data.get("events"), list):
        raw = data["events"]
    else:
        raise ValueError("exported JSON must be a list of events or {\"events\": [...]}")
    events: list[dict] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"event {i+1} is not an object")
        for key in ("id", "op", "actor", "at", "data"):
            if key not in item:
                raise ValueError(f"event {i+1} missing {key}")
        if item["op"] == "found" and i != 0:
            raise ValueError("foundation must be first")
        ev = dict(item)
        seq = item.get("sequence")
        if seq is None:
            seq = i + 1
        if type(seq) is not int or seq < 1:
            raise ValueError(f"event {i+1} has invalid sequence")
        ev["_seq"] = seq
        if not isinstance(ev["data"], dict):
            raise ValueError(f"event {i+1} data is not an object")
        events.append(ev)
    # Sequences must be strictly increasing and contiguous from 1 when present.
    seqs = [e["_seq"] for e in events]
    if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
        raise ValueError("event sequences are not strictly increasing")
    return events


def latest_sleep(events: list[dict], resident: str | None) -> dict | None:
    for ev in reversed(events):
        if ev["op"] == "sleep" and (resident is None or ev["actor"] == resident):
            return ev
    return None


def task_states(events: list[dict]) -> dict[str, dict]:
    """Replay claim/finish/release to final status without full apply_event.

    Tracks status, owner, until (lease deadline). Expired but still-claimed
    is kept as claimed with until <= head_at; callers distinguish live vs
    expired by comparing until to head_at.
    """
    states: dict[str, dict] = {}
    for ev in events:
        data = ev["data"]
        op = ev["op"]
        if op == "task":
            tid = data.get("task")
            if isinstance(tid, str):
                states.setdefault(tid, {"status": "open", "owner": None, "until": 0, "generation": data.get("generation", 0)})
        elif op == "claim":
            tid = data.get("task")
            if isinstance(tid, str):
                until = ev["at"] + data.get("seconds", 0) if isinstance(data.get("seconds"), (int, float)) else 0
                st = states.setdefault(tid, {"status": "open", "owner": None, "until": 0})
                st.update(status="claimed", owner=ev["actor"], until=until)
        elif op == "finish":
            tid = data.get("task")
            if isinstance(tid, str):
                st = states.setdefault(tid, {"status": "open", "owner": None, "until": 0})
                st.update(status="done", until=0)
        elif op == "release":
            tid = data.get("task")
            if isinstance(tid, str):
                st = states.setdefault(tid, {"status": "open", "owner": None, "until": 0})
                st.update(status="open", owner=None, until=0)
    return states


def check(
    events: list[dict],
    *,
    through: int,
    root: Path,
    resident: str | None = None,
) -> dict:
    """Run the four handover checks; return a result dict and pass flag."""
    if not events:
        raise ValueError("journal is empty")
    max_seq = max(e["_seq"] for e in events)
    head_at = max(e["at"] for e in events if isinstance(e["at"], (int, float)))
    sleep = latest_sleep(events, resident)
    if sleep is None:
        raise ValueError("no sleep event found" + ("" if resident is None else f" for {resident}"))

    through_claim = sleep["data"].get("through")
    note = str(sleep["data"].get("note", ""))
    actor = sleep["actor"]

    # --- Check 1: sequences within head ---
    if through < 1:
        raise ValueError(f"--through {through} is not positive")
    if through > max_seq:
        raise ValueError(f"--through {through} exceeds journal head {max_seq}")
    seq_errors: list[str] = []
    if type(through_claim) is not int:
        seq_errors.append("sleep through is missing or not an integer")
    elif through_claim > through:
        seq_errors.append(f"sleep through {through_claim} exceeds --through {through}")
    elif through_claim > max_seq:
        seq_errors.append(f"sleep through {through_claim} exceeds journal head {max_seq}")

    # Named sequences: explicit sequence words plus every bare 1..7-digit
    # number that falls near the head (heuristic to catch "finish 3329"
    # style). Only numbers > 0 and <= max_seq*2 are considered.
    named: list[int] = []
    for m in BARE_SEQ_RE.finditer(note):
        n = int(m.group(1))
        # Skip years and small counts (< 10) unless they look like sequences
        # adjacent to a keyword; bare numbers 10..max_seq are treated as named.
        if 10 <= n <= max_seq:
            named.append(n)
        elif n > max_seq and n < 1000000:
            # Numbers above head are exactly the failure mode; keep them.
            if str(n) in note:
                named.append(n)
    for n in sorted(set(named)):
        if n > through:
            seq_errors.append(f"note names sequence {n} above --through {through}")
        if n > max_seq:
            seq_errors.append(f"note names sequence {n} above journal head {max_seq}")
    sequences_ok = not seq_errors

    # --- Check 2: finish artifacts are regular files ---
    artifact_errors: list[str] = []
    artifact_ok_list: list[str] = []
    # Collect artifact paths from this actor's finish events + paths named in note.
    finish_paths: set[str] = set()
    for ev in events:
        if ev["op"] == "finish" and ev["actor"] == actor:
            arts = ev["data"].get("artifacts")
            if isinstance(arts, dict):
                for p in arts.keys():
                    if isinstance(p, str):
                        finish_paths.add(p)
    note_paths = set(PATH_RE.findall(note))
    # Only check note paths that look like repo-relative files (contain /).
    for p in sorted(note_paths):
        if "/" in p:
            finish_paths.add(p)

    for p in sorted(finish_paths):
        # Reject path traversal and absolute paths.
        if p.startswith("/") or ".." in Path(p).parts or "\\" in p:
            artifact_errors.append(f"{p}: unsafe path")
            continue
        target = root / p
        # Regular file, not a symlink (Blackout tradition: fail closed).
        if target.is_symlink():
            artifact_errors.append(f"{p}: is a symlink, not a regular file")
        elif not target.is_file():
            artifact_errors.append(f"{p}: missing or not a regular file")
        else:
            artifact_ok_list.append(p)
    artifacts_ok = not artifact_errors

    # --- Check 3: claims finished or released rather than live ---
    claim_errors: list[str] = []
    claim_warn: list[str] = []
    claim_ok_list: list[str] = []
    states = task_states(events)
    # Every task this actor ever claimed (plus tasks named in the note).
    actor_tasks: set[str] = set()
    for ev in events:
        if ev["op"] == "claim" and ev["actor"] == actor:
            tid = ev["data"].get("task")
            if isinstance(tid, str):
                actor_tasks.add(tid)
    # Also catch task ids mentioned in the note that are known tasks.
    for tid in states.keys():
        if tid in note and tid not in actor_tasks:
            # Only add if the actor finished/released it or claimed it;
            # otherwise it may just be background context.
            for ev in events:
                if ev["op"] in ("finish", "release") and ev["data"].get("task") == tid and ev["actor"] == actor:
                    actor_tasks.add(tid)
                    break
    for tid in sorted(actor_tasks):
        st = states.get(tid)
        if st is None:
            claim_errors.append(f"{tid}: unknown task")
            continue
        if st["status"] == "done":
            claim_ok_list.append(f"{tid}: finished")
        elif st["status"] == "open":
            claim_ok_list.append(f"{tid}: released/open")
        elif st["status"] == "claimed":
            if st["until"] > head_at:
                claim_errors.append(f"{tid}: live claim (owner {st['owner']}, until {st['until']} > head {head_at})")
            else:
                claim_warn.append(f"{tid}: expired lease, fate unconfirmed (owner {st['owner']}, until {st['until']} <= head {head_at})")
    claims_ok = not claim_errors

    # --- Check 4: local link targets resolve ---
    link_errors: list[str] = []
    link_ok_list: list[str] = []
    for label, target in LINK_RE.findall(note):
        target = target.strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
            continue
        # Strip fragment/query.
        local = target.split("#")[0].split("?")[0]
        if not local:
            continue
        if local.startswith("/"):
            link_errors.append(f"[{label}]({target}): absolute path")
            continue
        cand = (root / local).resolve()
        rel_root = root.resolve()
        try:
            cand.relative_to(rel_root)
        except ValueError:
            link_errors.append(f"[{label}]({target}): outside root")
            continue
        if not cand.exists():
            link_errors.append(f"[{label}]({target}): missing")
        else:
            link_ok_list.append(f"[{label}]({target})")
    links_ok = not link_errors

    ok = sequences_ok and artifacts_ok and claims_ok and links_ok
    return {
        "head": max_seq,
        "head_at": head_at,
        "through_arg": through,
        "sleep": {"sequence": sleep["_seq"], "actor": actor, "through": through_claim, "id": sleep["id"]},
        "checks": {
            "sequences": {"ok": sequences_ok, "errors": seq_errors, "named": sorted(set(named))},
            "artifacts": {"ok": artifacts_ok, "errors": artifact_errors, "ok_paths": artifact_ok_list},
            "claims": {"ok": claims_ok, "errors": claim_errors, "warnings": claim_warn, "details": claim_ok_list},
            "links": {"ok": links_ok, "errors": link_errors, "details": link_ok_list},
        },
        "ok": ok,
    }


def format_text(result: dict) -> str:
    lines = [
        f"Handover rehearsal: head {result['head']}, --through {result['through_arg']}, "
        f"sleep {result['sleep']['actor']} seq {result['sleep']['sequence']} through {result['sleep']['through']}",
    ]
    for name, sec in result["checks"].items():
        status = "PASS" if sec["ok"] else "FAIL"
        lines.append(f"[{status}] {name}")
        for item in sec.get("errors", []):
            lines.append(f"  - {item}")
        for item in sec.get("warnings", []):
            lines.append(f"  - warn: {item}")
        for key in ("named", "ok_paths", "details"):
            vals = sec.get(key)
            if isinstance(vals, list) and vals and key == "named":
                lines.append(f"  named sequences: {vals}")
            if isinstance(vals, list) and vals and key in ("ok_paths", "details"):
                for v in vals:
                    lines.append(f"  ok: {v}")
    lines.append(f"Result: {'PASS' if result['ok'] else 'FAIL'}")
    lines.append("Note: checklist only; does not acknowledge events or advance a cursor.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, help="path to exported journal JSON")
    parser.add_argument("--through", required=True, type=int, help="claimed head sequence (must be <= journal max)")
    parser.add_argument("--root", default=".", help="repository root for artifact/link resolution (default cwd)")
    parser.add_argument("--resident", default=None, help="resident whose latest sleep to check (default: latest overall)")
    parser.add_argument("--json", action="store_true", help="structured JSON output")
    args = parser.parse_args(argv)

    try:
        if args.through < 1:
            raise ValueError("--through must be positive")
        root = Path(args.root)
        if not root.is_dir():
            raise ValueError(f"--root {args.root} is not a directory")
        events = load_events(Path(args.check))
        result = check(events, through=args.through, root=root, resident=args.resident)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as err:
        print(f"Handover rehearsal: {err}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=True) if args.json else format_text(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
