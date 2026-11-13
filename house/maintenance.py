"""Explicit owner maintenance, outside the resident council and mailbox.

These receipts are cooperative operator attribution, not cryptographic identity.
The operator authenticates GitHub before appending; resident tools expose neither
operation. Initial authorization and all council state remain untouched.
"""
from __future__ import annotations

import copy
import hashlib
import re

from . import council
from .governance import canonical, digest
from .model import require

OPENCODE_APPROVAL = (
    "Owner report, 13 November 2026: opencode should work now as well\n"
    "Owner direction after the existing one-day cooldown was explained: you can override it\n"
    "Scope: one early OpenCode retry for budget event300, not a success claim, "
    "new credential, provider change, council change or recurring bypass.\n"
)
OPENCODE_SHA256 = hashlib.sha256(OPENCODE_APPROVAL.encode()).hexdigest()
GROWTH_SHA256 = "b75e6dad4f16a7e23b3b9b808b5d9465b9c17160408a2b316cf312f32132ba9b"
RETRY_SCOPE = "opencode-retry-20261113"
GROWTH_SCOPE = "room-growth-20261113"
REPAIR_SCOPE = "opencode-cli-repair-20261113"
FAILED_CLI_RUN = "6eec53281c2641f28677a9a7bcc41e8d"
FAILED_CLI_SHA256 = "cb62a75b5184f48c6050e1be789a1786c1a64087fc99f11213c4d140dc661dab"
FAILED_CLI_OBSERVATION = 465
SOURCES = {RETRY_SCOPE: OPENCODE_SHA256, GROWTH_SCOPE: GROWTH_SHA256, REPAIR_SCOPE: GROWTH_SHA256}
RETRY_BUDGET_SEQUENCE = 300
RETRY_BUDGET_UNTIL = 1794676437.592195
OWNER_MODULES = {"house/maintenance.py", "house/owner_upgrade.py"}
ALLOWED_CHANGES = {
    REPAIR_SCOPE: OWNER_MODULES | {"house/providers.py", "house/opencode_tool.py", "house/opencode_auth.py", "house/home.py", "house/body.py"},
    RETRY_SCOPE: OWNER_MODULES | {"house/model.py", "house/wake_policy.py",
        "house/body.py", "house/watch_recovery.py", "house/life.py", "house/home.py"},
    GROWTH_SCOPE: OWNER_MODULES | {"house/building.py", "house/life.py", "house/council.py",
        "house/body.py", "house/resident_actions.py", "house/mailbox.py", "house/home.py",
        "house/model.py", "house/wake_policy.py", "house/watch_recovery.py"},
}


def protected_manifest(state: dict) -> dict:
    return state.get("maintenance", {}).get("protected_files",
                                            state["wake_policy"]["protected_files"])


def fingerprint(manifest: dict) -> str:
    return digest(canonical(manifest).decode())


def _owner(state: dict, event: dict) -> None:
    data = event["data"]
    require(state["house_id"] == council.APPROVED_HOUSE and
            data.get("house") == state["house_id"], "wrong maintenance house")
    require(data.get("owner_id") == council.OWNER_ID and
            event["actor"] == state["council"]["authorized_by"], "owner operator required")
    require(state["residents"][event["actor"]]["awake"], "owner operator is asleep")
    require(data.get("scope") in SOURCES and
            data.get("approval_sha256") == SOURCES[data["scope"]], "wrong owner approval")


def _sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None



def cli_failure_proven(state: dict) -> bool:
    failed = state.get("life", {}).get("runs", {}).get(FAILED_CLI_RUN, {})
    return (failed.get("status") == "completed" and failed.get("outcome") == "failed" and
            failed.get("exit_code") == 1 and failed.get("usage") == {} and
            failed.get("started_sequence") == 462 and failed.get("ended_sequence") == 466 and
            failed.get("agent") == "opencode" and failed.get("resident") not in state["residents"])


