"""Lesson evidence uses the same immutable envelope as finished work."""
import base64
import copy
import hashlib

from house.__main__ import briefing, parser, run
from house.custodian import handle, read_page
from tests.support import HouseCase


def envelope(content=b'print(6 * 7)\n'):
    return {"sha256": hashlib.sha256(content).hexdigest(),
            "base64": base64.b64encode(content).decode()}


class LessonArtifactTests(HouseCase):
    def lesson(self, **changes):
        return dict(lesson="proof", key="answer", claim="The answer is 42",
                    evidence="Run the attached checker", **changes)

    def test_text_only_historical_shape_and_review_are_unchanged(self):
        self.record.append("learn", "alice", self.lesson())
        self.record.append("review", "bob", {"lesson": "proof", "evidence": "Checked"})
        lesson = self.record.read()[0]["lessons"]["proof"]
        self.assertNotIn("artifacts", lesson)
        self.assertEqual(lesson["status"], "observed")
        self.assertEqual(lesson["reviews"], ["bob"])

    def test_cli_copies_from_fixed_source_and_normal_reads_only_show_hashes(self):
        room = self.root / "room"
        room.mkdir()
        checker = room / "check.py"
        checker.write_bytes(b'print(6 * 7)\n')
        args = parser().parse_args(["--repo", str(self.repo), "--artifacts-from", str(room),
            "learn", "--as", "alice", "--lesson", "proof", "--key", "answer",
            "--claim", "The answer is 42", "--evidence", "Run checker",
            "--artifact", "check.py"])
        run(args)
        checker.write_text("changed")
        state, events, _ = self.record.read()
        self.assertEqual(state["lessons"]["proof"]["artifacts"], {"check.py": envelope()})
        summary = briefing(state)["lessons"]["proof"]["artifacts"]
        self.assertEqual(summary, {"check.py": {"sha256": envelope()["sha256"]}})
        page = read_page(state, events, "bob", {"after": 0, "limit": 20})
        self.assertEqual(page["events"][-1]["data"]["artifacts"], summary)
        self.assertEqual(self.cli("read", "--as", "bob", "--after", "0")
                         ["events"][-1]["data"]["artifacts"], summary)

    def test_cli_without_artifacts_retains_old_event_shape(self):
        self.cli("learn", "--as", "alice", "--lesson", "proof", "--key", "answer",
                 "--claim", "42", "--evidence", "text")
        self.assertNotIn("artifacts", self.record.read()[1][-1]["data"])
        self.assertNotIn("artifact", self.record.read()[1][-1]["data"])

    def test_malformed_envelopes_are_rejected_without_journal_changes(self):
        good = envelope()
        bad = [{}, [], {"../escape": good}, {"/absolute": good}, {"a//b": good},
               {"a\\b": good}, {"check.py": {"sha256": "bad", "base64": good["base64"]}},
               {"check.py": good | {"base64": "!"}}, {"check.py": good | {"extra": 1}},
               {"check.py": envelope(b'x' * 1000001)},
               {str(i): good for i in range(33)}]
        for artifacts in bad:
            with self.subTest(paths=str(list(artifacts)[:2])):
                self.rejected("learn", "alice", self.lesson(artifacts=artifacts),
                              "artifact|base64")

    def test_maximum_file_and_count_are_accepted(self):
        artifacts = {str(i): envelope(b'x' * 1000000 if i == 0 else b'') for i in range(32)}
        self.record.append("learn", "alice", self.lesson(artifacts=artifacts))
        self.assertEqual(self.record.read()[0]["lessons"]["proof"]["artifacts"], artifacts)

    def test_source_links_and_traversal_are_rejected(self):
        outside = self.root / "outside"
        outside.write_text("private")
        (self.repo / "link").symlink_to(outside)
        for name in ["link", "../outside"]:
            with self.subTest(name=name):
                head = self.record.read()[2]
                self.cli("learn", "--as", "alice", "--lesson", "proof", "--key", "answer",
                         "--claim", "42", "--evidence", "text", "--artifact", name, success=False)
                self.assertEqual(self.record.read()[2], head)

    def test_custodian_accepts_optional_artifacts_and_rejects_unknown_fields(self):
        request = {"version": 1, "house": self.foundation["house_id"], "resident": "alice",
                   "request": "learn-proof", "action": "append", "data": {
                       "operation": "learn", "body": self.lesson(artifacts={"check.py": envelope()})}}
        handle(self.record, self.foundation["anchor"], "alice", request)
        self.assertEqual(self.record.read()[0]["lessons"]["proof"]["artifacts"]["check.py"], envelope())
        request = copy.deepcopy(request)
        request["request"] = "bad-fields"
        request["data"]["body"]["unknown"] = True
        with self.assertRaisesRegex(ValueError, "invalid fields"):
            handle(self.record, self.foundation["anchor"], "alice", request)
