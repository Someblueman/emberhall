"""Tests for the offline Skein packet probe.

The fixtures mirror the shape of a milestone-2 review page: a static, escaped,
script-free document whose diff rows carry their change kind as words. The
probe's checks are deliberately generic, so these fixtures test the probe's
judgements rather than Skein's own renderer.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import comment_editor
import probe
import skein

CLEAN_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Skein review packet</title><style>body { color: #222; }</style></head>
<body><a class="skip" href="#files">Skip to changed files</a>
<main><h1>Skein review packet</h1>
<p class="identity">Base: <code>base111</code><br>Head: <code>head222</code></p>
<nav id="files" aria-label="Changed files"><ol><li><a href="#file-1">Modified: src/greet.py</a></li></ol></nav>
<section id="file-1" aria-labelledby="file-1-title">
<h2 id="file-1-title">Modified: src/greet.py</h2>
<div class="scroll"><table><caption>Old line and new line; 2 old / 2 new</caption>
<thead><tr><th scope="col">Old</th><th scope="col">New</th><th scope="col">Base text</th><th scope="col">Head text</th></tr></thead>
<tbody>
<tr class="equal"><th scope="row" class="number old-number"><span class="sr">Unchanged.</span> 1</th><th scope="row" class="number new-number">1</th><td class="old code">first</td><td class="new code">first</td></tr>
<tr class="insert"><th scope="row" class="number old-number"><span class="sr">Added.</span> </th><th scope="row" class="number new-number">2</th><td class="old code"></td><td class="new code">second</td></tr>
</tbody></table></div></section>
<footer>Review Skein packet format 1.</footer></main></body></html>
"""

HEAD_ROW = ('<thead><tr><th scope="col">Old</th><th scope="col">New</th>'
            '<th scope="col">Base text</th><th scope="col">Head text</th></tr></thead>')


