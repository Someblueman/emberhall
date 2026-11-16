"""Read-only downloaded-edit previews against real exported Git packets."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import comment_editor
import skein
from test_comment_editor import Page
from test_skein import SkeinFixture


class EditPreviewTests(SkeinFixture):
    def setUp(self):
        super().setUp()
        self.export()
        self.anchor = next(a for a in skein._load_anchors(self.packet) if a.side == "new")
        skein.add_comment(self.packet, "question", self.anchor.commit, self.anchor.path,
                          self.anchor.side, self.anchor.line, "Original question")
        self.edits = self.root / "edits.json"
        self.cli = [sys.executable, str(Path(comment_editor.__file__)),
                    "check", str(self.packet), str(self.edits)]

    def envelope(self, compose=False):
        page = (comment_editor.render_composer(self.packet) if compose else
                comment_editor.render_editor((self.packet / "comments.json").read_bytes()))
        return json.loads(next(s["text"] for s in Page(page).scripts
                               if s["attrs"].get("id") == "editor-data"))

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.packet.iterdir()}

    def test_cli_preview_then_apply_matches_each_record_without_writing(self):
        envelope = self.envelope(compose=True)
        old = deepcopy(envelope["document"]["comments"][0])
        updated = envelope["document"]["comments"][0]
        updated.update(body="Revised ☃\n\x1b[31m\u202equestion", resolution="resolved")
        added = skein.Comment("reply", self.anchor, "A second question").to_dict()
        envelope["document"]["comments"].append(added)
        self.edits.write_text(json.dumps(envelope), encoding="utf-8")
        original = self.snapshot()
        result = subprocess.run([*self.cli, "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual((preview["updated"], preview["added"]), (1, 1))
        self.assertEqual(preview["changes"], [
            {"before": old, "after": updated}, {"before": None, "after": added}])
        text = subprocess.run(self.cli, capture_output=True, text=True, check=True).stdout
        self.assertIn("Original question", text)
        self.assertIn("resolved", text)
        self.assertIn("A second question", text)
        self.assertIn("\\u001b[31m\\u202equestion", text)
        self.assertNotIn("\x1b", text)
        self.assertNotIn("\u202e", text)
        self.assertIn(self.anchor.commit, text)
        self.assertEqual(self.snapshot(), original)
        self.assertEqual(comment_editor.apply_edits(self.packet, self.edits), 2)
        after = json.loads((self.packet / "comments.json").read_text())["comments"]
        self.assertEqual(after, [change["after"] for change in preview["changes"]])
        self.assertEqual({k: v for k, v in self.snapshot().items() if k != "comments.json"},
                         {k: v for k, v in original.items() if k != "comments.json"})

    def test_unchanged_and_edit_only_previews_preserve_bytes(self):
        # The baseline binds exact bytes, including noncanonical whitespace.
        comments = self.packet / "comments.json"
        comments.write_bytes(comments.read_bytes() + b"\n")
        envelope = self.envelope()
        self.edits.write_text(json.dumps(envelope))
        original = self.snapshot()
        preview = comment_editor.preview_edits(self.packet, self.edits)
        self.assertEqual(preview["changes"], [])
        self.assertEqual((preview["updated"], preview["added"]), (0, 0))
        envelope["document"]["comments"][0]["resolution"] = "resolved"
        self.edits.write_text(json.dumps(envelope))
        preview = comment_editor.preview_edits(self.packet, self.edits)
        self.assertEqual((preview["updated"], preview["added"]), (1, 0))
        self.assertEqual(self.snapshot(), original)

    @unittest.skipUnless(shutil.which("node"), "Node needed for actual editor download events")
    def test_node_downloads_from_both_editor_modes_check_then_apply(self):
        baseline = self.snapshot()
        for compose in (False, True):
            with self.subTest(compose=compose):
                envelope = self.envelope(compose=compose)
                source = self.root / "envelope.json"
                source.write_text(json.dumps(envelope))
                command = ["node", str(Path(comment_editor.__file__).with_name("test_comment_editor_ui.js")),
                           str(source), str(self.edits)]
                if compose:
                    # The event harness takes the anchor array, not its packet wrapper.
                    anchors = self.root / "node-anchors.json"
                    anchors.write_text(json.dumps([a.to_dict() for a in skein._load_anchors(self.packet)]))
                    command.append(str(anchors))
                subprocess.run(command, check=True, capture_output=True)
                preview = comment_editor.preview_edits(self.packet, self.edits)
                self.assertEqual((preview["updated"], preview["added"]), (0, 2) if compose else (1, 0))
                self.assertEqual(self.snapshot(), baseline)
                comment_editor.apply_edits(self.packet, self.edits)
                applied = {c.identifier: c.to_dict() for c in
                           skein.loads_comments((self.packet / "comments.json").read_text())}
                for change in preview["changes"]:
                    self.assertEqual(applied[change["after"]["id"]], change["after"])
                (self.packet / "comments.json").write_bytes(baseline["comments.json"])

    def test_check_and_apply_reject_the_same_invalid_downloads_without_writes(self):
        valid = self.envelope(compose=True)
        variants = []
        for field, value in [("base_sha256", "stale"), ("packet_sha256", "stale"),
                             ("anchors_sha256", "stale"), ("version", True)]:
            variant = deepcopy(valid)
            variant[field] = value
            variants.append(json.dumps(variant))
        for field, value in [("id", "replacement"), ("body", " "),
                             ("resolution", "closed"),
                             ("anchor", {**self.anchor.to_dict(), "line": 999})]:
            variant = deepcopy(valid)
            variant["document"]["comments"][0][field] = value
            variants.append(json.dumps(variant))
        for comments in [[], valid["document"]["comments"] * 2,
                         [*valid["document"]["comments"],
                          skein.Comment("new", skein.Anchor(self.anchor.commit,
                              self.anchor.path, self.anchor.side, 999, "wrong"), "x").to_dict()]]:
            variant = deepcopy(valid)
            variant["document"]["comments"] = comments
            variants.append(json.dumps(variant))
        variants.extend(["{", '{"version":1,"version":2}', "[]"])
        original = self.snapshot()
        for serialized in variants:
            with self.subTest(serialized=serialized[:100]):
                self.edits.write_text(serialized)
                result = subprocess.run(self.cli, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                with self.assertRaises(skein.SkeinError):
                    comment_editor.apply_edits(self.packet, self.edits)
                self.assertEqual(self.snapshot(), original)
        self.edits.write_text(json.dumps(valid))
        link = self.root / "linked-edits.json"
        link.symlink_to(self.edits)
        with self.assertRaises(skein.SkeinError):
            comment_editor.preview_edits(self.packet, link)


if __name__ == "__main__":
    unittest.main()
