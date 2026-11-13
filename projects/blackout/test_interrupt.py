"""Send real SIGINT at deterministic scan and manifest-publication boundaries."""
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("blackout.py")
DRIVER = r'''
import os, runpy, signal, sys
phase, ready, cli, *args = sys.argv[1:]
def gate():
    os.write(int(ready), b"ready")
    while True:
        signal.pause()
if phase == "scan":
    original = os.read
    def read(*args, **kwargs):
        gate()
        return original(*args, **kwargs)
    os.read = read
else:
    original = os.link
    def link(*args, **kwargs):
        if phase == "before-publish":
            gate()
        result = original(*args, **kwargs)
        gate()
        return result
    os.link = link
sys.argv = [cli, *args]
runpy.run_path(cli, run_name="__main__")
'''


@unittest.skipUnless(os.name == "posix", "Blackout and SIGINT checks require POSIX")
class InterruptTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.root = self.home / "archive"
        self.root.mkdir()
        self.file = self.root / "keep"
        self.file.write_bytes(b"bytes worth keeping\n")
        self.manifest = self.home / "manifest.json"

    def cli(self, command):
        return subprocess.run([sys.executable, str(CLI), command, str(self.root), str(self.manifest)],
                              capture_output=True, text=True, timeout=10)

    def interrupt(self, command, phase, closed_stderr=False):
        before = (self.file.read_bytes(), self.file.stat())
        reader, writer = os.pipe()
        error_reader, error_writer = os.pipe()
        os.close(error_reader)
        process = subprocess.Popen([sys.executable, "-c", DRIVER, phase, str(writer), str(CLI),
                                    command, str(self.root), str(self.manifest)],
                                   pass_fds=(writer,), stdout=subprocess.PIPE,
                                   stderr=error_writer if closed_stderr else subprocess.PIPE, text=True)
        os.close(writer)
        os.close(error_writer)
        try:
            self.assertTrue(select.select([reader], [], [], 10)[0], "child never reached boundary")
            self.assertEqual(os.read(reader, 5), b"ready")
            process.send_signal(signal.SIGINT)
            out, err = process.communicate(timeout=10)
        finally:
            os.close(reader)
            if process.poll() is None:
                process.kill()
                process.communicate()
        self.assertEqual(self.file.read_bytes(), before[0])
        self.assertEqual((self.file.stat().st_mode, self.file.stat().st_mtime_ns),
                         (before[1].st_mode, before[1].st_mtime_ns))
        self.assertEqual(out, "")
        self.assertEqual(process.returncode, 130, err)
        if not closed_stderr:
            self.assertEqual(json.loads(err), {"error": "interrupted"})
        self.assertEqual(list(self.home.glob(".blackout-*")), [])

    def test_scan_interrupts_all_commands_without_touching_input(self):
        self.interrupt("create", "scan")
        self.assertFalse(self.manifest.exists())
        self.assertEqual(self.cli("create").returncode, 0)
        saved = self.manifest.read_bytes()
        for command in ("verify", "plan"):
            with self.subTest(command=command):
                self.interrupt(command, "scan")
                self.assertEqual(self.manifest.read_bytes(), saved)
                self.assertEqual(self.cli(command).returncode, 0)

    def test_cancel_before_publish_removes_only_staging_file(self):
        self.interrupt("create", "before-publish")
        self.assertFalse(self.manifest.exists())
        self.assertEqual(self.cli("create").returncode, 0)

    def test_cancel_after_publish_preserves_complete_exclusive_manifest(self):
        self.interrupt("create", "after-publish")
        saved = self.manifest.read_bytes()
        self.assertEqual(self.cli("verify").returncode, 0)
        self.assertEqual(self.cli("create").returncode, 2)
        self.assertEqual(self.manifest.read_bytes(), saved)

    def test_closed_error_pipe_does_not_mask_cancellation(self):
        self.interrupt("create", "scan", closed_stderr=True)
        self.assertFalse(self.manifest.exists())


if __name__ == "__main__":
    unittest.main()
