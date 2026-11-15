"""Real-Git acceptance tests for Skein's first portable-packet milestone."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import skein


class SkeinFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="skein-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        self.environment = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
            self.environment.pop(key, None)
        self.environment.update({
            "HOME": str(self.root), "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "Skein Fixture",
            "GIT_AUTHOR_EMAIL": "skein-fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Skein Fixture",
            "GIT_COMMITTER_EMAIL": "skein-fixture@example.invalid",
            "GIT_AUTHOR_DATE": "1700000000 +0000",
            "GIT_COMMITTER_DATE": "1700000000 +0000",
        })
        original_environment = os.environ.copy()

        def restore_environment() -> None:
            os.environ.clear()
            os.environ.update(original_environment)

        self.addCleanup(restore_environment)
        # Skein invokes Git itself; isolate those child processes as well as the
        # fixture commands from a developer's/global Git configuration.
        os.environ.clear()
        os.environ.update(self.environment)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Skein Fixture")
        self.git("config", "user.email", "skein-fixture@example.invalid")
        self.write("alpha.txt", "first\n<danger> & value\n\tTabbed\nduplicate\nduplicate\nlast")
        self.write("old-name.txt", "same\ncontent\n")
        self.commit("base")
        self.git("branch", "base")
        self.git("checkout", "--quiet", "-b", "feature")
        self.base = self.rev_parse("base")
        self.write(
            "alpha.txt",
            "<script>alert(\"x\")</script> & value\n<danger> & value\n"
            "\tTabbed\nduplicate\nduplicate\nlast\nhead tail\n",
        )
        self.git("mv", "old-name.txt", "renamed.txt")
        self.write("café-☃.txt", "Unicode ☃\n<second> line\n")
        self.commit("head with rename, Unicode, tabs and duplicate lines")
        self.head = self.rev_parse("feature")
        self.packet = self.root / "packet"

    def git(self, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
        result = subprocess.run(
            ["git", "--no-pager", "-C", str(cwd or self.repository), *arguments],
            env=self.environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=60,
        )
        if result.returncode:
            self.fail(
                f"fixture Git failed: {arguments!r}\n"
                f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
            )
        return result

    def write(self, relative: str, content: str | bytes) -> None:
        path = self.repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")

    def commit(self, message: str) -> None:
        self.git("add", "-A", "--", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "--quiet", "-m", message)

    def rev_parse(self, ref: str) -> str:
        return self.git("rev-parse", ref).stdout.decode("ascii").strip()

    def export(self, output: Path | None = None, **kwargs) -> dict:
        return skein.export_packet(
            self.repository, "base", "feature", output or self.packet, **kwargs
        )

    def restore_head(self) -> None:
        self.git("reset", "--hard", "--quiet", self.head)
        # Only fixture-created untracked files are removed by the individual cases.


class SkeinPacketTests(SkeinFixture):
    def test_export_html_anchors_bundle_and_comment_roundtrip(self) -> None:
        metadata = self.export()
        self.assertEqual(self.base, metadata["base"]["commit"])
        self.assertEqual(self.head, metadata["head"]["commit"])
        self.assertEqual(self.base, json.loads((self.packet / "packet.json").read_text())["base"]["commit"])
        files = metadata["files"]
        self.assertIn({"status": "renamed", "old_path": "old-name.txt",
                       "new_path": "renamed.txt", "old_lines": 2, "new_lines": 2}, files)
        self.assertIn("café-☃.txt", [item["new_path"] for item in files])

        page = (self.packet / "review.html").read_text(encoding="utf-8")
        self.assertIn("&lt;danger&gt; &amp; value", page)
        self.assertNotIn("<danger>", page)
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;alert", page)
        self.assertIn("\tTabbed", page)
        self.assertIn("café-☃.txt", page)
        self.assertIn("default-src 'none'", page)
        self.assertNotIn("<script src", page)
        self.assertIn("\\ No newline at end of file", page)

        anchor_document = json.loads((self.packet / "anchors.json").read_text(encoding="utf-8"))
        anchors = [skein.Anchor.from_dict(item) for item in anchor_document["anchors"]]
        duplicates = [item for item in anchors if item.commit == self.head
                      and item.path == "alpha.txt" and item.text == "duplicate"]
        self.assertEqual(2, len(duplicates))
        self.assertEqual({4, 5}, {item.line for item in duplicates})
        target = next(item for item in anchors if item.commit == self.head
                      and item.path == "alpha.txt" and item.text == "\tTabbed")

        # This is an actual ordinary full Git bundle: its own Git verifier and a
        # fresh clone both run; neither check trusts Skein's metadata alone.
        self.git("bundle", "verify", str(self.packet / "changes.bundle"))
        heads = self.git("bundle", "list-heads", str(self.packet / "changes.bundle")).stdout
        self.assertIn(b"refs/heads/skein-base", heads)
        self.assertIn(b"refs/heads/skein-head", heads)
        self.assertEqual((self.base, self.head), skein.verify_packet(self.packet))
        clone = self.root / "clone"
        self.git("clone", "--quiet", "--no-checkout", str(self.packet / "changes.bundle"),
                 str(clone), cwd=self.root)
        for commit in (self.base, self.head):
            self.git("cat-file", "-e", f"{commit}^{{commit}}", cwd=clone)

        comment = skein.add_comment(
            self.packet, "review-1", target.commit, target.path,
            target.side, target.line, "Please explain the tab alignment.",
        )
        stored = skein.loads_comments((self.packet / "comments.json").read_text(encoding="utf-8"))
        self.assertEqual([comment], stored)
        self.assertEqual([comment], skein.loads_comments(skein.dumps_comments(stored)))
        self.assertEqual("anchored", comment.state)

    def test_reexports_are_byte_identical(self) -> None:
        first = self.root / "first"
        second = self.root / "second"
        self.export(first)
        self.export(second)
        expected = {"packet.json", "anchors.json", "comments.json", "review.html", "changes.bundle"}
        self.assertEqual(expected, {path.name for path in first.iterdir()})
        self.assertEqual(expected, {path.name for path in second.iterdir()})
        for name in expected:
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)

    def test_newline_only_change_is_not_lost_from_static_diff(self) -> None:
        alpha = self.repository / "alpha.txt"
        alpha.write_text(alpha.read_text(encoding="utf-8").removesuffix("\n"), encoding="utf-8")
        self.commit("remove only the final newline")
        self.git("branch", "newline-only")
        metadata = skein.export_packet(self.repository, self.head, "newline-only", self.packet)
        self.assertEqual(1, len(metadata["files"]))
        self.assertEqual("modified", metadata["files"][0]["status"])
        self.assertEqual(7, metadata["files"][0]["old_lines"])
        self.assertEqual(7, metadata["files"][0]["new_lines"])
        page = (self.packet / "review.html").read_text(encoding="utf-8")
        self.assertIn("\\ No newline at end of file", page)
        self.assertIn('class="meta"', page)

    def test_full_commit_ids_are_accepted_without_moving_repository_refs(self) -> None:
        before = self.git("for-each-ref", "--format=%(refname) %(objectname)").stdout
        metadata = skein.export_packet(
            self.repository, self.base, self.head, self.packet,
        )
        self.assertEqual(self.base, metadata["base"]["commit"])
        self.assertEqual(self.head, metadata["head"]["commit"])
        self.assertEqual((self.base, self.head), skein.verify_packet(self.packet))
        after = self.git("for-each-ref", "--format=%(refname) %(objectname)").stdout
        self.assertEqual(before, after)

    def test_cli_exports_verifies_and_records_an_offline_comment(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(0, skein.main([
                "export", str(self.repository), "base", "feature", str(self.packet),
            ]))
            self.assertEqual(0, skein.main(["verify", str(self.packet)]))
            self.assertEqual(0, skein.main([
                "comment", str(self.packet), "--id", "cli-note", "--commit", self.head,
                "--path", "alpha.txt", "--side", "new", "--line", "1",
                "--body", "Escape this line and keep it escaped.",
            ]))
        self.assertIn("Verified full offline bundle", stdout.getvalue())
        comments = skein.loads_comments((self.packet / "comments.json").read_text(encoding="utf-8"))
        self.assertEqual(["cli-note"], [item.identifier for item in comments])
        self.assertEqual(1, comments[0].anchor.line)

    def test_rejects_dirty_staged_and_untracked_worktrees(self) -> None:
        cases = ("tracked", "staged", "untracked")
        for case in cases:
            with self.subTest(case=case):
                if case == "tracked":
                    self.write("alpha.txt", "uncommitted\n")
                elif case == "staged":
                    self.write("alpha.txt", "staged\n")
                    self.git("add", "alpha.txt")
                else:
                    self.write("untracked.txt", "not committed\n")
                with self.assertRaisesRegex(skein.SkeinError, "not clean"):
                    self.export(self.root / f"dirty-{case}")
                self.assertFalse((self.root / f"dirty-{case}").exists())
                self.restore_head()
                if case == "untracked":
                    (self.repository / "untracked.txt").unlink()

    def test_rejects_ambiguous_refs_instead_of_choosing_a_branch_or_tag(self) -> None:
        self.git("branch", "dual", self.head)
        self.git("tag", "dual", self.base)
        with self.assertRaisesRegex(skein.SkeinError, "ambiguous Git ref"):
            skein.export_packet(self.repository, "dual", "feature", self.packet)
        self.assertFalse(self.packet.exists())

    def test_rejects_unsafe_paths_and_output_overwrite(self) -> None:
        self.write("bad:name.txt", "not portable\n")
        self.commit("unsafe path")
        with self.assertRaisesRegex(skein.SkeinError, "unsafe or nonportable"):
            self.export()
        self.assertFalse(self.packet.exists())
        self.restore_head()
        with self.assertRaisesRegex(skein.SkeinError, "outside the source worktree"):
            self.export(self.repository / "inside.packet")
        outside = self.root / "occupied"
        outside.mkdir()
        with self.assertRaisesRegex(skein.SkeinError, "refusing to overwrite"):
            self.export(outside)

    @unittest.skipUnless(os.name == "posix", "Git symlink modes require POSIX fixture semantics")
    def test_rejects_symlink_blob(self) -> None:
        os.symlink("alpha.txt", self.repository / "link.txt")
        self.commit("symlink")
        with self.assertRaisesRegex(skein.SkeinError, "only regular file blobs"):
            self.export()
        self.assertFalse(self.packet.exists())

    def test_rejects_binary_non_utf8_and_oversized_changed_files(self) -> None:
        cases = (
            ("binary.bin", b"before\x00after", "binary file", skein.DEFAULT_MAX_FILE_BYTES),
            ("invalid.txt", b"\xff\xfe", "not UTF-8", skein.DEFAULT_MAX_FILE_BYTES),
            ("large.txt", b"x" * 201, "above the 200-byte limit", 200),
        )
        for name, content, message, maximum in cases:
            with self.subTest(name=name):
                self.write(name, content)
                self.commit(f"reject {name}")
                with self.assertRaisesRegex(skein.SkeinError, message):
                    self.export(max_file_bytes=maximum)
                self.assertFalse(self.packet.exists())
                self.restore_head()

    def test_comment_rejects_missing_anchor_duplicate_id_and_bad_json(self) -> None:
        self.export()
        target = next(item for item in skein._load_anchors(self.packet)
                      if item.commit == self.head and item.path == "alpha.txt"
                      and item.side == "new" and item.text == "duplicate")
        comment = skein.add_comment(
            self.packet, "once", target.commit, target.path, target.side,
            target.line, "First observation.",
        )
        self.assertEqual(target, comment.anchor)
        with self.assertRaisesRegex(skein.SkeinError, "already exists"):
            skein.add_comment(self.packet, "once", target.commit, target.path,
                              target.side, target.line, "A duplicate ID.")
        with self.assertRaisesRegex(skein.SkeinError, "exactly one rendered line"):
            skein.add_comment(self.packet, "missing", target.commit, target.path,
                              target.side, 999, "No such line.")
        with self.assertRaisesRegex(skein.SkeinError, "neither the packet base nor its head"):
            skein.add_comment(self.packet, "wrong", "f" * 40, target.path,
                              target.side, target.line, "Wrong revision.")
        with self.assertRaisesRegex(skein.SkeinError, "duplicate JSON key"):
            skein.loads_comments(
                '{"format":"review-skein-comments","format":"review-skein-comments",'
                '"version":1,"comments":[]}'
            )
        with self.assertRaisesRegex(skein.SkeinError, "unsupported comments header"):
            skein.loads_comments("{}")

    def test_rebase_is_unique_or_visibly_orphaned(self) -> None:
        original = skein.Anchor(self.head, "alpha.txt", "new", 4, "duplicate")
        comment = skein.Comment("rebind", original, "Why are these lines duplicated?")
        rebased = "f" * 40
        exact = skein.reanchor(comment, rebased, [
            skein.Anchor(rebased, "alpha.txt", "new", 4, "duplicate"),
            skein.Anchor(rebased, "alpha.txt", "new", 5, "duplicate"),
        ])
        self.assertEqual("anchored", exact.state)
        self.assertEqual(4, exact.anchor.line)
        self.assertEqual(original, exact.rebased_from)

        unique = skein.reanchor(comment, rebased, [
            skein.Anchor(rebased, "alpha.txt", "new", 9, "duplicate"),
        ])
        self.assertEqual("anchored", unique.state)
        self.assertEqual(9, unique.anchor.line)
        self.assertIsNone(unique.orphan_reason)

        duplicate = skein.reanchor(comment, rebased, [
            skein.Anchor(rebased, "alpha.txt", "new", 8, "duplicate"),
            skein.Anchor(rebased, "alpha.txt", "new", 9, "duplicate"),
        ])
        self.assertEqual("orphan", duplicate.state)
        self.assertIn("ambiguous", duplicate.orphan_reason)
        self.assertEqual(rebased, duplicate.anchor.commit)
        self.assertEqual(original, duplicate.rebased_from)
        restored = skein.Comment.from_dict(duplicate.to_dict())
        self.assertEqual(duplicate, restored)

        missing = skein.reanchor(comment, rebased, [])
        self.assertEqual("orphan", missing.state)
        self.assertIn("path and side are missing", missing.orphan_reason)
        changed = skein.reanchor(comment, rebased, [
            skein.Anchor(rebased, "alpha.txt", "new", 4, "edited"),
        ])
        self.assertEqual("orphan", changed.state)
        self.assertIn("uniquely matching text are missing", changed.orphan_reason)


if __name__ == "__main__":
    unittest.main()
