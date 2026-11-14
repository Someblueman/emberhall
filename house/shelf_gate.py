"""Authority and lifecycle wiring for the idea shelf's deterministic reducer."""
from __future__ import annotations

from . import shelf
from .governance import digest
from .model import require

# Bind executable semantics to the exact resident-written proposal. A different
# work-selection policy needs matching implementation, not a magic title or ID.
POLICY_SHA256 = "9dc13aa7de1a23f99c6630adf3141ccd039048ee82ee03c51fe16535e6b54136"
RESEARCH = frozenset({"explore-start", "explore-publish", "explore-release"})
ACTIONS = RESEARCH | {"choice-open", "choice-vote", "idea-return",
                      "project-done", "project-drop", "project-extend-vote"}


def enabled(state: dict) -> bool:
    from .maintenance import KEEP_MOVING_SCOPE
    return "wake_policy" not in state or KEEP_MOVING_SCOPE in state.get("maintenance", {}).get("migrations", {})


def policy(state: dict) -> str | None:
    return next((name for name, rule in state.get("council", {}).get("rules", {}).items()
                 if rule["status"] == "active" and rule.get("mode", "rule") == "rule"
                 and digest(rule["text"]) == POLICY_SHA256), None)


def apply(state: dict, event: dict) -> None:
    require(enabled(state), "shelf runtime is not enabled")
    data = event["data"]
    require(data.get("kind") in ACTIONS, "unknown shelf action")
    if "trial" in data:
        name = data["trial"]
        require(isinstance(name, str), "invalid trial proposal")
        proposal = state["proposals"].get(name, {})
        require(proposal.get("mode") == "rule" and proposal.get("status") == "pending"
                and digest(proposal.get("text", "")) == POLICY_SHA256,
                "trial requires the supported pending work-selection proposal")
        require(proposal["base"] == state["rule_revision"], "trial proposal has a stale rule base")
        # Only the isolated shelf is replaced. All readers see live resident and
        # task evidence, but trial choices cannot create real projects or tasks.
        trials = state.setdefault("shelf_trials", {})
        context = state | {"shelf": trials.setdefault(name, shelf.empty())}
        shelf.apply(context, event | {"data": {k: v for k, v in data.items() if k != "trial"}})
    else:
        if data["kind"] not in RESEARCH:
            require(policy(state) is not None, "real project decisions require the enacted work-selection policy")
        shelf.apply(state, event)


def advance(state: dict, at: float, sequence: int) -> None:
    # Hooks run only where a shelf already exists, preserving every historical
    # projection before adoption. They never append side records on a read.
    shelf.advance(state, at, sequence)
    for trial in state.get("shelf_trials", {}).values():
        shelf.advance(state | {"shelf": trial}, at, sequence)


def briefing(state: dict) -> dict:
    return {"enabled": enabled(state), "policy": policy(state),
            "record": state.get("shelf", shelf.empty()),
            "trials": state.get("shelf_trials", {}),
            "note": "Trials are isolated demonstrations, never chosen house projects. "
                    "Deadlines reconcile at the next accepted event; reads do not write."}
