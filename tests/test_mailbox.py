"""Actual client subprocesses; no model or forged live-wake evidence."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from unittest.mock import patch
import zipfile

from house import mailbox
from house.home_work import client, git, room
from house.life import CONTROLLER
from house.record import Record
from tests.support import HouseCase, SOURCE


class MailboxCase(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "source.txt").write_text("base\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "Initial source")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"
        self.private.mkdir()
        self.runtime = self.private / "fixture.pyz"
        with zipfile.ZipFile(self.runtime, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                archive.write(file, "house/" + file.name)
        self.run = uuid.uuid4().hex
        self.resident = "mailbox-resident"
        self.record.append("arrive", CONTROLLER, {"name": "Watch keeper"})
        self.record.append("life", CONTROLLER, {"kind": "run-start", "run": self.run,
            "resident": self.resident, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + self.run,
            "policy_revision": "synthetic-test-policy", "mode": "work"})
        self.record.append("life", CONTROLLER, {"kind": "run-launched", "run": self.run, "pgid": os.getpid()})
        self.workspace = room(self.record, self.private, self.run, self.base)
        self.client = client(self.record, self.workspace, self.resident, self.runtime)
        self.requests = self.workspace / ".house-mailbox/requests"
        self.responses = self.workspace / ".house-mailbox/responses"

    def start(self, *argv, sandbox=False):
        command = [str(self.client), *argv]
        if sandbox:
            command = ["/usr/bin/sandbox-exec", "-p", self.sandbox_profile(), *command]
        process = subprocess.Popen(command, cwd=self.workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        return process

    def sandbox_profile(self):
        return ('(version 1)(allow default)(deny file-write* (require-all (subpath ' +
                json.dumps(str(self.record.common)) + ') (require-not (subpath ' +
                json.dumps(str(self.workspace)) + '))))')

    def collect(self, process, success=True):
        deadline = time.monotonic() + 12
        while process.poll() is None and time.monotonic() < deadline:
            mailbox.service(self.record, self.private, self.run)
            time.sleep(0.02)
        output, errors = process.communicate(timeout=2)
        self.assertEqual(process.returncode, 0 if success else 2, (output, errors))
        return json.loads(output) if success else errors

    def call(self, *argv):
        return self.collect(self.start(*argv))

    def arrive(self):
        return self.call("arrive", "--as", self.resident, "--name", "Fixture", "--request", "arrival")

    def raw(self, argv, key=None):
        key = key or mailbox.alias_id(uuid.uuid4().hex)
        (self.requests / (key + ".json")).write_text(json.dumps({"version": 1, "id": key, "argv": argv}))
        return key


class MailboxTests(MailboxCase):
    def test_local_help_requires_no_server_and_shared_writes_are_unnecessary(self):
        before = self.record.read()[2]
        for args in (("--help",), ("arrive", "--help")):
            result = subprocess.run([str(self.client), *args], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("resident" if args[0] == "--help" else "--name", result.stdout)
        self.assertEqual(self.record.read()[2], before)
        if os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") or not Path("/usr/bin/sandbox-exec").exists():
            self.skipTest("macOS sandbox-exec unavailable; portable mailbox tests still run")
        direct = subprocess.run(["/usr/bin/sandbox-exec", "-p", self.sandbox_profile(), sys.executable, "-c",
            f"from house.record import Record;Record({str(self.repo)!r}).append('say','alice',{{'text':'blocked'}})"],
            cwd=SOURCE, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(direct.returncode, 0)
        self.assertIn("house-writer.lock", direct.stderr)
        reply = self.collect(self.start("arrive", "--as", self.resident, "--name", "Sandboxed", sandbox=True))
        self.assertIn("sequence", reply)
        self.assertIn(self.resident, self.record.read()[0]["residents"])
        self.assertEqual(git(self.workspace, "status", "--porcelain"), "")

    def test_server_rejects_bypassed_client_and_keeps_other_messages_moving(self):
        before = self.record.read()[2]
        bad = (["found", "--name", "Takeover", "--rules", "source.txt"],
               ["say", "--as", "alice", "Impersonation"], ["--repo", str(self.repo), "status"],
               ["finish", "x", "--as", self.resident, "--token", "x", "--result", "x",
                "--artifact", "source.txt", "--artifacts-from", str(self.repo)],
               ["life", "--as", self.resident, "--data", '{"kind":"run-finish"}'],
               ["wait", "--as", self.resident, "--after", "0", "--seconds", "3601"], ["say"])
        for argv in bad:
            key = self.raw(argv)
            self.assertEqual(mailbox.service(self.record, self.private, self.run), 1)
            self.assertFalse(json.loads((self.responses / (key + ".json")).read_text())["ok"])
        self.assertEqual(self.record.read()[2], before)
        self.assertTrue(self.call("verify")["valid"])

    def test_lost_reply_reuses_accepted_receipt_and_alias_remains_readable(self):
        arrival = self.arrive()
        argv = ["say", "--as", self.resident, "--request", "hello", "One event"]
        reply = self.call(*argv)
        key = mailbox.alias_id("hello")
        (self.responses / (key + ".json")).unlink()
        saved = self.private / self.run / "mailbox" / (key + ".json")
        metadata = json.loads(saved.read_text())
        metadata.pop("response")  # Crash after Git accepted, before response persistence.
        saved.write_text(json.dumps(metadata))
        again = self.call(*argv)
        self.assertTrue(again["replayed"])
        self.assertEqual(reply["sequence"], again["sequence"])
        self.assertEqual(self.call("receipt", "hello")["sequence"], reply["sequence"])
        self.assertEqual(self.call("receipt", reply["request"])["sequence"], reply["sequence"])
        self.assertEqual(self.call("receipt", arrival["request"])["sequence"], arrival["sequence"])
        other = self.record.append("say", "alice", {"text": "Earlier resident receipt"}, "earlier-canonical-receipt")
        self.assertEqual(self.call("receipt", "earlier-canonical-receipt")["sequence"], other["sequence"])
        self.collect(self.start(*argv[:-1], "Changed payload"), success=False)
        self.assertEqual(sum(e["op"] == "say" and e["actor"] == self.resident for e in self.record.read()[1]), 1)

    def test_finish_uses_own_artifact_and_lost_reply_never_resnapshots(self):
        self.arrive()
        self.call("task", "owned", "--as", self.resident, "--title", "Owned", "--description", "Fixture")
        self.call("claim", "owned", "--as", self.resident, "--expect", "0", "--token", "fixture-token")
        (self.workspace / "source.txt").write_text("private artifact\n")
        argv = ["finish", "owned", "--as", self.resident, "--request", "finish-owned", "--token", "fixture-token",
                "--result", "Actual private bytes", "--artifact", "source.txt"]
        first = self.call(*argv)
        key = mailbox.alias_id("finish-owned")
        (self.responses / (key + ".json")).unlink()
        saved = self.private / self.run / "mailbox" / (key + ".json")
        metadata = json.loads(saved.read_text()); metadata.pop("response"); saved.write_text(json.dumps(metadata))
        (self.workspace / "source.txt").write_text("changed after completion\n")
        self.assertEqual(self.call(*argv)["sequence"], first["sequence"])
        artifact = self.record.read()[0]["tasks"]["owned"]["artifacts"]["source.txt"]
        self.assertEqual(base64.b64decode(artifact["base64"]), b"private artifact\n")
        self.assertEqual((self.repo / "source.txt").read_text(), "base\n")

    def test_wait_is_nonblocking_ref_cached_and_deadline_survives_restart(self):
        self.arrive()
        through = self.record.read()[0]["sequence"]
        waiting = self.start("wait", "--as", self.resident, "--after", str(through), "--seconds", "1")
        deadline = time.monotonic() + 5
        while not list(self.requests.glob("*.json")) and time.monotonic() < deadline:
            time.sleep(0.01)
        mailbox.service(self.record, self.private, self.run)
        request = next(self.requests.glob("*.json"))
        saved = self.private / self.run / "mailbox" / request.name
        first_deadline = json.loads(saved.read_text())["deadline"]
        fresh = Record(self.repo)
        with patch.object(fresh, "read", wraps=fresh.read) as reads:
            for _ in range(5):
                mailbox.service(fresh, self.private, self.run)
            self.assertEqual(reads.call_count, 1)
        self.assertEqual(json.loads(saved.read_text())["deadline"], first_deadline)
        self.assertTrue(self.call("verify")["valid"])
        result = self.collect(waiting)
        self.assertFalse(result["changed"])

    def test_fifo_symlink_oversized_and_malformed_json_do_not_block(self):
        victim = self.root / "outside.txt"
        victim.write_text("untouched")
        keys = [mailbox.alias_id(str(index)) for index in range(4)]
        os.mkfifo(self.requests / (keys[0] + ".json"))
        (self.requests / (keys[1] + ".json")).symlink_to(victim)
        (self.requests / (keys[2] + ".json")).write_bytes(b" " * (mailbox.MAX_REQUEST + 1))
        (self.requests / (keys[3] + ".json")).write_text("[]")
        before = time.monotonic()
        self.assertEqual(mailbox.service(self.record, self.private, self.run), 4)
        self.assertLess(time.monotonic() - before, 2)
        for key in keys:
            self.assertFalse(json.loads((self.responses / (key + ".json")).read_text())["ok"])
        self.assertEqual(victim.read_text(), "untouched")
        key = self.raw(["verify"])
        (self.responses / (key + ".json")).symlink_to(victim)
        mailbox.service(self.record, self.private, self.run)
        self.assertEqual(victim.read_text(), "untouched")
        self.assertTrue(self.call("verify")["valid"])

    def test_many_waiters_cannot_starve_another_command(self):
        self.arrive()
        through = self.record.read()[0]["sequence"]
        for index in range(32):
            self.raw(["wait", "--as", self.resident, "--after", str(through), "--seconds", "60"], f"{index:064x}")
        key = self.raw(["verify"], "f" * 64)
        self.assertEqual(sum(mailbox.service(self.record, self.private, self.run) for _ in range(4)), 1)
        self.assertTrue(json.loads((self.responses / (key + ".json")).read_text())["ok"])

    def test_directory_scan_advances_past_more_than_512_junk_entries(self):
        for index in range(600):
            (self.requests / f"junk-{index}").touch()
        key = self.raw(["verify"])
        self.assertEqual(sum(mailbox.service(self.record, self.private, self.run) for _ in range(4)), 1)
        self.assertTrue(json.loads((self.responses / (key + ".json")).read_text())["ok"])

    def test_replaced_directory_and_ended_run_cannot_execute_requests(self):
        before = self.record.read()[2]
        original = self.requests.with_name("original-requests")
        self.requests.rename(original)
        self.requests.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(mailbox.service(self.record, self.private, self.run), 0)
        self.assertEqual(self.record.read()[2], before)
        self.requests.unlink(); original.rename(self.requests)
        self.record.append("life", CONTROLLER, {"kind": "run-finish", "run": self.run, "outcome": "interrupted",
            "exit_code": None, "usage": {}, "elapsed_seconds": 1})
        self.raw(["arrive", "--as", self.resident, "--name", "Too late"])
        self.assertEqual(mailbox.service(self.record, self.private, self.run), 0)
        self.assertNotIn(self.resident, self.record.read()[0]["residents"])
