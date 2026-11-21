"""One complete canonical idea, without the rest of the historical briefing."""
from __future__ import annotations


def idea_status(state: dict, head: str, idea_id: str, actor: str | None) -> dict:
    if actor not in state["residents"]:
        raise ValueError("status --idea requires --as with a known resident")
    idea = state.get("shelf", {}).get("ideas", {}).get(idea_id)
    if idea is None:
        raise ValueError(f"unknown idea: {idea_id}")
    brief = idea.get("brief", {})
    revision = brief.get("sequence")
    # Older records have only `second`; newer ones retain every keeper in `seconds`.
    checks = list(idea.get("seconds", []))
    second = idea.get("second")
    if second is not None and not any(entry["sequence"] == second["sequence"] for entry in checks):
        checks.append(second)
    own = [entry for entry in checks if entry["author"] == actor]
    current = [entry for entry in own if revision is not None and entry["brief"] == revision]
    earlier = [entry for entry in own if entry not in current]
    return {
        "house_id": state["house_id"],
        "name": state["name"],
        "source": {"journal_head": head, "sequence": state["sequence"]},
        "idea_id": idea_id,
        "brief_revision": revision,
        "idea": idea,
        "caller": {
            "resident": actor,
            "authored_idea": idea["author"] == actor,
            "authored_current_brief": brief.get("author") == actor,
            "checked_current_brief": bool(current),
            "current_checks": current,
            "earlier_checks": earlier,
        },
        "limitations": [
            "Read-only snapshot: no event, acknowledgement or saved cursor is changed.",
            "The entire idea record is included. A changed brief revision needs a fresh check; "
            "this reply neither checks sources nor decides eligibility under the charter.",
        ],
    }
