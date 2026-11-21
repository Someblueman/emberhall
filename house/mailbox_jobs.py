"""A serialized action worker and up to three bounded read-only source inspectors."""
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

from .mailbox import directory, read_json, write_json, parse, MAX_RESPONSE, ERRORS, ID
from .record import Record
from .resident_actions import ACTIONS, execute, known_result
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


def publish_target(record: Record, item: dict) -> str | None:
    """Return the target for a parsed publish request; other actions are not deduped."""
    try:
        args = parse(item["argv"], record.root,
                     workspace_path(record, item["run"]), item["resident"])
    except (*ERRORS, SystemExit):
        return None
    if args.command == "integrate" and args.publish and not args.inspect:
        return args.target
    return None


def publish_owner_precedes(owner: dict, item: dict) -> bool:
    """Running work owns its process; queued work follows one stable order."""
    return owner["id"] != item["id"] and (
        owner["status"] == "running" or (owner["status"] == "queued" and
        (owner["created_at"], owner["id"]) < (item["created_at"], item["id"])))


def pending_publish(record: Record, request: dict, target: str):
    """Find a running or earlier queued publish of the same contribution."""
    matches = []
    for item in jobs(record):
        if (not publish_owner_precedes(item, request) or
                publish_target(record, item) != target):
            continue
        # The worker writes its terminal action response before the coordinator
        # marks job.json done. Once that response exists, retries must not report
        # the acceptance as pending.
        action_result = record.common / "house-home" / "jobs" / item["id"] / "result.json"
        if action_result.exists():
            try:
                response = read(action_result)
            except (OSError, ValueError, TypeError):
                continue
            detail = response.get("result") if isinstance(response, dict) else None
            if not (response.get("ok") is True and isinstance(detail, dict) and
                    detail.get("status") == "in-progress"):
                continue
            # This is an interrupted duplicate response, not an action worker.
            continue
        matches.append(item)
    return min(matches, key=lambda item: (item["status"] != "running",
               item["created_at"], item["id"])) if matches else None


def duplicate_response(record: Record, item: dict, owner: dict):
    """Persist a prompt, nonterminal answer while the original publish is pending."""
    path = record.common / "house-home" / "jobs" / item["id"]
    response = {"ok": True, "result": {
        "status": "in-progress", "contribution": publish_target(record, item),
        "intent": "publish", "existing_job": owner["id"],
        "existing_status": owner["status"], "existing_resident": owner["resident"],
        "note": ("an equivalent publish for this contribution is already queued or running; "
                 "observe its terminal receipt instead of waiting behind it. Queued work is "
                 "cancelled if its requesting run exits before it starts. This answer is "
                 "not a terminal outcome. If that work "
                 "fails or is interrupted, submit a new request id.")}}
    write(path / "result.json", response)
    item.update(status="done", finished_at=time.time(), duplicate_of=owner["id"])
    write(path / "job.json", item)


def remove_result(path: Path):
    with directory(path.parent) as parent:
        try:
            os.unlink(path.name, dir_fd=parent)
            os.fsync(parent)
        except FileNotFoundError:
            pass


def repair_duplicate(record: Record, item: dict) -> bool:
    """Finish or reopen a duplicate admission interrupted between durable writes."""
    path = record.common / "house-home" / "jobs" / item["id"]
    result_path = path / "result.json"
    marker = item.get("duplicate_of")
    response = None
    if result_path.exists():
        try:
            candidate = read(result_path)
        except (OSError, ValueError, TypeError):
            candidate = None
        detail = candidate.get("result") if isinstance(candidate, dict) else None
        if isinstance(detail, dict) and detail.get("status") == "in-progress":
            response = candidate
            marker = marker or detail.get("existing_job")
    if not marker:
        return False
    owner = next((candidate for candidate in jobs(record)
                  if candidate["id"] == marker and publish_owner_precedes(candidate, item)), None)
    target = publish_target(record, item)
    if owner is not None and target is not None and publish_target(record, owner) == target:
        owner_result = record.common / "house-home" / "jobs" / owner["id"] / "result.json"
        if not owner_result.exists():
            if response is None:
                duplicate_response(record, item, owner)
            else:
                detail = response["result"]
                if detail.get("existing_status") != owner["status"]:
                    detail["existing_status"] = owner["status"]
                    write(result_path, response)
                item.update(status="done", finished_at=item.get("finished_at", time.time()),
                            duplicate_of=owner["id"])
                write(path / "job.json", item)
            return True
    # A terminal or missing owner makes an old in-progress answer stale. Clear
    # it before reopening the same exact request for normal serialized work.
    if response is not None or item.get("duplicate_of"):
        remove_result(result_path)
        item.pop("duplicate_of", None)
        item.pop("finished_at", None)
        item["status"] = "queued"
        write(path / "job.json", item)
    return False


