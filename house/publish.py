"""Publish only the record-generated public house to its dedicated Pages branch."""
from __future__ import annotations

import argparse
import fcntl
import gzip
import json
import os
import re
import sys
from pathlib import Path
import subprocess
import tempfile
import time

import hashlib
import marshal

from .body import export_inputs, projection as build_projection, replay, replay_context
from .door_summary import _FrameReader, now_bytes
from .record import Record
from .public_history import Encoder, decode

HISTORY_CACHE = "history-cache.marshal"
CACHE_FORMAT = 2  # 2: long lists are stored as chunks (wire version 4)

BRANCH = "codex/house-pages"
# Fail locally before GitHub's 100 MiB limit. On 17 November (evening) the history passed 64 MiB and
# the page stood still for forty minutes; it is now published in sealed parts, so nothing nears this.
MAX_PUBLIC_BLOB = 64 * 1024 * 1024
# The present view a visitor downloads first. Above the target the publisher still publishes and warns:
# a page that loads a little more is better than a house that stops publishing. Only the hard limit fails.
CURRENT_SNAPSHOT_TARGET_BYTES = 1_400_000
CURRENT_SNAPSHOT_MAX_BYTES = 8_000_000
# Cached listings can survive several publications. Keep their immutable targets
# available without growing the deployed tree indefinitely (no visitor downloads
# these extra files unless its listing names one).
CURRENT_RETAINED_COUNT = 32
CURRENT_RETAINED_BYTES = 32 * 1024 * 1024
CURRENT_RETENTION_INDEX = "current-retained.json"
CURRENT_COMPANION = re.compile(r"current/[0-9a-f]{16}\.json\.gz\Z")
# A sealed part of the node table is closed once its JSON reaches this size and never changes again.
PART_TARGET = 8 * 1024 * 1024
# A rebuild replays this many events at a time and saves its place this often (see history()).
REPLAY_BATCH = 100
CHECKPOINT_SECONDS = 120
PARTS_DIR = "history-parts"


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


def part_bytes(private: Path, cache: dict, index: int) -> bytes:
    """A sealed part's exact bytes: from the private folder, else rebuilt from the cached nodes."""
    entry, folder = cache["parts"][index], private / PARTS_DIR
    file = folder / entry["path"].rsplit("/", 1)[-1]
    try:
        data = file.read_bytes()
    except OSError:
        data = b""
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        start = sum(part["nodes"] for part in cache["parts"][:index])
        data = json.dumps(cache["nodes"][start:start + entry["nodes"]], separators=(",", ":"),
                          allow_nan=False).encode()
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("History cache no longer matches its sealed part")
        write_private(file, data)
    return data


