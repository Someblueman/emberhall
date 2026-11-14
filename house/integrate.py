"""Review private source contributions before a serialized fast-forward publication.

Candidates and failures remain in private Git clones. No reset, stash, forced
update or patch overwrite is used on the shared source checkout.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

from .home_work import git
from .record import Record
from . import test_sandbox
from .files import workspace_path


def integrate(record: Record, run: str, actor: str, *, publish: bool = False) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run):
        raise ValueError("invalid run ID")
    private = record.common / "house-home"
    private.mkdir(mode=0o700, exist_ok=True)
    with (private / "integration.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        state, _, _ = record.read()
        item = state.get("life", {}).get("runs", {}).get(run)
        if not item or item["status"] != "completed":
            raise ValueError("contribution requires a stopped resident")
        if actor not in state["residents"]:
            raise ValueError("integrator must be a resident")
        if actor == item["resident"] or not state["residents"][actor]["awake"]:
            raise ValueError("integration requires a different, awake resident")
        workspace = workspace_path(record, run, state)
        report = json.loads((private / run / "contribution.json").read_text())
        if report["base"] != item["source_head"] or report["commit"] != git(workspace, "rev-parse", "HEAD"):
            raise ValueError("contribution identity changed")
        head = git(record.root, "rev-parse", "HEAD")
        path = private / run / "integration.json"
        if path.exists():
            try:
                accepted = json.loads(path.read_text())
            except json.JSONDecodeError:
                # A stopped writer may have left an old non-atomic receipt.
                # Preserve its bytes; it cannot authorize acceptance. Re-review.
                path.replace(path.with_name("integration-incomplete-" + uuid.uuid4().hex + ".json"))
                accepted = {}
            if not isinstance(accepted, dict):
                raise ValueError("invalid integration receipt; preserve it")
            if accepted.get("status") == "integrated":
                # Both fields exist in durable receipts: normal merges record
                # candidate_head; operator-curated acceptance records canonical_commit.
                anchors = [accepted[key] for key in ("canonical_commit", "candidate_head") if key in accepted]
                if (accepted.get("run") != run or accepted.get("contribution") != report["commit"]
                        or not anchors or any(not isinstance(anchor, str)
                            or not re.fullmatch(r"[0-9a-f]{40}", anchor)
                            or anchor != anchors[0] for anchor in anchors)):
                    raise ValueError("accepted contribution receipt is inconsistent; preserve it")
                ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", anchors[0], head],
                                          cwd=record.root, capture_output=True)
                if ancestor.returncode != 0:
                    raise ValueError("accepted contribution is outside current source history; preserve it")
                if "candidate_head" in accepted:
                    contains = subprocess.run(["git", "merge-base", "--is-ancestor", report["commit"],
                                               accepted["candidate_head"]], cwd=record.root, capture_output=True)
                    if contains.returncode != 0:
                        raise ValueError("accepted contribution is absent from its merge commit; preserve it")
                return accepted
        if git(record.root, "status", "--porcelain", "--untracked-files=all"):
            raise ValueError("shared source has uncommitted work; preserve it")
        candidate = private / ("integration-" + uuid.uuid4().hex)
        subprocess.run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--no-tags",
                        str(record.root), str(candidate)], check=True, capture_output=True)
        git(candidate, "remote", "remove", "origin")
        git(candidate, "fetch", "--quiet", str(workspace), report["commit"])
        receipt = {"run": run, "actor": actor, "base": head, "contribution": report["commit"],
                   "candidate": candidate.name, "status": "conflict"}
        merged = subprocess.run(["git", "-C", str(candidate), "-c", "commit.gpgsign=false",
                                 "-c", "user.name=Emberhall integrator", "-c", "user.email=house@local",
                                 "merge", "--no-edit", report["commit"]], capture_output=True, text=True)
        (candidate.parent / (candidate.name + ".merge.log")).write_text(merged.stdout + merged.stderr)
        if merged.returncode == 0:
            receipt["candidate_head"] = git(candidate, "rev-parse", "HEAD")
            # A foundation change warrants the existing full acceptance suite.
            # Run only when accepting changed source, never as a wake ritual.
            with (candidate.parent / (candidate.name + ".tests.log")).open("w") as output:
                tested = test_sandbox.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
                                          cwd=candidate, stdout=output, timeout=900)
            unchanged = (git(candidate, "rev-parse", "HEAD") == receipt["candidate_head"] and
                         not git(candidate, "status", "--porcelain", "--untracked-files=all"))
            receipt.update(status="reviewed" if tested.returncode == 0 and unchanged else "tests-failed",
                           test_exit=tested.returncode)
        if publish and receipt["status"] == "reviewed":
            if head != git(record.root, "rev-parse", "HEAD") or git(record.root, "status", "--porcelain", "--untracked-files=all"):
                raise ValueError("shared source changed during review; candidate retained")
            # Git itself refuses overwrites if an interactive writer dirties a
            # touched path between the check and this fast-forward operation.
            git(record.root, "fetch", "--quiet", str(candidate), receipt["candidate_head"])
            git(record.root, "merge", "--ff-only", receipt["candidate_head"])
            receipt["status"] = "integrated"
        temporary = path.with_suffix(".tmp")
        with temporary.open("w") as output:
            temporary.chmod(0o600)
            output.write(json.dumps(receipt, indent=2) + "\n")
            output.flush(); os.fsync(output.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        record.append("say", actor, {"text": "house-integration-v1 " + json.dumps({
            k: v for k, v in receipt.items() if k != "candidate"}, sort_keys=True)})
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("run")
    parser.add_argument("--as", dest="actor", required=True)
    parser.add_argument("--publish", action="store_true", help="accept tested candidate by fast-forward")
    args = parser.parse_args()
    try:
        print(json.dumps(integrate(Record(args.repo), args.run, args.actor, publish=args.publish), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"integration retained for review: {type(error).__name__}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
