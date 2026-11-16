"""Comment viewing boundaries and a real exported-packet CLI lifecycle."""
from __future__ import annotations

import contextlib
from dataclasses import replace
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import comments_view
import probe
import skein
from test_skein import SkeinFixture


class Page(HTMLParser):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict]] = []
        self.words: list[str] = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.words.append(data)


def examples() -> list[skein.Comment]:
    anchor = skein.Anchor("a" * 40, "café.py", "new", 12, '<code> & "quoted"')
    return [
        skein.Comment("reader-1", anchor, "Question\n\twith café ☃"),
        skein.Comment("reader-2", replace(anchor, commit="b" * 40), "Resolved reply",
                      state="orphan", rebased_from=anchor, orphan_reason="line missing",
                      resolution="resolved"),
    ]


class CommentViewTests(unittest.TestCase):
    def test_text_preserves_identity_status_body_and_orphan_provenance(self):
        output = comments_view.render_comments(examples())
        for value in ("Showing 2 of 2", "1 open, 1 resolved; 1 orphan",
                      "reader-1 | open | anchored", "reader-2 | resolved | orphan",
                      "café.py | new line 12", "a" * 40, "b" * 40,
                      "Question\n\twith café ☃", '<code> & "quoted"',
                      "Orphan reason: line missing", "Rebased from:"):
            self.assertIn(value, output)

    def test_combined_filters_empty_results_and_totals_are_explicit(self):
        for output_format in ("text", "html"):
            output = comments_view.render_comments(
                examples(), output_format=output_format, state="orphan", resolution="resolved",
            )
            self.assertIn("Showing 1 of 2", output)
            self.assertIn("resolution=resolved, state=orphan", output)
            self.assertIn("1 open, 1 resolved; 1 orphan", output)
            self.assertIn("reader-2", output)
            self.assertNotIn("reader-1", output)
            empty = comments_view.render_comments(
                examples(), output_format=output_format, state="orphan", resolution="open",
            )
            self.assertIn("Showing 0 of 2", empty)
            self.assertIn("No comments match", empty)
            self.assertIn("Showing 0 of 0", comments_view.render_comments(
                [], output_format=output_format,
            ))

    def test_html_is_escaped_offline_navigable_and_deterministic(self):
        records = examples()
        records[0] = replace(records[0], body='<script src="https://example.invalid">&</script>')
        output = comments_view.render_comments(records, output_format="html")
        self.assertEqual(output, comments_view.render_comments(records, output_format="html"))
        page = Page(output)
        self.assertNotIn("script", [tag for tag, attrs in page.tags])
        identifiers = [attrs["id"] for tag, attrs in page.tags if "id" in attrs]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertIn(("html", {"lang": "en"}), page.tags)
        for tag, attrs in page.tags:
            self.assertFalse(any(key.startswith("on") for key in attrs))
            self.assertNotIn("src", attrs)
            for key in ("href", "aria-labelledby"):
                if key in attrs:
                    self.assertIn(attrs[key].removeprefix("#"), identifiers)
        self.assertIn("default-src 'none'", output)
        self.assertIn("&lt;script src=&quot;https://example.invalid&quot;&gt;&amp;&lt;/script&gt;", output)
        self.assertIn('<code> & "quoted"', "".join(page.words))
        self.assertIn("Status: resolved. Anchor: orphan.", "".join(page.words))
        self.assertIn("Rebased from", "".join(page.words))
        self.assertIn("Read-only snapshot", output)
        self.assertIn("color-scheme: light dark", output)
        self.assertIn("prefers-color-scheme: dark", output)
        self.assertIn('class="anchor"', output)
        self.assertIn("ui-monospace", output)
        self.assertEqual([], probe.audit(probe.parse(output)))

    def test_control_characters_are_literal_in_text_and_html(self):
        records = [replace(examples()[0], body="Escape\x1b[31m\r\x7f\u202e\n\t☃")]
        for output_format in ("text", "html"):
            output = comments_view.render_comments(records, output_format=output_format)
            self.assertIn("Escape\\u001b[31m\\u000d\\u007f\\u202e\n\t☃", output)
            for control in ("\x1b", "\r", "\x7f", "\u202e"):
                self.assertNotIn(control, output)

    def test_path_filter_controls_are_visible_without_changing_matching(self):
        raw_path = "src/\u202e.py"
        records = [replace(examples()[0], anchor=replace(examples()[0].anchor, path=raw_path))]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "comments.json"
            original = skein.dumps_comments(records).encode()
            source.write_bytes(original)
            for output_format in ("text", "html"):
                for pattern, shown, displayed in (
                    (raw_path, 1, "src/\\u202e.py"),
                    ("src/\u202e\x1b[31m.py", 0, "src/\\u202e\\u001b[31m.py"),
                    ("src/\\u202e.py", 0, "src/\\u202e.py"),
                ):
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        self.assertEqual(comments_view.main([
                            str(source), "--format", output_format, "--path", pattern,
                        ]), 0)
                    output = out.getvalue()
                    self.assertIn(f"Showing {shown} of 1", output)
                    self.assertIn(f"path={displayed}", output)
                    self.assertNotIn("\u202e", output)
                    self.assertNotIn("\x1b", output)
                    self.assertEqual(source.read_bytes(), original)

    def test_invalid_api_filter_does_not_silently_hide_comments(self):
        for kwargs in (
            {"resolution": "closed"},
            {"state": "missing"},
            {"output_format": "json"},
            {"paths": ["   "]},
            {"paths": "alpha.txt"},
            {"search": 123},
        ):
            with self.assertRaises(ValueError):
                comments_view.render_comments(examples(), **kwargs)

    def test_path_and_search_filters_match_metadata_and_preserve_totals(self):
        anchor_a = skein.Anchor("a" * 40, "src/app.py", "new", 10, "return compute()")
        anchor_b = skein.Anchor("a" * 40, "docs/guide.md", "new", 4, "See guide.")
        rebased = skein.Anchor("c" * 40, "legacy/old.py", "old", 3, "deprecated_call()")
        records = [
            skein.Comment("c-app", anchor_a, "Check edge case"),
            skein.Comment(
                "c-doc",
                anchor_b,
                "Typo in note",
                state="orphan",
                rebased_from=rebased,
                orphan_reason="line rewritten",
                resolution="resolved",
            ),
        ]
        for output_format in ("text", "html"):
            by_path = comments_view.render_comments(
                records, output_format=output_format, paths=["./src/"],
            )
            self.assertIn("Showing 1 of 2", by_path)
            self.assertIn("1 open, 1 resolved; 1 orphan", by_path)
            self.assertIn("c-app", by_path)
            self.assertNotIn("c-doc", by_path)

            for query, expected, hidden_id in (
                ("COMPUTE", "c-app", "c-doc"),
                ("rewritten", "c-doc", "c-app"),
                ("legacy/old.py", "c-doc", "c-app"),
                ("deprecated_call", "c-doc", "c-app"),
            ):
                by_search = comments_view.render_comments(
                    records, output_format=output_format, search=query,
                )
                self.assertIn("Showing 1 of 2", by_search)
                self.assertIn(expected, by_search)
                self.assertNotIn(hidden_id, by_search)

        with tempfile.TemporaryDirectory() as directory:
            comments_path = Path(directory) / "comments.json"
            comments_path.write_text(skein.dumps_comments(records), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = comments_view.main([
                    str(comments_path),
                    "--path", "./src",
                    "--search", "compute",
                ])
            self.assertEqual(rc, 0)
            self.assertIn("Showing 1 of 2", out.getvalue())
            self.assertIn("c-app", out.getvalue())
            self.assertNotIn("c-doc", out.getvalue())

            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(comments_view.main([str(comments_path), "--path", "./"]), 2)

    def test_reader_errors_produce_no_partial_output_and_preserve_bytes(self):
        valid = skein.dumps_comments(examples())
        malformed = json.loads(valid)
        malformed["comments"][1]["resolution"] = "closed"
        duplicate_ids = json.loads(valid)
        duplicate_ids["comments"][1]["id"] = "reader-1"
        inputs = [b"\xff", b"{", valid.replace('"version": 2', '"version": 1').encode(),
                  valid.replace('"version": 2', '"version": 2, "version": 2').encode(),
                  json.dumps(malformed).encode(), json.dumps(duplicate_ids).encode()]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comments.json"
            for data in inputs:
                with self.subTest(data=data[:40]):
                    path.write_bytes(data)
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        code = comments_view.main([str(path), "--resolution", "open"])
                    self.assertEqual(1, code)
                    self.assertEqual("", stdout.getvalue())
                    self.assertIn("comments-view:", stderr.getvalue())
                    self.assertEqual(data, path.read_bytes())
            path.write_text(valid, encoding="utf-8")
            link = Path(directory) / "link.json"
            link.symlink_to(path)
            for unreadable in (link, Path(directory), Path(directory) / "absent.json"):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(1, comments_view.main([str(unreadable)]))
            with patch.object(skein, "JSON_LIMIT", 10):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(1, comments_view.main([str(path)]))


class CommentViewCliTests(SkeinFixture):
    def test_real_packet_cli_edit_resolve_reopen_and_read_only_view(self):
        self.export()
        skein.add_comment(self.packet, "cli-note", self.head, "alpha.txt", "new", 1, "First question")
        viewer = Path(comments_view.__file__).resolve()
        exporter = Path(skein.__file__).resolve()

        def invoke(script, *arguments):
            result = subprocess.run(
                [sys.executable, str(script), *map(str, arguments)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            return result.stdout.decode("utf-8")

        for command, extra, expected_body, expected_status in (
            (None, [], "First question", "open"),
            ("edit-comment", ["--body", "Edited ☃ question"], "Edited ☃ question", "open"),
            ("resolve-comment", [], "Edited ☃ question", "resolved"),
            ("reopen-comment", [], "Edited ☃ question", "open"),
        ):
            if command:
                invoke(exporter, command, self.packet, "--id", "cli-note", *extra)
            before = {p.name: p.read_bytes() for p in self.packet.iterdir()}
            for arguments in ([], ["--format", "html"]):
                output = invoke(viewer, self.packet / "comments.json", *arguments)
                self.assertIn(expected_body, output)
                self.assertIn(expected_status, output)
                self.assertIn(self.head, output)
                self.assertIn("alpha.txt", output)
            self.assertEqual(before, {p.name: p.read_bytes() for p in self.packet.iterdir()})


if __name__ == "__main__":
    unittest.main()
