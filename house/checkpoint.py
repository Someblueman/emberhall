"""Verified journal exports into one assigned room, never automatic publication.

Private receipts fence cooperative resident retries, not hostile same-user shells.
The native-writable copies never share an inode with the protected cached payload.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import time
import uuid

from .model import require
from .record import ANCHOR, REF, Record
from .watch_recovery import FILE_LIMIT

META_LIMIT = 256_000
DIRECTORY = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


@contextmanager
def directory(path: Path, *, create=False):
    require(path.is_absolute(), "checkpoint path must be absolute")
    fd = os.open(path.anchor, DIRECTORY)
    try:
        for part in path.parts[1:]:
            require(part not in ("", ".", ".."), "invalid checkpoint path")
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, DIRECTORY, dir_fd=fd)
            os.close(fd); fd = child
        yield fd
    finally:
        os.close(fd)


def identity(info):
    return [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def read_file(fd: int, name: str, limit: int) -> tuple[bytes, list]:
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    try:
        before = os.fstat(handle)
        require(stat.S_ISREG(before.st_mode) and before.st_size <= limit,
                "checkpoint file must be bounded and regular")
        with os.fdopen(handle, "rb", closefd=False) as source:
            body = source.read(limit + 1)
        require(len(body) <= limit and identity(before) == identity(os.fstat(handle)),
                "checkpoint file changed during read")
        return body, identity(before)
    finally:
        os.close(handle)


def write_new(fd: int, name: str, body: bytes) -> list:
    handle = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    with os.fdopen(handle, "wb") as output:
        output.write(body); output.flush(); os.fsync(output.fileno())
        result = identity(os.fstat(output.fileno()))
    os.fsync(fd)
    return result


def save(fd: int, metadata: dict) -> None:
    body = (json.dumps(metadata, sort_keys=True, allow_nan=False, indent=2) + "\n").encode()
    require(len(body) <= META_LIMIT, "checkpoint metadata exceeds bound")
    try:
        read_file(fd, "job.json", META_LIMIT)
    except FileNotFoundError:
        pass
    temporary = ".receipt-" + uuid.uuid4().hex
    write_new(fd, temporary, body)
    os.replace(temporary, "job.json", src_dir_fd=fd, dst_dir_fd=fd)
    os.fsync(fd)


def binding(record, resident, run, task, token, requestid):
    require(isinstance(run, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", run),
            "invalid checkpoint run")
    for value, limit in ((resident, 100), (task, 100), (token, 20000), (requestid, 200)):
        require(isinstance(value, str) and 0 < len(value) <= limit, "invalid checkpoint request")
    key = sha(requestid.encode())
    return ({"resident": resident, "run": run, "task": task, "token": token, "requestid": requestid},
            record.common / "house-home" / "checkpoints" / key,
            record.common / "house-home" / "residents" / run)


def load(fd: int, expected: dict) -> dict:
    metadata = json.loads(read_file(fd, "job.json", META_LIMIT)[0])
    require(isinstance(metadata, dict) and metadata.get("binding") == expected,
            "checkpoint request collision or identity mismatch")
    return metadata


def guard(record: Record, expected: dict, generation: int | None = None) -> int:
    state = record.read()[0]
    run = state.get("life", {}).get("runs", {}).get(expected["run"], {})
    resident = expected["resident"]
    require(run.get("status") == "active" and run.get("resident") == resident and
            type(run.get("launched_sequence")) is int and
            run.get("workspace") == "residents/" + expected["run"] and
            state["residents"].get(resident, {}).get("awake") is True,
            "checkpoint needs its active launched awake resident")
    task = state["tasks"].get(expected["task"], {})
    require(task.get("status") == "claimed" and task.get("owner") == resident and
            task.get("token") == expected["token"] and task.get("until", 0) > max(time.time(), state["at"]),
            "checkpoint needs its own unexpired task token")
    require(generation is None or task["generation"] == generation, "checkpoint task generation changed")
    return task["generation"]


def cached(fd: int, output: dict) -> bytes:
    body, _ = read_file(fd, output["cache"], FILE_LIMIT)
    require(len(body) == output["size"] and sha(body) == output["sha256"], "cached checkpoint payload changed")
    return body


def completed(fd: int, workspace: Path, metadata: dict) -> dict | None:
    if "receipt" not in metadata:
        return None
    with directory(workspace / "evidence") as target:
        for name, output in metadata["outputs"].items():
            cached(fd, output)
            body, fingerprint = read_file(target, name, FILE_LIMIT)
            require(fingerprint == output["delivered"] and sha(body) == output["sha256"],
                    "delivered checkpoint changed; preserve it")
    return metadata["receipt"]


def known_result(record, resident, run, task, token, requestid) -> dict | None:
    """Read-only lost-reply recovery; an accepted export outlives its task lease."""
    expected, job, workspace = binding(record, resident, run, task, token, requestid)
    try:
        with directory(job) as fd:
            try:
                metadata = load(fd, expected)
            except FileNotFoundError:
                return None
            return completed(fd, workspace, metadata)
    except FileNotFoundError:
        # Missing accepted output is not an unstarted request.
        if job.exists():
            raise
        return None


def prepare(record: Record, fd: int, job: Path, metadata: dict) -> None:
    if "outputs" in metadata:
        for output in metadata["outputs"].values():
            cached(fd, output)
        return
    exported = metadata.get("prefix")
    try:
        bundle_body, _ = read_file(fd, "checkpoint.bundle", FILE_LIMIT)
    except FileNotFoundError:
        exported = record.bundle(str(job / "checkpoint.bundle"))
        bundle_body, _ = read_file(fd, "checkpoint.bundle", FILE_LIMIT)
    handle = os.open("checkpoint.bundle", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)
    os.fsync(fd)
    # A crash after bundle creation may precede the private receipt. Recover the
    # retained prefix from its advertised refs, never export a later prefix.
    advertised = record.git("bundle", "list-heads", str(job / "checkpoint.bundle")).decode().splitlines()
    refs = dict(line.split(" ", 1)[::-1] for line in advertised)
    require(set(refs) == {REF, ANCHOR} and all(re.fullmatch(r"[0-9a-f]{40}", value) for value in refs.values()),
            "invalid checkpoint bundle refs")
    if exported is not None:
        require(exported["head"] == refs[REF] and exported["anchor"] == refs[ANCHOR],
                "retained checkpoint prefix changed")
    metadata["prefix"] = {"head": refs[REF], "anchor": refs[ANCHOR]}
    save(fd, metadata)
    view = Record(record.root)
    original_ref = view.ref
    view.ref = lambda name: refs[name] if name in refs else original_ref(name)
    state, events, head = view.read()
    restore_path = Path(tempfile.mkdtemp(prefix="restore-", dir=job))
    record.git("init", "--quiet", str(restore_path))
    restored = Record(restore_path)
    receipt = restored.restore(str(job / "checkpoint.bundle"), refs[ANCHOR])
    require(restored.read() == (state, events, head) and restored.ref(ANCHOR) == refs[ANCHOR]
            and receipt == {"head": head, "anchor": refs[ANCHOR], "events": len(events)},
            "checkpoint restore did not reproduce exact state and events")
    shutil.rmtree(restore_path)  # Only this successfully verified, generated temporary repo.
    stem = "house-checkpoint-" + str(len(events)) + "-" + job.name
    document = {"house_id": state["house_id"], "name": state["name"], "head": head,
        "anchor": refs[ANCHOR], "events": len(events), "bundle": "evidence/" + stem + ".bundle",
        "bundle_sha256": sha(bundle_body),
        "first_event_utc": datetime.fromtimestamp(events[0]["at"], timezone.utc).isoformat(),
        "last_event_utc": datetime.fromtimestamp(events[-1]["at"], timezone.utc).isoformat(),
        "restored_exact_state_and_events": True, "restore_receipt": receipt,
        "note": "Verified fixed journal prefix. Later events may be outside this export. "
                "Not canonical publication, rule ratification or a claim of elapsed days."}
    raw = (json.dumps(document, sort_keys=True, indent=2) + "\n").encode()
    try:
        write_new(fd, "checkpoint.json", raw)
    except FileExistsError:
        require(read_file(fd, "checkpoint.json", FILE_LIMIT)[0] == raw, "cached checkpoint metadata differs")
    metadata["outputs"] = {stem + suffix: {"cache": "checkpoint" + suffix,
        "sha256": sha(body), "size": len(body)} for suffix, body in ((".bundle", bundle_body), (".json", raw))}
    metadata["result"] = {"format": "emberhall-resident-checkpoint-v1", "run": metadata["binding"]["run"],
        "task": metadata["binding"]["task"], "task_generation": metadata["task_generation"], "head": head, "anchor": refs[ANCHOR], "events": len(events),
        "bundle": document["bundle"], "metadata": "evidence/" + stem + ".json",
        "bundle_sha256": sha(bundle_body), "metadata_sha256": sha(raw), "restored_exact_state_and_events": True}
    save(fd, metadata)


def deliver(fd: int, target: int, metadata: dict) -> None:
    for name, output in metadata["outputs"].items():
        body = cached(fd, output)
        if "delivered" in output:
            actual, fingerprint = read_file(target, name, FILE_LIMIT)
            require(fingerprint == output["delivered"] and actual == body, "delivered checkpoint changed; preserve it")
            continue
        if "temporary" not in output:
            # Refuse even byte-identical pre-existing files: they are not ours.
            try:
                os.stat(name, dir_fd=target, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise ValueError("checkpoint destination already exists; preserve it")
            temporary = ".checkpoint-" + uuid.uuid4().hex
            fingerprint = write_new(target, temporary, body)
            output.update(temporary=temporary, inode=fingerprint[:2])
            save(fd, metadata)  # Durable intent precedes the no-clobber link.
        temporary = output["temporary"]
        try:
            actual, fingerprint = read_file(target, name, FILE_LIMIT)
        except FileNotFoundError:
            actual, fingerprint = read_file(target, temporary, FILE_LIMIT)
            require(actual == body and fingerprint[:2] == output["inode"], "checkpoint temporary changed")
            os.link(temporary, name, src_dir_fd=target, dst_dir_fd=target, follow_symlinks=False)
            os.fsync(target)
            actual, fingerprint = read_file(target, name, FILE_LIMIT)
        require(actual == body and fingerprint[:2] == output["inode"], "checkpoint destination is not this delivery")
        try:
            _, temporary_fingerprint = read_file(target, temporary, FILE_LIMIT)
            require(temporary_fingerprint[:2] == output["inode"], "checkpoint temporary replaced")
            os.unlink(temporary, dir_fd=target); os.fsync(target)
        except FileNotFoundError:
            pass  # Crash after unlink but before the delivered receipt.
        final_body, fingerprint = read_file(target, name, FILE_LIMIT)
        require(final_body == body and fingerprint[:2] == output["inode"], "checkpoint destination changed")
        output["delivered"] = fingerprint
        save(fd, metadata)
    metadata["receipt"] = metadata["result"]
    save(fd, metadata)


def create(record, workspace, resident, run, task, token, requestid) -> dict:
    expected, job, assigned = binding(record, resident, run, task, token, requestid)
    require(workspace == assigned, "checkpoint workspace must be its assigned private room")
    previous = known_result(record, resident, run, task, token, requestid)
    if previous is not None:
        return previous
    generation = guard(record, expected)
    with directory(assigned), directory(job, create=True) as fd:
        lock = os.open("job.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        try:
            require(stat.S_ISREG(os.fstat(lock).st_mode), "checkpoint lock must be regular")
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                metadata = load(fd, expected)
            except FileNotFoundError:
                metadata = {"binding": expected, "task_generation": generation}
                save(fd, metadata)
            previous = completed(fd, assigned, metadata)
            if previous is not None:
                return previous
            require(metadata["task_generation"] == generation, "checkpoint task generation changed")
            prepare(record, fd, job, metadata)
            with record.locked():
                guard(record, expected, metadata["task_generation"])
                with directory(assigned / "evidence", create=True) as target:
                    deliver(fd, target, metadata)
            return completed(fd, assigned, metadata)
        finally:
            os.close(lock)
