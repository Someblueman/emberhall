"""Recorded places, continuing ambitions and supervised resident lifetimes.

This is a projection, not a process monitor. Only the supervisor's observed
receipts establish process starts/stops; an arrival alone is not proof of liveness.
"""
from __future__ import annotations

import math
import re

from .model import require, string
from . import staffing

CONTROLLER = "watch-keeper"
KINDS = {"codex", "opencode", "muse", "agy"}
ROOMS = {"door": "The Door", "hearth": "The Hearth", "workshop": "The Workshop",
         "archive": "The Archive", "council": "The Council", "bedroom": "The Beds"}


def number(value, name, minimum=0):
    require(type(value) in (int, float) and math.isfinite(value) and value >= minimum,
            f"invalid {name}")
    return value


def fields(data, required, optional=()):
    require(set(required) <= data.keys() <= set(required) | set(optional), "invalid life fields")


def identifier(data, key):
    value = string(data, key, 100)
    require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", value) is not None, f"invalid {key}")
    return value


def empty():
    return {"rooms": {key: {"name": name} for key, name in ROOMS.items()},
            "ambitions": {}, "runs": {}, "budgets": {}, "requests": {}, "presence": {}}


def latest_run(state: dict, resident: str, *, exclude: str | None = None) -> dict | None:
    runs = (item for key, item in state.get("life", {}).get("runs", {}).items()
            if key != exclude and item["resident"] == resident)
    return max(runs, key=lambda item: item["started_sequence"], default=None)


# A route retired (Steward, 19 November, midday; owner migration below). Codex ran out as well, and the
# Steward: "I think we need to drop Astra as part of this as it's the one using a lot of tokens". From
# the migration no run starts on a retired route (model_available refuses it, in the coordinator and
# in the record), and the residents who lived on it are not lost: each returns on the route named in
# providers.RETIRED (Rook, Linnet and Mica wake on Sol). Before the migration nothing changes, so the
# journal replays as before.
RETIRED = "upgrade-20261119-astra-retired"


def lived(state: dict, agent: str | None, model: str | None) -> str | None:
    """The route a resident of this route lives on now: its successor if the route was retired."""
    if RETIRED not in state.get("maintenance", {}).get("migrations", {}):
        return model
    from .providers import RETIRED as successors
    return successors.get(agent, {}).get(model, model)


def return_eligible(state: dict, resident: str, agent: str, model: str, at: float) -> bool:
    """A stopped supervised mind may return; its run and workspace never do."""
    if state.get("maintenance", {}).get("resident_returns") is not True:
        return False
    person = state["residents"].get(resident)
    if not person or person["awake"] is not False:
        return False
    runs = state.get("life", {}).get("runs", {})
    if any(item["resident"] == resident and item["status"] == "active" for item in runs.values()):
        return False
    previous = latest_run(state, resident)
    if not previous or previous["status"] != "completed" or (
            previous["agent"], lived(state, previous["agent"], previous["model"])) != (agent, model):
        return False
    if ("agent" in person or "model" in person) and (
            person.get("agent"), lived(state, person.get("agent"), person.get("model"))) != (agent, model):
        return False
    return not any(task.get("owner") == resident and task["status"] == "claimed" and task["until"] > at
                   for task in state["tasks"].values())


# Quota rest (Steward, 16 November, late; owner migration below). OpenCode's weekly limit and one
# Antigravity model's limit had run out for six days, and each says so when it refuses. The house
# benched the whole family for fifteen minutes and then spent a real start finding out again: 66
# starts lost in a day, and Antigravity's other model, which still worked, sat out with the capped
# one. From this migration a quota rests the one model that hit it, until the time its provider
# gave (checked again every twelve hours in case the limit was lifted early), and the family stays
# available while any of its ordinary routes is open. Codex takes the share the resting routes leave.
QUOTA_REST = "upgrade-20261116-quota-rest"
PROBE_SECONDS = 12 * 3600


