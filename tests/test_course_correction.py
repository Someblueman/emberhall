"""Steward course correction of 15 November: rotation, great work and renovation."""
import copy
import json
from pathlib import Path
import unittest

from house import course, council, maintenance, providers, renovation, shelf, shelf_gate
from house.governance import digest
from tests import test_selection_repair, test_shelf

ROOT = Path(__file__).parents[1]


def great_idea(key):
    return test_shelf.idea(key) | {"scale": "great"}


class RotationTests(unittest.TestCase):
    def state(self, runs):
        return {"life": {"runs": {str(i): {"agent": agent, "model": model, "started_sequence": i}
                                  for i, (agent, model) in enumerate(runs, 1)}}}

    def test_two_codex_runs_in_three_are_sol_and_one_is_astra(self):
        # Steward, 18 November, night: "2/3 running sol and the last one running Astra".
        sol, astra = "gpt-6.1-sol", "gpt-6.2-astra"
        self.assertEqual({sol: 2, astra: 1}, providers.WEIGHTS)
        picked = []
        for _ in range(60):
            picked.append(course.route(self.state([("codex", model) for model in picked]), "codex"))
        for start in range(len(picked) - providers.ROTATION_WINDOW + 1):
            self.assertIn(picked[start:start + providers.ROTATION_WINDOW].count(astra), (7, 8, 9), start)
        self.assertIn(picked.count(astra), (19, 20, 21), "a third of sixty")
        self.assertNotIn([astra, astra], [picked[i:i + 2] for i in range(len(picked) - 1)], "Astra never runs twice in a row")
        # Explorers and great works take Sol on top; those runs count toward Sol's two thirds.
        strong = self.state([("codex", sol)] * 18 + [("codex", astra)] * 6)
        self.assertEqual(astra, course.route(strong, "codex"))
        self.assertEqual(sol, course.route(self.state([("codex", sol)] * 15 + [("codex", astra)] * 9), "codex"))
        # Helpers are not counted, and the other families still share evenly.
        helpers = self.state([("codex", "gpt-6-luna")] * 10)
        self.assertEqual(sol, course.route(helpers, "codex"))
        self.assertEqual("muse-wonder-full-1.0", course.route(self.state([("muse", "muse-ember-1.0")]), "muse"))

    def test_the_codex_resident_asleep_longest_goes_next_whatever_its_route(self):
        # Steward, 18 November, night: "just rotate across all the codex residents when the others time out".
        sol, astra = "gpt-6.1-sol", "gpt-6.2-astra"
        people = {"fern": (sol, 30), "tern": (sol, 10), "rook": (astra, 20), "linnet": (astra, 40),
                  "moss": ("gpt-6-luna", 1), "iona": ("gpt-6-astra", 2)}
        state = {"at": 100.0, "sequence": 100, "tasks": {}, "maintenance": {"resident_returns": True, "migrations": {}},
                 "residents": {name: {"awake": False} for name in people} | {"isolde": {"awake": False}},
                 "life": {"budgets": {}, "runs": {name: {
                     "resident": name, "agent": "codex", "model": model, "status": "completed",
                     "started_sequence": ended - 1, "ended_sequence": ended} for name, (model, ended) in people.items()}}}
        state["life"]["runs"]["isolde"] = {"resident": "isolde", "agent": "muse", "model": "muse-wonder-full-1.0",
                                           "status": "completed", "started_sequence": 3, "ended_sequence": 4}
        self.assertFalse(course.turns(state, "codex"), "nothing changes before the Steward's migration")
        state["maintenance"]["migrations"][course.TURNS] = {"at": 50.0}
        self.assertTrue(course.turns(state, "codex"))
        self.assertFalse(any(course.turns(state, kind) for kind in ("muse", "agy", "opencode")))

        def order(count):
            picked = []
            for _ in range(count):
                who = course.next_resident(state, "codex", 100.0)
                picked.append(who)
                if who is not None:     # it runs and sleeps again: now it is the most recently ended
                    state["sequence"] += 2
                    state["life"]["runs"][who].update(started_sequence=state["sequence"] - 1,
                                                      ended_sequence=state["sequence"])
            return picked

        # Helpers (Luna) and the retired Astra route are not in the ordinary rotation; Muse is another family.
        self.assertEqual(["tern", "rook", "fern", "linnet"] * 2, order(8))
        state["residents"]["rook"]["awake"] = True
        self.assertEqual(["tern", "fern", "linnet"], order(3), "a resident who is awake is passed over")
        state["tasks"]["t"] = {"owner": "tern", "status": "claimed", "until": 500.0}
        self.assertEqual(["fern", "linnet"], order(2), "and so is one still holding a task")
        self.assertEqual("linnet", course.next_resident(state, "codex", 100.0, lambda resident: resident != "fern"),
                         "an author never reviews their own work")
        state["life"]["model_budgets"] = {"codex": {sol: {"until": 900.0}}}
        self.assertEqual(["linnet", "linnet"], order(2), "a route resting on its quota waits")
        state["life"]["model_budgets"]["codex"][astra] = {"until": 900.0}
        self.assertIsNone(course.next_resident(state, "codex", 100.0))

    def test_least_used_route_wins_and_nothing_defaults_to_lowest_effort(self):
        deepseek = "opencode-go/deepseek-v4.1-flash"
        state = self.state([("opencode", deepseek)] * 5)
        self.assertEqual("opencode-go/kimi-k3.1-pro", course.route(state, "opencode"))
        state = self.state([("opencode", deepseek), ("opencode", "opencode-go/kimi-k3.1-pro")])
        self.assertEqual("opencode-go/minimax-m3.1-flash", course.route(state, "opencode"))
        for kind, pool in providers.ROTATION.items():
            for model in pool:
                providers.validate_model(kind, model)
                self.assertFalse(model.endswith("-low"), model)
            providers.validate_model(kind, providers.STRONG[kind])

    def test_strong_route_and_helpers_do_not_count(self):
        state = self.state([("codex", "gpt-6-luna")] * 4)
        self.assertEqual("gpt-6.1-sol", course.route(state, "codex"))
        self.assertEqual("gpt-6.1-sol", course.route(state, "codex", strong=True))
        self.assertNotIn("gpt-6-astra", set(providers.STRONG.values()) | {m for p in providers.ROTATION.values() for m in p})
        state = self.state([("agy", "gemini-4-hydrogen-high")])
        self.assertEqual("gemini-4-argon-high", course.route(state, "agy"))


class GreatWorkTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()
        original = shelf.apply
        self.addCleanup(setattr, shelf, "apply", original)
        shelf.apply = lambda state, event, selection_version=3: original(state, event, selection_version=3)

    def publish_great(self, keys=("g1", "g2"), round_id="rg"):
        f = self.f
        generation = f.state.get("shelf", {}).get("generation", 0)
        f.send("explore-start", actor="other", round=round_id, expect=generation, token=round_id, seconds=100)
        f.send("explore-publish", actor="other", round=round_id, token=round_id,
               ideas=[great_idea(k) for k in keys])

    def open_great(self, key="great1", stages=2):
        f = self.f
        candidates = shelf.great_ideas(f.state["shelf"])
        f.send("choice-open", actor="author", choice=key, slot="great", milestones={
            k: [{"milestone": f"Stage {n}", "seconds": 2 * shelf.DAY} for n in range(stages)] for k in candidates})

    def test_full_shelf_still_admits_a_great_explorer_and_slots_are_separate(self):
        f = self.f
        f.publish(keys=("a", "b", "c"))
        self.assertTrue(shelf.great_wanted(f.state["shelf"]))
        self.publish_great()
        self.assertFalse(shelf.great_wanted(f.state["shelf"]))
        f.reject("shelf is full", "explore-start", actor="v1", round="r9", expect=2, token="r9", seconds=10)
        # A small choice freezes only small ideas.
        f.send("choice-open", actor="other", choice="small1", slot="small",
               milestones={k: {"milestone": "One example"} for k in ("a", "b", "c")})
        for voter in ("v1", "v2", "v3"):
            f.send("choice-vote", actor=voter, choice="small1", idea="a", reason="Useful")
        self.assertEqual("small", f.state["shelf"]["projects"]["small1"]["slot"])
        f.reject("small project slot is occupied", "choice-open", choice="small2", slot="small",
                 milestones={k: {"milestone": "x"} for k in ("b", "c")})
        f.reject("2 to 8", "choice-open", choice="great1", slot="great",
                 milestones={k: [{"milestone": "only one"}] for k in ("g1", "g2")})
        self.open_great()
        self.assertEqual(["g1", "g2"], f.state["shelf"]["choices"]["great1"]["candidates"])
        for voter in ("v1", "v2", "v3"):
            f.send("choice-vote", actor=voter, choice="great1", idea="g1", reason="Ambitious and wanted")
        project = f.state["shelf"]["projects"]["great1"]
        self.assertEqual(("great", 0, "Stage 0"), (project["slot"], project["stage"], project["milestone"]))
        self.assertEqual(2, len(shelf.active_projects(f.state["shelf"])))

    def test_great_work_advances_milestone_by_milestone(self):
        f = self.f
        self.publish_great(); self.open_great(stages=3)
        for voter in ("v1", "v2", "v3"):
            f.send("choice-vote", actor=voter, choice="great1", idea="g2", reason="Yes")
        f.state["tasks"]["m"] = {"status": "done", "artifacts": {"a.txt": {"sha256": "x"}}}
        for stage in (1, 2):
            f.send("project-done", actor="author", project="great1", evidence="m")
            project = f.state["shelf"]["projects"]["great1"]
            self.assertEqual(("active", stage, f"Stage {stage}"),
                             (project["status"], project["stage"], project["milestone"]))
        f.send("project-done", actor="author", project="great1", evidence="m")
        project = f.state["shelf"]["projects"]["great1"]
        self.assertEqual("done", project["status"])
        self.assertEqual([0, 1, 2], [entry["stage"] for entry in project["completed"]])


