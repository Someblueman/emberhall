#!/usr/bin/env python3
"""Create a small, reproducible Skein practice workspace from invented text."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


TOOLS = Path(__file__).resolve().parent
PACKETS = ("common", "alice", "bob", "merge-target", "revised-packet")
BASE = "Welcome.\nThe door is blue.\nA lantern marks the path.\necho\necho\nGood night.\n"
FEATURE = BASE.replace("Welcome.", "Welcome, traveller.").replace("blue", "green")
REVISED = (
    "The door is green.\nWelcome, traveller.\nA lantern marks the safe path.\n"
    "signpost\necho\necho\nGood night.\n"
)


class ExampleError(ValueError):
    """The practice workspace could not be completed."""


def _environment() -> dict[str, str]:
    # Do not inherit a surrounding repo, user identity, signing, templates, hooks,
    # global attributes or config-injected filters into these invented fixtures.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_ATTR_NOSYSTEM": "1", "GIT_DEFAULT_HASH": "sha1",
        "GIT_AUTHOR_NAME": "Skein Example", "GIT_AUTHOR_EMAIL": "example@example.invalid",
        "GIT_COMMITTER_NAME": "Skein Example", "GIT_COMMITTER_EMAIL": "example@example.invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000", "LC_ALL": "C",
        "GIT_CONFIG_COUNT": "4",
        "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": os.devnull,
        "GIT_CONFIG_KEY_1": "commit.gpgSign", "GIT_CONFIG_VALUE_1": "false",
        "GIT_CONFIG_KEY_2": "core.autocrlf", "GIT_CONFIG_VALUE_2": "false",
        "GIT_CONFIG_KEY_3": "core.attributesFile", "GIT_CONFIG_VALUE_3": os.devnull,
    })
    return env


def _run(cwd: Path, env: dict[str, str], *command: str) -> str:
    try:
        result = subprocess.run(
            command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=120, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ExampleError(f"cannot run {command[0]}: {exc}") from exc
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()[:2000]
        raise ExampleError(f"{command[0]} failed ({result.returncode}): {detail}")
    return result.stdout.decode("utf-8").strip()


def create_example(output: Path) -> dict[str, object]:
    """Reserve a new directory; write example.json last as the completion marker.

    Failures preserve the partial new workspace for inspection. Existing paths
    are never reused, and no repository supplied by the caller is opened.
    """
    output = output.expanduser()
    if output.exists() or output.is_symlink():
        raise ExampleError("output must be a new path; refusing to overwrite anything")
    if not output.parent.is_dir():
        raise ExampleError("output parent must already be a directory")
    output = output.parent.resolve() / output.name
    try:
        output.mkdir()
    except FileExistsError as exc:
        raise ExampleError("output must be a new path; refusing to overwrite anything") from exc

    env = _environment()
    author = output / "author"
    author.mkdir()

    def git(*args: str) -> str:
        return _run(author, env, "git", *args)

    def tool(script: str, *args: str) -> str:
        return _run(output, env, sys.executable, str(TOOLS / script), *args)

    def commit(message: str, minute: int) -> str:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"2000-01-01T00:{minute:02}:00+0000"
        git("add", "--all")
        git("commit", "--quiet", "-m", message)
        return git("rev-parse", "HEAD")

    git("init", "--quiet", "--initial-branch=base", "--object-format=sha1", "--template=")
    (author / "story.txt").write_text(BASE, encoding="utf-8")
    (author / "notes.txt").write_text("A small invented review.\n", encoding="utf-8")
    base = commit("Invented starting text", 0)
    git("checkout", "--quiet", "-b", "feature")
    (author / "story.txt").write_text(FEATURE, encoding="utf-8")
    (author / "notes.txt").rename(author / "café.txt")
    (author / "café.txt").write_text("A small invented review.\n☃\tUnicode and a tab.\n", encoding="utf-8")
    feature = commit("A greeting and a green door", 1)
    git("checkout", "--quiet", "-b", "revised")
    (author / "story.txt").write_text(REVISED, encoding="utf-8")
    revised = commit("Move the greeting and clarify the path", 2)
    tool("skein.py", "export", str(author), "base", "feature", str(output / "common"))

    # Common notes deliberately cover unique movement, edits, duplicate text,
    # unchanged base anchors and Unicode. The two copies then diverge offline.
    notes = (
        ("greeting", feature, "story.txt", "new", 1, "Should the greeting be shorter?"),
        ("door", feature, "story.txt", "new", 2, "Is the green door intentional?"),
        ("lantern", feature, "story.txt", "new", 3, "Which path does the lantern mark?"),
        ("echo", feature, "story.txt", "new", 4, "This repeated line needs attention."),
        ("base-note", base, "story.txt", "old", 2, "The old door was blue."),
        ("unicode", feature, "café.txt", "new", 2, "Keep the snowman and literal tab."),
    )
    for identifier, revision, path, side, line, body in notes:
        tool("skein.py", "comment", str(output / "common"), "--id", identifier,
             "--commit", revision, "--path", path, "--side", side,
             "--line", str(line), "--body", body)
    for name in ("alice", "bob", "merge-target"):
        shutil.copytree(output / "common", output / name)
    for reviewer, body in (("alice", "Keep the full greeting."), ("bob", "Shorten the greeting.")):
        tool("skein.py", "edit-comment", str(output / reviewer), "--id", "greeting", "--body", body)
    tool("skein.py", "resolve-comment", str(output / "bob"), "--id", "door")
    for reviewer, side, revision, line in (("alice", "old", base, 1), ("bob", "new", feature, 6)):
        tool("skein.py", "comment", str(output / reviewer), "--id", f"{reviewer}-note",
             "--commit", revision, "--path", "story.txt", "--side", side,
             "--line", str(line), "--body", f"An independent note from {reviewer}.")
    tool("skein.py", "export", str(author), "base", "revised", str(output / "revised-packet"))
    manifest: dict[str, object] = {
        "format": "skein-example", "version": 1,
        "commits": {"base": base, "feature": feature, "revised": revised},
        "packets": list(PACKETS),
        "expected_after_merge_and_carry": {"comments": 9, "orphans": ["echo", "lantern"],
                                            "resolved": ["door"], "divergent": ["greeting"]},
    }
    (output / "example.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new workspace in an existing parent directory")
    args = parser.parse_args(argv)
    try:
        manifest = create_example(args.output)
    except (ExampleError, OSError) as exc:
        print(f"example: {exc}", file=sys.stderr)
        print("A failed new workspace may be partial; example.json marks completion.", file=sys.stderr)
        return 1
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
