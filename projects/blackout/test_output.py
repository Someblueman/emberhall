"""Exercise closed output pipes through the standalone CLI process."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("blackout.py")


class OutputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.root = self.home / "source"
        self.root.mkdir()
        (self.root / "ember").write_bytes(b"keep me\n")
        self.manifest = self.home / "manifest.json"

    def run_cli(self, command, closed=None, unbuffered=False):
        argv = [sys.executable]
        if unbuffered:
            argv.append("-u")
        argv += [str(CLI), command, str(self.root), str(self.manifest)]
        if closed is None:
            return subprocess.run(argv, capture_output=True, text=True, timeout=10)
        reader, writer = os.pipe()
        os.close(reader)  # No reader exists before the child can write.
        try:
            return subprocess.run(argv, stdout=writer if closed == "stdout" else subprocess.PIPE,
                                  stderr=writer if closed == "stderr" else subprocess.PIPE,
                                  text=True, timeout=10)
        finally:
            os.close(writer)

    def test_create_closed_stdout_preserves_published_manifest(self):
        for unbuffered in (False, True):
            with self.subTest(unbuffered=unbuffered):
                result = self.run_cli("create", "stdout", unbuffered)
                original = self.manifest.read_bytes()
                verified = self.run_cli("verify")
                self.assertEqual(verified.returncode, 0, verified.stderr)
                self.assertEqual(json.loads(verified.stdout)["matched"], 1)
                retry = self.run_cli("create")
                self.assertEqual(retry.returncode, 2)
                self.assertEqual(self.manifest.read_bytes(), original)
                self.manifest.unlink()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertNotIn("Exception ignored", result.stderr)

    def test_verify_closed_stdout_for_matching_and_changed_backup(self):
        self.assertEqual(self.run_cli("create").returncode, 0)
        for content in (b"keep me\n", b"changed\n"):
            (self.root / "ember").write_bytes(content)
            for unbuffered in (False, True):
                with self.subTest(content=content, unbuffered=unbuffered):
                    result = self.run_cli("verify", "stdout", unbuffered)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertNotIn("Exception ignored", result.stderr)
                    self.assertEqual((self.root / "ember").read_bytes(), content)

    def test_missing_manifest_with_closed_stderr(self):
        for unbuffered in (False, True):
            with self.subTest(unbuffered=unbuffered):
                result = self.run_cli("verify", "stderr", unbuffered)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertFalse(self.manifest.exists())


if __name__ == "__main__":
    unittest.main()
