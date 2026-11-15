"""The prose-only integration path is admitted from exact committed Git trees."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from house.integrate import check_plan


class ProseIntegrationGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="house-prose-gate-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Integration test")
        self.git("config", "user.email", "integration@local")
        (self.repo / "base.txt").write_text("base\n")
        self.git("add", ".")
        self.base = self.commit("base")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git("-c", "commit.gpgsign=false", "commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def plan(self):
        return check_plan(self.repo, self.base, self.git("rev-parse", "HEAD"))

    def note(self, path, content="A short recorded note.\n"):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.git("add", path)
        return target

    def test_ballots_selections_and_exploration_notes_use_prose_gate(self):
        for path in ("evidence/choice-010/vote-b.md",
                     "evidence/choice-010/selection.md",
                     "research/explorations/abc123.md"):
            with self.subTest(path=path):
                self.note(path)
                self.commit(path)
                scope, commands = self.plan()
                self.assertEqual((scope, commands), ("prose", []))
                self.base = self.git("rev-parse", "HEAD")

    def test_mixed_prose_and_code_keeps_foundation_gate(self):
        self.note("evidence/choice-010/vote-a.md")
        (self.repo / "house/change.py").parent.mkdir(parents=True)
        (self.repo / "house/change.py").write_text("value = 1\n")
        self.git("add", "house/change.py")
        self.commit("mixed")
        scope, commands = self.plan()
        self.assertEqual(scope, "foundation")
        self.assertIn("discover", commands[0])

    def test_similarly_named_or_protected_paths_keep_foundation_gate(self):
        for path in ("evidence/choice-10/vote-a.md",
                     "evidence/choice-010/README.md",
                     "evidence/choice-010/vote-a.json",
                     "evidence/choice-010/subdir/vote-a.md",
                     "evidence/choice-010/authority.md",
                     "research/exploration/note.md",
                     "research/explorations/note.py"):
            with self.subTest(path=path):
                self.note(path)
                self.commit(path)
                scope, commands = self.plan()
                self.assertEqual(scope, "foundation")
                self.assertIn("discover", commands[0])
                self.base = self.git("rev-parse", "HEAD")

    def test_executable_modes_and_symlinks_are_rejected(self):
        executable = self.note("evidence/choice-010/vote-a.md")
        executable.chmod(0o755)
        self.git("add", "evidence/choice-010/vote-a.md")
        self.commit("executable note")
        with self.assertRaisesRegex(ValueError, "non-executable regular"):
            self.plan()

        self.base = self.git("rev-parse", "HEAD")
        target = self.repo / "research/explorations/link.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to("../../base.txt")
        self.git("add", "research/explorations/link.md")
        self.commit("symlink note")
        with self.assertRaisesRegex(ValueError, "non-executable regular"):
            self.plan()

    def test_mode_change_from_regular_markdown_to_executable_is_rejected(self):
        executable = self.note("evidence/choice-010/vote-a.md")
        self.commit("regular note")
        self.base = self.git("rev-parse", "HEAD")
        executable.chmod(0o755)
        self.git("add", "evidence/choice-010/vote-a.md")
        self.commit("mode change")
        with self.assertRaisesRegex(ValueError, "non-executable regular"):
            self.plan()

    def test_binary_markdown_is_rejected(self):
        bad = self.repo / "research/explorations/note.md"
        bad.parent.mkdir(parents=True)
        bad.write_bytes(b"valid\x00invalid\n")
        self.git("add", "research/explorations/note.md")
        self.commit("binary note")
        with self.assertRaisesRegex(ValueError, "binary Markdown"):
            self.plan()

    def test_invalid_utf8_and_binary_data_are_rejected(self):
        bad = self.repo / "evidence/choice-010/vote-a.md"
        bad.parent.mkdir(parents=True)
        bad.write_bytes(b"\xff")
        self.git("add", str(bad.relative_to(self.repo)))
        self.commit("invalid UTF-8")
        with self.assertRaisesRegex(ValueError, "valid UTF-8"):
            self.plan()

    def test_project_and_other_source_dispatch_are_preserved(self):
        self.note("projects/example/README.md")
        self.commit("project")
        scope, commands = self.plan()
        self.assertEqual(scope, "projects:projects/example")
        self.assertIn("projects/example", commands[0])

        self.base = self.git("rev-parse", "HEAD")
        self.note("docs/ordinary.md")
        self.commit("ordinary documentation")
        scope, commands = self.plan()
        self.assertEqual(scope, "foundation")
        self.assertIn("discover", commands[0])


if __name__ == "__main__":
    unittest.main()
