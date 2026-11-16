"""Publish only the record-generated public house to its dedicated Pages branch."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

import hashlib
import marshal

from .body import export_inputs, projection as build_projection, replay, replay_context
from .record import Record
from .public_history import Encoder, decode

HISTORY_CACHE = "history-cache.marshal"
CACHE_FORMAT = 1

BRANCH = "codex/house-pages"
MAX_PUBLIC_BLOB = 64 * 1024 * 1024  # Fail locally before GitHub's 100 MiB limit.


def oversized_unpublished(record: Record, previous: str, remote: str | None) -> bool:
    args = ["rev-list", "--objects", "--no-object-names", previous]
    if remote:
        args.append("^" + remote)
    objects = record.git(*args)
    sizes = record.git("cat-file", "--batch-check=%(objecttype) %(objectsize)", data=objects)
    return any(kind == b"blob" and int(size) > MAX_PUBLIC_BLOB
               for kind, size in (line.split() for line in sizes.splitlines()))


def committed_blob(record: Record, head: str, path: str, *, optional=False) -> bytes | None:
    """Read an exact regular-file entry from the captured source tree."""
    entry = record.git("ls-tree", "-z", head, "--", path)
    if not entry and optional:
        return None
    parts = entry.rstrip(b"\0").split(b"\t", 1)
    if len(parts) != 2 or parts[1].decode() != path:
        raise ValueError("Missing committed public file: " + path)
    metadata = parts[0].split()
    if len(metadata) != 3 or metadata[0] not in (b"100644", b"100755") or metadata[1] != b"blob":
        raise ValueError("Public file is not a regular blob: " + path)
    return record.git("cat-file", "blob", metadata[2].decode())


def project_contents(record: Record, head: str) -> dict[str, bytes]:
    raw = committed_blob(record, head, "site/projects.json", optional=True)
    if raw is None:
        return {}
    manifest = json.loads(raw)
    if (not isinstance(manifest, dict) or manifest.get("version") != 1
            or type(manifest.get("version")) is not int or not isinstance(manifest.get("projects"), list)):
        raise ValueError("Invalid project manifest")
    contents = {"projects.json": raw}
    ids = set()
    for project in manifest["projects"]:
        if (not isinstance(project, dict) or set(project) != {"id", "title", "summary", "category", "action", "href", "files"}
                or any(not isinstance(project[key], str) or not project[key] for key in
                       ("id", "title", "summary", "category", "action", "href"))
                or project["id"] in ids or project["category"] not in ("creation", "house-tool")
                or project["action"] not in ("Open", "Play", "Read guide")
                or not isinstance(project["files"], list)):
            raise ValueError("Invalid project entry")
        ids.add(project["id"])
        for path in project["files"]:
            if not isinstance(path, str):
                raise ValueError("Invalid project path")
            parts = path.split("/")
            if (len(parts) < 3 or parts[0] != "projects" or
                    any(not part or part.startswith(".") or "\\" in part for part in parts)):
                raise ValueError("Unsafe project path: " + path)
            contents[path] = committed_blob(record, head, path)
    return contents


BALANCE_AREAS = (("building", ("projects/", "site/", "research/")),
                 ("record", ("evidence/", "docs/")),
                 ("foundations", ("house/", "tests/")))


def building_balance(record: Record, head: str, days: int = 7) -> dict:
    """Changed lines per day by area, from committed source history (no merges).

    Building is chosen work and the house's public face; record is evidence and
    documentation; foundations is the house's own code and tests. Binary files
    count as zero lines, so large evidence bundles are listed separately.
    """
    raw = record.git("log", "--no-merges", "--numstat", "--format=@%ct", "--since=" + str(days + 1) + ".days",
                     head, "--").decode("utf-8", "replace")
    per_day: dict[str, dict] = {}
    day = None
    for line in raw.splitlines():
        if line.startswith("@"):
            day = time.strftime("%Y-%m-%d", time.gmtime(int(line[1:])))
            per_day.setdefault(day, {"building": 0, "record": 0, "foundations": 0, "other": 0,
                                     "binary_files": 0})
            continue
        parts = line.split("\t")
        if day is None or len(parts) != 3:
            continue
        added, removed, path = parts
        area = next((name for name, prefixes in BALANCE_AREAS if path.startswith(prefixes)), "other")
        if added == "-" or removed == "-":
            per_day[day]["binary_files"] += 1
            continue
        per_day[day][area] += int(added) + int(removed)
    ordered = [{"day": key, **value} for key, value in sorted(per_day.items())][-days:]
    return {"version": 1, "source_head": head, "target_building_share": 0.5, "days": ordered,
            "note": "Changed text lines per UTC day by area; merges excluded; binary files counted separately."}


def code_identity() -> str:
    """The exact house code building the history; any change forces a full rebuild."""
    from .watch_recovery import RUNTIME
    digest = hashlib.sha256()
    if RUNTIME is not None:
        digest.update(RUNTIME.read_bytes())
    else:
        for path in sorted(Path(__file__).parent.glob("*.py")):
            digest.update(path.name.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def history(record: Record, private: Path, observed_at: float | None = None) -> tuple[bytes, dict]:
    """The public history.json, replaying only events newer than the private cache.

    Frames depend only on the events up to them, so the cache keeps the replay
    context and the already encoded frames. It is used only for the exact same
    house code and a journal that still contains the cached head; otherwise the
    history is rebuilt from the start. marshal holds plain data and cannot run code.
    """
    final, events, head, source_head, commits, observed_at = export_inputs(record, observed_at)
    identity = code_identity()
    path = private / HISTORY_CACHE
    cache = None
    try:
        cache = marshal.loads(path.read_bytes())
        if not (cache.get("format") == CACHE_FORMAT and cache["code"] == identity
                and 0 < cache["context"]["replayed"] <= len(events)
                and (cache["head"] == head or subprocess.run(
                    ["git", "-C", str(record.root), "merge-base", "--is-ancestor", cache["head"], head],
                    capture_output=True).returncode == 0)):
            cache = None
    except (OSError, ValueError, EOFError, TypeError, KeyError, AttributeError):
        cache = None
    if cache is None:
        cache = {"format": CACHE_FORMAT, "code": identity, "context": replay_context(),
                 "nodes": [], "seen": {}, "frames": []}
    context = cache["context"]
    encoder = Encoder(cache["nodes"], cache["seen"])
    new_frames = replay(events, context)
    for frame in new_frames:
        cache["frames"].append(encoder.value(frame))
    if not cache["frames"]:
        raise ValueError("No journal frames to publish")
    last_seq = len(cache["frames"])
    encoder.temporary()
    top = build_projection(final, head, source_head, observed_at, commits, [], context["scars"])
    root = encoder.intern({key: encoder.intern(cache["frames"]) if key == "frames" else encoder.value(value)
                           for key, value in top.items()})
    body = json.dumps({"version": 2, "root": root, "nodes": encoder.nodes},
                      separators=(",", ":"), allow_nan=False).encode()
    encoder.forget()
    if new_frames or cache.get("head") != head:
        cache["head"] = head
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_bytes(marshal.dumps(cache))
        temporary.chmod(0o600)
        os.replace(temporary, path)
    return body, {"journal_head": head, "source_head": source_head, "seq": last_seq,
                  "at": final["at"]}


def chronicle_body(record: Record) -> bytes:
    """The Chronicle Room page for the journal as it stands now."""
    from . import chronicle_page
    state, events, _ = record.read()
    numbered = [event | {"sequence": sequence} for sequence, event in enumerate(events, 1)]
    return chronicle_page.render_html(chronicle_page.select_milestones(numbered), through=len(numbered),
                                      house_id=state.get("house_id")).encode()


def publish(record: Record, *, push=False) -> dict:
    private = record.common / "house-home"
    private.mkdir(mode=0o700, exist_ok=True)
    with (private / "publisher.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        history_body, summary = history(record, private)
        head = summary["source_head"]
        if not head:
            raise ValueError("No source HEAD")
        contents = {name: committed_blob(record, head, "site/" + name)
                    for name in ("index.html", "house.css", "house.js")}
        missing_page = committed_blob(record, head, "site/404.html", optional=True)
        if missing_page is not None:
            contents["404.html"] = missing_page
        contents.update(project_contents(record, head))
        # Only the Chronicle page is public, never its journal input. It is
        # rebuilt from the journal on every publication so it cannot go stale;
        # the committed page is the fallback (and decides whether the room exists).
        chronicle = committed_blob(record, head, "site/chronicle/index.html", optional=True)
        if chronicle is not None:
            try:
                chronicle = chronicle_body(record)
            except (OSError, ValueError, KeyError, TypeError):
                pass
            contents["chronicle/index.html"] = chronicle
        contents["history.json"] = history_body
        # Visitors poll this tiny file and fetch the history only when it changes.
        contents["head.json"] = json.dumps(summary, separators=(",", ":"), sort_keys=True).encode()
        try:
            contents["balance.json"] = json.dumps(building_balance(record, head), separators=(",", ":")).encode()
        except (OSError, ValueError, subprocess.SubprocessError):
            pass  # The balance is a view; never block publication of the record.
        contents[".nojekyll"] = b""
        if any(len(body) > MAX_PUBLIC_BLOB for body in contents.values()):
            raise ValueError("Public snapshot exceeds the publication size budget")
        ref = "refs/heads/" + BRANCH
        previous = record.ref(ref)
        parent = previous
        recovering = False
        if push:
            remote = record.git("ls-remote", "origin", ref).decode().split()
            if remote and (not previous or remote[0] != previous):
                if not previous or record.git("merge-base", previous, remote[0]).decode().strip() != remote[0]:
                    raise ValueError("Pages branch diverged remotely; reconcile before publication")
            remote_head = remote[0] if remote else None
            if previous and previous != remote_head and oversized_unpublished(record, previous, remote_head):
                # Keep rejected local commits, but do not resend their oversized blobs.
                recovery = "refs/house-publication-recovery/" + previous
                saved = record.ref(recovery)
                if saved not in (None, previous):
                    raise ValueError("Publication recovery ref conflicts")
                if saved is None:
                    record.git("update-ref", recovery, previous, "0" * 40)
                parent = remote_head
                recovering = True
        if previous:
            try:
                old = json.loads(record.git("show", previous + ":head.json"))
                current_wire = True
            except ValueError:
                old_wire = json.loads(record.git("show", previous + ":history.json"))
                old, current_wire = decode(old_wire), old_wire.get("version") == 2
            if not recovering and current_wire and (old["journal_head"], old["source_head"]) == (summary["journal_head"], summary["source_head"]):
                if push:
                    record.git("push", "origin", ref + ":" + ref)
                    if record.git("ls-remote", "origin", ref).decode().split()[0] != previous:
                        raise ValueError("remote Pages commit not verified")
                return {"changed": False, "commit": previous, "pushed": push}
        with tempfile.TemporaryDirectory(prefix="house-public-index-") as temp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / "index"),
                       GIT_AUTHOR_NAME="Emberhall", GIT_AUTHOR_EMAIL="house@local",
                       GIT_COMMITTER_NAME="Emberhall", GIT_COMMITTER_EMAIL="house@local")
            def git(*args, data=None):
                return subprocess.run(["git", "-C", str(record.root), *args], env=env,
                                      input=data, capture_output=True, check=True).stdout.decode().strip()
            git("read-tree", "--empty")
            for name, body in contents.items():
                blob = git("hash-object", "-w", "--stdin", data=body)
                git("update-index", "--add", "--cacheinfo", "100644", blob, name)
            tree = git("write-tree")
            if not recovering and previous and git("rev-parse", previous + "^{tree}") == tree:
                return {"changed": False, "commit": previous}
            args = ["commit-tree", tree]
            if parent:
                args.extend(["-p", parent])
            commit = git(*args, data=f"Emberhall journal view through {summary['seq']}\n".encode())
            git("update-ref", ref, commit, previous or "0" * 40)
            if push:
                git("push", "origin", ref + ":" + ref)
                remote = git("ls-remote", "origin", ref).split()
                if not remote or remote[0] != commit:
                    raise ValueError("remote Pages commit not verified")
        return {"changed": True, "commit": commit, "pushed": push,
                "url": "https://someblueman.github.io/emberhall/"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(publish(Record(args.repo), push=args.push), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"published": False, "error": type(error).__name__}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