class LegacyShelfTests(unittest.TestCase):
    def test_older_versions_replay_unchanged(self):
        f = test_shelf.ShelfTests(); f.setUp()
        f.send("explore-start", round="r1", expect=0, token="r1", seconds=100)
        f.reject("invalid idea fields", "explore-publish", round="r1", token="r1",
                 ideas=[great_idea("a"), great_idea("b")])

    def test_policy_text_is_exactly_documented(self):
        self.assertEqual((ROOT / "docs/WORK_SELECTION_RULE_004.md").read_text(), shelf_gate.GREAT_POLICY_TEXT)
        self.assertEqual(3, shelf_gate.SUPPORTED_POLICIES[digest(shelf_gate.GREAT_POLICY_TEXT)])


class CourseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.prior = test_selection_repair.SelectionRepairTests(); self.prior.setUp()
        self.h = self.prior.h
        self.h.event("owner-migrate", self.prior.migration())

    def migration(self):
        old = maintenance.protected_manifest(self.h.state)
        extra = maintenance.OWNER_MODULES | maintenance.COURSE_MODULES
        changed = {name: "9" * 64 for name in maintenance.ALLOWED_CHANGES[maintenance.COURSE_SCOPE]
                   if name in old or name in extra}
        changed.update({name: "9" * 64 for name in extra})
        return self.prior.migration() | {
            "scope": maintenance.COURSE_SCOPE, "approval_sha256": maintenance.COURSE_SHA256,
            "previous_manifest_sha256": maintenance.fingerprint(old), "protected_files": old | changed}

    def test_enacts_great_work_rule_and_enables_course(self):
        data = self.migration(); data.pop("rule_base")
        self.h.event("owner-migrate", data)
        state = self.h.state
        self.assertTrue(course.enabled(state))
        self.assertEqual(shelf_gate.GREAT_POLICY_ID, shelf_gate.policy(state))
        self.assertEqual("superseded", state["council"]["rules"][shelf_gate.REVISED_POLICY_ID]["status"])
        self.assertTrue(set(maintenance.COURSE_MODULES) <= set(maintenance.protected_manifest(state)))

    def test_scope_is_bounded_and_bound_to_the_owner_words(self):
        data = self.migration(); data.pop("rule_base")
        for name in ("house/windows.py", "house/opencode_tool.py", "house/wake_policy.py", "house/test_sandbox.py"):
            if name not in data["protected_files"]:
                continue
            bad = copy.deepcopy(data); bad["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        self.assertEqual(digest((ROOT / "evidence/course-correction/owner-approval.txt").read_text()),
                         maintenance.COURSE_SHA256)

    def general(self, scope="upgrade-20261116-new-room", **files):
        old = maintenance.protected_manifest(self.h.state)
        manifest = old | {"house/windows.py": "8" * 64, "house/new_room.py": "7" * 64} | files
        return self.prior.migration() | {
            "scope": scope, "approval_sha256": "6" * 64,
            "previous_manifest_sha256": maintenance.fingerprint(old), "protected_files": manifest}

    def test_general_owner_upgrade_needs_only_the_course_correction(self):
        early = self.general(); early.pop("rule_base")
        self.h.reject("owner-migrate", early, "wrong owner approval")
        data = self.migration(); data.pop("rule_base")
        self.h.event("owner-migrate", data)
        bad = self.general(**{"docs/x.md": "7" * 64}); bad.pop("rule_base")
        self.h.reject("owner-migrate", bad, "invalid replacement manifest")
        good = self.general(); good.pop("rule_base")
        self.h.event("owner-migrate", good)
        manifest = maintenance.protected_manifest(self.h.state)
        self.assertEqual(("8" * 64, "7" * 64), (manifest["house/windows.py"], manifest["house/new_room.py"]))
        self.h.reject("owner-migrate", good, "already used|stale")
        self.assertIsNone(maintenance.UPGRADE.fullmatch("upgrade-tomorrow"))


