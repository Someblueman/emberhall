"""Owner-gated staffing and bounded helper admissions, never task ownership."""
from __future__ import annotations

from .model import require

SCOPE = "helper-staffing-20261114"
HELPER_MODELS = ("gpt-6-luna", "gpt-6.1-terra")
ROLES = {"build", "review"}


def enabled(state: dict) -> bool:
    # Unlike older synthetic fixtures, absence of a wake policy grants nothing.
    return SCOPE in state.get("maintenance", {}).get("migrations", {})


def helper(route: dict) -> bool:
    return route.get("agent") == "codex" and route.get("model") in HELPER_MODELS


def capacity(state: dict) -> dict:
    active = [r for r in state.get("life", {}).get("runs", {}).values() if r["status"] == "active"]
    helpers = sum(helper(r) for r in active)
    return {"baseline": 2 if enabled(state) else 1, "total_limit": 4 if enabled(state) else 3,
            "regular_limit": 3, "helper_limit": 2 if enabled(state) else 0,
            "regular": len(active) - helpers, "helpers": helpers, "total": len(active)}


def metadata(state: dict, value: str, *, clear: bool = False) -> None:
    require(enabled(state), "helper staffing requires activation migration")
    require(isinstance(value, str) and (value in ROLES or (clear and value == "none")),
            "invalid helper role")


def task_eligible(task: dict) -> bool:
    return task.get("helper") in ROLES and task.get("ready") is True and task.get("status") != "done"


def help_eligible(state: dict, request: dict, at: float, *, help_id: str | None = None) -> bool:
    from . import project_work
    if "review_run" in request:
        source = state.get("life", {}).get("runs", {}).get(request["review_run"], {})
        return source.get("status") == "completed"
    task_id = request.get("task")
    return (task_eligible(state["tasks"].get(task_id, {}))
            and project_work.available(state, task_id, at, help_id=help_id))


def validate_help(state: dict, request: dict) -> None:
    if helper(request):
        require(enabled(state), "helper staffing requires activation migration")
        require("review_run" in request or task_eligible(state["tasks"].get(request.get("task"), {})),
                "helper help requires an eligible task or independent source review")


def validate_admission(state: dict, data: dict, at: float) -> None:
    """Called inside the journal writer before any reservation is published."""
    from . import project_work
    c = capacity(state)
    if not helper(data):
        require(c["total"] < c["total_limit"] and c["regular"] < c["regular_limit"],
                "resident capacity reached" if enabled(state) else "three residents are already home")
        return
    require(enabled(state), "helper staffing requires activation migration")
    require(c["regular"] >= 2 and c["helpers"] < 2 and c["total"] < 4,
            "helper capacity changed")
    require("explore_generation" not in data, "helper cannot explore")
    help_id = data.get("help_request")
    request = state.get("life", {}).get("requests", {}).get(help_id, {})
    if help_id is not None:
        require(request.get("status") == "pending" and help_eligible(state, request, at, help_id=help_id),
                "helper help demand changed")
        if helper(request):
            require(data["model"] == request["model"], "helper requested model changed")
        else:
            require("model" not in request and request.get("agent", "codex") == "codex",
                    "helper cannot replace an explicit ordinary route")
        if "review_run" in request:
            source = state["life"]["runs"][request["review_run"]]
            require(data["resident"] != source["resident"], "source reviewer must be independent")
            require(not {"task", "task_generation", "backlog"} & data.keys()
                    and data["mode"] == "review", "invalid helper source review admission")
            return
        require(data.get("task") == request.get("task"), "helper task binding changed")
    require("task" in data and "task_generation" in data, "helper requires a bounded task")
    task_id = data["task"]
    task = state["tasks"].get(task_id, {})
    require(type(data["task_generation"]) is int and data["task_generation"] == task.get("generation"),
            "helper task generation changed")
    require(task_eligible(task) and project_work.available(state, task_id, at, help_id=help_id),
            "helper task demand changed")
    require((help_id is not None and "backlog" not in data) or
            (help_id is None and data.get("backlog") is True), "invalid helper task admission")
    require(data["mode"] == ("review" if task["helper"] == "review" else "work"),
            "helper task role changed")
    # Ordinary unassigned residents already cover this many ready tasks.
    if help_id is None:
        from .life import workload
        require(workload(state, at)["uncovered_tasks"] > 0, "helper task coverage changed")


def select(state: dict, at: float, demand: dict) -> dict | None:
    """Select real eligible demand; keep project-first ordering among candidates."""
    from . import project_work
    from .life import provider_available
    c = capacity(state)
    if (not enabled(state) or c["regular"] < 2 or c["helpers"] >= 2 or c["total"] >= 4
            or not provider_available(state, "codex", at)):
        return None
    requests = state.get("life", {}).get("requests", {})
    pending = [k for k in demand["pending_help"] if help_eligible(state, requests[k], at, help_id=k)
               and (helper(requests[k]) or
                    ("model" not in requests[k] and requests[k].get("agent", "codex") == "codex"))]
    ready = [k for k in demand["ready_tasks"] if task_eligible(state["tasks"][k])] if demand["uncovered_tasks"] else []
    # Eligibility cannot let unrelated helpers jump ahead of selected-project work.
    selected = project_work.first(state, at,
        demand["ready_tasks"] if demand["uncovered_tasks"] else [], demand["pending_help"])
    if selected and not (selected.get("task") in ready or selected.get("help_request") in pending):
        return None
    if selected is None:
        selected = {"help_request": pending[0]} if pending else (
            {"task": ready[0], "task_generation": state["tasks"][ready[0]]["generation"]} if ready else None)
    if selected is None:
        return None
    request = requests.get(selected.get("help_request"), {})
    if "task" in request and "review_run" not in request:
        selected.update(task=request["task"], task_generation=state["tasks"][request["task"]]["generation"])
    previous = [r for r in state.get("life", {}).get("runs", {}).values() if helper(r)]
    last = max(previous, key=lambda r: r["started_sequence"], default={}).get("model")
    selected["helper_model"] = request.get("model", HELPER_MODELS[1] if last == HELPER_MODELS[0] else HELPER_MODELS[0])
    return selected
