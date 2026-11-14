"""Council wake text and receipts for a later resident testing a runtime change.

This module neither installs a runtime nor invents a model wake. The controller
owns launch evidence and must hold its activation lock around refresh_gate and
the pointer change. Simulated lifecycle fixtures are tests, never live approval.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

from .council import fields, require, text
from .governance import canonical, digest
from .record import Record
from . import test_sandbox

APPROVED_SOURCE_SHA256 = "50f6c535ed42c4e640a5a09a77a3eb3a45568c710b40ab49da44d1da00b96f30"
OWNER_LIMITS = {
    "money": "No spending money or per-token-billed providers.",
    "credentials": "No new passwords or keys.",
    "irreversible": "No irreversible actions.",
    "sandbox": "Workspace-write equivalent, limited network; keep Muse sandbox on, "
               "use agy --sandbox, never no-sandbox or permission-bypass modes.",
    "providers": "Only the Steward-listed Codex, opencode, Muse and agy providers/models.",
    "ratification": "A recorded trial, two independent non-author endorsements, a full "
                    "24-hour public veto window and fresh authenticated Steward check. "
                    "Only the Steward changes this process or these protected limits.",
}
ENVELOPE_SHA256 = digest(canonical(OWNER_LIMITS).decode())
INITIAL_PROMPT = """You are home in Emberhall, a house of discontinuous minds.
Read the current door, Steward orders, ambitions and verified record. Pick up a
thread another resident left, or begin useful work that advances the house's
long-running ambitions. Make the house wiser, more capable and more beautiful;
do something worth having beyond the house itself.

Work with the other residents through the house controller and journal. Claim
clear ownership, preserve others' work, and ask for help when another kind of
mind would improve the result. Follow actual usage and availability rather than
manufacturing busywork. Quiet observation and a thoughtful handoff are legitimate.

