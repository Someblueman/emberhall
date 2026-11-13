"""Replay fails closed and verified bundles survive an actual fresh repository."""
import copy
import json

from house.record import ANCHOR, REF, Record
from tests.support import HouseCase


class RecoveryTests(HouseCase):
    def publish_invalid(self, event):
        head = self.record.read()[2]
        oid = self.record.commit(event, head)
        self.record.git("update-ref", REF, oid, head)

    def assert_corrupt_blocks_read_and_write(self, reason):
        head = self.record.ref(REF)
        with self.assertRaisesRegex(ValueError, reason):
            self.record.read()
        with self.assertRaisesRegex(ValueError, reason):
            self.record.append("say", "alice", {"text": "Must not append"})
        self.assertEqual(self.record.ref(REF), head)

    def test_duplicate_request_injected_in_history_fails_closed(self):
        _, events, _ = self.record.read()
        self.publish_invalid(copy.deepcopy(events[-1]))
        self.assert_corrupt_blocks_read_and_write("duplicate request")

    def test_replayed_bad_signature_fails_closed(self):
        state = self.record.read()[0]
        self.record.append("propose", "alice", {"proposal": "bad", "base": state["rule_revision"],
                           "text": "Crown the resident", "reason": "Attack"})
        state = self.record.read()[0]
        self.publish_invalid({"id": "forged", "actor": "alice", "op": "ratify", "at": state["at"],
                              "data": {"proposal": "bad", "signature": "Forged"}})
        self.assert_corrupt_blocks_read_and_write("sealed")

    def test_merge_parent_is_not_silently_ignored(self):
        head = self.record.read()[2]
        tree = self.record.git("rev-parse", f"{head}^{{tree}}").decode().strip()
        merge = self.record.git("commit-tree", tree, "-p", head, "-p", self.foundation["anchor"],
                               data=b"Injected merge\n").decode().strip()
        self.record.git("update-ref", REF, merge, head)
        self.assert_corrupt_blocks_read_and_write("not linear")

    def test_unexpected_extra_tree_file_fails_closed(self):
        state, _, head = self.record.read()
        event = {"id": "extra", "actor": "alice", "op": "say", "at": state["at"],
                 "data": {"text": "Extra hidden file"}}
        raw = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
        blob = self.record.git("hash-object", "-w", "--stdin", data=raw).decode().strip()
        tree = self.record.git("mktree", data=(f"100644 blob {blob}\tevent.json\n"
                               f"100644 blob {blob}\tunexpected\n").encode()).decode().strip()
        oid = self.record.git("commit-tree", tree, "-p", head, data=b"Extra tree\n").decode().strip()
        self.record.git("update-ref", REF, oid, head)
        self.assert_corrupt_blocks_read_and_write("unexpected journal tree")

    def test_noncanonical_event_bytes_fail_closed(self):
        state, _, head = self.record.read()
        raw = json.dumps({"id": "spaces", "actor": "alice", "op": "say", "at": state["at"],
                          "data": {"text": "Whitespace"}}, indent=2).encode()
        blob = self.record.git("hash-object", "-w", "--stdin", data=raw).decode().strip()
        tree = self.record.git("mktree", data=f"100644 blob {blob}\tevent.json\n".encode()).decode().strip()
        oid = self.record.git("commit-tree", tree, "-p", head, data=b"Spaced\n").decode().strip()
        self.record.git("update-ref", REF, oid, head)
        self.assert_corrupt_blocks_read_and_write("noncanonical")

    def test_bundle_round_trip_preserves_history_and_does_not_overwrite(self):
        self.record.append("say", "alice", {"text": "Remember this"}, "remember")
        bundle = self.root / "checkpoint.bundle"
        self.record.bundle(str(bundle))
        target = Record(self.new_repo("restored"))
        with self.assertRaisesRegex(ValueError, "trust anchor"):
            target.restore(str(bundle), "0" * 40)
        self.assertIsNone(target.ref(REF))
        restored = target.restore(str(bundle), self.foundation["anchor"])
        self.assertEqual(restored["head"], self.record.read()[2])
        self.assertEqual(target.read(), self.record.read())
        with self.assertRaisesRegex(ValueError, "overwrite"):
            target.restore(str(bundle), self.foundation["anchor"])
        self.assertEqual(target.ref(ANCHOR), self.foundation["anchor"])
        self.cli("say", "--as", "bob", "Restored and usable", repo=target.root)
        self.assertEqual(target.read()[0]["sequence"], 5)

    def test_invalid_bundle_never_publishes_canonical_refs(self):
        state, _, _ = self.record.read()
        self.publish_invalid({"id": "unknown", "actor": "alice", "op": "crown", "at": state["at"],
                              "data": {}})
        bundle = self.root / "invalid.bundle"
        self.record.git("bundle", "create", str(bundle), REF, ANCHOR)
        target = Record(self.new_repo("rejected"))
        with self.assertRaisesRegex(ValueError, "unknown operation"):
            target.restore(str(bundle), self.foundation["anchor"])
        self.assertIsNone(target.ref(REF))
        self.assertIsNone(target.ref(ANCHOR))
        self.assertEqual(target.git("for-each-ref", "refs/house-import/"), b"")
