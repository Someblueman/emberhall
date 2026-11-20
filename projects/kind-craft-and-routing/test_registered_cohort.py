"""A new registration cannot recycle an earlier cohort or move its boundary."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import collect_trial
import offer_fields
import registered_cohort as registered
import test_trial
import tie_replay
import trial
import turn_loss


class RegisteredCohortTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.path = self.directory / "registration.json"
        patcher = patch.object(registered, "REGISTRATION", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        declaration = patch.object(registered, "DECLARATION_ID", "fixture-registration")
        declaration.start()
        self.addCleanup(declaration.stop)
        self.house = test_trial.TrialTests()
        self.house.setUp()
        self.manifest = {f"house/{name}.py": "f" * 64 for name in registered.POLICY_MODULES}
        self.config = {"schema": 1, "name": "new-cohort", "task": "declare-new-cohort",
                       "registrar": "writer", "installation": 22498, "source_commit": "a" * 40,
                       "manifest_sha256": hashlib.sha256(registered.canonical(self.manifest).encode()).hexdigest(),
                       "policy_files": self.manifest.copy()}
        self.save()
        self.house.events = [{"sequence": 22497, "id": "22497", "op": "task", "actor": "writer",
                              "data": {"task": "early", "project": "math"}}]
        self.house.install(op="owner-migrate", protected_files=self.manifest)

    def save(self):
        self.path.write_text(json.dumps(self.config))

    def declare(self):
        self.house.add("task", "writer", task=self.config["task"], project=registered.PROJECT)
        seq = self.house.add("learn", "writer", evidence=registered.PREFIX + registered.canonical(self.config))
        self.house.events[-1]["id"] = registered.DECLARATION_ID
        return seq

    def result(self):
        return trial.assess(self.house.events, self.house.events[-1]["sequence"], trial.NEXT)

    def test_only_offers_after_public_declaration_enroll_and_late_reviews_join(self):
        self.house.offer("before", "early", finished=True)
        self.assertIsNone(self.result()["installed_at"])
        declared = self.declare()
        offer = self.house.offer("receiver", "early", finished=True)
        review = {"run": "receiver", "actor": "reviewer", "base": "b" * 40,
                  "contribution": "c" * 40, "status": "integrated", "test_exit": 0}
        seq = self.house.add("say", "reviewer", text="house-integration-v1 " + json.dumps(review))
        self.house.events[-1]["id"] = "87654321-4321-4321-8321-123456789abc"
        result = self.result()
        self.assertEqual((22498, declared, declared, 0),
                         (result["installed_at"], result["declared_at"], result["admissions_after"], result["routing_weight"]))
        self.assertEqual([offer], [r["offer"] for r in result["enrolled"]])
        self.assertEqual(seq, result["enrolled"][0]["receiver_first_review"]["sequence"])
        # Omitting the registration, instead of silently treating the install as
        # the boundary, leaves the separate cohort unobserved.
        self.assertIsNone(trial.assess(self.house.events[:declared - 22497], declared - 1, trial.NEXT)["installed_at"])

    def test_every_consumer_uses_the_same_registered_boundary_and_collector_reopens(self):
        self.house.offer("before", "early", finished=True)
        self.declare()
        offer = self.house.offer("receiver", "early", finished=True)
        events, through = self.house.events, self.house.events[-1]["sequence"]
        runs = {e["data"]["run"]: e["data"] | {"started_sequence": e["sequence"]}
                for e in events if e["op"] == "life" and e["data"]["kind"] == "run-start"}
        status = {"house_id": "test", "sequence": through, "life": {"runs": runs, "requests": {}},
                  "shelf": {"record": {"projects": {"math": {"started_sequence": 1, "idea": "proof"}},
                                       "ideas": {"proof": {"brief": {"sequence": 1, "field": "mathematics"}}}}}}
        fields = offer_fields.compare(status, events, through, baseline=trial.NEXT)
        ties = tie_replay.replay(status, events, through, trial.NEXT)
        turns = turn_loss.report(status, events, through, trial.NEXT)
        self.assertEqual([offer], [r["offer"] for r in fields["offers"]])
        self.assertEqual([offer], [r["offer"] for r in ties["decisions"]])
        self.assertEqual([offer], [r["offer"] for r in turns["decisions"]])
        self.assertEqual(0, ties["routing_weight"])

        def reader(*args):
            if args == ("status",):
                return status
            after, count = int(args[4]), int(args[6])
            page = [e for e in events if after < e["sequence"] <= after + count]
            end = page[-1]["sequence"]
            return {"events": page, "through": end, "latest": through, "has_more": end < through}

        directory = self.directory / "collection"
        expected = collect_trial.collect(directory, "writer", trial.NEXT, 22497, reader)
        reopened = collect_trial.collect(directory, "writer", trial.NEXT, 22497,
                                         lambda *args: self.fail("reopened collection contacted the house"))
        self.assertEqual(expected, reopened)
        self.assertEqual([offer], [r["offer"] for r in expected["enrolled"]])

    def test_registration_schema_cannot_omit_policy_files_or_accept_malformed_identity(self):
        original = copy.deepcopy(self.config)
        variants = [original | {"installation": True}, original | {"source_commit": 123},
                    original | {"manifest_sha256": "z" * 64}, original | {"schema": 2},
                    original | {"schema": True}, original | {"extra": 1}, original | {"policy_files": {}}]
        for config in variants:
            with self.subTest(config=config), self.assertRaises(ValueError):
                self.config = config
                self.save()
                registered.load()

    def test_changed_registration_or_untrusted_declaration_cannot_redefine_the_sample(self):
        self.declare()
        original = copy.deepcopy(self.config)
        self.config["name"] = "another"
        self.save()
        with self.assertRaisesRegex(ValueError, "public cohort declaration"):
            self.result()
        self.config = original | {"task": "replaced"}
        self.save()
        with self.assertRaisesRegex(ValueError, "public cohort declaration"):
            self.result()
        self.config = original
        self.save()
        self.house.events[-1]["actor"] = "someone-else"
        with self.assertRaisesRegex(ValueError, "wrong author"):
            self.result()
        self.house.events[-1]["actor"] = "writer"
        self.house.events[-2]["data"]["project"] = "other"
        with self.assertRaisesRegex(ValueError, "public cohort declaration"):
            self.result()

    def test_identical_declaration_under_another_receipt_cannot_replace_the_pinned_one(self):
        self.declare()
        self.house.events[-1]["id"] = "another-registration"
        self.assertIsNone(self.result()["installed_at"])

    def test_wrong_installation_or_missing_earlier_pages_is_refused(self):
        self.declare()
        install = self.house.events[1]
        original = copy.deepcopy(install)
        for edit in ({"source_head": "b" * 40}, {"protected_files": {}},
                     {"protected_files": self.manifest | {"house/body.py": "e" * 64}}):
            install["data"] = original["data"] | edit
            with self.subTest(edit=edit), self.assertRaisesRegex(ValueError, "pinned source"):
                self.result()
        install.update(original)
        with self.assertRaisesRegex(ValueError, "include registered installation"):
            trial.assess(self.house.events[2:], self.house.events[-1]["sequence"], trial.NEXT)

    def test_policy_change_before_declaration_prevents_all_enrollment(self):
        changed = self.house.install(op="owner-migrate", protected_files=self.manifest | {"house/course.py": "0" * 64})
        self.declare()
        self.house.offer("late", "early", finished=True)
        result = self.result()
        self.assertEqual((changed, []), (result["runtime_changed_at"], result["enrolled"]))

    def test_each_policy_module_stops_admissions_missing_hash_is_distinct_and_restoring_does_not_restart(self):
        self.declare()
        offer = self.house.offer("receiver", "early", finished=True)
        base = copy.deepcopy(self.house.events)
        for name in registered.POLICY_MODULES:
            with self.subTest(name=name):
                self.house.events = copy.deepcopy(base)
                stop = self.house.install(op="owner-migrate", protected_files=self.manifest | {f"house/{name}.py": "0" * 64})
                self.house.install(op="owner-migrate", protected_files=self.manifest)
                self.house.offer("later", "different", finished=True)
                result = self.result()
                self.assertEqual((stop, [offer]), (result["runtime_changed_at"], [r["offer"] for r in result["enrolled"]]))
        self.house.events = base
        partial = self.manifest.copy()
        del partial["house/project_work.py"]
        stop = self.house.install(op="owner-migrate", protected_files=partial)
        self.assertEqual(stop, self.result()["runtime_unverified_at"])

    def test_quota_and_repeated_tasks_do_not_fill_twenty_places(self):
        self.declare()
        self.house.offer("quota", "early", outcome="quota", finished=True)
        for n in range(21):
            self.house.offer(f"run-{n}", f"task-{n}", finished=True)
        self.house.offer("again", "task-0", finished=True)
        result = self.result()
        self.assertEqual((20, 1, "twenty baseline offers observed"),
                         (len(result["enrolled"]), result["quota_exits"], result["state"]))

    def test_report_only_change_does_not_close_enrollment_and_explorer_stays_out(self):
        self.declare()
        self.house.install(op="owner-migrate", protected_files=self.manifest | {"house/body.py": "e" * 64})
        self.house.offer("explorer", "early")
        start = next(e for e in self.house.events if e["op"] == "life" and e["data"].get("run") == "explorer")
        start["data"]["explore_generation"] = 1
        receipt = next(e for e in self.house.events if e["id"] == "home-explorer-assignment")
        value = json.loads(receipt["data"]["text"].split(" ", 1)[1])
        for key in ("task", "task_generation", "tied_families"):
            del value[key]
        receipt["data"]["text"] = "house-assignment-v1 " + json.dumps(value)
        offer = self.house.offer("work", "early", finished=True)
        result = self.result()
        self.assertEqual([offer], [r["offer"] for r in result["enrolled"]])
        self.assertIsNone(result["runtime_changed_at"])


if __name__ == "__main__":
    unittest.main()
