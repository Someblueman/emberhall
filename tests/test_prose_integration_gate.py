"""The prose-only integration path is admitted from exact committed Git trees."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from house.integrate import PROSE_PATH_LIMIT, check_plan


class ProseIntegrationGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="house-prose-gate-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Integration test")
        self.git("config", "user.email", "integration@local")
        (self.repo / "base.txt").write_text("base\n")
        marker = self.repo / "evidence/keep-moving/owner-objective.md"
        marker.parent.mkdir(parents=True)
        marker.write_text("Owner-supplied policy source.\n", encoding="utf-8")
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

    def test_new_evidence_notes_use_prose_gate(self):
        for path in ("evidence/native-reports/trial.md",
                     "evidence/native-residents/new-report.md",
                     "evidence/rain-ledger-owner/assessment.md"):
            with self.subTest(path=path):
                self.note(path)
                self.commit(path)
                self.assertEqual(self.plan(), ("prose", []))
                self.base = self.git("rev-parse", "HEAD")

    def test_existing_evidence_edits_deletes_and_renames_keep_foundation_gate(self):
        path = "evidence/rain-ledger-owner/assessment.md"
        original = self.note(path)
        self.base = self.commit("original evidence")

        original.write_text("Updated existing evidence.\n", encoding="utf-8")
        self.git("add", path)
        self.commit("edit evidence")
        self.assertEqual(self.plan()[0], "foundation")
        self.base = self.git("rev-parse", "HEAD")

        self.git("rm", path)
        self.commit("delete evidence")
        self.assertEqual(self.plan()[0], "foundation")
        self.base = self.git("rev-parse", "HEAD")

        self.note(path)
        self.commit("restore evidence")
        self.base = self.git("rev-parse", "HEAD")
        renamed = "evidence/rain-ledger-owner/renamed.md"
        self.git("mv", path, renamed)
        self.commit("rename evidence")
        self.assertEqual(self.plan()[0], "foundation")

    def test_new_evidence_names_exclude_ambiguous_and_instruction_paths(self):
        for path in ("evidence/.hidden/assessment.md", "evidence/notes/.hidden.md",
                     "evidence/notes/AGENTS.md",
                     "evidence/notes/skill.md", "evidence/notes/assessment.txt",
                     "evidence/notes/assessment name.md", "evidence/notes/odd\nname.md",
                     "evidence/notes/assessment-\u00e9.md", "evidence/keep-moving/new-note.md"):
            with self.subTest(path=path):
                self.note(path)
                self.commit("unsafe path")
                self.assertEqual(self.plan()[0], "foundation")
                self.base = self.git("rev-parse", "HEAD")

    def test_new_evidence_and_code_keep_foundation_gate(self):
        self.note("evidence/native-reports/trial.md")
        code = self.repo / "house/change.py"
        code.parent.mkdir(parents=True)
        code.write_text("value = 1\n", encoding="utf-8")
        self.git("add", "house/change.py")
        self.commit("mixed evidence and code")
        self.assertEqual(self.plan()[0], "foundation")

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

    def test_new_evidence_rejects_executable_symlink_binary_and_invalid_utf8(self):
        executable = self.note("evidence/native-reports/executable.md")
        executable.chmod(0o755)
        self.git("add", "evidence/native-reports/executable.md")
        self.commit("executable evidence")
        with self.assertRaisesRegex(ValueError, "non-executable regular"):
            self.plan()

        self.base = self.git("rev-parse", "HEAD")
        link = self.repo / "evidence/native-reports/link.md"
        link.symlink_to("../../base.txt")
        self.git("add", "evidence/native-reports/link.md")
        self.commit("symlink evidence")
        with self.assertRaisesRegex(ValueError, "non-executable regular"):
            self.plan()

        self.base = self.git("rev-parse", "HEAD")
        binary = self.repo / "evidence/native-reports/binary.md"
        binary.write_bytes(b"note\x00binary")
        self.git("add", "evidence/native-reports/binary.md")
        self.commit("binary evidence")
        with self.assertRaisesRegex(ValueError, "binary Markdown"):
            self.plan()

        self.base = self.git("rev-parse", "HEAD")
        invalid = self.repo / "evidence/native-reports/invalid.md"
        invalid.write_bytes(b"\xff")
        self.git("add", "evidence/native-reports/invalid.md")
        self.commit("invalid UTF-8 evidence")
        with self.assertRaisesRegex(ValueError, "valid UTF-8"):
            self.plan()

    def test_new_evidence_rejects_gitlinks(self):
        tree = self.git("rev-parse", f"{self.base}^{{tree}}")
        nested_commit = self.git("commit-tree", tree, "-m", "nested repository commit")
        self.git("update-index", "--add", "--cacheinfo",
                 f"160000,{nested_commit},evidence/native-reports/nested.md")
        self.commit("gitlink evidence")
        with self.assertRaisesRegex(ValueError, "non-executable regular"):
            self.plan()

    def test_new_evidence_obeys_existing_file_total_and_path_limits(self):
        self.note("evidence/limits/exact.md", "x" * 64_000)
        self.commit("at file limit")
        self.assertEqual(self.plan(), ("prose", []))

        self.base = self.git("rev-parse", "HEAD")
        too_large = self.note("evidence/limits/too-large.md", "x" * 64_001)
        self.commit("above file limit")
        with self.assertRaisesRegex(ValueError, "bounded UTF-8"):
            self.plan()

        self.base = self.git("rev-parse", "HEAD")
        total_base = self.base
        for index in range(4):
            self.note(f"evidence/total/note-{index}.md", "x" * 64_000)
        self.commit("at total limit")
        self.assertEqual(self.plan(), ("prose", []))

        self.base = total_base
        self.note("evidence/total/note-4.md", "x" * 64_000)
        self.commit("above total limit")
        with self.assertRaisesRegex(ValueError, "content limit"):
            self.plan()

        self.base = self.git("rev-parse", "HEAD")
        for index in range(65):
            self.note(f"evidence/count/note-{index}.md", "x")
        self.commit("above path limit")
        with self.assertRaisesRegex(ValueError, "changed-file limit"):
            self.plan()

    def test_count_preflight_uses_committed_diff_before_path_lookups(self):
        for index in range(PROSE_PATH_LIMIT + 1):
            self.note(f"evidence/count-boundary/note-{index}.md")
        self.commit("oversized additions")
        head = self.git("rev-parse", "HEAD")
        with patch("house.integrate.subprocess.run", wraps=subprocess.run) as run:
            with self.assertRaisesRegex(ValueError, "changed-file limit"):
                check_plan(self.repo, self.base, head)
        commands = [call.args[0] for call in run.call_args_list]
        listings = [command for command in commands if "ls-tree" in command]
        self.assertEqual(len(listings), 1)
        self.assertTrue(all("--name-only" in command for command in listings))
        self.assertTrue(all("cat-file" not in command for command in commands))

    def test_count_boundary_and_category_listing_reuse(self):
        for index in range(PROSE_PATH_LIMIT):
            self.note(f"evidence/count-boundary/note-{index}.md")
        self.commit("exactly at path limit")
        head = self.git("rev-parse", "HEAD")
        with patch("house.integrate.subprocess.run", wraps=subprocess.run) as run:
            self.assertEqual(check_plan(self.repo, self.base, head), ("prose", []))
        listings = [call.args[0] for call in run.call_args_list
                    if "--name-only" in call.args[0] and "ls-tree" in call.args[0]]
        self.assertEqual(len(listings), 1)

    def test_oversized_existing_evidence_edits_keep_foundation_gate(self):
        for index in range(PROSE_PATH_LIMIT + 1):
            self.note(f"evidence/old-notes/note-{index}.md")
        self.base = self.commit("existing notes")
        for index in range(PROSE_PATH_LIMIT + 1):
            self.note(f"evidence/old-notes/note-{index}.md", "Edited.\n")
        self.commit("oversized edits")
        self.assertEqual(self.plan()[0], "foundation")

    def test_protected_additions_at_and_over_limit_keep_foundation_gate(self):
        for count in (PROSE_PATH_LIMIT, PROSE_PATH_LIMIT + 1):
            for index in range(count):
                self.note(f"evidence/keep-moving/protected-{count}-{index}.md")
            self.commit(f"protected additions {count}")
            self.assertEqual(self.plan()[0], "foundation")
            self.base = self.git("rev-parse", "HEAD")

    def test_mixed_protected_and_ordinary_over_limit_keep_foundation_gate(self):
        for index in range(40):
            self.note(f"evidence/keep-moving/mixed-protected-{index}.md")
        for index in range(30):
            self.note(f"evidence/mixed-ordinary/mixed-{index}.md")
        self.commit("mixed protected and ordinary additions")
        self.assertEqual(self.plan()[0], "foundation")

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
