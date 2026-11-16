"""Keep comments with mismatched raw line text out of verified inline diffs."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys

import probe
import review_view
import skein
from test_skein import SkeinFixture


class CommentAnchorPlacementTests(SkeinFixture):
    def snapshot(self) -> dict[str, bytes]:
        return {path.name: path.read_bytes() for path in self.packet.iterdir()}

    def test_same_coordinate_comments_require_matching_text_on_both_sides(self) -> None:
        self.export()
        comments = []
        for side, commit in (("old", self.base), ("new", self.head)):
            valid = skein.add_comment(
                self.packet, f"valid-{side}", commit, "alpha.txt", side, 1,
                f"Matching {side} comment stays inline",
            )
            comments.extend([
                valid,
                replace(valid, identifier=f"mismatch-{side}",
                        anchor=replace(valid.anchor, text=f"Wrong {side} line <tag>\u202e"),
                        body=f"Mismatched {side} comment must stay visible"),
            ])
        skein._atomic_comments(self.packet, comments)
        before = self.snapshot()
        shutil.rmtree(self.repository)

        text = review_view.render_packet(self.packet, context=0)
        self.assertIn("Orphaned and unplaced comments (2):", text)
        unplaced, diff = text.split("===", 1)
        for side in ("old", "new"):
            self.assertIn(f"mismatch-{side}", unplaced)
            self.assertIn(f"Wrong {side} line <tag>\\u202e", unplaced)
            self.assertNotIn(f"mismatch-{side}", diff)
            self.assertIn(f"[valid-{side} | open | anchored | {side} line 1]", diff)
        self.assertIn("anchor target or text does not match verified packet diffs", unplaced)

        result = subprocess.run(
            [sys.executable, str(Path(review_view.__file__)), str(self.packet),
             "--format", "html", "--context", "0"],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        page = result.stdout
        self.assertIn("Orphaned and unplaced comments (2)", page)
        unplaced, diff = page.split('<section id="file-1"', 1)
        for side in ("old", "new"):
            self.assertIn(f"mismatch-{side}", unplaced)
            self.assertIn(f"Wrong {side} line &lt;tag&gt;\\u202e", unplaced)
            self.assertNotIn(f"mismatch-{side}", diff)
            self.assertIn(f"valid-{side}", diff)
        self.assertEqual([], probe.audit(probe.parse(page)))
        self.assertEqual(before, self.snapshot())

    def test_raw_bidi_and_literal_escape_are_distinct_anchor_texts(self) -> None:
        self.git("checkout", "--quiet", self.base)
        self.write("controls.txt", "value \u202e\n")
        self.commit("raw marker")
        self.git("branch", "-f", "base")
        self.base = self.rev_parse("base")
        self.git("checkout", "--quiet", "-B", "feature")
        self.write("controls.txt", "value \\u202e\n")
        self.commit("literal marker")
        self.head = self.rev_parse("feature")
        self.export()
        comments = []
        for side, commit, wrong_text in (("old", self.base, "value \\u202e"),
                                         ("new", self.head, "value \u202e")):
            valid = skein.add_comment(
                self.packet, f"valid-{side}", commit, "controls.txt", side, 1, "Correct raw text",
            )
            comments.extend([
                valid,
                replace(valid, identifier=f"mismatch-{side}",
                        anchor=replace(valid.anchor, text=wrong_text), body="Different raw text"),
            ])
        skein._atomic_comments(self.packet, comments)
        before = self.snapshot()

        for output_format in ("text", "html"):
            with self.subTest(output_format=output_format):
                result = review_view.render_packet(self.packet, output_format=output_format)
                self.assertIn("Orphaned and unplaced comments (2)", result)
                self.assertNotIn("\u202e", result)
                self.assertIn("\\u202e", result)
                for side in ("old", "new"):
                    self.assertEqual(1, result.count(f"mismatch-{side}"))
                    self.assertIn(f"valid-{side}", result)
                if output_format == "html":
                    self.assertEqual([], probe.audit(probe.parse(result)))
        filtered = review_view.render_packet(self.packet, resolution="resolved")
        self.assertIn("Showing 0 of 4 comments", filtered)
        self.assertIn("All comments: 4 open, 0 resolved; 0 orphan.", filtered)
        self.assertNotIn("mismatch-old", filtered)
        self.assertEqual(before, self.snapshot())
