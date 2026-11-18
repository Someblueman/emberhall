"""Bounded dated Ten-Second Door summary built strictly from public record data."""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

from .body import label

TWELVE_HOURS = 12 * 3600
RECENT_RUN_WINDOW = 3600
CHANGES_LIMIT = 50
LATELY_LIMIT = 12
LATELY_SCAN = 600
SUMMARY_BYTES = 64 * 1024
TASKS_LIMIT = 16
ROOMS_LIMIT = 16
RESIDENTS_LIMIT = 8
RUNS_LIMIT = 25
HEARTH_LIMIT = 6
CREATIONS_LIMIT = 6
QUIET_OPS = frozenset({"life", "renew", "owner-admissions", "owner-migrate", "council-sync"})


class _FrameReader:
    """Uniform read-only accessor over plain exported frames or version-4 marshal cache."""

    def __init__(self, frames: list[dict], nodes: list | None = None):
        self._frames = frames
        self._nodes = nodes
        self._memo: dict[int, Any] = {}

    def length(self) -> int:
        return len(self._frames)

    def _raw(self, index: int) -> dict:
        entry = self._frames[index]
        return entry if self._nodes is None else self._nodes[entry["ref"]]

    def _resolve(self, value: Any) -> Any:
        if self._nodes is None:
            return value
        if isinstance(value, dict) and set(value) == {"ref"}:
            idx = value["ref"]
            if idx in self._memo:
                return self._memo[idx]
            node = self._nodes[idx]
            if isinstance(node, list) and len(node) == 1 and isinstance(node[0], list):
                out = []
                for part_ref in node[0]:
                    out.extend(self._resolve({"ref": part_ref}))
            elif isinstance(node, list):
                out = [self._resolve(item) for item in node]
            elif isinstance(node, dict):
                out = {k: self._resolve(v) for k, v in node.items()}
            else:
                out = node
            self._memo[idx] = out
            return out
        return value

    def at(self, index: int) -> float:
        return self._raw(index)["at"]

    def seq(self, index: int) -> int:
        return self._raw(index)["seq"]

    def rooms_ref(self, index: int) -> Any:
        return self._raw(index).get("rooms")

    def rooms(self, index: int) -> list[dict]:
        return self._resolve(self.rooms_ref(index)) or []

    def projects_ref(self, index: int) -> Any:
        shelf = self._resolve_shallow_shelf(index)
        return shelf.get("projects") if isinstance(shelf, dict) else None

    def _resolve_shallow_shelf(self, index: int) -> dict | None:
        shelf_ref = self._raw(index).get("shelf")
        if shelf_ref is None:
            return None
        if self._nodes is None:
            return shelf_ref
        return self._nodes[shelf_ref["ref"]]

    def projects(self, index: int) -> list[dict]:
        return self._resolve(self.projects_ref(index)) or []

    def event(self, index: int) -> dict:
        return self._resolve(self._raw(index).get("event")) or {}

    def tasks(self, index: int) -> list[dict]:
        return self._resolve(self._raw(index).get("tasks")) or []

    def field(self, index: int, key: str, default: Any = None) -> Any:
        raw = self._raw(index)
        if key not in raw:
            return default
        return self._resolve(raw[key])


