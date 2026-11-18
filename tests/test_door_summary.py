"""Bounded Ten-Second Door summary publication from the real public record."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from house import body, council, door_summary, maintenance, publish as publisher, shelf, shelf_gate
from house.governance import digest
from house.home_work import git
from house.public_history import decode
from house.publish import BRANCH, publish
from tests import test_runtime
from tests.support import HouseCase
from tests.test_shelf import idea


HOUR = 3600
SOURCE = Path(__file__).resolve().parents[1]


def reference_twelve_hour_changes(exported: dict, end_at: float) -> list[dict]:
    """Reference 12-hour room/project growth matching site/house.js recentGrowth()."""
    frames = exported["frames"]
    since = end_at - 12 * HOUR
    changes: list[dict] = []
    for i in range(1, len(frames)):
        nxt, prev = frames[i], frames[i - 1]
        if nxt["at"] < since or nxt["at"] > end_at:
            continue
        prev_rooms = {room["id"]: room for room in prev.get("rooms", [])}
        for room in nxt.get("rooms", []):
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
                    "seq": nxt["seq"],
                    "at": nxt["at"],
                })
        prev_projects = {project["id"]: project for project in prev.get("shelf", {}).get("projects", [])}
        for project in nxt.get("shelf", {}).get("projects", []):
            changes.extend(_reference_project_changes(prev_projects.get(project["id"]), project, nxt["seq"], nxt["at"]))
    changes.reverse()
    return changes


def _reference_project_changes(previous: dict | None, project: dict, sequence: int, at: float) -> list[dict]:
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
            "status": project["status"],
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
        "status": project["status"],
        "seq": sequence,
        "at": at,
        "verb": verb,
    }]


class DoorSummaryTests(unittest.TestCase):
    def setUp(self):
        self.clock = 1_795_000_000.0
        self.time_patch = patch("house.record.time.time", side_effect=lambda: self._tick())
        self.time_patch.start()
        self.addCleanup(self.time_patch.stop)
        fixture = test_runtime.RuntimeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.repo = fixture.repo
        self.record = fixture.record
        (self.repo / "site").mkdir()
        (self.repo / "site/index.html").write_text("<!doctype html><html><body>door</body></html>")
        (self.repo / "site/house.css").write_text("body{}")
        (self.repo / "site/house.js").write_text('fetch("now.json");')
        self.creation_files = [
            "projects/lantern-loop/index.html",
            "projects/lantern-loop/gallery-preview.svg",
        ]
        for rel in self.creation_files:
            target = self.repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"fixture {rel}")
        self.manifest = {
            "version": 1,
            "projects": [{
                "id": "lantern-loop",
                "title": "Lantern Loop",
                "summary": "A six-second silent moth film.",
                "category": "creation",
                "action": "Play",
                "href": "projects/lantern-loop/index.html",
                "files": self.creation_files,
            }],
        }
        (self.repo / "site/projects.json").write_text(json.dumps(self.manifest))
        self.commit("Public fixture")
        self._enable_growth_and_shelf()

    def _tick(self) -> float:
        self.clock += 1.0
        return self.clock

    def commit(self, message: str = "Update"):
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", message)

    def _enable_growth_and_shelf(self):
        state = self.record.read()[0]
        old = maintenance.protected_manifest(state)
        manifest = old | {name: "a" * 64 for name in maintenance.OWNER_MODULES | {"house/building.py"}}
        self.record.append("owner-migrate", "alice", {
            "scope": maintenance.GROWTH_SCOPE, "approval_sha256": maintenance.GROWTH_SHA256,
            "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64, "protected_files": manifest,
            "previous_manifest_sha256": maintenance.fingerprint(old),
            "previous_runtime_sha256": "c" * 64, "runtime_sha256": "d" * 64,
            "test_output_sha256": "e" * 64, "test_count": 1})
        manifest2 = manifest | {name: "a" * 64 for name in (
            "house/shelf.py", "house/shelf_gate.py", "house/windows.py", "house/home_control.py")}
        self.record.append("owner-migrate", "alice", {
            "scope": maintenance.KEEP_MOVING_SCOPE, "approval_sha256": maintenance.KEEP_MOVING_SHA256,
            "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64, "protected_files": manifest2,
            "previous_manifest_sha256": maintenance.fingerprint(manifest),
            "previous_runtime_sha256": "d" * 64, "runtime_sha256": "e" * 64,
            "test_output_sha256": "f" * 64, "test_count": 1})
        manifest3 = manifest2 | {"house/project_work.py": "a" * 64}
        manifest3 = manifest2 | {"house/project_work.py": "a" * 64}
        self.record.append("owner-migrate", "alice", {
            "scope": maintenance.PROJECT_WORK_SCOPE,
            "approval_sha256": maintenance.SOURCES[maintenance.PROJECT_WORK_SCOPE],
            "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64, "protected_files": manifest3,
            "previous_manifest_sha256": maintenance.fingerprint(manifest2),
            "previous_runtime_sha256": "e" * 64, "runtime_sha256": "f" * 64,
            "test_output_sha256": "1" * 64, "test_count": 1})
        manifest4 = manifest3 | {"house/home.py": "a" * 64, "house/life.py": "a" * 64}
        self.record.append("owner-migrate", "alice", {
            "scope": maintenance.BACKLOG_SCOPE, "approval_sha256": maintenance.BACKLOG_SHA256,
            "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64, "protected_files": manifest4,
            "previous_manifest_sha256": maintenance.fingerprint(manifest3),
            "previous_runtime_sha256": "f" * 64, "runtime_sha256": "2" * 64,
            "test_output_sha256": "3" * 64, "test_count": 1})
        for actor, name, agent, model in (
            ("alice", "Alice", "agy", "gemini-4-hydrogen-high"),
            ("bob", "Bob", "codex", "gpt-6.1-sol"),
            ("carol", "Carol", "muse", "muse-wonder-full-1.0"),
            ("dave", "Dave", "opencode", "opencode-go/kimi-k3.1-pro"),
        ):
            if actor not in state["residents"]:
                self.record.append("arrive", actor, {"name": name})
            self.record.append("life", actor, {"kind": "identity", "agent": agent, "model": model})
        self.record.append("council-propose", "alice", {
            "proposal": "door-selection-policy", "mode": "rule", "title": "Fixture selection",
            "text": shelf_gate.REVISED_POLICY_TEXT, "reason": "Enable choice-open for fixture",
            "base": self.record.read()[0]["rule_revision"]})
        self.record.append("task", "alice", {
            "task": "policy-trial", "title": "Trial", "description": "Synthetic trial"})
        self.record.append("claim", "alice", {
            "task": "policy-trial", "expect": 0, "token": "pt", "seconds": 60})
        self.record.append("finish", "alice", {
            "task": "policy-trial", "token": "pt", "result": "Trial ok",
            "artifacts": {"trial.txt": {
                "sha256": digest("trial"), "base64": base64.b64encode(b"trial").decode()}}})
        self.record.append("council-trial", "alice", {
            "proposal": "door-selection-policy", "task": "policy-trial", "evidence": "Synthetic"})
        for actor in ("bob", "carol"):
            self.record.append("council-endorse", actor, {
                "proposal": "door-selection-policy", "evidence": "Synthetic"})
        self.record.append("council-notice", "alice", {
            "proposal": "door-selection-policy", "repository": council.REPOSITORY,
            "issue": council.ISSUE, "comment_id": 123, "text_sha256": shelf_gate.REVISED_POLICY_SHA256})
        self.clock += council.WAIT_SECONDS + 10
        self.record.append("council-sync", "alice", {
            "repository": council.REPOSITORY, "issue": council.ISSUE,
            "owner_id": council.OWNER_ID, "checked_at": self.clock, "comments": []})
        self.record.append("council-enact", "alice", {"proposal": "door-selection-policy"})

    def _start_project(self, choice_id: str, idea_keys: tuple[str, ...], winner: str, explorer: str = "alice"):
        expect = self.record.read()[0].get("shelf", {}).get("generation", 0)
        self.record.append("shelf", explorer, {
            "kind": "explore-start", "round": choice_id, "expect": expect,
            "token": choice_id, "seconds": 3600})
        self.record.append("shelf", explorer, {
            "kind": "explore-publish", "round": choice_id, "token": choice_id,
            "ideas": [idea(k) for k in idea_keys]})
        opener = "bob" if explorer != "bob" else "alice"
        candidates = shelf.shelf_ids(self.record.read()[0]["shelf"])
        self.record.append("shelf", opener, {
            "kind": "choice-open", "choice": choice_id,
            "milestones": {k: {"milestone": f"Ship {k}", "seconds": 86400} for k in candidates}})
        for voter in ("bob", "carol", "dave"):
            if voter == explorer:
                voter = "alice"
            self.record.append("shelf", voter, {
                "kind": "choice-vote", "choice": choice_id, "idea": winner,
                "reason": f"Build {winner} now."})

    def _publish_at(self, observed_at: float) -> dict:
        with patch("house.body.time.time", return_value=observed_at):
            result = publish(self.record)
        self.assertIn("now.json", git(self.repo, "ls-tree", "-r", "--name-only", BRANCH).splitlines())
        return result

    def _published_now(self) -> dict:
        return json.loads(self.record.git("show", BRANCH + ":now.json"))

    def test_occupied_scene_privacy_and_opt_in_boundaries(self):
        self._start_project("door-choice", ("ten-second-door", "other-idea"), "ten-second-door")
        # Private lesson evidence and private task artifact must never appear in now.json.
        self.record.append("learn", "bob", {
            "lesson": "private-check", "key": "private-check", "claim": "Public lesson claim only",
            "evidence": "TOP_SECRET_EVIDENCE_PAYLOAD /Users/private/secret.txt"})
        secret_bytes = b"TOP_SECRET_ARTIFACT_BYTES"
        self.record.append("task", "bob", {
            "task": "old-task", "title": "Old task", "description": "Done work"})
        self.record.append("claim", "bob", {
            "task": "old-task", "expect": 0, "token": "tok-old", "seconds": 60})
        self.record.append("finish", "bob", {
            "task": "old-task", "token": "tok-old", "result": "Done",
            "artifacts": {"secret.txt": {
                "sha256": hashlib.sha256(secret_bytes).hexdigest(),
                "base64": base64.b64encode(secret_bytes).decode()}}})
        self.record.append("sleep", "bob", {"through": self.record.read()[0]["sequence"], "note": "Sleep"})
        # Expired claim on carol must not be treated as active work.
        self.record.append("task", "carol", {
            "task": "expired-task", "title": "Expired bench task", "description": "Timed out"})
        self.record.append("claim", "carol", {
            "task": "expired-task", "expect": 0, "token": "tok-exp", "seconds": 10})
        self.clock += 50.0
        # Alice holds an unexpired claim on the active project.
        self.record.append("task", "alice", {
            "task": "door-scene", "title": "The front door shows who is building right away.",
            "description": "Build now.json", "project": "door-choice", "ready": True})
        self.record.append("claim", "alice", {
            "task": "door-scene", "expect": 0, "token": "tok-alice", "seconds": 3600})
        # Untracked/dirty site/now.json must be ignored in favour of journal generation.
        (self.repo / "site/now.json").write_text('{"forged": true}')

        observed_at = self.clock + 10.0
        self._publish_at(observed_at)
        now = self._published_now()
        raw_now = self.record.git("show", BRANCH + ":now.json").decode()

        self.assertEqual(now["version"], 1)
        self.assertEqual(now["observed_at"], observed_at)
        self.assertEqual(now["journal_head"], self.record.read()[2])
        self.assertNotIn("forged", now)
        self.assertNotIn("TOP_SECRET_EVIDENCE_PAYLOAD", raw_now)
        self.assertNotIn("TOP_SECRET_ARTIFACT_BYTES", raw_now)
        self.assertNotIn(base64.b64encode(secret_bytes).decode(), raw_now)
        self.assertNotIn("archive", now)

        scene = now["scene"]
        self.assertEqual(scene["status"], "occupied")
        self.assertEqual(scene["activity"], "working")
        self.assertEqual(scene["resident"]["id"], "alice")
        self.assertEqual(scene["resident"]["name"], "Alice")
        self.assertEqual(scene["room"]["id"], "workshop")
        self.assertEqual(scene["work"]["kind"], "task")
        self.assertEqual(scene["work"]["id"], "door-scene")
        self.assertEqual(scene["work"]["detail"], "The front door shows who is building right away.")
        self.assertEqual(scene["work"]["project"]["id"], "door-choice")
        self.assertEqual(scene["destination"]["kind"], "room")
        self.assertEqual(scene["destination"]["room_id"], "workshop")
        self.assertEqual(scene["destination"]["href"], "#room/workshop")
        self.assertEqual(scene["creation"]["id"], "lantern-loop")
        self.assertEqual(scene["creation"]["href"], "projects/lantern-loop/index.html")
        self.assertTrue(any(r["id"] == scene["room"]["id"] for r in now["rooms"]))
        self.assertTrue(all("history" not in r for r in now["rooms"]))

        # Existing archive still publishes identically to full export.
        wire = json.loads(self.record.git("show", BRANCH + ":history.json"))
        decoded = decode(wire, lambda path: self.record.git("show", BRANCH + ":" + path))
        self.assertEqual(decoded, body.export(self.record, observed_at))

        # Symlink site/now.json is refused without corrupting the branch.
        previous = self.record.ref("refs/heads/" + BRANCH)
        (self.repo / "site/now.json").unlink()
        (self.repo / "site/now.json").symlink_to("index.html")
        self.commit("Bad now.json symlink")
        with self.assertRaisesRegex(ValueError, "not a regular blob: site/now.json"):
            publish(self.record)
        self.assertEqual(self.record.ref("refs/heads/" + BRANCH), previous)

    def test_quiet_scene_never_invents_awake_resident_or_active_work(self):
        self._start_project("quiet-choice", ("quiet-idea", "other-quiet"), "quiet-idea")
        # Claim a task, let it expire, and put everyone to sleep.
        self.record.append("task", "alice", {
            "task": "expired-work", "title": "Expired work", "description": "Timed out",
            "project": "quiet-choice"})
        self.record.append("claim", "alice", {
            "task": "expired-work", "expect": 0, "token": "tok-q", "seconds": 5})
        self.clock += 20.0
        for actor in ("alice", "bob", "carol", "dave"):
            self.record.append("sleep", actor, {"through": self.record.read()[0]["sequence"], "note": "Goodnight"})

        observed_at = self.clock + 5.0
        self._publish_at(observed_at)
        now = self._published_now()
        scene = now["scene"]
        self.assertEqual(scene["status"], "quiet")
        self.assertEqual(scene["activity"], "quiet")
        self.assertIsNone(scene["resident"])
        self.assertIsNone(scene["work"])
        self.assertEqual(now["counts"]["awake"], 0)
        self.assertTrue(any(r["id"] == scene["room"]["id"] for r in now["rooms"]))
        self.assertTrue(scene["destination"]["href"].startswith("#room/"))
        self.assertEqual(scene["waiting_project"]["id"], "quiet-choice")
        self.assertEqual(scene["creation"]["id"], "lantern-loop")

    def test_twelve_hour_changes_match_full_record_across_dense_interval_and_cache_resume(self):
        # T = 0h: older room + project change (will fall OUTSIDE 12h window later).
        self.record.append("task", "alice", {
            "task": "old-room-task", "title": "Build old room", "description": "Old"})
        self.record.append("claim", "alice", {
            "task": "old-room-task", "expect": 0, "token": "tok-r0", "seconds": 3600})
        self.record.append("life", "alice", {
            "kind": "room-plan", "room": "old-wing", "name": "Old Wing",
            "purpose": "Older than twelve hours", "reason": "Test cutoff",
            "floor": 0, "task": "old-room-task", "expect": 0})
        self._start_project("old-proj", ("old-a", "old-b"), "old-a")

        # T = +3h: inside 12h window when observed at T = +14h!
        self.clock += 3 * HOUR
        self.record.append("task", "bob", {
            "task": "new-room-task", "title": "Build new room", "description": "Recent"})
        self.record.append("claim", "bob", {
            "task": "new-room-task", "expect": 0, "token": "tok-r1", "seconds": 3600})
        self.record.append("life", "bob", {
            "kind": "room-plan", "room": "observatory", "name": "Observatory",
            "purpose": "Inside twelve hours", "reason": "Test cutoff",
            "floor": 0, "task": "new-room-task", "expect": 0})
        self.record.append("finish", "bob", {
            "task": "new-room-task", "token": "tok-r1", "result": "Finished observatory",
            "artifacts": {"room.txt": {
                "sha256": digest("room"), "base64": base64.b64encode(b"room").decode()}}})
        self.record.append("life", "bob", {
            "kind": "room-open", "room": "observatory", "expect": 1,
            "evidence": "Opened inside twelve-hour window"})
        self._start_project("recent-proj", ("recent-a", "recent-b"), "recent-a", explorer="bob")

        # Publish once midway to warm the incremental marshal cache.
        self._publish_at(self.clock + 10.0)

        # T = +13.5h: dense burst of 90 say events (> 48 frames) before publication at +14h.
        self.clock += 10.5 * HOUR
        for n in range(90):
            self.record.append("say", "carol" if n % 2 else "dave", {"text": f"Dense chatter {n}"})

        observed_at = self.clock + 60.0  # ~14h after T=0h; old-wing/old-proj are >12h old!
        self._publish_at(observed_at)
        now = self._published_now()
        exported = body.export(self.record, observed_at)
        expected_changes = reference_twelve_hour_changes(exported, observed_at)

        self.assertEqual(now["changes"]["items"], expected_changes)
        self.assertEqual(now["changes"]["count"], len(expected_changes))
        self.assertEqual(now["changes"]["since"], observed_at - 12 * HOUR)
        self.assertEqual(now["changes"]["until"], observed_at)
        titles = {(c["kind"], c["id"], c["verb"]) for c in now["changes"]["items"]}
        self.assertIn(("room", "observatory", "Building began"), titles)
        self.assertIn(("room", "observatory", "Room opened"), titles)
        self.assertIn(("project", "recent-proj", "Project started"), titles)
        self.assertNotIn(("room", "old-wing", "Building began"), titles)
        self.assertNotIn(("project", "old-proj", "Project started"), titles)
        self.assertGreater(len(now["lately"]), 0)
        self.assertLessEqual(len(now["lately"]), 12)

    def test_plain_task_present_scene_marker_trigger_and_chunked_export_parity(self):
        # Marker file site/now.json triggers publication even if house.js is minimal.
        (self.repo / "site/house.js").write_text("console.log('minimal');")
        (self.repo / "site/now.json").write_text('{"ignored": true}')
        self.commit("Use site/now.json marker")
        # Speak at hearth with bob, sleep everyone else -> awake-without-claim ("present").
        self.record.append("say", "bob", {"text": "At the hearth beside the warm kettle."})
        for actor in ("alice", "carol", "dave"):
            self.record.append("sleep", actor, {"through": self.record.read()[0]["sequence"], "note": "Sleep"})
        observed_at = self.clock + 5.0
        with patch("house.public_history.CHUNK", 4):
            self._publish_at(observed_at)
        now = self._published_now()
        self.assertNotIn("ignored", now)
        self.assertEqual(now["scene"]["status"], "occupied")
        self.assertEqual(now["scene"]["activity"], "present")
        self.assertEqual(now["scene"]["resident"]["id"], "bob")
        self.assertEqual(now["scene"]["room"]["id"], "hearth")
        self.assertEqual(now["scene"]["destination"]["href"], "#room/hearth")

        # Verify byte-exact parity between marshal-cache publish() and plain export() build_now.
        exported = body.export(self.record, observed_at)
        direct_bytes = door_summary.now_bytes(
            final=self.record.read()[0],
            head=exported["journal_head"],
            source_head=exported["source_head"],
            observed_at=exported["observed_at"],
            commits=exported["commits"],
            frames=exported["frames"],
            catalog_raw=json.dumps(self.manifest).encode(),
        )
        self.assertEqual(self.record.git("show", BRANCH + ":now.json"), direct_bytes)

        # Verify plain task detail + hyphen-preserving lately task title on plain frames.
        plain_frame = json.loads(json.dumps(exported["frames"][-1]))
        plain_frame["seq"] += 1
        plain_frame["at"] += 1.0
        plain_frame["event"] = {"op": "task", "actor": "bob", "title": "Ten-Second Door keeps hyphens"}
        plain_frame["tasks"] = [{
            "id": "t-plain", "title": "Technical title",
            "plain": "Visitors see a Ten-Second Door right away.",
            "owner": "bob", "status": "claimed", "until": observed_at + 1000, "generation": 1,
        }]
        for r in plain_frame["residents"]:
            if r["id"] == "bob":
                r["pose"] = "standing"
                r["room"] = "workshop"
                r["tasks"] = ["t-plain"]
        built = door_summary.build_now(
            final=self.record.read()[0],
            head=exported["journal_head"],
            source_head=exported["source_head"],
            observed_at=observed_at + 2.0,
            commits=exported["commits"],
            frames=[*exported["frames"], plain_frame],
            catalog=self.manifest,
        )
        self.assertEqual(built["scene"]["work"]["detail"], "Visitors see a Ten-Second Door right away.")
        self.assertEqual(built["lately"][0]["title"], "Ten-Second Door keeps hyphens")


class DoorSizeTests(unittest.TestCase):
    def test_large_house_keeps_featured_work_and_total_within_wire_budget(self):
        # Use the shipped history format. The only worker, room and claim all lie
        # beyond the preview limits. Multibyte prose competes for space with rows.
        archive = json.loads((SOURCE / "site/history.json").read_bytes())
        frame = dict(archive["frames"][0])
        at = frame["at"]
        rooms = [{"id": f"room-{i}", "name": f"Room {i}", "status": "open", "opened_at": at}
                 for i in range(160)]
        rooms[-1]["purpose"] = "🌒" * 2000
        residents = [{"id": f"guest-{i}", "name": f"Guest {i}", "pose": "sleeping", "room": "door"}
                     for i in range(5000)]
        residents[-1].update(pose="standing", room=rooms[-1]["id"], tasks=["held"] * 1000)
        tasks = [{"id": f"todo-{i}", "title": "Waiting", "status": "open"} for i in range(150)]
        tasks.append({"id": "last-claim", "title": "Repair the telescope", "owner": residents[-1]["id"],
                      "status": "claimed", "until": at + 120})
        projects = [{"id": f"p-{i}", "title": "🌕" * 2000, "status": "active",
                     "milestone": "🌘" * 20000} for i in range(40)]
        latest = dict(frame, seq=frame["seq"] + 1, rooms=rooms, residents=residents, tasks=tasks,
                      shelf={"projects": projects})
        raw = door_summary.now_bytes(final=archive, head=archive["journal_head"], source_head=None,
                                     observed_at=at, commits=[], frames=[frame, latest])
        result = json.loads(raw)
        self.assertLessEqual(len(raw), 64 * 1024)
        self.assertEqual(result["counts"]["total_residents"], 5000)
        self.assertEqual(result["counts"]["awake"], 1)
        self.assertEqual(result["scene"]["work"]["title"], "Repair the telescope")
        self.assertIn("last-claim", result["scene"]["resident"]["tasks"])
        self.assertIn(residents[-1]["id"], [r["id"] for r in result["residents"]])
        self.assertIn(rooms[-1]["id"], [r["id"] for r in result["rooms"]])
        self.assertIn("last-claim", [t["id"] for t in result["tasks"]])
        self.assertEqual(result["changes"]["count"], len(rooms) + len(projects))
        self.assertGreater(len(result["changes"]["items"]), 0)
        self.assertLess(len(result["changes"]["items"]), result["changes"]["count"])


if __name__ == "__main__":
    unittest.main()
