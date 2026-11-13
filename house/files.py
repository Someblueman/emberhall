"""Read bounded regular artifacts without following symlinks or blocking on FIFOs."""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
import stat


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
