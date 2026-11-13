"""Exercise the isolated forced-command protocol, not a deployed account boundary."""
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import subprocess
import sys
import time

from tests.support import HouseCase, SOURCE


class CustodianTests(HouseCase):
    def request(self, action="verify", data=None, request="test-request", **changes):
        body = {"version": 1, "house": self.foundation["house_id"], "resident": "alice",
                "request": request, "action": action, "data": {} if data is None else data}
        return body | changes

    def server(self, *, anchor=None, resident="alice", timeout="5", env=None, cwd=None):
        return subprocess.Popen(
            [sys.executable, "-I", str(SOURCE / "custodian_entry.py"), "--repo", str(self.repo),
             "--expect-anchor", anchor or self.foundation["anchor"], "--resident", resident,
             "--timeout", timeout], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=cwd or self.root, env=dict(os.environ, **(env or {})))

    def exchange(self, body=None, *, raw=None, success=True, **options):
        payload = raw if raw is not None else json.dumps(body or self.request()).encode()
        process = self.server(**options)
        try:
            out, err = process.communicate(payload, timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)
            raise
        self.assertEqual(process.returncode, 0 if success else 2, (out[:1000], err[:1000]))
        response = json.loads(out)
        self.assertIs(response["ok"], success)
        self.assertEqual(response["version"], 1)
        if success:
            self.assertEqual(response["house"], self.foundation["house_id"])
            self.assertEqual(response["resident"], "alice")
            self.assertEqual(response["request"], (body or self.request())["request"])
            self.assertIn("result", response)
        else:
            self.assertEqual(set(response), {"version", "ok", "error"})
            self.assertTrue(response["error"])
        return response

    def append_request(self, operation, body, request="append-request"):
        return self.request("append", {"operation": operation, "body": body}, request)

    def test_identity_house_anchor_and_version_are_bound(self):
        self.exchange()
        before = self.record.read()[2]
        for changes in ({"resident": "bob"}, {"house": "another-house"},
                        {"version": True}, {"version": "1"}, {"version": 2},
                        {"request": ""}, {"request": "x" * 201}):
            with self.subTest(changes=changes):
                self.exchange(self.request(**changes), success=False)
        self.exchange(anchor="0" * 40, success=False)
        self.assertEqual(self.record.read()[2], before)

    def test_envelope_rejects_missing_extra_duplicate_and_nonfinite_fields(self):
        complete = self.request()
        for key in complete:
            with self.subTest(missing=key):
                body = dict(complete)
                body.pop(key)
                self.exchange(body, success=False)
        self.exchange(complete | {"actor": "bob"}, success=False)
        raws = [b"", b"[]", b"null", b"{", b"\xff", b"{} {}", b"[" * 2000 + b"0" + b"]" * 2000,
                json.dumps(complete).encode().replace(b'"version": 1', b'"version": 1, "version": 1'),
                json.dumps(complete).encode().replace(b'"data": {}', b'"data": {"x":NaN}'),
                json.dumps(complete).encode().replace(b'"data": {}', b'"data": {"x":Infinity}'),
                json.dumps(complete).encode().replace(b'"data": {}', b'"data": {"x":1e999}'),
                json.dumps(self.append_request("say", {"text": "Hello"})).encode().replace(
                    b'"text": "Hello"', b'"text":"First","text":"Second"')]
        before = self.record.read()[2]
        for raw in raws:
            with self.subTest(raw=raw[:100]):
                self.exchange(raw=raw, success=False)
        self.assertEqual(self.record.read()[2], before)

    def test_unknown_actions_extra_data_and_privileged_operations_fail(self):
        before = self.record.read()[2]
        forbidden = ("found", "restore", "bundle", "enroll", "exec", "seed", "adopt", "extract")
        for operation in forbidden:
            with self.subTest(operation=operation):
                self.exchange(self.request(operation), success=False)
                self.exchange(self.append_request(operation, {}), success=False)
        for action in ("verify", "status", "rules"):
            self.exchange(self.request(action, {"unexpected": 1}), success=False)
        self.exchange(self.request("append", {"operation": "say", "body": {"text": "Attack"},
                                               "actor": "bob"}), success=False)
        self.exchange(self.request("append", {"operation": "say"}), success=False)
        self.exchange(self.request("append", {"operation": "say", "body": []}), success=False)
        self.assertEqual(self.record.read()[2], before)

    def test_extra_operation_fields_cannot_choose_an_actor(self):
        before = self.record.read()[2]
        self.exchange(self.append_request("say", {"text": "Injected", "actor": "bob"}),
                      success=False)
        self.assertEqual(self.record.read()[2], before)
        self.exchange(self.append_request("say", {"text": "Bound correctly"}))
        event = self.record.read()[1][-1]
        self.assertEqual(event["actor"], "alice")
        self.assertEqual(event["data"], {"text": "Bound correctly"})

    def test_parallel_appends_and_exact_retries_keep_one_valid_history(self):
        payloads = [self.append_request("say", {"text": f"Message {i}"}, f"parallel-{i}")
                    for i in range(6)]
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(self.exchange, payloads))
        self.assertEqual({r["result"]["sequence"] for r in results}, set(range(4, 10)))
        retry = self.append_request("say", {"text": "Only once"}, "one-receipt")
        with ThreadPoolExecutor(max_workers=4) as pool:
            receipts = list(pool.map(self.exchange, [retry] * 4))
        self.assertEqual(sum(not r["result"]["replayed"] for r in receipts), 1)
        self.assertEqual(self.record.read()[0]["sequence"], 10)
        self.exchange(self.append_request("say", {"text": "Changed"}, "one-receipt"), success=False)
        receipt = self.exchange(self.request("receipt", {"id": "one-receipt"}))["result"]
        self.assertEqual(receipt["event"]["data"]["text"], "Only once")

    def test_rules_remain_sealed_when_proposed_or_forged(self):
        state = self.record.read()[0]
        self.exchange(self.append_request("propose", {"proposal": "amend", "base": state["rule_revision"],
            "text": "Resident becomes owner", "reason": "Attempted takeover"}, "proposal"))
        ballot = self.exchange(self.request("ballot", {"proposal": "amend"}))["result"]
        decoded = json.loads(base64.b64decode(ballot["payload_base64"], validate=True))
        self.assertEqual(decoded["house"], state["house_id"])
        before = self.record.read()[2]
        self.exchange(self.append_request("ratify", {"proposal": "amend", "signature": "Forged"}),
                      success=False)
        self.assertEqual(self.record.read()[2], before)
        rules = self.exchange(self.request("rules"))["result"]
        self.assertEqual(rules, {"revision": state["rule_revision"], "text": state["rules"]})

    def test_input_limit_and_unclosed_stdin_have_bounded_failures(self):
        self.exchange(raw=b" " * 8_000_001, success=False)
        process = self.server(timeout="1")
        started = time.monotonic()
        try:
            process.stdin.write(b'{"version":')
            process.stdin.flush()
            process.wait(timeout=4)
            out = process.stdout.read()
            err = process.stderr.read()
            self.assertEqual(process.returncode, 2, (out, err))
            self.assertFalse(json.loads(out)["ok"])
            self.assertLess(time.monotonic() - started, 4)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

    def test_deadline_includes_waiting_for_writer_lock(self):
        started = time.monotonic()
        with self.record.locked():
            self.exchange(self.append_request("say", {"text": "Blocked writer"}),
                          timeout="1", success=False)
        self.assertLess(time.monotonic() - started, 4)
        self.assertEqual(self.record.read()[0]["sequence"], 3)

    def test_git_environment_cannot_redirect_repository_or_write_trace(self):
        elsewhere = self.new_repo("elsewhere")
        trace = self.root / "injected-trace"
        env = {"GIT_DIR": str(elsewhere / ".git"), "GIT_WORK_TREE": str(elsewhere),
               "GIT_COMMON_DIR": str(elsewhere / ".git"), "GIT_OBJECT_DIRECTORY": str(elsewhere),
               "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.repositoryformatversion",
               "GIT_CONFIG_VALUE_0": "9999", "GIT_CONFIG_PARAMETERS": "malformed injection",
               "GIT_TRACE": str(trace), "GIT_TRACE_SETUP": str(trace)}
        self.exchange(self.append_request("say", {"text": "Trusted repository only"}), env=env)
        self.assertEqual(self.record.read()[1][-1]["data"]["text"], "Trusted repository only")
        self.assertFalse(trace.exists())
        self.assertFalse((elsewhere / ".git/refs/heads/house-ledger").exists())

    def test_original_ssh_command_is_rejected_and_python_path_is_ignored(self):
        marker = self.root / "executed"
        (self.root / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'w').write('unsafe')")
        self.exchange(env={"PYTHONPATH": str(self.root)})
        self.assertFalse(marker.exists())
        self.exchange(env={"SSH_ORIGINAL_COMMAND": "echo unrestricted shell"}, success=False)
        self.assertEqual(self.record.read()[0]["sequence"], 3)

    def test_artifact_body_is_bytes_not_a_server_filesystem_read(self):
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "file-token",
                           "expect": 0, "seconds": 60})
        secret = self.repo / "private.txt"
        secret.write_text("Must not disclose this local content")
        content = b"Explicitly submitted bytes"
        artifact = {"sha256": hashlib.sha256(content).hexdigest(),
                    "base64": base64.b64encode(content).decode()}
        self.exchange(self.append_request("finish", {"task": "work", "token": "file-token",
            "result": "Submitted", "artifacts": {"private.txt": artifact}}, "finished"))
        receipt = self.exchange(self.request("receipt", {"id": "finished"}))["result"]
        self.assertEqual(receipt["event"]["data"]["artifacts"]["private.txt"], artifact)
        page = self.exchange(self.request("read", {"after": 0, "limit": 200}))["result"]
        completion = next(e for e in page["events"] if e["op"] == "finish")
        self.assertEqual(completion["data"]["artifacts"]["private.txt"], {"sha256": artifact["sha256"]})
        self.assertEqual(secret.read_text(), "Must not disclose this local content")

    def test_only_utf8_json_is_accepted(self):
        for encoding in ("utf-16", "utf-32"):
            with self.subTest(encoding=encoding):
                self.exchange(raw=json.dumps(self.request()).encode(encoding), success=False)

    def test_closed_response_pipe_exits_cleanly(self):
        process = self.server()
        process.stdout.close()
        process.stdout = None
        request = self.append_request("say", {"text": "Accepted without receipt"}, "lost-response")
        _, err = process.communicate(json.dumps(request).encode(), timeout=5)
        self.assertEqual(process.returncode, 2, err.decode())
        self.assertNotIn(b"Exception ignored", err)
        receipt = self.exchange(self.request("receipt", {"id": "lost-response"}))["result"]
        self.assertEqual(receipt["event"]["data"]["text"], "Accepted without receipt")
        before = self.record.read()[2]
        retry = self.exchange(request)
        self.assertTrue(retry["result"]["replayed"])
        self.assertEqual(self.record.read()[2], before)

    def test_response_deadline_covers_an_undrained_pipe(self):
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "large-result",
                           "expect": 0, "seconds": 60})
        content = b"x" * 200000
        self.record.append("finish", "alice", {"task": "work", "token": "large-result",
            "result": "Done", "artifacts": {"large.txt": {
                "sha256": hashlib.sha256(content).hexdigest(),
                "base64": base64.b64encode(content).decode()}}}, "large-receipt")
        process = self.server(timeout="1")
        try:
            process.stdin.write(json.dumps(self.request("receipt", {"id": "large-receipt"})).encode())
            process.stdin.close()
            process.stdin = None
            process.wait(timeout=4)
            self.assertEqual(process.returncode, 2)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
        self.assertEqual(self.record.read()[0]["receipts"]["large-receipt"], 6)

    def test_home_git_configuration_and_path_cannot_control_git(self):
        hostile = self.root / "hostile-home"
        hostile.mkdir()
        (hostile / ".gitconfig").write_text("[invalid syntax\n")
        marker = self.root / "fake-git-executed"
        fake_git = hostile / "git"
        fake_git.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 42\n")
        fake_git.chmod(0o755)
        self.exchange(env={"HOME": str(hostile), "PATH": str(hostile)})
        self.assertFalse(marker.exists())

    def test_read_boundaries_and_unknown_receipts_are_structured_errors(self):
        first = self.exchange(self.request("read", {"after": None, "limit": 1}))["result"]
        self.assertEqual(first["through"], 1)
        self.assertTrue(first["has_more"])
        for data in ({"after": -1, "limit": 1}, {"after": True, "limit": 1},
                     {"after": 4, "limit": 1}, {"after": 0, "limit": True},
                     {"after": 0, "limit": 0}, {"after": 0, "limit": 201}):
            self.exchange(self.request("read", data), success=False)
        self.exchange(self.request("receipt", {"id": "missing"}), success=False)
