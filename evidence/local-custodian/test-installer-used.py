"""Local operator installation and enrollment in disposable repositories."""
import concurrent.futures
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import unittest

from tests.support import HouseCase, SOURCE


@unittest.skipUnless(sys.platform == "darwin", "macOS launch-agent installation")
class LocalCustodianTests(HouseCase):
    def setUp(self):
        super().setUp()
        shutil.copytree(SOURCE / "house", self.repo / "house", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(SOURCE / "custodian_entry.py", self.repo / "custodian_entry.py")
        self.record.git("add", "house", "custodian_entry.py")
        self.record.git("-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm", "Runtime")
        self.installation = self.root / "custodian"

    def operator(self, *args):
        return subprocess.run([sys.executable, str(SOURCE / "scripts/local_custodian.py"),
                               "--root", str(self.installation), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=20)

    def prepare(self):
        result = self.operator("prepare", "--source", str(self.repo), "--port", "22345")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_prepare_pins_runtime_keeps_journal_and_does_not_activate(self):
        before = self.record.read()
        manifest = self.prepare()
        self.assertEqual(self.record.read(), before)
        self.assertEqual(manifest["anchor"], self.foundation["anchor"])
        self.assertEqual(manifest["source"], str(self.repo.resolve()))
        config = (self.installation / "sshd_config").read_text()
        self.assertIn("ListenAddress 127.0.0.1\n", config)
        self.assertIn("StrictModes yes\n", config)
        self.assertIn("DisableForwarding yes\n", config)
        self.assertEqual((self.installation / "host_key").stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.installation / "release/house/record.py").read_bytes(),
                         (self.repo / "house/record.py").read_bytes())
        with (self.installation / "local.emberhall.custodian.plist").open("rb") as stream:
            plist = plistlib.load(stream)
        self.assertTrue(plist["KeepAlive"])
        self.assertEqual(plist["ProgramArguments"][:2], ["/usr/bin/env", "-i"])
        again = self.operator("prepare", "--source", str(self.repo))
        self.assertEqual(again.returncode, 2)
        self.assertEqual(self.record.read(), before)

    def test_dirty_runtime_is_rejected_before_installation(self):
        with (self.repo / "house/model.py").open("a") as stream:
            stream.write("\n# changed\n")
        result = self.operator("prepare", "--source", str(self.repo))
        self.assertEqual(result.returncode, 2)
        self.assertIn("runtime must match", result.stderr)
        self.assertFalse(self.installation.exists())

    def test_concurrent_enrollment_retains_distinct_restricted_bindings(self):
        self.prepare()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda name: self.operator("enroll", name),
                                    ["alice", "bob", "carol", "dana"]))
        self.assertTrue(all(r.returncode == 0 for r in results), [r.stderr for r in results])
        lines = (self.installation / "authorized_keys").read_text().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(len({line.split("ssh-ed25519 ")[1] for line in lines}), 4)
        self.assertTrue(all(line.startswith('restrict,command="') for line in lines))
        for resident in ("alice", "bob", "carol", "dana"):
            home = self.installation / "residents" / resident
            self.assertIn(f"--resident {resident} ", (home / "launch").read_text())
            self.assertEqual((home / "key").stat().st_mode & 0o777, 0o600)
            response = subprocess.run([str(home / "launch")], input="", capture_output=True,
                                      text=True, env=dict(os.environ, SSH_ORIGINAL_COMMAND="touch /tmp/never"))
            self.assertEqual(response.returncode, 2)
            self.assertIn("remote commands are not accepted", response.stderr)
        before = (self.installation / "authorized_keys").read_bytes()
        self.assertEqual(self.operator("enroll", "alice").returncode, 2)
        self.assertEqual(self.operator("enroll", "../../escape").returncode, 2)
        self.assertEqual((self.installation / "authorized_keys").read_bytes(), before)
