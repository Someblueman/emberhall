"""Private scheduled-work rescue and explicit, committed watch runtime snapshots."""
from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

from .record import Record

RUNTIME = Path(__loader__.archive).resolve() if hasattr(__loader__, "archive") else None
SOURCE = Path(__file__).resolve().parents[1]
FILE_LIMIT = 8 * 1024 * 1024
TOTAL_LIMIT = 64 * 1024 * 1024


def launcher() -> tuple[list[str], Path]:
    if RUNTIME:
        return [sys.executable, str(RUNTIME)], RUNTIME.parent
    return [sys.executable, "-m", "house.watch"], SOURCE


def source_head(record: Record) -> str:
    return record.git("rev-parse", "--verify", "HEAD").decode().strip()


def file_identity(value: os.stat_result) -> tuple:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


def capture(record: Record) -> bytes | None:
    """Read bounded regular changed files and their index versions without altering either."""
    status = record.git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    if not status:
        return None
    head = source_head(record)
    changed = set(record.git("diff", "--no-renames", "--name-only", "-z", "HEAD").split(b"\0"))
    changed.update(record.git("diff", "--cached", "--no-renames", "--name-only", "-z", "HEAD").split(b"\0"))
    changed.update(record.git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0"))
    changed.discard(b"")
    index = record.git("ls-files", "--stage", "-z")
    files, staged, witnessed = {}, [], {}
    total = 0
    for raw in sorted(changed):
        name = raw.decode("utf-8")
        path = record.root / name
        for parent in path.parents:
            if parent == record.root:
                break
            if parent.is_symlink():
                raise ValueError("unsafe rescue path component")
        try:
            before = path.lstat()
        except FileNotFoundError:
            files[name] = None
            continue
        if not stat.S_ISREG(before.st_mode) or before.st_size > FILE_LIMIT:
            raise ValueError("rescue requires bounded regular files")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("rescue file is not regular")
            body = stream.read(FILE_LIMIT + 1)
        total += len(body)
        if len(body) > FILE_LIMIT or total > TOTAL_LIMIT or file_identity(path.lstat()) != file_identity(before):
            raise ValueError("rescue file changed or exceeded budget")
        witnessed[name] = before
        files[name] = {"mode": stat.S_IMODE(before.st_mode),
                       "base64": base64.b64encode(body).decode()}
    for item in index.split(b"\0"):
        if not item:
            continue
        header, raw = item.split(b"\t", 1)
        if raw not in changed:
            continue
        mode, oid, stage = header.decode().split()
        size = int(record.git("cat-file", "-s", oid))
        total += size
        if size > FILE_LIMIT or total > TOTAL_LIMIT:
            raise ValueError("rescue index exceeded budget")
        staged.append({"path": raw.decode(), "mode": mode, "stage": stage,
                       "base64": base64.b64encode(record.git("cat-file", "blob", oid)).decode()})
    if (status != record.git("status", "--porcelain=v1", "-z", "--untracked-files=all") or
            index != record.git("ls-files", "--stage", "-z") or head != source_head(record) or
            any(file_identity((record.root / name).lstat()) != file_identity(before) for name, before in witnessed.items())):
        raise ValueError("checkout changed during rescue")
    return json.dumps({"head": head, "status": base64.b64encode(status).decode(),
                       "files": files, "index": staged}, sort_keys=True).encode()


def fingerprint(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def rescue_git(directory: Path, *args: str, data: bytes | None = None,
               lock_fd: int | None = None) -> bytes:
    env = dict(os.environ, GIT_AUTHOR_NAME="Private watch rescue", GIT_AUTHOR_EMAIL="watch@local",
               GIT_COMMITTER_NAME="Private watch rescue", GIT_COMMITTER_EMAIL="watch@local")
    result = subprocess.run(["git", "--git-dir", str(directory), *args], input=data,
                            capture_output=True, env=env, check=True,
                            pass_fds=() if lock_fd is None else (lock_fd,))
    return result.stdout


def save_rescue(record: Record, private: Path, run: str) -> dict | None:
    payload = capture(record)
    if payload is None:
        return None
    with (private / "rescue-writer.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        return store_rescue(private, run, payload, lock.fileno())


def store_rescue(private: Path, run: str, payload: bytes, fd: int) -> dict:
    directory = private / "rescue.git"
    if not directory.exists():
        subprocess.run(["git", "init", "--bare", "--quiet", str(directory)],
                       check=True, pass_fds=(fd,))
        directory.chmod(0o700)
    def git(*args: str, data: bytes | None = None) -> bytes:
        return rescue_git(directory, *args, data=data, lock_fd=fd)
    digest = fingerprint(payload)
    # Only this protocol writes these refs; inherited flock fences surviving Git children.
    ref = f"refs/rescues/{run}/{digest}"
    abandoned = directory / (ref + ".lock")
    if abandoned.exists():
        abandoned.unlink()
    prior = git("for-each-ref", "--format=%(objectname)", ref).strip()
    if prior:
        commit = prior.decode()
    else:
        blob = git("hash-object", "-w", "--stdin", data=payload).decode().strip()
        tree = git("mktree", data=f"100644 blob {blob}\trescue.json\n".encode())
        commit = git("commit-tree", tree.decode().strip(),
                     data=f"Private interrupted watch {run}\n".encode()).decode().strip()
        git("update-ref", ref, commit, "0" * 40)
    return {"commit": commit, "fingerprint": digest, "source_head": json.loads(payload)["head"]}


def verify_rescue(private: Path, rescue: dict, payload: bytes) -> bool:
    if fingerprint(payload) != rescue["fingerprint"]:
        return False
    stored = rescue_git(private / "rescue.git", "show", rescue["commit"] + ":rescue.json")
    return stored == payload


def prompt_bytes(record: Record, prompt: Path, private: Path, start: dict) -> bytes:
    prior = start.get("recover_from")
    if prior:
        base = (private / prior / "base-prompt.txt").read_bytes()
    elif RUNTIME:
        with zipfile.ZipFile(RUNTIME) as archive:
            base = archive.read("docs/WATCH_PROMPT.md")
    else:
        base = prompt.read_bytes()
    prefix = (f"RUNNER ASSIGNMENT: your resident ID is {start['resident']}. Choose your own name, "
              "but use this exact ID for arrival and all work. Do not impersonate any other ID.\n")
    if prior:
        prefix += (f"RECOVERY ONLY: scheduled run {prior}, resident {start['prior_resident']}, "
                   f"left this exact privately preserved checkout. Rescue commit {start['rescue_commit']} "
                   f"is in {private / 'rescue.git'}. Inspect the journal and private rescue before editing. "
                   "Resume only that unfinished work; preserve tracked, staged and untracked bytes. "
                   "Do not reset, stash, unlink, overwrite, publish rescue data, or start unrelated work. "
                   "Old claims are not yours: never renew them or steal a live lease. Reclaim expired "
                   "work only with its current generation and a new token. If uncertain, leave a precise "
                   "private/local handoff and stop without destructive changes. Use the pinned runner's "
                   "Python package for journal access if working imports are broken; repair mutable code "
                   "with a witnessed test, never change journal schemas or the pinned runtime.\n")
    if RUNTIME:
        prefix += "Pinned journal command prefix (argv): " + json.dumps(
            [sys.executable, str(RUNTIME), "house", "--repo", str(record.root)]) + "\n"
    recovery_steps = (
        "Read AGENTS.md, docs/STEWARD_ORDERS.md and docs/RESUME.md for applicable constraints. "
        "Verify the journal, arrive with the assigned ID, and inspect the original run/claim. "
        "Claim only this bounded repair with explicit affected paths. After repair, run relevant "
        "checks, preserve reviewed immutable artifacts, finish/release your own claim, read and sleep. "
        "Commit only completed repair under repository policy. Do not push or publish private rescue "
        "evidence. If repair cannot be completed safely, preserve bytes and leave an exact handoff.\n")
    assigned = prefix.encode() + (recovery_steps.encode() if prior else base)
    path = private / start["run"]
    for name, data in (("base-prompt.txt", base), ("prompt.txt", assigned)):
        with (path / name).open("xb") as output:
            os.chmod(path / name, 0o600)
            output.write(data)
    return assigned


def prepare_runtime(record: Record, private: Path) -> dict:
    if record.git("status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("runtime preparation requires a clean committed checkout")
    head = source_head(record)
    files = record.git("ls-tree", "-rz", head, "house", "docs/WATCH_PROMPT.md")
    contents = {}
    for item in files.split(b"\0"):
        if not item:
            continue
        header, raw = item.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        name = raw.decode()
        if name != "docs/WATCH_PROMPT.md" and not name.endswith(".py"):
            continue
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("runtime source must contain regular files")
        contents[name] = record.git("cat-file", "blob", oid)
    if not {"house/watch.py", "house/watch_recovery.py", "docs/WATCH_PROMPT.md"} <= contents.keys():
        raise ValueError("committed runtime or prompt is missing")
    contents["__main__.py"] = (b"import sys\n"
        b"if sys.argv[1:2] == ['house']:\n    del sys.argv[1]\n"
        b"    from house.__main__ import main\n"
        b"elif sys.argv[1:2] == ['home']:\n    del sys.argv[1]\n    from house.home import main\n"
        b"elif sys.argv[1:2] == ['steward']:\n    del sys.argv[1]\n    from house.steward import main\n"
        b"elif sys.argv[1:2] == ['runtime']:\n    del sys.argv[1]\n    from house.runtime import main\n"
        b"elif sys.argv[1:2] == ['owner-upgrade']:\n    del sys.argv[1]\n    from house.owner_upgrade import main\n"
        b"else:\n    from house.watch import main\n"
        b"raise SystemExit(main())\n")
    contents["runtime-source.json"] = json.dumps({"source_head": head, "sha256": {
        name: fingerprint(body) for name, body in contents.items()}}, sort_keys=True).encode()
    target = private / f"runtime-{head}.pyz"
    if not target.exists():
        temporary = private / f"runtime-{head}-{os.getpid()}.tmp"
        with zipfile.ZipFile(temporary, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, body in sorted(contents.items()):
                archive.writestr(zipfile.ZipInfo(name), body)
        temporary.chmod(0o600)
        with zipfile.ZipFile(temporary) as archive:
            if {name: archive.read(name) for name in archive.namelist()} != contents:
                raise ValueError("runtime verification failed")
        os.link(temporary, target)
        temporary.unlink()
    with zipfile.ZipFile(target) as archive:
        if {name: archive.read(name) for name in archive.namelist()} != contents:
            raise ValueError("existing runtime does not match committed source")
    return {"source_head": head, "runtime_sha256": fingerprint(target.read_bytes()),
            "files": json.loads(contents["runtime-source.json"])["sha256"],
            "entry": str(target), "command": [sys.executable, str(target),
                                              "--repo", str(record.root), "run"]}
