"""Lease fencing, durable cursors, and evidence-preserving lessons."""
import base64
import hashlib
from unittest.mock import patch

from tests.support import HouseCase


class LifecycleTests(HouseCase):
    def claim(self, actor="alice", token="first", expect=0):
        return self.record.append("claim", actor, {
            "task": "work", "token": token, "expect": expect, "seconds": 10})

    def completion(self, token):
        content = b"An immutable contribution\n"
        return {"task": "work", "token": token, "result": "Finished",
                "artifacts": {"result.txt": {"sha256": hashlib.sha256(content).hexdigest(),
                                            "base64": base64.b64encode(content).decode()}}}

    def test_expired_and_reclaimed_tokens_cannot_finish_renew_or_release(self):
        self.task()
        now = self.record.read()[0]["at"]
        with patch("house.record.time.time", return_value=now):
            self.claim()
        with patch("house.record.time.time", return_value=now + 11):
            self.rejected("finish", "alice", self.completion("first"), "expired")
            self.claim("bob", "second", 1)
            for op, data in (("finish", self.completion("first")),
                             ("renew", {"task": "work", "token": "first", "seconds": 10}),
                             ("release", {"task": "work", "token": "first", "note": "Late"})):
                with self.subTest(op=op):
                    self.rejected(op, "alice", data, "stale")
            self.record.append("finish", "bob", self.completion("second"))
        task = self.record.read()[0]["tasks"]["work"]
        self.assertEqual(task["status"], "done")
        self.assertEqual(task["artifacts"], self.completion("second")["artifacts"])

    def test_reused_token_cannot_revive_old_completion(self):
        self.task()
        now = self.record.read()[0]["at"]
        with patch("house.record.time.time", return_value=now):
            self.claim()
        with patch("house.record.time.time", return_value=now + 11):
            with self.assertRaisesRegex(ValueError, "token"):
                self.claim("alice", "first", 1)

    def test_long_sleep_catches_up_without_read_acknowledgement(self):
        through = self.record.read()[0]["sequence"]
        self.record.append("sleep", "alice", {"through": through, "note": "Returning later"})
        for i in range(20):
            self.record.append("say", "bob", {"text": f"While asleep {i}"})
        self.record.append("wake", "alice", {})
        page = self.cli("read", "--as", "alice", "--limit", "3")
        self.assertTrue(page["has_more"])
        self.assertEqual(page["through"], through + 3)
        self.assertEqual(len(page["events"]), 3)
        following = self.cli("read", "--as", "alice", "--after", str(page["through"]),
                             "--limit", "3")
        self.assertEqual(following["events"][0]["sequence"], page["through"] + 1)
        first = self.cli("read", "--as", "alice")
        second = self.cli("read", "--as", "alice")
        self.assertEqual(first, second)
        self.assertEqual([e["sequence"] for e in first["events"]],
                         list(range(through + 1, first["through"] + 1)))
        self.assertEqual(self.record.read()[0]["residents"]["alice"]["cursor"], through)
        self.rejected("sleep", "alice", {"through": first["through"] + 1, "note": "Unseen"},
                      "through")
        self.record.append("sleep", "alice", {"through": first["through"], "note": "Caught up"})
        self.rejected("sleep", "alice", {"through": through, "note": "Backwards"}, "backwards")

    def test_contradictions_require_explicit_supersession_and_fresh_review(self):
        for lesson, claim in (("old", "It is safe"), ("new", "It is unsafe")):
            self.record.append("learn", "alice", {"lesson": lesson, "key": "safety",
                               "claim": claim, "evidence": "Observed a reproduction"})
        lessons = self.record.read()[0]["lessons"]
        self.assertEqual({v["status"] for v in lessons.values()}, {"contested"})
        self.rejected("review", "bob", {"lesson": "new", "evidence": "Checked"}, "contradictions")
        self.record.append("supersede", "bob", {"old": "old", "new": "new",
                           "evidence": "The old observation missed a boundary"})
        self.rejected("review", "alice", {"lesson": "new", "evidence": "Myself"}, "independent")
        self.record.append("review", "bob", {"lesson": "new", "evidence": "Independent check"})
        lessons = self.record.read()[0]["lessons"]
        self.assertEqual(lessons["old"]["status"], "superseded")
        self.assertEqual(lessons["old"]["replaced_by"], "new")
        self.assertEqual(lessons["old"]["claim"], "It is safe")
        self.assertEqual(lessons["new"]["reviews"], ["bob"])