def write_private(path: Path, data: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.chmod(0o600)
    os.replace(temporary, path)


def history(record: Record, private: Path, observed_at: float | None = None) -> tuple[bytes, dict, dict[str, bytes]]:
    """The public history.json and its sealed parts, replaying only events newer than the private cache.

    The persistent prefix of the node table is cut into parts of about PART_TARGET bytes. A part ends
    where the cache says (its node count is kept), so old parts keep their bytes and names and only
    new parts are added at the end. Everything after the last part stays in history.json.

    Frames depend only on the events up to them, so the cache keeps the replay
    context and the already encoded frames. It is used only for the exact same
    house code and a journal that still contains the cached head; otherwise the
    history is rebuilt from the start. marshal holds plain data and cannot run code.
    """
    body, summary, parts, _ = _history_with_cache(record, private, observed_at)
    return body, summary, parts


def _history_with_cache(
    record: Record,
    private: Path,
    observed_at: float | None = None,
) -> tuple[bytes, dict, dict[str, bytes], dict]:
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
    encoder = Encoder(cache["nodes"], cache["seen"], chunked=True)

    def save() -> None:
        cache["head"] = head
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_bytes(marshal.dumps(cache))
        temporary.chmod(0o600)
        os.replace(temporary, path)

    # Replay in batches and keep the place. A full rebuild used to hold every frame in memory at once
    # and save nothing until the end; on 18 November, with the machine short of memory, it passed the
    # publisher's twenty-minute limit, was killed and began again from nothing, so the page stood
    # still. Now a stopped rebuild resumes where its last checkpoint left it. The cache then names the
    # current head while holding fewer events: the journal only grows, so its first events are the same.
    new_frames, saved = False, time.monotonic()
    while context["replayed"] < len(events):
        before = context["replayed"]
        for frame in replay(events[:before + REPLAY_BATCH], context):
            cache["frames"].append(encoder.value(frame))
            encoder.appended(cache["frames"])  # a full chunk of the frame list joins the persistent table now
        new_frames = True
        if context["replayed"] <= before:
            raise ValueError("The history replay made no progress")
        if context["replayed"] < len(events) and time.monotonic() - saved >= CHECKPOINT_SECONDS:
            save()
            saved = time.monotonic()
    if not cache["frames"]:
        raise ValueError("No journal frames to publish")
    last_seq = len(cache["frames"])
    encoder.temporary()
    top = build_projection(final, head, source_head, observed_at, commits, [], context["scars"])
    root = encoder.intern({key: encoder.sequence(cache["frames"]) if key == "frames" else encoder.value(value)
                           for key, value in top.items()})
    persistent, had_parts = encoder.mark, "parts" in cache
    sealed = sum(part["nodes"] for part in cache.get("parts", ()))
    if "parts" not in cache or sealed > persistent:
        cache["parts"], sealed = [], 0
    pieces = [json.dumps(node, separators=(",", ":"), allow_nan=False) for node in encoder.nodes[sealed:]]
    first = size = 0
    grown = False
    for number in range(persistent - sealed):
        size += len(pieces[number]) + 1
        if size >= PART_TARGET:
            data = ("[" + ",".join(pieces[first:number + 1]) + "]").encode()
            digest = hashlib.sha256(data).hexdigest()
            name = f"history/part-{len(cache['parts']):04d}-{digest[:16]}.json"
            write_private(private / PARTS_DIR / name.rsplit("/", 1)[-1], data)
            cache["parts"].append({"path": name, "nodes": number + 1 - first, "sha256": digest})
            first, size, grown = number + 1, 0, True
    parts = {entry["path"]: part_bytes(private, cache, number) for number, entry in enumerate(cache["parts"])}
    body = ('{"version":4,"parts":' + json.dumps(cache["parts"], separators=(",", ":")) +
            ',"root":' + json.dumps(root, separators=(",", ":")) +
            ',"nodes":[' + ",".join(pieces[first:]) + "]}").encode()
    encoder.forget()
    if grown or not had_parts:
        for stale in (private / PARTS_DIR).glob("part-*"):
            if "history/" + stale.name not in parts:
                stale.unlink(missing_ok=True)
    if new_frames or grown or not had_parts or cache.get("head") != head:
        save()
    from .craft_outcomes import PUBLIC_WINDOW
    snapshot = {
        "final": final,
        "recent_events": events[-PUBLIC_WINDOW:],
        "head": head,
        "source_head": source_head,
        "commits": commits,
        "observed_at": observed_at,
        "frames": cache["frames"],
        "nodes": cache["nodes"],
        "scars": context["scars"],
    }
    return body, {"journal_head": head, "source_head": source_head, "seq": last_seq,
                  "at": final["at"], "history_version": 4}, parts, snapshot


def current_snapshot_files(snapshot: dict) -> dict[str, bytes]:
    """Build the present view by resolving only nodes reachable from the latest frame."""
    try:
        frames, nodes = snapshot["frames"], snapshot["nodes"]
        if not isinstance(frames, list) or not frames or not isinstance(nodes, list):
            raise ValueError("No current frame to publish")
        reader = _FrameReader(frames, nodes)
        last = len(frames) - 1
        raw = reader._raw(last)
        if not isinstance(raw, dict):
            raise ValueError("Invalid current frame")
        frame = {key: reader.field(last, key) for key in raw}
        if type(frame.get("seq")) is not int or frame["seq"] < 1:
            raise ValueError("Invalid current frame sequence")
        if not isinstance(frame.get("scars"), list):
            raise ValueError("Invalid current frame scars")
        scars = {scar["id"]: snapshot["scars"][scar["id"]] for scar in frame["scars"]}
        projection = build_projection(
            snapshot["final"], snapshot["head"], snapshot["source_head"],
            snapshot["observed_at"], snapshot["commits"], [frame], scars,
        )
        projection["history"] = {"current_only": True, "total_frames": len(frames),
                                 "last_sequence": frame["seq"]}
        body = json.dumps(projection, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    except (KeyError, IndexError, TypeError, RecursionError) as error:
        raise ValueError("Malformed current snapshot cache") from error
    if len(body) <= min(CURRENT_SNAPSHOT_TARGET_BYTES, CURRENT_SNAPSHOT_MAX_BYTES):
        return {"current.json": body}
    # GitHub Pages serves these as static files. Keep the complete projection
    # in a gzip companion when the plain JSON will not fit the transfer budget.
    compressed = gzip.compress(body, mtime=0)
    path = f"current/{hashlib.sha256(compressed).hexdigest()[:16]}.json.gz"
    manifest = json.dumps({
        "version": 1, "gzip": path, "journal_head": projection["journal_head"],
        "source_head": projection["source_head"], "history": projection["history"],
    }, separators=(",", ":")).encode()
    size = len(manifest) + len(compressed)
    if size > CURRENT_SNAPSHOT_MAX_BYTES:
        raise ValueError(f"The current snapshot is {size:,} bytes and exceeds its first-paint size budget "
                         f"of {CURRENT_SNAPSHOT_MAX_BYTES:,} bytes")
    if size > CURRENT_SNAPSHOT_TARGET_BYTES:
        print(f"house publish: the current snapshot is {size:,} bytes, over its "
              f"{CURRENT_SNAPSHOT_TARGET_BYTES:,}-byte target; slim the latest frame", file=sys.stderr)
    return {"current.json": manifest, path: compressed}


def retain_current_snapshots(record: Record, previous: str | None, contents: dict[str, bytes]) -> None:
    """Keep newest-first compressed snapshots across replacement Pages trees."""
    retained = [path for path in contents if CURRENT_COMPANION.fullmatch(path)]
    size = sum(len(contents[path]) for path in retained)
    candidates = []
    if previous:
        # The previous listing also bootstraps retention on the first upgraded
        # publication. A plain (large) snapshot is not a companion listing.
        for name in ("current.json", CURRENT_RETENTION_INDEX):
            raw = committed_blob(record, previous, name, optional=True)
            if raw is None or len(raw) > 4096:
                continue
            try:
                value = json.loads(raw)
            except (ValueError, UnicodeError):
                continue
            if name == "current.json" and isinstance(value, dict):
                candidates.append(value.get("gzip"))
            elif name == CURRENT_RETENTION_INDEX and isinstance(value, list):
                candidates.extend(value[:CURRENT_RETAINED_COUNT])
    seen = set(retained)
    for path in candidates:
        if len(retained) >= CURRENT_RETAINED_COUNT:
            break
        if not isinstance(path, str) or not CURRENT_COMPANION.fullmatch(path) or path in seen:
            continue
        seen.add(path)
        body = committed_blob(record, previous, path, optional=True)
        if body is None or len(body) > MAX_PUBLIC_BLOB or hashlib.sha256(body).hexdigest()[:16] != path[8:24]:
            continue
        if size + len(body) > CURRENT_RETAINED_BYTES:
            # Preserve a contiguous newest-first window rather than keeping
            # older small files at the expense of a newer snapshot.
            break
        contents[path] = body
        retained.append(path)
        size += len(body)
    if retained:
        contents[CURRENT_RETENTION_INDEX] = json.dumps(retained, separators=(",", ":")).encode()


def chronicle_body(record: Record, contents: dict[str, bytes]) -> bytes:
    """The Chronicle Room page for the journal as it stands now."""
    from . import chronicle_page
    state, events, _ = record.read()
    numbered = [event | {"sequence": sequence} for sequence, event in enumerate(events, 1)]
    return chronicle_page.render_html(chronicle_page.select_milestones(numbered), through=len(numbered),
                                      house_id=state.get("house_id"),
                                      catalog=json.loads(contents.get("projects.json", b"null"))).encode()


def publish(record: Record, *, push=False) -> dict:
    private = record.common / "house-home"
    private.mkdir(mode=0o700, exist_ok=True)
    with (private / "publisher.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        history_body, summary, parts, snapshot = _history_with_cache(record, private)
        head = summary["source_head"]
        if not head:
            raise ValueError("No source HEAD")
        contents = {name: committed_blob(record, head, "site/" + name)
                    for name in ("index.html", "house.css", "house.js")}
        missing_page = committed_blob(record, head, "site/404.html", optional=True)
        if missing_page is not None:
            contents["404.html"] = missing_page
        contents.update(project_contents(record, head))
        if b"craft.json" in contents["house.js"]:
            from .craft_outcomes import public_window
            contents["craft.json"] = json.dumps(public_window(
                snapshot["recent_events"], summary["seq"], summary["journal_head"], head,
            ), separators=(",", ":")).encode()
        # Only the Chronicle page is public, never its journal input. It is
        # rebuilt from the journal on every publication so it cannot go stale;
        # the committed page is the fallback (and decides whether the room exists).
        chronicle = committed_blob(record, head, "site/chronicle/index.html", optional=True)
        if chronicle is not None:
            try:
                chronicle = chronicle_body(record, contents)
            except (OSError, ValueError, KeyError, TypeError):
                pass
            contents["chronicle/index.html"] = chronicle
        # Optional Ten-Second Door summary: always rebuilt from the public journal,
        # activated once site/house.js requests now.json or site/now.json is committed.
        door_marker = committed_blob(record, head, "site/now.json", optional=True)
        if door_marker is not None or b"now.json" in contents["house.js"]:
            contents["now.json"] = now_bytes(
                final=snapshot["final"],
                head=snapshot["head"],
                source_head=snapshot["source_head"],
                observed_at=snapshot["observed_at"],
                commits=snapshot["commits"],
                frames=snapshot["frames"],
                nodes=snapshot["nodes"],
                catalog_raw=contents.get("projects.json"),
            )
        contents.update(parts)
        contents["history.json"] = history_body
        contents.update(current_snapshot_files(snapshot))
        # Visitors poll this tiny file and fetch a new snapshot when it changes.
        contents["head.json"] = json.dumps(summary, separators=(",", ":"), sort_keys=True).encode()
        try:
            contents["balance.json"] = json.dumps(building_balance(record, head), separators=(",", ":")).encode()
        except (OSError, ValueError, subprocess.SubprocessError):
            pass  # The balance is a view; never block publication of the record.
        contents[".nojekyll"] = b""
        ref = "refs/heads/" + BRANCH
        previous = record.ref(ref)
        retain_current_snapshots(record, previous, contents)
        if any(len(body) > MAX_PUBLIC_BLOB for body in contents.values()):
            raise ValueError("Public snapshot exceeds the publication size budget")
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
                current_wire = old.get("history_version") == 4
            except ValueError:
                old_wire = json.loads(record.git("show", previous + ":history.json"))
                old = decode(old_wire, lambda path: record.git("show", previous + ":" + path))
                current_wire = old_wire.get("version") == 4
            if (not recovering and current_wire
                    and (old["journal_head"], old["source_head"]) == (summary["journal_head"], summary["source_head"])
                    and record.git("ls-tree", previous, "--", "current.json")):
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
        print(json.dumps({"published": False, "error": type(error).__name__, "detail": str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
