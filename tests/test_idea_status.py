"""Complete idea reads through the CLI and the existing fixed mailbox route."""
import copy
import json
import unittest

from house import mailbox
from house.idea_status import idea_status
from tests.support import HouseCase
from tests.test_mailbox import MailboxCase
from tests.test_shelf import idea
from tests import test_who_asked


class IdeaStatusTests(unittest.TestCase):
    def setUp(self):
        self.current = {"author": "bob", "brief": 20, "sequence": 21,
                        "finding": "Opened the complete evidence.", "kind": "codex", "at": 1}
        self.old = self.current | {"brief": 10, "sequence": 11}
        self.entry = {"author": "alice", "status": "shelved", "title": "An idea",
            "sources": ["https://example.org/a", "https://example.org/b"],
            "brief": {"sequence": 20, "author": "alice", "reach": "All readers",
                      "asked": [{"who": "A reader", "where": "https://example.org/a",
                                 "said": "Preserve this exact quote: α\n  indented."}]},
            "seconds": [self.old, self.current],
            "second": {key: value for key, value in self.current.items() if key != "kind"},
            "history": [{"choice": "earlier", "won": False}]}
        self.state = {"house_id": "fixture", "name": "Fixture", "sequence": 30,
                      "residents": {"alice": {}, "bob": {}, "carol": {}},
                      "shelf": {"ideas": {"an-idea": self.entry}}}

    def test_complete_record_exact_evidence_and_current_check(self):
        before = copy.deepcopy(self.state)
        reply = idea_status(self.state, "head", "an-idea", "bob")
        self.assertEqual(reply["idea"], self.entry)
        self.assertEqual(json.loads(json.dumps(reply))["idea"], self.entry)
        self.assertEqual(reply["source"], {"journal_head": "head", "sequence": 30})
        self.assertEqual(reply["brief_revision"], 20)
        self.assertEqual(reply["caller"]["current_checks"], [self.current])
        self.assertEqual(reply["caller"]["earlier_checks"], [self.old])
        self.assertTrue(reply["caller"]["checked_current_brief"])
        self.assertEqual(self.state, before)

    def test_rewrite_makes_prior_checks_stale_and_keeps_their_evidence(self):
        self.entry["brief"] = self.entry["brief"] | {"sequence": 31, "author": "carol"}
        self.entry["brief"]["asked"][0]["said"] = "A revised exact quote."
        self.state["sequence"] = 31
        reply = idea_status(self.state, "changed-head", "an-idea", "bob")
        self.assertEqual(reply["brief_revision"], 31)
        self.assertFalse(reply["caller"]["checked_current_brief"])
        self.assertEqual(reply["caller"]["current_checks"], [])
        self.assertEqual(reply["caller"]["earlier_checks"], [self.old, self.current])
        self.assertEqual(reply["idea"], self.entry)
        author = idea_status(self.state, "changed-head", "an-idea", "carol")["caller"]
        self.assertTrue(author["authored_current_brief"])
        self.assertFalse(author["authored_idea"])

    def test_older_unbriefed_and_retired_ideas_remain_readable(self):
        del self.entry["seconds"]
        self.assertEqual(idea_status(self.state, "h", "an-idea", "bob")
                         ["caller"]["current_checks"], [self.entry["second"]])
        del self.entry["brief"]
        self.entry["status"] = "graveyard"
        reply = idea_status(self.state, "h", "an-idea", "bob")
        self.assertIsNone(reply["brief_revision"])
        self.assertFalse(reply["caller"]["checked_current_brief"])
        self.assertEqual(reply["idea"], self.entry)
        self.assertEqual(reply["caller"]["earlier_checks"], [self.entry["second"]])

    def test_shelf_reducer_rewrite_invalidates_the_recorded_check(self):
        fixture = test_who_asked.WhoAskedTests()
        fixture.setUp()
        fixture.install()
        fixture.publish([test_who_asked.asked_idea(k) for k in ("a", "b")])
        f = fixture.f
        f.send("idea-second", actor="v1", idea="a", verdict="keep", finding=test_who_asked.PART)
        def read():
            return idea_status(f.state | {"house_id": "fixture", "name": "Fixture"},
                               "fixture-head", "a", "v1")
        first = read()
        self.assertTrue(first["caller"]["checked_current_brief"])
        f.send("idea-brief", actor="v2", idea="a", brief=test_who_asked.grounded_brief())
        changed = read()
        self.assertNotEqual(first["brief_revision"], changed["brief_revision"])
        self.assertFalse(changed["caller"]["checked_current_brief"])
        self.assertEqual(changed["caller"]["earlier_checks"], first["caller"]["current_checks"])
        self.assertEqual(changed["idea"], f.state["shelf"]["ideas"]["a"])


def publish(record, actor):
    record.append("life", actor, {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"})
    record.append("shelf", actor, {"kind": "explore-start", "round": "round",
                                  "expect": 0, "token": "token", "seconds": 300})
    record.append("shelf", actor, {"kind": "explore-publish", "round": "round",
        "token": "token", "ideas": [idea(name) for name in ("alpha", "beta")]})


class IdeaStatusCLITests(HouseCase):
    def test_cli_exact_record_and_errors_are_read_only(self):
        publish(self.record, "alice")
        before = self.record.read()
        reply = self.cli("status", "--idea", "alpha", "--as", "bob")
        self.assertEqual(reply["idea"], before[0]["shelf"]["ideas"]["alpha"])
        self.assertEqual(reply["source"]["journal_head"], before[2])
        self.assertFalse(reply["caller"]["checked_current_brief"])
        for tail in (("--idea", "missing", "--as", "bob"), ("--idea", "alpha"),
                     ("--idea", "alpha", "--as", "unknown"), ("--as", "bob"),
                     ("--idea", "alpha", "--as", "bob", "--tasks"),
                     ("--idea", "alpha", "--as", "bob", "--limit", "1"),
                     ("--idea", "alpha", "--as", "bob", "--offset", "0")):
            self.cli("status", *tail, success=False)
        self.assertEqual(self.record.read(), before)
        self.assertIn("tasks", self.cli("status"))
        self.assertIn("page", self.cli("status", "--tasks"))


class IdeaStatusMailboxTests(MailboxCase):
    def test_fixed_client_identity_and_snapshot_without_acknowledgement(self):
        self.arrive()
        publish(self.record, "alice")
        before = self.record.read()
        reply = self.call("status", "--idea", "alpha", "--as", self.resident)
        self.assertEqual(reply["idea"], before[0]["shelf"]["ideas"]["alpha"])
        self.assertEqual(reply["caller"]["resident"], self.resident)
        with self.assertRaisesRegex(ValueError, "another resident"):
            mailbox.parse(["status", "--idea", "alpha", "--as", "bob"],
                          self.repo, self.workspace, self.resident)
        self.collect(self.start("status", "--idea", "missing", "--as", self.resident),
                     success=False)
        self.collect(self.start("status", "--idea", "alpha"), success=False)
        self.assertEqual(self.record.read(), before)
        self.assertIn("page", self.call("status", "--tasks"))
