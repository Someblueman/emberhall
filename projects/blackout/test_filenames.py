"""Real filesystem boundaries that normalization-insensitive hosts cannot witness."""
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unicodedata


CLI = Path(__file__).with_name("blackout.py")


@unittest.skipUnless(os.name == "posix", "Blackout requires POSIX")
class FilenameTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.root = self.home / "archive"
        self.root.mkdir()
        self.manifest = self.home / "manifest.json"

    def cli(self, command, code=0, manifest=None):
        result = subprocess.run([sys.executable, str(CLI), command, str(self.root),
                                 str(manifest or self.manifest)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if code == 2:
            self.assertEqual(result.stdout, "", "unsafe input must not emit a partial result")
        else:
            self.assertEqual(result.stderr, "")
        return json.loads(result.stderr if code == 2 else result.stdout)

    def snapshot(self):
        snapshot = {}
        for name in os.listdir(os.fsencode(self.root)):
            path = os.fsencode(self.root) + b"/" + name
            info = os.stat(path)
            with open(path, "rb") as stream:
                snapshot[name] = (stream.read(), info.st_size, info.st_mode, info.st_mtime_ns)
        return snapshot

    def test_invalid_utf8_filename_rejects_all_commands_without_partial_output(self):
        (self.root / "valid").write_bytes(b"keep these bytes\n")
        self.cli("create")
        manifest = self.manifest.read_bytes()
        bad = os.fsencode(self.root) + b"/\xff.txt"
        try:
            with open(bad, "xb") as stream:
                stream.write(b"keep invalid-name input too\n")
        except OSError as error:
            if error.errno in (errno.EPERM, errno.EINVAL, errno.EILSEQ):
                self.skipTest(f"filesystem refuses invalid UTF-8 filename: errno {error.errno}")
            raise
        before = self.snapshot()
        self.assertIn(b"\xff.txt", before)
        new_manifest = self.home / "new.json"
        for command in ("create", "verify", "plan"):
            with self.subTest(command=command):
                result = self.cli(command, 2, new_manifest if command == "create" else self.manifest)
                self.assertEqual(result, {"error": "file path is not valid UTF-8"})
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.manifest.read_bytes(), manifest)
                self.assertFalse(new_manifest.exists())
                self.assertEqual(list(self.home.glob(".blackout-*")), [])

    def test_nfc_and_nfd_names_remain_distinct_when_filesystem_supports_both(self):
        nfc = "caf\u00e9.txt"
        nfd = unicodedata.normalize("NFD", nfc)
        (self.root / nfc).write_bytes(b"NFC content\n")
        try:
            with (self.root / nfd).open("xb") as stream:
                stream.write(b"different NFD content\n")
        except FileExistsError:
            self.skipTest("filesystem aliases NFC and NFD names")
        before = self.snapshot()
        self.assertEqual(set(before), {nfc.encode(), nfd.encode()})
        self.cli("create")
        saved = self.manifest.read_bytes()
        self.assertEqual({item["path"] for item in json.loads(saved)["files"]}, {nfc, nfd})
        for command in ("verify", "plan"):
            result = self.cli(command)
            self.assertEqual(result["matched"], 2)
            self.assertTrue(result["ok"])
            self.assertEqual(self.snapshot(), before)
        # Delete only a synthetic fixture member, then check exact missing spelling.
        (self.root / nfd).unlink()
        remaining = self.snapshot()
        for command in ("verify", "plan"):
            result = self.cli(command, 1)
            self.assertEqual(result["missing"], [nfd])
            self.assertEqual(result["matched"], 1)
            self.assertEqual(result["extra"], [])
            if command == "plan":
                self.assertEqual(result["unrecoverable"], [nfd])
            self.assertEqual(self.snapshot(), remaining)
            self.assertEqual(self.manifest.read_bytes(), saved)


if __name__ == "__main__":
    unittest.main()
