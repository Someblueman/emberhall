"""Opt-in real loopback OpenSSH checks, with temporary keys/config and no host edits."""
import getpass
import json
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess
import sys
import time
import unittest

from tests.support import HouseCase, SOURCE


@unittest.skipUnless(os.environ.get("HOUSE_SSH_TESTS") == "1" and Path("/usr/sbin/sshd").exists(),
                     "set HOUSE_SSH_TESTS=1 to run the disposable loopback SSH acceptance")
class CustodianSSHTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.log = (self.root / "sshd.log").open("w+")
        self.addCleanup(self.log.close)
        for key in ("host", "resident", "outsider"):
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f",
                            str(self.root / key)], check=True, capture_output=True)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.port = probe.getsockname()[1]
        command = shlex.join([sys.executable, "-I", str(SOURCE / "custodian_entry.py"),
                             "--repo", str(self.repo), "--expect-anchor", self.foundation["anchor"],
                             "--resident", "alice", "--timeout", "5"])
        escaped = command.replace("\\", "\\\\").replace('"', '\\"')
        (self.root / "authorized").write_text(
            f'restrict,command="{escaped}" ' + (self.root / "resident.pub").read_text())
        os.chmod(self.root / "authorized", 0o600)
        self.known = self.root / "known"
        self.known.write_text(f"[127.0.0.1]:{self.port} " + (self.root / "host.pub").read_text())
        # StrictModes=no is fixture-only: this same-user temp tree does not claim
        # production ownership isolation. The deployment template requires yes.
        config = f"""Port {self.port}
ListenAddress 127.0.0.1
HostKey {self.root}/host
PidFile {self.root}/pid
AuthorizedKeysFile {self.root}/authorized
StrictModes no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
UsePAM no
PermitRootLogin no
AllowUsers {getpass.getuser()}
PermitUserEnvironment no
PermitUserRC no
LogLevel VERBOSE
"""
        (self.root / "server").write_text(config)
        self.client = self.root / "client"
        self.client.write_text(f"""Host test-custodian
 HostName 127.0.0.1
 Port {self.port}
 User {getpass.getuser()}
 IdentityFile {self.root}/resident
 IdentityAgent none
 IdentitiesOnly yes
 UserKnownHostsFile {self.known}
 GlobalKnownHostsFile /dev/null
 StrictHostKeyChecking yes
 BatchMode yes
""")
        self.daemon = subprocess.Popen(["/usr/sbin/sshd", "-D", "-e", "-f", str(self.root / "server")],
                                       stdout=subprocess.DEVNULL, stderr=self.log)
        self.addCleanup(self.stop_daemon)
        for _ in range(100):
            if self.daemon.poll() is not None:
                break
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.1):
                    return
            except OSError:
                time.sleep(0.02)
        self.log.seek(0)
        self.fail("Disposable sshd did not start: " + self.log.read())

    def stop_daemon(self):
        if self.daemon.poll() is None:
            self.daemon.terminate()
        self.daemon.wait(timeout=5)

    def remote(self, action, data, resident="alice", request="ssh-request"):
        return subprocess.run([sys.executable, "-m", "house.remote", "--ssh-config", str(self.client),
                               "--host", "test-custodian", "--house", self.foundation["house_id"],
                               "--resident", resident, "--request", request, "--timeout", "10",
                               action, "--data", json.dumps(data)],
                              cwd=SOURCE, capture_output=True, text=True, timeout=15)

    def ssh(self, options, command=None, body=None):
        args = ["ssh", "-F", str(self.client), *options, "test-custodian"]
        if command:
            args.extend(command)
        return subprocess.run(args, input=body, capture_output=True, text=True, timeout=10)

    def test_shipped_client_appends_once_and_recovers_receipt_over_ssh(self):
        data = {"operation": "say", "body": {"text": "Accepted through real SSH"}}
        first = self.remote("append", data)
        self.assertEqual(first.returncode, 0, (first.stdout, first.stderr))
        head = self.record.read()[2]
        second = self.remote("append", data)
        self.assertEqual(second.returncode, 0, (second.stdout, second.stderr))
        self.assertTrue(json.loads(second.stdout)["result"]["replayed"])
        self.assertEqual(self.record.read()[2], head)
        receipt = self.remote("receipt", {"id": "ssh-request"}, request="inspect")
        self.assertEqual(receipt.returncode, 0, receipt.stderr)
        self.assertEqual(json.loads(receipt.stdout)["result"]["event"]["actor"], "alice")

    def test_wire_identity_cannot_override_key_binding(self):
        before = self.record.read()[2]
        forged = self.remote("append", {"operation": "say", "body": {"text": "Forged"}},
                             resident="bob")
        self.assertEqual(forged.returncode, 2)
        self.assertIn("resident binding mismatch", forged.stderr)
        self.assertEqual(self.record.read()[2], before)

    def test_shell_and_subsystem_requests_cannot_execute_arbitrary_commands(self):
        marker = self.root / "must-not-exist"
        before = self.record.read()[2]
        result = self.ssh(["-T"], [f"touch {shlex.quote(str(marker))}"])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(marker.exists())
        subsystem = self.ssh(["-T", "-s"], ["sftp"])
        self.assertNotEqual(subsystem.returncode, 0)
        self.assertEqual(self.record.read()[2], before)

    def test_restricted_key_denies_pty_and_remote_forwarding(self):
        pty = self.ssh(["-tt"], body="{}")
        self.assertIn("PTY allocation request failed", pty.stderr)
        forward = self.ssh(["-T", "-N", "-o", "ExitOnForwardFailure=yes",
                            "-R", "0:127.0.0.1:9"])
        self.assertNotEqual(forward.returncode, 0)
        self.assertIn("forwarding failed", forward.stderr)

    def test_changed_host_key_blocks_shipped_client_before_mutation(self):
        before = self.record.read()[2]
        self.known.write_text(f"[127.0.0.1]:{self.port} " + (self.root / "outsider.pub").read_text())
        result = self.remote("append", {"operation": "say", "body": {"text": "Must not arrive"}})
        self.assertEqual(result.returncode, 2)
        self.assertIn("transport exited", result.stderr)
        self.assertEqual(self.record.read()[2], before)
