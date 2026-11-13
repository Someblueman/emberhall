"""A linear Git journal, isolated from the working index and source branch."""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import time
import uuid
from pathlib import Path

from .governance import canonical
from .model import apply_event, require

REF = "refs/heads/house-ledger"
ANCHOR = "refs/house/foundation"
ZERO = "0" * 40


class Record:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root).resolve()
        self.gitdir = Path(self.git("rev-parse", "--absolute-git-dir").decode().strip())
        self.common = Path(self.git("rev-parse", "--path-format=absolute",
                                    "--git-common-dir").decode().strip())
        require(self.git("rev-parse", "--show-object-format").strip() == b"sha1",
                "this journal version requires Git SHA-1 object format")

    def git(self, *args: str, data: bytes | None = None) -> bytes:
        env = dict(os.environ, GIT_AUTHOR_NAME="House journal", GIT_AUTHOR_EMAIL="house@local",
                   GIT_COMMITTER_NAME="House journal", GIT_COMMITTER_EMAIL="house@local")
        result = subprocess.run(["git", "-C", str(self.root), *args], input=data,
                                capture_output=True, env=env, check=False,
                                pass_fds=getattr(self, "_lock_fds", ()))
        if result.returncode:
            raise ValueError(result.stderr.decode(errors="replace").strip() or "Git command failed")
        return result.stdout

    def ref(self, name: str) -> str | None:
        result = subprocess.run(["git", "-C", str(self.root), "show-ref", "--verify", "--hash", name],
                                capture_output=True, check=False)
        if result.returncode == 1:
            return None
        # show-ref --verify returns 128 for an absent ref in some Git versions.
        if result.returncode and not (self.common / name).exists():
            listed = self.git("for-each-ref", "--format=%(objectname)", name).decode().strip()
            return listed or None
        require(result.returncode == 0, "cannot read house ref")
        return result.stdout.decode().strip()

    @contextlib.contextmanager
    def locked(self):
        # Descriptor inheritance keeps the lock alive if the Python parent is killed
        # while Git is updating the ref. Every house writer uses this same lock.
        with (self.common / "house-writer.lock").open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            self._lock_fds = (lock.fileno(),)
            try:
                # These two refs are exclusively owned by this protocol. A killed
                # Git child can leave its lockfile; no live house writer can own it here.
                for ref in (REF, ANCHOR):
                    path = self.common / (ref + ".lock")
                    if path.exists():
                        path.unlink()
                yield
            finally:
                self._lock_fds = ()
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def commit(self, event: dict, parent: str | None) -> str:
        blob = self.git("hash-object", "-w", "--stdin", data=canonical(event)).decode().strip()
        tree = self.git("mktree", data=f"100644 blob {blob}\tevent.json\n".encode()).decode().strip()
        args = ["commit-tree", tree]
        if parent:
            args.extend(["-p", parent])
        return self.git(*args, data=f"house: {event['op']} {event['id']}\n".encode()).decode().strip()

    def read(self) -> tuple[dict, list[dict], str]:
        head = self.ref(REF)
        anchor = self.ref(ANCHOR)
        require(bool(head and anchor), "house not founded/restored; read AGENTS.md")
        commits = self.git("rev-list", "--reverse", "--first-parent", head).decode().splitlines()
        require(bool(commits) and commits[0] == anchor, "foundation anchor mismatch")
        queries = [value for oid in commits for value in (oid, f"{oid}:event.json")]
        packed = self.git("cat-file", "--batch", data=("\n".join(queries) + "\n").encode())
        objects = []
        offset = 0
        for query in queries:
            end = packed.index(b"\n", offset)
            header = packed[offset:end].split()
            require(len(header) == 3, f"missing journal object: {query}")
            oid, kind, length = header
            size = int(length)
            content = packed[end + 1:end + 1 + size]
            actual = hashlib.sha1(kind + b" " + str(size).encode() + b"\0" + content).hexdigest()
            require(actual == oid.decode(), "corrupt Git object")
            objects.append((kind, content))
            offset = end + size + 2
        require(offset == len(packed), "invalid Git object stream")
        events = []
        state = None
        parent = None
        for index, oid in enumerate(commits):
            commit_kind, commit = objects[2 * index]
            event_kind, raw = objects[2 * index + 1]
            require(commit_kind == b"commit" and event_kind == b"blob", "invalid object types")
            headers = commit.split(b"\n\n", 1)[0].splitlines()
            parents = [line[7:].decode() for line in headers if line.startswith(b"parent ")]
            require(parents == ([parent] if parent else []), "journal is not linear")
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).digest()
            tree_body = b"100644 event.json\0" + blob
            tree_hash = hashlib.sha1(b"tree " + str(len(tree_body)).encode() + b"\0" + tree_body).hexdigest()
            trees = [line[5:].decode() for line in headers if line.startswith(b"tree ")]
            require(trees == [tree_hash], "unexpected journal tree")
            event = json.loads(raw)
            require(canonical(event) == raw, "noncanonical event")
            state = apply_event(state, event)
            events.append(event)
            parent = oid
        assert state is not None
        return state, events, head

    def found(self, name: str, rules: str, owner_key: str = "") -> dict:
        with self.locked():
            require(not self.ref(REF) and not self.ref(ANCHOR), "house already exists")
            event = {"id": str(uuid.uuid4()), "op": "found", "actor": "founder",
                     "at": time.time(), "data": {"name": name, "rules": rules,
                     "owner_key": owner_key.strip(), "house_id": str(uuid.uuid4())}}
            state = apply_event(None, event)
            oid = self.commit(event, None)
            # Atomic ref transaction; restart cannot find a half-founded house.
            self.git("update-ref", "--stdin", data=(f"start\ncreate {ANCHOR} {oid}\n"
                f"create {REF} {oid}\nprepare\ncommit\n").encode())
            return {"head": oid, "anchor": oid, "house_id": state["house_id"]}

    def append(self, op: str, actor: str, data: dict, request: str | None = None) -> dict:
        request = request or str(uuid.uuid4())
        with self.locked():
            state, events, head = self.read()
            if request in state["receipts"]:
                sequence = state["receipts"][request]
                prior = events[sequence - 1]
                require(prior["op"] == op and prior["actor"] == actor and prior["data"] == data,
                        "request id reused with different content")
                return {"request": request, "sequence": sequence, "replayed": True}
            event = {"id": request, "op": op, "actor": actor,
                     "at": max(time.time(), state["at"]), "data": data}
            require(len(canonical(event)) <= 8000000, "event exceeds 8 MB")
            next_state = apply_event(state, event)
            oid = self.commit(event, head)
            self.git("update-ref", REF, oid, head)
            return {"request": request, "sequence": next_state["sequence"], "head": oid,
                    "replayed": False}

    def bundle(self, destination: str) -> dict:
        with self.locked():
            state, _, head = self.read()
            target = Path(destination).resolve()
            require(not target.exists(), "bundle destination already exists")
            self.git("bundle", "create", str(target), REF, ANCHOR)
            return {"head": head, "anchor": self.ref(ANCHOR), "events": state["sequence"],
                    "bundle": str(target)}

    def restore(self, source: str, expected_anchor: str) -> dict:
        with self.locked():
            require(not self.ref(REF) and not self.ref(ANCHOR), "refuse to overwrite an existing house")
            source = str(Path(source).resolve())
            advertised = self.git("bundle", "list-heads", source).decode().splitlines()
            refs = dict(line.split(" ", 1)[::-1] for line in advertised)
            require(set(refs) == {REF, ANCHOR} and refs[ANCHOR] == expected_anchor,
                    "bundle trust anchor mismatch")
            # Fetch objects to temporary refs, validate before publishing canonical refs.
            prefix = "refs/house-import/" + uuid.uuid4().hex
            try:
                self.git("fetch", "--no-write-fetch-head", source,
                         f"{REF}:{prefix}/ledger", f"{ANCHOR}:{prefix}/foundation")
                # Validate the imported chain using an isolated Record view.
                reader = Record(self.root)
                original_ref = reader.ref
                reader.ref = lambda name: refs[name] if name in refs else original_ref(name)
                state, _, head = reader.read()
                self.git("update-ref", "--stdin", data=(f"start\ncreate {REF} {head}\n"
                    f"create {ANCHOR} {expected_anchor}\nprepare\ncommit\n").encode())
                return {"head": head, "events": state["sequence"], "anchor": expected_anchor}
            finally:
                for suffix in ("ledger", "foundation"):
                    self.git("update-ref", "-d", f"{prefix}/{suffix}")
