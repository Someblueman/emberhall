"""Bind a new, separate cohort to a public declaration and an exact installation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

REGISTRATION = Path(__file__).with_name("next-cohort.json")
DECLARATION_ID = ("mailbox-754310c7a296492298e4fa92f441e286-"
                  "1c8637976100ce651732d3e1f3aa7d3c07cd7c3c1ec1add6edac05d41c344df7")
PREFIX = "house-cohort-registration-v1 "
PROJECT = "house-after-rooms-20261119"
# These determine ordinary family rotation, task eligibility, and protected turns.
POLICY_MODULES = ("home", "life", "staffing", "providers", "maintenance", "work_metrics",
                  "ballot_work", "course", "shelf", "project_work", "home_control", "checks")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load():
    value = json.loads(REGISTRATION.read_text())
    fields = {"schema", "name", "task", "registrar", "installation", "source_commit",
              "manifest_sha256", "policy_files"}
    if (not isinstance(value, dict) or set(value) != fields
            or type(value["schema"]) is not int or value["schema"] != 1):
        raise ValueError("invalid cohort registration schema")
    if (type(value["installation"]) is not int or value["installation"] < 1
            or any(not isinstance(value[k], str) or not value[k]
                   for k in ("name", "task", "registrar", "source_commit", "manifest_sha256"))
            or not re.fullmatch(r"[0-9a-f]{40}", value["source_commit"])
            or not re.fullmatch(r"[0-9a-f]{64}", value["manifest_sha256"])):
        raise ValueError("invalid cohort registration identity")
    files = value["policy_files"]
    if (not isinstance(files, dict)
            or set(files) != {f"house/{name}.py" for name in POLICY_MODULES}
            or any(not isinstance(h, str) or not re.fullmatch(r"[0-9a-f]{64}", h)
                   for h in files.values())):
        raise ValueError("registration must pin every policy module")
    return value


def installation(events):
    """Return the pinned installation with its later public enrollment boundary."""
    registration = load()
    anchor = registration["installation"]
    if events[0]["sequence"] > anchor:
        raise ValueError(f"include registered installation {anchor} and consecutive pages after it")
    if events[-1]["sequence"] < anchor:
        return None
    start = events[anchor - events[0]["sequence"]]
    data = start["data"]
    manifest = data.get("protected_files")
    if (start["op"] not in {"owner-migrate", "renovation-install"}
            or (start["op"] == "renovation-install" and start["actor"] != "watch-keeper")
            or data.get("source_head") != registration["source_commit"]
            or not isinstance(manifest, dict)
            or hashlib.sha256(canonical(manifest).encode()).hexdigest() != registration["manifest_sha256"]
            or any(manifest.get(path) != digest for path, digest in registration["policy_files"].items())):
        raise ValueError(f"registered installation {anchor} differs from its pinned source")
    task_seen = False
    for event in events:
        if event["sequence"] <= anchor:
            continue
        if (event["op"] == "task" and event["actor"] == registration["registrar"]
                and event["data"].get("task") == registration["task"]
                and event["data"].get("project") == PROJECT):
            task_seen = True
        if event["id"] == DECLARATION_ID:
            if (event["op"] != "learn" or event["actor"] != registration["registrar"]
                    or not event["data"].get("evidence", "").startswith(PREFIX)):
                raise ValueError("registered declaration has the wrong author or operation")
            announced = json.loads(event["data"]["evidence"][len(PREFIX):])
            if not isinstance(announced, dict):
                raise ValueError("invalid public cohort declaration")
            if announced != registration or not task_seen:
                raise ValueError("public cohort declaration differs from its registration or task")
            return start | {"cohort_declared_at": event["sequence"]}
    return None
