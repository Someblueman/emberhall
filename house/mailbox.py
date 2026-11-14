"""Bounded per-room journal requests, executed only by the existing coordinator."""
from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import uuid

from .__main__ import parser, run as dispatch
from .record import REF, Record
from .resident_actions import ACTIONS
from .files import workspace_location

ALLOWED = frozenset({"status", "rules", "verify", "read", "wait", "receipt", "arrive", "rename", "wake",
                    "sleep", "say", "task", "ready", "claim", "renew", "release", "finish", "learn",
                    "review", "supersede", "life", "shelf"}) | ACTIONS
MUTATIONS = ALLOWED - {"status", "rules", "verify", "read", "wait", "receipt"}
MAX_REQUEST, MAX_RESPONSE = 256_000, 12_000_000
ID = re.compile(r"[0-9a-f]{64}")
DIRECTORY = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
ERRORS = (OSError, ValueError, KeyError, TypeError, RecursionError)


@contextmanager
def directory(root: Path, *parts: str, create=False):
    fd = os.open(root, DIRECTORY)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, DIRECTORY, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def read_json(fd: int, name: str, limit: int):
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    try:
        before = os.fstat(handle)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError("mailbox entry must be a bounded regular file")
        with os.fdopen(handle, "rb", closefd=False) as stream:
            raw = stream.read(limit + 1)
        after = os.fstat(handle)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
        if identity(before) != identity(after) or len(raw) > limit:
            raise ValueError("mailbox entry changed while reading")
        return json.loads(raw)
    finally:
        os.close(handle)


def write_json(fd: int, name: str, value: dict, limit: int):
    raw = json.dumps(value, sort_keys=True, allow_nan=False).encode()
    if len(raw) > limit:
        raise ValueError("mailbox message exceeds its size limit")
    temporary = ".tmp-" + uuid.uuid4().hex
    handle = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            existing = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if not stat.S_ISREG(existing.st_mode):
                raise ValueError("mailbox destination is not a regular file")
        except FileNotFoundError:
            pass
        os.replace(temporary, name, src_dir_fd=fd, dst_dir_fd=fd)
        os.fsync(fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=fd)
        except FileNotFoundError:
            pass


def fingerprint(argv: list[str]) -> str:
    return hashlib.sha256(json.dumps(argv, separators=(",", ":")).encode()).hexdigest()


def alias_id(value: str) -> str:
    return hashlib.sha256(("request\0" + value).encode()).hexdigest()


def parse(argv: list[str], repo: Path, workspace: Path, resident: str):
    if (not isinstance(argv, list) or not 1 <= len(argv) <= 128 or
            not all(isinstance(arg, str) and len(arg) <= 100_000 for arg in argv) or argv[0] not in ALLOWED):
        raise ValueError("use a bounded normal resident command")
    if any(arg in {"--repo", "--artifacts-from", "--help", "-h"} or
           arg.startswith(("--repo=", "--artifacts-from=")) for arg in argv):
        raise ValueError("mailbox command cannot override its root or request remote help")
    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
        try:
            if argv[0] in ACTIONS:
                from .resident_actions import parse as action_parse
                return action_parse(argv, resident)
            args = parser().parse_args(["--repo", str(repo), "--artifacts-from", str(workspace), *argv])
        except SystemExit:
            raise ValueError("invalid resident command arguments") from None
    if args.repo != str(repo) or args.artifacts_from != str(workspace):
        raise ValueError("fixed source roots cannot be overridden")
    if hasattr(args, "actor") and args.actor != resident:
        raise ValueError("this mailbox belongs to another resident")
    if args.command == "life":
        data = json.loads(args.data)
        if not isinstance(data, dict) or data.get("kind") not in {
                "identity", "activity", "room", "ambition", "help",
                "room-plan", "room-open", "room-repurpose", "room-close"}:
            raise ValueError("not a resident life command")
    if args.command == "shelf":
        from .shelf_gate import ACTIONS as SHELF_ACTIONS
        data = json.loads(args.data)
        if not isinstance(data, dict) or data.get("kind") not in SHELF_ACTIONS:
            raise ValueError("not a resident shelf command")
    if args.command == "wait" and not 1 <= args.seconds <= 3600:
        raise ValueError("wait must be between 1 and 3600 seconds")
    return args


