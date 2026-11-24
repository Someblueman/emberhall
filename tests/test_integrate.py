"""Independent review and conflicting real source contributions preserve work."""
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
from house.home_work import contribution, git, room
from house.integrate import integrate
from house.home import pending_contributions
from tests.support import HouseCase


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host-only sandbox boundary fixture cannot nest macOS sandboxes")
class IntegrationTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        (self.repo / "tests").mkdir()
        (self.repo / "tests/test_document.py").write_text(
            "import pathlib,unittest\nclass Document(unittest.TestCase):\n"
            " def test_document(self): self.assertIn(pathlib.Path('document.txt').read_text(), ['base\\n','first\\n','second\\n'])\n")
        (self.repo / "document.txt").write_text("base\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Base source")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"
        self.private.mkdir()

    def candidate(self, run, text):
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": run,
            "resident": "author-" + run, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "author-" + run, {"name": "Author"})
        workspace = room(self.record, self.private, run, self.base)
        (workspace / "document.txt").write_text(text)
        (self.private / run).mkdir()
        contribution(workspace, self.base, self.private / run / "contribution.json", journal_artifacts={})
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": run,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        return workspace

    def test_wren_self_review_rejected_and_two_conflicting_contributions_retained(self):
        first = self.candidate("one", "first\n")
        second = self.candidate("two", "second\n")
        self.record.append("wake", "author-one", {})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, "one", "author-one", publish=True)
        result = integrate(self.record, "one", "alice", publish=True)
        self.assertEqual(result["status"], "integrated")
        self.assertEqual((self.repo / "document.txt").read_text(), "first\n")
        result = integrate(self.record, "two", "bob", publish=True)
        self.assertEqual(result["status"], "conflict")
        self.assertEqual((self.repo / "document.txt").read_text(), "first\n")
        self.assertEqual((second / "document.txt").read_text(), "second\n")
        self.assertEqual((first / "document.txt").read_text(), "first\n")
        shutil.rmtree(second)
        journal = self.record.read()[2]
        self.assertEqual(integrate(self.record, "two", "bob", publish=True), result)
        self.assertEqual(self.record.read()[2], journal)

    def test_accepted_retry_keeps_receipt_history_and_does_no_new_work(self):
        workspace = self.candidate("one", "first\n")
        accepted = integrate(self.record, "one", "alice", publish=True)
        shutil.rmtree(workspace)
        path = self.private / "one/integration.json"
        original = path.read_bytes()
        head = git(self.repo, "rev-parse", "HEAD")
        journal = self.record.read()[2]
        candidates = sorted(self.private.glob("integration-*"))
        for publish in (False, True):
            self.assertEqual(integrate(self.record, "one", "bob", publish=publish), accepted)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)
            self.assertEqual(self.record.read()[2], journal)
            self.assertEqual(sorted(self.private.glob("integration-*")), candidates)
            self.assertEqual(pending_contributions(self.private), [])
        # A read-only receipt replay must not touch someone else's dirty work.
        (self.repo / "document.txt").write_text("uncommitted next task\n")
        self.assertEqual(integrate(self.record, "one", "bob"), accepted)
        self.assertEqual((self.repo / "document.txt").read_text(), "uncommitted next task\n")

    def test_failed_receipt_survives_missing_source_room(self):
        self.assert_missing_terminal_replay("failed", "invalid\n")

    def test_rejected_receipt_survives_missing_source_room(self):
        self.assert_missing_terminal_replay("rejected", "first\n")

    def assert_missing_terminal_replay(self, run, text):
        with self.subTest(run=run):
            workspace = self.candidate(run, text)
            result = integrate(self.record, run, "alice",
                               reject="Not suitable" if run == "rejected" else None)
            self.assertEqual(result["status"], "rejected" if run == "rejected" else "tests-failed")
            if run == "failed":
                self.assertIn("AssertionError", result["diagnostics"]["tail"])
            shutil.rmtree(workspace)
            path = self.private / run / "integration.json"
            original, journal = path.read_bytes(), self.record.read()[2]
            head = git(self.repo, "rev-parse", "HEAD")
            candidates = sorted(self.private.glob("integration-*"))
            with patch.dict(os.environ, {"EMBERHALL_ACTION_JOB": "1"}):
                self.assertEqual(integrate(self.record, run, "bob", publish=True), result)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(self.record.read()[2], journal)
            self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)
            self.assertEqual(sorted(self.private.glob("integration-*")), candidates)
            with self.assertRaisesRegex(ValueError, "different, awake"):
                integrate(self.record, run, "author-" + run)
            report_path = self.private / run / "contribution.json"
            report = json.loads(report_path.read_text())
            report_path.write_text(json.dumps(dict(report, commit="0" * 40)))
            with self.assertRaisesRegex(ValueError, "receipt is inconsistent"):
                integrate(self.record, run, "bob")
            self.assertEqual(path.read_bytes(), original)

    def test_new_and_prepared_reviews_still_require_the_source_room(self):
        for status in (None, "prepared"):
            with self.subTest(status=status):
                run = status or "new"
                workspace = self.candidate(run, "first\n")
                path = self.private / run / "integration.json"
                if status:
                    path.write_text(json.dumps({"run": run, "status": status}))
                shutil.rmtree(workspace)
                journal = self.record.read()[2]
                with self.assertRaises(subprocess.CalledProcessError):
                    integrate(self.record, run, "alice", publish=True)
                self.assertEqual(self.record.read()[2], journal)
                self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.base)

    def test_terminal_receipt_does_not_excuse_a_changed_existing_room(self):
        workspace = self.candidate("one", "first\n")
        result = integrate(self.record, "one", "alice", reject="Not suitable")
        git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "--allow-empty", "-m", "Changed candidate")
        path = self.private / "one/integration.json"
        original, journal = path.read_bytes(), self.record.read()[2]
        with self.assertRaisesRegex(ValueError, "identity changed"):
            integrate(self.record, "one", "bob")
        self.assertEqual(json.loads(path.read_text()), result)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(self.record.read()[2], journal)

    def test_incomplete_receipt_is_preserved_and_actual_integration_recovers(self):
        self.candidate("one", "first\n")
        path = self.private / "one/integration.json"
        path.write_bytes(b'{"status": "integrated",')
        self.assertEqual(len(pending_contributions(self.private)), 1)
        result = integrate(self.record, "one", "alice", publish=True)
        self.assertEqual(result["status"], "integrated")
        self.assertEqual((self.repo / "document.txt").read_text(), "first\n")
        retained = list(path.parent.glob("integration-incomplete-*.json"))
        self.assertEqual(len(retained), 1)
        self.assertEqual(retained[0].read_bytes(), b'{"status": "integrated",')
        self.assertEqual(json.loads(path.read_text()), result)
        self.assertFalse(path.with_suffix(".tmp").exists())
        self.assertEqual(pending_contributions(self.private), [])

    def test_operator_acceptance_survives_later_commits_without_self_review(self):
        workspace = self.candidate("one", "first\n")
        (self.repo / "document.txt").write_text("first\n")
        git(self.repo, "add", "document.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Curated acceptance")
        accepted = {"run": "one", "actor": "alice", "status": "integrated",
                    "contribution": git(workspace, "rev-parse", "HEAD"),
                    "canonical_commit": git(self.repo, "rev-parse", "HEAD")}
        path = self.private / "one/integration.json"
        # Existing operator-curated receipts bind canonical_commit, not candidate_head.
        path.write_text(json.dumps(accepted))
        shutil.rmtree(workspace)
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "--allow-empty", "-m", "Later work")
        self.assertEqual(integrate(self.record, "one", "bob"), accepted)
        self.record.append("wake", "author-one", {})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, "one", "author-one")
        self.record.append("sleep", "bob", {"through": 0, "note": "Rest"})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, "one", "bob")

    def test_inconsistent_acceptance_and_changed_contribution_fail_closed(self):
        workspace = self.candidate("one", "first\n")
        accepted = integrate(self.record, "one", "alice", publish=True)
        path = self.private / "one/integration.json"
        for field, value in (("run", "other"), ("contribution", "0" * 40),
                             ("candidate_head", "0" * 40), ("candidate_head", "--all"),
                             ("canonical_commit", 7), ("canonical_commit", self.base),
                             ("candidate_head", self.base)):
            with self.subTest(field=field, value=value):
                broken = dict(accepted, **{field: value})
                path.write_text(json.dumps(broken))
                before = path.read_bytes()
                with self.assertRaisesRegex(ValueError, "accepted contribution"):
                    integrate(self.record, "one", "bob")
                self.assertEqual(path.read_bytes(), before)
        other = self.candidate("other", "second\n")
        other_head = git(other, "rev-parse", "HEAD")
        git(self.repo, "fetch", str(other), other_head)
        path.write_text(json.dumps(dict(accepted, candidate_head=other_head)))
        with self.assertRaisesRegex(ValueError, "outside current source history"):
            integrate(self.record, "one", "bob")
        path.write_text(json.dumps(accepted))
        git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "--allow-empty", "-m", "Changed candidate")
        with self.assertRaisesRegex(ValueError, "identity changed"):
            integrate(self.record, "one", "bob")
        self.assertEqual(json.loads(path.read_text()), accepted)

    def test_concurrent_replays_preserve_accepted_receipt(self):
        self.candidate("one", "first\n")
        accepted = integrate(self.record, "one", "alice", publish=True)
        path = self.private / "one/integration.json"
        original, journal = path.read_bytes(), self.record.read()[2]
        script = """
import json,sys
from house.record import Record
from house.integrate import integrate
try:
 print(json.dumps(integrate(Record(sys.argv[1]), 'one', 'bob', publish=True)))
except BlockingIOError:
 sys.exit(2)
"""
        processes = [self.script(script), self.script(script)]
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertIn(process.returncode, (0, 2), err)
            if process.returncode == 0:
                self.assertEqual(json.loads(out), accepted)
        self.assertTrue(any(p.returncode == 0 for p in processes))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(self.record.read()[2], journal)