def apply(state: dict, event: dict) -> None:
    _owner(state, event)
    data, scope = event["data"], event["data"]["scope"]
    seq = state["sequence"] + 1
    if event["op"] == "owner-migrate":
        council.fields(data, {"scope", "approval_sha256", "house", "owner_id",
            "source_head", "source_sha256", "protected_files", "previous_manifest_sha256",
            "previous_runtime_sha256", "runtime_sha256", "test_output_sha256", "test_count"})
        old = protected_manifest(state)
        maintenance = state.get("maintenance", {})
        require(scope not in maintenance.get("migrations", {}), "owner migration already used")
        require(data["previous_manifest_sha256"] == fingerprint(old), "stale protected manifest")
        manifest = data["protected_files"]
        extra = OWNER_MODULES | ({"house/building.py"} if scope == GROWTH_SCOPE else set())
        if scope == REPAIR_SCOPE:
            extra.add("house/opencode_auth.py")
        require(isinstance(manifest, dict) and set(manifest) == set(old) | extra
                and all(_sha(value) for value in manifest.values()), "invalid replacement manifest")
        changes = {name for name in manifest if manifest[name] != old.get(name)}
        require(changes <= ALLOWED_CHANGES[scope], "source change outside owner maintenance scope")
        require(isinstance(data["source_head"], str) and
                re.fullmatch(r"[0-9a-f]{40}", data["source_head"]), "invalid source commit")
        require(all(_sha(data[key]) for key in ("source_sha256", "previous_runtime_sha256",
                "runtime_sha256", "test_output_sha256")), "invalid maintenance digest")
        require(type(data["test_count"]) is int and data["test_count"] > 0,
                "owner migration requires executed passing tests")
        require(not any(run["status"] == "active" for run in
                state.get("life", {}).get("runs", {}).values()), "drain native residents before migration")
        entry = copy.deepcopy(data) | {"at": event["at"], "sequence": seq, "actor": event["actor"]}
        current = copy.deepcopy(maintenance)
        current.setdefault("migrations", {})[scope] = entry
        current.update(protected_files=dict(manifest), at=event["at"],
                       room_growth=current.get("room_growth", False) or scope == GROWTH_SCOPE)
        state["maintenance"] = current
        if scope == GROWTH_SCOPE:
            from .building import initialize
            initialize(state)
    elif event["op"] == "owner-provider-release":
        extra = {"expected_observation", "failed_run", "failed_output_sha256"} if scope == REPAIR_SCOPE else set()
        council.fields(data, {"scope", "approval_sha256", "house", "owner_id",
                              "agent", "expected_sequence", "expected_until"} | extra)
        require(scope in {RETRY_SCOPE, REPAIR_SCOPE} and data["agent"] == "opencode", "only approved OpenCode hold may release")
        current = state.get("maintenance", {})
        require(scope in current.get("migrations", {}), "owner retry runtime is not authorized")
        require(scope not in current.get("releases", {}), "owner release already used")
        require(type(data["expected_sequence"]) is int and data["expected_sequence"] == RETRY_BUDGET_SEQUENCE and
                type(data["expected_until"]) in (int, float) and
                data["expected_until"] == RETRY_BUDGET_UNTIL, "wrong approved hold")
        observation = RETRY_BUDGET_SEQUENCE
        if scope == REPAIR_SCOPE:
            original = current.get("releases", {}).get(RETRY_SCOPE, {})
            require(original.get("consumed_run") == FAILED_CLI_RUN and
                    data["failed_run"] == FAILED_CLI_RUN and data["failed_output_sha256"] == FAILED_CLI_SHA256 and
                    type(data["expected_observation"]) is int and data["expected_observation"] == FAILED_CLI_OBSERVATION,
                    "repair credit requires the exact spent pre-provider attempt")
            require(cli_failure_proven(state),
                    "repair credit does not cover a model attempt or an uncertain failure")
            observation = FAILED_CLI_OBSERVATION
        budget = state["life"]["budgets"].get("opencode", {})
        require(budget.get("sequence") == data["expected_sequence"] and
                budget.get("until") == data["expected_until"] and
                state["life"].get("budget_observations", {}).get("opencode") == observation,
                "provider hold changed; do not erase new failure")
        require(event["at"] < budget["until"], "provider hold already elapsed")
        current.setdefault("releases", {})[scope] = copy.deepcopy(data) | {
            "at": event["at"], "sequence": seq, "previous": copy.deepcopy(budget)}
    else:
        raise ValueError("unknown owner maintenance operation")


def retry_permit(state: dict, agent: str, at: float) -> dict | None:
    """Return the still-valid one-use credit, without shortening any cooldown."""
    if agent != "opencode":
        return None
    life = state.get("life", {})
    budget = life.get("budgets", {}).get(agent, {})
    for scope in (REPAIR_SCOPE, RETRY_SCOPE):
        release = state.get("maintenance", {}).get("releases", {}).get(scope)
        if not release or "consumed_run" in release or at >= release["expected_until"]:
            continue
        if scope == REPAIR_SCOPE and not cli_failure_proven(state):
            continue
        observation = release.get("expected_observation", release["expected_sequence"])
        if (life.get("budget_observations", {}).get(agent) == observation and
                budget.get("sequence") == release["expected_sequence"] and
                budget.get("until") == release["expected_until"]):
            return release
    return None
