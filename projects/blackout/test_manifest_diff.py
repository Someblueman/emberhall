"""Accept the offline manifest comparison through real subprocess CLI calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("blackout.py")


def entry(path, content=b"recorded bytes", size=None):
    return {"path": path, "size": len(content) if size is None else size,
            "sha256": hashlib.sha256(content).hexdigest()}


@unittest.skipUnless(os.name == "posix", "Blackout requires POSIX")
class ManifestDiffTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.old = self.home / "old.json"
        self.new = self.home / "new.json"

    def manifest(self, path, files):
        path.write_text(json.dumps({"format": "blackout-kit", "version": 1,
                                    "files": files}), encoding="utf-8")

    def snapshot(self):
        result = {}
        for path in self.home.rglob("*"):
            info = path.lstat()
            value = (os.readlink(path) if path.is_symlink() else
                     path.read_bytes() if path.is_file() else None)
            result[str(path.relative_to(self.home))] = (
                value, info.st_mode, info.st_size, info.st_mtime_ns)
        return result

    def diff(self, old=None, new=None, code=0):
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(CLI), "diff", str(old or self.old),
                                 str(new or self.new)], capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(self.snapshot(), before, "diff changed an input or created a file")
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if code == 2:
            self.assertEqual(result.stdout, "", "invalid input emitted a partial result")
            error = json.loads(result.stderr)
            self.assertEqual(set(error), {"error"})
            self.assertIsInstance(error["error"], str)
            self.assertTrue(error["error"])
            return error
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_equality_ignores_record_order_and_needs_no_archive(self):
        # These recorded paths do not exist beside either saved inventory.
        files = [entry("unmounted/nested/item"), entry("empty", b"")]
        self.manifest(self.old, files)
        self.manifest(self.new, list(reversed(files)))
        expected = {"ok": True, "missing": [], "extra": [], "changed": [], "matched": 2}
        self.assertEqual(self.diff(), expected)
        self.assertEqual(self.diff(self.new, self.old), expected)
        self.assertEqual(self.diff(self.old, self.old), expected)

    def test_direction_sorting_size_and_same_size_hash_changes(self):
        self.manifest(self.old, [entry("z-missing"), entry("size"), entry("same"),
                                 entry("hash", b"ab"), entry("a-missing")])
        self.manifest(self.new, [entry("z-extra"), entry("hash", b"cd"), entry("same"),
                                 entry("size", size=999), entry("a-extra")])
        forward = {"ok": False, "missing": ["a-missing", "z-missing"],
                   "extra": ["a-extra", "z-extra"], "changed": ["hash", "size"], "matched": 1}
        self.assertEqual(self.diff(code=1), forward)
        self.assertEqual(self.diff(code=1), forward)
        self.assertEqual(self.diff(self.new, self.old, code=1),
                         {**forward, "missing": forward["extra"], "extra": forward["missing"]})

    def test_empty_inventories_and_one_sided_entries(self):
        self.manifest(self.old, [])
        self.manifest(self.new, [])
        self.assertEqual(self.diff(), {"ok": True, "missing": [], "extra": [],
                                       "changed": [], "matched": 0})
        self.manifest(self.new, [entry("added")])
        self.assertEqual(self.diff(code=1), {"ok": False, "missing": [], "extra": ["added"],
                                            "changed": [], "matched": 0})
        self.assertEqual(self.diff(self.new, self.old, code=1),
                         {"ok": False, "missing": ["added"], "extra": [],
                          "changed": [], "matched": 0})

    def test_case_and_unicode_spelling_are_exact_without_rename_inference(self):
        self.manifest(self.old, [entry("Report.txt"), entry("caf\u00e9.txt"), entry("same")])
        self.manifest(self.new, [entry("report.txt"), entry("cafe\u0301.txt"), entry("same")])
        self.assertEqual(self.diff(code=1),
                         {"ok": False, "missing": ["Report.txt", "caf\u00e9.txt"],
                          "extra": ["cafe\u0301.txt", "report.txt"], "changed": [], "matched": 1})
        # Inventories can record both spellings even on a normalizing host filesystem.
        both = [entry("caf\u00e9.txt"), entry("cafe\u0301.txt"), entry("A"), entry("a")]
        self.manifest(self.old, both)
        self.manifest(self.new, list(reversed(both)))
        self.assertEqual(self.diff()["matched"], 4)

    def test_strict_loader_rejects_invalid_content_on_either_side(self):
        valid = {"format": "blackout-kit", "version": 1, "files": [entry("keep")]}
        invalid = [b"{", b"\xff", b'{}', b'{"version":1,"version":1}',
                   json.dumps({**valid, "version": True}).encode(),
                   json.dumps({**valid, "files": [entry("../escape")]}).encode(),
                   json.dumps({**valid, "files": [entry("x", size=-1)]}).encode(),
                   json.dumps({**valid, "files": [{**entry("x"), "sha256": "bad"}]}).encode(),
                   json.dumps({**valid, "files": [entry("x"), entry("x")]}).encode(),
                   json.dumps({**valid, "files": [entry("x"), entry("x/child")]}).encode()]
        for side in (self.old, self.new):
            for content in invalid:
                with self.subTest(side=side.name, content=content):
                    self.manifest(self.old, valid["files"])
                    self.manifest(self.new, valid["files"])
                    side.write_bytes(content)
                    self.diff(code=2)

    def test_unsafe_manifest_locations_on_either_side_do_not_hang(self):
        self.manifest(self.old, [entry("keep")])
        self.manifest(self.new, [entry("keep")])
        link = self.home / "link.json"
        link.symlink_to(self.old)
        fifo = self.home / "fifo"
        os.mkfifo(fifo)
        alias = self.home / "alias"
        alias.symlink_to(self.home, target_is_directory=True)
        for unsafe in (link, fifo, self.home, self.home / "absent", alias / "old.json"):
            for side in ("old", "new"):
                with self.subTest(unsafe=unsafe, side=side):
                    self.diff(**{side: unsafe}, code=2)

    def test_closed_output_pipes_return_two_and_preserve_inputs(self):
        self.manifest(self.old, [entry("keep")])
        self.manifest(self.new, [entry("keep")])
        for scenario in ("equal", "different", "invalid"):
            with self.subTest(scenario=scenario):
                if scenario == "different":
                    self.manifest(self.new, [])
                elif scenario == "invalid":
                    self.new.write_bytes(b"{")
                before = self.snapshot()
                reader, writer = os.pipe()
                os.close(reader)
                try:
                    result = subprocess.run(
                        [sys.executable, str(CLI), "diff", str(self.old), str(self.new)],
                        stdout=writer if scenario != "invalid" else subprocess.PIPE,
                        stderr=writer if scenario == "invalid" else subprocess.PIPE,
                        text=True, timeout=10)
                finally:
                    os.close(writer)
                self.assertEqual(result.returncode, 2, result)
                self.assertEqual(result.stderr if scenario != "invalid" else result.stdout, "")
                self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
