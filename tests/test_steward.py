"""The phone adapter authenticates remote receipts and fails closed on outages."""
import contextlib
from email.utils import formatdate
import io
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from house import council, steward, wake_policy


class StewardTests(unittest.TestCase):
    def test_wake_authorization_requires_exact_owner_source_before_network_or_append(self):
        record = Mock()
        record.read.return_value = ({}, [], "head")
        record.ref.return_value = steward.FOUNDATION
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "wrong-objective.md"
            source.write_text("A resident cannot authorize its own limits.")
            with patch.object(steward, "Record", return_value=record), \
                    patch.object(steward, "github") as network, \
                    contextlib.redirect_stderr(io.StringIO()) as errors:
                code = steward.main(["--as", "alice", "authorize-wake", "--source", str(source),
                                     "--source-commit", "a" * 40])
        self.assertEqual(code, 2)
        self.assertIn("source bytes", errors.getvalue())
        record.append.assert_not_called()
        network.assert_not_called()

    def test_wake_notice_names_protected_scope_without_changing_old_rule_notice(self):
        item = {"mode": "rule", "status": "pending", "title": "A rule", "text": "Exact text\n",
                "author": "alice", "base": "revision"}
        old = steward.notice_body("rule", item)
        changed = steward.notice_body("rule", item | {"mode": "wake-prompt"})
        self.assertNotIn("Scope: council wake", old)
        self.assertIn("Scope: council wake prompt only", changed)
        self.assertIn("24-hour veto window", changed)
        self.assertIn("two independent non-author endorsements", changed)

    def test_github_requires_fresh_server_date_and_success(self):
        now = time.time()
        response = SimpleNamespace(returncode=0, stdout=(
            f"HTTP/2.0 200 OK\nDate: {formatdate(now, usegmt=True)}\n\n" + '{"id":1}'))
        with patch.object(steward.subprocess, "run", return_value=response) as call:
            value, checked = steward.github("user")
            self.assertEqual(value, {"id": 1})
            self.assertLess(abs(now - checked), 1)
            self.assertEqual(call.call_args.args[0], ["gh", "api", "--include", "--method", "GET", "user"])
            response.stdout = 'HTTP/2.0 200 OK\n\n{"id":1}'
            with self.assertRaisesRegex(ValueError, "server date"):
                steward.github("user")
            response.stdout = f"HTTP/2.0 200 OK\nDate: {formatdate(now-120, usegmt=True)}\n\n{{}}"
            with self.assertRaisesRegex(ValueError, "clock"):
                steward.github("user")
            response.returncode = 1
            with self.assertRaisesRegex(ValueError, "request failed"):
                steward.github("user")

    def test_every_page_is_read_and_only_steward_identity_is_forwarded(self):
        foreign = [{"id": n, "user": {"id": 999}, "body": "VETO rule"} for n in range(1, 101)]
        owner = {"id": 101, "user": {"id": council.OWNER_ID}, "body": "VETO rule"}
        with patch.object(steward, "github", side_effect=[(foreign, 1000), ([owner], 1001)]) as call:
            comments, checked = steward.comments()
        self.assertEqual(comments, [owner])
        self.assertEqual(checked, 1001)
        self.assertTrue(call.call_args_list[1].args[0].endswith("page=2"))
        with patch.object(steward, "github", return_value=([owner, owner], 1001)):
            with self.assertRaisesRegex(ValueError, "repeated"):
                steward.comments()

    def test_changed_owner_or_locked_bell_cannot_be_used(self):
        repo = {"full_name": council.REPOSITORY, "owner": {"id": council.OWNER_ID}}
        issue = {"number": council.ISSUE, "html_url": steward.BELL_URL, "locked": False}
        with patch.object(steward, "github", side_effect=[(repo, 1), (issue, 1)]):
            steward.context()
        for bad_repo, bad_issue in [({**repo, "owner": {"id": 999}}, issue),
                                    (repo, {**issue, "locked": True})]:
            with patch.object(steward, "github", side_effect=[(bad_repo, 1), (bad_issue, 1)]):
                with self.assertRaisesRegex(ValueError, "identity or availability"):
                    steward.context()

    def test_lost_notice_receipt_reuses_exact_public_notice_without_posting(self):
        item = {"mode": "rule", "status": "pending", "title": "A rule", "text": "Exact text\n",
                "author": "alice", "base": "revision"}
        record = Mock()
        record.read.return_value = ({"proposals": {"rule": item}}, [], "head")
        comment = {"id": 123, "user": {"id": council.OWNER_ID},
                   "body": steward.notice_body("rule", item)}
        with patch.object(steward, "context"), patch.object(steward, "comments", return_value=([comment], 1)), \
                patch.object(steward, "github") as network:
            steward.publish_notice(record, "alice", "rule")
            network.assert_not_called()
            self.assertEqual(record.append.call_args.args[2]["comment_id"], 123)
            comment["body"] += "changed"
            record.append.reset_mock()
            with self.assertRaisesRegex(ValueError, "notice changed"):
                steward.publish_notice(record, "alice", "rule")
            record.append.assert_not_called()

    def test_enactment_cannot_bypass_a_failed_fresh_sync(self):
        record = Mock()
        record.read.return_value = ({}, [], "head")
        with patch.object(steward, "Record", return_value=record), \
                patch.object(steward, "sync", side_effect=ValueError("network unavailable")), \
                contextlib.redirect_stderr(io.StringIO()) as errors:
            code = steward.main(["--as", "alice", "enact", "rule"])
        self.assertEqual(code, 2)
        self.assertIn("network unavailable", errors.getvalue())
        record.append.assert_not_called()
