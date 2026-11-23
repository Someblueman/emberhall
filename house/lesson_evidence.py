"""One named lesson, one verified file, and a client-local exclusive write."""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path

from .model import require, validate_artifacts


def read(state: dict, lesson: str, resident: str, name: str | None = None) -> dict:
    require(resident in state["residents"], "unknown resident")
    item = state["lessons"][lesson]
    result = {"lesson": lesson, **{key: item[key] for key in
              ("key", "claim", "evidence", "status", "reviews", "author")}}
    if "replaced_by" in item:
        result["replaced_by"] = item["replaced_by"]
    artifacts = item.get("artifacts", {})
    result["artifacts"] = {path: {"sha256": value["sha256"]}
                           for path, value in artifacts.items()}
    if name is not None:
        require(name in artifacts, "lesson has no evidence file with that name")
        result["artifact"] = {"name": name, **artifacts[name]}
    return result


def save(result: dict, root: Path, output: str) -> dict:
    """Called by the local client, never by coordinator dispatch.

    Parent directories must already exist. No symlink is followed, and an
    existing destination of any kind is never replaced.
    """
    parts = output.split("/")
    require(bool(output) and "\\" not in output and
            all(part not in ("", ".", "..") for part in parts),
            "output must be a relative file without dot components")
    require(isinstance(result, dict) and isinstance(result.get("artifact"), dict),
            "invalid evidence response")
    value = result["artifact"]
    require(set(value) == {"name", "sha256", "base64"} and isinstance(value["name"], str),
            "invalid evidence response")
    require(isinstance(value.get("base64"), str) and len(value["base64"]) <= 1333336,
            "evidence file exceeds 1 MB")
    validate_artifacts({value["name"]: {key: value[key] for key in ("sha256", "base64")}})
    content = base64.b64decode(value["base64"], validate=True)
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
        except BaseException:
            os.unlink(parts[-1], dir_fd=directory)
            raise
    finally:
        os.close(directory)
    return {key: val for key, val in result.items() if key != "artifact"} | {
        "saved": {"path": output, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}}