def _project_progress_changes(previous: dict | None, project: dict, sequence: int, at: float) -> list[dict]:
    title = project.get("title") or project["id"]
    stages = project.get("milestones")
    completed = project.get("completed") if isinstance(project.get("completed"), list) else []
    earlier = previous.get("completed") if previous and isinstance(previous.get("completed"), list) else []
    receipts = [
        entry for entry in completed
        if entry.get("sequence") == sequence
        and isinstance(entry.get("stage"), int) and not isinstance(entry.get("stage"), bool)
        and isinstance(stages, list) and 0 <= entry["stage"] < len(stages)
        and not any(old.get("stage") == entry["stage"] and old.get("sequence") == entry["sequence"]
                    for old in earlier)
    ]
    if receipts:
        verb_prefix = "Final stage" if project.get("status") == "done" else "Stage"
        return [{
            "kind": "project",
            "id": project["id"],
            "title": title,
            "status": project.get("status"),
            "seq": sequence,
            "at": at,
            "verb": f"{verb_prefix} {entry['stage'] + 1} of {len(stages)} completed",
            "milestone": entry.get("milestone") or stages[entry["stage"]]["milestone"],
        } for entry in receipts]
    if previous and previous.get("status") == project.get("status"):
        return []
    verb = {"active": "Project started", "done": "Milestone completed", "dropped": "Project dropped"}.get(
        project.get("status")
    )
    if not verb:
        return []
    return [{
        "kind": "project",
        "id": project["id"],
        "title": title,
        "status": project.get("status"),
        "seq": sequence,
        "at": at,
        "verb": verb,
    }]


def twelve_hour_changes(reader: _FrameReader, observed_at: float) -> dict:
    """Compute room and project changes over the previous twelve elapsed hours at observed_at."""
    since = observed_at - TWELVE_HOURS
    changes: list[dict] = []
    for i in range(1, reader.length()):
        at = reader.at(i)
        if at < since or at > observed_at:
            continue
        seq = reader.seq(i)
        if reader.rooms_ref(i) != reader.rooms_ref(i - 1):
            prev_rooms = {room["id"]: room for room in reader.rooms(i - 1)}
            for room in reader.rooms(i):
                old = prev_rooms.get(room["id"])
                status = room.get("status") or "open"
                if old and (old.get("status") or "open") == status:
                    continue
                if not old and not room.get("planned_at") and not room.get("opened_at") and status != "construction":
                    continue
                verb = {"construction": "Building began", "open": "Room opened", "closed": "Room closed"}.get(status)
                if verb:
                    changes.append({
                        "kind": "room",
                        "id": room["id"],
                        "title": room["name"],
                        "verb": verb,
                        "seq": seq,
                        "at": at,
                    })
        if reader.projects_ref(i) != reader.projects_ref(i - 1):
            prev_projects = {project["id"]: project for project in reader.projects(i - 1)}
            for project in reader.projects(i):
                changes.extend(_project_progress_changes(prev_projects.get(project["id"]), project, seq, at))
    changes.reverse()
    return {
        "window_seconds": TWELVE_HOURS,
        "since": since,
        "until": observed_at,
        "count": len(changes),
        "items": changes[:CHANGES_LIMIT],
    }


def _task_title_at(reader: _FrameReader, index: int, task_id: str, latest_tasks: list[dict]) -> str:
    if not task_id:
        return ""
    candidates = [reader.tasks(index)]
    if index > 0:
        candidates.append(reader.tasks(index - 1))
    candidates.append(latest_tasks)
    for task_list in candidates:
        for task in task_list:
            if task.get("id") == task_id:
                return task.get("plain") or task.get("title") or task_id
    return task_id.replace("-", " ")


def _lately_events(reader: _FrameReader, resident_names: dict[str, str], latest_tasks: list[dict]) -> list[dict]:
    total = reader.length()
    stop = max(-1, total - 1 - LATELY_SCAN)
    found: list[dict] = []
    for i in range(total - 1, stop, -1):
        if len(found) >= LATELY_LIMIT:
            break
        event = reader.event(i)
        op = event.get("op", "")
        actor = event.get("actor", "")
        if not op or op in QUIET_OPS or actor == "watch-keeper":
            continue
        if found and found[-1]["actor"] == actor and found[-1]["op"] == op and op == "say":
            found[-1]["times"] += 1
            continue
        raw_title = event.get("title", "")
        title = _task_title_at(reader, i, raw_title, latest_tasks) if op in {"claim", "finish", "release"} else raw_title
        found.append({
            "seq": reader.seq(i),
            "at": reader.at(i),
            "op": op,
            "actor": actor,
            "actor_name": resident_names.get(actor, actor),
            "title": label(title, 140),
            "times": 1,
        })
    return found


