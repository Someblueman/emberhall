#!/usr/bin/env python3
"""Offline, read-only backup inventory, integrity checking and recovery planning.

Python 3.10+, POSIX. No packages, network, or house runtime required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from typing import Any, TextIO


class InventoryError(ValueError):
    """The source or manifest cannot be inventoried safely."""


def _path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise InventoryError("file path must be a nonempty string")
    if (any(part in ("", ".", "..") for part in value.split("/"))
            or "\\" in value or ":" in value
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise InventoryError(f"unsafe or nonportable file path: {value!r}")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise InventoryError("file path is not valid UTF-8") from exc
    return value


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _directory(path: Path) -> int:
    """Open every directory component without following symlinks."""
    if os.name != "posix" or not hasattr(os, "O_NOFOLLOW"):
        raise InventoryError("safe descriptor-based scanning requires POSIX")
    if ".." in path.parts:
        raise InventoryError("directory paths must not contain '..' components")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    absolute = Path(os.path.abspath(path))
    descriptor = os.open(absolute.anchor, flags)
    try:
        for part in absolute.parts[1:]:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _walk(descriptor: int, prefix: str, entries: list[dict[str, Any]]) -> None:
    before = os.fstat(descriptor)
    for name in sorted(os.listdir(descriptor)):
        relative = _path(prefix + name)
        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=descriptor)
            try:
                if _identity(os.fstat(child)) != _identity(info):
                    raise InventoryError(f"directory changed during scan: {relative}")
                _walk(child, relative + "/", entries)
            finally:
                os.close(child)
        elif stat.S_ISREG(info.st_mode):
            # O_NONBLOCK prevents a raced replacement FIFO from hanging the scan.
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                            dir_fd=descriptor)
            try:
                if _identity(os.fstat(child)) != _identity(info):
                    raise InventoryError(f"file changed during scan: {relative}")
                digest = hashlib.sha256()
                while chunk := os.read(child, 1024 * 1024):
                    digest.update(chunk)
                if _identity(os.fstat(child)) != _identity(info):
                    raise InventoryError(f"file changed during scan: {relative}")
                entries.append({"path": relative, "size": info.st_size,
                                "sha256": digest.hexdigest()})
            finally:
                os.close(child)
        else:
            raise InventoryError(f"symlink or special file is forbidden: {relative}")
    if _identity(os.fstat(descriptor)) != _identity(before):
        raise InventoryError(f"directory changed during scan: {prefix or '.'}")


def inventory(root: Path) -> dict[str, Any]:
    descriptor = _directory(root)
    entries: list[dict[str, Any]] = []
    try:
        _walk(descriptor, "", entries)
    finally:
        os.close(descriptor)
    entries.sort(key=lambda entry: entry["path"])
    return {"format": "blackout-kit", "version": 1, "files": entries}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_manifest(path: Path) -> dict[str, Any]:
    parent = _directory(path.parent)
    try:
        info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise InventoryError("manifest must be a regular file, not a symlink or special file")
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=parent)
        with os.fdopen(descriptor, encoding="utf-8") as stream:
            if _identity(os.fstat(stream.fileno())) != _identity(info):
                raise InventoryError("manifest changed before it could be read")
            manifest = json.load(stream, object_pairs_hook=_unique_object)
            if _identity(os.fstat(stream.fileno())) != _identity(info):
                raise InventoryError("manifest changed while reading")
    finally:
        os.close(parent)
    if (not isinstance(manifest, dict)
            or set(manifest) != {"format", "version", "files"}
            or manifest["format"] != "blackout-kit"
            or type(manifest["version"]) is not int or manifest["version"] != 1
            or not isinstance(manifest["files"], list)):
        raise InventoryError("unsupported or malformed manifest header")
    paths: set[str] = set()
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise InventoryError("malformed file entry")
        relative = _path(entry["path"])
        if relative in paths:
            raise InventoryError(f"duplicate file path: {relative}")
        paths.add(relative)
        if type(entry["size"]) is not int or entry["size"] < 0:
            raise InventoryError(f"invalid size: {relative}")
        if (not isinstance(entry["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None):
            raise InventoryError(f"invalid SHA-256: {relative}")
    for relative in paths:
        parts = relative.split("/")
        if any("/".join(parts[:index]) in paths for index in range(1, len(parts))):
            raise InventoryError(f"file is also used as a directory: {relative}")
    return manifest


def compare(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    old = {entry["path"]: entry for entry in expected["files"]}
    new = {entry["path"]: entry for entry in actual["files"]}
    missing = sorted(old.keys() - new.keys())
    extra = sorted(new.keys() - old.keys())
    changed = sorted(path for path in old.keys() & new.keys() if old[path] != new[path])
    return {"ok": not (missing or extra or changed), "missing": missing,
            "changed": changed, "extra": extra,
            "matched": len(old.keys() & new.keys()) - len(changed)}


def recovery_plan(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    """Build a read-only recovery plan from a trusted inventory and a surviving archive.

    The plan reuses :func:`compare` classifications and adds an explicit,
    deterministic suggestion for every missing or changed target. A candidate
    source is any surviving regular file whose size and SHA-256 are byte-identical
    to the expected entry for that target. Candidates include extra files (for
    example a renamed file) and matched files with identical bytes. The plan
    never chooses among multiple candidates: every case with more than one
    byte-identical source is marked ambiguous and the caller must choose.
    Nothing is copied, renamed, overwritten, or deleted.
    """
    diff = compare(expected, actual)
    expected_by_path = {entry["path"]: entry for entry in expected["files"]}
    by_bytes: dict[tuple[int, str], list[str]] = {}
    for entry in actual["files"]:
        by_bytes.setdefault((entry["size"], entry["sha256"]), []).append(entry["path"])
    missing_set = set(diff["missing"])
    restores: list[dict[str, Any]] = []
    for target in sorted(missing_set | set(diff["changed"])):
        expected_entry = expected_by_path[target]
        key = (expected_entry["size"], expected_entry["sha256"])
        candidates = sorted(path for path in by_bytes.get(key, []) if path != target)
        restores.append({
            "ambiguous": len(candidates) > 1,
            "candidates": candidates,
            "recoverable": bool(candidates),
            "status": "missing" if target in missing_set else "changed",
            "target": target,
        })
    restores.sort(key=lambda item: item["target"])
    return {
        **diff,
        "ambiguous": sorted(item["target"] for item in restores if item["ambiguous"]),
        "restores": restores,
        "unrecoverable": sorted(item["target"] for item in restores if not item["recoverable"]),
    }


def save_manifest(manifest: dict[str, Any], destination: Path, root: Path) -> None:
    destination = destination.absolute()
    if destination.resolve().is_relative_to(root.resolve()):
        raise InventoryError("store the manifest outside the inventoried directory")
    content = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False,
                                         dir=destination.parent, prefix=".blackout-") as stream:
            temporary = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        # A complete manifest appears at once; an existing destination is never replaced.
        os.link(temporary, destination)
        directory = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary is not None:
            os.unlink(temporary)


def _emit(value: dict[str, Any], stream: TextIO) -> bool:
    try:
        print(json.dumps(value, sort_keys=True), file=stream, flush=True)
    except OSError:
        # A shutdown reflush must not replace our handled failure with exit 120.
        sink = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(sink, stream.fileno())
        finally:
            os.close(sink)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "verify", "plan"):
        command = commands.add_parser(name)
        command.add_argument("root", type=Path)
        command.add_argument("manifest", type=Path)
    diff_command = commands.add_parser("diff")
    diff_command.add_argument("old_manifest", type=Path)
    diff_command.add_argument("new_manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            manifest = inventory(args.root)
            save_manifest(manifest, args.manifest, args.root)
            result = {"created": str(args.manifest), "files": len(manifest["files"])}
            return 0 if _emit(result, sys.stdout) else 2
        if args.command == "diff":
            expected = load_manifest(args.old_manifest)
            actual = load_manifest(args.new_manifest)
            result = compare(expected, actual)
        else:
            expected = load_manifest(args.manifest)
            actual = inventory(args.root)
            result = recovery_plan(expected, actual) if args.command == "plan" else compare(expected, actual)
        if not _emit(result, sys.stdout):
            return 2
        return 0 if result["ok"] else 1
    except KeyboardInterrupt:
        _emit({"error": "interrupted"}, sys.stderr)
        return 130
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        _emit({"error": str(exc)}, sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
