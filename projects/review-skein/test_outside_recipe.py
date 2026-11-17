"""Tests for the outside-user recipe and synchronized Milestone 4 docs."""
from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import comparison
import skein


ROOT = Path(__file__).resolve().parent


def _clean_git_env(home: Path) -> dict[str, str]:
    """Return an isolated Git environment ignoring ambient repository settings."""
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
        env.pop(key, None)
    env.update({
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_AUTHOR_NAME": "Outside Author",
        "GIT_AUTHOR_EMAIL": "author@example.invalid",
        "GIT_COMMITTER_NAME": "Outside Author",
        "GIT_COMMITTER_EMAIL": "author@example.invalid",
    })
    return env


class OutsideRecipeAndDocSyncTests(unittest.TestCase):
    """Verify the outside-user CLI workflow and Milestone 4 doc alignment."""

    def test_recovery_doc_matches_live_comparison_measurements(self) -> None:
        report = comparison.measure_workflows()
        raw = report["measured"]["raw_git_bundle"]
        sk = report["measured"]["skein"]
        text = (ROOT / "RECOVERY.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())

        raw_total = f"{raw['reviewer_exchange_bytes']:,} B"
        skein_total = f"{sk['reviewer_exchange_bytes']:,} B"
        self.assertIn(f"| Two complete reviewer returns (bytes) | {raw_total} | {skein_total} |", text)
        self.assertNotIn("| 3,701 B | 22,773 B |", text)
        self.assertIn(
            f"| Selected tool operations | {raw['cli_commands']} | {sk['cli_commands']} |",
            text,
        )
        self.assertNotIn("CLI commands executed", text)
        self.assertIn("not CLI command counts or human effort", normalized)
        self.assertIn("neither is run or benchmarked", normalized)

        html_bytes = sum(v for k, v in sk["reviewer_artifacts"].items() if k.endswith("/review.html"))
        anchors_bytes = sum(v for k, v in sk["reviewer_artifacts"].items() if k.endswith("/anchors.json"))
        manifests_bytes = sum(v for k, v in sk["reviewer_artifacts"].items() if k.endswith("/packet.json"))
        bundles_bytes = sum(v for k, v in sk["reviewer_artifacts"].items() if k.endswith("/changes.bundle"))
        comments_bytes = sum(v for k, v in sk["reviewer_artifacts"].items() if k.endswith("/comments.json"))

        self.assertIn(f"{bundles_bytes:,} B of bundles", normalized)
        self.assertIn(f"{manifests_bytes:,} B of manifests", normalized)
        self.assertIn(f"{anchors_bytes:,} B of anchors", normalized)
        self.assertIn(f"{html_bytes:,} B of HTML", normalized)
        self.assertIn(f"{comments_bytes:,} B of comments", normalized)

    def test_readme_reconciles_milestone_status_and_outside_recipe(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        self.assertIn("closed in the project record", normalized)
        for ref in ("12546", "12553", "FINAL_REVIEW.md", "MILESTONE_4_TRIAL.md"):
            self.assertIn(ref, normalized)
        self.assertIn("## Outside-user recipe (your own repository)", text)
        for command_hint in (
            "skein.py export",
            "skein.py verify",
            "git clone --branch skein-head",
            "skein.py comment",
            "exchange.py merge",
            "exchange.py revise",
            "recovery.py diagnose",
            "recovery.py rebuild",
        ):
            self.assertIn(command_hint, text)
        self.assertIn("Hashing binds bytes, not people.", normalized)

    def test_outside_user_own_repo_end_to_end_cli_recipe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = _clean_git_env(root / "home")
            (root / "home").mkdir()

            def git(repo: Path, *args: str) -> str:
                proc = subprocess.run(
                    ["git", "-C", str(repo), *args],
                    env=env, capture_output=True, text=True, check=True, timeout=60,
                )
                return proc.stdout.strip()

            repo = root / "my-project"
            repo.mkdir()
            git(repo, "init", "-b", "main")
            (repo / "app.py").write_text("def greet(name):\n    return f'Hello, {name}'\n", encoding="utf-8")
            git(repo, "add", "app.py")
            git(repo, "commit", "-m", "initial")

            git(repo, "checkout", "-b", "feature")
            (repo / "app.py").write_text(
                "# Validate input\ndef greet(name):\n    return f'Hi, {name}!'\n",
                encoding="utf-8",
            )
            git(repo, "add", "app.py")
            git(repo, "commit", "-m", "greet update")
            feature_commit = git(repo, "rev-parse", "HEAD")

            section = (ROOT / "README.md").read_text(encoding="utf-8").split(
                "## Outside-user recipe (your own repository)", 1
            )[1].split("## Honest boundary", 1)[0]
            blocks = re.findall(r"```sh\n(.*?)```", section, re.DOTALL)
            self.assertEqual(len(blocks), 6)
            review = root / "review workspace"

            def step(index: int, expected: int = 0) -> str:
                # Execute the guide itself, substituting only fixture paths and Python.
                script = blocks[index].replace(
                    'repo="/absolute/path/to/your/repository"', "repo=" + shlex.quote(str(repo))
                ).replace(
                    'review="/absolute/path/to/new/review-workspace"', "review=" + shlex.quote(str(review))
                ).replace("python3 ", shlex.quote(sys.executable) + " ")
                # Each block runs in a fresh shell; carry the guide's variables forward.
                proc = subprocess.run(
                    ["sh", "-eu", "-c", script], cwd=ROOT.parent.parent,
                    env=dict(env, repo=str(repo), review=str(review)),
                    capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
                return proc.stdout

            step(0)
            clone = review / "clone"
            self.assertEqual(git(clone, "rev-parse", "HEAD"), feature_commit)
            step(1)
            returned = skein.loads_comments((review / "reviewer/comments.json").read_text())
            self.assertEqual([(c.identifier, c.body, c.anchor.line) for c in returned],
                             [("rev-1", "Should empty names raise ValueError?", 3)])
            step(2)
            self.assertEqual(skein.loads_comments(
                (review / "original/comments.json").read_text()), [])
            self.assertEqual((review / "merged/comments.json").read_bytes(),
                             (review / "reviewer/comments.json").read_bytes())

            (repo / "app.py").write_text(
                "# Greeter module\n# Validate input\ndef greet(name):\n    return f'Hi, {name}!'\n",
                encoding="utf-8",
            )
            git(repo, "add", "app.py")
            git(repo, "commit", "-m", "add header comment")
            view = step(3)
            comments = skein.loads_comments((review / "revised/comments.json").read_text())
            self.assertEqual(len(comments), 1)
            self.assertEqual((comments[0].state, comments[0].anchor.line), ("anchored", 4))
            self.assertIsNotNone(comments[0].rebased_from)
            self.assertIn(returned[0].body, view)
            self.assertIn("status=recoverable", step(4, expected=1))
            before = {p.name: p.read_bytes() for p in (review / "damaged").iterdir()}
            step(5)
            self.assertEqual(before, {p.name: p.read_bytes()
                                     for p in (review / "damaged").iterdir()})
            self.assertEqual((review / "rebuilt/comments.json").read_bytes(),
                             (review / "revised/comments.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