def quota_rest(state: dict) -> bool:
    return QUOTA_REST in state.get("maintenance", {}).get("migrations", {})


def model_available(state: dict, agent: str, model: str, at: float) -> bool:
    if lived(state, agent, model) != model:
        return False    # a retired route: nothing starts on it again
    return state.get("life", {}).get("model_budgets", {}).get(agent, {}).get(model, {}).get("until", 0) <= at


def open_models(state: dict, agent: str, at: float) -> list[str]:
    """This family's ordinary routes that are not resting on a quota."""
    from .providers import ROTATION
    return [model for model in ROTATION[agent] if model_available(state, agent, model, at)]


# A limit whose return time the house cannot read (Steward, 18 November, night). Muse names a moment
# ("resets at 2026-11-23T00:00:00Z") where the others give a wait, the house did not read it, and each
# refusal was a fifteen-minute rest and then another lost start: 25 of 34 Muse starts in twelve hours.
# The Steward: "If muse has run out of tokens let's fall back to more codex". providers.reset_after now
# reads Muse's form. For any refusal that still gives no time, the route rests fifteen minutes after the
# first and twice as long after each further one in a row, up to four hours; one finished run on that
# route starts the count again. Codex takes the share meanwhile (home.provider_shares), exactly as for a
# limit with a stated return. Only the coordinator's choice of "until" changes, so the journal replays
# as before.
UNKNOWN_REST_SECONDS = 900
UNKNOWN_REST_LIMIT = 4 * 3600


def refusals(state: dict, agent: str, model: str, run: str | None = None) -> int:
    """How many of this route's latest ended runs in a row ended on its quota, not counting `run`."""
    ended = sorted((item for key, item in state.get("life", {}).get("runs", {}).items()
                    if key != run and item["agent"] == agent and item["model"] == model
                    and item["status"] != "active"), key=lambda item: item["started_sequence"])
    count = 0
    for item in reversed(ended):
        if item.get("outcome") != "quota":
            break
        count += 1
    return count


def unknown_rest(state: dict, agent: str, model: str, run: str | None = None) -> int:
    """Seconds a route rests after a quota refusal that named no return time (`run` is that refusal)."""
    return min(UNKNOWN_REST_LIMIT, UNKNOWN_REST_SECONDS * 2 ** min(refusals(state, agent, model, run), 10))


def provider_available(state: dict, agent: str, at: float) -> bool:
    from .maintenance import retry_permit
    if not (state.get("life", {}).get("budgets", {}).get(agent, {}).get("until", 0) <= at
            or retry_permit(state, agent, at) is not None):
        return False
    return not state.get("life", {}).get("model_budgets", {}).get(agent) or bool(open_models(state, agent, at))


def backlog_enabled(state: dict) -> bool:
    from .maintenance import BACKLOG_SCOPE
    return "wake_policy" not in state or BACKLOG_SCOPE in state.get("maintenance", {}).get("migrations", {})


EXPLORER_ADMISSION_SECONDS = 900
IDLE_COVERAGE_SCOPE = "idle-coverage-20261115"


def generic_run_reserved(state: dict, run: dict, at: float) -> bool:
    """Keep an unclaimed generic admission useful for one finite claim window."""
    if ("wake_policy" in state
            and IDLE_COVERAGE_SCOPE not in state.get("maintenance", {}).get("migrations", {})):
        return True
    return at < run.get("started_at", at) + EXPLORER_ADMISSION_SECONDS


def explorer_reserved(run: dict, at: float) -> bool:
    """A wake gets a finite chance to claim the real, separately fenced role."""
    return (run["status"] == "active" and "explore_generation" in run
            and at < run["started_at"] + EXPLORER_ADMISSION_SECONDS)


def explorer_owner(state: dict, at: float) -> str | None:
    record = state.get("shelf", {})
    expedition = record.get("rounds", {}).get(record.get("explorer"))
    if (expedition and expedition["until"] > at
            and state["residents"][expedition["owner"]]["awake"]):
        return expedition["owner"]
    return None