def snapshot(record: Record):
    cached = getattr(record, "_mailbox_snapshot", None)
    head = record.ref(REF)
    if cached is None or cached[2] != head:
        cached = record.read()
        record._mailbox_snapshot = cached
    return cached


def release(record: Record, run: str) -> None:
    scans = getattr(record, "_mailbox_scans", {})
    previous = scans.pop(run, None)
    if previous:
        previous[1].close()


def process(record: Record, workspace: Path, resident: str, run: str, key: str,
            request: dict, receipts: int) -> dict | None:
    if (not isinstance(request, dict) or set(request) != {"version", "id", "argv"} or
            type(request["version"]) is not int or request["version"] != 1 or request["id"] != key):
        raise ValueError("invalid mailbox request schema")
    args = parse(request["argv"], record.root, workspace, resident)
    signature = fingerprint(request["argv"])
    name = key + ".json"
    try:
        saved = read_json(receipts, name, MAX_RESPONSE + MAX_REQUEST)
        if saved["sha256"] != signature:
            raise ValueError("mailbox request id reused with different content")
    except FileNotFoundError:
        saved = {"sha256": signature, "request": request, "first_seen": time.time()}
        if args.command == "wait":
            saved["deadline"] = saved["first_seen"] + args.seconds
        write_json(receipts, name, saved, MAX_RESPONSE + MAX_REQUEST)
    if "response" in saved:
        return saved["response"]
    state, events, head = snapshot(record)
    try:
        if args.command in ACTIONS:
            from . import mailbox_jobs
            job = mailbox_jobs.enqueue(record, run, request["argv"], "mailbox-" + run + "-" + key)
            answer = mailbox_jobs.result(record, job)
            if answer is None:
                return None
            if not answer["ok"]:
                raise ValueError(answer["error"])
            result = answer["result"]
        elif args.command == "wait":
            if resident not in state["residents"] or not 0 <= args.after <= state["sequence"]:
                raise ValueError("invalid waiting resident or cursor")
            if state["sequence"] <= args.after and time.time() < saved["deadline"]:
                return None
            result = {"changed": state["sequence"] > args.after, "through": state["sequence"], "head": head,
                      "note": "Resident waited through its coordinator mailbox; no model call was required."}
        elif args.command in MUTATIONS:
            args.request = "mailbox-" + run + "-" + key
            if args.request in state["receipts"]:
                sequence = state["receipts"][args.request]
                previous = events[sequence - 1]
                if previous["actor"] != resident or previous["op"] != args.command:
                    raise ValueError("mailbox receipt does not match its assigned command")
                result = {"request": args.request, "sequence": sequence, "replayed": True}
            else:
                result = dispatch(args)
        else:
            if args.command == "receipt" and args.request not in state["receipts"]:
                try:
                    local = read_json(receipts, alias_id(args.request) + ".json", MAX_RESPONSE + MAX_REQUEST)
                    if local["request"]["argv"][0] in MUTATIONS:
                        args.request = "mailbox-" + run + "-" + alias_id(args.request)
                except FileNotFoundError:
                    pass
            result = dispatch(args)
        response = {"id": key, "sha256": signature, "ok": True, "result": result}
        if len(json.dumps(response).encode()) > MAX_RESPONSE:
            raise ValueError("response exceeds mailbox bound; request a smaller read")
    except ERRORS as error:
        response = {"id": key, "sha256": signature, "ok": False,
                    "error": type(error).__name__ + ": " + str(error)[:300]}
    saved["response"] = response
    write_json(receipts, name, saved, MAX_RESPONSE + MAX_REQUEST)
    return response


