"""Fixed resident source paths and bounded, no-symlink artifact reads."""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
import re
import stat


def workspace_location(record, run: str, state: dict | None = None) -> tuple[Path, tuple[str, ...]]:
    """Old clones stay put; only later runs use the ordinary ignored directory."""
    if not isinstance(run, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", run) is None:
        raise ValueError("invalid resident workspace run")
    state = record.read()[0] if state is None else state
    epoch = state.get("maintenance", {}).get("workspace_layout_sequence")
    item = state.get("life", {}).get("runs", {}).get(run, {})
    if epoch is not None:
        if (type(epoch) is not int or epoch <= 0 or
                item.get("workspace") != "residents/" + run or
                type(item.get("started_sequence")) is not int):
            raise ValueError("workspace needs its recorded run and migration")
        if item["started_sequence"] > epoch:
            if any(part in {".git", ".muse", ".agents", ".husky"} for part in record.root.parts):
                raise ValueError("resident source root is inside protected metadata")
            return record.root, (".house-residents", run)
    return record.common / "house-home", ("residents", run)


def workspace_path(record, run: str, state: dict | None = None) -> Path:
    root, parts = workspace_location(record, run, state)
    # Validate every existing component, including the parent of the source room.
    # Missing rooms are legitimate before creation or after an interrupted start.
    # Same-user replacement after this check is not hostile-process isolation.
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=descriptor)
            except FileNotFoundError:
                break
            os.close(descriptor)
            descriptor = child
    finally:
        os.close(descriptor)
    return root.joinpath(*parts)


def artifact(root: Path, name: str) -> dict:
    parts = name.split("/")
    if not name or any(part in ("", ".", "..") for part in parts) or "\\" in name:
        raise ValueError("artifact must be a repo-relative file without dot components")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(root, directory_flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > 1000000:
                raise ValueError("artifact must be a regular file <= 1 MB")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                content = stream.read(1000001)
            after = os.fstat(fd)
            identity = lambda info: (info.st_dev, info.st_ino, info.st_size,
                                     info.st_mtime_ns, info.st_ctime_ns)
            if identity(before) != identity(after) or len(content) > 1000000:
                raise ValueError("artifact changed while being read")
        finally:
            os.close(fd)
    finally:
        os.close(directory)
    return {"sha256": hashlib.sha256(content).hexdigest(),
            "base64": base64.b64encode(content).decode()}
