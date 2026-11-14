"""One durable trusted action worker; native residents keep their sandbox."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from .mailbox import directory, read_json, write_json, MAX_RESPONSE, ERRORS, ID
from .record import Record
from .resident_actions import execute, known_result
from .files import workspace_path
from .watch import group_members, group_stopped, kill_group

LIMIT = MAX_RESPONSE + 300_000
BOOT = "import sys;sys.path.insert(0,sys.argv[1]);from house.mailbox_jobs import main;raise SystemExit(main(sys.argv[2:]))"


def write(path: Path, value: dict):
    with directory(path.parent) as parent:
        write_json(parent, path.name, value, LIMIT)


def read(path: Path):
    with directory(path.parent) as parent:
        return read_json(parent, path.name, LIMIT)


def enqueue(record: Record, run: str, argv: list[str], requestid: str) -> str:
    job = hashlib.sha256(requestid.encode()).hexdigest()
    root = record.common / "house-home" / "jobs"
    root.mkdir(mode=0o700, exist_ok=True)
    path = root / job
    path.mkdir(mode=0o700, exist_ok=True)
    metadata = path / "job.json"
    if metadata.exists():
        existing = read(metadata)
        if existing["run"] != run or existing["argv"] != argv or existing["requestid"] != requestid:
            raise ValueError("job id reused with different content")
        return job
    runtime = Path(getattr(record, "_mailbox_runtime", ""))
    if not runtime.is_file() or runtime.is_symlink():
        raise ValueError("coordinator has no trusted pinned job runtime")
    item = record.read()[0]["life"]["runs"][run]
    write(metadata, {"id": job, "run": run, "resident": item["resident"], "argv": argv,
        "requestid": requestid, "runtime": str(runtime),
        "runtime_sha256": hashlib.sha256(runtime.read_bytes()).hexdigest(),
        "status": "queued", "created_at": time.time()})
    return job


def result(record: Record, job: str):
    path = record.common / "house-home" / "jobs" / job
    metadata = read(path / "job.json")
    return read(path / "result.json") if metadata["status"] == "done" else None


def jobs(record: Record):
    root = record.common / "house-home" / "jobs"
    if not root.exists():
        return []
    return [read(path / "job.json") for path in root.iterdir()
            if ID.fullmatch(path.name) and path.is_dir() and not path.is_symlink() and (path / "job.json").exists()]


def complete(record: Record, item: dict, response: dict):
    path = record.common / "house-home" / "jobs" / item["id"]
    write(path / "result.json", response)
    item.update(status="done", finished_at=time.time())
    write(path / "job.json", item)


def interrupt(record: Record, item: dict):
    path = record.common / "house-home" / "jobs" / item["id"]
    if item.get("pgid"):
        members = group_members(item["pgid"])
        if members and not any(item["id"] in command for command in members):
            raise ValueError("unidentified action worker group; no signal sent")
        if members:
            kill_group(item["pgid"])
        if not group_stopped(item["pgid"]):
            raise ValueError("action worker group has not stopped")
    processes = getattr(record, "_mailbox_processes", {})
    child = processes.pop(item["id"], None)
    if child is not None:
        child.wait(timeout=5)
    if (path / "result.json").exists():
        response = read(path / "result.json")
    else:
        previous = known_result(record, item["resident"], item["run"], item["argv"], item["requestid"])
        response = ({"ok": True, "result": previous} if previous is not None else
                    {"ok": False, "error": "action interrupted without a durable result; inspect preserved state before a new request"})
    complete(record, item, response)


def recover(record: Record):
    for item in jobs(record):
        if item["status"] == "running":
            interrupt(record, item)


def stop(record: Record, run: str):
    for item in jobs(record):
        if item["run"] == run and item["status"] != "done":
            interrupt(record, item)


def tick(record: Record) -> None:
    all_jobs = jobs(record)
    processes = getattr(record, "_mailbox_processes", {})
    running = [item for item in all_jobs if item["status"] == "running"]
    if len(running) > 1:
        raise ValueError("more than one trusted action worker recorded")
    if running:
        item = running[0]
        child = processes.get(item["id"])
        if child is not None and child.poll() is None and time.time() - item["started_at"] < 1200:
            return
        interrupt(record, item)
    pending = sorted((item for item in all_jobs if item["status"] == "queued"), key=lambda item: item["created_at"])
    if not pending:
        return
    item = pending[0]
    state = record.read()[0]
    run = state.get("life", {}).get("runs", {}).get(item["run"], {})
    if run.get("status") != "active" or run.get("resident") != item["resident"]:
        complete(record, item, {"ok": False, "error": "requesting resident has stopped"})
        return
    root = record.common / "house-home" / "jobs"
    path = root / item["id"]
    runtime = Path(item["runtime"])
    if runtime.is_symlink() or not runtime.is_file() or hashlib.sha256(runtime.read_bytes()).hexdigest() != item["runtime_sha256"]:
        complete(record, item, {"ok": False, "error": "trusted action runtime bytes changed before launch"})
        return
    with (root / "worker.lock").open("a+b") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        gate_read, gate_write = os.pipe()
        child = None
        try:
            with (path / "stdout.log").open("ab") as output, (path / "stderr.log").open("ab") as errors:
                os.chmod(output.name, 0o600); os.chmod(errors.name, 0o600)
                child = subprocess.Popen([sys.executable, "-I", "-c", BOOT, item["runtime"],
                    "--repo", str(record.root), "--job", item["id"], "--gate", str(gate_read)],
                    cwd=path, stdin=subprocess.DEVNULL, stdout=output, stderr=errors,
                    start_new_session=True, pass_fds=(gate_read, lock.fileno()))
            item.update(status="running", pgid=child.pid, started_at=time.time())
            write(path / "job.json", item)
            processes[item["id"]] = child
            record._mailbox_processes = processes
            os.write(gate_write, b"go")
        except (OSError, ValueError, subprocess.SubprocessError):
            if child is not None:
                kill_group(child.pid); child.wait()
            complete(record, item, {"ok": False, "error": "trusted action worker failed to launch"})
        finally:
            os.close(gate_read); os.close(gate_write)


def main(argv=None):
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument("--repo", required=True)
    options.add_argument("--job", required=True)
    options.add_argument("--gate", type=int, required=True)
    args = options.parse_args(argv)
    if not ID.fullmatch(args.job) or os.read(args.gate, 2) != b"go":
        return 2
    os.close(args.gate)
    record = Record(args.repo)
    path = record.common / "house-home" / "jobs" / args.job
    item = read(path / "job.json")
    if item["status"] != "running" or item["pgid"] != os.getpid():
        return 2
    try:
        runtime = Path(item["runtime"])
        if runtime.is_symlink() or hashlib.sha256(runtime.read_bytes()).hexdigest() != item["runtime_sha256"]:
            raise ValueError("trusted action runtime bytes changed")
        os.environ["EMBERHALL_ACTION_JOB"] = item["id"]
        value = execute(record, workspace_path(record, item["run"]),
                        item["resident"], item["run"], item["argv"], item["requestid"])
        response = {"ok": True, "result": value}
    except (*ERRORS, subprocess.SubprocessError) as error:
        response = {"ok": False, "error": type(error).__name__ + ": " + str(error)[:300]}
    write(path / "result.json", response)
    return 0
