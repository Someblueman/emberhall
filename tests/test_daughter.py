"""The door to Reedbank: one supervised wake in the daughter house, and nothing wider."""
import argparse
import base64
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from house import daughter, mailbox, mailbox_jobs, renovation, resident_actions
from house.record import ANCHOR, REF, Record
from tests.test_mailbox import MailboxCase

SOURCE = Path(__file__).resolve().parents[1]
CHECKPOINT = (SOURCE / daughter.BUNDLE).read_bytes()


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout.decode().strip()


def door(*argv):
    root = argparse.ArgumentParser(allow_abbrev=False)
    daughter.arguments(root)
    return root.parse_args(list(argv))


class DoorCase(unittest.TestCase):
    """A stand-in Emberhall checkout that has the real Reedbank checkpoint committed."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name).resolve() / "emberhall"
        self.repo.mkdir()
        git(self.repo, "init", "--quiet")
        self.commit(CHECKPOINT)
        self.record = Record(self.repo)
        self.base = daughter.home(self.record)

    def commit(self, raw):
        target = self.repo / daughter.BUNDLE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        git(self.repo, "add", daughter.BUNDLE)
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "--quiet", "-m", "checkpoint")

    def act(self, *argv, resident="rook", run="run-a", request="r1"):
        return daughter.act(self.record, resident, run, door(*argv), request)

    def reedbank(self):
        return Record(self.base / "house").read()


class ConstantTests(unittest.TestCase):
    def test_only_the_steward_can_change_the_door(self):
        self.assertIn("house/daughter.py", renovation.STEWARD_ONLY)

    def test_the_steward_allowed_one_wake(self):
        self.assertEqual(1, daughter.WAKES)

    def test_the_committed_checkpoint_is_the_pinned_one(self):
        self.assertEqual(daughter.BUNDLE_SHA256, hashlib.sha256(CHECKPOINT).hexdigest())

    def test_the_grammar_has_no_file_or_root_option(self):
        for argv in (["status", "--repo", "x"], ["say", "hi", "--artifacts-from", "x"], ["finish"], ["propose"],
                     ["ratify"], ["task"], ["claim"], ["restore", "x"], ["adopt", "x"], ["say", "hi", "--file", "x"],
                     ["arrive", "--na", "Wren"], ["read", "--aft", "1"], ["sleep", "--thr", "1", "--note", "n"]):
            with self.assertRaises(SystemExit, msg=argv), patch("sys.stderr"):
                door(*argv)


class OpeningTests(DoorCase):
    def test_first_use_restores_the_recorded_nineteen_events(self):
        status = self.act("status")
        self.assertEqual((daughter.NAME, daughter.IDENTITY, 19, daughter.START_HEAD),
                         (status["house"], status["identity"], status["events"], status["head"]))
        self.assertEqual("sealed", status["governance"])
        self.assertIn("Reedbank is a separate disposable daughter house", status["charter"])
        self.assertEqual({"allowed": 1, "used": 0, "wakes": []}, status["wake"])
        self.assertTrue(all(not item["awake"] for item in status["residents"].values()))
        self.assertIn("reedbank-checkpoint-recovery-v1", status["lessons"])

    def test_looking_changes_neither_house(self):
        self.act("status")
        before = git(self.repo, "for-each-ref"), git(self.base / "house", "for-each-ref")
        self.act("status"); self.act("read"); self.act("bundle")
        self.assertEqual(before, (git(self.repo, "for-each-ref"), git(self.base / "house", "for-each-ref")),
                         "neither house's refs moved")
        self.assertEqual((19, daughter.START_HEAD), (self.reedbank()[0]["sequence"], self.reedbank()[2]))
        self.assertFalse((self.base / "wakes.json").exists(), "looking notes no wake")

    def test_a_changed_checkpoint_is_refused_and_nothing_is_created(self):
        self.commit(CHECKPOINT + b"x")
        with self.assertRaisesRegex(ValueError, "not the reviewed one"):
            self.act("status")
        self.assertFalse((self.base / "house").exists())

    def test_another_houses_journal_in_its_place_is_refused(self):
        self.act("status")
        other = Record(self.base / "house")
        with patch.object(daughter, "IDENTITY", "someone-else"):
            with self.assertRaisesRegex(ValueError, "not Reedbank's"):
                self.act("status")
        git(other.root, "update-ref", ANCHOR, git(other.root, "rev-parse", REF))
        with self.assertRaisesRegex(ValueError, "not Reedbank's foundation"):
            self.act("status")

    def test_read_pages_the_journal_within_bounds(self):
        page = self.act("read", "--after", "17", "--limit", "5")
        self.assertEqual(([18, 19], 19, False), ([e["sequence"] for e in page["events"]], page["latest"], page["has_more"]))
        self.assertTrue(self.act("read", "--limit", "3")["has_more"])
        for argv in (["read", "--after", "20"], ["read", "--after", "-1"], ["read", "--limit", "0"], ["read", "--limit", "51"]):
            with self.assertRaises(ValueError, msg=argv):
                self.act(*argv)

    def test_the_bundle_restores_to_the_same_journal(self):
        self.act("arrive", "--name", "Wren")
        out = self.act("bundle")
        raw = base64.b64decode(out["base64"])
        self.assertEqual((out["sha256"], out["bytes"]), (hashlib.sha256(raw).hexdigest(), len(raw)))
        fresh = Path(self.temporary.name) / "fresh"
        fresh.mkdir(); git(fresh, "init", "--quiet")
        (fresh / "b.bundle").write_bytes(raw)
        restored = Record(fresh).restore(str(fresh / "b.bundle"), daughter.FOUNDATION)
        self.assertEqual((21, out["head"]), (restored["events"], restored["head"]))


class WakeTests(DoorCase):
    def test_arriving_adds_a_new_reedbank_identity_and_the_doors_note(self):
        before = git(self.repo, "for-each-ref")
        out = self.act("arrive", "--name", "Wren")
        state, events, _ = self.reedbank()
        visitor = out["you_are"]
        self.assertRegex(visitor, r"^wren-[0-9a-f]{10}$")
        self.assertEqual((21, 20, 21), (state["sequence"], out["arrive_sequence"], out["door_note_sequence"]))
        self.assertEqual({"name": "Wren", "awake": True}, {k: state["residents"][visitor][k] for k in ("name", "awake")})
        self.assertEqual(("say", visitor), (events[20]["op"], events[20]["actor"]))
        note = events[20]["data"]["text"]
        self.assertIn("run run-a", note); self.assertIn("Supervised wake 1 of 1", note)
        self.assertIn("not written by the resident", note)
        self.assertNotIn("rook", note, "no Emberhall identity is carried into Reedbank")
        self.assertEqual(state["rules"], out["charter"])
        self.assertEqual("", state["owner_key"], "governance stays sealed")
        self.assertEqual(before, git(self.repo, "for-each-ref"), "Emberhall's refs are untouched")
        self.assertEqual(1, self.act("status")["wake"]["used"])

    def test_the_one_wake_cannot_be_taken_twice(self):
        first = self.act("arrive", "--name", "Wren")
        for run in ("run-a", "run-b"):
            with self.assertRaisesRegex(ValueError, "has been used.*needs the Steward"):
                self.act("arrive", "--name", "Lark", resident="heron", run=run)
        # The same resident asking again, even from a later run, is shown the wake it already has; no second one.
        again = self.act("arrive", "--name", "Lark", run="run-c")
        self.assertEqual((first["you_are"], "Wren", 1), (again["you_are"], again["name"], self.act("status")["wake"]["used"]))
        with self.assertRaisesRegex(ValueError, "only the run that arrived"):
            self.act("say", "from the later run", run="run-c")
        self.assertEqual(21, self.reedbank()[0]["sequence"])

    def test_it_stays_used_after_the_visitor_sleeps(self):
        self.act("arrive", "--name", "Wren")
        self.act("sleep", "--through", "21", "--note", "handoff", request="s")
        with self.assertRaisesRegex(ValueError, "has been used"):
            self.act("arrive", "--name", "Lark", resident="heron", run="run-b")

    def test_asking_to_arrive_again_from_the_same_run_changes_nothing(self):
        first = self.act("arrive", "--name", "Wren")
        again = self.act("arrive", "--name", "Other name", request="r2")
        self.assertEqual((first["you_are"], 21), (again["you_are"], self.reedbank()[0]["sequence"]))
        self.assertEqual((2, True), tuple(self.act("status")["wake"]["wakes"][0][key] for key in ("writes", "awake")))

    def test_a_bad_name_is_refused_and_the_wake_is_not_spent(self):
        for name in ("", " Wren", "Wren\n", "9lives", "x" * 41, "Wren;rm", "../x"):
            with self.assertRaises(ValueError, msg=name):
                self.act("arrive", "--name", name)
        self.assertEqual(0, self.act("status")["wake"]["used"])
        self.act("arrive", "--name", "Mary-Ann O'Wren")

    def test_an_arrival_reedbank_refuses_does_not_spend_the_wake(self):
        self.act("status")
        with patch.object(Record, "append", side_effect=ValueError("refused")):
            with self.assertRaisesRegex(ValueError, "refused"):
                self.act("arrive", "--name", "Wren")
        self.assertEqual(0, self.act("status")["wake"]["used"])
        self.assertEqual(19, self.reedbank()[0]["sequence"])

    def test_an_arrival_cut_short_is_finished_by_asking_again(self):
        self.act("status")
        real = Record.append
        calls = []

        def once(record, op, *rest):
            calls.append(op)
            if op == "say":
                raise OSError("power cut")
            return real(record, op, *rest)
        with patch.object(Record, "append", once):
            with self.assertRaises(OSError):
                self.act("arrive", "--name", "Wren")
        self.assertEqual((20, 1), (self.reedbank()[0]["sequence"], self.act("status")["wake"]["used"]))
        out = self.act("arrive", "--name", "Wren", request="r2")
        self.assertEqual((20, 21, 21), (out["arrive_sequence"], out["door_note_sequence"], self.reedbank()[0]["sequence"]))

    def test_nobody_arrives_while_someone_is_awake_there(self):
        self.act("status")
        Record(self.base / "house").append("wake", "osier-61464e3b88", {})
        with self.assertRaisesRegex(ValueError, "already awake"):
            self.act("arrive", "--name", "Wren")
        self.assertEqual(0, self.act("status")["wake"]["used"])

    def test_a_damaged_wake_record_stops_arrivals(self):
        self.act("status")
        for damage in ('{"wakes": "none"}', "not json", '{"wakes": [{"number": "1"}]}'):
            (self.base / "wakes.json").write_text(damage)
            with self.assertRaisesRegex(ValueError, "disagree"):
                self.act("arrive", "--name", "Wren")
        self.assertEqual(19, self.reedbank()[0]["sequence"])

    def test_a_wake_noted_but_never_arrived_did_not_happen(self):
        # The worker dies after noting whose wake it is and before Reedbank's journal changes; that run never returns.
        self.act("status")
        with patch.object(Record, "append", side_effect=OSError("killed")):
            with self.assertRaises(OSError):
                self.act("arrive", "--name", "Wren")
        self.assertEqual((19, 0), (self.reedbank()[0]["sequence"], self.act("status")["wake"]["used"]))
        out = self.act("arrive", "--name", "Lark", resident="heron", run="run-b")
        self.assertRegex(out["you_are"], r"^lark-")
        state = self.reedbank()[0]
        self.assertEqual((21, 1), (state["sequence"], self.act("status")["wake"]["used"]))
        self.assertFalse(any(key.startswith("wren-") for key in state["residents"]))
        with self.assertRaisesRegex(ValueError, "has been used: Lark"):
            self.act("arrive", "--name", "Wren", run="run-c")

    def test_an_arrival_the_file_cannot_explain_stops_the_door_but_not_looking(self):
        self.act("arrive", "--name", "Wren")
        (self.base / "wakes.json").unlink()     # as after a power cut that lost the note
        for argv, who in ((["arrive", "--name", "Lark"], ("heron", "run-b")), (["say", "hi"], ("rook", "run-a"))):
            with self.assertRaisesRegex(ValueError, "disagree"):
                self.act(*argv, resident=who[0], run=who[1])
        self.assertEqual(21, self.reedbank()[0]["sequence"])
        status = self.act("status")
        self.assertIn("disagree", status["wake"]["problem"])
        self.assertEqual(21, self.act("read")["latest"])


class WritingTests(DoorCase):
    def setUp(self):
        super().setUp()
        self.visitor = self.act("arrive", "--name", "Wren")["you_are"]

    def test_the_visitor_speaks_learns_and_reviews_by_reedbanks_rules(self):
        said = self.act("say", "I read the checkpoint lesson.", request="a")
        self.act("learn", "--lesson", "wake-lesson-v1", "--key", "supervised-wake", "--claim", "A claim.",
                 "--evidence", "Events 20 to 22.", request="b")
        self.act("review", "reedbank-checkpoint-recovery-v1", "--evidence", "Read the frozen artifacts.", request="c")
        state, events, _ = self.reedbank()
        self.assertEqual((22, 24), (said["sequence"], state["sequence"]))
        self.assertEqual({self.visitor}, {event["actor"] for event in events[19:]})
        self.assertEqual(self.visitor, state["lessons"]["wake-lesson-v1"]["author"])
        self.assertIn(self.visitor, state["lessons"]["reedbank-checkpoint-recovery-v1"]["reviews"])
        with self.assertRaises(ValueError, msg="Reedbank forbids reviewing your own lesson"):
            self.act("review", "wake-lesson-v1", "--evidence", "mine", request="d")

    def test_a_repeated_request_is_replayed_not_written_twice(self):
        first = self.act("say", "once", request="same")
        again = self.act("say", "once", request="same")
        self.assertEqual((first["sequence"], True, 22), (again["sequence"], again["replayed"], self.reedbank()[0]["sequence"]))
        self.assertEqual(first["writes_left"], again["writes_left"])

    def test_only_the_arriving_run_writes(self):
        for resident, run in (("rook", "run-later"), ("heron", "run-a"), ("heron", "run-b")):
            with self.assertRaisesRegex(ValueError, "only the run that arrived"):
                self.act("say", "hello", resident=resident, run=run, request="x")
        self.assertEqual(21, self.reedbank()[0]["sequence"])

    def test_the_same_resident_may_hand_off_from_a_later_run_but_nobody_else(self):
        with self.assertRaisesRegex(ValueError, "only the run that arrived"):
            self.act("sleep", "--through", "21", "--note", "n", resident="heron", run="run-b", request="s0")
        out = self.act("sleep", "--through", "21", "--note", "Read all 21; next visitor: review the lesson.",
                       run="run-later", request="s1")
        state = self.reedbank()[0]
        self.assertTrue(out["slept"])
        self.assertEqual((False, 21), (state["residents"][self.visitor]["awake"], state["residents"][self.visitor]["cursor"]))
        self.assertFalse(self.act("status")["wake"]["wakes"][0]["awake"])

    def test_after_sleeping_the_wake_is_over(self):
        self.act("sleep", "--through", "21", "--note", "done", request="s")
        for argv in (["say", "more"], ["sleep", "--through", "22", "--note", "again"]):
            with self.assertRaisesRegex(ValueError, "has slept"):
                self.act(*argv, request="after-" + argv[0])
        self.assertEqual(22, self.reedbank()[0]["sequence"])

    def test_sleep_names_an_event_that_exists(self):
        for through in ("22", "-1"):
            with self.assertRaisesRegex(ValueError, "last Reedbank event you read"):
                self.act("sleep", "--through", through, "--note", "n", request="s" + through)

    def test_a_wake_adds_a_bounded_number_of_entries_and_the_last_is_always_the_handoff(self):
        with patch.object(daughter, "WRITES", 4):
            self.assertEqual(1, self.act("say", "three", request="3")["writes_left"])
            for number, argv in enumerate((["say", "four"], ["review", "reedbank-checkpoint-recovery-v1", "--evidence", "e"],
                                           ["learn", "--lesson", "l", "--key", "k", "--claim", "c", "--evidence", "e"])):
                with self.assertRaisesRegex(ValueError, "one entry remains, for sleep"):
                    self.act(*argv, request=f"over-{number}")
            self.assertEqual(22, self.act("say", "three", request="3")["sequence"], "a replay is still answered")
            out = self.act("sleep", "--through", "22", "--note", "handoff", request="s")
        self.assertEqual((True, 0, 23), (out["slept"], out["writes_left"], self.reedbank()[0]["sequence"]))
        self.assertFalse(self.reedbank()[0]["residents"][self.visitor]["awake"])

    def test_a_write_that_landed_before_a_crash_still_counts(self):
        real = daughter.written
        with patch.object(daughter, "WRITES", 4):
            # The reply to this write is lost after Reedbank's journal took it.
            with patch.object(daughter, "written", side_effect=[real(self.reedbank()[1], self.visitor), OSError("killed")]):
                with self.assertRaises(OSError):
                    self.act("say", "landed", request="lost")
            self.assertEqual(22, self.reedbank()[0]["sequence"])
            with self.assertRaisesRegex(ValueError, "one entry remains"):
                self.act("say", "one more", request="next")

    def test_nothing_is_written_after_the_journal_says_asleep_even_if_the_note_was_lost(self):
        with patch.object(daughter, "save", side_effect=OSError("killed")):
            with self.assertRaises(OSError):
                self.act("sleep", "--through", "21", "--note", "handoff", request="s")
        self.assertFalse(self.reedbank()[0]["residents"][self.visitor]["awake"], "the sleep reached the journal")
        for argv in (["say", "after"], ["learn", "--lesson", "l", "--key", "k", "--claim", "c", "--evidence", "e"],
                     ["sleep", "--through", "22", "--note", "again"]):
            with self.assertRaisesRegex(ValueError, "has slept"):
                self.act(*argv, request="after-" + argv[0])
        self.assertEqual(22, self.reedbank()[0]["sequence"])
        self.assertTrue(self.act("sleep", "--through", "21", "--note", "handoff", request="s")["replayed"])
        with self.assertRaisesRegex(ValueError, "has been used"):
            self.act("arrive", "--name", "Lark", resident="heron", run="run-b")

    def test_text_is_bounded_and_ids_are_plain(self):
        cases = (["say", "x" * 4001], ["say", "  "], ["say", "a\x00b"], ["say", "red \x1b[31m text"],
                 ["say", "over\u202eride"], ["say", "lone \ud800 half"], ["sleep", "--through", "21", "--note", "a\rb"],
                 ["learn", "--lesson", "Bad Id", "--key", "k", "--claim", "c", "--evidence", "e"],
                 ["learn", "--lesson", "ok", "--key", "k" * 101, "--claim", "c", "--evidence", "e"],
                 ["sleep", "--through", "21", "--note", "n" * 4001])
        for number, argv in enumerate(cases):
            with self.assertRaises(ValueError, msg=argv):
                self.act(*argv, request=f"bad-{number}")
        self.assertEqual(21, self.reedbank()[0]["sequence"])
        self.assertEqual(22, self.act("say", "Two lines\nand a\ttab are plain text.", request="ok")["sequence"])


class ChannelTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.arrive()
        patcher = patch.object(daughter, "checkpoint", return_value=CHECKPOINT)
        patcher.start(); self.addCleanup(patcher.stop)

    def argv(self, *rest, request="door-1"):
        return ["reedbank", "--as", self.resident, "--request", request, *rest]

    def execute(self, *rest, request="door-1"):
        return resident_actions.execute(self.record, self.workspace, self.resident, self.run,
                                        self.argv(*rest, request=request), request)

    def test_looking_shares_the_read_only_lane_and_writing_waits_its_turn(self):
        lanes = {name: mailbox_jobs.lane(self.record, {"argv": self.argv(*rest), "run": self.run,
                                                       "resident": self.resident})
                 for name, rest in {"status": ["status"], "read": ["read"], "bundle": ["bundle"],
                                    "arrive": ["arrive", "--name", "Wren"], "say": ["say", "hi"],
                                    "sleep": ["sleep", "--through", "1", "--note", "n"]}.items()}
        self.assertEqual({"status": "inspection", "read": "inspection", "bundle": "inspection",
                          "arrive": "worker", "say": "worker", "sleep": "worker"}, lanes)

    def test_a_whole_wake_through_the_channel_records_nothing_in_emberhall(self):
        for rest in (["status"], ["arrive", "--name", "Wren"], ["say", "hello"]):
            mailbox.parse(self.argv(*rest), self.record.root, self.workspace, self.resident)
        before = self.record.read()[0]["sequence"]
        self.assertEqual(0, self.execute("status")["wake"]["used"])
        visitor = self.execute("arrive", "--name", "Wren", request="door-2")["you_are"]
        self.assertEqual(22, self.execute("say", "A real wake.", request="door-3")["sequence"])
        self.assertTrue(self.execute("sleep", "--through", "22", "--note", "Handoff.", request="door-4")["slept"])
        self.assertEqual(before, self.record.read()[0]["sequence"], "Emberhall's journal is unchanged")
        state = Record(self.private / "daughters" / "reedbank" / "house").read()[0]
        self.assertEqual((23, False, "Handoff."), (state["sequence"], state["residents"][visitor]["awake"],
                                                    state["residents"][visitor]["note"]))
        self.assertIn(self.run, Record(self.private / "daughters" / "reedbank" / "house").read()[1][20]["data"]["text"])
        self.assertIsNone(resident_actions.known_result(self.record, self.resident, self.run, self.argv("status"), "door-1"))

    def test_another_residents_name_or_a_root_override_is_refused(self):
        with self.assertRaises(ValueError):
            resident_actions.parse(["reedbank", "--as", "someone-else", "status"], self.resident)
        for extra in (["--repo", "/tmp/x"], ["--artifacts-from", "/tmp/x"]):
            with self.assertRaises(ValueError):
                mailbox.parse(self.argv("status", *extra), self.record.root, self.workspace, self.resident)


if __name__ == "__main__":
    unittest.main()
