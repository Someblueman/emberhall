"""A read-only task queue page, separate from the full historical briefing."""
from __future__ import annotations

import time


def task_page(state: dict, head: str, *, limit: int, offset: int) -> dict:
    if not 1 <= limit <= 50 or offset < 0:
        raise ValueError("task page limit must be 1..50 and offset must be nonnegative")
    at = time.time()
    tasks = state["tasks"]
    names = sorted(name for name, task in tasks.items()
                   if task["status"] == "claimed" or
                   (task["status"] == "open" and task.get("ready", False)))
    fields = ("title", "plain", "description", "status", "generation", "owner", "until",
              "ready", "project", "ballot_choice", "helper", "review_run")
    page = {}
    for name in names[offset:offset + limit]:
        task = tasks[name]
        page[name] = {key: task[key] for key in fields if key in task}
        page[name]["available"] = task["status"] == "open" or task["until"] <= at
    following = offset + len(page)
    more = following < len(names)
    return {
        "house_id": state["house_id"],
        "name": state["name"],
        "source": {"journal_head": head, "sequence": state["sequence"], "as_of": at},
        "scope": "Queued open and claimed tasks, sorted by task ID; not all house work.",
        "tasks": page,
        "page": {"offset": offset, "limit": limit, "total": len(names), "shown": len(page),
                 "has_more": more, "next_offset": following if more else None},
        "omitted": {
            "done": sum(task["status"] == "done" for task in tasks.values()),
            "unqueued_open": sum(task["status"] == "open" and not task.get("ready", False)
                                 for task in tasks.values()),
        },
        "limitations": [
            "Read-only projection: does not acknowledge events, reserve work or change a claim.",
            "If journal_head changes between pages, restart at offset 0; offsets are not saved cursors.",
            "Available describes the lease at as_of, not a stopped process or permission to edit; "
            "inspect ownership and claim the current generation before working.",
            "Completed and unqueued open tasks are counted but omitted; projects, votes, help "
            "and other house work remain in full status and the verified record.",
        ],
    }