def enqueue(record: Record, run: str, argv: list[str], requestid: str) -> str:
    job = hashlib.sha256(requestid.encode()).hexdigest()
    root = record.common / "house-home" / "jobs"
    root.mkdir(mode=0o700, exist_ok=True)
    path = root / job
    path.mkdir(mode=0o700, exist_ok=True)
    metadata = path / "job.json"
    if metadata.exists():
        item = read(metadata)
        if item["run"] != run or item["argv"] != argv or item["requestid"] != requestid:
            raise ValueError("job id reused with different content")
        # A retry must never replace durable process ownership with a duplicate
        # answer, even if another admission was interrupted after its queued write.
        if item["status"] == "running":
            return job
        if repair_duplicate(record, item):
            return job
        if item["status"] == "done":
            return job
    else:
        runtime = Path(getattr(record, "_mailbox_runtime", ""))
        if not runtime.is_file() or runtime.is_symlink():
            raise ValueError("coordinator has no trusted pinned job runtime")
        resident_state = record.read()[0]["life"]["runs"][run]
        item = {"id": job, "run": run, "resident": resident_state["resident"], "argv": argv,
                "requestid": requestid, "runtime": str(runtime),
                "runtime_sha256": hashlib.sha256(runtime.read_bytes()).hexdigest(),
                "status": "queued", "created_at": time.time()}
        write(metadata, item)

    target = publish_target(record, item)
    owner = pending_publish(record, item, target) if target is not None else None
    if owner is not None:
        duplicate_response(record, item, owner)
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


def stop(record: Record, run: str, *, running: bool = True):
    for item in jobs(record):
        if item["run"] == run and (item["status"] == "queued" or
                                   (running and item["status"] == "running")):
            interrupt(record, item)


def lane(record: Record, item: dict) -> str:
    """Reparse the fixed-channel command; never trust a stored lane label."""
    args = parse(item["argv"], record.root, workspace_path(record, item["run"]), item["resident"])
    if args.command not in ACTIONS:
        raise ValueError("not a trusted action command")
    # Looking at a page or reading the house's public site changes nothing, so both share the read-only lane
    # and never wait behind an integration.
    if args.command == "reedbank":
        from .daughter import READ_ONLY
        return "inspection" if args.door in READ_ONLY else "worker"
    return "inspection" if args.command in {"view", "read-site"} or (args.command == "integrate" and args.inspect) else "worker"


# Read-only looks run side by side (Steward, 21 November: "Still can't see anything different really?").
# One inspection at a time took 20 to 60 seconds each; a reviewer asking for ten paths held the lane for up to
# fifteen minutes, and five reviews that afternoon gave up with nothing decided. Inspections change nothing, so
# three may run at once, each holding its own lock; actions that change the house still go one at a time.
SLOTS = {"worker": 1, "inspection": 3}


def tick(record: Record) -> None:
    all_jobs = jobs(record)
    processes = getattr(record, "_mailbox_processes", {})
    running = [item for item in all_jobs if item["status"] == "running"]
    occupied: dict[str, int] = {}
    for item in running:
        name = lane(record, item)
        occupied[name] = occupied.get(name, 0) + 1
        if occupied[name] > SLOTS[name]:
            raise ValueError("more trusted action workers recorded in a lane than it has slots")
    for item in running:
        child = processes.get(item["id"])
        if child is not None and child.poll() is None and time.time() - item["started_at"] < 1200:
            continue
        interrupt(record, item)
        occupied[lane(record, item)] -= 1
    pending = sorted((item for item in all_jobs if item["status"] == "queued"), key=lambda item: (item["created_at"], item["id"]))
    for item in pending:
        try:
            name = lane(record, item)
        except (*ERRORS, SystemExit):
            complete(record, item, {"ok": False, "error": "invalid trusted action command"})
            continue
        if occupied.get(name, 0) >= SLOTS[name]:
            continue
        state = record.read()[0]
        run = state.get("life", {}).get("runs", {}).get(item["run"], {})
        if run.get("status") != "active" or run.get("resident") != item["resident"]:
            complete(record, item, {"ok": False, "error": "requesting resident has stopped"})
            continue
        runtime = Path(item["runtime"])
        if runtime.is_symlink() or not runtime.is_file() or hashlib.sha256(runtime.read_bytes()).hexdigest() != item["runtime_sha256"]:
            complete(record, item, {"ok": False, "error": "trusted action runtime bytes changed before launch"})
            continue
        if start(record, item, name, processes):
            occupied[name] = occupied.get(name, 0) + 1


def start(record: Record, item: dict, name: str, processes: dict) -> bool:
    root = record.common / "house-home" / "jobs"
    for slot in range(SLOTS[name]):
        if launch(record, item, root / ((name if slot == 0 else f"{name}-{slot}") + ".lock"), processes):
            return True
    return False


def launch(record: Record, item: dict, lock_path: Path, processes: dict) -> bool:
    """Start the job under this lock when it is free; False when another worker holds it."""
    root = record.common / "house-home" / "jobs"
    path = root / item["id"]
    with lock_path.open("a+b") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
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
    return True


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
