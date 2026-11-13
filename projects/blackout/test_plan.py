"""Exercise the read-only recovery-plan CLI against real files; no mocked filesystem."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("blackout.py")


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve()
        self.root = self.home / "archive"
        self.root.mkdir()
        self.manifest = self.home / "manifest.json"

    def run_cli(self, command, root=None, manifest=None, code=None):
        result = subprocess.run(
            [sys.executable, str(CLI), command, str(root or self.root),
             str(manifest or self.manifest)], capture_output=True, text=True, timeout=10)
        if code is not None:
            self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def create_and_load(self):
        result = self.run_cli("create")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout if result.stdout.strip().startswith("{") else result.stdout)

    def plan(self, code=None):
        result = self.run_cli("plan", code=code)
        if result.returncode < 2:
            return result, json.loads(result.stdout)
        return result, json.loads(result.stderr)

    def snapshot(self):
        data = {}
        for node in sorted(self.root.rglob("*")):
            if node.is_symlink():
                data[str(node.relative_to(self.root))] = ("symlink", str(os.readlink(node)))
            elif node.is_dir():
                data[str(node.relative_to(self.root))] = ("dir",)
            elif node.is_file():
                data[str(node.relative_to(self.root))] = node.read_bytes()
        return data

    def fixture_nested(self):
        (self.root / "a").mkdir()
        (self.root / "a" / "b").mkdir(parents=True)
        (self.root / "a" / "b" / "keep.txt").write_bytes(b"nested bytes\n")
        (self.root / "top.txt").write_bytes(b"top\n")
        self.run_cli("create", code=0)

    def test_clean_archive_is_ok(self):
        self.fixture_nested()
        _, data = self.plan(code=0)
        self.assertEqual(data["ok"], True)
        self.assertEqual(data["missing"], [])
        self.assertEqual(data["changed"], [])
        self.assertEqual(data["extra"], [])
        self.assertEqual(data["restores"], [])
        self.assertEqual(data["ambiguous"], [])
        self.assertEqual(data["unrecoverable"], [])

    def test_missing_nested_is_unrecoverable(self):
        self.fixture_nested()
        (self.root / "a" / "b" / "keep.txt").unlink()
        before = self.snapshot()
        _, data = self.plan(code=1)
        self.assertEqual(data["ok"], False)
        self.assertEqual(data["missing"], ["a/b/keep.txt"])
        self.assertEqual(len(data["restores"]), 1)
        entry = data["restores"][0]
        self.assertEqual(entry["target"], "a/b/keep.txt")
        self.assertEqual(entry["status"], "missing")
        self.assertEqual(entry["candidates"], [])
        self.assertFalse(entry["recoverable"])
        self.assertFalse(entry["ambiguous"])
        self.assertEqual(data["unrecoverable"], ["a/b/keep.txt"])
        self.assertEqual(data["ambiguous"], [])
        self.assertEqual(self.snapshot(), before)

    def test_renamed_file_suggests_extra_candidate(self):
        self.fixture_nested()
        original = self.root / "a" / "b" / "keep.txt"
        original_bytes = original.read_bytes()
        renamed = self.root / "a" / "b" / "renamed.txt"
        original.rename(renamed)
        before = self.snapshot()
        _, data = self.plan(code=1)
        self.assertEqual(data["missing"], ["a/b/keep.txt"])
        self.assertEqual(data["extra"], ["a/b/renamed.txt"])
        self.assertEqual(len(data["restores"]), 1)
        entry = data["restores"][0]
        self.assertEqual(entry["candidates"], ["a/b/renamed.txt"])
        self.assertTrue(entry["recoverable"])
        self.assertFalse(entry["ambiguous"])
        self.assertEqual(entry["status"], "missing")
        # Read-only: nothing restored or renamed by plan.
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(original.exists())
        self.assertEqual(renamed.read_bytes(), original_bytes)

    def test_changed_corruption_restorable_from_extra(self):
        self.fixture_nested()
        target = self.root / "top.txt"
        original_bytes = target.read_bytes()
        target.write_bytes(b"corrupt\n")
        (self.root / "rescue").mkdir()
        (self.root / "rescue" / "copy.txt").write_bytes(original_bytes)
        before = self.snapshot()
        _, data = self.plan(code=1)
        self.assertEqual(data["changed"], ["top.txt"])
        entry = [e for e in data["restores"] if e["target"] == "top.txt"][0]
        self.assertEqual(entry["status"], "changed")
        self.assertEqual(entry["candidates"], ["rescue/copy.txt"])
        self.assertTrue(entry["recoverable"])
        self.assertFalse(entry["ambiguous"])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(target.read_bytes(), b"corrupt\n")

    def test_duplicate_extra_bytes_are_ambiguous(self):
        (self.root / "needed.txt").write_bytes(b"same bytes\n")
        (self.root / "other.txt").write_bytes(b"other\n")
        self.run_cli("create", code=0)
        (self.root / "needed.txt").unlink()
        (self.root / "x").mkdir()
        (self.root / "x" / "one.txt").write_bytes(b"same bytes\n")
        (self.root / "y").mkdir()
        (self.root / "y" / "two.txt").write_bytes(b"same bytes\n")
        before = self.snapshot()
        _, data = self.plan(code=1)
        entry = [e for e in data["restores"] if e["target"] == "needed.txt"][0]
        self.assertEqual(entry["candidates"], ["x/one.txt", "y/two.txt"])
        self.assertTrue(entry["recoverable"])
        self.assertTrue(entry["ambiguous"])
        self.assertEqual(data["ambiguous"], ["needed.txt"])
        self.assertEqual(data["unrecoverable"], [])
        self.assertEqual(self.snapshot(), before)

    def test_matched_duplicate_source_is_candidate(self):
        (self.root / "keep.txt").write_bytes(b"dup\n")
        (self.root / "gone.txt").write_bytes(b"dup\n")
        self.run_cli("create", code=0)
        (self.root / "gone.txt").unlink()
        _, data = self.plan(code=1)
        entry = [e for e in data["restores"] if e["target"] == "gone.txt"][0]
        self.assertEqual(entry["candidates"], ["keep.txt"])
        self.assertTrue(entry["recoverable"])
        self.assertFalse(entry["ambiguous"])

    def test_shared_candidate_can_serve_two_targets(self):
        (self.root / "one.txt").write_bytes(b"shared\n")
        (self.root / "two.txt").write_bytes(b"shared\n")
        self.run_cli("create", code=0)
        (self.root / "one.txt").unlink()
        (self.root / "two.txt").unlink()
        (self.root / "spare.txt").write_bytes(b"shared\n")
        _, data = self.plan(code=1)
        self.assertEqual(sorted(data["missing"]), ["one.txt", "two.txt"])
        self.assertEqual(len(data["restores"]), 2)
        for entry in data["restores"]:
            self.assertEqual(entry["candidates"], ["spare.txt"])
            self.assertTrue(entry["recoverable"])
            self.assertFalse(entry["ambiguous"])
        self.assertEqual(data["ambiguous"], [])
        self.assertEqual(data["unrecoverable"], [])

    def test_extra_only_has_no_restores_but_mismatch(self):
        self.fixture_nested()
        (self.root / "new.txt").write_bytes(b"extra\n")
        _, data = self.plan(code=1)
        self.assertEqual(data["ok"], False)
        self.assertEqual(data["missing"], [])
        self.assertEqual(data["changed"], [])
        self.assertEqual(data["extra"], ["new.txt"])
        self.assertEqual(data["restores"], [])

    def test_output_is_deterministic(self):
        self.fixture_nested()
        (self.root / "a" / "b" / "keep.txt").unlink()
        (self.root / "z").mkdir()
        (self.root / "z" / "a.txt").write_bytes(b"nested bytes\n")
        (self.root / "z" / "b.txt").write_bytes(b"nested bytes\n")
        first = self.run_cli("plan", code=1)
        second = self.run_cli("plan", code=1)
        self.assertEqual(first.stdout, second.stdout)
        data = json.loads(first.stdout)
        candidates = [e for e in data["restores"] if e["target"] == "a/b/keep.txt"][0]["candidates"]
        self.assertEqual(candidates, sorted(candidates))

    def test_plan_rejects_unsafe_root_and_manifest(self):
        self.fixture_nested()
        alias = self.home / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        result = self.run_cli("plan", root=alias)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        fifo = self.home / "manifest.fifo"
        os.mkfifo(fifo)
        result = self.run_cli("plan", manifest=fifo)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        colons = self.root / "a:b"
        colons.touch()
        result = self.run_cli("plan")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        colons.unlink()
        link = self.root / "link"
        link.symlink_to(self.manifest)
        result = self.run_cli("plan")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_plan_rejects_dotdot_components(self):
        self.fixture_nested()
        alias = self.home / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        result = self.run_cli("plan", root=alias / ".." / "archive")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_plan_rejects_malformed_manifest(self):
        self.fixture_nested()
        self.manifest.write_text("{")
        result = self.run_cli("plan")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_plan_closed_stdout_without_mutation(self):
        self.fixture_nested()
        (self.root / "top.txt").write_bytes(b"changed\n")
        before = self.snapshot()
        manifest_bytes = self.manifest.read_bytes()
        for unbuffered in (False, True):
            with self.subTest(unbuffered=unbuffered):
                argv = [sys.executable]
                if unbuffered:
                    argv.append("-u")
                argv += [str(CLI), "plan", str(self.root), str(self.manifest)]
                reader, writer = os.pipe()
                os.close(reader)
                try:
                    result = subprocess.run(argv, stdout=writer, stderr=subprocess.PIPE,
                                            text=True, timeout=10)
                finally:
                    os.close(writer)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.manifest.read_bytes(), manifest_bytes)


if __name__ == "__main__":
    unittest.main()