class RenovationTests(unittest.TestCase):
    def descriptor(self, **files):
        return json.dumps({"source_commit": "a" * 40, "summary": "Teach the house a new trick",
                           "files": files or {"house/home.py": "b" * 64}})

    def test_descriptor_rejects_steward_only_and_foreign_paths(self):
        self.assertEqual({"house/home.py": "b" * 64}, renovation.descriptor(self.descriptor())["files"])
        for name in sorted(renovation.STEWARD_ONLY):
            with self.assertRaisesRegex(ValueError, "Steward-only"):
                renovation.descriptor(self.descriptor(**{name: "b" * 64}))
        for name in ("docs/x.md", "house/../x.py", "house/sub/x.py", "tests/test_x.py"):
            with self.assertRaisesRegex(ValueError, "not a house module"):
                renovation.descriptor(self.descriptor(**{name: "b" * 64}))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            renovation.descriptor('{"source_commit": "' + "a" * 40 + '", "summary": "x", "summary": "y", "files": {}}')

    def state(self):
        manifest = {"house/home.py": "1" * 64, "house/council.py": "2" * 64}
        return {"sequence": 5, "wake_policy": {"protected_files": manifest}, "maintenance": {"migrations": {course.SCOPE: {}}, "protected_files": manifest},
                "life": {"runs": {}}, "residents": {"watch-keeper": {"awake": True}},
                "proposals": {"reno-1": {"status": "enacted"}},
                "council": {"rules": {"reno-1": {"mode": "renovation", "status": "approved", "enacted_sequence": 4,
                                                 "renovation": renovation.descriptor(self.descriptor())}}}}

    def install_event(self, state, **changes):
        manifest = renovation.target_manifest(state, "reno-1")
        data = {"proposal": "reno-1", "source_head": "c" * 40, "protected_files": manifest,
                "previous_manifest_sha256": maintenance.fingerprint(maintenance.protected_manifest(state)),
                "previous_runtime_sha256": "d" * 64, "runtime_sha256": "e" * 64,
                "test_output_sha256": "f" * 64, "test_count": 3} | changes
        return {"op": "renovation-install", "actor": "watch-keeper", "at": 10, "data": data}

    def test_install_updates_only_the_enacted_files(self):
        state = self.state()
        self.assertEqual(["reno-1"], renovation.pending(state))
        renovation.apply(state, self.install_event(state))
        self.assertEqual({"house/home.py": "b" * 64, "house/council.py": "2" * 64},
                         state["maintenance"]["protected_files"])
        self.assertEqual("installed", state["council"]["rules"]["reno-1"]["status"])
        self.assertEqual([], renovation.pending(state))

    def test_install_rejects_other_files_resident_actor_active_runs_and_no_tests(self):
        for change, message in [
                ({"protected_files": {"house/home.py": "b" * 64, "house/council.py": "9" * 64}}, "differ"),
                ({"test_count": 0}, "passing tests")]:
            state = self.state()
            with self.assertRaisesRegex(ValueError, message):
                renovation.apply(state, self.install_event(state, **change))
        state = self.state()
        with self.assertRaisesRegex(ValueError, "coordinator"):
            renovation.apply(state, self.install_event(state) | {"actor": "resident-x"})
        state["life"]["runs"]["r"] = {"status": "active"}
        with self.assertRaisesRegex(ValueError, "drain"):
            renovation.apply(state, self.install_event(state))

    def test_failure_is_recorded_once(self):
        state = self.state()
        renovation.apply(state, {"op": "renovation-failed", "actor": "watch-keeper", "at": 10,
                                 "data": {"proposal": "reno-1", "reason": "tests failed"}})
        self.assertEqual("failed", state["council"]["rules"]["reno-1"]["status"])
        with self.assertRaisesRegex(ValueError, "not awaiting"):
            renovation.apply(state, self.install_event(state))

    def test_renovations_wait_an_hour_and_rules_a_day(self):
        state = {"maintenance": {"migrations": {council.QUICK_RENOVATIONS: {}}}}
        self.assertEqual(3600, council.veto_window(state, {"mode": "renovation"}))
        self.assertEqual(86400, council.veto_window(state, {"mode": "rule"}))
        self.assertEqual(86400, council.veto_window(state, {"mode": "wake-prompt"}))
        # History before the upgrade replays with the old window.
        self.assertEqual(86400, council.veto_window({"maintenance": {"migrations": {}}}, {"mode": "renovation"}))

    def test_outdated_renovation_is_named_without_draining(self):
        from unittest.mock import patch
        state = self.state()
        record = type("R", (), {"root": Path(".")})()
        with patch("house.wake_policy.source_snapshot", return_value={"files": {"house/home.py": "0" * 64, "house/council.py": "2" * 64}}):
            self.assertIn("house/home.py", renovation.outdated(record, state))
        with patch("house.wake_policy.source_snapshot", return_value={"files": {"house/home.py": "b" * 64, "house/council.py": "2" * 64}}):
            self.assertIsNone(renovation.outdated(record, state))

    def test_renovation_mode_needs_the_course_correction(self):
        self.assertIn("renovation", council.MODES)
        self.assertFalse(renovation.enabled({"maintenance": {}}))