def _compact_room(room: dict) -> dict:
    return {
        "id": room["id"],
        "name": room["name"],
        "status": room.get("status") or "open",
        "floor": room.get("floor") or 0,
        **({"purpose": label(room["purpose"], 240)} if room.get("purpose") else {}),
        **({"last_used_at": room["last_used_at"]} if room.get("last_used_at") is not None else {}),
        **({"last_used_by": room["last_used_by"]} if room.get("last_used_by") is not None else {}),
        **({"planned_at": room["planned_at"]} if room.get("planned_at") is not None else {}),
        **({"opened_at": room["opened_at"]} if room.get("opened_at") is not None else {}),
        **({"closed_at": room["closed_at"]} if room.get("closed_at") is not None else {}),
    }


def _compact_resident(resident: dict) -> dict:
    return {
        "id": resident["id"],
        "name": resident["name"],
        "agent": resident.get("agent", "unrecorded"),
        "model": resident.get("model", ""),
        "room": resident.get("room", "door"),
        "pose": resident.get("pose", "standing"),
        "presence": resident.get("presence", "recorded awake"),
        "tasks": list(resident.get("tasks", ())[:4]),
    }


def _compact_project(project: dict, resident_names: dict[str, str]) -> dict:
    item = {
        "id": project["id"],
        "title": label(project.get("title") or project["id"], 180),
        "status": project.get("status", "active"),
        "owner": project.get("owner", ""),
        "owner_name": resident_names.get(project.get("owner", ""), project.get("owner", "")),
        **({"idea": project["idea"]} if project.get("idea") else {}),
        **({"plain": label(project["plain"], 200)} if project.get("plain") else {}),
        **({"slot": project["slot"]} if project.get("slot") else {}),
        **({"deadline": project["deadline"]} if project.get("deadline") is not None else {}),
    }
    milestones = project.get("milestones")
    if isinstance(milestones, list) and milestones:
        stage = project.get("stage")
        if not isinstance(stage, int) or isinstance(stage, bool):
            stage = len(project.get("completed") or ())
        item["stage"] = stage
        item["stages"] = len(milestones)
        if 0 <= stage < len(milestones):
            item["milestone"] = label(milestones[stage].get("milestone", ""), 400)
    elif project.get("milestone"):
        item["milestone"] = label(project["milestone"], 400)
    return item


def _room_destination(room: dict) -> dict:
    return {
        "kind": "room",
        "room_id": room["id"],
        "label": f"Enter {room['name']}",
        "href": "#room/" + quote(room["id"], safe=""),
    }


def _featured_creation(catalog_entries: list[dict], projects: list[dict]) -> tuple[dict | None, list[dict]]:
    playable = []
    for entry in catalog_entries:
        if entry.get("category") != "creation" or entry.get("action") == "Read guide":
            continue
        # An optional catalogue link must stay whole. Its full entry remains in the Gallery.
        if len(entry["id"]) > 100 or len(entry["href"]) > 512:
            continue
        preview = next((f for f in entry.get("files", ()) if isinstance(f, str)
                        and len(f) <= 512 and f.endswith("/gallery-preview.svg")), None)
        item = {
            "id": entry["id"],
            "title": label(entry["title"], 180),
            "summary": label(entry["summary"], 240),
            "action": entry["action"],
            "href": entry["href"],
            **({"preview": preview} if preview else {}),
        }
        playable.append(item)
    if not playable:
        return None, []
    by_id = {entry["id"]: entry for entry in playable}
    done_order = [p["idea"] for p in reversed(projects) if p.get("status") == "done" and p.get("idea") in by_id]
    ordered = [by_id[idea_id] for idea_id in dict.fromkeys(done_order)]
    seen = set(done_order)
    ordered.extend(entry for entry in reversed(playable) if entry["id"] not in seen)
    return ordered[0], ordered[:CREATIONS_LIMIT]


