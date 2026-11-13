"""Names can change; identity, authorship and historical receipts cannot."""
import copy
import contextlib
import io
from pathlib import Path
import unittest

from house import mailbox
from house.__main__ import parser
from house.model import validate_resident_name
from tests import test_council as fixtures


class ResidentNameTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.CouncilTests(); self.h.setUp()
        self.h.state["maintenance"] = {"resident_names": True}

    def test_trimmed_personal_names_are_allowed_without_aesthetic_blacklist(self):
        for name in (" Ember ", "Bryn", "Ada Lovelace", "Jean-Luc", "O'Keeffe", "Élodie", "Wonder"):
            self.h.event("rename", {"name": name})
            self.assertEqual(self.h.state["residents"]["alice"]["name"], name.strip())
        self.h.event("arrive", {"name": "  Fern  "}, "new-person")
        self.assertEqual(self.h.state["residents"]["new-person"]["name"], "Fern")

    def test_duplicate_technical_and_generated_labels_reject_for_arrival_and_rename(self):
        names = ("", "   ", "a" * 101, "line\nbreak", "BOB", "Hydrogen", "Ember Muse", "hydrogen-1f27",
                 "agy-hydrogen", "muse / muse-ember-1.0", "Emberkeeper-23", "gpt-6.1-sol",
                 "opencode-go/kimi-k3.1-pro", "resident-abcd", "agent-42", "run-test",
                 "0123456789abcdef", "Fern-a1b2", "01234567-89ab-cdef-0123-456789abcdef")
        for name in names:
            with self.subTest(name=name):
                self.h.reject("rename", {"name": name}, "name|label|ID")
                self.h.reject("arrive", {"name": name}, "name|label|ID", "new-person")
        self.h.event("arrive", {"name": "Ember"}, "old-ember")
        self.h.reject("rename", {"name": " eMbEr "}, "already taken")

    def test_canonically_equal_unicode_names_share_one_spelling(self):
        self.h.event("rename", {"name": "E\u0301lodie"})
        self.assertEqual(self.h.state["residents"]["alice"]["name"], "Élodie")
        self.h.reject("rename", {"name": "éLODIE"}, "already taken", "bob")
        self.h.reject("arrive", {"name": "E\u0301lodie"}, "already taken", "new-person")
        self.h.state["residents"]["alice"]["name"] = "E\u0301lodie"  # A pre-migration spelling.
        self.h.reject("rename", {"name": "Élodie"}, "already taken", "bob")
        self.assertEqual(self.h.state["residents"]["alice"]["name"], "E\u0301lodie")

    def test_self_only_awake_and_exact_payload(self):
        for field in ("actor", "resident", "id", "target"):
            self.h.reject("rename", {"name": "Fern", field: "bob"}, "own name")
        self.h.reject("rename", {"name": "Fern"}, "unknown resident", "stranger")
        self.h.event("sleep", {"through": self.h.state["sequence"], "note": "Later"})
        self.h.reject("rename", {"name": "Fern"}, "sleeping")
        self.h.event("wake", {})
        bob = copy.deepcopy(self.h.state["residents"]["bob"])
        self.h.event("rename", {"name": "Fern"})
        self.assertEqual(self.h.state["residents"]["bob"], bob)

    def test_rename_preserves_memory_claims_authorship_and_old_event_data(self):
        self.h.event("task", {"task": "held", "title": "A thread", "description": "Continue"})
        self.h.event("claim", {"task": "held", "token": "keep-token", "expect": 0, "seconds": 60})
        self.h.event("learn", {"lesson": "learned", "key": "names", "claim": "Names are not IDs", "evidence": "Fixture"})
        old_arrival = {"name": "Original Fern"}
        self.h.event("arrive", old_arrival, "fern")
        before = copy.deepcopy(self.h.state)
        self.h.event("rename", {"name": "Briar"})
        after = self.h.state
        self.assertEqual(after["residents"]["alice"], before["residents"]["alice"] | {"name": "Briar"})
        for key in ("tasks", "lessons", "rules", "rule_revision"):
            self.assertEqual(after[key], before[key])
        self.assertEqual(before["residents"]["alice"]["name"], "alice")
        self.h.reject("review", {"lesson": "learned", "evidence": "New name, same author"}, "independent")
        self.h.event("rename", {"name": "Hazel"}, "fern")
        self.assertEqual(old_arrival, {"name": "Original Fern"})

    def test_historical_names_and_duplicates_replay_until_owner_flag(self):
        self.h.state.pop("maintenance")
        self.h.event("arrive", {"name": "Hydrogen"}, "technical-one")
        self.h.event("arrive", {"name": "Hydrogen"}, "technical-two")
        self.h.event("arrive", {"name": "   "}, "legacy-space")
        self.h.reject("rename", {"name": "Fern"}, "not enabled")
        names = copy.deepcopy(self.h.state["residents"])
        self.h.state["maintenance"] = {"resident_names": True}
        self.assertEqual(self.h.state["residents"], names)
        with self.assertRaises(ValueError):
            validate_resident_name(self.h.state, "technical-one", "Hydrogen")
        self.h.event("rename", {"name": "Fern"}, "technical-one")
        self.assertEqual(self.h.state["residents"]["technical-two"]["name"], "Hydrogen")

    def test_cli_and_fixed_mailbox_offer_only_self_rename(self):
        args = parser().parse_args(["rename", "--as", "alice", "--name", "Fern", "--request", "wake-rename"])
        self.assertEqual((args.command, args.actor, args.name), ("rename", "alice", "Fern"))
        args = mailbox.parse(["rename", "--as", "alice", "--name", "Fern"], Path("/canonical"), Path("/room"), "alice")
        self.assertEqual(args.command, "rename")
        self.assertIn("rename", mailbox.MUTATIONS)
        self.assertNotIn("rename", mailbox.ACTIONS)
        with self.assertRaisesRegex(ValueError, "another resident"):
            mailbox.parse(["rename", "--as", "bob", "--name", "Fern"], Path("/canonical"), Path("/room"), "alice")
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser().parse_args(["rename", "--as", "alice", "--name", "Fern", "--target", "bob"])


