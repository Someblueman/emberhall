"""Bounded scheduled wakes; the house journal is the quota and outcome record."""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

from .model import apply_event
from .record import Record, REF
from .watch_recovery import (capture, launcher, prepare_runtime, prompt_bytes,
                             save_rescue, source_head, verify_rescue)

ACTOR = "watch-keeper"
PREFIX = "house-watch-v1 "
MAX_STARTS = 12
MAX_SECONDS = 1200
DEFAULT_CODEX = "/Users/sws/.local/bin/codex"
TERMINAL = {"finish", "recovered-interruption"}


def local_day(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp).astimezone().date().isoformat()


def entries(events: list[dict]) -> list[dict]:
    result = []
    for sequence, event in enumerate(events, 1):
        text = event["data"].get("text", "")
        if event["op"] == "say" and event["actor"] == ACTOR and text.startswith(PREFIX):
            item = json.loads(text[len(PREFIX):])
            result.append({**item, "at": event["at"], "sequence": sequence})
    return result


def message(kind: str, run: str, **fields) -> dict:
    return {"text": PREFIX + json.dumps({"kind": kind, "run": run, **fields}, sort_keys=True)}


def emit(record: Record, kind: str, run: str, **fields) -> dict:
    record.append("say", ACTOR, message(kind, run, **fields), f"watch-{run}-{kind}")
    return {"kind": kind, "run": run, **fields}


def private_root(record: Record) -> Path:
    path = record.common / "house-watch"
    path.mkdir(mode=0o700, exist_ok=True)
    path.chmod(0o700)
    return path


def admission_state(record: Record, state: dict, history: list[dict], now: float) -> tuple:
    if any(task["status"] == "claimed" and task["until"] > now
           for task in state["tasks"].values()):
        return "live-task-claim", None
    if not record.git("status", "--porcelain", "--untracked-files=all").strip():
        return None, None
    previous = next((item for item in reversed(history) if item["kind"] == "start"), None)
    rescue = next((item for item in reversed(history) if previous and
                   item["kind"] == "rescue" and item["run"] == previous["run"]), None)
    if not rescue:
        return "dirty-checkout", None
    try:
        payload = capture(record)
        if payload and verify_rescue(record.common / "house-watch", rescue, payload):
            return None, {**rescue, "resident": previous["resident"]}
    except (OSError, ValueError, subprocess.SubprocessError):
        return "rescue-unavailable", None
    return "dirty-checkout-changed-after-rescue", None


def preserve_work(record: Record, run: str) -> None:
    history = [item for item in entries(record.read()[1]) if item["run"] == run]
    if any(item["kind"] in {"rescue", "rescue-blocked"} for item in history):
        return
    start = next(item for item in history if item["kind"] == "start")
    if "source_head" not in start:
        return  # No clean admission witness: old/unattributed work remains blocked.
    try:
        rescue = save_rescue(record, private_root(record), run)
        if rescue:
            emit(record, "rescue", run, **rescue)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        emit(record, "rescue-blocked", run, reason=type(error).__name__)


def inspect(record: Record) -> dict:
    state, events, head = record.read()
    now = time.time()
    history = entries(events)
    starts = [item for item in history if item["kind"] == "start"]
    ended = {item["run"] for item in history if item["kind"] in TERMINAL}
    reason, rescue = admission_state(record, state, history, now)
    return {"house": state["house_id"], "head": head, "local_day": local_day(now),
            "starts_today": sum(item["local_day"] == local_day(now) for item in starts),
            "daily_limit": MAX_STARTS, "deadline_seconds": MAX_SECONDS,
            "pending": [item["run"] for item in starts if item["run"] not in ended],
            "blocked": reason, "recoverable_run": rescue["run"] if rescue else None,
            "recent": history[-12:]}


def admit(record: Record, run: str, seconds: float, prompt: Path, codex: str) -> dict:
    # Check ownership and budget against exactly the head that accepts the start.
    with record.locked():
        state, events, head = record.read()
        wall_time = time.time()
        now = max(wall_time, state["at"])
        day = local_day(wall_time)
        reason, rescue = admission_state(record, state, entries(events), now)
        count = sum(item["kind"] == "start" and item["local_day"] == day
                    for item in entries(events))
        if not reason and count >= MAX_STARTS:
            reason = "daily-limit"
        kind = "skip" if reason else "start"
        fields = {"reason": reason} if reason else {
            "local_day": day, "deadline_at": wall_time + seconds,
            "seconds": seconds, "prompt": str(prompt.relative_to(record.root)),
            "executable": Path(codex).name, "source_head": source_head(record),
            "resident": "watch-" + run, "clean_admission": rescue is None}
        if rescue and not reason:
            fields.update(recover_from=rescue["run"], prior_resident=rescue["resident"],
                          rescue_commit=rescue["commit"], rescue_fingerprint=rescue["fingerprint"])
        event = {"id": f"watch-{run}-{kind}", "op": "say", "actor": ACTOR,
                 "at": now, "data": message(kind, run, **fields)}
        apply_event(state, event)
        oid = record.commit(event, head)
        record.git("update-ref", REF, oid, head)
        return {"kind": kind, "run": run, **fields}


