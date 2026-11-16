"""Real-Git and bundle tests for Skein's offline two-revision interdiff view."""
from __future__ import annotations

import contextlib
from dataclasses import replace
import io
import json
from pathlib import Path
import shutil
import unittest

import exchange
import interdiff
import probe
import skein
from test_skein import SkeinFixture


def _snapshot(directory: Path) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


class InterdiffTests(SkeinFixture):
    def _build_two_revision_scenario(self) -> tuple[Path, Path]:
        """Create packet_v1 and packet_v2 with reanchored, orphaned, unchanged, base, and V1-only comments."""
        self.git("checkout", "--quiet", self.base)
        self.write(
            "app.py",
            "def greet():\n    return 'hello'\n\ndef lantern():\n    return 'old'\n",
        )
        self.write("stable.py", "BASE_VALUE = 1\n")
        self.commit("base commit")
        self.git("branch", "-f", "base")
        self.base = self.rev_parse("base")

        # Revision 1: modifies app.py and stable.py, adds notes.txt
        self.git("checkout", "--quiet", "-B", "feature-v1")
        self.write(
            "app.py",
            "def greet():\n    return 'hi'\n\ndef lantern():\n    return 'v1'\n",
        )
        self.write("stable.py", "BASE_VALUE = 2\n")
        self.write("notes.txt", "first line\nsecond line\n")
        self.commit("feature v1")
        head_v1 = self.rev_parse("feature-v1")

        packet_v1 = self.root / "packet-v1"
        skein.export_packet(self.repository, "base", head_v1, packet_v1)
        skein.add_comment(
            packet_v1, "reanchored-note", head_v1, "app.py", "new", 2,
            "Check greeting return",
        )
        skein.add_comment(
            packet_v1, "lantern-orphan", head_v1, "app.py", "new", 5,
            "Lantern needs updating",
        )
        skein.add_comment(
            packet_v1, "stable-note", head_v1, "stable.py", "new", 1,
            "Changed only in v1, untouched in v2",
        )
        skein.add_comment(
            packet_v1, "base-note", self.base, "app.py", "old", 2,
            "Compare with original base greeting",
        )
        skein.add_comment(
            packet_v1, "v1-only-note", head_v1, "notes.txt", "new", 2,
            "Temporary note not carried to v2",
        )

        # Revision 2: shifts line in app.py, changes lantern line, modifies notes.txt, leaves stable.py untouched
        self.git("checkout", "--quiet", "-B", "feature-v2", "feature-v1")
        self.write(
            "app.py",
            "# header\ndef greet():\n    return 'hi'\n\ndef lantern():\n    return 'v2'\n",
        )
        self.write("notes.txt", "first line\nsecond line revised\nthird line\n")
        self.commit("feature v2")
        head_v2 = self.rev_parse("feature-v2")

        packet_v2 = self.root / "packet-v2"
        skein.export_packet(self.repository, "base", head_v2, packet_v2)

        # Carry all comments except v1-only-note so V1-only handling is also exercised.
        subset_v1 = self.root / "v1-carry-subset.json"
        carried_src = [
            c for c in skein.loads_comments((packet_v1 / "comments.json").read_text(encoding="utf-8"))
            if c.identifier != "v1-only-note"
        ]
        subset_v1.write_text(skein.dumps_comments(carried_src), encoding="utf-8")
        exchange.carry_comments(packet_v2, [subset_v1])
        skein.update_comment(packet_v2, "reanchored-note", resolution="resolved")
        skein.add_comment(
            packet_v2, "new-v2-note", head_v2, "notes.txt", "new", 3,
            "Added third line looks good",
        )
        return packet_v1, packet_v2

    def test_interdiff_places_carried_orphaned_unchanged_and_v1_only_without_repo(self) -> None:
        packet_v1, packet_v2 = self._build_two_revision_scenario()
        snap_v1 = _snapshot(packet_v1)
        snap_v2 = _snapshot(packet_v2)

        # Author repository is completely absent; only the two exported packets are read.
        shutil.rmtree(self.repository)

        for output_format in ("text", "html"):
            with self.subTest(output_format=output_format):
                rendered = interdiff.render_interdiff(
                    packet_v1, packet_v2, output_format=output_format, context=1,
                )
                # Diff shows V1 -> V2 changes only (app.py and notes.txt), not stable.py.
                self.assertIn("app.py", rendered)
                self.assertIn("notes.txt", rendered)
                self.assertNotIn("modified: stable.py", rendered)
                # Base stayed identical between revisions.
                self.assertIn("unchanged", rendered.lower())
                # Transition & inline/bucket placements:
                self.assertIn("reanchored-note", rendered)
                self.assertIn("lantern-orphan", rendered)
                self.assertIn("new-v2-note", rendered)
                self.assertIn("v1-only-note", rendered)
                self.assertIn("stable-note", rendered)
                self.assertIn("base-note", rendered)
                self.assertIn("V1-only", rendered)
                if output_format == "html":
                    self.assertEqual([], probe.audit(probe.parse(rendered)))
                    transcript = "\n".join(probe.transcript(probe.parse(rendered), max_rows=300))
                    self.assertIn("lantern-orphan", transcript)
                    self.assertIn("reanchored-note", transcript)
                    self.assertIn("stable-note", transcript)
                    self.assertIn("base-note", transcript)

        json_out = json.loads(interdiff.render_interdiff(packet_v1, packet_v2, output_format="json"))
        self.assertTrue(json_out["same_base"])
        self.assertEqual(["app.py", "notes.txt"], [f["display_path"] for f in json_out["changed_files"]])
        self.assertIn("lantern-orphan", json_out["transitions"]["newly_orphaned"])
        self.assertIn("reanchored-note", json_out["transitions"]["reanchored"])
        self.assertIn("v1-only-note", json_out["transitions"]["only_in_first"])
        self.assertIn("new-v2-note", json_out["transitions"]["only_in_second"])
        self.assertIn("lantern-orphan", json_out["placements"]["inline_v1_orphan"])
        self.assertIn("reanchored-note", json_out["placements"]["inline_v2"])
        self.assertIn("v1-only-note", json_out["placements"]["inline_v1_only"])
        self.assertIn("stable-note", json_out["placements"]["unchanged_files"])
        self.assertIn("base-note", json_out["placements"]["base_side"])

        self.assertEqual(snap_v1, _snapshot(packet_v1))
        self.assertEqual(snap_v2, _snapshot(packet_v2))

    def test_divergent_variants_keep_both_revisions_in_all_formats_and_filters(self) -> None:
        p1, p2 = self._build_two_revision_scenario()
        # Interdiff uses the same compact headers and comment-row layout.
        page = interdiff.render_interdiff(p1, p2, output_format="html")
        self.assertEqual([], probe.audit(probe.parse(page)))
        self.assertIn(
            '<thead><tr><th scope="col" class="number">V1</th>'
            '<th scope="col" class="number">V2</th>',
            page,
        )
        self.assertNotIn("min-width: 34rem", page)
        self.assertIn('<th scope="row" colspan="2" class="comment-label">Comment<span class="sr">.</span></th>', page)
        self.assertIn('<td colspan="2" class="comment-cell"><div class="comment-meta">', page)
        old = next(c for c in skein.loads_comments((p1 / "comments.json").read_text())
                   if c.identifier == "v1-only-note")
        new = next(c for c in skein.loads_comments((p2 / "comments.json").read_text())
                   if c.identifier == "new-v2-note")
        older = [
            replace(old, body="Earlier original question"),
            replace(old, identifier="v1-only-note--divergent-cafebabe", body="Earlier variant question"),
            replace(old, identifier="same-id", body="Earlier same ID question"),
        ]
        newer = [
            replace(new, identifier="v1-only-note--divergent-deadbeef",
                    body="Revised variant answer", resolution="resolved"),
            replace(new, identifier="same-id", body="Revised same ID answer"),
        ]
        for packet, comments in ((p1, older), (p2, newer)):
            (packet / "comments.json").write_text(skein.dumps_comments(comments))
        report = exchange.compare_packets(p1, p2)
        self.assertEqual([], report["only_in_first"])
        self.assertEqual(["same-id", "v1-only-note"], report["divergent"])
        snapshots = (_snapshot(p1), _snapshot(p2))
        shutil.rmtree(self.repository)

        cases = [
            ({}, older + newer),
            ({"resolution": "open"}, older + [newer[1]]),
            ({"resolution": "resolved"}, [newer[0]]),
            ({"state": "anchored"}, older + newer),
            ({"state": "orphan"}, []),
            ({"paths": ["notes.txt"], "only_commented": True, "context": 0}, older + newer),
            ({"paths": ["app.py"], "only_commented": True}, []),
            ({"search": "earlier"}, older),
            ({"search": "divergent"}, older + newer),
        ]
        for fmt in ("text", "html", "json"):
            for filters, expected in cases:
                with self.subTest(format=fmt, filters=filters):
                    output = interdiff.render_interdiff(p1, p2, output_format=fmt, **filters)
                    if fmt == "json":
                        data = json.loads(output)
                        actual = data["comments"]
                        self.assertCountEqual([c.to_dict() for c in expected],
                                              [e["comment"] for e in actual])
                        self.assertEqual(len(expected), data["counts"]["selected_entries"])
                        for entry in actual:
                            self.assertEqual("divergent", entry["transition"])
                            comment = skein.Comment.from_dict(entry["comment"])
                            self.assertEqual("V2" if comment in newer else "V1", entry["origin"])
                        if not filters:
                            self.assertCountEqual([c.identifier for c in older],
                                                  data["placements"]["inline_v1_divergent"])
                            self.assertEqual([], data["placements"]["inline_v1_only"])
                    else:
                        for comment in older + newer:
                            self.assertEqual(comment in expected, comment.body in output)
                        if older[0] in expected:
                            self.assertIn("V1 (divergent)" if fmt == "text" else "V1, divergent", output)
                        if fmt == "html":
                            self.assertEqual([], probe.audit(probe.parse(output)))
        self.assertEqual(snapshots, (_snapshot(p1), _snapshot(p2)))

    def test_divergent_groups_keep_buckets_without_duplicating_identical_records(self) -> None:
        self.export()
        p2 = self.root / "packet-copy"
        shutil.copytree(self.packet, p2)
        skein.add_comment(self.packet, "shared--divergent-deadbeef", self.head,
                          "alpha.txt", "new", 1, "Identical retained record")
        common = skein.loads_comments((self.packet / "comments.json").read_text())[0]
        older = [
            common,
            replace(common, identifier="shared", state="orphan",
                    orphan_reason="Older unmatched anchor", body="Earlier orphan content"),
            replace(common, identifier="shared--divergent-cafebabe",
                    anchor=skein.Anchor(self.base, "alpha.txt", "old", 1, "first"),
                    body="Earlier base content"),
        ]
        newer = [common, replace(common, identifier="shared--divergent-12345678",
                                 body="Revised unchanged-file content")]
        for packet, comments in ((self.packet, older), (p2, newer)):
            (packet / "comments.json").write_text(skein.dumps_comments(comments))
        for fmt in ("text", "html", "json"):
            with self.subTest(format=fmt):
                output = interdiff.render_interdiff(self.packet, p2, output_format=fmt,
                                                    only_commented=True)
                if fmt == "json":
                    data = json.loads(output)
                    self.assertCountEqual([c.to_dict() for c in older + newer[1:]],
                                          [e["comment"] for e in data["comments"]])
                    common_entries = [e for e in data["comments"]
                                      if e["comment"]["id"] == common.identifier]
                    self.assertEqual(1, len(common_entries))
                    self.assertEqual("V2", common_entries[0]["origin"])
                    self.assertEqual(["shared"], data["placements"]["orphans_unplaced"])
                    self.assertEqual([older[2].identifier], data["placements"]["base_side"])
                    self.assertCountEqual([c.identifier for c in newer],
                                          data["placements"]["unchanged_files"])
                else:
                    for comment in older + newer:
                        self.assertIn(comment.body, output)
                    self.assertIn("Showing 4 of 4 comments", output)
                    if fmt == "html":
                        self.assertEqual([], probe.audit(probe.parse(output)))

    def test_base_shift_is_reported_honestly(self) -> None:
        self.git("checkout", "--quiet", self.base)
        self.write("shared.txt", "line 1\n")
        self.commit("base 1")
        self.git("branch", "-f", "base1")
        base1 = self.rev_parse("base1")

        self.git("checkout", "--quiet", "-B", "feat1", "base1")
        self.write("shared.txt", "line 1\nfeat 1\n")
        self.commit("feat 1")
        head1 = self.rev_parse("feat1")

        self.git("checkout", "--quiet", "-B", "base2", "base1")
        self.write("upstream.txt", "upstream change\n")
        self.commit("base 2")
        base2 = self.rev_parse("base2")

        self.git("checkout", "--quiet", "-B", "feat2", "base2")
        self.write("shared.txt", "line 1\nfeat 2\n")
        self.commit("feat 2")
        head2 = self.rev_parse("feat2")

        p1 = self.root / "p1"
        p2 = self.root / "p2"
        skein.export_packet(self.repository, base1, head1, p1)
        skein.export_packet(self.repository, base2, head2, p2)

        text = interdiff.render_interdiff(p1, p2, output_format="text")
        html_out = interdiff.render_interdiff(p1, p2, output_format="html")
        data = json.loads(interdiff.render_interdiff(p1, p2, output_format="json"))

        self.assertFalse(data["same_base"])
        self.assertIn("Base revision changed between packets", text)
        self.assertIn("Base revision changed between packets", html_out)
        self.assertIn("upstream.txt", text)
        self.assertIn("shared.txt", text)
        self.assertEqual([], probe.audit(probe.parse(html_out)))

    def test_identical_heads_reports_no_code_delta_and_passes_audit(self) -> None:
        self.export()
        p2 = self.root / "packet-copy"
        shutil.copytree(self.packet, p2)
        skein.add_comment(p2, "second-note", self.head, "alpha.txt", "new", 1, "Added in copy")

        text = interdiff.render_interdiff(self.packet, p2, output_format="text")
        html_out = interdiff.render_interdiff(self.packet, p2, output_format="html")
        data = json.loads(interdiff.render_interdiff(self.packet, p2, output_format="json"))

        self.assertEqual([], data["changed_files"])
        self.assertIn("identical file trees", text.lower())
        self.assertIn("identical file trees", html_out.lower())
        self.assertIn("second-note", text)
        self.assertIn("second-note", html_out)
        self.assertEqual([], probe.audit(probe.parse(html_out)))

    def test_rename_and_delete_between_revisions(self) -> None:
        self.git("checkout", "--quiet", self.base)
        self.write("mod.txt", "line one\nline two\nline three\nline four\n")
        self.write("drop.txt", "to be dropped\n")
        self.commit("base rename-delete")
        self.git("branch", "-f", "base")

        self.git("checkout", "--quiet", "-B", "v1")
        self.write("mod.txt", "line one\nline two revised\nline three\nline four\n")
        self.write("drop.txt", "still here in v1\n")
        self.commit("v1")
        h1 = self.rev_parse("v1")

        self.git("checkout", "--quiet", "-B", "v2")
        self.git("mv", "mod.txt", "moved.txt")
        self.write("moved.txt", "line one\nline two revised\nline three\nline four\nline five added\n")
        self.git("rm", "--quiet", "drop.txt")
        self.commit("v2")
        h2 = self.rev_parse("v2")

        p1 = self.root / "p1"
        p2 = self.root / "p2"
        skein.export_packet(self.repository, "base", h1, p1)
        skein.export_packet(self.repository, "base", h2, p2)
        skein.add_comment(p1, "v1-drop-note", h1, "drop.txt", "new", 1, "Why keep drop.txt?")
        skein.add_comment(p2, "v2-moved-note", h2, "moved.txt", "new", 5, "Nice addition after rename")

        data = json.loads(interdiff.render_interdiff(p1, p2, output_format="json"))
        statuses = {f["display_path"]: f["status"] for f in data["changed_files"]}
        self.assertEqual("renamed", statuses["mod.txt \u2192 moved.txt"])
        self.assertEqual("deleted", statuses["drop.txt \u2192 "])
        self.assertIn("v1-drop-note", data["placements"]["inline_v1_only"])
        self.assertIn("v2-moved-note", data["placements"]["inline_v2"])

        html_out = interdiff.render_interdiff(p1, p2, output_format="html")
        self.assertIn("renamed: mod.txt \u2192 moved.txt", html_out)
        self.assertIn("deleted: drop.txt \u2192 ", html_out)
        self.assertEqual([], probe.audit(probe.parse(html_out)))

    def test_controls_escaped_without_losing_raw_diff_semantics(self) -> None:
        controls = "\u202e\x1b\r\x7f"
        self.git("checkout", "--quiet", self.base)
        self.write("ctrl.txt", "top\nline\n")
        self.commit("base ctrl")
        self.git("branch", "-f", "base")

        self.git("checkout", "--quiet", "-B", "v1")
        self.write("ctrl.txt", f"top\nvalue {controls}\tend\n")
        self.commit("v1 ctrl")
        h1 = self.rev_parse("v1")

        self.git("checkout", "--quiet", "-B", "v2")
        self.write("ctrl.txt", "top\nvalue \\u202e\\u001b\\u000d\\u007f\tend\n")
        self.commit("v2 ctrl")
        h2 = self.rev_parse("v2")

        p1 = self.root / "p1"
        p2 = self.root / "p2"
        skein.export_packet(self.repository, "base", h1, p1)
        skein.export_packet(self.repository, "base", h2, p2)
        skein.add_comment(p2, "ctrl-comment", h2, "ctrl.txt", "new", 2, f"body {controls}")

        for fmt in ("text", "html"):
            out = interdiff.render_interdiff(
                p1, p2, output_format=fmt, paths=["ctrl.txt"], search=f"body {controls}",
            )
            for ch in controls:
                self.assertNotIn(ch, out)
                self.assertIn(f"\\u{ord(ch):04x}", out)
            self.assertIn("ctrl-comment", out)
            self.assertIn("\tend", out)
            if fmt == "html":
                self.assertEqual([], probe.audit(probe.parse(out)))

    def test_filters_and_determinism(self) -> None:
        p1, p2 = self._build_two_revision_scenario()

        open_text = interdiff.render_interdiff(
            p1, p2, output_format="text", resolution="open", state="orphan",
        )
        self.assertIn("lantern-orphan", open_text)
        self.assertNotIn("reanchored-note", open_text)
        self.assertNotIn("new-v2-note", open_text)

        path_html = interdiff.render_interdiff(
            p1, p2, output_format="html", paths=["notes.txt"], only_commented=True,
        )
        self.assertIn("notes.txt", path_html)
        self.assertNotIn("modified: app.py", path_html)
        self.assertIn("new-v2-note", path_html)
        self.assertIn("v1-only-note", path_html)
        self.assertEqual([], probe.audit(probe.parse(path_html)))

        for fmt in ("text", "html", "json"):
            a = interdiff.render_interdiff(p1, p2, output_format=fmt)
            b = interdiff.render_interdiff(p1, p2, output_format=fmt)
            self.assertEqual(a, b)

        # CLI main returns 0 cleanly for text, html, and json.
        for fmt in ("text", "html", "json"):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = interdiff.main([str(p1), str(p2), "--format", fmt])
            self.assertEqual(0, code)
            self.assertEqual("", stderr.getvalue())
            self.assertTrue(stdout.getvalue())

        # Inline V1 label appears for V1-placed orphans in text as well as HTML.
        text_full = interdiff.render_interdiff(p1, p2, output_format="text")
        self.assertIn("V1 line 5", text_full)
        self.assertIn("V2 line 3", text_full)

    def test_rejects_tampered_symlink_and_oversized_inputs_without_writes(self) -> None:
        p1, p2 = self._build_two_revision_scenario()
        snap_v1 = _snapshot(p1)
        snap_v2 = _snapshot(p2)

        # Oversized max_file_bytes check
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = interdiff.main([str(p1), str(p2), "--max-file-bytes", "5"])
        self.assertEqual(1, code)
        self.assertEqual("", stdout.getvalue())
        self.assertTrue(stderr.getvalue().startswith("error: "))

        # Symlinked packet directory rejected
        link = self.root / "link-packet"
        link.symlink_to(p2)
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = interdiff.main([str(p1), str(link)])
        self.assertEqual(1, code)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("not a regular directory", stderr.getvalue().lower())

        # Symlinked internal comments.json rejected without reads
        p2_sym = self.root / "p2-sym"
        shutil.copytree(p2, p2_sym)
        target_comments = self.root / "outside-comments.json"
        target_comments.write_bytes((p2 / "comments.json").read_bytes())
        (p2_sym / "comments.json").unlink()
        (p2_sym / "comments.json").symlink_to(target_comments)
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = interdiff.main([str(p1), str(p2_sym)])
        self.assertEqual(1, code)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("not a regular file", stderr.getvalue().lower())

        # Tampered anchors.json rejected without modifying packet
        anchors_path = p2 / "anchors.json"
        data = json.loads(anchors_path.read_text(encoding="utf-8"))
        data["anchors"] = data["anchors"][1:]
        anchors_path.write_text(json.dumps(data), encoding="utf-8")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = interdiff.main([str(p1), str(p2)])
        self.assertEqual(1, code)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("anchors.json", stderr.getvalue())

        self.assertEqual(snap_v1, _snapshot(p1))

    def test_full_commit_identity_not_duplicated_and_anchor_card_preserves_lines(self) -> None:
        self.git("checkout", "--quiet", "base")
        base_oid = self.rev_parse("HEAD")
        self.write("a.txt", "one\ntwo\n")
        self.commit("v1 commit")
        v1_oid = self.rev_parse("HEAD")
        self.write("a.txt", "one\nthree\n")
        self.commit("v2 commit")
        v2_oid = self.rev_parse("HEAD")
        p1 = self.root / "oid-p1"
        p2 = self.root / "oid-p2"
        skein.export_packet(self.repository, base_oid, v1_oid, p1)
        skein.export_packet(self.repository, base_oid, v2_oid, p2)
        text = interdiff.render_interdiff(p1, p2, output_format="text")
        self.assertIn(f"V1 head: {v1_oid}\n", text)
        self.assertIn(f"V2 head: {v2_oid}\n", text)
        self.assertIn(f"Base: {base_oid} — unchanged between revisions.", text)
        for oid in (base_oid, v1_oid, v2_oid):
            self.assertNotIn(f"{oid} ({oid})", text)
        page = interdiff.render_interdiff(p1, p2, output_format="html")
        self.assertEqual([], probe.audit(probe.parse(page)))
        self.assertIn(f"V1 head: <code>{v1_oid}</code>", page)
        self.assertIn(f"V2 head: <code>{v2_oid}</code>", page)
        for oid in (base_oid, v1_oid, v2_oid):
            self.assertNotIn(f"{oid} ({oid})", page)
        self.assertIn(".comment-extra code", page)
        self.assertIn("white-space: pre-wrap", page)


if __name__ == "__main__":
    unittest.main()
