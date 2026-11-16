"""Tests for the acceptance preflight report.

The unit tests feed the parser and the analysis fixed diffs, so they check the
tool's own judgements rather than Git's output. The end-to-end tests build a
real temporary Git repository and run the command over it, because the tool is
meant to be run inside a checkout.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import preflight

SCRIPT = Path(preflight.__file__).resolve()

DIFF = """diff --git a/src/alpha.py b/src/alpha.py
index 1111111..2222222 100644
--- a/src/alpha.py
+++ b/src/alpha.py
@@ -1,3 +1,4 @@
 import beta
+# a comment
-def old():
+def new():
     pass
diff --git a/src/beta.py b/src/beta.py
index 3333333..4444444 100644
--- a/src/beta.py
+++ b/src/beta.py
@@ -1,2 +1,2 @@
-ALPHA = 1
+ALPHA = 2
diff --git a/docs/guide.md b/docs/guide.md
new file mode 100644
index 0000000..5555555
--- /dev/null
+++ b/docs/guide.md
@@ -0,0 +1,2 @@
+# Guide
+some prose
"""

RENAME_DIFF = """diff --git a/src/old.py b/src/new.py
similarity index 100%
rename from src/old.py
rename to src/new.py
"""

DELETED_DIFF = """diff --git a/src/gone.py b/src/gone.py
deleted file mode 100644
index 6666666..0000000
--- a/src/gone.py
+++ /dev/null
@@ -1,2 +0,0 @@
-first
-second
"""


def git_environment(root: Path) -> dict:
    """A Git environment that reads no user configuration."""
    env = dict(os.environ)
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
        env.pop(name, None)
    env.update({
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(root),
        "GIT_AUTHOR_NAME": "Preflight Test",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "Preflight Test",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+0000",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+0000",
    })
    return env


def git(root: Path, env: dict, *args) -> str:
    """Run one Git command in a temporary checkout."""
    result = subprocess.run(["git", "-C", str(root), *args], env=env,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def write(path: Path, text: str) -> None:
    """Write a file, creating its directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ParseTest(unittest.TestCase):
    """The diff parser."""

    def test_counts_and_paths(self):
        changes = preflight.parse_diff(DIFF)
        self.assertEqual([change.path for change in changes],
                         ["src/alpha.py", "src/beta.py", "docs/guide.md"])

    def test_added_and_removed_lines(self):
        alpha, beta, guide = preflight.parse_diff(DIFF)
        self.assertEqual((alpha.added, alpha.removed), (2, 1))
        self.assertEqual((beta.added, beta.removed), (1, 1))
        self.assertEqual((guide.added, guide.removed), (2, 0))

    def test_statuses(self):
        alpha, beta, guide = preflight.parse_diff(DIFF)
        self.assertEqual(alpha.status, "modified")
        self.assertEqual(beta.status, "modified")
        self.assertEqual(guide.status, "added")
        self.assertIsNone(guide.old_path)

    def test_null_old_header_without_mode_and_added_binary(self):
        text = ("diff --git a/new.txt b/new.txt\n"
                "--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+new\n")
        binary = ("diff --git a/new.png b/new.png\nnew file mode 100644\n"
                  "Binary files /dev/null and b/new.png differ\n")
        for diff in (text, binary):
            change = preflight.parse_diff(diff)[0]
            self.assertEqual(change.status, "added")
            self.assertIsNone(change.old_path)

    def test_deleted_file_keeps_its_path(self):
        change = preflight.parse_diff(DELETED_DIFF)[0]
        self.assertEqual(change.path, "src/gone.py")
        self.assertEqual(change.status, "deleted")
        self.assertEqual(change.removed, 2)

    def test_rename_without_content_is_a_move(self):
        change = preflight.parse_diff(RENAME_DIFF)[0]
        self.assertEqual((change.path, change.status), ("src/new.py", "renamed"))
        self.assertEqual(change.old_path, "src/old.py")
        self.assertFalse(change.content_changed)

    def test_a_removed_line_that_looks_like_a_header_is_still_content(self):
        diff = ("diff --git a/notes.md b/notes.md\n"
                "--- a/notes.md\n"
                "+++ b/notes.md\n"
                "@@ -1,2 +1,2 @@\n"
                "-- old heading\n"
                "+new heading\n")
        change = preflight.parse_diff(diff)[0]
        self.assertEqual(change.path, "notes.md")
        self.assertEqual((change.added, change.removed), (1, 1))
        self.assertEqual(change.removed_lines, ["- old heading"])

    def test_binary_change_is_marked(self):
        diff = ("diff --git a/logo.png b/logo.png\n"
                "index 1111111..2222222 100644\n"
                "Binary files a/logo.png and b/logo.png differ\n")
        change = preflight.parse_diff(diff)[0]
        self.assertTrue(change.binary)


