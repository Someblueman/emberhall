#!/usr/bin/env python3
"""Skein milestone 1: portable, static Git review packets.

Python 3.10+ and Git are the only requirements. Skein invokes local Git commands;
it never contacts a forge, runs a hook, or applies/merges another repository.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import difflib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Iterable


FORMAT = "review-skein-packet"
COMMENT_FORMAT = "review-skein-comments"
ANCHOR_FORMAT = "review-skein-anchors"
VERSION = 1
COMMENT_VERSION = 2
DEFAULT_MAX_FILE_BYTES = 256 * 1024
JSON_LIMIT = 32 * 1024 * 1024
GIT_TIMEOUT = 120
OID_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z")


class SkeinError(ValueError):
    """A packet cannot be exported, read or annotated honestly."""


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    command = ["git", "--no-pager", "-C", str(repository), *arguments]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=GIT_TIMEOUT,
        )
    except FileNotFoundError as exc:
        raise SkeinError("Git is not installed or is not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise SkeinError(f"local Git {arguments[0]} exceeded {GIT_TIMEOUT} seconds") from exc
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if len(detail) > 2000:
            detail = detail[:1997] + "..."
        raise SkeinError(f"git {arguments[0]} failed: {detail or 'unknown Git error'}")
    return result


def _oid(value: Any, label: str = "commit") -> str:
    if not isinstance(value, str) or OID_RE.fullmatch(value) is None:
        raise SkeinError(f"{label} must be a full lowercase Git object ID")
    return value


def _safe_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise SkeinError("repository path must be a nonempty UTF-8 string")
    if (value.startswith("/") or "\\" in value or ":" in value
            or any(part in {"", ".", ".."} for part in value.split("/"))
            or any(part.casefold() == ".git" for part in value.split("/"))
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise SkeinError(f"unsafe or nonportable repository path: {value!r}")
    return value


def _decode_path(value: bytes) -> str:
    try:
        return _safe_path(value.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise SkeinError("a changed repository path is not valid UTF-8") from exc


def _worktree(repository: Path) -> Path:
    repository = repository.expanduser().resolve()
    if not repository.is_dir():
        raise SkeinError(f"repository directory does not exist: {repository}")
    inside = _git(repository, "rev-parse", "--is-inside-work-tree").stdout.strip()
    if inside != b"true":
        raise SkeinError("Skein milestone 1 requires a non-bare worktree")
    root = Path(_git(repository, "rev-parse", "--show-toplevel").stdout.decode("utf-8").strip())
    return root.resolve()


def _all_refs(repository: Path) -> set[str]:
    output = _git(repository, "for-each-ref", "--format=%(refname)").stdout
    return {line.decode("utf-8") for line in output.splitlines() if line}


def _reject_ambiguous_name(repository: Path, ref: str) -> None:
    if not ref or ref.startswith("-") or any(ord(c) < 32 or ord(c) == 127 for c in ref):
        raise SkeinError(f"invalid Git ref: {ref!r}")
    if ref == "HEAD" or ref.startswith("refs/"):
        return
    # Git's usual ref search rules. In particular, do not silently choose a
    # branch when a tag with the same short name points somewhere else.
    possible = (
        f"refs/{ref}", f"refs/tags/{ref}", f"refs/heads/{ref}",
        f"refs/remotes/{ref}", f"refs/remotes/{ref}/HEAD",
    )
    matches = sorted(_all_refs(repository).intersection(possible))
    if len(matches) > 1:
        raise SkeinError(f"ambiguous Git ref {ref!r}: {', '.join(matches)}")
    if re.fullmatch(r"[0-9a-fA-F]{4,39}", ref):
        rows = _git(repository, "rev-parse", f"--disambiguate={ref}").stdout.splitlines()
        if len(rows) > 1:
            raise SkeinError(f"ambiguous abbreviated Git object ID: {ref}")


def _resolve_commit(repository: Path, ref: str) -> str:
    _reject_ambiguous_name(repository, ref)
    result = _git(repository, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
    # Some Git versions diagnose a ref ambiguity as a warning yet still print
    # one candidate. Treat that warning as rejection rather than choosing one.
    warning = result.stderr.decode("utf-8", errors="replace")
    if "ambiguous" in warning.casefold():
        raise SkeinError(f"ambiguous Git ref {ref!r}: {warning.strip()}")
    try:
        value = result.stdout.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise SkeinError(f"Git returned a non-ASCII object ID for {ref!r}") from exc
    return _oid(value, f"object resolved from {ref!r}")


def _require_clean(repository: Path) -> None:
    status = _git(
        repository, "status", "--porcelain=v1", "-z", "--untracked-files=all",
        "--ignore-submodules=none",
    ).stdout
    if status:
        first = status.split(b"\0", 1)[0].decode("utf-8", errors="replace")
        raise SkeinError(
            "worktree or index is not clean (tracked, staged and untracked changes "
            f"are all rejected); first status: {first!r}"
        )


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    kind: str
    oid: str
    path: str


def _tree(repository: Path, commit: str) -> dict[str, TreeEntry]:
    output = _git(repository, "ls-tree", "-r", "-z", commit, "--").stdout
    result: dict[str, TreeEntry] = {}
    for record in output.split(b"\0"):
        if not record:
            continue
        try:
            meta, raw_path = record.split(b"\t", 1)
            mode, kind, oid = meta.decode("ascii").split(" ")
        except (ValueError, UnicodeDecodeError) as exc:
            raise SkeinError("Git returned a malformed tree entry") from exc
        path = _decode_path(raw_path)
        if path in result:
            raise SkeinError(f"duplicate path in Git tree: {path!r}")
        result[path] = TreeEntry(mode, kind, _oid(oid, "tree object"), path)
    return result


@dataclass(frozen=True)
class Change:
    status: str
    old_path: str | None
    new_path: str | None

    @property
    def display_path(self) -> str:
        if self.old_path == self.new_path:
            return self.new_path or self.old_path or ""
        return f"{self.old_path or ''} → {self.new_path or ''}"


def _changes(repository: Path, base: str, head: str) -> list[Change]:
    output = _git(
        repository, "diff", "--name-status", "-z", "--find-renames",
        "--no-ext-diff", "--no-textconv", base, head, "--",
    ).stdout
    fields = output.split(b"\0")
    index = 0
    result: list[Change] = []
    while index < len(fields):
        if not fields[index]:
            index += 1
            continue
        try:
            marker = fields[index].decode("ascii")
        except UnicodeDecodeError as exc:
            raise SkeinError("Git returned an invalid name-status marker") from exc
        index += 1
        code = marker[:1]
        if marker[1:] and not marker[1:].isdigit():
            raise SkeinError(f"unsupported Git name-status marker: {marker!r}")
        width = 2 if code in {"R", "C"} else 1
        if index + width > len(fields):
            raise SkeinError("truncated Git name-status output")
        paths = [_decode_path(value) for value in fields[index:index + width]]
        index += width
        if code in {"R", "C"}:
            result.append(Change("renamed" if code == "R" else "copied", paths[0], paths[1]))
        elif code == "A":
            result.append(Change("added", None, paths[0]))
        elif code == "D":
            result.append(Change("deleted", paths[0], None))
        elif code == "M":
            result.append(Change("modified", paths[0], paths[0]))
        elif code == "T":
            raise SkeinError(f"file type changes are not supported: {paths[0]!r}")
        else:
            raise SkeinError(f"unsupported or unmerged change {marker!r} at {paths[0]!r}")
    return result


class TextLines(list[str]):
    """Logical Git lines plus the new-line-at-EOF bit a plain list would lose."""

    def __init__(self, values: Iterable[str], final_newline: bool):
        super().__init__(values)
        self.final_newline = final_newline


def _lines(text: str) -> TextLines:
    if not text:
        return TextLines([], False)
    values = text.split("\n")
    final_newline = text.endswith("\n")
    if final_newline:
        values.pop()
    return TextLines(values, final_newline)


class BlobReader:
    def __init__(self, repository: Path, maximum: int):
        self.repository = repository
        self.maximum = maximum
        self.cache: dict[str, list[str]] = {}

    def read(self, entry: TreeEntry | None) -> list[str]:
        if entry is None:
            return []
        if entry.kind != "blob" or entry.mode not in {"100644", "100755"}:
            raise SkeinError(
                f"only regular file blobs are supported; symlinks, submodules and other "
                f"modes are rejected: {entry.path!r} ({entry.mode} {entry.kind})"
            )
        if entry.oid in self.cache:
            return self.cache[entry.oid]
        raw_size = _git(self.repository, "cat-file", "-s", entry.oid).stdout.strip()
        try:
            size = int(raw_size)
        except ValueError as exc:
            raise SkeinError(f"Git returned an invalid blob size for {entry.path!r}") from exc
        if size > self.maximum:
            raise SkeinError(
                f"file {entry.path!r} is {size} bytes, above the {self.maximum}-byte limit"
            )
        content = _git(self.repository, "cat-file", "blob", entry.oid).stdout
        if len(content) != size:
            raise SkeinError(f"blob size changed while reading {entry.path!r}")
        if b"\0" in content:
            raise SkeinError(f"binary file is not renderable as text: {entry.path!r}")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SkeinError(f"file is not UTF-8 text: {entry.path!r}") from exc
        result = _lines(text)
        self.cache[entry.oid] = result
        return result


@dataclass(frozen=True)
class Anchor:
    commit: str
    path: str
    side: str
    line: int
    text: str

    def __post_init__(self) -> None:
        _oid(self.commit)
        _safe_path(self.path)
        if self.side not in {"old", "new"}:
            raise SkeinError("comment anchor side must be 'old' or 'new'")
        if type(self.line) is not int or self.line < 1:
            raise SkeinError("comment anchor line must be a positive integer")
        if not isinstance(self.text, str) or "\0" in self.text:
            raise SkeinError("invalid comment anchor text")

    def to_dict(self) -> dict[str, Any]:
        return {
            "commit": self.commit, "path": self.path, "side": self.side,
            "line": self.line, "text": self.text,
        }

    @classmethod
    def from_dict(cls, value: Any) -> Anchor:
        if not isinstance(value, dict) or set(value) != {"commit", "path", "side", "line", "text"}:
            raise SkeinError("malformed comment anchor")
        return cls(value["commit"], value["path"], value["side"], value["line"], value["text"])


@dataclass(frozen=True)
class Comment:
    identifier: str
    anchor: Anchor
    body: str
    state: str = "anchored"
    rebased_from: Anchor | None = None
    orphan_reason: str | None = None
    resolution: str = "open"

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or ID_RE.fullmatch(self.identifier) is None:
            raise SkeinError("comment ID must be 1-100 safe ASCII characters")
        if not isinstance(self.anchor, Anchor):
            raise SkeinError("comment requires a valid anchor")
        if (not isinstance(self.body, str) or not self.body.strip()
                or len(self.body) > 20000 or "\0" in self.body):
            raise SkeinError("comment body must be nonempty text of at most 20000 characters")
        if self.state not in {"anchored", "orphan"}:
            raise SkeinError("comment state must be 'anchored' or 'orphan'")
        if self.rebased_from is not None and not isinstance(self.rebased_from, Anchor):
            raise SkeinError("rebased_from must be an anchor or null")
        if self.state == "orphan":
            if not isinstance(self.orphan_reason, str) or not self.orphan_reason.strip():
                raise SkeinError("an orphan comment requires an explicit reason")
        elif self.orphan_reason is not None:
            raise SkeinError("an anchored comment cannot retain an orphan reason")
        if not isinstance(self.resolution, str) or self.resolution not in {"open", "resolved"}:
            raise SkeinError("comment resolution must be 'open' or 'resolved'")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "anchor": self.anchor.to_dict(),
            "body": self.body,
            "state": self.state,
            "rebased_from": self.rebased_from.to_dict() if self.rebased_from else None,
            "orphan_reason": self.orphan_reason,
            "resolution": self.resolution,
        }

    @classmethod
    def from_dict(cls, value: Any) -> Comment:
        required = {"id", "anchor", "body", "state", "rebased_from", "orphan_reason", "resolution"}
        if not isinstance(value, dict) or set(value) != required:
            raise SkeinError("malformed comment record")
        previous = value["rebased_from"]
        return cls(
            value["id"], Anchor.from_dict(value["anchor"]), value["body"], value["state"],
            Anchor.from_dict(previous) if previous is not None else None,
            value["orphan_reason"],
            value["resolution"],
        )


def reanchor(comment: Comment, new_commit: str, available: Iterable[Anchor]) -> Comment:
    """Rebind after a rebase, or preserve a visible orphan instead of guessing.

    The same path/side/line/text wins first. Otherwise exactly one matching text
    on that path and side is enough. Missing, changed-path and duplicate-text
    matches become an explicit orphan; they never jump to another file.
    """
    new_commit = _oid(new_commit, "rebased commit")
    candidates = list(available)
    if any(not isinstance(item, Anchor) or item.commit != new_commit for item in candidates):
        raise SkeinError("all rebase anchors must belong to the new commit")
    original = comment.anchor
    same_file = [
        item for item in candidates
        if item.path == original.path and item.side == original.side
    ]
    exact = [
        item for item in same_file
        if item.line == original.line and item.text == original.text
    ]
    matches = exact or [item for item in same_file if item.text == original.text]
    if len(matches) == 1:
        return replace(
            comment, anchor=matches[0], state="anchored",
            rebased_from=original, orphan_reason=None,
        )
    if not same_file:
        reason = "rebase: original path and side are missing"
    elif not matches:
        reason = "rebase: anchor line and uniquely matching text are missing"
    else:
        reason = "rebase: anchor text is ambiguous on duplicate lines"
    retained = replace(original, commit=new_commit)
    return replace(
        comment, anchor=retained, state="orphan", rebased_from=original,
        orphan_reason=reason,
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SkeinError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise SkeinError(f"packet JSON is missing or is not a regular file: {path.name}")
    data = path.read_bytes()
    if len(data) > JSON_LIMIT:
        raise SkeinError(f"packet JSON exceeds {JSON_LIMIT} bytes: {path.name}")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SkeinError(f"invalid JSON in {path.name}: {exc}") from exc


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def dumps_comments(comments: Iterable[Comment]) -> str:
    values = list(comments)
    if any(not isinstance(item, Comment) for item in values):
        raise SkeinError("only Comment records can be serialized")
    identifiers = [item.identifier for item in values]
    if len(identifiers) != len(set(identifiers)):
        raise SkeinError("duplicate comment ID")
    return _json_text({
        "format": COMMENT_FORMAT, "version": COMMENT_VERSION,
        "comments": [item.to_dict() for item in values],
    })


def loads_comments(text: str) -> list[Comment]:
    try:
        value = json.loads(text, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise SkeinError(f"invalid comments JSON: {exc}") from exc
    if (not isinstance(value, dict) or set(value) != {"format", "version", "comments"}
            or value["format"] != COMMENT_FORMAT or type(value["version"]) is not int
            or value["version"] not in {1, COMMENT_VERSION} or not isinstance(value["comments"], list)):
        raise SkeinError("unsupported comments header")
    if value["version"] == 1:
        raise SkeinError("comments version 1 requires: migrate-comments PACKET")
    comments = [Comment.from_dict(item) for item in value["comments"]]
    identifiers = [item.identifier for item in comments]
    if len(identifiers) != len(set(identifiers)):
        raise SkeinError("duplicate comment ID")
    return comments


def _load_packet(packet: Path) -> dict[str, Any]:
    value = _read_json(packet / "packet.json")
    required = {"format", "version", "base", "head", "bundle", "diff", "anchors", "comments", "files"}
    if (not isinstance(value, dict) or set(value) != required
            or value["format"] != FORMAT or type(value["version"]) is not int
            or value["version"] != VERSION or not isinstance(value["files"], list)):
        raise SkeinError("unsupported or malformed packet header")
    for key in ("base", "head"):
        if not isinstance(value[key], dict) or set(value[key]) != {"ref", "commit"}:
            raise SkeinError(f"malformed packet {key} identity")
        if not isinstance(value[key]["ref"], str) or not value[key]["ref"]:
            raise SkeinError(f"malformed packet {key} ref")
        _oid(value[key]["commit"], key)
    fixed = {"bundle": "changes.bundle", "diff": "review.html",
             "anchors": "anchors.json", "comments": "comments.json"}
    if any(value[key] != expected for key, expected in fixed.items()):
        raise SkeinError("packet member names do not match the version-1 layout")
    return value


def _load_anchors(packet: Path) -> list[Anchor]:
    value = _read_json(packet / "anchors.json")
    if (not isinstance(value, dict) or set(value) != {"format", "version", "anchors"}
            or value["format"] != ANCHOR_FORMAT or type(value["version"]) is not int
            or value["version"] != VERSION or not isinstance(value["anchors"], list)):
        raise SkeinError("unsupported or malformed anchor file")
    return [Anchor.from_dict(item) for item in value["anchors"]]


def _atomic_comments(packet: Path, comments: list[Comment]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".comments-", dir=packet)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(dumps_comments(comments))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, packet / "comments.json")
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def migrate_comments(packet: Path) -> list[Comment]:
    """Explicitly upgrade a v1 comments file; validate v2 without rewriting it."""
    packet = packet.expanduser().resolve()
    _load_packet(packet)
    value = _read_json(packet / "comments.json")
    legacy = (isinstance(value, dict) and type(value.get("version")) is int
              and value["version"] == 1)
    if legacy:
        records = value.get("comments")
        required = {"id", "anchor", "body", "state", "rebased_from", "orphan_reason"}
        if (not isinstance(records, list)
                or any(not isinstance(item, dict) or set(item) != required for item in records)):
            raise SkeinError("malformed version-1 comment record")
        value = {**value, "version": COMMENT_VERSION,
                 "comments": [{**item, "resolution": "open"} for item in records]}
    comments = loads_comments(_json_text(value))
    if legacy:
        _atomic_comments(packet, comments)
    return comments


def update_comment(
    packet: Path, identifier: str, *, body: str | None = None,
    resolution: str | None = None,
) -> Comment:
    """Edit one existing comment without moving its anchor or changing its ID."""
    if body is None and resolution is None:
        raise SkeinError("provide a comment body or resolution to update")
    packet = packet.expanduser().resolve()
    _load_packet(packet)
    comments = loads_comments(_json_text(_read_json(packet / "comments.json")))
    for index, comment in enumerate(comments):
        if comment.identifier == identifier:
            updated = replace(
                comment, body=comment.body if body is None else body,
                resolution=comment.resolution if resolution is None else resolution,
            )
            comments[index] = updated
            _atomic_comments(packet, comments)
            return updated
    raise SkeinError(f"comment ID does not exist: {identifier}")


def add_comment(
    packet: Path, identifier: str, commit: str, path: str, side: str,
    line: int, body: str,
) -> Comment:
    """Validate and append one offline comment inside an exported packet."""
    packet = packet.expanduser().resolve()
    metadata = _load_packet(packet)
    if not packet.is_dir():
        raise SkeinError("packet is not a directory")
    valid_commits = {metadata["base"]["commit"], metadata["head"]["commit"]}
    if commit not in valid_commits:
        raise SkeinError("comment commit is neither the packet base nor its head")
    matches = [
        item for item in _load_anchors(packet)
        if item.commit == commit and item.path == path
        and item.side == side and item.line == line
    ]
    if len(matches) != 1:
        raise SkeinError("comment anchor does not name exactly one rendered line")
    comments = loads_comments((packet / "comments.json").read_text(encoding="utf-8"))
    if any(item.identifier == identifier for item in comments):
        raise SkeinError(f"comment ID already exists: {identifier}")
    comment = Comment(identifier, matches[0], body)
    _atomic_comments(packet, [*comments, comment])
    return comment


ROW_STATUS = {
    "equal": "Unchanged", "insert": "Added", "delete": "Removed",
    "replace": "Changed", "meta": "Note",
}


def _row(old_number: int | None, new_number: int | None,
         old: str, new: str, kind: str) -> str:
    def number(value: int | None) -> str:
        return str(value) if value is not None else ""
    # Change kind must be text, not row colour alone, for screen readers.
    status = f'<span class="sr">{ROW_STATUS[kind]}.</span> '
    return (
        f'<tr class="{kind}"><th scope="row" class="number old-number">{status}{number(old_number)}</th>'
        f'<th scope="row" class="number new-number">{number(new_number)}</th>'
        f'<td class="old code">{html.escape(old)}</td>'
        f'<td class="new code">{html.escape(new)}</td></tr>\n'
    )


def _diff_rows(old: list[str], new: list[str]) -> str:
    rows: list[str] = []
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for operation, a1, a2, b1, b2 in matcher.get_opcodes():
        if operation == "equal":
            for offset in range(a2 - a1):
                rows.append(_row(a1 + offset + 1, b1 + offset + 1,
                                 old[a1 + offset], new[b1 + offset], "equal"))
        elif operation == "replace":
            width = max(a2 - a1, b2 - b1)
            for offset in range(width):
                ai, bi = a1 + offset, b1 + offset
                rows.append(_row(
                    ai + 1 if ai < a2 else None, bi + 1 if bi < b2 else None,
                    old[ai] if ai < a2 else "", new[bi] if bi < b2 else "", "replace",
                ))
        elif operation == "delete":
            for ai in range(a1, a2):
                rows.append(_row(ai + 1, None, old[ai], "", "delete"))
        elif operation == "insert":
            for bi in range(b1, b2):
                rows.append(_row(None, bi + 1, "", new[bi], "insert"))
    if old or new:
        old_final = getattr(old, "final_newline", True)
        new_final = getattr(new, "final_newline", True)
        if not old_final or not new_final:
            rows.append(_row(
                None, None,
                "" if old_final else "\\ No newline at end of file",
                "" if new_final else "\\ No newline at end of file",
                "meta",
            ))
    return "".join(rows)


STYLE = """
:root { color-scheme: light dark; --bg: #fff; --fg: #24292f; --muted: #6e7781;
  --border: #d0d7de; --add: #dafbe1; --del: #ffebe9; --change: #fff8c5; }
@media (prefers-color-scheme: dark) { :root { --bg: #0d1117; --fg: #e6edf3;
  --muted: #8b949e; --border: #30363d; --add: #12261e; --del: #2d1618; --change: #302b12; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.5 system-ui, sans-serif; }
main { max-width: 1600px; margin: auto; padding: 1rem; }
.identity { overflow-wrap: anywhere; } .identity code { user-select: all; }
nav { margin: 1rem 0; } nav li { margin: .3rem 0; }
section { margin: 2rem 0; } h2 { font-size: 1.1rem; overflow-wrap: anywhere; }
table { border-collapse: collapse; width: 100%; table-layout: fixed; }
caption { text-align: left; color: var(--muted); padding: .3rem 0; }
th, td { border: 1px solid var(--border); vertical-align: top; }
th.number { width: 4.5em; text-align: right; color: var(--muted); font-weight: normal;
  user-select: none; }
td.code { white-space: pre-wrap; overflow-wrap: anywhere; tab-size: 4;
  font: 13px/1.45 ui-monospace, SFMono-Regular, Consolas, monospace; }
tr.insert td.new { background: var(--add); } tr.delete td.old { background: var(--del); }
tr.replace td.old { background: var(--del); } tr.replace td.new { background: var(--add); }
tr.meta td { color: var(--muted); font-style: italic; }
a { color: inherit; } footer { color: var(--muted); margin-top: 2rem; }
.sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; border: 0; }
.skip { position: absolute; left: -9999px; top: 0; background: var(--bg); color: var(--fg);
  padding: .5rem 1rem; z-index: 1; }
.skip:focus { left: 0; }
a:focus-visible { outline: 3px solid var(--fg); outline-offset: 2px; }
.scroll { overflow-x: auto; }
@media (max-width: 640px) { table { min-width: 34rem; } main { padding: .5rem; } }
"""


def _render_html(metadata: dict[str, Any], rendered: list[tuple[Change, list[str], list[str]]]) -> str:
    sections: list[str] = []
    navigation: list[str] = []
    for index, (change, old, new) in enumerate(rendered, 1):
        title = f"{change.status}: {change.display_path}"
        navigation.append(f'<li><a href="#file-{index}">{html.escape(title)}</a></li>')
        sections.append(
            f'<section id="file-{index}" aria-labelledby="file-{index}-title">'
            f'<h2 id="file-{index}-title">{html.escape(title)}</h2>\n'
            f'<div class="scroll"><table><caption>Old line and new line; {len(old)} old / {len(new)} new</caption>\n'
            '<thead><tr><th scope="col">Old</th><th scope="col">New</th>'
            '<th scope="col">Base text</th><th scope="col">Head text</th></tr></thead>\n'
            f'<tbody>{_diff_rows(old, new)}</tbody></table></div></section>\n'
        )
    if not sections:
        navigation.append("<li>No textual changes between these commits.</li>")
    body = "".join(sections) or "<p>The two commits have identical file trees.</p>"
    base = html.escape(f'{metadata["base"]["ref"]} ({metadata["base"]["commit"]})')
    head = html.escape(f'{metadata["head"]["ref"]} ({metadata["head"]["commit"]})')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Skein review packet</title><style>{STYLE}</style></head>
<body><a class="skip" href="#files">Skip to changed files</a><main><h1>Skein review packet</h1>
<p class="identity">Base: <code>{base}</code><br>Head: <code>{head}</code></p>
<p>This file is static. No network, account, JavaScript or live review service is used.</p>
<nav id="files" aria-label="Changed files"><ol>{''.join(navigation)}</ol></nav>
{body}<footer>Review Skein packet format {VERSION}. The adjacent bundle carries the Git objects;
hashes bind bytes, not people. Comments reside in comments.json.</footer></main></body></html>
'''


def _make_bundle(worktree: Path, staging: Path, base: str, head: str) -> None:
    """Create an independent full bundle containing exactly the review histories.

    A private temporary bare repository gives arbitrary resolved commits stable
    branch names without changing the user's refs. Its temporary alternate only
    reads the original object store; ``bundle create`` copies every reachable
    object into the standalone packet before that alternate is discarded.
    """
    raw_objects = _git(worktree, "rev-parse", "--git-path", "objects").stdout
    try:
        object_directory = Path(raw_objects.decode("utf-8").strip())
    except UnicodeDecodeError as exc:
        raise SkeinError("the Git object-directory path is not UTF-8") from exc
    if not object_directory.is_absolute():
        object_directory = worktree / object_directory
    object_directory = object_directory.resolve()
    if not object_directory.is_dir() or "\n" in str(object_directory) or "\r" in str(object_directory):
        raise SkeinError("cannot safely name the source Git object directory")
    bundle_repository = staging / "bundle-source.git"
    _git(staging, "init", "--bare", "--quiet", str(bundle_repository))
    _write(bundle_repository / "objects" / "info" / "alternates", str(object_directory) + "\n")
    _git(bundle_repository, "update-ref", "refs/heads/skein-base", base)
    _git(bundle_repository, "update-ref", "refs/heads/skein-head", head)
    _git(
        bundle_repository, "bundle", "create", str(staging / "changes.bundle"),
        "refs/heads/skein-base", "refs/heads/skein-head",
    )


def verify_packet(packet: Path) -> tuple[str, str]:
    """Clone the full bundle in isolation and prove both immutable IDs exist."""
    packet = packet.expanduser().resolve()
    metadata = _load_packet(packet)
    base, head = metadata["base"]["commit"], metadata["head"]["commit"]
    _load_anchors(packet)
    comments_path = packet / "comments.json"
    if comments_path.is_symlink() or not comments_path.is_file():
        raise SkeinError("packet comments are missing or not a regular file")
    loads_comments(comments_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="skein-verify-") as temporary:
        root = Path(temporary)
        clone = root / "clone"
        _git(root, "clone", "--quiet", "--no-checkout", str(packet / "changes.bundle"), str(clone))
        _git(clone, "bundle", "verify", str(packet / "changes.bundle"))
        for commit in (base, head):
            _git(clone, "cat-file", "-e", f"{commit}^{{commit}}")
    return base, head


def export_packet(
    repository: Path, base_ref: str, head_ref: str, output: Path,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> dict[str, Any]:
    """Export a deterministic packet and atomically publish a new directory."""
    if type(max_file_bytes) is not int or max_file_bytes < 1:
        raise SkeinError("max_file_bytes must be a positive integer")
    worktree = _worktree(repository)
    output = output.expanduser().resolve()
    if output == worktree or output.is_relative_to(worktree):
        raise SkeinError("packet output must be outside the source worktree")
    if output.exists() or output.is_symlink():
        raise SkeinError("packet output must be a new path; refusing to overwrite anything")
    base = _resolve_commit(worktree, base_ref)
    head = _resolve_commit(worktree, head_ref)
    _require_clean(worktree)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.parent.is_dir():
        raise SkeinError("packet output parent is not a directory")
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    published = False
    try:
        old_tree, new_tree = _tree(worktree, base), _tree(worktree, head)
        changes = _changes(worktree, base, head)
        reader = BlobReader(worktree, max_file_bytes)
        rendered: list[tuple[Change, list[str], list[str]]] = []
        anchors: list[Anchor] = []
        file_records: list[dict[str, Any]] = []
        for change in changes:
            old_entry = old_tree.get(change.old_path) if change.old_path else None
            new_entry = new_tree.get(change.new_path) if change.new_path else None
            old = reader.read(old_entry)
            new = reader.read(new_entry)
            rendered.append((change, old, new))
            file_records.append({
                "status": change.status, "old_path": change.old_path,
                "new_path": change.new_path, "old_lines": len(old), "new_lines": len(new),
            })
            if change.old_path:
                anchors.extend(Anchor(base, change.old_path, "old", number, text)
                               for number, text in enumerate(old, 1))
            if change.new_path:
                anchors.extend(Anchor(head, change.new_path, "new", number, text)
                               for number, text in enumerate(new, 1))
        metadata = {
            "format": FORMAT, "version": VERSION,
            "base": {"ref": base_ref, "commit": base},
            "head": {"ref": head_ref, "commit": head},
            "bundle": "changes.bundle", "diff": "review.html",
            "anchors": "anchors.json", "comments": "comments.json",
            "files": file_records,
        }
        _write(staging / "packet.json", _json_text(metadata))
        _write(staging / "anchors.json", _json_text({
            "format": ANCHOR_FORMAT, "version": VERSION,
            "anchors": [item.to_dict() for item in anchors],
        }))
        _write(staging / "comments.json", dumps_comments([]))
        _write(staging / "review.html", _render_html(metadata, rendered))
        _make_bundle(worktree, staging, base, head)
        shutil.rmtree(staging / "bundle-source.git")
        verify_packet(staging)
        staging.rename(output)
        published = True
        return metadata
    finally:
        if not published:
            shutil.rmtree(staging, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    export = subcommands.add_parser("export", help="export a new portable review packet")
    export.add_argument("repository", type=Path)
    export.add_argument("base_ref")
    export.add_argument("head_ref")
    export.add_argument("output", type=Path)
    export.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    verify = subcommands.add_parser("verify", help="clone a packet bundle and verify its commits")
    verify.add_argument("packet", type=Path)
    comment = subcommands.add_parser("comment", help="record one validated offline comment")
    comment.add_argument("packet", type=Path)
    comment.add_argument("--id", required=True, dest="identifier")
    comment.add_argument("--commit", required=True)
    comment.add_argument("--path", required=True)
    comment.add_argument("--side", choices=("old", "new"), required=True)
    comment.add_argument("--line", type=int, required=True)
    comment.add_argument("--body", required=True)
    edit = subcommands.add_parser("edit-comment", help="replace an existing comment body")
    edit.add_argument("packet", type=Path)
    edit.add_argument("--id", required=True, dest="identifier")
    edit.add_argument("--body", required=True)
    for command, help_text in (
        ("resolve-comment", "mark an existing comment resolved"),
        ("reopen-comment", "mark an existing comment open"),
    ):
        resolution = subcommands.add_parser(command, help=help_text)
        resolution.add_argument("packet", type=Path)
        resolution.add_argument("--id", required=True, dest="identifier")
    migrate = subcommands.add_parser("migrate-comments", help="upgrade v1 comments to v2")
    migrate.add_argument("packet", type=Path)
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "export":
            metadata = export_packet(
                arguments.repository, arguments.base_ref, arguments.head_ref,
                arguments.output, arguments.max_file_bytes,
            )
            print(f"Exported Skein packet to {arguments.output}")
            print(f"Base {metadata['base']['commit']} -> head {metadata['head']['commit']}")
        elif arguments.command == "verify":
            base, head = verify_packet(arguments.packet)
            print(f"Verified full offline bundle: base {base}, head {head}")
        elif arguments.command == "comment":
            result = add_comment(
                arguments.packet, arguments.identifier, arguments.commit,
                arguments.path, arguments.side, arguments.line, arguments.body,
            )
            print(f"Recorded {result.identifier} at {result.anchor.path}:{result.anchor.line}")
        elif arguments.command == "migrate-comments":
            comments = migrate_comments(arguments.packet)
            print(f"Comments version {COMMENT_VERSION}: {len(comments)} comments")
        else:
            if arguments.command == "edit-comment":
                result = update_comment(arguments.packet, arguments.identifier, body=arguments.body)
            else:
                result = update_comment(
                    arguments.packet, arguments.identifier,
                    resolution="resolved" if arguments.command == "resolve-comment" else "open",
                )
            print(f"Updated {result.identifier}: {result.resolution}")
        return 0
    except (SkeinError, OSError) as exc:
        parser.exit(2, f"skein: {exc}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