class InspectionPagingTests(unittest.TestCase):
    def setUp(self):
        self.f = IntegrationTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def commit_files(self, room, files, message="Large contribution"):
        for rel, content in files.items():
            target = room / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")
        git(room, "add", "--all")
        git(room, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", message)
        report = self.f.private / "one/contribution.json"
        data = json.loads(report.read_text())
        data["commit"] = git(room, "rev-parse", "HEAD")
        report.write_text(json.dumps(data))

    def test_reconstructs_large_utf8_diff_and_content_across_nonoverlapping_pages(self):
        from house.integrate import INSPECTION_LIMIT, inspect_contribution

        f = self.f
        room = f.candidate("one", "first\n")
        # Place 4-byte UTF-8 emojis across INSPECTION_LIMIT and 2 * INSPECTION_LIMIT boundaries.
        chunk = ("a" * (INSPECTION_LIMIT - 2)) + "😀" + ("b" * (INSPECTION_LIMIT - 2)) + "—"
        large_text = chunk + "tail-section\nFINAL LINE\n"
        extra_text = "x" * 2000 + "\nEXTRA FINAL\n"
        self.commit_files(room, {"large.txt": large_text, "extra.txt": extra_text})

        expected_full_diff = subprocess.run(
            ["git", "--literal-pathspecs", "diff", "--no-ext-diff", "--no-textconv",
             "--no-renames", "--no-color", f.base, git(room, "rev-parse", "HEAD"), "--"],
            cwd=room, capture_output=True, check=True, text=True).stdout
        expected_file_diff = subprocess.run(
            ["git", "--literal-pathspecs", "diff", "--no-ext-diff", "--no-textconv",
             "--no-renames", "--no-color", f.base, git(room, "rev-parse", "HEAD"), "--", "large.txt"],
            cwd=room, capture_output=True, check=True, text=True).stdout

        # Reconstruct cumulative diff across nonoverlapping pages.
        diff_pages = []
        cursor = None
        while True:
            page = inspect_contribution(f.record, "one", "alice", diff_after=cursor)
            self.assertEqual(page["limit_bytes"], INSPECTION_LIMIT)
            self.assertEqual(page["diff_after"], 0 if cursor is None else cursor)
            self.assertLessEqual(len(page["diff"].encode("utf-8")), INSPECTION_LIMIT)
            self.assertNotIn("\ufffd", page["diff"])
            self.assertEqual(page["truncated"], page["diff_has_more"])
            diff_pages.append(page)
            if not page["diff_has_more"]:
                break
            self.assertGreater(page["diff_through"], page["diff_after"])
            cursor = page["diff_through"]
        self.assertGreater(len(diff_pages), 2)
        reconstructed_diff = "".join(p["diff"] for p in diff_pages)
        self.assertEqual(reconstructed_diff, expected_full_diff)
        self.assertIn("EXTRA FINAL\n", reconstructed_diff)
        self.assertIn("FINAL LINE\n", diff_pages[-1]["diff"])

        # Reconstruct per-file diff across nonoverlapping pages.
        file_diff_parts = []
        cursor = 0
        while True:
            page = inspect_contribution(f.record, "one", "alice", "large.txt", diff_after=cursor)
            self.assertEqual(page["diff_after"], cursor)
            file_diff_parts.append(page["diff"])
            if not page["diff_has_more"]:
                end_diff = page["diff_through"]
                break
            cursor = page["diff_through"]
        self.assertEqual("".join(file_diff_parts), expected_file_diff)
        self.assertIn("FINAL LINE\n", file_diff_parts[-1])

        # Exact EOF cursor returns empty slice and has_more=False.
        eof_diff = inspect_contribution(f.record, "one", "alice", "large.txt", diff_after=end_diff)
        self.assertEqual(eof_diff["diff"], "")
        self.assertEqual(eof_diff["diff_after"], end_diff)
        self.assertEqual(eof_diff["diff_through"], end_diff)
        self.assertFalse(eof_diff["diff_has_more"])
        self.assertFalse(eof_diff["truncated"])

        # Without content_after, large text remains content_status='too-large' with no content.
        unpaged = inspect_contribution(f.record, "one", "alice", "large.txt")
        self.assertEqual(unpaged["content_status"], "too-large")
        self.assertNotIn("content", unpaged)
        self.assertEqual(unpaged["content_bytes"], len(large_text.encode("utf-8")))
        self.assertTrue(unpaged["content_has_more"])

        # Reconstruct regular text content across nonoverlapping pages.
        content_pages = []
        cursor = 0
        while True:
            page = inspect_contribution(f.record, "one", "alice", "large.txt", content_after=cursor)
            self.assertEqual(page["content_status"], "partial")
            self.assertEqual(page["content_after"], cursor)
            self.assertLessEqual(len(page["content"].encode("utf-8")), INSPECTION_LIMIT)
            self.assertNotIn("\ufffd", page["content"])
            content_pages.append(page)
            if not page["content_has_more"]:
                end_content = page["content_through"]
                break
            self.assertGreater(page["content_through"], page["content_after"])
            cursor = page["content_through"]
        self.assertGreater(len(content_pages), 2)
        self.assertEqual("".join(p["content"] for p in content_pages), large_text)
        self.assertTrue(content_pages[-1]["content"].endswith("FINAL LINE\n"))

        eof_content = inspect_contribution(f.record, "one", "alice", "large.txt", content_after=end_content)
        self.assertEqual(eof_content["content"], "")
        self.assertEqual(eof_content["content_through"], end_content)
        self.assertFalse(eof_content["content_has_more"])
        self.assertFalse((f.private / "one/integration.json").exists())

    def test_paging_rejects_malformed_cursors_paths_and_authorization(self):
        from house.integrate import INSPECTION_LIMIT, inspect_contribution

        f = self.f
        room = f.candidate("one", "first\n")
        large_text = ("a" * (INSPECTION_LIMIT - 2)) + "😀tail\n"
        self.commit_files(room, {"large.txt": large_text})

        # Malformed cursor types and negative values.
        for bad in (-1, True, False, "0", 1.5):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    inspect_contribution(f.record, "one", "alice", diff_after=bad)
                with self.assertRaises(ValueError):
                    inspect_contribution(f.record, "one", "alice", "large.txt", content_after=bad)

        # content_after without path.
        with self.assertRaisesRegex(ValueError, "path"):
            inspect_contribution(f.record, "one", "alice", content_after=0)

        # Out-of-range cursors.
        content_len = len(large_text.encode("utf-8"))
        with self.assertRaises(ValueError):
            inspect_contribution(f.record, "one", "alice", "large.txt", content_after=content_len + 1)
        with self.assertRaises(ValueError):
            inspect_contribution(f.record, "one", "alice", "large.txt", diff_after=content_len + 10_000)

        # Mid-UTF-8 character cursors.
        emoji_offset = INSPECTION_LIMIT - 2
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            inspect_contribution(f.record, "one", "alice", "large.txt", content_after=emoji_offset + 1)
        page1 = inspect_contribution(f.record, "one", "alice", "large.txt", diff_after=0)
        self.assertTrue(page1["diff_has_more"])
        # The diff line has '+' before 'a's, so emoji starts at emoji_offset + header bytes; find its continuation byte.
        full_diff = subprocess.run(
            ["git", "--literal-pathspecs", "diff", "--no-ext-diff", "--no-textconv",
             "--no-renames", "--no-color", f.base, git(room, "rev-parse", "HEAD"), "--", "large.txt"],
            cwd=room, capture_output=True, check=True).stdout
        mid_diff = full_diff.index("😀".encode("utf-8")) + 1
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            inspect_contribution(f.record, "one", "alice", "large.txt", diff_after=mid_diff)

        # Exact changed-path validation preserved.
        for bad_path in ("../large.txt", "/etc/passwd", ":(glob)*", "tests/test_document.py"):
            with self.assertRaisesRegex(ValueError, "exact changed"):
                inspect_contribution(f.record, "one", "alice", bad_path, diff_after=0)
            with self.assertRaisesRegex(ValueError, "exact changed"):
                inspect_contribution(f.record, "one", "alice", bad_path, content_after=0)

        # Authorization & immutable contribution identity preserved across pages.
        with self.assertRaisesRegex(ValueError, "different, awake"):
            inspect_contribution(f.record, "one", "author-one", "large.txt", content_after=0)
        self.f.record.append("sleep", "bob", {"through": 0, "note": "Rest"})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            inspect_contribution(f.record, "one", "bob", "large.txt", content_after=0)
        git(room, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "--allow-empty", "-m", "Mutate candidate")
        with self.assertRaisesRegex(ValueError, "identity changed"):
            inspect_contribution(f.record, "one", "alice", "large.txt", content_after=page1["diff_through"])

    def test_paging_preserves_binary_nonregular_and_deleted_protections(self):
        from house.integrate import INSPECTION_LIMIT, inspect_contribution

        f = self.f
        room = f.candidate("one", "first\n")
        (room / "late_binary.bin").write_bytes((b"x" * (INSPECTION_LIMIT + 10)) + b"\x00tail")
        (room / "link").symlink_to("/etc/passwd")
        (room / "document.txt").unlink()
        self.commit_files(room, {})

        # Binary tail past INSPECTION_LIMIT must still classify file as binary even on page 0.
        for cursor in (0, INSPECTION_LIMIT):
            res = inspect_contribution(f.record, "one", "alice", "late_binary.bin", content_after=cursor)
            self.assertEqual(res["content_status"], "binary")
            self.assertNotIn("content", res)
        for path, status in (("link", "not-regular-file"), ("document.txt", "deleted")):
            res = inspect_contribution(f.record, "one", "alice", path, content_after=0)
            self.assertEqual(res["content_status"], status)
            self.assertNotIn("content", res)
            with self.assertRaises(ValueError):
                inspect_contribution(f.record, "one", "alice", path, content_after=1)

    def test_cli_and_resident_actions_paging_routing(self):
        from house import integrate as integrate_mod
        from house.resident_actions import parse

        f = self.f
        room = f.candidate("one", "first\n")
        large_text = ("line\n" * 16_000) + "CLI FINAL LINE\n"
        self.commit_files(room, {"large.txt": large_text})

        args = parse(["integrate", "one", "--inspect", "--path", "large.txt",
                      "--diff-after", "0", "--content-after", "10", "--as", "alice"], "alice")
        self.assertEqual((args.diff_after, args.content_after), (0, 10))
        with self.assertRaises(SystemExit):
            parse(["integrate", "one", "--inspect", "--diff-after", "abc", "--as", "alice"], "alice")

        # CLI main() reconstructs full content and rejects invalid combinations.
        parts = []
        cursor = 0
        while True:
            proc = subprocess.run(
                [sys.executable, "-m", "house.integrate", "--repo", str(f.repo), "one",
                 "--as", "alice", "--inspect", "--path", "large.txt", "--content-after", str(cursor)],
                capture_output=True, text=True, check=True)
            page = json.loads(proc.stdout)
            parts.append(page["content"])
            if not page["content_has_more"]:
                break
            cursor = page["content_through"]
        self.assertEqual("".join(parts), large_text)

        for bad_args in (
            ["--inspect", "--content-after", "0"],
            ["--diff-after", "0"],
            ["--path", "large.txt", "--content-after", "0"],
            ["--inspect", "--path", "large.txt", "--content-after", "-1"],
        ):
            proc = subprocess.run(
                [sys.executable, "-m", "house.integrate", "--repo", str(f.repo), "one",
                 "--as", "alice", *bad_args],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, (bad_args, proc.stdout, proc.stderr))

