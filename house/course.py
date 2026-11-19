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

    The route furthest below its share of this agent's recent non-helper runs
    wins (providers.WEIGHTS: two Sol runs for each Astra 6.2 run, otherwise equal
    shares); ties go to the route used least recently, then to the listed order.
    Explorers and great-work builders take the agent's stronger route.
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
    # Where one more run would leave each route against its share: the lowest goes next.
    return min(pool, key=lambda model: ((counts[model] + 1) / providers.WEIGHTS.get(model, 1), last[model],
                                        pool.index(model)))


# Turns for every Codex resident (Steward, 18 November, night; owner migration below). "Rook seems to
# be doing a lot of work", and it was woken 26 times in a day against 15 to 18 for each Sol resident:
# the house chose a route first and then a resident on it, the two Codex routes took turns, and for most
# of the day one resident was alone on Astra 6.2. The Steward: "just rotate across all the codex
# residents when the others time out". From this migration an ordinary Codex wake goes to the Codex
# resident who has been asleep longest, whichever of the open routes it lives on, and it keeps its own
# route. Explorers and great works still take Sol, and their Sol resident goes to the back of the same
# queue afterwards. Only when every Codex resident is awake or holding a task does a newcomer arrive,
# on the route the weights choose (two Sol for each Astra 6.2). The other families are unchanged. The
# coordinator alone chooses who wakes, so the journal replays as before.
TURNS = "upgrade-20261118-codex-turns"


def turns(state: dict, kind: str) -> bool:
    return kind == "codex" and TURNS in state.get("maintenance", {}).get("migrations", {})


def next_resident(state: dict, kind: str, at: float, allowed=lambda resident: True) -> str | None:
    """The resident of this family who may return and has been asleep longest, across its open routes."""
    from .life import latest_run, lived, open_models, return_eligible
    routes = open_models(state, kind, at)
    waiting = [resident for resident in state["residents"]
               if allowed(resident) and (previous := latest_run(state, resident)) is not None
               and previous["agent"] == kind and lived(state, kind, previous["model"]) in routes
               and return_eligible(state, resident, kind, lived(state, kind, previous["model"]), at)]
    return min(waiting, key=lambda key: (latest_run(state, key)["ended_sequence"], key), default=None)