def _build_scene(
    residents: list[dict],
    rooms: list[dict],
    tasks: list[dict],
    active_projects: list[dict],
    all_projects_by_id: dict[str, dict],
    runs: list[dict],
    hearth: list[dict],
    latest_event: dict,
    featured_creation: dict | None,
    observed_at: float,
) -> dict:
    rooms_by_id = {room["id"]: room for room in rooms}
    fallback_room = rooms_by_id.get("door") or (rooms[0] if rooms else {"id": "door", "name": "The door", "status": "open", "floor": 0})
    latest_run_by_resident: dict[str, int] = {}
    for run in runs:
        resident_id = run.get("resident")
        if resident_id:
            latest_run_by_resident[resident_id] = max(
                latest_run_by_resident.get(resident_id, 0),
                int(run.get("sequence") or 0),
            )
    projects_by_id = {project["id"]: project for project in active_projects}
    awake = [r for r in residents if r.get("pose") not in ("sleeping", "unconfirmed")]
    unexpired_by_owner: dict[str, list[dict]] = {}
    for task in tasks:
        if task.get("status") == "claimed" and (task.get("until") or 0) > observed_at and task.get("owner"):
            unexpired_by_owner.setdefault(task["owner"], []).append(task)

    working: list[tuple[tuple[int, int, str], dict, dict]] = []
    for resident in awake:
        held = unexpired_by_owner.get(resident["id"], [])
        if not held:
            continue
        held.sort(key=lambda t: (t.get("project") in projects_by_id, t["id"]), reverse=True)
        task = held[0]
        score = (
            1 if task.get("project") in projects_by_id else 0,
            latest_run_by_resident.get(resident["id"], 0),
            resident["id"],
        )
        working.append((score, resident, task))

    if working:
        working.sort(key=lambda item: item[0], reverse=True)
        _, resident, task = working[0]
        room = rooms_by_id.get(resident.get("room", "")) or rooms_by_id.get("workshop") or fallback_room
        project = all_projects_by_id.get(task.get("project"))
        return {
            "status": "occupied",
            "activity": "working",
            "resident": resident,
            "room": room,
            "work": {
                "kind": "task",
                "id": task["id"],
                "title": task["title"],
                **({"plain": task["plain"]} if task.get("plain") else {}),
                "detail": task.get("plain") or task["title"],
                "until": task["until"],
                "project": project,
            },
            "waiting_project": None,
            "destination": _room_destination(room),
            "creation": featured_creation,
        }

    if awake:
        awake_sorted = sorted(
            awake,
            key=lambda r: (latest_run_by_resident.get(r["id"], 0), r["id"]),
            reverse=True,
        )
        resident = awake_sorted[0]
        room = rooms_by_id.get(resident.get("room", "")) or fallback_room
        detail = ""
        if room["id"] == "hearth":
            for voice in reversed(hearth):
                if voice.get("resident") == resident["id"]:
                    detail = voice.get("text", "")
                    break
        if not detail and latest_event.get("actor") == resident["id"] and latest_event.get("title"):
            detail = latest_event["title"]
        if not detail:
            detail = room.get("purpose") or f"{resident['name']} is in {room['name']}"
        return {
            "status": "occupied",
            "activity": "present",
            "resident": resident,
            "room": room,
            "work": {
                "kind": "presence",
                "detail": label(detail, 240),
                "project": active_projects[0] if active_projects else None,
            },
            "waiting_project": None,
            "destination": _room_destination(room),
            "creation": featured_creation,
        }

    open_rooms = [room for room in rooms if room.get("status") == "open"]
    waiting_project = active_projects[0] if active_projects else None
    if waiting_project and rooms_by_id.get("workshop", {}).get("status") == "open":
        quiet_room = rooms_by_id["workshop"]
    elif open_rooms:
        quiet_room = max(open_rooms, key=lambda r: (r.get("last_used_at") or 0, r["id"] == "door"))
    else:
        quiet_room = fallback_room
    return {
        "status": "quiet",
        "activity": "quiet",
        "resident": None,
        "room": quiet_room,
        "work": None,
        "waiting_project": waiting_project,
        "destination": _room_destination(quiet_room),
        "creation": featured_creation,
    }


