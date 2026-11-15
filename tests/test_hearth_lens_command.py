"""House-first and fixed-mailbox command coverage for Hearth Lens."""

from house import mailbox
from tests.test_mailbox import MailboxCase
from tests.support import HouseCase


class HearthLensCommandTests(HouseCase):
    def test_real_house_command_uses_verified_snapshot_and_bounds_rows(self):
        self.task()
        before = self.record.read()

        result = self.cli("lens", "--task", "work", "--limit", "1")

        self.assertEqual(result["selector"], {"task": "work"})
        self.assertEqual(result["source"]["journal_head"], before[2])
        self.assertEqual(result["page"]["shown"], 1)
        self.assertEqual(result["events"][0]["sequence"], 4)
        self.assertIn("does not acknowledge", " ".join(result["limitations"]))
        self.assertEqual(self.record.read(), before)

    def test_real_house_command_rejects_invalid_bounds_without_writing(self):
        before = self.record.read()
        for tail in (("--task", "work", "--limit", "0"),
                     ("--resident", "alice", "--before", "0"),
                     ("--task", "", "--limit", "1")):
            self.cli("lens", *tail, success=False)
        self.assertEqual(self.record.read(), before)


class HearthLensMailboxTests(MailboxCase):
    def test_fixed_native_channel_traces_without_cursor_or_journal_changes(self):
        self.arrive()
        self.record.append("task", "alice", {
            "task": "native-work", "title": "Native work", "description": "Fixture"})
        before = self.record.read()

        answer = self.call("lens", "--task", "native-work", "--limit", "1")

        self.assertEqual(answer["selector"], {"task": "native-work"})
        self.assertEqual(answer["source"]["journal_head"], before[2])
        task_sequence = next(sequence for sequence, event in enumerate(before[1], 1)
                             if event["op"] == "task" and event["data"]["task"] == "native-work")
        self.assertEqual(answer["events"][0]["sequence"], task_sequence)
        self.assertEqual(self.record.read(), before)
        self.assertFalse((self.workspace / "house").exists())

    def test_mailbox_allows_lens_but_still_pins_its_repository(self):
        self.arrive()
        before = self.record.read()
        with self.assertRaisesRegex(ValueError, "cannot override"):
            mailbox.parse(["lens", "--task", "work", "--repo", str(self.repo)],
                          self.repo, self.workspace, self.resident)
        parsed = mailbox.parse(["lens", "--resident", self.resident, "--limit", "1"],
                               self.repo, self.workspace, self.resident)
        self.assertEqual(parsed.command, "lens")
        self.assertEqual(self.record.read(), before)