class NamingTest(unittest.TestCase):
    """Test-file conventions."""

    def test_test_paths(self):
        for path in ("tests/test_alpha.py", "src/test_alpha.py", "alpha_test.py",
                     "src/alpha.test.js", "spec/alpha.rb", "src/__tests__/alpha.js"):
            self.assertTrue(preflight.is_test_path(path), path)

    def test_other_paths_are_not_tests(self):
        for path in ("src/alpha.py", "docs/guide.md", "src/latest.py", "src/contest.py"):
            self.assertFalse(preflight.is_test_path(path), path)

    def test_test_stem(self):
        self.assertEqual(preflight.test_stem("tests/test_alpha.py"), "alpha")
        self.assertEqual(preflight.test_stem("src/alpha_test.py"), "alpha")
        self.assertIsNone(preflight.test_stem("src/alpha.py"))


class AnalyseTest(unittest.TestCase):
    """The judgements the report draws."""

    def report(self, diff=DIFF, sizes=None, base_paths=None, limit=400):
        changes = preflight.parse_diff(diff)
        sizes = sizes if sizes is not None else {
            "src/alpha.py": (10, 100), "src/beta.py": (5, 50)}
        base_paths = base_paths if base_paths is not None else {
            "src/alpha.py", "src/beta.py", "src/gamma.py", "docs/guide.md"}
        return preflight.analyse(changes, sizes, base_paths, limit)

    def test_totals(self):
        report = self.report()
        self.assertEqual(report["totals"]["files"], 3)
        self.assertEqual(report["totals"]["changed_lines"], 7)
        self.assertEqual(report["totals"]["added"], 5)
        self.assertEqual(report["totals"]["removed"], 2)

    def test_a_change_touching_most_of_a_file_needs_the_whole_file(self):
        report = self.report()
        beta = [entry for entry in report["files"] if entry["path"] == "src/beta.py"][0]
        self.assertTrue(beta["whole_file"])
        alpha = [entry for entry in report["files"] if entry["path"] == "src/alpha.py"][0]
        self.assertFalse(alpha["whole_file"])

    def test_a_new_file_is_a_whole_file_read(self):
        report = self.report()
        guide = [entry for entry in report["files"] if entry["path"] == "docs/guide.md"][0]
        self.assertTrue(guide["whole_file"])
        self.assertEqual(guide["file_lines"], 2)

    def test_a_long_file_is_over_the_reader_limit(self):
        report = self.report(limit=4)
        alpha = [entry for entry in report["files"] if entry["path"] == "src/alpha.py"][0]
        self.assertTrue(alpha["over_reader_limit"])

    def test_files_nothing_links_are_separate_clusters(self):
        report = self.report()
        groups = [group["files"] for group in report["clusters"]]
        self.assertIn(["src/alpha.py", "src/beta.py"], groups)
        self.assertIn(["docs/guide.md"], groups)
        self.assertEqual(report["totals"]["clusters"], 2)

    def test_a_mention_links_two_files(self):
        report = self.report()
        alpha = [entry for entry in report["files"] if entry["path"] == "src/alpha.py"][0]
        self.assertEqual(alpha["mentions"], ["src/beta.py"])

    def test_content_in_the_tree_the_reviewer_cannot_see(self):
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-from gamma import thing\n"
                "+from gamma import other\n")
        report = self.report(diff=diff, sizes={"src/alpha.py": (4, 40)})
        alpha = [entry for entry in report["files"] if entry["path"] == "src/alpha.py"][0]
        self.assertEqual(alpha["invisible"], ["src/gamma.py"])

    def test_production_code_changed_without_a_test(self):
        report = self.report()
        self.assertEqual(report["flags"]["production_files_without_tests"],
                         ["src/alpha.py", "src/beta.py"])
        self.assertNotIn("docs/guide.md",
                         report["flags"]["production_files_without_tests"])

    def test_a_changed_test_covers_its_production_file(self):
        diff = DIFF + ("diff --git a/tests/test_alpha.py b/tests/test_alpha.py\n"
                       "--- a/tests/test_alpha.py\n"
                       "+++ b/tests/test_alpha.py\n"
                       "@@ -1,1 +1,1 @@\n"
                       "-def test_alpha():\n"
                       "+def test_alpha():\n")
        report = self.report(diff=diff)
        self.assertNotIn("src/alpha.py", report["flags"]["production_files_without_tests"])
        self.assertEqual(report["flags"]["changed_test_files"], ["tests/test_alpha.py"])

    def test_a_differently_named_test_that_names_the_file_counts(self):
        diff = DIFF + ("diff --git a/tests/test_other.py b/tests/test_other.py\n"
                       "--- a/tests/test_other.py\n"
                       "+++ b/tests/test_other.py\n"
                       "@@ -1,1 +1,2 @@\n"
                       " import unittest\n"
                       "+import alpha\n")
        report = self.report(diff=diff)
        self.assertNotIn("src/alpha.py", report["flags"]["production_files_without_tests"])
        self.assertIn("src/beta.py", report["flags"]["production_files_without_tests"])
        self.assertEqual(report["flags"]["changed_test_files"], ["tests/test_other.py"])

    def test_each_invisible_path_is_one_action_however_often_named(self):
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-from gamma import thing\n"
                "+from gamma import other\n"
                "diff --git a/src/beta.py b/src/beta.py\n"
                "--- a/src/beta.py\n"
                "+++ b/src/beta.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-from gamma import thing\n"
                "+from gamma import another\n")
        report = self.report(diff=diff)
        invisible_actions = [action["detail"] for action in report["actions"]
                             if action["kind"] == "invisible"]
        self.assertEqual(len(invisible_actions), 1)
        self.assertIn("src/gamma.py", invisible_actions[0])
        for entry in report["files"]:
            self.assertEqual(entry["invisible"], ["src/gamma.py"])

    def test_a_whole_file_test_mention_keeps_test_with_its_code(self):
        # A changed test file is read whole: a mention far from the changed
        # lines still links the test to the code it exercises.
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-x = 1\n"
                "+x = 2\n"
                "diff --git a/tests/test_alpha.py b/tests/test_alpha.py\n"
                "--- a/tests/test_alpha.py\n"
                "+++ b/tests/test_alpha.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-def test_alpha():\n"
                "+def test_alpha():\n")
        changes = preflight.parse_diff(diff)
        whole_texts = {"tests/test_alpha.py": ["import src.alpha", "def test_alpha():", "    pass"]}
        report = preflight.analyse(changes, {"src/alpha.py": (10, 100), "tests/test_alpha.py": (5, 50)},
                                   {"src/alpha.py", "tests/test_alpha.py"}, 400, None, whole_texts)
        groups = [group["files"] for group in report["clusters"]]
        # test and alpha in one group
        self.assertTrue(any(set(group) == {"src/alpha.py", "tests/test_alpha.py"} for group in groups))
        alpha = [e for e in report["files"] if e["path"] == "tests/test_alpha.py"][0]
        self.assertIn("src/alpha.py", alpha["mentions"])
        self.assertIn("src/alpha.py", alpha["whole_file_mentions"])

    def test_a_production_file_is_not_read_whole(self):
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-x = 1\n"
                "+x = 2\n"
                "diff --git a/src/beta.py b/src/beta.py\n"
                "--- a/src/beta.py\n"
                "+++ b/src/beta.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-y = 1\n"
                "+y = 2\n")
        changes = preflight.parse_diff(diff)
        # Even if the whole production file mentions beta, it must not link.
        whole_texts = {"src/alpha.py": ["import beta", "x = 2"]}
        report = preflight.analyse(changes, {"src/alpha.py": (10, 100), "src/beta.py": (10, 100)},
                                   {"src/alpha.py", "src/beta.py"}, 400, None, whole_texts)
        alpha = [e for e in report["files"] if e["path"] == "src/alpha.py"][0]
        self.assertEqual(alpha["mentions"], [])
        self.assertEqual(alpha["whole_file_mentions"], [])
        groups = [group["files"] for group in report["clusters"]]
        self.assertIn(["src/alpha.py"], groups)
        self.assertIn(["src/beta.py"], groups)

    def test_an_ambiguous_mention_links_neither_file(self):
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,2 @@\n"
                " x = 1\n"
                "+ open('summary.json')\n"
                "diff --git a/docs/summary.json b/docs/summary.json\n"
                "--- a/docs/summary.json\n"
                "+++ b/docs/summary.json\n"
                "@@ -1,1 +1,1 @@\n"
                "-{ \"a\": 1 }\n"
                "+{ \"a\": 2 }\n"
                "diff --git a/site/summary.json b/site/summary.json\n"
                "new file mode 100644\n"
                "--- /dev/null\n"
                "+++ b/site/summary.json\n"
                "@@ -0,0 +1 @@\n"
                "+{}\n")
        changes = preflight.parse_diff(diff)
        base_paths = {"src/alpha.py", "docs/summary.json"}  # site/summary.json is new
        report = preflight.analyse(changes, {"src/alpha.py": (5, 50), "docs/summary.json": (1, 10)},
                                   base_paths, 400)
        alpha = [e for e in report["files"] if e["path"] == "src/alpha.py"][0]
        self.assertEqual(alpha["mentions"], [])
        self.assertEqual(alpha["invisible"], [])

    def test_a_name_shared_by_two_files_is_not_reported_as_unseen(self):
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,2 @@\n"
                " x = 1\n"
                "+ open('summary.json')\n"
                "diff --git a/docs/summary.json b/docs/summary.json\n"
                "--- a/docs/summary.json\n"
                "+++ b/docs/summary.json\n"
                "@@ -1,1 +1,1 @@\n"
                "-{ \"a\": 1 }\n"
                "+{ \"a\": 2 }\n"
                "diff --git a/site/summary.json b/site/summary.json\n"
                "new file mode 100644\n"
                "--- /dev/null\n"
                "+++ b/site/summary.json\n"
                "@@ -0,0 +1 @@\n"
                "+{}\n")
        changes = preflight.parse_diff(diff)
        base_paths = {"src/alpha.py", "docs/summary.json"}
        report = preflight.analyse(changes, {"src/alpha.py": (5, 50), "docs/summary.json": (1, 10)},
                                   base_paths, 400)
        # docs/summary.json is in the change, so it must not appear as unseen.
        for entry in report["files"]:
            self.assertNotIn("docs/summary.json", entry["invisible"])
        invisible_actions = [a["detail"] for a in report["actions"] if a["kind"] == "invisible"]
        for detail in invisible_actions:
            self.assertNotIn("docs/summary.json", detail)
            self.assertNotIn("site/summary.json", detail)

    def test_the_text_report_does_not_claim_nothing_links(self):
        diff = ("diff --git a/src/alpha.py b/src/alpha.py\n"
                "--- a/src/alpha.py\n"
                "+++ b/src/alpha.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-x = 1\n"
                "+x = 2\n"
                "diff --git a/src/beta.py b/src/beta.py\n"
                "--- a/src/beta.py\n"
                "+++ b/src/beta.py\n"
                "@@ -1,1 +1,1 @@\n"
                "-y = 1\n"
                "+y = 2\n")
        changes = preflight.parse_diff(diff)
        report = preflight.analyse(changes, {"src/alpha.py": (5, 50), "src/beta.py": (5, 50)},
                                   {"src/alpha.py", "src/beta.py"}, 400)
        # render_text needs the envelope build_report adds.
        report["range"] = "test"
        report["mode"] = "range"
        report["base"] = "HEAD"
        text = preflight.render_text(report)
        self.assertNotIn("nothing links", text)
        self.assertIn("no link was found", text)
        self.assertIn("separate groups", text)

    def test_documentation_only_edits_are_flagged_when_mixed(self):
        report = self.report()
        self.assertFalse(report["flags"]["mixed_documentation_and_code"])

    def test_documentation_only_file_alone_is_not_a_mix(self):
        diff = ("diff --git a/docs/guide.md b/docs/guide.md\n"
                "--- a/docs/guide.md\n"
                "+++ b/docs/guide.md\n"
                "@@ -1,1 +1,1 @@\n"
                "-# old heading\n"
                "+# new heading\n")
        report = self.report(diff=diff, sizes={})
        self.assertEqual(report["flags"]["documentation_only_files"], ["docs/guide.md"])
        self.assertFalse(report["flags"]["mixed_documentation_and_code"])

    def test_the_report_never_claims_to_predict_review_duration(self):
        report = self.report()
        self.assertIn("does not predict how long a review takes", report["limits"][0])

    def test_the_same_inputs_give_the_same_report(self):
        first = self.report()
        second = self.report()
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))


