"""Real disposable Git remotes: publish accepted SHA only and recover lost receipts."""
import fcntl
import json
import subprocess
import unittest
from unittest.mock import patch

from house import source_delivery as delivery
from house.home_work import git
from tests.support import HouseCase


class SourceDeliveryTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        git(self.repo, "symbolic-ref", "HEAD", "refs/heads/main")
        self.base = self.commit("base")
        self.remote = self.root / "remote.git"
        git(self.repo, "init", "--bare", str(self.remote))
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "origin", "main")
        self.private = self.record.common / "house-home"
        (self.private / "one").mkdir(parents=True)
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": "one",
            "resident": "writer", "agent": "codex", "model": "gpt-6.1-sol", "source_head": self.base,
            "workspace": "residents/one", "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "writer", {"name": "Writer"})
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": "one",
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        self.accepted = self.commit("accepted")
        self.report = {"run": "one", "actor": "alice", "status": "integrated",
            "contribution": self.accepted, "candidate_head": self.accepted, "test_exit": 0}
        (self.private / "one/contribution.json").write_text(json.dumps({"commit": self.accepted}))
        self.receipt()
        # Only activation and the approved remote location are substituted.
        # All Git transport, ancestry, writer locks and journal receipts are real.
        for name, value in (("enabled", True), ("approved_remote", "disposable-fixture")):
            helper = patch("house.source_delivery." + name, return_value=value)
            helper.start(); self.addCleanup(helper.stop)

    def commit(self, text):
        (self.repo / "document.txt").write_text(text)
        git(self.repo, "add", "document.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", text)
        return git(self.repo, "rev-parse", "HEAD")

    def receipt(self):
        (self.private / "one/integration.json").write_text(json.dumps(self.report))

    def remote_head(self):
        return git(self.repo, "ls-remote", "origin", "refs/heads/main").split()[0]

    def test_only_accepted_commit_pushed_dirty_work_preserved_and_retry_is_local(self):
        later = self.commit("unreviewed")
        (self.repo / "document.txt").write_text("unfinished")
        result = delivery.deliver(self.record, self.private)
        self.assertEqual(result["commit"], self.accepted)
        self.assertEqual(self.remote_head(), self.accepted)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), later)
        self.assertEqual((self.repo / "document.txt").read_text(), "unfinished")
        head = self.record.read()[2]
        # A delivered receipt needs no accessible network on replay.
        git(self.repo, "remote", "remove", "origin")
        self.assertTrue(delivery.deliver(self.record, self.private)["already_recorded"])
        self.assertEqual(self.record.read()[2], head)

    def test_push_succeeded_but_receipt_lost_retries_without_duplicate_event(self):
        with patch.object(self.record, "append", side_effect=OSError("lost receipt")):
            with self.assertRaisesRegex(OSError, "lost receipt"):
                delivery.deliver(self.record, self.private)
        self.assertEqual(self.remote_head(), self.accepted)
        delivery.deliver(self.record, self.private)
        delivery.deliver(self.record, self.private)
        receipts = [e for e in self.record.read()[1] if e["id"] == "source-delivered-" + self.accepted]
        self.assertEqual(len(receipts), 1)

    def test_remote_divergence_preserves_both_histories(self):
        fork = self.root / "fork"
        git(self.repo, "clone", str(self.remote), str(fork))
        git(fork, "checkout", "main")
        (fork / "other.txt").write_text("remote work")
        git(fork, "add", "other.txt")
        git(fork, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Independent remote work")
        git(fork, "push", "origin", "main")
        remote = self.remote_head()
        git(self.repo, "fetch", "origin", "main")
        with self.assertRaisesRegex(ValueError, "diverged"):
            delivery.deliver(self.record, self.private)
        self.assertEqual(self.remote_head(), remote)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.accepted)

    def test_bad_acceptance_and_concurrent_integration_cannot_publish(self):
        good = self.report.copy()
        for changes in ({"actor": "writer"}, {"test_exit": 1}, {"candidate_head": self.base}):
            self.report = good | changes; self.receipt()
            with self.assertRaises(ValueError):
                delivery.deliver(self.record, self.private)
            self.assertEqual(self.remote_head(), self.base)
        self.report = good; self.receipt()
        with (self.private / "integration.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                delivery.deliver(self.record, self.private)
        self.assertEqual(self.remote_head(), self.base)

    def test_failed_push_does_not_record_delivery_and_later_retry_succeeds(self):
        hook = self.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n"); hook.chmod(0o700)
        with self.assertRaises(subprocess.CalledProcessError):
            delivery.deliver(self.record, self.private)
        self.assertNotIn("source-delivered-" + self.accepted, self.record.read()[0]["receipts"])
        self.assertEqual(self.remote_head(), self.base)
        hook.unlink()
        delivery.deliver(self.record, self.private)
        self.assertEqual(self.remote_head(), self.accepted)

    def test_newer_acceptance_is_not_blocked_by_old_receipt_format(self):
        state = self.record.read()[0]
        state["life"]["runs"]["historical"] = dict(state["life"]["runs"]["one"])
        path = self.private / "historical"; path.mkdir()
        (path / "contribution.json").write_text(json.dumps({"commit": self.base}))
        old = dict(self.report, run="historical", contribution=self.base, candidate_head=self.base)
        old.pop("test_exit")
        (path / "integration.json").write_text(json.dumps(old))
        self.assertEqual(delivery.accepted_target(self.record, self.private, state), self.accepted)


class RemoteValidationTests(HouseCase):
    def test_only_single_approved_fetch_and_push_url(self):
        git(self.repo, "remote", "add", "origin", "https://github.com/Someblueman/emberhall.git")
        self.assertEqual(delivery.approved_remote(self.repo), "Someblueman/emberhall")
        git(self.repo, "config", "remote.origin.pushurl", "/tmp/unapproved")
        with self.assertRaisesRegex(ValueError, "approved repository"):
            delivery.approved_remote(self.repo)
        git(self.repo, "config", "remote.origin.pushurl", "https://github.com/Someblueman/emberhall.git")
        git(self.repo, "config", "--add", "remote.origin.pushurl", "https://github.com/Someblueman/emberhall.git")
        with self.assertRaisesRegex(ValueError, "approved repository"):
            delivery.approved_remote(self.repo)
