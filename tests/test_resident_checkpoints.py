"""Real Git restores and filesystem failures; synthetic supervised assignments."""
import copy
import hashlib
import json
import os
from pathlib import Path
import time
from unittest.mock import patch

from house import checkpoint
from house.home_work import git, room
from house.record import ANCHOR, REF, Record
from tests.support import HouseCase


class ResidentCheckpointTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "source.txt").write_text("preserve source\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Source fixture")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.run, self.resident, self.task, self.token = "checkpoint-run", "exporter", "export", "task-token"
        self.record.append("arrive", "watch-keeper", {"name": "Controller"})
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": self.run,
            "resident": self.resident, "agent": "codex", "model": "gpt-6.1-sol", "source_head": self.base,
            "workspace": "residents/" + self.run, "policy_revision": "fixture", "mode": "work"})
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": self.run, "pgid": os.getpid()})
        self.record.append("arrive", self.resident, {"name": "Maple"})
        self.record.append("task", self.resident, {"task": self.task, "title": "Checkpoint", "description": "Verify export"})
        self.record.append("claim", self.resident, {"task": self.task, "token": self.token, "expect": 0, "seconds": 600})
        self.private = self.record.common / "house-home"
        self.private.mkdir()
        self.workspace = room(self.record, self.private, self.run, self.base)

    def create(self, request="export-request", **changes):
        args = dict(record=self.record, workspace=self.workspace, resident=self.resident, run=self.run,
                    task=self.task, token=self.token, requestid=request)
        return checkpoint.create(**(args | changes))

    def known(self, request="export-request", **changes):
        args = dict(record=self.record, resident=self.resident, run=self.run, task=self.task,
                    token=self.token, requestid=request)
        return checkpoint.known_result(**(args | changes))

    def job(self, request="export-request"):
        return self.private / "checkpoints" / hashlib.sha256(request.encode()).hexdigest()

    def test_real_restore_preserves_exact_prefix_source_index_and_private_inode(self):
        before = self.record.read()
        index = (self.record.gitdir / "index").read_bytes()
        result = self.create()
        self.assertEqual(result["head"], before[2]); self.assertEqual(result["events"], before[0]["sequence"])
        self.assertEqual(result["task_generation"], 1)
        self.assertEqual(self.record.read(), before)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.base)
        self.assertEqual((self.record.gitdir / "index").read_bytes(), index)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        bundle, document = self.workspace / result["bundle"], self.workspace / result["metadata"]
        data = json.loads(document.read_text())
        self.assertEqual(data["bundle_sha256"], hashlib.sha256(bundle.read_bytes()).hexdigest())
        restored = Record(self.new_repo("independently-restored"))
        restored.restore(str(bundle), data["anchor"])
        self.assertEqual(restored.read(), before)
        self.assertEqual(restored.ref(ANCHOR), self.record.ref(ANCHOR))
        self.assertTrue(data["restored_exact_state_and_events"])
        self.assertNotEqual(bundle.stat().st_ino, (self.job() / "checkpoint.bundle").stat().st_ino)
        self.assertEqual(bundle.stat().st_nlink, 1)
        self.assertFalse(list(self.job().glob("restore-*")))
        self.assertFalse((self.workspace / "evidence/checkpoint.json").exists())
        self.assertFalse((self.workspace / "docs/RESUME.md").exists())

    def test_completed_retry_and_known_result_outlive_claim_without_new_effects(self):
        result = self.create()
        before = (self.job() / "job.json").read_bytes()
        self.record.append("release", self.resident, {"task": self.task, "token": self.token, "note": "Done exporting"})
        self.record.append("sleep", self.resident, {"through": self.record.read()[0]["sequence"], "note": "Later"})
        head = self.record.read()[2]
        with patch.object(self.record, "bundle", side_effect=AssertionError("must not export again")):
            self.assertEqual(self.create(), result)
            self.assertEqual(self.known(), result)
        self.assertEqual(self.record.read()[2], head)
        self.assertEqual((self.job() / "job.json").read_bytes(), before)
        self.assertIsNone(self.known("not-started"))
        for change in ({"resident": "bob"}, {"run": "other"}, {"task": "other"}, {"token": "new-token"}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "collision|mismatch"):
                self.known(**change)

    def test_identity_liveness_and_token_refusals(self):
        for changes in ({"workspace": self.repo}, {"resident": "bob"}, {"run": "missing"},
                        {"task": "missing"}, {"token": "stale"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.create(**changes)
        self.record.append("sleep", self.resident, {"through": 0, "note": "Asleep"})
        with self.assertRaisesRegex(ValueError, "awake"):
            self.create()
        self.record.append("wake", self.resident, {})
        with patch("house.checkpoint.time.time", return_value=time.time() + 1000):
            with self.assertRaisesRegex(ValueError, "unexpired"):
                self.create()
        # Replay-derived run data is the liveness boundary; test a missing launch receipt.
        state, events, head = self.record.read()
        unlaunched = copy.deepcopy(state); del unlaunched["life"]["runs"][self.run]["launched_sequence"]
        with patch.object(self.record, "read", return_value=(unlaunched, events, head)):
            with self.assertRaisesRegex(ValueError, "launched"):
                self.create()
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": self.run,
            "outcome": "interrupted", "exit_code": None, "usage": {}, "elapsed_seconds": 1})
        with self.assertRaisesRegex(ValueError, "active"):
            self.create()
        self.assertFalse(self.job().exists())

    def test_task_reclaimed_during_verification_blocks_final_delivery(self):
        original = checkpoint.prepare
        def reclaim(*args):
            original(*args)
            self.record.append("release", self.resident, {"task": self.task, "token": self.token, "note": "Lease changed"})
            self.record.append("claim", "bob", {"task": self.task, "token": "successor", "expect": 1, "seconds": 600})
        with patch("house.checkpoint.prepare", side_effect=reclaim):
            with self.assertRaisesRegex(ValueError, "unexpired task token"):
                self.create()
        self.assertTrue((self.job() / "checkpoint.bundle").is_file())
        self.assertFalse((self.workspace / "evidence").exists())
        self.assertIsNone(self.known())
        with self.assertRaisesRegex(ValueError, "collision|mismatch"):
            self.known(token="successor")

    def test_interrupted_delivery_reuses_original_prefix_after_later_events(self):
        original_link = os.link
        for failure in ("before-json", "after-bundle"):
            request = failure
            prefix = self.record.read()
            def interrupted(source, target, **kwargs):
                if failure == "before-json" and target.endswith(".json"):
                    raise OSError("synthetic second-file interruption")
                original_link(source, target, **kwargs)
                if failure == "after-bundle" and target.endswith(".bundle"):
                    raise OSError("synthetic interruption after no-clobber link")
            with patch("house.checkpoint.os.link", side_effect=interrupted):
                with self.assertRaisesRegex(OSError, "synthetic"):
                    self.create(request)
            self.assertIsNone(self.known(request))
            self.record.append("say", "alice", {"text": "A later event, outside retained prefix"})
            with patch.object(self.record, "bundle", side_effect=AssertionError("must retain prefix")):
                result = self.create(request)
            self.assertEqual(result["head"], prefix[2])
            self.assertEqual(result["events"], prefix[0]["sequence"])
            self.assertEqual(self.known(request), result)

    def test_existing_outputs_and_symlinks_are_never_replaced(self):
        original = checkpoint.deliver
        for suffix in (".bundle", ".json"):
            for symlink in (False, True):
                request = suffix + str(symlink)
                outside = self.root / ("outside" + request); outside.write_bytes(b"untouched")
                competitor = []
                def collide(fd, target, metadata):
                    name = next(name for name in metadata["outputs"] if name.endswith(suffix))
                    path = self.workspace / "evidence" / name; competitor.append(path)
                    path.symlink_to(outside) if symlink else path.write_bytes(b"competitor")
                    original(fd, target, metadata)
                with patch("house.checkpoint.deliver", side_effect=collide):
                    with self.assertRaisesRegex(ValueError, "destination already exists"):
                        self.create(request)
                self.assertEqual(outside.read_bytes(), b"untouched")
                self.assertEqual(competitor[0].is_symlink(), symlink)
                if not symlink: self.assertEqual(competitor[0].read_bytes(), b"competitor")
                self.assertIsNone(self.known(request))
        other = room(self.record, self.private, "symlink-room", self.base)
        evidence = self.workspace / "evidence"
        parked = self.workspace / "old-evidence"; evidence.rename(parked); evidence.symlink_to(other)
        with self.assertRaises(OSError):
            self.create("symlink-parent")
        self.assertFalse(list(other.glob("house-checkpoint-*")))

    def test_changed_or_deleted_completed_output_is_not_silently_repaired(self):
        for mutation in ("change", "delete"):
            result = self.create(mutation)
            target = self.workspace / result["bundle"]
            target.write_bytes(b"changed") if mutation == "change" else target.unlink()
            with self.assertRaises((ValueError, OSError)):
                self.known(mutation)
            with self.assertRaises((ValueError, OSError)):
                self.create(mutation)
            if mutation == "change": self.assertEqual(target.read_bytes(), b"changed")
            else: self.assertFalse(target.exists())

    def test_oversized_bundle_is_kept_private_and_never_delivered(self):
        with patch("house.checkpoint.FILE_LIMIT", 64):
            with self.assertRaisesRegex(ValueError, "bounded"):
                self.create()
        self.assertTrue((self.job() / "checkpoint.bundle").is_file())
        self.assertFalse((self.workspace / "evidence").exists())
        self.assertIsNone(self.known())

    def test_competitor_at_no_clobber_link_boundary_is_preserved(self):
        original_link = os.link
        for suffix in (".bundle", ".json"):
            for symlink in (False, True):
                request = "race" + suffix + str(symlink)
                competitor = []
                outside = self.root / ("race-outside" + request); outside.write_bytes(b"outside intact")
                def race(source, target, **kwargs):
                    if target.endswith(suffix):
                        competitor.append(self.workspace / "evidence" / target)
                        if symlink:
                            os.symlink(outside, target, dir_fd=kwargs["dst_dir_fd"])
                        else:
                            descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                                                 0o600, dir_fd=kwargs["dst_dir_fd"])
                            with os.fdopen(descriptor, "wb") as output:
                                output.write(b"won race")
                    original_link(source, target, **kwargs)
                with patch("house.checkpoint.os.link", side_effect=race):
                    with self.assertRaises(FileExistsError):
                        self.create(request)
                self.assertEqual(outside.read_bytes(), b"outside intact")
                self.assertEqual(competitor[0].is_symlink(), symlink)
                if not symlink: self.assertEqual(competitor[0].read_bytes(), b"won race")
                with self.assertRaises((ValueError, OSError)):
                    self.create(request)
                self.assertIsNone(self.known(request))
