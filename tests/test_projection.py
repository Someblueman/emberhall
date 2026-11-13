"""Disposable projection ownership must not leak failed or caller-owned mutations."""
import base64
import hashlib

from tests.support import HouseCase


class ProjectionTests(HouseCase):
    def claim(self, seconds=60):
        return self.record.append("claim", "alice", {
            "task": "work", "expect": 0, "token": "fresh-token", "seconds": seconds})

    def completion(self):
        content = b"Independent immutable evidence"
        return {"task": "work", "token": "fresh-token", "result": "Done",
                "artifacts": {"result.txt": {"sha256": hashlib.sha256(content).hexdigest(),
                                            "base64": base64.b64encode(content).decode()}}}

    def test_rejected_claim_does_not_consume_its_token(self):
        self.task()
        before = self.record.read()
        with self.assertRaisesRegex(ValueError, "seconds"):
            self.claim(seconds=0)
        self.assertEqual(self.record.read(), before)
        self.claim()
        self.assertEqual(self.record.read()[0]["tasks"]["work"]["used_tokens"], ["fresh-token"])

    def test_rejected_release_does_not_remove_the_live_lease(self):
        self.task()
        self.claim()
        before = self.record.read()
        with self.assertRaisesRegex(ValueError, "note"):
            self.record.append("release", "alice", {
                "task": "work", "token": "fresh-token", "note": ""})
        self.assertEqual(self.record.read(), before)
        self.record.append("finish", "alice", self.completion())
        self.assertEqual(self.record.read()[0]["tasks"]["work"]["status"], "done")

    def test_artifact_projection_and_event_history_do_not_alias(self):
        self.task()
        self.claim()
        original = self.completion()["artifacts"]["result.txt"]
        self.record.append("finish", "alice", self.completion())
        self.record.append("say", "bob", {"text": "An event after completion"})
        state, events, _ = self.record.read()
        saved = next(e for e in events if e["op"] == "finish")["data"]["artifacts"]["result.txt"]
        projected = state["tasks"]["work"]["artifacts"]["result.txt"]
        projected["base64"] = "changed locally"
        self.assertEqual(saved, original)
        saved["sha256"] = "changed separately"
        self.assertEqual(projected["sha256"], original["sha256"])
        self.assertEqual(self.record.read()[0]["tasks"]["work"]["artifacts"]["result.txt"], original)