class ProbeAuditTest(unittest.TestCase):
    """The probe's judgements about the markup."""

    def codes(self, findings) -> list:
        return sorted(finding.code for finding in findings)

    def test_clean_page_reports_nothing(self):
        self.assertEqual(self.codes(probe.audit(probe.parse(CLEAN_PAGE))), [])

    def test_missing_language_is_reported(self):
        page = CLEAN_PAGE.replace('<html lang="en">', "<html>")
        self.assertIn("missing-lang", self.codes(probe.audit(probe.parse(page))))

    def test_script_element_is_reported(self):
        page = CLEAN_PAGE.replace("</body>", "<script>alert(1)</script></body>")
        self.assertIn("script-element", self.codes(probe.audit(probe.parse(page))))

    def test_inline_handler_is_reported(self):
        page = CLEAN_PAGE.replace("<main>", '<main onclick="x()">')
        self.assertIn("inline-handler", self.codes(probe.audit(probe.parse(page))))

    def test_external_reference_is_reported(self):
        page = CLEAN_PAGE.replace('<a class="skip" href="#files">',
                                  '<a class="skip" href="https://example.invalid/x">')
        self.assertIn("external-reference", self.codes(probe.audit(probe.parse(page))))

    def test_relative_and_parent_references_leaving_page_are_reported(self):
        for tag in (
            '<img src="../outside.png">',
            '<img src="/outside.png">',
            '<a href="other.html">other</a>',
            '<img srcset="outside.png 1x">',
        ):
            page = CLEAN_PAGE.replace("</body>", f"{tag}</body>")
            self.assertIn("external-reference", self.codes(probe.audit(probe.parse(page))), tag)

    def test_duplicate_id_is_reported(self):
        page = CLEAN_PAGE.replace('id="file-1-title"', 'id="file-1"')
        self.assertIn("duplicate-id", self.codes(probe.audit(probe.parse(page))))

    def test_broken_fragment_is_reported(self):
        page = CLEAN_PAGE.replace('href="#files"', 'href="#nowhere"')
        self.assertIn("broken-fragment", self.codes(probe.audit(probe.parse(page))))

    def test_broken_aria_reference_is_reported(self):
        page = CLEAN_PAGE.replace('aria-labelledby="file-1-title"',
                                  'aria-labelledby="missing-title"')
        self.assertIn("broken-reference", self.codes(probe.audit(probe.parse(page))))

    def test_heading_skip_is_reported(self):
        page = CLEAN_PAGE.replace('<h2 id="file-1-title">', '<h3 id="file-1-title">')
        self.assertIn("heading-skip", self.codes(probe.audit(probe.parse(page))))

    def test_table_without_caption_is_reported(self):
        page = CLEAN_PAGE.replace("<caption>Old line and new line; 2 old / 2 new</caption>", "")
        self.assertIn("table-without-caption", self.codes(probe.audit(probe.parse(page))))

    def test_table_without_column_headers_is_reported(self):
        page = CLEAN_PAGE.replace(HEAD_ROW, "")
        self.assertIn("table-without-column-headers", self.codes(probe.audit(probe.parse(page))))

    def test_row_status_in_colour_only_is_reported(self):
        page = CLEAN_PAGE.replace('<span class="sr">Added.</span> ', "")
        self.assertIn("row-without-words", self.codes(probe.audit(probe.parse(page))))

    def test_diff_rows_without_row_scope_or_status_spans_are_reported(self):
        page = (
            CLEAN_PAGE
            .replace('<span class="sr">Unchanged.</span> ', "")
            .replace('<span class="sr">Added.</span> ', "")
            .replace(' scope="row"', "")
        )
        findings = probe.audit(probe.parse(page))
        self.assertEqual([finding.code for finding in findings],
                         ["row-without-words", "row-without-words"])

    def test_aria_hidden_status_cell_and_ancestors_are_reported_and_not_spoken(self):
        hidden_cell_page = CLEAN_PAGE.replace(
            '<tr class="insert"><th scope="row" class="number old-number"><span class="sr">Added.</span> </th>',
            '<tr class="insert"><th scope="row" class="number old-number" aria-hidden="true"><span class="sr">Added.</span> </th>',
        )
        self.assertIn("row-without-words", self.codes(probe.audit(probe.parse(hidden_cell_page))))
        spoken_cell = "\n".join(probe.transcript(probe.parse(hidden_cell_page)))
        self.assertNotIn("Added", spoken_cell)

        hidden_row_page = CLEAN_PAGE.replace(
            '<tr class="insert">',
            '<tr class="insert" aria-hidden="true">',
        )
        self.assertIn("row-without-words", self.codes(probe.audit(probe.parse(hidden_row_page))))
        spoken_row = "\n".join(probe.transcript(probe.parse(hidden_row_page)))
        self.assertNotIn("Added", spoken_row)

        hidden_tbody_page = CLEAN_PAGE.replace("<tbody>", '<tbody aria-hidden="true">')
        self.assertEqual(
            [finding.code for finding in probe.audit(probe.parse(hidden_tbody_page))],
            ["row-without-words", "row-without-words"],
        )
        spoken_tbody = "\n".join(probe.transcript(probe.parse(hidden_tbody_page)))
        self.assertNotIn("Added", spoken_tbody)
        self.assertNotIn("Unchanged", spoken_tbody)

    def test_findings_are_ordered_and_repeatable(self):
        page = CLEAN_PAGE.replace("<html lang=\"en\">", "<html>")
        first = probe.audit(probe.parse(page))
        second = probe.audit(probe.parse(page))
        self.assertEqual([finding.code for finding in first],
                         [finding.code for finding in second])


STATUS_ELEMENT = '<p id="editor-status" role="status" aria-live="polite">Loading comments…</p>'


