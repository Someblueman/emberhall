"""Offline editor data/CSP, strict atomic application and a real-Git CLI lifecycle."""
from __future__ import annotations

import base64
from dataclasses import replace
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import comment_editor
import skein
from test_skein import SkeinFixture


ROOT = Path(__file__).parent


class Page(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.tags = []
        self.scripts = []
        self.current_script = None
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "script":
            self.current_script = {"attrs": attrs, "text": ""}
            self.scripts.append(self.current_script)

    def handle_data(self, value):
        if self.current_script is not None:
            self.current_script["text"] += value

    def handle_endtag(self, tag):
        if tag == "script":
            self.current_script = None


def records():
    anchor = skein.Anchor("a" * 40, "café.py", "new", 1, "line")
    return [skein.Comment("one", anchor, "Question"),
            skein.Comment("two", anchor, "Reply", state="orphan", rebased_from=anchor,
                          orphan_reason="line removed", resolution="resolved")]


class EditorTests(unittest.TestCase):
    def test_embedded_text_is_inert_and_script_csp_is_exact(self):
        comments = records()
        attack = '</script><script src="https://example.invalid">&\u2028\u2029'
        comments[0] = replace(comments[0], body=attack)
        data = skein.dumps_comments(comments).encode()
        html = comment_editor.render_editor(data)
        self.assertEqual(html, comment_editor.render_editor(data))
        page = Page(html)
        self.assertEqual(len(page.scripts), 2)
        self.assertEqual(page.scripts[0]["attrs"], {"type": "application/json", "id": "editor-data"})
        envelope = json.loads(page.scripts[0]["text"])
        self.assertEqual(envelope["document"]["comments"][0]["body"], attack)
        self.assertNotIn("<", page.scripts[0]["text"])
        script = page.scripts[1]["text"]
        self.assertEqual(script, (ROOT / "comment_editor.js").read_text())
        digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        csp = next(attrs["content"] for tag, attrs in page.tags
                   if attrs.get("http-equiv") == "Content-Security-Policy")
        self.assertIn(f"script-src 'sha256-{digest}'", csp)
        self.assertIn("default-src 'none'", csp)
        self.assertIn("form-action 'none'", csp)
        for tag, attrs in page.tags:
            self.assertFalse(any(key.startswith("on") for key in attrs))
            self.assertNotIn("src", attrs)
            if "href" in attrs:
                self.assertTrue(attrs["href"].startswith("#"))
        self.assertNotIn("innerHTML", script)
        self.assertIn(("html", {"lang": "en"}), page.tags)
        self.assertIn("noscript", [tag for tag, attrs in page.tags])

    def test_apply_validates_the_entire_batch_and_preserves_fixed_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            packet, edits = self.packet(Path(directory))
            original = (packet / "comments.json").read_bytes()
            envelope = self.envelope(original)
            envelope["document"]["comments"][0]["body"] = "Revised ☃"
            envelope["document"]["comments"][1]["resolution"] = "open"
            edits.write_text(json.dumps(envelope), encoding="utf-8")
            self.assertEqual(comment_editor.apply_edits(packet, edits), 2)
            result = skein.loads_comments((packet / "comments.json").read_text())
            self.assertEqual(result[0], replace(records()[0], body="Revised ☃"))
            self.assertEqual(result[1], replace(records()[1], resolution="open"))
            self.assertEqual((packet / "packet.json").read_bytes(), self.manifest)
            applied = (packet / "comments.json").read_bytes()
            with self.assertRaisesRegex(skein.SkeinError, "stale"):
                comment_editor.apply_edits(packet, edits)
            self.assertEqual((packet / "comments.json").read_bytes(), applied)

    manifest = json.dumps({"format": skein.FORMAT, "version": 1,
                           "base": {"ref": "base", "commit": "a" * 40},
                           "head": {"ref": "head", "commit": "b" * 40},
                           "bundle": "changes.bundle", "diff": "review.html",
                           "anchors": "anchors.json", "comments": "comments.json", "files": []}).encode()

    def packet(self, directory):
        packet = directory / "packet"
        packet.mkdir()
        (packet / "packet.json").write_bytes(self.manifest)
        (packet / "comments.json").write_text(skein.dumps_comments(records()), encoding="utf-8")
        return packet, directory / "edits.json"

    def envelope(self, original):
        return json.loads(Page(comment_editor.render_editor(original)).scripts[0]["text"])

    def test_malformed_stale_and_identity_changing_downloads_never_write(self):
        with tempfile.TemporaryDirectory() as directory:
            packet, edits = self.packet(Path(directory))
            original = (packet / "comments.json").read_bytes()
            valid = self.envelope(original)
            variants = []
            for key, value in [("version", True), ("version", 2), ("base_sha256", "wrong"), ("extra", 1)]:
                variants.append({**valid, key: value})
            for field, value in [("id", "changed"), ("body", " "), ("body", "\0"),
                                 ("resolution", "closed"), ("state", []), ("state", "orphan"),
                                 ("rebased_from", records()[0].anchor.to_dict()),
                                 ("anchor", {**records()[0].anchor.to_dict(), "line": 9})]:
                variant = json.loads(json.dumps(valid))
                variant["document"]["comments"][1]["body"] = "Must not apply partially"
                variant["document"]["comments"][0][field] = value
                variants.append(variant)
            for order in [[valid["document"]["comments"][0]] * 2,
                          list(reversed(valid["document"]["comments"])), [],
                          valid["document"]["comments"] + [valid["document"]["comments"][0]]]:
                variants.append({**valid, "document": {**valid["document"], "comments": order}})
            serialized = [json.dumps(value).encode() for value in variants]
            serialized += [b"{", b"\xff", b"[]", json.dumps(valid).replace('"version": 1', '"version": 1, "version": 1').encode()]
            for value in serialized:
                with self.subTest(value=value[:100]):
                    edits.write_bytes(value)
                    with self.assertRaises((skein.SkeinError, UnicodeError)):
                        comment_editor.apply_edits(packet, edits)
                    self.assertEqual((packet / "comments.json").read_bytes(), original)
                    self.assertEqual((packet / "packet.json").read_bytes(), self.manifest)
            edits.write_text(json.dumps(valid))
            self.assertEqual(comment_editor.apply_edits(packet, edits), 0)
            self.assertEqual((packet / "comments.json").read_bytes(), original)
            (packet / "comments.json").write_bytes(original + b"\n")
            with self.assertRaisesRegex(skein.SkeinError, "stale"):
                comment_editor.apply_edits(packet, edits)

    def test_file_boundaries_and_atomic_failure_leave_original_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            packet, edits = self.packet(Path(directory))
            original = (packet / "comments.json").read_bytes()
            valid = self.envelope(original)
            valid["document"]["comments"][0]["body"] = "changed"
            edits.write_text(json.dumps(valid))
            with patch.object(skein.os, "replace", side_effect=OSError("disk failure")):
                with self.assertRaises(OSError):
                    comment_editor.apply_edits(packet, edits)
            self.assertEqual((packet / "comments.json").read_bytes(), original)
            self.assertFalse(list(packet.glob(".comments-*")))
            link = Path(directory) / "link.json"
            link.symlink_to(edits)
            with self.assertRaises(skein.SkeinError):
                comment_editor.apply_edits(packet, link)
            with patch.object(skein, "JSON_LIMIT", 1):
                with self.assertRaises(skein.SkeinError):
                    comment_editor.apply_edits(packet, edits)
            self.assertEqual((packet / "comments.json").read_bytes(), original)

    @unittest.skipUnless(shutil.which("node"), "Node needed for editor event/data checks")
    def test_node_editor_events_and_empty_comments(self):
        subprocess.run(["node", str(ROOT / "test_comment_editor_ui.js")], check=True, capture_output=True)


class EditorLifecycleTests(SkeinFixture):
    @unittest.skipUnless(shutil.which("node"), "Node needed for generated-page edit lifecycle")
    def test_real_packet_cli_page_node_download_apply(self):
        self.export()
        anchor = next(a for a in skein._load_anchors(self.packet) if a.side == "new")
        skein.add_comment(self.packet, "reviewer-1", anchor.commit, anchor.path, anchor.side, anchor.line, "Original question")
        members = {p.name: p.read_bytes() for p in self.packet.iterdir()}
        page = self.root / "editor.html"
        cli = [sys.executable, str(ROOT / "comment_editor.py")]
        subprocess.run([*cli, "page", str(self.packet / "comments.json"), str(page)], check=True, capture_output=True)
        second = subprocess.run([*cli, "page", str(self.packet / "comments.json"), str(page)], capture_output=True)
        self.assertEqual(second.returncode, 1)
        envelope = self.root / "envelope.json"
        envelope.write_text(Page(page.read_text()).scripts[0]["text"])
        edits = self.root / "download.json"
        subprocess.run(["node", str(ROOT / "test_comment_editor_ui.js"), str(envelope), str(edits)], check=True, capture_output=True)
        result = subprocess.run([*cli, "apply", str(self.packet), str(edits)], check=True, capture_output=True, text=True)
        self.assertIn("1 comment", result.stdout)
        comment = skein.loads_comments((self.packet / "comments.json").read_text())[0]
        self.assertEqual(comment.body, 'Edited café ☃ <script> & "quoted"')
        self.assertEqual(comment.resolution, "resolved")
        self.assertEqual(comment.anchor, anchor)
        for name, value in members.items():
            if name != "comments.json":
                self.assertEqual((self.packet / name).read_bytes(), value)
        invalid = json.loads(edits.read_text())
        invalid["document"]["comments"][0]["body"] = "Other writer"
        edits.write_text(json.dumps(invalid))
        before = (self.packet / "comments.json").read_bytes()
        rejected = subprocess.run([*cli, "apply", str(self.packet), str(edits)], capture_output=True)
        self.assertEqual(rejected.returncode, 1)
        self.assertEqual((self.packet / "comments.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
