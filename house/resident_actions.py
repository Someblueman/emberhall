"""Resident-requested council and foundation actions, without owner initializers."""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from .files import artifact, workspace_path
from .record import Record

ACTIONS = frozenset({"council", "integrate", "runtime-test", "runtime-refresh", "checkpoint", "review-complete",
                     "view", "read-site", "reedbank"})


def parser():
    root = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ACTIONS:
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("--as", dest="actor", required=True)
        command.add_argument("--request")
        if name == "integrate":
            command.add_argument("target")
            mode = command.add_mutually_exclusive_group()
            mode.add_argument("--publish", action="store_true")
            mode.add_argument("--inspect", action="store_true")
            mode.add_argument("--export-patch", action="store_true")
            mode.add_argument("--reject")
            command.add_argument("--path")
            command.add_argument("--diff-after", type=int)
            command.add_argument("--content-after", type=int)
            command.add_argument("--bundle", action="store_true")
            command.add_argument("--paths", nargs="+")
            command.add_argument("--offset", type=int)
            command.add_argument("--preview", action="store_true")
        elif name == "view":
            # See one page of your own room rendered (house/view.py); no journal event.
            command.add_argument("path")
            command.add_argument("--steps")
        elif name == "read-site":
            # Read one page or asset of the house's own public site (house/site_read.py); no journal event.
            command.add_argument("path", nargs="?", default="")
        elif name == "reedbank":
            # The one supervised wake in the daughter house (house/daughter.py); no Emberhall journal event.
            from .daughter import arguments
            arguments(command)
        elif name.startswith("runtime-") or name in {"checkpoint", "review-complete"}:
            command.add_argument("--task", required=True)
            if name in {"runtime-test", "checkpoint", "review-complete"}:
                command.add_argument("--token", required=True)
        else:
            council = command.add_subparsers(dest="action", required=True)
            for action in ("status", "wake-prompt", "propose", "trial", "endorse", "notice", "sync", "enact"):
                item = council.add_parser(action, allow_abbrev=False)
                if action in {"propose", "trial", "endorse", "notice", "enact"}:
                    item.add_argument("proposal")
                if action == "propose":
                    item.add_argument("--title", required=True)
                    item.add_argument("--file", required=True)
                    item.add_argument("--reason", required=True)
                    from .council import MODES
                    item.add_argument("--mode", choices=sorted(MODES), default="rule")
                if action in {"trial", "endorse"}:
                    item.add_argument("--evidence", required=True)
                if action == "trial":
                    item.add_argument("--task", required=True)
    return root


def parse(argv: list[str], resident: str):
    args = parser().parse_args(argv)
    if args.actor != resident:
        raise ValueError("this action belongs to another resident")
    return args


def known_result(record: Record, resident: str, run: str, argv: list[str], requestid: str):
    """Recognize accepted effects after a lost worker reply; never execute here."""
    args = parse(argv, resident)
    if args.command in {"view", "read-site", "reedbank"}:
        return None     # nothing of Emberhall's to recognize; an interrupted Reedbank request is asked again
    if args.command == "checkpoint":
        from .checkpoint import known_result as checkpoint_result
        return checkpoint_result(record, resident, run, args.task, args.token, requestid)
    if args.command == "review-complete":
        from .review_completion import known_result as review_result

        return review_result(record, args.task, resident, args.token, requestid)
    state, events, _ = record.read()
    key = requestid
    if args.command == "council" and args.action in {"notice", "enact"}:
        key = "council-" + args.action + "-" + args.proposal
    if args.command == "runtime-test":
        key = "runtime-tested-" + args.task
    if key in state["receipts"]:
        sequence = state["receipts"][key]
        if events[sequence - 1]["actor"] == resident:
            return {"request": key, "sequence": sequence, "replayed": True}
    if args.command == "runtime-refresh":
        from .runtime import selected
        try:
            receipt = selected(record)
        except FileNotFoundError:
            return None
        proof = receipt.get("attestation", {})
        if (proof.get("resident"), proof.get("run"), proof.get("task")) == (resident, run, args.task):
            return receipt
    return None


def execute(record: Record, workspace: Path, resident: str, run: str, argv: list[str], requestid: str):
    args = parse(argv, resident)
    state = record.read()[0]
    item = state.get("life", {}).get("runs", {}).get(run, {})
    expected = workspace_path(record, run, state)
    if (item.get("status") != "active" or item.get("resident") != resident or
            "launched_sequence" not in item or workspace != expected or
            not state["residents"].get(resident, {}).get("awake")):
        raise ValueError("action needs its assigned active, awake resident and fixed room")
    previous = known_result(record, resident, run, argv, requestid)
    if previous is not None:
        return previous
    if args.command == "view":
        from .view import render
        return render(workspace, args.path, args.steps)
    if args.command == "read-site":
        from .site_read import read_site
        return read_site(record.common / "house-home" / "site-read", run, args.path)
    if args.command == "reedbank":
        from .daughter import act
        return act(record, resident, run, args, requestid)
    if args.command == "checkpoint":
        from .checkpoint import create
        return create(record, workspace, resident, run, args.task, args.token, requestid)
    if args.command == "review-complete":
        from .review_completion import complete

        return complete(record, args.task, resident, args.token, requestid)
    if args.command == "integrate":
        from .integrate import integrate, inspect_contribution, validate_inspect_options, export_contribution
        if args.export_patch:
            if (args.path is not None or args.bundle or args.offset is not None or args.preview
                    or args.diff_after is not None or args.content_after is not None):
                raise ValueError("--export-patch accepts only optional --paths")
            return export_contribution(record, args.target, resident, workspace, args.paths)
        validate_inspect_options(
            inspect=args.inspect, path=args.path,
            diff_after=args.diff_after, content_after=args.content_after,
            bundle=args.bundle, paths=args.paths, offset=args.offset, preview=args.preview,
        )
        if args.inspect:
            return inspect_contribution(
                record, args.target, resident, args.path,
                diff_after=args.diff_after, content_after=args.content_after,
                bundle=args.bundle, paths=args.paths, offset=args.offset, preview=args.preview)
        return integrate(record, args.target, resident, publish=args.publish, reject=args.reject)
    if args.command == "runtime-test":
        from .wake_policy import test_runtime
        return test_runtime(record, resident, run, args.task, args.token, record.root)
    if args.command == "runtime-refresh":
        from .runtime import activate
        return activate(record, resident, args.task, run)
    from . import steward
    if args.action == "status":
        return {"council": state.get("council"), "proposals": state["proposals"]}
    if args.action == "wake-prompt":
        from .wake_policy import active_policy, active_prompt
        return {**active_policy(state), "assembled_prompt": active_prompt(state)}
    if args.action == "sync":
        return steward.sync(record, resident, requestid)
    if args.action == "notice":
        return steward.publish_notice(record, resident, args.proposal)
    if args.action == "enact":
        steward.sync(record, resident, requestid + "-sync")
        return record.append("council-enact", resident, {"proposal": args.proposal},
                             "council-enact-" + args.proposal)
    data = {"proposal": args.proposal}
    if args.action == "propose":
        content = base64.b64decode(artifact(workspace, args.file)["base64"]).decode()
        data.update(mode=args.mode, title=args.title, text=content, reason=args.reason, base=state["rule_revision"])
    else:
        data["evidence"] = args.evidence
        if args.action == "trial":
            data["task"] = args.task
    return record.append("council-" + args.action, resident, data, requestid)