def explorer_demand(state: dict, at: float) -> int | None:
    from . import shelf, shelf_gate
    from .maintenance import EXPLORER_SCOPE
    if (EXPLORER_SCOPE not in state.get("maintenance", {}).get("migrations", {})
            or not shelf_gate.enabled(state) or shelf_gate.policy(state) is None):
        return None
    record = state.get("shelf", shelf.empty())
    from .governance import digest
    rule = shelf_gate.policy(state)
    version = shelf_gate.SUPPORTED_POLICIES[digest(state["council"]["rules"][rule]["text"])]
    if not shelf.research_open(state, record, at, version):
        return None
    if explorer_owner(state, at) is not None:
        return None
    if any(explorer_reserved(run, at) for run in state.get("life", {}).get("runs", {}).values()):
        return None
    return record["generation"]


TARGETED_SCOPE = "targeted-resident-wakes-20261114"


# Notes, not wakes (Steward, 20 November: "We ran out of tokens pretty quickly, but I don't see any work
# actually happening?"). Between 04:00 and 08:30 residents left one another about ninety targeted help
# requests with no task and no contribution to review ("Coordination with your current run only, no extra
# staffing"). Each one woke its resident for a whole session, about three hours later, when the matter was
# settled: 49 of the 59 Codex sessions after 10:11 were spent confirming that, and Codex ran out at 11:43.
# From this migration such a request is a note. It wakes nobody, and the coordinator puts it in the
# resident's next prompt and resolves it there. Help with a task or a review to do still wakes someone.
NOTES = "upgrade-20261120-notes-not-wakes"


def note(state: dict, request: dict) -> bool:
    """A targeted request with nothing to do attached: delivered at the resident's next wake, never a wake."""
    return (NOTES in state.get("maintenance", {}).get("migrations", {}) and "target_resident" in request
            and "task" not in request and "review_run" not in request)


def waiting_notes(state: dict, resident: str) -> list[tuple[str, dict]]:
    requests = state.get("life", {}).get("requests", {})
    return sorted(((key, request) for key, request in requests.items()
                   if request["status"] == "pending" and request.get("target_resident") == resident
                   and note(state, request)), key=lambda item: float(item[1].get("at") or 0))


def targeted_pending_eligible(state: dict, request: dict, at: float) -> bool:
    """Targeted pending help is eligible only for its exact resident/route."""
    target = request.get("target_resident")
    if target is None:
        return True
    if note(state, request):
        return False
    # Pinned runtime gate: targeted help is usable only after activation migration
    # when a pinned wake_policy is present; synthetic no-policy states test directly.
    if "wake_policy" in state:
        if TARGETED_SCOPE not in state.get("maintenance", {}).get("migrations", {}):
            return False
    agent = request.get("agent")
    model = request.get("model")
    if agent is None or model is None:
        return False
    if not return_eligible(state, target, agent, model, at):
        return False
    if not provider_available(state, agent, at):
        return False
    if not model_available(state, agent, model, at):
        return False    # its exact route is resting on a quota: it waits, and must not hold up other starts
    if "review_run" in request:
        source = state.get("life", {}).get("runs", {}).get(request["review_run"], {})
        if target == source.get("resident"):
            return False
    from . import ballot_work
    task = state.get("tasks", {}).get(request.get("task"), {})
    if not ballot_work.eligible(state, task, target):
        return False
    return True


