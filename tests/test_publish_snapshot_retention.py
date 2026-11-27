"""Cached current listings must outlive the next publication's tree replacement."""
import gzip
from contextlib import nullcontext
import hashlib
import json
import unittest
from unittest.mock import patch

from house import publish as publisher
from house.home_work import git
from tests.support import HouseCase


def companion(body):
    return "current/" + hashlib.sha256(body).hexdigest()[:16] + ".json.gz"


class SnapshotRetentionTests(unittest.TestCase):
    def retain(self, old, contents, **limits):
        reads = []

        def read(record, head, path, *, optional=False):
            reads.append(path)
            return old.get(path)

        with patch.object(publisher, "committed_blob", side_effect=read):
            with patch.multiple(publisher, **limits) if limits else nullcontext():
                publisher.retain_current_snapshots(object(), "previous", contents)
        return reads

    def test_upgrade_retains_previous_listing_and_deduplicates_newest(self):
        old_body, new_body = gzip.compress(b"old"), gzip.compress(b"new")
        old_path, new_path = companion(old_body), companion(new_body)
        old = {"current.json": json.dumps({"gzip": old_path}).encode(), old_path: old_body}
        contents = {new_path: new_body}
        self.retain(old, contents)
        self.assertEqual(contents[old_path], old_body)
        self.assertEqual(json.loads(contents[publisher.CURRENT_RETENTION_INDEX]), [new_path, old_path])
        same = dict(contents)
        same["current.json"] = json.dumps({"gzip": new_path}).encode()
        fresh = {new_path: new_body}
        self.retain(same, fresh)
        self.assertEqual(json.loads(fresh[publisher.CURRENT_RETENTION_INDEX]), [new_path, old_path])

    def test_count_and_byte_limits_expire_oldest(self):
        bodies = [bytes([i]) * 10 for i in range(5)]
        paths = [companion(body) for body in bodies]
        old = dict(zip(paths[1:], bodies[1:]))
        old[publisher.CURRENT_RETENTION_INDEX] = json.dumps(paths[1:]).encode()
        for limits in ({"CURRENT_RETAINED_COUNT": 3}, {"CURRENT_RETAINED_BYTES": 30}):
            with self.subTest(limits=limits):
                contents = {paths[0]: bodies[0]}
                self.retain(old, contents, **limits)
                self.assertEqual(json.loads(contents[publisher.CURRENT_RETENTION_INDEX]), paths[:3])
                self.assertNotIn(paths[3], contents)

    def test_missing_corrupt_and_unsafe_entries_do_not_break_publication(self):
        body = b"correct"
        path = companion(body)
        missing = companion(b"missing")
        old = {"current.json": b"{broken", path: b"wrong bytes",
               publisher.CURRENT_RETENTION_INDEX: json.dumps(["../secret", None, missing, path]).encode()}
        contents = {"current.json": b"plain current snapshot"}
        reads = self.retain(old, contents)
        self.assertNotIn("../secret", reads)
        self.assertEqual(contents, {"current.json": b"plain current snapshot"})

    def test_plain_snapshot_still_keeps_previous_compressed_target(self):
        body = gzip.compress(b"old")
        path = companion(body)
        old = {"current.json": json.dumps({"gzip": path}).encode(), path: body}
        contents = {"current.json": b"plain snapshot"}
        self.retain(old, contents)
        self.assertEqual(contents[path], body)

    def test_oversized_previous_blob_is_not_carried_past_publication_limit(self):
        body = b"too large"
        path = companion(body)
        old = {"current.json": json.dumps({"gzip": path}).encode(), path: body}
        contents = {"current.json": b"new"}
        self.retain(old, contents, MAX_PUBLIC_BLOB=3)
        self.assertNotIn(path, contents)


class SnapshotPublicationTests(HouseCase):
    def test_cached_listing_target_survives_real_republication_without_source_changes(self):
        (self.repo / "site").mkdir()
        for name in ("index.html", "house.js", "house.css"):
            (self.repo / "site" / name).write_text("fixture " + name)
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "Fixture")
        (self.repo / "site/index.html").write_text("private unfinished edit")
        index = (self.record.gitdir / "index").read_bytes()
        source = git(self.repo, "rev-parse", "HEAD")
        with patch.object(publisher, "CURRENT_SNAPSHOT_TARGET_BYTES", 0):
            first = publisher.publish(self.record)
            listing = json.loads(git(self.repo, "show", first["commit"] + ":current.json"))
            target = listing["gzip"]
            original = self.record.git("show", first["commit"] + ":" + target)
            self.record.append("say", "alice", {"text": "A newer house"})
            second = publisher.publish(self.record)
            self.assertEqual(self.record.git("show", second["commit"] + ":" + target), original)
            snapshot = json.loads(gzip.decompress(original))
            self.assertEqual(snapshot["journal_head"], listing["journal_head"])
            self.assertNotEqual(json.loads(git(self.repo, "show", second["commit"] + ":current.json"))["gzip"], target)
            self.assertFalse(publisher.publish(self.record)["changed"])
        self.assertEqual((self.record.gitdir / "index").read_bytes(), index)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), source)
        self.assertEqual((self.repo / "site/index.html").read_text(), "private unfinished edit")
