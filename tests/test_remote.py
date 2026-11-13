"""Real client processes talking to an inert SSH executable, never a live account."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from house.remote import MAX_REQUEST, request_bytes, response

SOURCE = Path(__file__).resolve().parents[1]
FAKE_SSH = r'''
import json, os, pathlib, sys, time
request = json.load(sys.stdin)
with pathlib.Path(os.environ['FAKE_RECORD']).open('a') as record:
    record.write(json.dumps({'argv': sys.argv[1:], 'request': request}) + '\n')
mode = os.environ.get('FAKE_MODE', 'ok')
value = {'version': 1, 'ok': True, 'house': request['house'],
         'resident': request['resident'], 'request': request['request'],
         'result': {'echo': request['data']}}
if mode == 'timeout':
    time.sleep(60)
elif mode == 'large':
    sys.stdout.write('x' * 16_000_001)
elif mode == 'diagnostics':
    sys.stderr.write('SECRET-TRANSPORT-DIAGNOSTICS' * 4000)
elif mode == 'transport':
    sys.stderr.write('SECRET-TRANSPORT-DIAGNOSTICS')
    sys.exit(255)
elif mode == 'error':
    print(json.dumps({'version': 1, 'ok': False, 'error': 'lease expired'}))
    sys.exit(2)
elif mode == 'wrong_exit':
    print(json.dumps(value))
    sys.exit(2)
elif mode == 'duplicate':
    print(json.dumps(value)[:-1] + ', "version": 1}')
elif mode == 'nan':
    value['result'] = float('nan')
    print(json.dumps(value))
elif mode == 'overflow':
    print(json.dumps(value).replace('"result": {"echo": {}}', '"result": 1e999'))
elif mode == 'garbage':
    print('not JSON')
elif mode == 'trailing':
    print(json.dumps(value) + '{}')
elif mode == 'utf8':
    sys.stdout.buffer.write(b'\xff')
elif mode in ('house', 'resident', 'request'):
    value[mode] = 'wrong'
    print(json.dumps(value))
elif mode == 'bool_version':
    value['version'] = True
    print(json.dumps(value))
elif mode == 'extra':
    value['extra'] = 1
    print(json.dumps(value))
else:
    print(json.dumps(value))
'''


class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="house-remote-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        ssh = self.root / "ssh"
        ssh.write_text(f"#!{sys.executable}\n" + FAKE_SSH)
        ssh.chmod(0o700)
        self.record = self.root / "requests.jsonl"

    def cli(self, *args, mode="ok", code=0, host="emberhall-custodian"):
        result = subprocess.run(
            [sys.executable, "-m", "house.remote", "--host=" + host,
             "--house", "house-id", "--resident", "alice", *args],
            cwd=SOURCE, capture_output=True, text=True, timeout=8,
            env=dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ["PATH"],
                     FAKE_MODE=mode, FAKE_RECORD=str(self.record)))
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("SECRET-TRANSPORT-DIAGNOSTICS", result.stderr)
        return json.loads(result.stdout if code == 0 else result.stderr)

    def requests(self):
        return [json.loads(line) for line in self.record.read_text().splitlines()]

    def test_exact_request_and_hardened_argv_with_no_remote_command(self):
        data = {"operation": "say", "body": {"text": "hello; $(touch /never-execute)"}}
        result = self.cli("--request", "one", "append", "--data", json.dumps(data))
        observed = self.requests()[0]
        self.assertEqual(observed["request"], {"version": 1, "house": "house-id",
            "resident": "alice", "request": "one", "action": "append", "data": data})
        self.assertEqual(result["result"]["echo"], data)
        self.assertEqual(observed["argv"], ["-T", "-a", "-x", "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=yes", "-o", "ClearAllForwardings=yes",
            "-o", "RemoteCommand=none", "-o", "PermitLocalCommand=no", "-o", "ControlMaster=no",
            "-o", "ControlPath=none", "--", "emberhall-custodian"])

    def test_read_generates_id_but_append_requires_explicit_stable_id(self):
        error = self.cli("append", code=2)
        self.assertIn("explicit stable", error["error"])
        self.assertFalse(self.record.exists())
        result = self.cli("status")
        self.assertEqual(len(result["request"]), 36)
        self.assertEqual(self.requests()[0]["request"]["data"], {})

    def test_operator_config_is_one_argv_value_and_keeps_hardening(self):
        self.cli("status")
        default = self.requests()[0]["argv"]
        config = self.root / "operator config; literal"
        config.write_text("Host emberhall-custodian\n    HostName 127.0.0.1\n")
        self.cli("--ssh-config", str(config), "status")
        self.assertEqual(self.requests()[1]["argv"], ["-F", str(config), *default])

    def test_alias_cannot_inject_options_shell_or_remote_command(self):
        for host in ("-oProxyCommand=anything", "name;touch marker", "user@host", "name command",
                     "host\ncommand", "$(touch marker)", "a" * 254):
            with self.subTest(host=host):
                self.cli("status", host=host, code=2)
                self.assertFalse(self.record.exists())

    def test_data_file_and_untrusted_json_are_checked_before_connecting(self):
        path = self.root / "data.json"
        for content in ('[]', '{', '{"a":1,"a":2}', '{"body":{"x":1,"x":2}}',
                        '{"n":NaN}', '{"n":Infinity}', '{"n":-Infinity}', '{"n":1e999}',
                        '{"text":"\\ud800"}'):
            with self.subTest(content=content):
                path.write_text(content)
                self.cli("status", "--data-file", str(path), code=2)
                self.assertFalse(self.record.exists())
        path.write_text('{"after":null,"limit":10}')
        result = self.cli("read", "--data-file", str(path))
        self.assertEqual(result["result"]["echo"], {"after": None, "limit": 10})

    def test_data_file_fifo_and_symlink_fail_without_hanging(self):
        fifo = self.root / "fifo"
        os.mkfifo(fifo)
        regular = self.root / "regular"
        regular.write_text("{}")
        link = self.root / "link"
        link.symlink_to(regular)
        for path in (fifo, link, self.root):
            with self.subTest(path=path):
                self.cli("status", "--data-file", str(path), code=2)
                self.assertFalse(self.record.exists())

    def test_complete_request_limit_includes_envelope(self):
        path = self.root / "large.json"
        path.write_text(json.dumps({"text": "x" * MAX_REQUEST}))
        self.cli("status", "--data-file", str(path), code=2)
        self.assertFalse(self.record.exists())
        path.write_text(json.dumps({"text": "x" * (MAX_REQUEST - 30)}))
        error = self.cli("status", "--data-file", str(path), code=2)
        self.assertIn("complete request", error["error"])
        self.assertFalse(self.record.exists())

    def test_corrupt_and_unbound_responses_fail_closed(self):
        for mode in ("house", "resident", "request", "bool_version", "extra", "duplicate",
                     "nan", "overflow", "garbage", "trailing", "utf8", "wrong_exit"):
            with self.subTest(mode=mode):
                self.cli("status", mode=mode, code=2)

    def test_server_error_is_surfaced_but_transport_diagnostics_are_not(self):
        error = self.cli("status", mode="error", code=2)
        self.assertIn("lease expired", error["error"])
        error = self.cli("status", mode="transport", code=2)
        self.assertIn("status 255", error["error"])

    def test_limits_timeout_and_lost_receipt_never_trigger_retry(self):
        for mode, expected in (("large", "16,000,000"), ("diagnostics", "65,536"),
                               ("timeout", "timed out")):
            with self.subTest(mode=mode):
                before = len(self.requests()) if self.record.exists() else 0
                timeout = "0.3" if mode == "timeout" else "3"
                error = self.cli("--request", "same-id", "--timeout", timeout, "append",
                                 mode=mode, code=2)
                self.assertEqual(len(self.requests()), before + 1)
                self.assertIn(expected, error["error"])
                self.assertEqual(error["request"], "same-id")
                self.assertIn("may already be accepted", error["recovery"])
                self.assertIn("same ID", error["recovery"])

    def test_large_payload_flows_through_real_pipes_without_deadlock(self):
        path = self.root / "data.json"
        body = {"operation": "say", "body": {"text": "x" * 1_000_000}}
        path.write_text(json.dumps(body))
        result = self.cli("--request", "large-message", "append", "--data-file", str(path))
        self.assertEqual(result["result"]["echo"], body)

    def test_invalid_timeout_and_id_reject_before_transport(self):
        for timeout in ("0", "-1", "301", "nan", "inf"):
            with self.subTest(timeout=timeout):
                self.cli("--timeout", timeout, "status", code=2)
                self.assertFalse(self.record.exists())
        for request in ("", "x" * 201):
            with self.subTest(request=request):
                self.cli("--request", request, "append", code=2)
                self.assertFalse(self.record.exists())

    def test_closed_output_exits_two_without_shutdown_reflush_or_retry(self):
        for mode, closed in (("ok", "stdout"), ("error", "stderr")):
            with self.subTest(mode=mode, closed=closed):
                before = len(self.requests()) if self.record.exists() else 0
                process = subprocess.Popen(
                    [sys.executable, "-m", "house.remote", "--host", "fixture",
                     "--house", "house-id", "--resident", "alice", "--request", "closed-output",
                     "append"], cwd=SOURCE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    env=dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ["PATH"],
                             FAKE_MODE=mode, FAKE_RECORD=str(self.record)))
                getattr(process, closed).close()
                try:
                    self.assertEqual(process.wait(timeout=5), 2)
                    remaining = process.stderr if closed == "stdout" else process.stdout
                    self.assertEqual(remaining.read(), b"")
                    self.assertEqual(len(self.requests()), before + 1)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                    process.stdout.close()
                    process.stderr.close()

    def test_envelope_version_and_error_shape_are_strict(self):
        for value, code in (({"version": True}, 0),
                            ({"version": 1, "ok": False, "error": "bad", "extra": 1}, 2),
                            ({"version": 1, "ok": False, "error": 12}, 2),
                            ({"version": 1, "ok": False, "error": "bad"}, 0)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    response(json.dumps(value).encode(), code, "h", "r", "q")
        with self.assertRaises(ValueError):
            request_bytes("h", "r", "q", "status", {"n": float("nan")})


if __name__ == "__main__":
    unittest.main()
