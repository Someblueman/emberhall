"""Real CLI practice generation, deterministic bytes and offline exchange."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import example
import skein


ROOT = Path(__file__).resolve().parent
MEMBERS = ("packet.json", "anchors.json", "comments.json", "review.html", "changes.bundle")


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.first = cls.root / "first workspace"
        cls.second = cls.root / "second"
        cls.run_tool("example.py", cls.first)
        # Ambient repository/config/identity variables must not leak into fixtures.
        config = cls.root / "global-config"
        config.write_text("[commit]\n gpgSign = true\n[user]\n name = Unrelated Person\n")
        env = dict(os.environ, GIT_DIR=str(cls.root / "absent-repo"),
                   GIT_CONFIG_GLOBAL=str(config), GIT_AUTHOR_NAME="Ambient Author",
                   GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="commit.gpgSign", GIT_CONFIG_VALUE_0="true")
        cls.run_tool("example.py", cls.second, env=env)

    @staticmethod
    def run_tool(script, *args, expected=0, env=None):
        result = subprocess.run([sys.executable, str(ROOT / script), *map(str, args)],
                                capture_output=True, text=True, env=env, timeout=120)
        if result.returncode != expected:
            raise AssertionError(f"{script}: exit {result.returncode}: {result.stderr}")
        return result

    def test_distinct_destinations_and_ambient_config_produce_identical_packets(self):
        self.assertEqual((self.first / "example.json").read_bytes(),
                         (self.second / "example.json").read_bytes())
        manifest = json.loads((self.first / "example.json").read_text())
        for name in example.PACKETS:
            for member in MEMBERS:
                self.assertEqual((self.first / name / member).read_bytes(),
                                 (self.second / name / member).read_bytes(), (name, member))
            base, head = skein.verify_packet(self.first / name)
            self.assertEqual(base, manifest["commits"]["base"])
            expected_head = "revised" if name == "revised-packet" else "feature"
            self.assertEqual(head, manifest["commits"][expected_head])
        author = self.first / "author"
        self.assertEqual(subprocess.check_output(["git", "-C", str(author), "remote"]), b"")
        self.assertEqual(subprocess.check_output(["git", "-C", str(author), "status", "--porcelain"]), b"")

    def test_recipe_exchanges_local_bundle_and_preserves_conflicts_and_orphans(self):
        # Keep both reproducibility fixtures immutable regardless of test order.
        work = self.root / "recipe"
        shutil.copytree(self.first, work)
        clone = self.root / "independent-reviewer"
        subprocess.run(["git", "clone", "--quiet", "--branch", "skein-head",
                        str(work / "common" / "changes.bundle"), str(clone)], check=True,
                       capture_output=True, timeout=120)
        self.assertEqual((clone / "story.txt").read_text(), example.FEATURE)
        target = work / "merge-target"
        fixed = {name: (target / name).read_bytes() for name in MEMBERS if name != "comments.json"}
        before = (target / "comments.json").read_bytes()
        self.run_tool("exchange.py", "merge", target, work / "alice", work / "bob",
                      "--base", work / "common", "--on-divergent", "reject", expected=2)
        self.assertEqual(before, (target / "comments.json").read_bytes())
        self.run_tool("exchange.py", "merge", target, work / "alice", work / "bob",
                      "--base", work / "common")
        for name, value in fixed.items():
            self.assertEqual((target / name).read_bytes(), value)
        self.run_tool("exchange.py", "carry", work / "revised-packet", target)
        comments = skein.loads_comments((work / "revised-packet" / "comments.json").read_text())
        by_id = {item.identifier: item for item in comments}
        self.assertEqual(len(comments), 9)
        self.assertEqual({item.identifier for item in comments if item.state == "orphan"},
                         {"echo", "lantern"})
        self.assertEqual(by_id["door"].resolution, "resolved")
        self.assertEqual(by_id["door"].anchor.line, 1)
        self.assertIsNone(by_id["base-note"].rebased_from)
        greeting = [item for item in comments if item.identifier.startswith("greeting--divergent-")]
        self.assertEqual({item.body for item in greeting}, {"Keep the full greeting.", "Shorten the greeting."})
        self.assertTrue(all(item.anchor.line == 2 and item.state == "anchored" for item in greeting))
        self.assertTrue(all(by_id[name].orphan_reason and by_id[name].rebased_from
                            for name in ("echo", "lantern")))
        self.run_tool("skein.py", "verify", work / "revised-packet")
        self.run_tool("probe.py", "audit", work / "revised-packet")
        self.run_tool("comments_view.py", work / "revised-packet" / "comments.json")
        self.run_tool("exchange.py", "compare", target, work / "revised-packet")
        self.run_tool("exchange.py", "revise", work / "author", "base", "revised",
                      work / "revised-in-one-step", "--from", target)
        for name in MEMBERS:
            self.assertEqual((work / "revised-in-one-step" / name).read_bytes(),
                             (work / "revised-packet" / name).read_bytes())
        self.run_tool("comment_editor.py", "page", work / "revised-packet" / "comments.json",
                      self.root / "editor.html")
        # The walkthrough's annotated view and damage/recovery steps (EXAMPLE.md).
        revised = work / "revised-packet"
        packet_bytes = {name: (revised / name).read_bytes() for name in MEMBERS}
        view = self.run_tool("review_view.py", revised)
        for text in ("Showing 9 of 9 comments", "Orphaned and unplaced comments (2):",
                     "[door | resolved | anchored | new line 1]",
                     "Keep the full greeting.", "Shorten the greeting."):
            self.assertIn(text, view.stdout)
        self.assertEqual({name: (revised / name).read_bytes() for name in MEMBERS}, packet_bytes)
        damaged = work / "damaged-packet"
        shutil.copytree(revised, damaged)
        (damaged / "review.html").unlink()
        damaged_bytes = {name: (damaged / name).read_bytes()
                         for name in MEMBERS if name != "review.html"}
        diagnosis = self.run_tool("recovery.py", "diagnose", damaged, expected=1)
        self.assertIn("status=recoverable", diagnosis.stdout)
        self.assertIn("missing=1", diagnosis.stdout)
        self.assertIn("comments=intact_v2", diagnosis.stdout)
        self.assertFalse((damaged / "review.html").exists())
        self.assertEqual({name: (damaged / name).read_bytes() for name in damaged_bytes},
                         damaged_bytes)
        rebuilt = work / "rebuilt-packet"
        self.run_tool("recovery.py", "rebuild", damaged, rebuilt)
        self.assertEqual((rebuilt / "review.html").read_bytes(), packet_bytes["review.html"])
        self.assertEqual((rebuilt / "comments.json").read_bytes(), packet_bytes["comments.json"])
        self.assertFalse((damaged / "review.html").exists())
        self.run_tool("skein.py", "verify", rebuilt)
        healthy = self.run_tool("recovery.py", "diagnose", rebuilt)
        self.assertIn("status=healthy", healthy.stdout)

    def test_existing_paths_and_symlinks_are_refused_without_mutation(self):
        for name, kind in (("occupied", "directory"), ("file", "file"), ("link", "link")):
            path = self.root / name
            if kind == "directory":
                path.mkdir()
                (path / "keep.txt").write_text("keep")
            elif kind == "file":
                path.write_text("keep")
            else:
                path.symlink_to(self.root / "missing")
            self.run_tool("example.py", path, expected=1)
            if kind == "directory":
                self.assertEqual(list(path.iterdir()), [path / "keep.txt"])
                self.assertEqual((path / "keep.txt").read_text(), "keep")
            elif kind == "file":
                self.assertEqual(path.read_text(), "keep")
            else:
                self.assertTrue(path.is_symlink())
                self.assertFalse(path.exists())

    def test_failed_build_preserves_partial_output_and_marks_no_completion(self):
        output = self.root / "failed"
        with patch.object(example, "TOOLS", self.root / "missing-tools"):
            with self.assertRaisesRegex(example.ExampleError, "failed"):
                example.create_example(output)
        self.assertTrue((output / "author" / ".git").is_dir())
        self.assertFalse((output / "example.json").exists())
        self.run_tool("example.py", output, expected=1)
        self.assertTrue((output / "author" / ".git").is_dir())


if __name__ == "__main__":
    unittest.main()
