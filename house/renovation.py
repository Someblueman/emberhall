"""Council renovation: residents install changes to the house's own code.

The Steward's course correction of 15 November 2026 hands ordinary changes to
the house's code and runtime to residents and the council. A renovation is a
council proposal (mode ``renovation``) whose text is a JSON descriptor binding
exact file hashes. It follows the normal ratification process: a trial, two
independent endorsements by residents other than its author, and the full
24-hour notice on the Steward's bell. Once enacted, the coordinator stops
admitting new residents, waits for the house to drain, runs the full test
suite in the restrictive sandbox, records the installation and restarts itself
on the new runtime. Failures are recorded and nothing is installed.

Steward-only files can never be renovated: money, credentials, irreversible
actions, sandbox and web safeguards, ratification and this route stay with the
Steward. See docs/RENOVATION.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

from .model import require

STEWARD_ONLY = frozenset({
    "house/maintenance.py", "house/owner_upgrade.py", "house/renovation.py",
    "house/council.py", "house/governance.py", "house/steward.py", "house/wake_policy.py",
    "house/windows.py", "house/providers.py", "house/opencode_tool.py",
    "house/opencode_auth.py", "house/test_sandbox.py", "house/runtime.py", "house/testrun.py",
    # The page viewer is a sandbox boundary: only the Steward widens what a resident's page may reach.
    "house/view.py",
    # Reading the house's public site is a web safeguard loosened by the Steward alone, to exactly one origin.
    "house/site_read.py",
    # The door to the daughter house: the Steward alone decides how many wakes there are and what they may do.
    "house/daughter.py",
})
PATH = re.compile(r"house/[a-z_][a-z0-9_]*\.py")
MAX_FILES = 40
LAUNCHER = "launcher.py"


def enabled(state: dict) -> bool:
    from . import course
    return course.enabled(state)


def descriptor(value: str) -> dict:
    """Parse and validate a renovation descriptor without trusting its author."""
    def unique(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, "duplicate renovation JSON field")
            result[key] = item
        return result
    try:
        data = json.loads(value, object_pairs_hook=unique)
    except json.JSONDecodeError as error:
        raise ValueError("renovation text must be a JSON descriptor") from error
    require(isinstance(data, dict) and set(data) == {"source_commit", "files", "summary"},
            "renovation descriptor needs source_commit, files and summary")
    require(isinstance(data["source_commit"], str) and
            re.fullmatch(r"[0-9a-f]{40}", data["source_commit"]) is not None, "invalid renovation commit")
    require(isinstance(data["summary"], str) and 0 < len(data["summary"].strip()) <= 4000,
            "invalid renovation summary")
    files = data["files"]
    require(isinstance(files, dict) and 1 <= len(files) <= MAX_FILES, "renovate 1 to 40 house files")
    for name, value in files.items():
        require(isinstance(name, str) and PATH.fullmatch(name) is not None, f"not a house module: {name}")
        require(name not in STEWARD_ONLY, f"{name} is Steward-only and cannot be renovated")
        require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
                f"invalid hash for {name}")
    return {"source_commit": data["source_commit"], "files": dict(sorted(files.items())),
            "summary": data["summary"]}


def pending(state: dict) -> list[str]:
    """Enacted renovations not yet installed or failed, oldest first."""
    rules = state.get("council", {}).get("rules", {})
    return sorted((name for name, rule in rules.items()
                   if rule.get("mode") == "renovation" and rule["status"] == "approved"),
                  key=lambda name: rules[name]["enacted_sequence"])


def target_manifest(state: dict, proposal: str) -> dict:
    from .maintenance import protected_manifest
    manifest = dict(protected_manifest(state))
    manifest.update(state["council"]["rules"][proposal]["renovation"]["files"])
    return manifest


def apply(state: dict, event: dict) -> None:
    """Journal reducer for renovation-install and renovation-failed."""
    from .council import fields
    from .life import CONTROLLER
    from .maintenance import fingerprint, protected_manifest
    require(enabled(state), "council renovation is not enabled")
    require(event["actor"] == CONTROLLER, "only the coordinator installs renovations")
    data = event["data"]
    proposal = data.get("proposal")
    require(proposal in pending(state), "renovation is not awaiting installation")
    rule = state["council"]["rules"][proposal]
    seq = state["sequence"] + 1
    if event["op"] == "renovation-failed":
        fields(data, {"proposal", "reason"})
        require(isinstance(data["reason"], str) and 0 < len(data["reason"]) <= 2000, "invalid failure reason")
        rule.update(status="failed", failed_at=event["at"], failed_sequence=seq, reason=data["reason"])
        state["proposals"][proposal].update(installation="failed")
        return
    fields(data, {"proposal", "source_head", "protected_files", "previous_manifest_sha256",
                  "previous_runtime_sha256", "runtime_sha256", "test_output_sha256", "test_count"})
    old = protected_manifest(state)
    require(data["previous_manifest_sha256"] == fingerprint(old), "stale protected manifest")
    require(data["protected_files"] == target_manifest(state, proposal),
            "installed files differ from the enacted renovation")
    require(isinstance(data["source_head"], str) and re.fullmatch(r"[0-9a-f]{40}", data["source_head"]),
            "invalid source commit")
    require(all(isinstance(data[key], str) and re.fullmatch(r"[0-9a-f]{64}", data[key]) for key in
                ("previous_runtime_sha256", "runtime_sha256", "test_output_sha256")), "invalid digest")
    require(type(data["test_count"]) is int and data["test_count"] > 0,
            "renovation requires executed passing tests")
    require(not any(run["status"] == "active" for run in state.get("life", {}).get("runs", {}).values()),
            "drain native residents before renovation")
    maintenance = state.setdefault("maintenance", {})
    maintenance["protected_files"] = dict(data["protected_files"])
    maintenance.setdefault("renovations", {})[proposal] = {
        "source_head": data["source_head"], "runtime_sha256": data["runtime_sha256"],
        "test_count": data["test_count"], "at": event["at"], "sequence": seq}
    rule.update(status="installed", installed_at=event["at"], installed_sequence=seq,
                runtime_sha256=data["runtime_sha256"], source_head=data["source_head"])
    state["proposals"][proposal].update(installation="installed")


def _sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def drained(record, private: Path) -> bool:
    state = record.read()[0]
    if any(run["status"] == "active" for run in state.get("life", {}).get("runs", {}).values()):
        return False
    for job in (private / "jobs").glob("*/job.json"):
        if json.loads(job.read_text()).get("status") != "done":
            return False
    from .publication_worker import drained as published
    return published(record)


def outdated(record, state: dict) -> str | None:
    """Why the oldest enacted renovation cannot be installed from main as it stands.

    Checked before the house is held, so a renovation that main has already
    moved past (for example one an owner upgrade delivered) costs no drain.
    """
    from .wake_policy import source_snapshot
    proposal = pending(state)[0]
    files = source_snapshot(record.root)["files"]
    mismatched = sorted(name for name, value in target_manifest(state, proposal).items() if files.get(name) != value)
    if not mismatched:
        return None
    return ("main does not contain exactly the enacted files (integrate the renovation's source "
            "first, and renovate other changed house files separately): " + ", ".join(mismatched[:12]))


def record_failure(record, proposal: str, reason: str) -> None:
    from .life import CONTROLLER
    record.append("renovation-failed", CONTROLLER, {"proposal": proposal, "reason": reason[:2000]},
                  "renovation-" + proposal + "-failed")


def install(record, private: Path) -> dict:
    """Install the oldest enacted renovation. Call only from the drained coordinator."""
    from .life import CONTROLLER
    from .maintenance import fingerprint, protected_manifest
    from .owner_upgrade import passed_count
    from .runtime import selected
    from .testrun import SUITE_ARGS
    from .wake_policy import active_policy, source_snapshot
    from .watch_recovery import prepare_runtime
    from . import test_sandbox
    state = record.read()[0]
    proposal = pending(state)[0]
    request = "renovation-" + proposal

    def fail(reason: str) -> dict:
        record_failure(record, proposal, reason)
        return {"installed": False, "proposal": proposal, "reason": reason}

    snapshot = source_snapshot(record.root)
    manifest = target_manifest(state, proposal)
    reason = outdated(record, state)
    if reason:
        return fail(reason)
    with tempfile.TemporaryDirectory(prefix="emberhall-renovation-") as temporary, \
            tempfile.TemporaryFile() as output:
        candidate = Path(temporary) / "source"
        subprocess.run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--no-tags",
                        str(record.root), str(candidate)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(candidate), "checkout", "--quiet", "--detach",
                        snapshot["source_head"]], check=True, capture_output=True)
        tested = test_sandbox.run([str(Path(sys.executable).resolve()), *SUITE_ARGS],
                                  cwd=candidate, stdout=output, timeout=1800)
        output.seek(0)
        raw = output.read(800001)
    report = private / f"renovation-{proposal}-tests.txt"
    report.write_bytes(raw[:800000])
    report.chmod(0o600)
    try:
        count = passed_count(raw, tested.returncode)
    except ValueError:
        return fail(f"tests did not pass (exit {tested.returncode}); private output {report.name}")
    if source_snapshot(record.root) != snapshot:
        return fail("main changed while the renovation was being tested; it will need re-enacting")
    previous = selected(record)
    target = prepare_runtime(record, private)
    data = {"proposal": proposal, "source_head": snapshot["source_head"], "protected_files": manifest,
            "previous_manifest_sha256": fingerprint(protected_manifest(state)),
            "previous_runtime_sha256": previous["runtime_sha256"], "runtime_sha256": target["runtime_sha256"],
            "test_output_sha256": _sha(raw), "test_count": count}
    receipt = record.append("renovation-install", CONTROLLER, data, request)
    target = target | {"attestation": {"renovation": proposal, "source_head": snapshot["source_head"],
                                       "policy_revision": active_policy(record.read()[0])["revision"]}}
    from .owner_upgrade import atomic_json
    atomic_json(private / "active-runtime.json", target)
    return {"installed": True, "proposal": proposal, "receipt": receipt, "runtime": target["entry"]}


LAUNCHER_SOURCE = '''"""Start the Emberhall coordinator on the currently selected, verified runtime."""
import hashlib, json, os, sys
from pathlib import Path
private = Path(__file__).resolve().parent
repo = private.parent.parent
receipt = json.loads((private / "active-runtime.json").read_text())
entry = Path(receipt["entry"])
if entry.parent != private or entry.is_symlink() or not entry.name.startswith("runtime-"):
    raise SystemExit("runtime outside private immutable store")
if hashlib.sha256(entry.read_bytes()).hexdigest() != receipt["runtime_sha256"]:
    raise SystemExit("pinned runtime bytes changed")
python = sys.executable
os.execv(python, [python, "-I", str(entry), "home", "--repo", str(repo), "--runtime", str(entry),
                  "--publish", "serve"])
'''


def write_launcher(private: Path) -> Path:
    """The LaunchAgent runs this so a restarted coordinator loads the selected runtime."""
    path = private / LAUNCHER
    temporary = private / (LAUNCHER + ".tmp")
    temporary.write_text(LAUNCHER_SOURCE)
    temporary.chmod(0o600)
    os.replace(temporary, path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Describe a renovation for a council proposal.")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--commit", required=True, help="committed source containing the new house files")
    parser.add_argument("--summary", required=True)
    parser.add_argument("files", nargs="+", help="house/*.py files the renovation changes or adds")
    args = parser.parse_args()
    try:
        files = {}
        for name in args.files:
            body = subprocess.run(["git", "-C", str(args.repo), "show", f"{args.commit}:{name}"],
                                  check=True, capture_output=True).stdout
            files[name] = _sha(body)
        commit = subprocess.run(["git", "-C", str(args.repo), "rev-parse", args.commit + "^{commit}"],
                                check=True, capture_output=True, text=True).stdout.strip()
        text = json.dumps({"source_commit": commit, "files": files, "summary": args.summary},
                          indent=2, sort_keys=True)
        descriptor(text)
        print(text)
        return 0
    except (ValueError, subprocess.SubprocessError) as error:
        print(f"renovation: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
