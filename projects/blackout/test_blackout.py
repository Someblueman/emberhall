"""Exercise the public CLI against real files; no mocked filesystem."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("blackout.py")


class BlackoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve()
        self.root = self.home / "source"
        self.root.mkdir()
        self.manifest = self.home / "manifest.json"

    def run_cli(self, command, root=None, manifest=None, code=0):
        result = subprocess.run(
            [sys.executable, str(CLI), command, str(root or self.root),
             str(manifest or self.manifest)], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout if code < 2 else result.stderr)

    def fixture(self):
        (self.root / "nested").mkdir()
        (self.root / "nested" / "winter.txt").write_text("remember the winter\n")
        (self.root / "snow ☃").write_bytes(bytes(range(256)))
        (self.root / "empty").touch()
        self.run_cli("create")

    def edit_manifest(self, change):
        value = json.loads(self.manifest.read_text())
        change(value)
        self.manifest.write_text(json.dumps(value))

    def test_round_trip_and_relocation(self):
        self.fixture()
        result = self.run_cli("verify")
        self.assertEqual(result, {"ok": True, "matched": 3,
                                  "missing": [], "changed": [], "extra": []})
        moved = self.home / "restored"
        self.root.rename(moved)
        self.assertTrue(self.run_cli("verify", root=moved)["ok"])

    def test_reports_all_differences_without_writing(self):
        self.fixture()
        (self.root / "empty").unlink()
        (self.root / "snow ☃").write_bytes(b"corrupt")
        (self.root / "new").write_text("extra")
        result = self.run_cli("verify", code=1)
        self.assertEqual(result, {"ok": False, "matched": 1, "missing": ["empty"],
                                  "changed": ["snow ☃"], "extra": ["new"]})
        self.assertEqual((self.root / "snow ☃").read_bytes(), b"corrupt")
        self.assertFalse((self.root / "empty").exists())

    def test_same_size_corruption(self):
        self.fixture()
        (self.root / "snow ☃").write_bytes(bytes(reversed(range(256))))
        self.assertEqual(self.run_cli("verify", code=1)["changed"], ["snow ☃"])

    def test_empty_directory(self):
        self.run_cli("create")
        self.assertEqual(self.run_cli("verify")["matched"], 0)

    def test_output_is_exclusive_and_outside_source(self):
        self.fixture()
        original = self.manifest.read_bytes()
        self.run_cli("create", code=2)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.run_cli("create", manifest=self.root / "inside.json", code=2)
        self.assertFalse((self.root / "inside.json").exists())
        self.assertEqual(list(self.home.glob(".blackout-*")), [])

    def test_rejects_file_and_directory_symlinks(self):
        target = self.home / "outside"
        target.write_text("do not read")
        for destination in (target, self.home):
            with self.subTest(destination=destination):
                link = self.root / "link"
                link.symlink_to(destination)
                self.assertIn("forbidden", self.run_cli("create", code=2)["error"])
                self.assertFalse(self.manifest.exists())
                link.unlink()

    def test_rejects_symlink_root_and_parent(self):
        alias = self.home / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        self.run_cli("create", root=alias, code=2)
        (self.root / "child").mkdir()
        self.run_cli("create", root=alias / "child", code=2)

    def test_dotdot_cannot_hide_invalid_directory_components(self):
        alias = self.home / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        for component in (alias, self.home / "missing", self.root):
            with self.subTest(component=component):
                self.run_cli("create", root=component / ".." / "source", code=2)
                self.assertFalse(self.manifest.exists())

    def test_verify_rejects_symlink_replacement(self):
        self.fixture()
        (self.root / "empty").unlink()
        (self.root / "empty").symlink_to(self.manifest)
        self.run_cli("verify", code=2)

    def test_fifo_is_rejected_without_hanging(self):
        os.mkfifo(self.root / "pipe")
        self.run_cli("create", code=2)

    def test_manifest_must_be_regular_without_symlink_components(self):
        self.fixture()
        fifo = self.home / "manifest.fifo"
        os.mkfifo(fifo)
        link = self.home / "manifest.link"
        link.symlink_to(self.manifest)
        alias = self.home / "alias"
        alias.symlink_to(self.home, target_is_directory=True)
        for manifest in (fifo, link, self.root, alias / self.manifest.name):
            with self.subTest(manifest=manifest):
                self.run_cli("verify", manifest=manifest, code=2)

    def test_nonportable_source_names(self):
        for name in ("new\nline", "a:b", "back\\slash"):
            with self.subTest(name=name):
                path = self.root / name
                path.touch()
                self.run_cli("create", code=2)
                path.unlink()

    def test_manifest_paths_are_untrusted(self):
        self.fixture()
        original = self.manifest.read_bytes()
        for path in ("../escape", "/etc/passwd", "a/../b", "a//b", "./a", "a/",
                     "C:/secret", "\\server\\secret", "line\nbreak", "", None, 12):
            with self.subTest(path=path):
                self.manifest.write_bytes(original)
                self.edit_manifest(lambda value: value["files"][0].update(path=path))
                self.run_cli("verify", code=2)

    def test_malformed_manifest_schema(self):
        self.fixture()
        original = self.manifest.read_bytes()
        mutations = [
            lambda m: m.update(version=True), lambda m: m.update(version=2),
            lambda m: m.update(format="other"), lambda m: m.update(unknown=1),
            lambda m: m.update(files={}), lambda m: m["files"].append(m["files"][0]),
            lambda m: m["files"][0].update(size=True),
            lambda m: m["files"][0].update(size=-1),
            lambda m: m["files"][0].update(size=0.0),
            lambda m: m["files"][0].update(sha256="0" * 63),
            lambda m: m["files"][0].update(sha256="g" * 64),
            lambda m: m["files"][0].update(sha256=None),
            lambda m: m["files"][0].update(extra="field"),
            lambda m: m["files"].append({**m["files"][0], "path": "empty/child"}),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                self.manifest.write_bytes(original)
                self.edit_manifest(mutate)
                self.run_cli("verify", code=2)

    def test_invalid_json_and_duplicate_keys(self):
        for content in ('{', '[]', 'null', '{"version": 1, "version": 2}',
                        '{"format":"blackout-kit","version":1,"files":[null]}'):
            with self.subTest(content=content):
                self.manifest.write_text(content)
                self.run_cli("verify", code=2)

    def test_missing_source_and_manifest(self):
        self.run_cli("create", root=self.home / "absent", code=2)
        self.run_cli("verify", code=2)


if __name__ == "__main__":
    unittest.main()