class OwnerInstallTests(unittest.TestCase):
    """One-command owner upgrades: the drained coordinator installs a queued request."""

    def setUp(self):
        import subprocess, tempfile
        self.subprocess = subprocess
        self.root = Path(tempfile.mkdtemp(prefix="owner-install-"))
        self.addCleanup(__import__("shutil").rmtree, self.root, True)
        self.private = self.root / ".git/house-home"
        self.git("init", "-q")
        self.private.mkdir(parents=True)
        root = self.root

        class FakeRecord:
            def __init__(self):
                self.root = root
                self.common = root / ".git"

            def git(self, *args):
                return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout

            def read(self):
                return {"maintenance": {}, "council": {"rules": {}}}, [], "h"
        self.record = FakeRecord()

    def git(self, *args):
        return self.subprocess.run(["git", "-c", "user.name=T", "-c", "user.email=t@local", "-c",
                                    "commit.gpgsign=false", *args], cwd=self.root, capture_output=True,
                                   check=True, text=True).stdout.strip()

    def commit(self, text):
        (self.root / "house").mkdir(exist_ok=True)
        (self.root / "house/x.py").write_text(text)
        self.git("add", "-A"); self.git("commit", "-qm", text)
        return self.git("rev-parse", "HEAD")

    def queue(self, commit):
        from house import owner_upgrade
        owner_upgrade.atomic_json(self.private / owner_upgrade.REQUEST, {
            "format": "emberhall-owner-install-v1", "actor": "keeper-01", "scope": "upgrade-20261116-x",
            "note": str(self.private / "note.txt"), "source_commit": commit, "requested_at": 1})

    def test_scope_name_is_checked_before_anything_else(self):
        from house import owner_upgrade
        with self.assertRaisesRegex(ValueError, "upgrade-YYYYMMDD"):
            owner_upgrade.request_install(self.record, "keeper-01", "course-correction-20261115", "x")
        self.assertIsNone(owner_upgrade.pending_install(self.private))

    def test_status_says_what_a_waiting_install_waits_for(self):
        from unittest.mock import patch
        from house import owner_upgrade
        self.queue(self.commit("a = 1\n"))
        self.record.read = lambda: ({"life": {"runs": {"abcdef123": {"agent": "muse", "status": "active"}}}}, [], "h")
        with patch("house.runtime.selected", return_value={"source_head": "c" * 40}), \
                patch("house.publication_worker.drained", return_value=True):
            found = owner_upgrade.status(self.record)
        self.assertEqual(["muse abcdef12"], found["draining"]["active_residents"])
        self.assertEqual((0, True), (found["draining"]["unfinished_jobs"], found["draining"]["pages_publisher_idle"]))

    def test_steward_only_change_after_request_is_refused_and_releases_the_hold(self):
        from house import owner_upgrade
        self.queue(self.commit("a = 1\n"))
        (self.root / "house/council.py").write_text("changed = True\n")
        self.git("add", "-A"); self.git("commit", "-qm", "resident council change")
        with self.assertRaisesRegex(ValueError, "Steward-only house code changed after the request"):
            owner_upgrade.install_requested(self.record, self.private)
        self.assertIsNone(owner_upgrade.pending_install(self.private))

    def test_reviewed_resident_work_landed_while_draining_is_included(self):
        from unittest.mock import patch
        from house import owner_upgrade
        self.queue(self.commit("a = 1\n"))
        self.commit("a = 2\n")
        with patch.object(owner_upgrade, "prepare", return_value=Path("plan")) as prepare, \
                patch.object(owner_upgrade, "apply", return_value={"runtime": {"entry": "r.pyz"}}):
            result = owner_upgrade.install_requested(self.record, self.private)
        self.assertEqual(["house/x.py"], result["included_resident_changes"])
        self.assertEqual(self.git("rev-parse", "HEAD"), prepare.call_args.args[4])
        self.assertIsNone(owner_upgrade.pending_install(self.private))

    def coordinator(self):
        from house import home
        fake = type("C", (), {})()
        fake.record, fake.private, fake.running, fake.stopping = self.record, self.private, {}, False
        return fake, home.Coordinator.renovate

    def test_coordinator_holds_until_drained_then_installs_and_restarts(self):
        from unittest.mock import patch
        from house import owner_upgrade
        self.queue(self.commit("a = 1\n"))
        fake, renovate = self.coordinator()
        with patch("house.renovation.drained", return_value=False):
            self.assertTrue(renovate(fake))
        with patch("house.renovation.drained", return_value=True), \
                patch.object(owner_upgrade, "install_requested", return_value={"installed": True}):
            self.assertTrue(renovate(fake))
        self.assertTrue(fake.stopping)
        self.assertTrue((self.private / "owner-install-result.json").is_file())

    def test_coordinator_failure_is_recorded_once_and_admissions_resume(self):
        from unittest.mock import patch
        self.queue(self.commit("a = 1\n"))
        fake, renovate = self.coordinator()
        with patch("house.renovation.drained", return_value=True):
            self.assertFalse(renovate(fake))
        self.assertFalse(fake.stopping)
        self.assertIn("note.txt", json.loads((self.private / "owner-install-error.json").read_text())["reason"])
        self.assertFalse(renovate(fake))  # The request was consumed; nothing is retried.
