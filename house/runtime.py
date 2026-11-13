"""Atomic, verified runtime selection; council tests are required after bootstrap."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

from .record import Record, REF
from .model import apply_event
from .wake_policy import active_policy, protected_source, refresh_gate, source_snapshot
from .watch_recovery import prepare_runtime


def selected(record: Record) -> dict:
    private = record.common / "house-home"
    receipt = json.loads((private / "active-runtime.json").read_text())
    path = Path(receipt["entry"])
    if path.parent != private or path.is_symlink() or not path.name.startswith("runtime-"):
        raise ValueError("runtime outside private immutable store")
    if hashlib.sha256(path.read_bytes()).hexdigest() != receipt["runtime_sha256"]:
        raise ValueError("pinned runtime bytes changed")
    return receipt


def activate(record: Record, actor: str, task: str | None = None, run: str | None = None) -> dict:
    private = record.common / "house-home"
    private.mkdir(mode=0o700, exist_ok=True)
    with (private / "runtime.lock").open("a+b") as lock, record.locked():
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = record.read()[0]
        target = private / "active-runtime.json"
        if target.exists():
            if not task or not run:
                raise ValueError("refresh requires a tested later council wake")
            attestation = refresh_gate(record, actor, task, run, record.root)
        else:
            # The sole initial bootstrap is bound to the exact committed source
            # accepted by the recorded, attachment-pinned Steward authorization.
            snapshot = source_snapshot(record.root)
            protected_source(state, snapshot)
            if snapshot["source_head"] != state["wake_policy"]["source_head"]:
                raise ValueError("bootstrap source differs from explicit authorization")
            attestation = {"bootstrap": True, "policy_revision": active_policy(state)["revision"]}
        receipt = prepare_runtime(record, private) | {"attestation": attestation}
        expected_head = attestation.get("source_head", state["wake_policy"]["source_head"])
        if receipt["source_head"] != expected_head:
            raise ValueError("source moved during runtime preparation")
        # Journal intent precedes the atomic pointer. A crash leaves either old
        # valid pointer or new valid pointer, never a partially written archive.
        state, _, head = record.read()
        event = {"op": "say", "actor": actor, "at": max(time.time(), state["at"]),
                 "id": "runtime-activation-" + uuid.uuid4().hex,
                 "data": {"text": "house-runtime-v2 " + json.dumps({
            "source_head": receipt["source_head"], "runtime_sha256": receipt["runtime_sha256"],
            "attestation": attestation}, sort_keys=True)}}
        apply_event(state, event)
        record.git("update-ref", REF, record.commit(event, head), head)
        temporary = private / ("active-runtime-" + uuid.uuid4().hex + ".tmp")
        with temporary.open("x") as output:
            temporary.chmod(0o600)
            json.dump(receipt, output, indent=2)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        directory = os.open(private, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("command", choices=["inspect", "activate"])
    parser.add_argument("--as", dest="actor", default="keeper-01")
    parser.add_argument("--task")
    parser.add_argument("--run")
    args = parser.parse_args()
    try:
        record = Record(args.repo)
        receipt = selected(record) if args.command == "inspect" else activate(record, args.actor, args.task, args.run)
        print(json.dumps(receipt, indent=2))
    except (ValueError, OSError, KeyError) as error:
        print(f"runtime: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
