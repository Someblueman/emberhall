"""Real-Git tests for Skein's read-only annotated diff-and-comment view."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import probe
import review_view
import skein
from test_skein import SkeinFixture


TOOLS = Path(__file__).resolve().parent


def _snapshot(directory: Path) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


class ReviewViewTests(SkeinFixture):
    def test_diff_controls_are_visible_without_changing_line_anchors(self) -> None:
        controls = "\u202e\u2066\x1b\r\x7f"
        self.git("checkout", "--quiet", self.base)
        self.write("controls.txt", f"start\nold {controls}\tend\nlast\n")
        self.commit("old controls")
        self.git("branch", "-f", "base")
        self.base = self.rev_parse("base")
        self.git("checkout", "--quiet", "-B", "feature")
        self.write("controls.txt", f"start\nnew {controls}\tend\nlast\n")
        self.commit("new controls")
        self.head = self.rev_parse("feature")
        self.export()
        for side, commit in (("old", self.base), ("new", self.head)):
            skein.add_comment(self.packet, f"{side}-note", commit, "controls.txt", side, 2,
                              f"{side} body {controls}\nsecond line")
        before = _snapshot(self.packet)
        # Even the author repository is unnecessary; only carried packet bytes are read.
        shutil.rmtree(self.repository)
        for output_format in ("text", "html"):
            with self.subTest(output_format=output_format):
                result = review_view.render_packet(self.packet, output_format=output_format, context=0)
                for control in controls:
                    self.assertNotIn(control, result)
                    self.assertIn(f"\\u{ord(control):04x}", result)
                self.assertIn("old-note", result)
                self.assertIn("new-note", result)
                self.assertIn("old line 2", result)
                self.assertIn("new line 2", result)
                self.assertIn("\tend", result)
                if output_format == "html":
                    self.assertEqual([], probe.audit(probe.parse(result)))
        self.assertEqual(before, _snapshot(self.packet))

    def test_literal_escape_and_raw_bidi_remain_a_changed_row(self) -> None:
        self.git("checkout", "--quiet", self.base)
        self.write("literal.txt", "before\nvalue \u202e\nafter\n")
        self.commit("raw bidi")
        self.git("branch", "-f", "base")
        self.base = self.rev_parse("base")
        self.git("checkout", "--quiet", "-B", "feature")
        self.write("literal.txt", "before\nvalue \\u202e\nafter\n")
        self.commit("literal escape")
        self.head = self.rev_parse("feature")
        self.export()
        skein.add_comment(self.packet, "changed-note", self.head, "literal.txt", "new", 2, "Changed")
        page = review_view.render_packet(self.packet, output_format="html", context=0)
        text = review_view.render_packet(self.packet, context=0)
        self.assertIn('<tr class="replace">', page)
        self.assertIn("new line 2", page)
        self.assertIn("-    2", text)
        self.assertIn("+          2", text)
        self.assertIn("changed-note", text)
        self.assertNotIn("\u202e", page + text)
        self.assertEqual([], probe.audit(probe.parse(page)))

    def test_anchor_inventory_must_match_verified_bundle_without_writes(self) -> None:
        self.export()
        path = self.packet / "anchors.json"
        original = json.loads(path.read_bytes())
        first = original["anchors"][0]
        variants = {
            "extra": original["anchors"] + [{**first, "line": 999}],
            "missing": original["anchors"][1:],
            "duplicate": original["anchors"] + [first],
        }
        for field, value in (("text", "wrong"), ("commit", "0" * 40),
                             ("path", "elsewhere.txt"), ("side", "new"), ("line", 999)):
            changed = copy.deepcopy(original["anchors"])
            changed[0][field] = value
            variants[field] = changed
        for name, anchors in variants.items():
            path.write_text(json.dumps({**original, "anchors": anchors}), encoding="utf8")
            before = _snapshot(self.packet)
            for output_format in ("text", "html"):
                with self.subTest(tamper=name, output_format=output_format):
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        code = review_view.main([str(self.packet), "--format", output_format])
                    self.assertEqual(1, code)
                    self.assertEqual("", stdout.getvalue())
                    self.assertIn("anchors.json", stderr.getvalue())
                    self.assertEqual(before, _snapshot(self.packet))
        # Coordinate order is not part of the anchor contract.
        path.write_text(json.dumps({**original, "anchors": original["anchors"][::-1]}), encoding="utf8")
        self.assertIn("Skein review", review_view.render_packet(self.packet))

    def _build_rich_packet(self) -> tuple[Path, list[skein.Comment]]:
        # Add a long file with changes far apart so context windowing around
        # unchanged commented lines is exercised directly.
        lines = [f"ctx-{i:02d}" for i in range(1, 21)]
        lines[1] = "old-top-line"
        lines[18] = "old-bottom-line"
        self.git("checkout", "--quiet", self.base)
        self.write("long.py", "\n".join(lines) + "\n")
        self.write("removed.txt", "gone line 1\ngone line 2\n")
        self.commit("rich base")
        self.git("branch", "-f", "base")
        self.base = self.rev_parse("base")

        self.git("checkout", "--quiet", "-b", "rich-head")
        head_lines = list(lines)
        head_lines[1] = "new-top-line <tag>"
        head_lines[18] = "new-bottom-line"
        self.write("long.py", "\n".join(head_lines) + "\n")
        self.git("rm", "--quiet", "removed.txt")
        self.write("added.txt", "brand new\n")
        self.write("café-☃.txt", "Unicode ☃\n<script>alert(1)</script>\n")
        self.git("mv", "old-name.txt", "renamed.txt")
        self.commit("rich head")
        self.head = self.rev_parse("rich-head")

        packet = self.root / "rich-packet"
        skein.export_packet(self.repository, "base", "rich-head", packet)

        comments = [
            skein.add_comment(
                packet, "files", self.base, "long.py", "old", 2,
                "Old-side question on replaced line",
            ),
            skein.add_comment(
                packet, "note-new-2", self.head, "long.py", "new", 2,
                "First comment on new line 2\nSecond line\twith tab",
            ),
            skein.add_comment(
                packet, "orphans", self.head, "long.py", "new", 2,
                "Second comment on same new line 2",
            ),
            skein.add_comment(
                packet, "far-unchanged", self.head, "long.py", "new", 10,
                "Comment on unchanged middle line 10",
            ),
            skein.add_comment(
                packet, "deleted-note", self.base, "removed.txt", "old", 1,
                "Why remove this?",
            ),
            skein.add_comment(
                packet, "bidi-note", self.head, "café-☃.txt", "new", 2,
                "Watch \u202ebidi\u202c and <script> & tag",
            ),
        ]
        # Resolve one comment, rebase-annotate one, and add one explicit orphan.
        skein.update_comment(packet, "orphans", resolution="resolved")
        current = skein.loads_comments((packet / "comments.json").read_text(encoding="utf-8"))
        prior = skein.Anchor("0" * 40, "long.py", "new", 1, "prior text")
        current[0] = skein.Comment(
            current[0].identifier, current[0].anchor, current[0].body,
            state="anchored", rebased_from=prior, resolution="open",
        )
        orphan = skein.Comment(
            "lost-line",
            skein.Anchor(self.head, "missing.py", "new", 7, "deleted text"),
            "Orphaned body",
            state="orphan",
            rebased_from=skein.Anchor(self.base, "missing.py", "new", 7, "deleted text"),
            orphan_reason="file deleted in revision",
            resolution="resolved",
        )
        current.append(orphan)
        skein._atomic_comments(packet, current)
        return packet, current

    def test_text_renders_inline_comments_distant_context_and_orphans(self) -> None:
        packet, _ = self._build_rich_packet()
        before = _snapshot(packet)

        text = review_view.render_packet(packet, output_format="text", context=1)
        self.assertIn(f"Base: base ({self.base})", text)
        self.assertIn(f"Head: rich-head ({self.head})", text)
        self.assertIn("Showing 7 of 7 comments. Filters: resolution=all, state=all.", text)
        self.assertIn("All comments: 5 open, 2 resolved; 1 orphan.", text)
        self.assertIn("Orphaned and unplaced comments (1):", text)
        self.assertIn("lost-line", text)
        self.assertIn("file deleted in revision", text)

        # Distant unchanged line 10 must appear because it has an inline comment.
        self.assertIn("ctx-10", text)
        self.assertIn("[far-unchanged | open | anchored | new line 10]", text)
        # Unchanged line 14 far from both hunks and comments should be omitted at context=1,
        # but included when context=-1 (full file).
        self.assertNotIn("ctx-14", text)
        full_text = review_view.render_packet(packet, output_format="text", context=-1)
        self.assertIn("ctx-14", full_text)

        # Old-side and new-side inline comments appear right after their respective lines.
        old_line_idx = text.index("old-top-line")
        old_comment_idx = text.index("[files | open | anchored | old line 2]")
        new_line_idx = text.index("new-top-line <tag>")
        new_comment_1 = text.index("[note-new-2 | open | anchored | new line 2]")
        new_comment_2 = text.index("[orphans | resolved | anchored | new line 2]")
        self.assertLess(old_line_idx, old_comment_idx)
        self.assertLess(old_comment_idx, new_line_idx)
        self.assertLess(new_line_idx, new_comment_1)
        self.assertLess(new_comment_1, new_comment_2)
        self.assertIn("\\u202ebidi\\u202c", text)
        self.assertEqual(_snapshot(packet), before)

    def test_html_is_probe_clean_escaped_deterministic_and_collides_no_ids(self) -> None:
        packet, _ = self._build_rich_packet()
        before = _snapshot(packet)

        page_one = review_view.render_packet(packet, output_format="html")
        page_two = review_view.render_packet(packet, output_format="html")
        self.assertEqual(page_one, page_two)

        tree = probe.parse(page_one)
        findings = probe.audit(tree)
        self.assertEqual(findings, [], f"unexpected probe findings: {findings}")

        # Annotated rows keep status in the gutter and metadata beside the body.
        self.assertIn(
            '<thead><tr><th scope="col" class="number">Old</th>'
            '<th scope="col" class="number">New</th>',
            page_one,
        )
        self.assertNotIn("min-width: 34rem", page_one)
        self.assertIn('<th scope="row" colspan="2" class="comment-label">Comment<span class="sr">.</span></th>', page_one)
        self.assertIn('<td colspan="2" class="comment-cell"><div class="comment-meta">', page_one)

        self.assertIn("Content-Security-Policy", page_one)
        self.assertIn("default-src 'none'; style-src 'unsafe-inline'", page_one)
        self.assertNotIn("<script>alert(1)</script>", page_one)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page_one)
        self.assertIn("\\u202ebidi\\u202c", page_one)
        self.assertIn("file deleted in revision", page_one)
        self.assertIn("Old-side question on replaced line", page_one)
        self.assertIn("Comment on unchanged middle line 10", page_one)

        transcript = "\n".join(probe.transcript(tree, max_rows=500))
        self.assertIn("Comment.", transcript)
        self.assertIn("Orphaned and unplaced comments", transcript)
        self.assertEqual(_snapshot(packet), before)

    def test_filters_preserve_totals_and_reject_invalid_values(self) -> None:
        packet, _ = self._build_rich_packet()

        filtered = review_view.render_packet(
            packet, output_format="text", resolution="resolved", state="anchored",
        )
        self.assertIn("Showing 1 of 7 comments. Filters: resolution=resolved, state=anchored.", filtered)
        self.assertIn("All comments: 5 open, 2 resolved; 1 orphan.", filtered)
        self.assertIn("orphans", filtered)
        self.assertNotIn("lost-line", filtered)
        self.assertNotIn("far-unchanged", filtered)

        only_orphans = review_view.render_packet(
            packet, output_format="html", resolution="resolved", state="orphan",
        )
        self.assertEqual(probe.audit(probe.parse(only_orphans)), [])
        self.assertIn("Showing 1 of 7 comments. Filters: resolution=resolved, state=orphan.", only_orphans)
        self.assertIn("lost-line", only_orphans)
        self.assertNotIn("Old-side question on replaced line", only_orphans)

        with self.assertRaises(ValueError):
            review_view.render_packet(packet, output_format="xml")
        with self.assertRaises(ValueError):
            review_view.render_packet(packet, resolution="closed")
        with self.assertRaises(ValueError):
            review_view.render_packet(packet, context=-2)

    def test_unplaced_anchored_comment_is_never_silently_dropped(self) -> None:
        packet, _ = self._build_rich_packet()
        current = skein.loads_comments((packet / "comments.json").read_text(encoding="utf-8"))
        current.append(
            skein.Comment(
                "unplaced-anchor",
                skein.Anchor(self.head, "nonexistent.py", "new", 1, "ghost"),
                "Must still appear in output",
                state="anchored",
            )
        )
        skein._atomic_comments(packet, current)

        text = review_view.render_packet(packet, output_format="text")
        self.assertIn("Orphaned and unplaced comments (2):", text)
        self.assertIn("unplaced-anchor", text)
        self.assertIn("Must still appear in output", text)

    def test_rejections_preserve_packet_and_cli_works_without_source_repo(self) -> None:
        packet, _ = self._build_rich_packet()
        # Move packet away from repository and run CLI from an isolated directory.
        carried = self.root / "carried-packet"
        shutil.copytree(packet, carried)
        shutil.rmtree(self.repository)

        result = subprocess.run(
            [sys.executable, str(TOOLS / "review_view.py"), str(carried), "--format", "html"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(probe.audit(probe.parse(result.stdout)), [])

        # Max file bytes boundary rejection and override.
        tight = subprocess.run(
            [sys.executable, str(TOOLS / "review_view.py"), str(carried), "--max-file-bytes", "10"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(tight.returncode, 1)
        self.assertEqual(tight.stdout, "")

        # Version-1 comments rejection.
        v1_packet = self.root / "v1-packet"
        shutil.copytree(carried, v1_packet)
        v1_data = json.loads((v1_packet / "comments.json").read_text(encoding="utf-8"))
        v1_data["version"] = 1
        for item in v1_data["comments"]:
            item.pop("resolution")
        (v1_packet / "comments.json").write_text(json.dumps(v1_data), encoding="utf-8")
        v1_run = subprocess.run(
            [sys.executable, str(TOOLS / "review_view.py"), str(v1_packet)],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(v1_run.returncode, 1)
        self.assertIn("migrate-comments", v1_run.stderr)

        # Tampered packet.json file list mismatch.
        tampered = self.root / "tampered-packet"
        shutil.copytree(carried, tampered)
        meta = json.loads((tampered / "packet.json").read_text(encoding="utf-8"))
        meta["files"] = []
        (tampered / "packet.json").write_text(json.dumps(meta), encoding="utf-8")
        before_tamper = _snapshot(tampered)
        tamper_run = subprocess.run(
            [sys.executable, str(TOOLS / "review_view.py"), str(tampered)],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(tamper_run.returncode, 1)
        self.assertEqual(_snapshot(tampered), before_tamper)

        # Symlinked comments.json refusal.
        if hasattr(os, "symlink"):
            linked = self.root / "symlink-packet"
            shutil.copytree(carried, linked)
            real = linked / "comments.json"
            target = self.root / "outside.json"
            target.write_bytes(real.read_bytes())
            real.unlink()
            os.symlink(target, real)
            sym_run = subprocess.run(
                [sys.executable, str(TOOLS / "review_view.py"), str(linked)],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(sym_run.returncode, 1)
            self.assertEqual(sym_run.stdout, "")

    def test_html_and_text_expose_file_comment_counts_and_comment_jump_index(self) -> None:
        packet, _ = self._build_rich_packet()
        before = _snapshot(packet)

        page = review_view.render_packet(packet, output_format="html", context=1)
        tree = probe.parse(page)
        self.assertEqual([], probe.audit(tree))

        # File index summarizes open/resolved counts per file.
        self.assertIn("modified: long.py</a> — 4 comments (3 open, 1 resolved)", page)
        self.assertIn("added:  → added.txt</a> — 0 comments", page)
        self.assertIn("added:  → café-☃.txt</a> — 1 comment (1 open, 0 resolved)", page)

        # Comment jump index links directly to #comment-1..#comment-7 with no broken fragments.
        self.assertIn('<nav id="comments" aria-label="Comments">', page)
        self.assertIn("Comments in view (7)", page)
        for index in range(1, 8):
            self.assertIn(f'href="#comment-{index}"', page)
            self.assertIn(f'id="comment-{index}"', page)
        self.assertNotIn('id="comment-8"', page)

        # Text output includes a changed-files summary with per-file comment counts.
        text = review_view.render_packet(packet, output_format="text", context=1)
        self.assertIn("Changed files: 5 of 5 shown.", text)
        self.assertIn("- modified: long.py — 4 comments (3 open, 1 resolved)", text)
        self.assertIn("- added:  → added.txt — 0 comments", text)
        self.assertEqual(_snapshot(packet), before)

    def test_path_search_and_only_commented_filters_preserve_totals(self) -> None:
        packet, _ = self._build_rich_packet()
        # Add a nested file to test directory-prefix path filtering.
        self.git("checkout", "--quiet", "rich-head")
        self.write("nested/mod.py", "def ok():\n    return 1\n")
        self.commit("add nested file")
        head2 = self.rev_parse("HEAD")
        packet2 = self.root / "nested-packet"
        skein.export_packet(self.repository, "base", head2, packet2)
        skein.add_comment(packet2, "nested-note", head2, "nested/mod.py", "new", 2, "Check nested return")
        skein.add_comment(packet2, "long-note", head2, "long.py", "new", 2, "Check top line")
        skein.add_comment(packet2, "old-renamed", self.base, "old-name.txt", "old", 1, "Before rename")
        skein.update_comment(packet2, "long-note", resolution="resolved")
        orphan = skein.Comment(
            "orphan-search",
            skein.Anchor(head2, "nested/gone.py", "new", 3, "gone"),
            "Needle phrase in orphan body",
            state="orphan",
            rebased_from=skein.Anchor(self.base, "nested/gone.py", "new", 3, "gone"),
            orphan_reason="removed during cleanup",
            resolution="open",
        )
        current = skein.loads_comments((packet2 / "comments.json").read_text(encoding="utf-8"))
        current.append(orphan)
        skein._atomic_comments(packet2, current)
        before = _snapshot(packet2)

        # Directory prefix and exact path filtering match without substring leakage (a.py != ba.py).
        nested_only = review_view.render_packet(
            packet2, output_format="text", paths=["nested"],
        )
        self.assertIn("Showing 2 of 4 comments.", nested_only)
        self.assertIn("All comments: 3 open, 1 resolved; 1 orphan.", nested_only)
        self.assertIn("Changed files: 1 of 6 shown.", nested_only)
        self.assertIn("added:  → nested/mod.py", nested_only)
        self.assertIn("nested-note", nested_only)
        self.assertIn("orphan-search", nested_only)
        self.assertNotIn("long-note", nested_only)
        self.assertNotIn("modified: long.py", nested_only)

        # Renamed file matches on either old_path or new_path.
        renamed_view = review_view.render_packet(
            packet2, output_format="text", paths=["old-name.txt"],
        )
        self.assertIn("old-name.txt → renamed.txt", renamed_view)
        self.assertIn("old-renamed", renamed_view)
        self.assertIn("Changed files: 1 of 6 shown.", renamed_view)

        # Case-insensitive search across body, identifier, path, and orphan reason.
        searched = review_view.render_packet(
            packet2, output_format="html", search="NEEDLE PHRASE", only_commented=True,
        )
        self.assertEqual([], probe.audit(probe.parse(searched)))
        self.assertIn("Showing 1 of 4 comments.", searched)
        self.assertIn("All comments: 3 open, 1 resolved; 1 orphan.", searched)
        self.assertIn("Changed files: 0 of 6 shown.", searched)
        self.assertIn("orphan-search", searched)
        self.assertNotIn("long-note", searched)
        self.assertNotIn("nested-note", searched)

        # --only-commented keeps files with matching inline comments and hides uncommented files.
        commented_html = review_view.render_packet(
            packet2, output_format="html", resolution="open", only_commented=True,
        )
        self.assertEqual([], probe.audit(probe.parse(commented_html)))
        self.assertIn("Changed files: 2 of 6 shown.", commented_html)
        self.assertIn("nested/mod.py", commented_html)
        self.assertIn("old-name.txt → renamed.txt", commented_html)
        self.assertNotIn("long.py", commented_html)
        self.assertNotIn("added.txt", commented_html)

        # Invalid filter inputs fail clearly.
        for bad_kwargs in (
            {"paths": "nested/mod.py"},
            {"paths": [""]},
            {"paths": ["   "]},
            {"search": 123},
            {"only_commented": "yes"},
        ):
            with self.subTest(bad_kwargs=bad_kwargs):
                with self.assertRaises(ValueError):
                    review_view.render_packet(packet2, **bad_kwargs)

        # CLI flags --path, --search, --only-commented work together read-only.
        cli = subprocess.run(
            [
                sys.executable, str(TOOLS / "review_view.py"), str(packet2),
                "--format", "html", "--path", "nested", "--search", "check nested",
                "--only-commented",
            ],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(0, cli.returncode, cli.stderr)
        self.assertEqual([], probe.audit(probe.parse(cli.stdout)))
        self.assertIn("Showing 1 of 4 comments.", cli.stdout)
        self.assertIn("Changed files: 1 of 6 shown.", cli.stdout)
        self.assertIn("nested-note", cli.stdout)
        self.assertNotIn("orphan-search", cli.stdout)
        self.assertEqual(_snapshot(packet2), before)


if __name__ == "__main__":
    unittest.main()