class CommandTest(unittest.TestCase):
    """The command, run over a real temporary Git checkout."""

    def setUp(self):
        if not shutil.which("git"):
            self.skipTest("git is not installed")
        self.root = Path(tempfile.mkdtemp(prefix="preflight-test-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.env = git_environment(self.root)
        git(self.root, self.env, "init", "--quiet")
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 1\n" * 20)
        write(self.root / "src" / "beta.py", "ALPHA = 1\n")
        write(self.root / "tests" / "test_alpha.py", "def test_alpha():\n    pass\n")
        git(self.root, self.env, "add", "-A")
        git(self.root, self.env, "commit", "--quiet", "-m", "first")

    def run_preflight(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                              env=self.env, capture_output=True, text=True)

    def test_it_reports_uncommitted_work(self):
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 2\n" * 20)
        write(self.root / "scratch.txt", "not tracked\n")
        result = self.run_preflight("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["totals"]["files"], 1)
        self.assertEqual(report["files"][0]["path"], "src/alpha.py")
        self.assertIn("scratch.txt", report["flags"]["untracked_files"])

    def test_it_reports_a_committed_range(self):
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 2\n" * 20)
        git(self.root, self.env, "add", "-A")
        git(self.root, self.env, "commit", "--quiet", "-m", "second")
        result = self.run_preflight("HEAD~1..HEAD", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["mode"], "range")
        self.assertEqual(report["totals"]["files"], 1)
        self.assertEqual(report["totals"]["changed_lines"], 40)

    def test_committed_range_reports_unstaged_edits_when_also_staged(self):
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 2\n" * 20)
        git(self.root, self.env, "add", "src/alpha.py")
        git(self.root, self.env, "commit", "--quiet", "-m", "second")
        # Stage one edit and make another unstaged edit on the same path (porcelain MM),
        # plus an added+modified file (AM), a renamed+modified file (RM), and a staged-only file (M ).
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 3\n" * 20)
        git(self.root, self.env, "add", "src/alpha.py")
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 4\n" * 20)
        write(self.root / "src" / "gamma.py", "y = 1\n")
        git(self.root, self.env, "add", "src/gamma.py")
        write(self.root / "src" / "gamma.py", "y = 2\n")
        git(self.root, self.env, "mv", "src/beta.py", "src/beta_moved.py")
        write(self.root / "src" / "beta_moved.py", "ALPHA = 9\n")
        write(self.root / "tests" / "test_alpha.py", "def test_alpha():\n    assert True\n")
        git(self.root, self.env, "add", "tests/test_alpha.py")

        result = self.run_preflight("HEAD~1..HEAD", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["flags"]["unstaged_files"],
                         ["src/alpha.py", "src/beta_moved.py", "src/gamma.py"])
        unstaged_actions = [a["detail"] for a in report["actions"] if a["kind"] == "unstaged"]
        self.assertEqual(len(unstaged_actions), 3)
        self.assertTrue(any("src/alpha.py" in detail for detail in unstaged_actions))

        # Worktree mode compares HEAD against the working tree, so those edits are in the diff.
        worktree_result = self.run_preflight("--json")
        self.assertEqual(worktree_result.returncode, 0, worktree_result.stderr)
        worktree_report = json.loads(worktree_result.stdout)
        self.assertEqual(worktree_report["flags"]["unstaged_files"], [])

    def test_the_same_tree_gives_the_same_numbers_twice(self):
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 2\n" * 20)
        first = self.run_preflight("--json")
        second = self.run_preflight("--json")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def test_a_changed_test_read_whole_links_far_mention_in_one_group(self):
        # The test file changes only a distant line, but its whole content
        # names the production file, so the two end up in one group.
        write(self.root / "src" / "alpha.py", "def f():\n    return 1\n")
        test_path = self.root / "tests" / "test_behaviour.py"
        body = ("# spacer\n" * 20 +
                "import src.alpha\ndef test_result():\n    assert src.alpha.f() == 1\n")
        write(test_path, "# hello\n" + body)
        git(self.root, self.env, "add", "-A")
        git(self.root, self.env, "commit", "--quiet", "-m", "base")
        # Change only the first line of the test, far from the import.
        write(test_path, "# hello2\n" + body)
        write(self.root / "src" / "alpha.py", "def f():\n    return 2\n")
        git(self.root, self.env, "add", "-A")
        git(self.root, self.env, "commit", "--quiet", "-m", "change")
        diff = git(self.root, self.env, "diff", "--unified=3", "HEAD~1..HEAD")
        self.assertNotIn("import src.alpha", diff)
        result = self.run_preflight("HEAD~1..HEAD", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        groups = [set(g["files"]) for g in report["clusters"]]
        # Both changed files in one group thanks to whole-file read.
        self.assertIn({"src/alpha.py", "tests/test_behaviour.py"}, groups)
        self.assertNotIn("src/alpha.py", report["flags"]["production_files_without_tests"])
        test_entry = [e for e in report["files"] if e["path"] == "tests/test_behaviour.py"][0]
        self.assertIn("src/alpha.py", test_entry["mentions"])
        self.assertIn("src/alpha.py", test_entry["whole_file_mentions"])

    def test_path_mentions_resolve_across_changed_and_base_paths(self):
        cases = [
            ("added", "summary.json", None),
            ("modified", "summary.json", None),
            ("unchanged", "summary.json", None),
            ("deleted", "summary.json", None),
            ("unchanged", "docs/summary.json", "docs/summary.json"),
            ("unchanged", "site/summary.json", "site/summary.json"),
        ]
        for state, mention, target in cases:
            with self.subTest(state=state, mention=mention):
                write(self.root / "src/alpha.py", "x = 1\n")
                write(self.root / "docs/summary.json", '{"v": 1}\n')
                other = self.root / "site/summary.json"
                if state == "added":
                    other.unlink(missing_ok=True)
                else:
                    write(other, '{}\n')
                git(self.root, self.env, "add", "-A")
                git(self.root, self.env, "commit", "--quiet", "--allow-empty", "-m", "base")

                write(self.root / "src/alpha.py", f"x = 1\nopen({mention!r})\n")
                write(self.root / "docs/summary.json", '{"v": 2}\n')
                if state in {"added", "modified"}:
                    write(other, '{"new": 1}\n')
                elif state == "deleted":
                    other.unlink()
                git(self.root, self.env, "add", "-A")
                git(self.root, self.env, "commit", "--quiet", "-m", "change")

                first = self.run_preflight("HEAD~1..HEAD", "--json")
                second = self.run_preflight("HEAD~1..HEAD", "--json")
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(first.stdout, second.stdout)
                report = json.loads(first.stdout)
                alpha = next(e for e in report["files"] if e["path"] == "src/alpha.py")
                changed_target = target == "docs/summary.json"
                self.assertEqual(alpha["mentions"], [target] if changed_target else [])
                self.assertEqual(alpha["invisible"], [target] if target and not changed_target else [])
                if target is None:
                    self.assertIn(["src/alpha.py"], [g["files"] for g in report["clusters"]])
                    self.assertFalse(any(e["invisible"] for e in report["files"]))
                    self.assertFalse(any(a["kind"] == "invisible" for a in report["actions"]))

    def test_the_text_report_names_the_files(self):
        write(self.root / "src" / "alpha.py", "import beta\n" + "x = 2\n" * 20)
        result = self.run_preflight()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("src/alpha.py", result.stdout)
        self.assertIn("Reading load", result.stdout)
        self.assertIn("does not predict how long a review takes", result.stdout)

    def test_a_staged_new_file_is_part_of_the_change(self):
        write(self.root / "src" / "gamma.py", "y = 3\n")
        git(self.root, self.env, "add", "src/gamma.py")
        result = self.run_preflight("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        paths = [entry["path"] for entry in report["files"]]
        self.assertIn("src/gamma.py", paths)

    def test_outside_a_checkout_it_fails_with_a_message(self):
        outside = Path(tempfile.mkdtemp(prefix="preflight-outside-"))
        self.addCleanup(shutil.rmtree, outside, True)
        env = git_environment(outside)
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=outside, env=env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("preflight:", result.stderr)


if __name__ == "__main__":
    unittest.main()