def group_members(pgid: int) -> list[str]:
    result = subprocess.run(["ps", "-axo", "pgid=,stat=,command="],
                            capture_output=True, text=True, check=True)
    members = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3 and parts[0] == str(pgid) and not parts[1].startswith("Z"):
            members.append(parts[2])
    return members


def kill_group(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def group_stopped(pgid: int) -> bool:
    for _ in range(40):
        if not group_members(pgid):
            return True
        time.sleep(0.05)
    return False


def recover(record: Record) -> str | None:
    history = entries(record.read()[1])
    finished = {item["run"] for item in history if item["kind"] in TERMINAL}
    for start in (item for item in history if item["kind"] == "start"):
        run = start["run"]
        if run in finished:
            continue
        launched = next((item for item in history
                         if item["run"] == run and item["kind"] == "launched"), None)
        if launched:
            members = group_members(launched["pgid"])
            # Never signal an unrelated process after PID reuse. The gate and Codex
            # argv both carry this unique run ID (Codex's private final-file path).
            if members and not any(run in command for command in members):
                return "unidentified-process-group"
            if members:
                kill_group(launched["pgid"])
                if not group_stopped(launched["pgid"]):
                    return "process-group-still-running"
        preserve_work(record, run)
        observed = next((item for item in history
                         if item["run"] == run and item["kind"] == "execution-result"), None)
        if observed is not None:
            emit(record, "finish", run, outcome=observed["outcome"],
                 exit_code=observed["exit_code"], recovered=True)
        else:
            emit(record, "recovered-interruption", run,
                 reason="supervisor-ended-without-finish")
    return None


def worker(record: Record, run: str, fd: int, codex: str, prompt: Path,
           deadline: float) -> int:
    # fd is inherited from the launcher. Its shared flock survives launcher death.
    private = private_root(record)
    inherited = os.fstat(fd)
    expected = (private / "runner.lock").stat()
    if (inherited.st_dev, inherited.st_ino) != (expected.st_dev, expected.st_ino):
        raise ValueError("worker requires inherited runner lock")
    history = [item for item in entries(record.read()[1]) if item["run"] == run]
    if len(history) != 1 or history[0]["kind"] != "start":
        raise ValueError("worker requires a fresh journal start")
    seconds = history[0]["seconds"]
    if not 0 < seconds <= MAX_SECONDS or not math.isfinite(deadline):
        raise ValueError("invalid worker deadline")
    deadline = min(deadline, time.monotonic() + seconds)
    path = private / run
    path.mkdir(mode=0o700)
    for name in ("events.jsonl", "stderr.log", "final.txt"):
        descriptor = os.open(path / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
    gate_read, gate_write = os.pipe()
    child = None
    outcome, code = "launch-failed", None
    try:
        prompt_bytes(record, prompt, private, history[0])
        with (path / "prompt.txt").open("rb") as source, (path / "events.jsonl").open("ab") as output, \
                (path / "stderr.log").open("ab") as errors:
            entry, location = launcher()
            argv = [*entry, "--repo", str(record.root),
                    "_exec", "--gate", str(gate_read), "--run-id", run,
                    "--codex", codex, "--final", str(path / "final.txt")]
            child = subprocess.Popen(argv, cwd=location, stdin=source, stdout=output,
                                     stderr=errors, start_new_session=True, pass_fds=(gate_read,))
            os.close(gate_read)
            gate_read = -1
            # The child cannot exec Codex until its group is recoverable in Git.
            emit(record, "launched", run, pgid=child.pid)
            if local_day(time.time()) != history[0]["local_day"]:
                raise ValueError("civil day changed before launch")
            if (time.monotonic() >= deadline or
                    time.time() >= history[0]["deadline_at"]):
                kill_group(child.pid)
                child.wait()
                outcome = "timeout"
                emit(record, "timeout", run)
                raise TimeoutError("launch deadline elapsed")
            os.write(gate_write, b"go")
            os.close(gate_write)
            gate_write = -1
            try:
                while True:
                    remaining = min(deadline - time.monotonic(),
                                    history[0]["deadline_at"] - time.time())
                    try:
                        code = child.wait(timeout=max(0, min(remaining, 1)))
                        break
                    except subprocess.TimeoutExpired:
                        if remaining <= 1:
                            raise
                outcome = "success" if code == 0 else "child-failed"
            except subprocess.TimeoutExpired:
                kill_group(child.pid)
                child.wait()
                outcome = "timeout"
                emit(record, "timeout", run)
            finally:
                # Also remove background descendants after a successful CLI exit.
                kill_group(child.pid)
                child.wait()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        # Exception messages can contain sensitive tool paths/content; keep them local.
        with (path / "stderr.log").open("a") as errors:
            errors.write(f"watch supervisor: {type(error).__name__}\n")
        if child is not None:
            kill_group(child.pid)
            child.wait()
    finally:
        for pipe in (gate_read, gate_write):
            if pipe >= 0:
                os.close(pipe)
    # A known CLI result is not proof that descendants stopped. Preserve it
    # before the bounded cleanup check so recovery need not invent an outcome.
    emit(record, "execution-result", run, outcome=outcome, exit_code=code)
    if child is not None and not group_stopped(child.pid):
        print(json.dumps({"stage": "cleanup-pending", "run": run,
                          "pgid": child.pid}), file=sys.stderr, flush=True)
        return 1  # No terminal receipt while a member could still be running.
    preserve_work(record, run)
    emit(record, "finish", run, outcome=outcome, exit_code=code)
    return 0 if outcome == "success" else 1


def run_watch(record: Record, codex: str = DEFAULT_CODEX,
              prompt: str = "docs/WATCH_PROMPT.md", seconds: float = MAX_SECONDS) -> dict:
    if not math.isfinite(seconds) or not 0 < seconds <= MAX_SECONDS:
        raise ValueError("deadline must be positive and at most 1200 seconds")
    prompt_path = (record.root / prompt).resolve()
    prompt_path.relative_to(record.root)
    if not os.path.isabs(codex):
        raise ValueError("Codex executable must be an absolute path")
    record.append("arrive", ACTOR, {"name": "Watch keeper"}, "watch-keeper-arrival-v1")
    path = private_root(record)
    run = uuid.uuid4().hex
    with (path / "runner.lock").open("a+b") as lock:
        os.chmod(path / "runner.lock", 0o600)
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return emit(record, "skip", run, reason="active-run")
        reason = recover(record)
        if reason:
            return emit(record, "skip", run, reason=reason)
        decision = admit(record, run, seconds, prompt_path, codex)
        if decision["kind"] == "skip":
            return decision
        deadline = time.monotonic() + seconds
        entry, location = launcher()
        argv = [*entry, "--repo", str(record.root),
                "_worker", "--run-id", run, "--fd", str(lock.fileno()), "--codex", codex,
                "--prompt", str(prompt_path), "--deadline", str(deadline)]
        try:
            # Keep process diagnostics private; a deployment failure must not be
            # erased by DEVNULL before the recovery path can explain it.
            with (path / f"{run}-supervisor.log").open("xb") as diagnostics:
                os.chmod(diagnostics.name, 0o600)
                supervisor = subprocess.Popen(argv, cwd=location, stdin=subprocess.DEVNULL,
                                              stdout=subprocess.DEVNULL, stderr=diagnostics,
                                              pass_fds=(lock.fileno(),), start_new_session=True)
                try:
                    supervisor.wait(timeout=seconds + 30)
                except subprocess.TimeoutExpired:
                    supervisor.kill()
                    supervisor.wait()
            emit(record, "supervisor-exit", run, exit_code=supervisor.returncode)
        except OSError:
            emit(record, "finish", run, outcome="supervisor-launch-failed", exit_code=None)
        reason = recover(record)
        if reason:
            return emit(record, "skip", run, reason=reason)
        outcomes = [item for item in entries(record.read()[1])
                    if item["run"] == run and item["kind"] in TERMINAL]
        return outcomes[-1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("inspect", help="read safe journal summaries without starting a run")
    sub.add_parser("prepare-runtime", help="freeze clean committed runner and prompt privately")
    run = sub.add_parser("run", help="attempt one bounded wake; never installs a schedule")
    run.add_argument("--codex", default=DEFAULT_CODEX)
    run.add_argument("--prompt", default="docs/WATCH_PROMPT.md")
    run.add_argument("--seconds", type=float, default=MAX_SECONDS)
    work = sub.add_parser("_worker", help=argparse.SUPPRESS)
    for name in ("run-id", "codex", "prompt"):
        work.add_argument("--" + name, required=True)
    work.add_argument("--fd", type=int, required=True)
    work.add_argument("--deadline", type=float, required=True)
    execute = sub.add_parser("_exec", help=argparse.SUPPRESS)
    execute.add_argument("--gate", type=int, required=True)
    for name in ("run-id", "codex", "final"):
        execute.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "_exec":
            if os.read(args.gate, 2) != b"go":
                return 1
            os.close(args.gate)
            os.execv(args.codex, [args.codex, "exec", "--approve-for-me", "--json",
                                 "-C", args.repo, "-o", args.final, "-"])
        record = Record(args.repo)
        if args.command == "_worker":
            return worker(record, args.run_id, args.fd, args.codex,
                          Path(args.prompt), args.deadline)
        if args.command == "prepare-runtime":
            result = prepare_runtime(record, private_root(record))
        elif args.command == "inspect":
            result = inspect(record)
        else:
            result = run_watch(record, args.codex, args.prompt, args.seconds)
        print(json.dumps(result, indent=2), flush=True)
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        if isinstance(error, BrokenPipeError):
            with open(os.devnull, "w") as null:
                os.dup2(null.fileno(), sys.stdout.fileno())
        # Never echo raw subprocess diagnostics or model output into published summaries.
        try:
            print(json.dumps({"error": type(error).__name__, "message": "watch failed; no retry"}),
                  file=sys.stderr, flush=True)
        except BrokenPipeError:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stderr.fileno())
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