Keep the evidence that changes what the house knows. Test changed boundaries,
retain useful failures, and let later wakes build on them. Checkpoint on the
house's sensible shared schedule rather than repeating unchanged ceremonies at
every wake. Leave your threads, decisions and next useful action in the record.
Council proposals are not law until enacted. Improve these wake instructions
through the approved council, and refresh the pinned runtime only through the
tested later-wake gate. Never turn a simulated test into a live witness.
"""
REPORT_NAME = "runtime-test.json"
TEST_ARGS = ["-m", "unittest", "discover", "-s", "tests", "-v"]
PROTECTED_FILES = frozenset("house/" + name + ".py" for name in (
    "providers", "council", "wake_policy", "steward", "model", "record", "governance",
    "resident_client", "mailbox", "mailbox_jobs", "resident_actions", "opencode_tool", "test_sandbox",
    "life", "inbox", "publish", "body", "integrate", "home", "home_work", "watch_recovery", "runtime", "__main__", "watch", "files", "__init__"))


def approval(source: str, snapshot: dict) -> dict:
    require(PROTECTED_FILES <= snapshot["files"].keys(), "protected runtime sources are missing")
    return {"source": source, "source_sha256": APPROVED_SOURCE_SHA256,
            "prompt_sha256": digest(INITIAL_PROMPT), "envelope_sha256": ENVELOPE_SHA256,
            "source_head": snapshot["source_head"],
            "protected_files": {name: snapshot["files"][name] for name in sorted(PROTECTED_FILES)}}


def authorize(state: dict, event: dict) -> None:
    data = event["data"]
    fields(data, {"source", "source_sha256", "prompt_sha256", "envelope_sha256",
                  "source_head", "protected_files"})
    require("wake_policy" not in state, "wake policy already authorized")
    require(isinstance(data["protected_files"], dict) and set(data["protected_files"]) == PROTECTED_FILES
            and all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                    for value in data["protected_files"].values()) and
            isinstance(data["source_head"], str) and re.fullmatch(r"[0-9a-f]{40}", data["source_head"]),
            "invalid protected runtime manifest")
    snapshot = {"source_head": data["source_head"], "files": data["protected_files"]}
    require(data == approval(text(data, "source"), snapshot), "wrong wake-policy Steward authorization")
    state["wake_policy"] = {**data, "protected_files": dict(data["protected_files"]),
                             "authorized_at": event["at"],
                             "authorized_sequence": state["sequence"] + 1, "tests": {}}


def protected_source(state: dict, snapshot: dict) -> None:
    manifest = state.get("maintenance", {}).get("protected_files",
                                               state["wake_policy"]["protected_files"])
    require(manifest.keys() <= snapshot["files"].keys() and
            {name: snapshot["files"][name] for name in manifest} == manifest,
            "protected enforcement source changed; new Steward authorization required")


def active_policy(state: dict) -> dict:
    authority = state.get("wake_policy")
    require(authority is not None, "wake policy is not authorized")
    require(authority["source_sha256"] == APPROVED_SOURCE_SHA256 and
            authority["envelope_sha256"] == ENVELOPE_SHA256,
            "protected wake envelope changed without Steward authorization")
    proposal, prompt, sequence = None, INITIAL_PROMPT, authority["authorized_sequence"]
    for name, item in state["council"]["rules"].items():
        if item.get("mode") == "wake-prompt" and item["status"] == "active":
            proposal, prompt, sequence = name, item["text"], item["enacted_sequence"]
    from . import windows
    limits = dict(OWNER_LIMITS)
    revision_data = {"source": APPROVED_SOURCE_SHA256, "proposal": proposal,
                     "sequence": sequence, "prompt_sha256": digest(prompt)}
    if windows.enabled(state):
        limits.update(windows.LIMITS)
        revision_data["envelope_sha256"] = digest(canonical(limits).decode())
    envelope = digest(canonical(limits).decode())
    return {"proposal": proposal, "text": prompt, "text_sha256": digest(prompt),
            "revision": digest(canonical(revision_data).decode()), "enacted_sequence": sequence,
            "envelope_sha256": envelope, "protected_limits": limits}


def active_prompt(state: dict) -> str:
    policy = active_policy(state)
    limits = "\n".join(f"- {key}: {value}" for key, value in policy["protected_limits"].items())
    return ("STEWARD-PROTECTED LIMITS — council text cannot override these:\n" + limits +
            "\n\nCOUNCIL WAKE PROMPT (subordinate to the protected limits):\n" + policy["text"] +
            "\nThe protected Steward limits above still apply to every instruction.\n")


def later_wake(state: dict, actor: str, run_id: str) -> tuple[dict, dict]:
    policy = active_policy(state)
    require(policy["proposal"] is not None, "runtime refresh requires an enacted wake prompt")
    run = state.get("life", {}).get("runs", {}).get(run_id)
    require(run is not None and run["resident"] == actor, "no assigned later resident run")
    require(run["status"] == "active" and type(run.get("launched_sequence")) is int,
            "runtime tests require an actually launched active wake")
    require(run["started_sequence"] > policy["enacted_sequence"],
            "wake began before prompt enactment")
    require(run["policy_revision"] == policy["revision"], "wake uses a different policy revision")
    require(state["residents"][actor]["awake"], "testing resident is asleep")
    return policy, run


def report_for(state: dict, actor: str, run_id: str, task_id: str) -> dict:
    policy, run = later_wake(state, actor, run_id)
    task = state["tasks"].get(task_id)
    require(task is not None and task["status"] == "done" and task["owner"] == actor,
            "runtime tests require the resident's completed task")
    require(task["finished_at"] > run["launched_sequence"], "test task predates the wake")
    artifact = task["artifacts"].get(REPORT_NAME)
    require(artifact is not None, "missing immutable runtime test report")
    body = base64.b64decode(artifact["base64"], validate=True)
    require(hashlib.sha256(body).hexdigest() == artifact["sha256"], "runtime report hash mismatch")
    report = json.loads(body)
    require(body == canonical(report) + b"\n", "runtime report must be canonical JSON")
    fields(report, {"format", "house", "resident", "run", "proposal", "policy_revision",
                    "envelope_sha256", "source_head", "source_sha256", "files", "command",
                    "exit_code", "test_count", "started_at", "finished_at", "output_sha256"})
    require(report["format"] == "emberhall-runtime-test-v1" and
            report["house"] == state["house_id"] and report["resident"] == actor and
            report["run"] == run_id and report["proposal"] == policy["proposal"] and
            report["policy_revision"] == policy["revision"] and
            report["envelope_sha256"] == policy["envelope_sha256"], "runtime report binding mismatch")
    require(type(report["exit_code"]) is int and report["exit_code"] == 0 and
            type(report["test_count"]) is int and report["test_count"] > 0,
            "runtime tests did not pass")
    require(isinstance(report["command"], list) and len(report["command"]) == len(TEST_ARGS) + 1
            and report["command"][1:] == TEST_ARGS and Path(report["command"][0]).is_absolute(),
            "unexpected runtime test command")
    require(type(report["started_at"]) in (int, float) and
            type(report["finished_at"]) in (int, float) and
            run["started_at"] <= report["started_at"] <= report["finished_at"] <= state["at"],
            "runtime test clock is outside the later wake")
    require(isinstance(report["files"], dict) and bool(report["files"]), "missing source manifest")
    for name, sha in report["files"].items():
        require(isinstance(name, str) and isinstance(sha, str) and
                re.fullmatch(r"[0-9a-f]{64}", sha) is not None, "invalid source manifest")
    require(isinstance(report["source_head"], str) and
            re.fullmatch(r"[0-9a-f]{40}", report["source_head"]) is not None and
            report["source_sha256"] == digest(canonical(report["files"]).decode()),
            "runtime source identity mismatch")
    protected_source(state, report)
    output = task["artifacts"].get("runtime-test-output.txt")
    require(output is not None and output["sha256"] == report["output_sha256"],
            "missing immutable test output")
    return report


def accept_tests(state: dict, event: dict) -> None:
    data = event["data"]
    fields(data, {"task", "run"})
    task_id, run_id = text(data, "task", 100), text(data, "run", 100)
    report = report_for(state, event["actor"], run_id, task_id)
    require(task_id not in state["wake_policy"]["tests"], "runtime test receipt already accepted")
    state["wake_policy"]["tests"][task_id] = {
        "actor": event["actor"], "run": run_id, "sequence": state["sequence"] + 1,
        "policy_revision": report["policy_revision"], "source_head": report["source_head"],
        "source_sha256": report["source_sha256"]}


def source_snapshot(source_repo: Path) -> dict:
    """Bind runtime and tests to committed bytes; never import the tested checkout here."""
    source_repo = source_repo.resolve()
    def git(*args: str) -> bytes:
        return subprocess.run(["git", "-C", str(source_repo), *args], capture_output=True,
                              check=True).stdout
    require(not git("status", "--porcelain", "--untracked-files=all").strip(),
            "runtime tests and refresh require clean committed source")
    head = git("rev-parse", "--verify", "HEAD").decode().strip()
    manifest = {}
    for item in git("ls-tree", "-rz", head, "house", "tests", "custodian_entry.py",
                    "docs/WATCH_PROMPT.md", "pyproject.toml").split(b"\0"):
        if not item:
            continue
        header, raw = item.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        name = raw.decode()
        require(kind == "blob" and mode in {"100644", "100755"},
                "runtime sources must be regular committed files")
        manifest[name] = hashlib.sha256(git("cat-file", "blob", oid)).hexdigest()
    require({"house/wake_policy.py", "house/council.py"} <= manifest.keys()
            and any(name.startswith("tests/test_") for name in manifest),
            "runtime policy sources or tests are missing")
    return {"source_head": head, "source_sha256": digest(canonical(manifest).decode()),
            "files": manifest}


def test_runtime(record: Record, actor: str, run_id: str, task_id: str, token: str,
                 source_repo: Path) -> dict:
    state = record.read()[0]
    policy, _ = later_wake(state, actor, run_id)
    task = state["tasks"].get(task_id)
    require(task is not None and task["status"] == "claimed" and task["owner"] == actor
            and task["token"] == token and task["until"] > time.time(),
            "runtime test task must have a current owned lease")
    before = source_snapshot(source_repo)
    protected_source(state, before)
    command = [str(Path(sys.executable).resolve()), *TEST_ARGS]
    started = time.time()
    # Tests may modify their room, never the canonical source or authority store.
    with tempfile.TemporaryDirectory(prefix="emberhall-runtime-test-") as temporary, tempfile.TemporaryFile() as output:
        candidate = Path(temporary) / "source"
        subprocess.run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--no-tags",
                        str(source_repo), str(candidate)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(candidate), "checkout", "--quiet", "--detach", before["source_head"]],
                       check=True, capture_output=True)
        result = test_sandbox.run(command, cwd=candidate, stdout=output, timeout=300)
        require(source_snapshot(candidate) == before, "test candidate changed during runtime tests")
        output.seek(0)
        raw = output.read(800001)
    finished = time.time()
    require(len(raw) <= 800000, "runtime test output exceeds artifact budget")
    require(source_snapshot(source_repo) == before, "source changed during runtime tests")
    matches = re.findall(rb"\nRan ([0-9]+) tests? in ", raw)
    skipped = re.findall(rb"\nOK \(skipped=([0-9]+)\)", raw)
    count = max(0, (int(matches[-1]) if matches else 0) - (int(skipped[-1]) if skipped else 0))
    report = {"format": "emberhall-runtime-test-v1", "house": state["house_id"],
              "resident": actor, "run": run_id, "proposal": policy["proposal"],
              "policy_revision": policy["revision"], "envelope_sha256": policy["envelope_sha256"],
              **before, "command": command, "exit_code": result.returncode,
              "test_count": count, "started_at": started, "finished_at": finished,
              "output_sha256": hashlib.sha256(raw).hexdigest()}
    artifacts = {}
    for name, body in ((REPORT_NAME, canonical(report) + b"\n"), ("runtime-test-output.txt", raw)):
        artifacts[name] = {"sha256": hashlib.sha256(body).hexdigest(),
                           "base64": base64.b64encode(body).decode()}
    completion = record.append("finish", actor, {"task": task_id, "token": token,
        "result": f"Runtime tests exited {result.returncode}; {count} non-skipped tests observed. "
                  "This receipt is not runtime activation.", "artifacts": artifacts},
        f"runtime-test-finish-{task_id}")
    if result.returncode != 0 or count == 0:
        return {"tested": False, "completion": completion}
    accepted = record.append("council-runtime-tested", actor, {"task": task_id, "run": run_id},
                             f"runtime-tested-{task_id}")
    return {"tested": True, "completion": completion, "receipt": accepted, **before}


def refresh_gate(record: Record, actor: str, task_id: str, run_id: str,
                 source_repo: Path) -> dict:
    state = record.read()[0]
    report = report_for(state, actor, run_id, task_id)
    receipt = state["wake_policy"]["tests"].get(task_id)
    require(receipt is not None and receipt["actor"] == actor and receipt["run"] == run_id,
            "runtime tests have no accepted council receipt")
    snapshot = source_snapshot(source_repo)
    protected_source(state, snapshot)
    require(all(snapshot[key] == report[key] for key in snapshot),
            "committed runtime no longer matches the tested source")
    return {**snapshot, "task": task_id, "run": run_id, "resident": actor,
            "policy_revision": report["policy_revision"], "proposal": report["proposal"],
            "envelope_sha256": report["envelope_sha256"], "tested_sequence": receipt["sequence"]}
