"""Explicit independent comparison work, distinct from the voting law."""
from __future__ import annotations

from .model import require, string

SCOPE = "ballot-work-routing-20261115"


def enabled(state: dict) -> bool:
    return "wake_policy" not in state or SCOPE in state.get("maintenance", {}).get("migrations", {})


def association(state: dict, data: dict) -> str:
    require(enabled(state), "ballot work runtime not enabled")
    choice = string(data, "ballot_choice", 100)
    require(choice in state.get("shelf", {}).get("choices", {}), "unknown ballot choice")
    return choice


def eligible(state: dict, task: dict, resident: str) -> bool:
    choice_id = task.get("ballot_choice")
    if not enabled(state) or choice_id is None:
        return True
    shelf = state["shelf"]
    choice = shelf["choices"][choice_id]
    if choice["status"] != "open":
        return True  # A worker can record the verified closed finding.
    return (resident in state["residents"] and resident not in choice["votes"]
            and all(shelf["ideas"][key]["author"] != resident for key in choice["candidates"]))


def uncovered(state: dict, tasks: list[str], residents: list[str]) -> list[str]:
    """Maximum matching: each idle resident covers at most one eligible task."""
    if not enabled(state):
        return tasks[min(len(tasks), len(residents)):]
    matched: dict[str, str] = {}
    def assign(task_id: str, seen: set[str]) -> bool:
        for resident in residents:
            if resident in seen or not eligible(state, state["tasks"][task_id], resident):
                continue
            seen.add(resident)
            if resident not in matched or assign(matched[resident], seen):
                matched[resident] = task_id
                return True
        return False
    # Generic cards are considered last so scarce eligible residents cover ballots.
    ordered = sorted(tasks, key=lambda key: ("ballot_choice" not in state["tasks"][key], tasks.index(key)))
    for task_id in ordered:
        assign(task_id, set())
    covered = set(matched.values())
    return [key for key in tasks if key not in covered]