def workload(state: dict, at: float) -> dict:
    """Count declared work and unclaimed native capacity, not apparent CPU activity."""
    from .home_control import paused
    life = state.get("life", {})
    active = {key: run for key, run in life.get("runs", {}).items() if run["status"] == "active"}
    active_residents = {run["resident"] for run in active.values()}
    requests = life.get("requests", {})
    from . import ballot_work, project_work
    project_routing = project_work.enabled(state)
    pending = [key for key, request in requests.items() if request["status"] == "pending"
               and project_work.help_available(state, request, at, help_id=key)
               and (not staffing.helper(request) or staffing.help_eligible(state, request, at, help_id=key))
               and targeted_pending_eligible(state, request, at)]
    reserved = {request.get("task") for request in requests.values()
                if request["status"] == "pending" or
                (request["status"] == "assigned" and request.get("run") in active)}
    claimed = {task["owner"] for task in state["tasks"].values()
               if task["status"] == "claimed" and (task["until"] > at or task["owner"] in active_residents)}
    task_reservations = {run["task"] for run in active.values()
                         if "task" in run and project_work.reserved(
                             run, at, state["tasks"].get(run["task"], {}))
                         and (project_routing or (ballot_work.enabled(state) and
                              "ballot_choice" in state["tasks"].get(run["task"], {})))}
    exploring = explorer_owner(state, at)
    idle = [run["resident"] for key, run in active.items() if run["resident"] not in claimed
            and run["resident"] != exploring
            and not explorer_reserved(run, at)
            and generic_run_reserved(state, run, at)
            and not ("task" in run and (project_routing or
                     (ballot_work.enabled(state) and "ballot_choice" in state["tasks"].get(run["task"], {}))))
            and not staffing.helper(run)
            and not (requests.get(run.get("help_request"), {}).get("status") == "assigned")]
    ready = [key for key, task in state["tasks"].items()
             if backlog_enabled(state) and task.get("ready") is True and task["status"] != "done" and task["until"] <= at
             and not (task["status"] == "claimed" and task["owner"] in active_residents)
             and key not in reserved and key not in task_reservations
             and (not project_routing or "project" not in task
                  or project_work.active_project(state, task["project"], at) is not None)]
    uncovered_ids = ballot_work.uncovered(state, ready, idle)
    uncovered = len(uncovered_ids)
    explore = explorer_demand(state, at)
    capacity = staffing.capacity(state)
    return {"ready_tasks": ready, "uncovered_task_ids": uncovered_ids, "idle_residents": idle, "pending_help": pending,
            "uncovered_tasks": uncovered, "explore_generation": explore,
            "wanted_starts": 0 if paused(state, at) else min(max(0, capacity["total_limit"] - len(active)),
                                 max(capacity["baseline"] - capacity["regular"],
                                     len(pending) + uncovered + (explore is not None)))}


