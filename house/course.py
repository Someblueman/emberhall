"""Steward course correction of 15 November 2026.

Activated only by the owner migration ``course-correction-20261115``; every
historical projection before it replays exactly as it did. See
docs/COURSE_CORRECTION_2026-11-15.md and docs/RENOVATION.md.
"""
from __future__ import annotations

from . import providers, staffing

SCOPE = "course-correction-20261115"
BUILD_STRETCH_SECONDS = 3600


def enabled(state: dict) -> bool:
    return SCOPE in state.get("maintenance", {}).get("migrations", {})


def great_project(state: dict, task: dict | None) -> dict | None:
    """The active great-work project a task belongs to, if any."""
    if not task or "project" not in task:
        return None
    project = state.get("shelf", {}).get("projects", {}).get(task["project"])
    if project and project.get("slot") == "great" and project["status"] == "active":
        return project
    return None


def route(state: dict, kind: str, *, strong: bool = False, at: float | None = None) -> str:
    """Spread ordinary runs across an agent's approved routes.

    The least-used route among this agent's recent non-helper runs wins; ties go
    to the route used least recently, then to the listed order. Explorers and
    great-work builders take the agent's stronger route.
    """
    from .life import model_available, open_models
    # A route resting on its quota is passed over; the stronger route falls back to the ordinary ones.
    if strong and (at is None or model_available(state, kind, providers.STRONG[kind], at)):
        return providers.STRONG[kind]
    pool = providers.ROTATION[kind]
    if at is not None:
        pool = tuple(open_models(state, kind, at)) or pool
    runs = sorted((run for run in state.get("life", {}).get("runs", {}).values()
                   if run["agent"] == kind and not staffing.helper(run)),
                  key=lambda run: run["started_sequence"])
    recent = runs[-providers.ROTATION_WINDOW:]
    counts = {model: sum(run["model"] == model for run in recent) for model in pool}
    last = {model: max((run["started_sequence"] for run in runs if run["model"] == model), default=0)
            for model in pool}
    return min(pool, key=lambda model: (counts[model], last[model], pool.index(model)))