class ResidentNameMailboxTests(unittest.TestCase):
    def test_real_client_rename_keeps_history_and_replays_lost_reply(self):
        import uuid
        from unittest.mock import patch
        from house import body, council, maintenance
        from house.record import Record
        from tests import test_mailbox as mailbox_fixture, test_wake_policy
        original_found, original_append = Record.found, Record.append
        def approved_found(record, *args, **kwargs):
            with patch("house.record.uuid.uuid4", side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
                return original_found(record, *args, **kwargs)
        def append(record, op, actor, data, request=None):
            if op == "life" and data.get("kind") == "run-start":
                original_append(record, "council-authorize", "alice", fixtures.approval())
                original_append(record, "council-wake-authorize", "alice", test_wake_policy.approval())
                state = record.read()[0]; old = maintenance.protected_manifest(state)
                original_append(record, "owner-migrate", "alice", {
                    "scope": maintenance.NAMING_SCOPE, "approval_sha256": maintenance.GROWTH_SHA256,
                    "house": state["house_id"], "owner_id": council.OWNER_ID,
                    "source_head": "a" * 40, "source_sha256": "b" * 64,
                    "protected_files": old | {name: "c" * 64 for name in maintenance.OWNER_MODULES},
                    "previous_manifest_sha256": maintenance.fingerprint(old), "previous_runtime_sha256": "d" * 64,
                    "runtime_sha256": "e" * 64, "test_output_sha256": "f" * 64, "test_count": 1})
            return original_append(record, op, actor, data, request)
        f = mailbox_fixture.MailboxCase()
        with patch.object(Record, "found", approved_found), patch.object(Record, "append", append):
            f.setUp()
        self.addCleanup(f.doCleanups)
        arrival = f.arrive()
        before = body.export(f.record)
        renamed = f.call("rename", "--as", f.resident, "--name", "Fern", "--request", "one-rename")
        head = f.record.read()[2]
        repeated = f.call("rename", "--as", f.resident, "--name", "Fern", "--request", "one-rename")
        self.assertEqual(renamed, repeated); self.assertEqual(f.record.read()[2], head)
        state, events, _ = f.record.read()
        self.assertEqual(state["residents"][f.resident]["name"], "Fern")
        self.assertEqual(events[arrival["sequence"] - 1]["data"]["name"], "Fixture")
        self.assertEqual(events[renamed["sequence"] - 1]["op"], "rename")
        after = body.export(f.record)
        self.assertEqual(after["frames"][:len(before["frames"])], before["frames"])
        old_person = next(person for person in before["frames"][-1]["residents"] if person["id"] == f.resident)
        new_person = next(person for person in after["frames"][-1]["residents"] if person["id"] == f.resident)
        self.assertEqual(old_person["name"], "Fixture"); self.assertEqual(new_person["name"], "Fern")
        self.assertNotIn("name_history", old_person)
        self.assertEqual(new_person["name_history"], [{"from": "Fixture", "to": "Fern",
            "sequence": renamed["sequence"], "at": events[renamed["sequence"] - 1]["at"]}])
        error = f.collect(f.start("rename", "--as", "alice", "--name", "Rowan"), success=False)
        self.assertIn("another resident", error)
        f.call("sleep", "--as", f.resident, "--through", str(state["sequence"]), "--note", "Later")
        error = f.collect(f.start("rename", "--as", f.resident, "--name", "Rowan"), success=False)
        self.assertIn("sleeping", error)