def service(record: Record, private: Path, run: str) -> int:
    """Service at most 32 requests for one accepted active run, without waiting."""
    if private != record.common / "house-home" or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", run) is None:
        raise ValueError("invalid coordinator mailbox root or run")
    state = snapshot(record)[0]
    item = state.get("life", {}).get("runs", {}).get(run)
    if not item or item["status"] != "active" or "launched_sequence" not in item:
        release(record, run)
        return 0
    if item["workspace"] != "residents/" + run:
        raise ValueError("run workspace does not match its mailbox")
    root, parts = workspace_location(record, run, state)
    workspace = root.joinpath(*parts)
    served = 0
    try:
        with directory(root, *parts, ".house-mailbox", "requests") as requests, \
             directory(root, *parts, ".house-mailbox", "responses") as responses, \
             directory(private, run, "mailbox", create=True) as receipts:
            scans = getattr(record, "_mailbox_scans", {})
            identity = (os.fstat(requests).st_dev, os.fstat(requests).st_ino)
            if run not in scans or scans[run][0] != identity:
                release(record, run)
                scans[run] = (identity, os.scandir(requests))
                record._mailbox_scans = scans
            names = []
            for _ in range(512):
                entry = next(scans[run][1], None)
                if entry is None:
                    release(record, run)
                    break
                if entry.name.endswith(".json") and ID.fullmatch(entry.name[:-5]):
                    names.append(entry.name)
                    if len(names) >= 32:
                        break
            for name in names:
                key = name[:-5]
                try:
                    request = read_json(requests, name, MAX_REQUEST)
                    response = process(record, workspace, item["resident"], run, key, request, receipts)
                except ERRORS as error:
                    response = {"id": key, "ok": False, "error": type(error).__name__ + ": " + str(error)[:300]}
                if response is None:
                    continue
                try:
                    write_json(responses, name, response, MAX_RESPONSE)
                    os.unlink(name, dir_fd=requests)
                    served += 1
                except ERRORS:
                    continue
    except ERRORS:
        return served
    return served


def submit(workspace: Path, resident: str, argv: list[str], *, timeout: float = 120) -> dict:
    """Client side: only local room reads/writes, never a canonical Record."""
    args = parse(argv, workspace, workspace, resident)
    alias = args.request if args.command in MUTATIONS else None
    key = alias_id(alias) if alias else hashlib.sha256(os.urandom(32)).hexdigest()
    request = {"version": 1, "id": key, "argv": argv}
    signature = fingerprint(argv)
    name = key + ".json"
    with directory(workspace, ".house-mailbox", "requests") as requests, \
         directory(workspace, ".house-mailbox", "responses") as responses:
        try:
            existing = read_json(requests, name, MAX_REQUEST)
            if existing != request:
                raise ValueError("mailbox request id reused with different content")
        except FileNotFoundError:
            write_json(requests, name, request, MAX_REQUEST)
        deadline = time.monotonic() + (max(timeout, 1800) if args.command in ACTIONS else timeout) + (args.seconds if args.command == "wait" else 0)
        while time.monotonic() < deadline:
            try:
                response = read_json(responses, name, MAX_RESPONSE)
            except FileNotFoundError:
                time.sleep(0.1)
                continue
            if not isinstance(response, dict) or response.get("id") != key:
                raise ValueError("invalid mailbox response")
            if response.get("sha256", signature) != signature:
                raise ValueError("mailbox request id reused with different content")
            if not response.get("ok"):
                raise ValueError(response.get("error", "mailbox request rejected"))
            return response["result"]
    raise ValueError("coordinator reply timed out; retained mailbox id " + key)


def client_main(workspace: Path, resident: str, argv: list[str]) -> int:
    try:
        if argv in (["--help"], ["-h"]):
            print("Emberhall resident mailbox. Commands: " + ", ".join(sorted(ALLOWED)))
            print("Use COMMAND --help for arguments. The coordinator pins your identity and source room.")
            return 0
        if argv and argv[0] in ALLOWED and any(arg in {"--help", "-h"} for arg in argv):
            if argv[0] in ACTIONS:
                from .resident_actions import parser as action_parser
                action_parser().parse_args(argv)
            parser().parse_args([argv[0], "--help"])
        print(json.dumps(submit(workspace, resident, argv), indent=2))
        return 0
    except ERRORS as error:
        print("house mailbox: " + str(error)[:500], file=sys.stderr)
        return 2