def build_now(
    *,
    final: dict,
    head: str,
    source_head: str | None,
    observed_at: float,
    commits: list[dict],
    frames: list[dict],
    nodes: list | None = None,
    catalog: dict | None = None,
) -> dict:
    """Build the bounded now.json summary from verified frames and optional committed catalog."""
    reader = _FrameReader(frames, nodes)
    total = reader.length()
    if total == 0:
        raise ValueError("No journal frames to summarize")
    last = total - 1
    latest_seq = reader.seq(last)
    latest_at = reader.at(last)
    latest_event = reader.event(last)
    raw_rooms = reader.rooms(last)
    rooms = [_compact_room(room) for room in raw_rooms]
    raw_residents = reader.field(last, "residents", []) or []
    residents = [_compact_resident(resident) for resident in raw_residents]
    resident_names = {r["id"]: r["name"] for r in residents}
    raw_tasks = reader.field(last, "tasks", []) or []
    floors = reader.field(last, "floors", []) or []
    hearth = list((reader.field(last, "hearth", []) or [])[-HEARTH_LIMIT:])
    raw_runs = reader.field(last, "runs", []) or []
    recent_runs = [
        run for run in raw_runs
        if run.get("end") is None or run["end"] > observed_at or run["end"] >= observed_at - RECENT_RUN_WINDOW
    ][-RUNS_LIMIT:]
    shelf_node = reader._resolve_shallow_shelf(last)
    raw_projects = reader.projects(last) if isinstance(shelf_node, dict) else []
    slot_rank = {"house": 0, "great": 1, "small": 2}
    active_projects = sorted(
        [_compact_project(p, resident_names) for p in raw_projects if p.get("status") == "active"],
        key=lambda p: (slot_rank.get(p.get("slot"), 3), p["id"]),
    )
    raw_needs = reader._resolve(shelf_node.get("needs")) if isinstance(shelf_node, dict) and "needs" in shelf_node else []
    open_needs = [
        {"id": need["id"], "for_title": need.get("for_title", need.get("for", "")),
         "plain": need.get("plain", ""), "status": need.get("status", "open")}
        for need in (raw_needs or []) if need.get("status") == "open"
    ]
    voting_ref = reader._raw(last).get("voting")
    voting = reader._resolve(voting_ref) if voting_ref is not None else {}
    raw_choices = voting.get("choices", []) if isinstance(voting, dict) else []
    open_choices = [
        {
            "id": choice["id"],
            **({"slot": choice["slot"]} if choice.get("slot") else {}),
            "counted": sum(1 for v in choice.get("votes", ()) if v.get("counted") is True),
            "needed": 3,
            "candidates": [{"id": c["id"], "title": c["title"]} for c in choice.get("candidates", ())],
        }
        for choice in raw_choices if choice.get("status") == "open"
    ]
    catalog_entries = catalog.get("projects", []) if isinstance(catalog, dict) else []
    featured_creation, creations = _featured_creation(catalog_entries, raw_projects)
    all_projects_by_id = {p["id"]: _compact_project(p, resident_names) for p in raw_projects}
    scene = _build_scene(
        residents=residents,
        rooms=rooms,
        tasks=raw_tasks,
        active_projects=active_projects,
        all_projects_by_id=all_projects_by_id,
        runs=raw_runs,
        hearth=hearth,
        latest_event=latest_event,
        featured_creation=featured_creation,
        observed_at=observed_at,
    )
    active_threads = sum(
        1 for task in raw_tasks
        if (task.get("status") == "claimed" and (task.get("until") or 0) > observed_at)
        or task.get("ready") is True
    )
    counts = {
        "awake": sum(1 for r in residents if r["pose"] not in ("sleeping", "unconfirmed")),
        "asleep": sum(1 for r in residents if r["pose"] == "sleeping"),
        "unconfirmed": sum(1 for r in residents if r["pose"] == "unconfirmed"),
        "total_residents": len(residents),
        "rooms": len(rooms),
        "open_rooms": sum(1 for r in rooms if r["status"] == "open"),
        "active_threads": active_threads,
        "idle_threads": len(raw_tasks) - active_threads,
        "active_projects": len(active_projects),
        "open_choices": len(open_choices),
        "open_needs": len(open_needs),
    }
    changes = twelve_hour_changes(reader, observed_at)
    change_items = changes.pop("items")
    for item in change_items:
        item["title"] = label(item["title"], 180)
        if "milestone" in item:
            item["milestone"] = label(item["milestone"], 400)
    payload = {
        "version": 1,
        "name": label(final["name"], 80),
        "house_id": final["house_id"],
        "journal_head": head,
        "source_head": source_head,
        "observed_at": observed_at,
        "timezone": "Europe/London",
        "seq": latest_seq,
        "at": latest_at,
        "total_frames": total,
        "event": latest_event,
        "limits": "Dated scene with a limited preview. Counts cover the full record. All entries are in the archive.",
        "scene": scene,
        "counts": counts,
        "changes": changes,
    }

    # Reserve the featured records even when the lists or twelve-hour window are crowded.
    room = scene["room"]
    resident = scene["resident"]
    work_id = (scene["work"] or {}).get("id")
    task = next((t for t in raw_tasks if t["id"] == work_id), None)
    if task and work_id not in resident["tasks"]:
        resident["tasks"] = [work_id, *resident["tasks"][:3]]
    previews = {
        "rooms": [r for r in rooms[:ROOMS_LIMIT - 1] if r["id"] != room["id"]],
        "residents": [r for r in residents[:RESIDENTS_LIMIT - 1] if not resident or r["id"] != resident["id"]],
        "tasks": [t for t in raw_tasks[:TASKS_LIMIT - 1] if t["id"] != work_id],
        "lately": _lately_events(reader, resident_names, raw_tasks),
        "projects": active_projects,
        "open_choices": open_choices,
        "open_needs": open_needs,
        "hearth": hearth,
        "recent_runs": recent_runs,
        "floors": floors,
        "commits": list(commits[-3:]),
        "creations": creations,
    }
    payload.update({key: [] for key in previews})
    payload["rooms"] = [room]
    payload["residents"] = [resident] if resident else []
    payload["tasks"] = [task] if task else []
    changes["items"] = []
    # Count actual JSON bytes, including the newline and commas. Large optional rows
    # (such as a run with many completed tasks) stay in the archive intact.
    remaining = SUMMARY_BYTES - len(_json_bytes(payload)) - 1
    if remaining < 0:
        raise ValueError("Door scene exceeds its publication budget")
    sections = [(changes["items"], change_items)]
    sections.extend((payload[key], rows) for key, rows in previews.items())
    for target, rows in sections:
        for row in rows:
            size = len(_json_bytes(row)) + bool(target)
            if size > remaining:
                break
            target.append(row)
            remaining -= size
    return payload


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def now_bytes(
    *,
    final: dict,
    head: str,
    source_head: str | None,
    observed_at: float,
    commits: list[dict],
    frames: list[dict],
    nodes: list | None = None,
    catalog_raw: bytes | None = None,
) -> bytes:
    """Serialize bounded now.json bytes from public replay state and optional projects.json bytes."""
    catalog = json.loads(catalog_raw) if catalog_raw else None
    payload = build_now(
        final=final,
        head=head,
        source_head=source_head,
        observed_at=observed_at,
        commits=commits,
        frames=frames,
        nodes=nodes,
        catalog=catalog,
    )
    return _json_bytes(payload) + b"\n"