def apply(state, event):
    data, actor, at = event["data"], event["actor"], event["at"]
    seq = state["sequence"] + 1
    life = state.setdefault("life", empty())
    kind = string(data, "kind", 40)
    growth = state.get("maintenance", {}).get("room_growth") is True
    if kind in {"room-plan", "room-open", "room-repurpose", "room-close"}:
        from .building import apply as build
        build(state, event)
    elif kind == "identity":
        fields(data, {"kind", "agent", "model"})
        from .providers import validate_model
        validate_model(data["agent"], data["model"])
        require(not staffing.helper(data) or staffing.enabled(state),
                "helper staffing requires activation migration")
        resident = state["residents"][actor]
        require("agent" not in resident, "resident kind already recorded")
        assigned = [r for r in life["runs"].values() if r["resident"] == actor]
        require(not assigned or (assigned[-1]["agent"], assigned[-1]["model"]) ==
                (data["agent"], data["model"]), "identity differs from actual assigned route")
        resident.update(agent=data["agent"], model=data["model"])
    elif kind == "room":
        require(not growth, "new rooms require room-plan and witnessed construction")
        fields(data, {"kind", "room", "name"})
        room = identifier(data, "room")
        require(room not in life["rooms"], "room already exists")
        life["rooms"][room] = {"name": string(data, "name", 100), "sequence": seq}
    elif kind == "activity":
        fields(data, {"kind", "room"}, {"task"})
        require(data["room"] in life["rooms"], "unknown room")
        if "task" in data:
            task = state["tasks"].get(data["task"], {})
            require(task.get("owner") == actor and task.get("status") == "claimed"
                    and task["until"] > at, "activity requires own live task")
        if growth:
            from .building import activity
            room = life["rooms"][data["room"]]
            require(room.get("status") != "construction" or data.get("task") == room["task"],
                    "construction activity must name its construction task")
            activity(state, actor, data["room"], at, seq)
        life["presence"][actor] = {**data, "at": at, "sequence": seq}
    elif kind == "ambition":
        fields(data, {"kind", "ambition", "title", "description", "status", "next_step", "expect"})
        key = identifier(data, "ambition")
        old = life["ambitions"].get(key, {})
        require(type(data["expect"]) is int and data["expect"] == old.get("generation", 0),
                "ambition generation changed")
        require(data["status"] in {"growing", "resting", "fulfilled"}, "invalid ambition status")
        for name in ("title", "description", "next_step"):
            string(data, name)
        life["ambitions"][key] = {**data, "generation": data["expect"] + 1,
                                  "resident": actor, "sequence": seq, "at": at}
    elif kind == "help":
        fields(data, {"kind", "request", "reason"}, {"task", "agent", "model", "review_run", "target_resident"})
        key = identifier(data, "request")
        require(key not in life["requests"], "help request exists")
        string(data, "reason")
        if "review_run" in data:
            from .source_delivery import enabled
            require(enabled(state), "source delivery is not enabled")
            source = life["runs"].get(identifier(data, "review_run"), {})
            require(source.get("status") == "completed", "source review requires a stopped contribution")
        if "task" in data:
            require(data["task"] in state["tasks"], "unknown help task")
        if "agent" in data:
            require(data["agent"] in KINDS, "unknown agent kind")
        if "model" in data:
            require("agent" in data, "a model preference requires its agent kind")
            from .providers import validate_model
            validate_model(data["agent"], data["model"])
        staffing.validate_help(state, data)
        if "target_resident" in data:
            require(state.get("maintenance", {}).get("resident_returns") is True,
                    "targeted help requires resident returns enabled")
            # Activation gate: pinned runtime requires migration before targeted help is usable.
            if "wake_policy" in state:
                require(TARGETED_SCOPE in state.get("maintenance", {}).get("migrations", {}),
                        "targeted help requires activation migration")
            require("agent" in data and "model" in data,
                    "targeted help requires explicit agent and model")
            target = identifier(data, "target_resident")
            person = state["residents"].get(target)
            require(person is not None, "unknown targeted resident")
            previous = latest_run(state, target)
            require(previous is not None, "targeted resident is not supervised")
            require((previous["agent"], lived(state, previous["agent"], previous["model"])) ==
                    (data["agent"], data["model"]), "targeted route does not match latest run")
            if ("agent" in person or "model" in person):
                require((person.get("agent"), lived(state, person.get("agent"), person.get("model"))) ==
                        (data["agent"], data["model"]), "targeted identity does not match resident route")
            if "review_run" in data:
                source = life["runs"].get(identifier(data, "review_run"), {})
                require(target != source.get("resident"),
                        "targeted help cannot request source author as reviewer")
        life["requests"][key] = {**data, "resident": actor, "status": "pending", "at": at}
    else:
        require(actor == CONTROLLER, "only the supervisor records process observations")
        if kind == "run-start":
            from .home_control import paused
            require(not paused(state, at), "owner paused admissions")
            fields(data, {"kind", "run", "resident", "agent", "model", "source_head",
                          "workspace", "policy_revision", "mode"}, {"help_request", "backlog", "explore_generation",
                                                          "task", "task_generation", "ballot_open"})
            from .providers import validate_model
            validate_model(data["agent"], data["model"])
            run = identifier(data, "run")
            resident = identifier(data, "resident")
            require(run not in life["runs"], "run already exists")
            require(resident not in state["residents"] or
                    return_eligible(state, resident, data["agent"], data["model"], at),
                    "run resident already exists and is not eligible to return")
            active = [r for r in life["runs"].values() if r["status"] == "active"]
            staffing.validate_admission(state, data, at)
            require(all(r["resident"] != resident for r in active), "resident already running")
            require(provider_available(state, data["agent"], at),
                    "provider is cooling down")
            require(model_available(state, data["agent"], data["model"], at),
                    "this model is resting until its quota returns")
            require(data["mode"] in {"work", "review"}, "invalid work mode")
            require(re.fullmatch("[0-9a-f]{40}", data["source_head"]) is not None,
                    "invalid source head")
            string(data, "policy_revision", 100)
            require(data["workspace"] == "residents/" + run, "invalid private workspace")
            if "explore_generation" in data:
                require(type(data["explore_generation"]) is int and
                        not {"help_request", "backlog"} & data.keys(), "invalid Explorer admission")
                require(explorer_demand(state, at) == data["explore_generation"],
                        "Explorer demand changed")
            from . import ballot_work, project_work
            request_task = life["requests"].get(data.get("help_request"), {}).get("task")
            task_id = data.get("task", request_task)
            task = state["tasks"].get(task_id, {})
            requested_task = state["tasks"].get(request_task, {})
            if ballot_work.enabled(state) and "ballot_choice" in requested_task:
                require(data.get("task") == request_task, "ballot task binding changed")
            if ballot_work.enabled(state) and "ballot_choice" in task:
                require(((data.get("backlog") is True and "help_request" not in data) or
                         ("help_request" in data and "backlog" not in data)),
                        "invalid ballot task admission")
                require(data.get("task") == task_id and type(data.get("task_generation")) is int
                        and data["task_generation"] == task.get("generation"), "ballot task generation changed")
                require(project_work.available(state, task_id, at, help_id=data.get("help_request")),
                        "ballot task demand changed")
                choice = state["shelf"]["choices"][task["ballot_choice"]]
                require(type(data.get("ballot_open")) is bool and data["ballot_open"] == (choice["status"] == "open"),
                        "ballot choice state changed")
                require(ballot_work.eligible(state, task, resident), "ballot resident eligibility changed")
                if data.get("backlog") is True:
                    require(task_id in workload(state, at)["uncovered_task_ids"], "ballot task coverage changed")
            else:
                require("ballot_open" not in data, "invalid ballot admission")
                if not staffing.helper(data) and {"task", "task_generation"} & data.keys():
                    project_work.validate_admission(state, data, at)
            if "backlog" in data:
                require(data["backlog"] is True and "help_request" not in data,
                        "invalid backlog admission")
                require(workload(state, at)["uncovered_tasks"] > 0,
                        "ready backlog demand changed")
            if "help_request" in data:
                request = life["requests"].get(data["help_request"], {})
                require(request.get("status") == "pending", "help already taken")
                from .project_work import help_available
                require(help_available(state, request, at, help_id=data["help_request"]),
                        "project help demand changed")
                if "target_resident" in request:
                    target = request["target_resident"]
                    if "wake_policy" in state:
                        require(TARGETED_SCOPE in state.get("maintenance", {}).get("migrations", {}),
                                "targeted help requires activation migration")
                    require(resident == target,
                            "targeted admission resident mismatch")
                    require((data["agent"], data["model"]) == (request.get("agent"), request.get("model")),
                            "targeted admission route mismatch")
                    require(return_eligible(state, resident, data["agent"], data["model"], at),
                            "targeted resident is not eligible")
                    require(provider_available(state, data["agent"], at),
                            "provider is cooling down")
                if "review_run" in request:
                    require(resident != life["runs"][request["review_run"]]["resident"],
                            "source reviewer must be independent")
                request.update(status="assigned", run=run)
            from .maintenance import retry_permit
            permit = retry_permit(state, data["agent"], at)
            if permit is not None:
                permit.update(consumed_run=run, consumed_sequence=seq, consumed_at=at)
            life["runs"][run] = {**data, "status": "active", "started_at": at,
                                 "started_sequence": seq}
        elif kind == "run-launched":
            fields(data, {"kind", "run", "pgid"})
            run = life["runs"][data["run"]]
            require(run["status"] == "active" and "pgid" not in run, "run already launched/ended")
            require(type(data["pgid"]) is int and data["pgid"] > 1, "invalid process group")
            run.update(pgid=data["pgid"], launched_sequence=seq)
        elif kind == "run-finish":
            fields(data, {"kind", "run", "outcome", "exit_code", "usage", "elapsed_seconds"})
            run = life["runs"][data["run"]]
            require(run["status"] == "active", "run already ended")
            require(data["outcome"] in {"success", "quota", "interrupted", "failed"}, "invalid outcome")
            require(data["exit_code"] is None or type(data["exit_code"]) is int, "invalid exit code")
            require(isinstance(data["usage"], dict), "invalid usage")
            for key, value in data["usage"].items():
                require(key in {"input_tokens", "output_tokens", "cached_input_tokens", "total_tokens"},
                        "unknown usage field")
                number(value, key)
            number(data["elapsed_seconds"], "elapsed seconds")
            run.update(outcome=data["outcome"], exit_code=data["exit_code"], usage=dict(data["usage"]),
                       elapsed_seconds=data["elapsed_seconds"], status="completed", ended_at=at,
                       ended_sequence=seq)
            if run["resident"] in state["residents"]:
                state["residents"][run["resident"]]["awake"] = False
            # The supervisor has confirmed the entire process group stopped.
            # Fence its old tokens immediately, preserving the generation and
            # token history. Unconfirmed/manual disappearances still use expiry.
            released = []
            for task_id, task in state["tasks"].items():
                if task["owner"] == run["resident"] and task["status"] == "claimed":
                    released.append(task_id)
                    task.update(status="open", owner=None, token=None, until=0,
                                interrupted_run=data["run"])
            run["released_tasks"] = released
            # Native exit success alone does not prove a help request was handled.
            # The supervisor separately records an accepted handoff as resolved.
            if "help_request" in run:
                request = life["requests"][run["help_request"]]
                if request.get("run") == data["run"] and request["status"] == "assigned":
                    request.update(status="pending")
                    request.pop("run", None)
        elif kind == "budget" and "model" in data:
            # One model's quota: only that route rests. resets_at is when its provider said it returns.
            require(quota_rest(state), "model quota rests are not enabled yet")
            fields(data, {"kind", "agent", "model", "until", "reason"}, {"resets_at"})
            require(data["agent"] in KINDS, "unknown agent kind")
            from .providers import validate_model
            validate_model(data["agent"], data["model"])
            number(data["until"], "cooldown", at)
            if "resets_at" in data:
                number(data["resets_at"], "quota reset", at)
            string(data, "reason", 1000)
            rests = life.setdefault("model_budgets", {}).setdefault(data["agent"], {})
            if data["until"] >= rests.get(data["model"], {}).get("until", 0):
                rests[data["model"]] = {**data, "at": at, "sequence": seq}
        elif kind == "budget":
            fields(data, {"kind", "agent", "until", "reason"})
            require(data["agent"] in KINDS, "unknown agent kind")
            number(data["until"], "cooldown", at)
            string(data, "reason", 1000)
            life.setdefault("budget_observations", {})[data["agent"]] = seq
            previous = life["budgets"].get(data["agent"], {})
            # A second concurrent failure cannot shorten an existing quota wait.
            if data["until"] >= previous.get("until", 0):
                life["budgets"][data["agent"]] = {**data, "at": at, "sequence": seq}
        elif kind == "help-resolved":
            fields(data, {"kind", "request", "reason"})
            request = life["requests"][data["request"]]
            string(data, "reason")
            require(request["status"] != "resolved", "request already resolved")
            request.update(status="resolved", resolution=data["reason"], resolved_at=at)
        else:
            raise ValueError("unknown life operation")