def editor_page(script: str = "var ready = true;") -> str:
    """A minimal generated-editor shape whose CSP hash matches its script."""
    digest = base64.b64encode(
        hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-{digest}'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Edit Skein comments</title></head>
<body><a href="#comments">Skip to comments</a><main>
<h1>Edit Skein comments</h1>
<noscript>Use the skein.py comment commands instead.</noscript>
{STATUS_ELEMENT}
<button id="download" type="button">Download edits</button>
<label for="search">Search comments</label><input id="search" type="text">
<section id="comments" tabindex="-1" aria-label="Comment editor"></section>
</main><script type="application/json" id="editor-data">{{}}</script><script>{script}</script>
</body></html>
"""


class ProbeEditorAuditTest(unittest.TestCase):
    """The probe's judgements about a generated offline editor page."""

    def errors(self, page: str) -> list:
        return sorted(finding.code for finding in probe.audit(
            probe.parse(page), editor=True) if finding.severity == "error")

    def test_clean_editor_page_has_no_errors(self):
        self.assertEqual(self.errors(editor_page()), [])

    def test_editor_page_still_errors_as_a_packet(self):
        codes = [finding.code for finding in probe.audit(probe.parse(editor_page()))]
        self.assertIn("script-element", codes)

    def test_real_generated_editor_page_has_no_errors(self):
        page = comment_editor.render_editor(skein.dumps_comments([]).encode("utf-8"))
        self.assertEqual(self.errors(page), [])

    def test_missing_csp_is_reported(self):
        page = editor_page().replace("Content-Security-Policy", "X-Policy")
        self.assertIn("editor-csp", self.errors(page))

    def test_unsafe_inline_script_src_is_reported(self):
        page = editor_page().replace("script-src 'sha256-",
                                      "script-src 'unsafe-inline' 'sha256-")
        self.assertIn("editor-csp", self.errors(page))

    def test_tampered_script_hash_is_reported(self):
        page = editor_page().replace("<script>var", "<script>var extra = 1; var")
        self.assertIn("editor-csp", self.errors(page))

    def test_missing_skip_link_status_and_noscript_are_reported(self):
        self.assertIn("editor-skip-link", self.errors(
            editor_page().replace("Skip to comments", "Comments")))
        self.assertIn("editor-status-region", self.errors(
            editor_page().replace(STATUS_ELEMENT, "")))
        self.assertIn("editor-noscript", self.errors(
            editor_page().replace("<noscript>", "<p hidden>").replace(
                "</noscript>", "</p>")))

    def test_unlabelled_control_is_reported(self):
        page = editor_page().replace(
            "</main>", '<input id="orphan" type="text"></main>')
        self.assertIn("unlabelled-control", self.errors(page))

    def test_wrapping_label_names_a_control(self):
        page = editor_page().replace(
            "</main>", '<label>Filter <input type="text"></label></main>')
        self.assertEqual(self.errors(page), [])

    def test_dynamic_controls_notice_is_always_present(self):
        codes = [finding.code for finding in probe.audit(
            probe.parse(editor_page()), editor=True)]
        self.assertIn("editor-dynamic-controls", codes)

    def test_editor_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "editor.html"
            page.write_text(editor_page(), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(["audit", str(page), "--editor"]), 0)
                self.assertEqual(probe.main(["audit", str(page)]), 1)

    def test_hidden_status_region_is_not_a_live_region(self):
        """A live region a screen reader cannot reach must not pass the check."""
        for replacement in (
            '<div hidden role="status"></div>',
            '<p aria-hidden="true" role="status"></p>',
            '<p role="status" style="display:none"></p>',
            '<p role="status" style="visibility:hidden"></p>',
            '<div hidden><p role="status"></p></div>',
            '<template><p role="status"></p></template>',
        ):
            page = editor_page().replace(STATUS_ELEMENT, replacement)
            self.assertIn("editor-status-region", self.errors(page), replacement)

    def test_script_cannot_stand_in_for_the_live_region(self):
        """A script carrying role=status announces nothing, so it cannot pass."""
        page = editor_page().replace(STATUS_ELEMENT, "").replace(
            "<script>", '<script role="status">')
        self.assertIn("editor-status-region", self.errors(page))


class ProbeTranscriptTest(unittest.TestCase):
    """The reading transcript a reviewer can read without a browser."""

    def test_transcript_reads_in_document_order(self):
        lines = probe.transcript(probe.parse(CLEAN_PAGE))
        self.assertEqual(lines[0], "Document language: en")
        self.assertIn("Title: Skein review packet", lines)
        positions = []
        for needle in ("Heading 1: Skein review packet", "Navigation Changed files:",
                       "Section Modified: src/greet.py:",
                       "Table: Old line and new line; 2 old / 2 new"):
            self.assertIn(needle, lines)
            positions.append(lines.index(needle))
        self.assertEqual(positions, sorted(positions))

    def test_transcript_names_each_row_status(self):
        lines = probe.transcript(probe.parse(CLEAN_PAGE))
        self.assertIn("  Unchanged. 1 | 1 | first | first", lines)
        self.assertIn("  Added. | 2 |  | second", lines)

    def test_transcript_says_when_it_stops_early(self):
        lines = probe.transcript(probe.parse(CLEAN_PAGE), max_rows=1)
        self.assertTrue(any("further row" in line for line in lines), lines)

    def test_transcript_is_repeatable(self):
        first = probe.transcript(probe.parse(CLEAN_PAGE))
        second = probe.transcript(probe.parse(CLEAN_PAGE))
        self.assertEqual(first, second)


class ProbePacketTest(unittest.TestCase):
    """Reading a packet directory from the command line."""

    def write_packet(self, directory: Path, page: str = CLEAN_PAGE) -> None:
        (directory / "review.html").write_text(page, encoding="utf-8")

    def test_manifest_identity_is_reported_as_a_notice(self):
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            self.write_packet(packet)
            (packet / "packet.json").write_text(json.dumps({
                "format": "review-skein-packet", "version": 1,
                "base": {"ref": "main", "commit": "a" * 40},
                "head": {"ref": "topic", "commit": "b" * 40},
            }), encoding="utf-8")
            tree, notes = probe.load_packet(packet)
            self.assertEqual([note.code for note in notes], ["packet-identity"])
            self.assertEqual(notes[0].severity, "notice")
            self.assertIn("a" * 40, notes[0].detail)

    def test_missing_manifest_is_a_notice_not_an_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            self.write_packet(packet)
            tree, notes = probe.load_packet(packet)
            self.assertEqual([note.code for note in notes], ["packet-json-missing"])
            self.assertEqual(notes[0].severity, "notice")

    def test_unreadable_manifest_is_an_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            self.write_packet(packet)
            (packet / "packet.json").write_text("{not json", encoding="utf-8")
            tree, notes = probe.load_packet(packet)
            self.assertEqual([note.code for note in notes], ["packet-json-unreadable"])
            self.assertEqual(notes[0].severity, "error")

    def test_audit_exit_codes(self):
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            self.write_packet(packet)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(probe.main(["audit", str(packet)]), 0)
            self.assertIn("0 error(s)", output.getvalue())
            self.write_packet(packet, CLEAN_PAGE.replace('<html lang="en">', "<html>"))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(["audit", str(packet)]), 1)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(probe.main(["audit", str(packet / "absent")]), 2)

    def test_audit_json_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            self.write_packet(packet)
            (packet / "packet.json").write_text(json.dumps({
                "format": "review-skein-packet", "version": 1,
                "base": {"ref": "main", "commit": "a" * 40},
                "head": {"ref": "topic", "commit": "b" * 40},
            }), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                probe.main(["audit", str(packet), "--json"])
            report = json.loads(output.getvalue())
            self.assertEqual(report["errors"], 0)
            self.assertEqual([finding["code"] for finding in report["findings"]],
                             ["packet-identity"])
            self.assertEqual(report["summary"]["tables"], 1)
            self.assertEqual(report["summary"]["rows"], 3)

    def test_transcript_command_prints_the_reading(self):
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            self.write_packet(packet)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(probe.main(["transcript", str(packet)]), 0)
            self.assertIn("Heading 1: Skein review packet", output.getvalue())

    def test_cli_rejects_broken_row_scope_hidden_status_and_relative_image(self):
        broken_pages = [
            (
                CLEAN_PAGE
                .replace('<span class="sr">Unchanged.</span> ', "")
                .replace('<span class="sr">Added.</span> ', "")
                .replace(' scope="row"', ""),
                "row-without-words",
            ),
            (
                CLEAN_PAGE.replace(
                    '<tr class="insert"><th scope="row" class="number old-number"><span class="sr">Added.</span> </th>',
                    '<tr class="insert"><th scope="row" class="number old-number" aria-hidden="true"><span class="sr">Added.</span> </th>',
                ),
                "row-without-words",
            ),
            (
                CLEAN_PAGE.replace("</body>", '<img src="../outside.png"></body>'),
                "external-reference",
            ),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary)
            for page, expected_code in broken_pages:
                self.write_packet(packet, page)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = probe.main(["audit", str(packet), "--json"])
                self.assertEqual(rc, 1, expected_code)
                report = json.loads(output.getvalue())
                self.assertGreaterEqual(report["errors"], 1)
                self.assertIn(expected_code, [item["code"] for item in report["findings"]])

    def test_real_exported_packet_compatibility_and_byte_invariance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            env = {
                "GIT_AUTHOR_NAME": "Tester",
                "GIT_AUTHOR_EMAIL": "tester@example.invalid",
                "GIT_COMMITTER_NAME": "Tester",
                "GIT_COMMITTER_EMAIL": "tester@example.invalid",
                "PATH": "/usr/bin:/bin:/usr/local/bin",
            }
            subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (repo / "greet.py").write_text("def greet():\n    return 'hi'\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "greet.py"], check=True, env=env)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "base"], check=True, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "-C", str(repo), "checkout", "-b", "topic"], check=True, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (repo / "greet.py").write_text(
                "def greet(name='world'):\n    return f'hello {name}'\n",
                encoding="utf-8",
            )
            (repo / "notes.txt").write_text("added line\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "greet.py", "notes.txt"],
                           check=True, env=env)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "head"], check=True, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            packet = root / "packet"
            skein.export_packet(repo, "main", "topic", packet)
            before = {
                member.name: hashlib.sha256(member.read_bytes()).hexdigest()
                for member in sorted(packet.iterdir())
            }

            audit_out = io.StringIO()
            with contextlib.redirect_stdout(audit_out):
                self.assertEqual(probe.main(["audit", str(packet), "--json"]), 0)
            report = json.loads(audit_out.getvalue())
            self.assertEqual(report["errors"], 0)
            self.assertEqual([item["code"] for item in report["findings"]], ["packet-identity"])

            transcript_out = io.StringIO()
            with contextlib.redirect_stdout(transcript_out):
                self.assertEqual(probe.main(["transcript", str(packet)]), 0)
            reading = transcript_out.getvalue()
            self.assertIn("modified: greet.py", reading)
            self.assertIn("added: → notes.txt", reading)
            self.assertIn("Changed.", reading)
            self.assertIn("Added.", reading)

            after = {
                member.name: hashlib.sha256(member.read_bytes()).hexdigest()
                for member in sorted(packet.iterdir())
            }
            self.assertEqual(before, after)

    def test_standalone_html_file_audit_and_transcript_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            clean_html = root / "standalone.html"
            clean_html.write_text(CLEAN_PAGE, encoding="utf-8")

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(probe.main(["audit", str(clean_html), "--json"]), 0)
            report = json.loads(out.getvalue())
            self.assertEqual(report["errors"], 0)
            self.assertEqual([f["code"] for f in report["findings"]], ["standalone-html"])

            transcript_out = io.StringIO()
            with contextlib.redirect_stdout(transcript_out):
                self.assertEqual(probe.main(["transcript", str(clean_html)]), 0)
            self.assertIn("Heading 1: Skein review packet", transcript_out.getvalue())

            broken_html = root / "broken.html"
            broken_html.write_text(
                CLEAN_PAGE.replace("</body>", "<script>alert(1)</script></body>"),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(["audit", str(broken_html)]), 1)

            symlink_html = root / "link.html"
            symlink_html.symlink_to(clean_html)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(probe.main(["audit", str(symlink_html)]), 2)

            import comments_view
            rendered_comments = root / "comments.html"
            rendered_comments.write_text(
                comments_view.render_comments([], output_format="html"),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(["audit", str(rendered_comments)]), 0)


if __name__ == "__main__":
    unittest.main()
