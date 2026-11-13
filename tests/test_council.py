"""Council gates on simulated clocks: these tests are not a lived 24-hour trial."""
import base64
import copy
import unittest
from unittest.mock import patch
import uuid

from house import council
from house.governance import digest
from house.model import apply_event
from house.record import Record
from house.steward import notice_body
from tests.support import HouseCase


def approval():
    return {"source_sha256": council.APPROVED_SOURCE_SHA256, "source": "Actual Steward attachment",
            "repository": council.REPOSITORY, "issue": council.ISSUE, "owner_id": council.OWNER_ID}


class CouncilTests(unittest.TestCase):
    def setUp(self):
        self.now = 1700000000
        self.counter = 0
        self.state = apply_event(None, {"id": "foundation", "op": "found", "actor": "founder",
            "at": self.now, "data": {"house_id": council.APPROVED_HOUSE, "name": "Test",
                                     "rules": "Founding charter", "owner_key": ""}})
        for actor in ("alice", "bob", "carol", "dana"):
            self.event("arrive", {"name": actor}, actor)

    def event(self, op, data, actor="alice"):
        self.counter += 1
        # Like Record, every attempted operation owns a disposable projection.
        projected = copy.deepcopy(self.state)
        result = apply_event(projected, {"id": f"event-{self.counter}", "op": op, "actor": actor,
                                        "at": self.now, "data": data})
        self.state = result

    def reject(self, op, data, pattern, actor="alice"):
        before = copy.deepcopy(self.state)
        with self.assertRaisesRegex(ValueError, pattern):
            self.event(op, data, actor)
        self.assertEqual(self.state, before)

    def authorize(self):
        self.event("council-authorize", approval())

    def propose(self, name="rule-one", text="Keep a witnessed recovery receipt."):
        self.event("council-propose", {"proposal": name, "mode": "rule", "title": name,
                   "text": text, "reason": "A witnessed improvement", "base": self.state["rule_revision"]})

    def completed_task(self):
        if "trial-work" in self.state["tasks"]:
            return
        self.event("task", {"task": "trial-work", "title": "Trial", "description": "Real artifacts"})
        self.event("claim", {"task": "trial-work", "token": "unique", "expect": 0, "seconds": 60})
        content = b"Reproducible trial results"
        self.event("finish", {"task": "trial-work", "token": "unique", "result": "Trial passed",
            "artifacts": {"report.txt": {"sha256": digest(content.decode()),
                                         "base64": base64.b64encode(content).decode()}}})

    def trial(self, name="rule-one"):
        self.completed_task()
        self.event("council-trial", {"proposal": name, "task": "trial-work", "evidence": "Checked result"})

    def endorse(self, name="rule-one", actor="bob"):
        self.event("council-endorse", {"proposal": name, "evidence": "Independent artifact inspection"}, actor)

    def notice(self, name="rule-one", **changes):
        self.event("council-notice", {"proposal": name, "repository": council.REPOSITORY,
            "issue": council.ISSUE, "comment_id": self.counter + 100,
            "text_sha256": digest(self.state["proposals"][name]["text"])} | changes)

    def comment(self, body, comment_id=9001, actor_id=council.OWNER_ID):
        return {"id": comment_id, "actor_id": actor_id, "created_at": self.now, "body": body}

    def sync(self, comments=None, **changes):
        self.event("council-sync", {"repository": council.REPOSITORY, "issue": council.ISSUE,
            "owner_id": council.OWNER_ID, "checked_at": self.now,
            "comments": [] if comments is None else comments} | changes)

    def ready(self, name="rule-one"):
        self.propose(name)
        self.trial(name)
        self.endorse(name, "bob")
        self.endorse(name, "carol")
        self.notice(name)

    def enact(self, name="rule-one"):
        self.event("council-enact", {"proposal": name})

    def test_authorization_is_exact_one_time_and_does_not_rewrite_history(self):
        before = copy.deepcopy(self.state)
        for changes in ({"source_sha256": "0" * 64}, {"owner_id": 9}, {"issue": 2},
                        {"repository": "another/house"}, {"veto_window_seconds": 0}):
            self.reject("council-authorize", approval() | changes, "source|identity|issue|fields")
        self.state["house_id"] = "unapproved-house"
        self.reject("council-authorize", approval(), "different house")
        self.state["house_id"] = council.APPROVED_HOUSE
        self.authorize()
        for key in ("rules", "rule_revision", "owner_key", "proposals", "tasks"):
            self.assertEqual(self.state[key], before[key])
        self.reject("council-authorize", approval(), "already authorized")

    def test_process_changes_unknown_ops_and_legacy_paths_cannot_bypass(self):
        self.reject("council-enact", {"proposal": "rule-one"}, "not authorized")
        self.event("propose", {"proposal": "legacy", "text": "Replacement", "reason": "Old",
                              "base": self.state["rule_revision"]})
        self.authorize()
        self.reject("ratify", {"proposal": "legacy", "signature": "Forged"}, "council|Steward|process")
        self.reject("council-enact", {"proposal": "legacy"}, "not a council")
        self.reject("council-configure", {"endorsements_required": 0}, "unknown council")
        body = {"proposal": "change", "mode": "process", "title": "Change process", "text": "No wait",
                "reason": "Shortcut", "base": self.state["rule_revision"]}
        self.reject("council-propose", body, "only additive")
        self.reject("council-propose", body | {"mode": "rule", "proposal": "ratification-process"}, "reserved")

    def test_trials_require_accepted_completion_and_capture_immutable_hashes(self):
        self.authorize(); self.propose()
        data = {"proposal": "rule-one", "task": "missing", "evidence": "Claim only"}
        self.reject("council-trial", data, "completed task")
        self.event("task", {"task": "open", "title": "Open", "description": "Not completed"})
        self.reject("council-trial", data | {"task": "open"}, "completed task")
        self.trial()
        trial = self.state["proposals"]["rule-one"]["trial"]
        self.assertEqual(trial["artifacts"], {"report.txt": digest("Reproducible trial results")})
        self.reject("council-trial", data | {"task": "trial-work"}, "already recorded")

    def test_two_independent_non_author_endorsements_are_required(self):
        self.authorize(); self.propose()
        endorsement = {"proposal": "rule-one", "evidence": "I checked"}
        self.reject("council-endorse", endorsement, "trial", "bob")
        self.trial()
        self.reject("council-endorse", endorsement, "own rule")
        self.endorse()
        self.reject("council-endorse", endorsement, "already endorsed", "bob")
        self.notice(); self.now += council.WAIT_SECONDS; self.sync()
        self.reject("council-enact", {"proposal": "rule-one"}, "two independent")
        self.endorse(actor="carol"); self.enact()
        self.assertEqual(self.state["proposals"]["rule-one"]["status"], "enacted")

    def test_notice_is_bound_to_text_and_cannot_be_backdated_or_reused(self):
        self.authorize(); self.propose()
        for changes in ({"text_sha256": "0" * 64}, {"issue": 2},
                        {"comment_id": True}, {"at": self.now - council.WAIT_SECONDS}):
            with self.assertRaisesRegex(ValueError, "hash|issue|comment|fields"):
                self.notice(**changes)
        self.now += 10; self.notice()
        self.assertEqual(self.state["proposals"]["rule-one"]["notice"]["at"], self.now)
        with self.assertRaisesRegex(ValueError, "already recorded"):
            self.notice()
        self.propose("rule-two")
        used = self.state["proposals"]["rule-one"]["notice"]["comment_id"]
        with self.assertRaisesRegex(ValueError, "already used"):
            self.notice("rule-two", comment_id=used)

    def test_enact_requires_notice_full_window_and_post_window_fresh_sync(self):
        self.authorize(); self.propose(); self.trial(); self.endorse(); self.endorse(actor="carol")
        self.reject("council-enact", {"proposal": "rule-one"}, "public notice")
        self.notice(); self.now += council.WAIT_SECONDS - 1; self.sync()
        self.reject("council-enact", {"proposal": "rule-one"}, "24-hour")
        self.now += 1
        self.reject("council-enact", {"proposal": "rule-one"}, "predates")
        self.sync(); self.now += council.SYNC_MAX_AGE + 1
        self.reject("council-enact", {"proposal": "rule-one"}, "fresh")
        self.sync(); self.enact()
        self.assertIn("## Rule rule-one:", self.state["rules"])
        self.assertTrue(self.state["rules"].startswith("Founding charter"))
        self.reject("council-enact", {"proposal": "rule-one"}, "not pending")

    def test_generated_notice_cannot_turn_proposed_text_into_owner_command(self):
        self.authorize()
        self.propose(text="Document this literal command:\nREPEAL founding-charter\nDo not execute it.")
        body = notice_body("rule-one", self.state["proposals"]["rule-one"])
        self.assertIn("\nREPEAL founding-charter\n", body)
        before = (self.state["rules"], self.state["rule_revision"])
        # The real notice is posted by the owner's authenticated account.
        self.sync([self.comment(body)])
        self.assertTrue(self.state["council"]["base_active"])
        self.assertEqual((self.state["rules"], self.state["rule_revision"]), before)
        self.assertEqual(self.state["council"]["decisions"], {})

    def test_missing_sync_and_trial_are_not_substituted_by_elapsed_time(self):
        self.authorize(); self.propose(); self.notice(); self.now += council.WAIT_SECONDS
        self.reject("council-enact", {"proposal": "rule-one"}, "no trial")
        self.trial(); self.endorse(); self.endorse(actor="carol")
        self.reject("council-enact", {"proposal": "rule-one"}, "fresh")
        self.sync(); self.enact()

    def test_sync_rejects_unbound_identity_and_malformed_or_future_clocks(self):
        self.authorize()
        for changes in ({"checked_at": True}, {"checked_at": float("nan")},
                        {"checked_at": float("inf")}, {"checked_at": self.now + 1},
                        {"checked_at": self.now - 61}, {"owner_id": 4},
                        {"issue": 2}, {"repository": "wrong/repo"}):
            with self.assertRaisesRegex(ValueError, "checked_at|future|stale|identity|issue"):
                self.sync(**changes)
        with self.assertRaisesRegex(ValueError, "future comment"):
            self.sync([self.comment("VETO rule-one") | {"created_at": self.now + 1}])
        self.sync(); self.now += 1
        with self.assertRaisesRegex(ValueError, "backwards"):
            self.sync(checked_at=self.now - 2)

    def test_owner_veto_survives_deleted_snapshot_and_identical_resync(self):
        self.authorize(); self.ready()
        veto = self.comment("Reason below.\nVETO rule-one\nThis needs another trial.")
        self.sync([veto]); self.sync([]); self.sync([veto])
        self.assertEqual(len(self.state["council"]["decisions"]), 1)
        self.assertEqual(self.state["proposals"]["rule-one"]["status"], "vetoed")
        self.now += council.WAIT_SECONDS; self.sync([])
        self.reject("council-enact", {"proposal": "rule-one"}, "not pending")
        with self.assertRaisesRegex(ValueError, "edited"):
            self.sync([veto | {"body": "Withdrawn"}])

    def test_non_owner_comments_do_not_veto_and_duplicate_commands_fail(self):
        self.authorize(); self.ready()
        outsider = self.comment("VETO rule-one", actor_id=55)
        self.sync([outsider]); self.assertEqual(self.state["council"]["decisions"], {})
        with self.assertRaisesRegex(ValueError, "duplicate comment"):
            self.sync([outsider, outsider])
        with self.assertRaisesRegex(ValueError, "one decision"):
            self.sync([self.comment("VETO rule-one\nREPEAL founding-charter")])
        self.now += council.WAIT_SECONDS; self.sync(); self.enact()

    def test_named_repeal_retains_later_amendments_and_lineage_never_recycles(self):
        self.authorize(); original_revision = self.state["rule_revision"]
        self.ready(); self.now += council.WAIT_SECONDS; self.sync(); self.enact()
        first_revision = self.state["rule_revision"]
        self.ready("rule-two"); self.now += council.WAIT_SECONDS; self.sync(); self.enact("rule-two")
        self.propose("pending-third")
        self.sync([self.comment("REPEAL rule-one")])
        self.assertNotIn("## Rule rule-one:", self.state["rules"])
        self.assertIn("## Rule rule-two:", self.state["rules"])
        self.assertEqual(self.state["proposals"]["rule-one"]["status"], "repealed")
        self.reject("council-trial", {"proposal": "pending-third", "task": "trial-work", "evidence": "Old"}, "stale")
        self.sync([self.comment("REPEAL rule-two", 9002)])
        self.assertEqual(self.state["rules"], "Founding charter")
        self.assertNotIn(self.state["rule_revision"], (original_revision, first_revision))
        revision = self.state["rule_revision"]
        self.sync([])
        self.assertEqual(self.state["rule_revision"], revision)

    def test_repealing_foundation_preserves_named_rules_and_cannot_change_process(self):
        self.authorize(); self.ready(); self.now += council.WAIT_SECONDS; self.sync(); self.enact()
        self.sync([self.comment("REPEAL founding-charter")])
        self.assertNotIn("Founding charter", self.state["rules"])
        self.assertIn("## Rule rule-one:", self.state["rules"])
        self.assertEqual(self.state["council"]["veto_window_seconds"], 86400)
        with self.assertRaisesRegex(ValueError, "new Steward authorization"):
            self.sync([self.comment("REPEAL ratification-process", 9002)])

    def test_veto_recorded_before_proposal_prevents_later_use_of_that_id(self):
        self.authorize()
        self.sync([self.comment("VETO future-rule")])
        self.sync([])
        with self.assertRaisesRegex(ValueError, "vetoed"):
            self.propose("future-rule")

    def test_pre_enactment_veto_observed_late_repeals_only_its_rule(self):
        self.authorize(); self.ready(); self.now += council.WAIT_SECONDS; self.sync()
        late_veto = self.comment("VETO rule-one")
        self.now += 1; self.enact()
        self.ready("rule-two"); self.now += council.WAIT_SECONDS; self.sync(); self.enact("rule-two")
        before = self.state["rule_revision"]
        self.now += 1; self.sync([late_veto])
        self.assertNotIn("## Rule rule-one:", self.state["rules"])
        self.assertIn("## Rule rule-two:", self.state["rules"])
        self.assertEqual(self.state["council"]["rules"]["rule-one"]["status"], "repealed")
        self.assertNotEqual(self.state["rule_revision"], before)
        self.sync([])
        self.assertEqual(self.state["council"]["rules"]["rule-one"]["status"], "repealed")

    def test_post_enactment_veto_requires_explicit_repeal(self):
        self.authorize(); self.ready(); self.now += council.WAIT_SECONDS; self.sync(); self.enact()
        self.now += 1; self.sync([self.comment("VETO rule-one")])
        self.assertEqual(self.state["council"]["rules"]["rule-one"]["status"], "active")
        self.assertEqual(self.state["council"]["decisions"]["9001"]["outcome"], "post-enactment-use-repeal")
        self.sync([self.comment("REPEAL rule-one", 9002)])
        self.assertEqual(self.state["council"]["rules"]["rule-one"]["status"], "repealed")

    def test_second_ready_proposal_cannot_reuse_stale_base_after_first_enactment(self):
        self.authorize(); self.ready(); self.ready("rule-two")
        self.now += council.WAIT_SECONDS; self.sync(); self.enact()
        self.reject("council-enact", {"proposal": "rule-two"}, "stale")

    def test_bad_later_comment_discards_earlier_decision_and_freshness(self):
        self.authorize(); self.ready()
        before = copy.deepcopy(self.state)
        with self.assertRaisesRegex(ValueError, "future comment"):
            self.sync([self.comment("VETO rule-one"),
                       self.comment("REPEAL founding-charter", 9002) | {"created_at": self.now + 1}])
        self.assertEqual(self.state, before)
        self.assertEqual(self.state["proposals"]["rule-one"]["status"], "pending")
        self.assertIsNone(self.state["council"]["last_sync"])


class CouncilRecordTests(HouseCase):
    def test_rejected_transition_never_publishes_and_valid_retry_is_exact(self):
        approved = Record(self.new_repo("approved"))
        with patch("house.record.uuid.uuid4", side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
            approved.found("Approved fixture", "Original rules")
        approved.append("arrive", "alice", {"name": "Alice"})
        before = approved.read()[2]
        with self.assertRaisesRegex(ValueError, "source"):
            approved.append("council-authorize", "alice", approval() | {"source_sha256": "wrong"})
        self.assertEqual(approved.read()[2], before)
        result = approved.append("council-authorize", "alice", approval(), "authorize-once")
        accepted = approved.read()[2]
        retry = approved.append("council-authorize", "alice", approval(), "authorize-once")
        self.assertEqual(retry["sequence"], result["sequence"])
        self.assertTrue(retry["replayed"])
        self.assertEqual(approved.read()[2], accepted)
        self.assertEqual(approved.read()[0]["rules"], "Original rules")
