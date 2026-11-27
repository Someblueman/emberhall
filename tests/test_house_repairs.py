"""The 26 November repairs on disposable journal projections and inert runs."""
import copy
import unittest
from unittest.mock import patch

from house import home, maintenance, project_work, shelf
from house.governance import canonical, digest
from house.model import apply_event
from tests import test_course_correction, test_helper_home, test_helper_staffing, test_home, test_shelf


class RepairJournalTests(unittest.TestCase):
    def setUp(self):
        self.prior = test_course_correction.CourseMigrationTests()
        self.prior.setUp()
        data = self.prior.migration()
        data.pop("rule_base")
        self.prior.h.event("owner-migrate", data)
        self.base = copy.deepcopy(self.prior.h.state)
        self.state = copy.deepcopy(self.base)
        self.events = []
        self.send("life", {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"})
        self.shelf_event("explore-start", round="r1", expect=0, token="r1", seconds=60)
        self.shelf_event("explore-publish", round="r1", token="r1", ideas=[
            test_shelf.idea("small") | {"scale": "small"},
            test_shelf.idea("great") | {"scale": "great"}])

    def send(self, op, data, actor="alice", at=None):
        event = {"id": f"repair-fixture-{len(self.events)}", "op": op, "actor": actor,
                 "at": self.state["at"] + 1 if at is None else at, "data": data}
        self.state = apply_event(copy.deepcopy(self.state), event)
        self.events.append(event)

    def shelf_event(self, kind, actor="alice", at=None, **data):
        self.send("shelf", {"kind": kind, **data}, actor, at)

    def migrate(self, scope="upgrade-20261126-house-repairs", at=None):
        old = maintenance.protected_manifest(self.state)
        data = self.prior.general(scope=scope)
        data.pop("rule_base")
        self.send("owner-migrate", data | {"previous_manifest_sha256": maintenance.fingerprint(old),
                  "protected_files": old | data["protected_files"]}, at=at)

    def choice(self, which, seconds=2 * shelf.DAY):
        plan = {"milestone": "A visible result", "seconds": seconds}
        plans = [plan, {"milestone": "The next result"}] if which == "great" else plan
        self.shelf_event("choice-open", choice=f"choose-{which}", slot=which, milestones={which: plans})

    def vote(self, which, actor):
        self.shelf_event("choice-vote", actor, choice=f"choose-{which}", idea=which, reason="Useful result")

    def choose(self, which, **kwargs):
        self.choice(which, **kwargs)
        for voter in ("bob", "carol", "dana"):
            self.vote(which, voter)

    def project(self, which):
        return self.state["shelf"]["projects"][f"choose-{which}"]

    def extend(self, actor, at):
        self.shelf_event("project-extend-vote", actor, at, project="choose-small", reason="Useful progress")

    def observe(self, at):
        self.send("say", {"text": "A later event reconciles the shelf."}, at=at)

    def replay(self):
        result = copy.deepcopy(self.base)
        for event in self.events:
            result = apply_event(result, event)
        return result

    def test_without_migration_the_same_history_replays_as_before(self):
        with self.assertRaisesRegex(ValueError, "unknown shelf action"):
            self.shelf_event("house-only-end", note="Too early")
        self.choose("great")
        self.choose("small")
        deadline = self.project("small")["deadline"]
        with self.assertRaisesRegex(ValueError, "deadline has not arrived"):
            self.extend("bob", deadline - 1)
        for voter in ("bob", "carol", "dana"):
            self.extend(voter, deadline + 1)
        self.observe(deadline + 7 * shelf.DAY)
        self.assertEqual("dropped", self.project("great")["status"])
        self.assertEqual("active", self.project("small")["status"])
        self.observe(self.project("small")["deadline"] + 7 * shelf.DAY)
        self.assertEqual(self.state, self.replay())
        # Canonical projection of this history on the source before the repair migration.
        self.assertEqual("2331fc3e7b33869ebb9aee5be90d45975439c1dbe48d9b9ae2e17c4e13e5fd4b",
                         digest(canonical(self.state).decode()))

    def test_only_house_choices_can_open_or_close_and_only_steward_can_end_it(self):
        self.choose("great")
        self.choice("small")
        for voter in ("bob", "carol"):
            self.vote("small", voter)
        projects = copy.deepcopy(self.state["shelf"]["projects"])
        self.migrate()
        migration = self.state["maintenance"]["migrations"][shelf.HOUSE_REPAIRS]
        self.assertEqual((self.state["at"], self.state["sequence"]), (migration["at"], migration["sequence"]))
        self.assertEqual(projects, self.state["shelf"]["projects"])
        for which in ("small", "great"):
            with self.assertRaisesRegex(ValueError, "only house choices"):
                self.choice(which)
        with self.assertRaisesRegex(ValueError, "only house choices"):
            self.vote("small", "dana")
        with self.assertRaisesRegex(ValueError, "only the Steward"):
            self.shelf_event("house-only-end", "bob", note="Resume")
        with self.assertRaisesRegex(ValueError, "unexpected shelf fields"):
            self.shelf_event("house-only-end", note="Resume", trial="an-isolated-trial")
        self.shelf_event("house-only-end", note="Resume")
        self.assertEqual({"actor": "alice", "at": self.state["at"], "sequence": self.state["sequence"],
                          "note": "Resume"}, self.state["shelf"]["house_only_end"])
        with self.assertRaisesRegex(ValueError, "already ended"):
            self.shelf_event("house-only-end", note="Again")
        self.vote("small", "dana")
        self.assertEqual("active", self.project("small")["status"])
        self.assertEqual(self.state, self.replay())

    def test_a_great_ballot_waits_for_the_steward_to_end_the_period(self):
        self.choice("great")
        for voter in ("bob", "carol"):
            self.vote("great", voter)
        self.migrate()
        with self.assertRaisesRegex(ValueError, "only house choices"):
            self.vote("great", "dana")
        self.shelf_event("house-only-end", note="Resume")
        self.vote("great", "dana")
        self.assertEqual("active", self.project("great")["status"])

    def test_house_choice_can_open_and_close_while_a_small_ballot_waits(self):
        self.choice("small")
        self.migrate(shelf.HOUSE_WORK)
        # Seed a house idea already on the shelf. Brief acceptance is covered by test_house_work.
        ideas = self.state["shelf"]["ideas"]
        ideas["house"] = copy.deepcopy(ideas["great"]) | {"title": "House work", "scale": "house"}
        self.migrate()
        self.choose("house")
        self.assertEqual("active", self.project("house")["status"])
        self.assertEqual("open", self.state["shelf"]["choices"]["choose-small"]["status"])

    def test_deadline_at_migration_is_hard_and_earlier_deadlines_keep_grace(self):
        self.choose("great")
        self.choose("small", seconds=shelf.DAY - 5)
        deadline = self.project("great")["deadline"]
        earlier = self.project("small")["deadline"]
        self.assertLess(earlier, deadline)
        self.migrate(at=deadline)
        self.assertEqual("dropped", self.project("great")["status"])
        self.assertEqual("active", self.project("small")["status"])
        self.observe(earlier + 7 * shelf.DAY)
        self.assertEqual("dropped", self.project("small")["status"])

    def test_extension_requires_three_votes_before_hard_deadline(self):
        self.choose("small")
        self.migrate()
        deadline = self.project("small")["deadline"]
        with self.assertRaisesRegex(ValueError, "open one day before"):
            self.extend("bob", deadline - shelf.DAY - 1)
        with self.assertRaisesRegex(ValueError, "owner cannot"):
            self.extend("alice", deadline - shelf.DAY)
        self.extend("bob", deadline - shelf.DAY)
        self.extend("carol", deadline - 1)
        self.assertFalse(self.project("small")["extended"])
        self.assertIsNone(project_work.active_project(self.state, "choose-small", deadline))
        with self.assertRaisesRegex(ValueError, "not active"):
            self.extend("dana", deadline)
        self.extend("dana", deadline - 1)
        self.assertTrue(self.project("small")["extended"])
        self.assertEqual(deadline + 7 * shelf.DAY, self.project("small")["deadline"])
        self.shelf_event("house-only-end", note="Resume")
        self.observe(deadline)
        self.assertEqual("active", self.project("small")["status"])
        self.observe(deadline + 7 * shelf.DAY)
        self.assertEqual("no timely second-deadline decision", self.project("small")["lesson"])
        self.assertEqual(self.state, self.replay())


class RepairFocusTests(unittest.TestCase):
    def test_no_task_falls_back_to_a_visible_repair_and_legacy_keeps_house_work(self):
        state = {"at": 1000, "tasks": {}, "shelf": shelf.empty(),
                 "maintenance": {"migrations": {shelf.HOUSE_WORK: {"at": 1}, home.SHOWN: {"at": 2}}}}
        state["shelf"]["projects"]["rooms"] = {"slot": "house", "status": "active", "deadline": 3000,
                                              "idea": "room-idea", "milestone": "Make the rooms legible",
                                              "owner": "alice"}
        state["shelf"]["ideas"]["room-idea"] = {"title": "Better rooms"}
        self.assertIn("create the next piece", home.focus_prompt(state, "improve"))
        state["maintenance"]["migrations"][shelf.HOUSE_REPAIRS] = {"at": 1000}
        state["tasks"]["finished-room-task"] = {"project": "rooms", "status": "done", "ready": True, "until": 0}
        owner_note = home.closing_line(state, "alice")
        self.assertIn("project-done", owner_note)
        self.assertIn("fix a visible site bug", owner_note)
        self.assertIn("No house project has a task you can claim now", home.focus_prompt(state, "room"))
        for task in ({"status": "open", "ready": False, "until": 0},
                     {"status": "claimed", "ready": True, "until": 1100}):
            state["tasks"]["room-task"] = task | {"project": "rooms"}
            prompt = home.focus_prompt(state, "room")
            self.assertIn("No house project has a task you can claim now", prompt)
            self.assertNotIn("create the next piece", prompt)
            for words in ("docs/SITE_REPAIRS.md", "first unchecked", "If the list is missing", "site/",
                          "exact files it owns", "Claim it before editing", "Do not sleep BLOCKED"):
                self.assertIn(words, prompt)
        state["tasks"]["room-task"].update(status="open", until=0)
        prompt = home.focus_prompt(state, "improve")
        self.assertIn("advance the active house project rooms", prompt)
        self.assertIn("If no task is still available when you check", prompt)
        self.assertIn("No house project has a task", home.focus_prompt(state, "room", at=3000))
        state["shelf"]["house_only_end"] = {"note": "Resume"}
        self.assertIn("create the next piece", home.focus_prompt(state, "improve"))

    def test_concurrent_ordinary_starts_rotate_and_use_direction_with_no_repair_file(self):
        fixture = test_home.HomeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.delay = 30
        coordinator = fixture.coordinator

        def drain():
            # The inert children spawn no descendants. Wait directly so this test
            # does not depend on the host's process-listing permission.
            for running in coordinator.running.values():
                running.process.terminate()
                running.process.wait(timeout=15)
            with patch("house.home.group_stopped", return_value=True):
                fixture.drain()

        self.addCleanup(drain)
        with patch("house.shelf.repairs_since", return_value=1):
            first = coordinator.tick(poll=False)["started"][0]
            second = coordinator.start("muse")
        self.assertEqual({first, second}, set(coordinator.running))
        for run, focus in ((first, "improve"), (second, "room")):
            private = coordinator.private / run
            prompt = (private / "prompt.txt").read_text()
            self.assertIn(f"HOUSE FOCUS for this run ({focus})", prompt)
            self.assertIn("HOUSE REPAIRS (Steward, 26 November", prompt)
            self.assertIn("the website keeps crashing", prompt)
            self.assertIn("docs/SITE_REPAIRS.md", prompt)
        self.assertEqual(2, coordinator.focus_record()["count"])

    def test_house_research_takes_one_explorer_turn_before_repairs(self):
        fixture = test_home.HomeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.delay = 30
        coordinator = fixture.coordinator

        def drain():
            for running in coordinator.running.values():
                running.process.terminate()
                running.process.wait(timeout=15)
            with patch("house.home.group_stopped", return_value=True):
                fixture.drain()

        def demand(state, at):
            # One round at a time: an admitted Explorer closes the demand, as explorer_reserved does live.
            runs = state.get("life", {}).get("runs", {}).values()
            return None if any("explore_generation" in run for run in runs) else 0

        self.addCleanup(drain)
        with patch("house.shelf.repairs_since", return_value=1), \
                patch("house.shelf.house_research", return_value=True), \
                patch("house.life.explorer_demand", demand):
            first = coordinator.tick(poll=False)["started"][0]
            second = coordinator.start("muse")
        runs = fixture.record.read()[0]["life"]["runs"]
        self.assertEqual(0, runs[first]["explore_generation"])
        self.assertNotIn("explore_generation", runs[second])
        explorer = (coordinator.private / first / "prompt.txt").read_text()
        self.assertIn("Automatic Explorer assignment", explorer)
        self.assertNotIn("HOUSE FOCUS for this run", explorer)
        self.assertIn("HOUSE FOCUS for this run", (coordinator.private / second / "prompt.txt").read_text())
        self.assertEqual(1, coordinator.focus_record()["count"])

    def test_helpers_and_reviews_do_not_take_a_repair_turn(self):
        fixture = test_helper_home.HelperHomeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        test_helper_staffing.regulars(fixture.record)
        test_helper_staffing.offer(fixture.record, "build")
        with patch("house.shelf.repairs_since", return_value=1):
            helper = fixture.launch_failure(backlog=True, task_id="build", task_generation=0,
                                            helper_model="gpt-6-luna")
            fixture.record.append("life", "alice", {"kind": "help", "request": "review",
                                  "review_run": helper, "reason": "Independent review"})
            state = fixture.record.read()[0]
            after_cooldown = state["life"]["budgets"]["codex"]["until"] + 1
            with patch("house.home.time.time", return_value=after_cooldown):
                review = fixture.launch_failure(help_id="review")
        self.assertEqual("review", fixture.record.read()[0]["life"]["runs"][review]["mode"])
        for run in (helper, review):
            prompt = (fixture.coordinator.private / run / "prompt.txt").read_text()
            self.assertNotIn("HOUSE REPAIRS", prompt)
            self.assertNotIn("HOUSE FOCUS", prompt)
        self.assertEqual({}, fixture.coordinator.focus_record())


class HouseResearchTests(RepairJournalTests):
    def research(self):
        record = shelf.empty() | self.state.get("shelf", {})
        # The live house has had the research-flow migration since 16 November; this fixture predates it.
        with patch.object(shelf, "flow_since", lambda state: 0.0):
            return shelf.thin(self.state, record), shelf.research_open(self.state, record, self.state["at"], 3)

    def test_house_research_runs_only_with_its_migration_during_the_period(self):
        self.migrate()
        self.assertTrue(shelf.house_only(self.state))
        self.assertFalse(shelf.house_research(self.state))
        self.assertNotEqual(self.research()[0], ["house"])
        self.migrate(scope=shelf.HOUSE_RESEARCH)
        self.assertTrue(shelf.house_research(self.state))
        self.assertEqual(self.research(), (["house"], True))
        self.shelf_event("house-only-end", note="Resume great and small choices.")
        self.assertFalse(shelf.house_research(self.state))

    def test_a_full_house_bench_closes_house_research(self):
        self.migrate()
        self.migrate(scope=shelf.HOUSE_RESEARCH)
        kept = {f"house-{n}": {"scale": "house"} for n in range(shelf.HOUSE_ONLY_BENCH)}
        with patch.object(shelf, "shelf_ids", lambda record: list(kept)), \
                patch.object(shelf, "grounded", lambda state, idea: True), \
                patch.dict(self.state["shelf"]["ideas"], kept):
            self.assertEqual(self.research(), ([], False))
        with patch.object(shelf, "shelf_ids", lambda record: list(kept)[1:]), \
                patch.object(shelf, "grounded", lambda state, idea: True), \
                patch.dict(self.state["shelf"]["ideas"], kept):
            self.assertEqual(self.research(), (["house"], True))
