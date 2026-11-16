#!/usr/bin/env python3
"""Preflight: show what a reader will have to open before you hand over a change.

Preflight reads a Git change and reports the reading and reconstruction load a
reviewer would carry: the files a reader must open whole, how far the change
spreads across directories and subsystems, which groups of files nothing links
and could therefore be handed over separately, whether behaviour changes are
mixed with documentation-only edits, whether changed production files come with
a test file, and which content in the tree would never reach a reviewer.

It makes no claim about how long a review takes. Pull-request size does not
reliably relate to time-to-merge (Kudrjavets, Nagappan & Rastogi, MSR 2022,
arXiv:2203.05045), and a size statistic is not a danger statistic (repowise
says so of its own score). Preflight counts what can be counted and names what
a reader would have to open; the judgement stays with the reader.

Usage:
    python3 preflight.py BASE..HEAD          # a committed range
    python3 preflight.py BASE...HEAD         # a range from the merge base
    python3 preflight.py REF                 # REF against the working tree
    python3 preflight.py                     # uncommitted work
    python3 preflight.py BASE..HEAD --json
    python3 preflight.py --root /path/to/checkout BASE..HEAD

Everything is local: standard library only, no network, no model, no account.
The same tree and the same command give the same numbers every time; nothing
in the report depends on the clock.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = 1
TOOL = "acceptance-preflight"
DEFAULT_READER_LIMIT = 400
WHOLE_FILE_SHARE = 1.0 / 3.0

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
HEADER = re.compile(r"^diff --git a/(.*?) b/(.*)$")
QUOTED = re.compile(r"""["']([^"'\s]{2,200})["']""")
MODULE = re.compile(r"\b(?:from|import)\s+([A-Za-z_][A-Za-z0-9_.]*)")
INCLUDE = re.compile(r"#[ \t]*include[ \t]*[<\"]([^>\"]+)[>\"]")
FILENAME = re.compile(r"\b([A-Za-z0-9_][A-Za-z0-9_./-]*\.[A-Za-z0-9]{1,8})\b")
COMMENT_PREFIXES = ("#", "//", "/*", "*", "<!--", "--", ";", '"""', "'''")
CODE_EXTENSIONS = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".rb", ".go", ".java", ".php", ".rs", ".c",
    ".cc", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala", ".sh", ".sql", ".mjs",
})
LIMITS = (
    "This counts what a reader would have to open. It does not predict how long a review takes.",
    "A whole-file read is a proxy: a new or deleted file, or a change touching a third of the file's lines.",
    "Links between files are textual mentions, not a dependency graph; a missing link can hide a real dependency.",
    "Production files without a test are matched by file-name convention or by a changed test file naming them, not by test coverage.",
    "Documentation-only means every changed line is blank or a comment; a docstring body counts as code.",
)


class PreflightError(Exception):
    """A condition that stops the report."""


@dataclass
class FileChange:
    """One file's change, as a unified diff describes it."""

    path: str = ""
    old_path: str | None = None
    status: str = "modified"
    added: int = 0
    removed: int = 0
    hunks: int = 0
    binary: bool = False
    added_lines: list = field(default_factory=list)
    removed_lines: list = field(default_factory=list)
    context_lines: list = field(default_factory=list)
    old_header_seen: bool = False
    header_old: str | None = None
    header_new: str | None = None

    @property
    def changed_lines(self) -> int:
        return self.added + self.removed

    @property
    def content_changed(self) -> bool:
        return bool(self.added or self.removed)

    @property
    def changed_text(self) -> list:
        return self.added_lines + self.removed_lines

    @property
    def scannable_text(self) -> list:
        """The lines a reader of this change would see, changed and nearby."""
        return self.added_lines + self.removed_lines + self.context_lines


@dataclass
class FileInfo:
    """One file's change with the readings the report draws from it."""

    change: FileChange
    file_lines: int | None = None
    file_bytes: int | None = None
    whole_file: bool = False
    whole_reason: str = ""
    over_limit: bool = False
    changed_share: float | None = None
    documentation_only: bool = False
    move_only: bool = False
    is_test: bool = False
    mentions: list = field(default_factory=list)
    invisible: list = field(default_factory=list)


def _strip_prefix(value: str) -> str | None:
    """Turn a diff path header into a repository path, or None for /dev/null."""
    value = value.strip()
    if value == "/dev/null":
        return None
    if len(value) > 1 and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if value.startswith(("a/", "b/")):
        value = value[2:]
    return value or None


def parse_diff(text: str) -> list:
    """Parse a Git unified diff into per-file changes."""
    changes = []
    current = None
    in_hunk = False
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("diff --git "):
            current = FileChange()
            changes.append(current)
            in_hunk = False
            header = HEADER.match(line)
            if header:
                current.header_old = header.group(1)
                current.header_new = header.group(2)
            continue
        if line.startswith("--- ") and not in_hunk:
            if current is None or current.hunks or current.added_lines or current.removed_lines:
                current = FileChange()
                changes.append(current)
            current.old_path = _strip_prefix(line[4:].split("\t", 1)[0])
            current.old_header_seen = True
            continue
        if line.startswith("+++ ") and not in_hunk:
            if current is None:
                current = FileChange()
                changes.append(current)
            current.path = _strip_prefix(line[4:].split("\t", 1)[0]) or ""
            continue
        if current is None:
            continue
        if line.startswith("new file mode"):
            current.status = "added"
        elif line.startswith("deleted file mode"):
            current.status = "deleted"
        elif line.startswith("rename from "):
            current.old_path = line[len("rename from "):].strip()
            current.status = "renamed"
        elif line.startswith("rename to "):
            current.path = line[len("rename to "):].strip()
            current.status = "renamed"
        elif line.startswith("Binary files ") or line.startswith("GIT binary patch"):
            current.binary = True
        elif line.startswith("@@"):
            match = HUNK.match(line)
            if match:
                current.hunks += 1
                in_hunk = True
        elif line.startswith("+"):
            current.added += 1
            current.added_lines.append(line[1:])
        elif line.startswith("-"):
            current.removed += 1
            current.removed_lines.append(line[1:])
        elif line.startswith(" "):
            current.context_lines.append(line[1:])
    result = []
    for change in changes:
        if change.old_path:
            change.old_path = _strip_prefix(change.old_path) or change.old_path
        if not change.old_header_seen and not change.old_path and change.status != "added" and change.header_old:
            change.old_path = change.header_old
        if not change.path and change.header_new:
            change.path = change.header_new
        if not change.path and change.old_path:
            change.path = change.old_path
            if change.status == "modified":
                change.status = "deleted"
        if change.old_path is None and change.path and change.status == "modified":
            change.status = "added"
        if change.path:
            result.append(change)
    return result


def line_kind(text: str) -> str:
    """Classify one changed line as blank, comment or code."""
    stripped = text.strip()
    if not stripped:
        return "blank"
    if stripped.startswith(COMMENT_PREFIXES):
        return "comment"
    return "code"


def is_test_path(path: str) -> bool:
    """True when the path looks like a test file by naming convention."""
    parts = path.split("/")
    directories = parts[:-1]
    if any(part in {"test", "tests", "__tests__", "spec", "specs"} for part in directories):
        return True
    name = parts[-1]
    stem = name
    for suffix in (".py", ".js", ".jsx", ".ts", ".tsx", ".rb", ".go", ".java", ".php", ".rs", ".c", ".cpp"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    else:
        stem = name.rsplit(".", 1)[0]
    if ".test." in name or ".spec." in name:
        return True
    return stem.startswith("test_") or stem.endswith("_test")


def is_code_path(path: str) -> bool:
    """True when the path names source code rather than prose or data."""
    name = path.rsplit("/", 1)[-1]
    _, dot, extension = name.rpartition(".")
    return bool(dot) and f".{extension.lower()}" in CODE_EXTENSIONS


def test_stem(path: str) -> str | None:
    """The name a test file would carry for the thing it tests, or None."""
    name = path.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    if stem.startswith("test_"):
        return stem[len("test_"):]
    if stem.endswith("_test"):
        return stem[: -len("_test")]
    for marker in (".test", ".spec"):
        if marker in stem:
            return stem.split(marker, 1)[0]
    return None


def module_names(path: str) -> set:
    """Module-style names a path can be imported as."""
    name = path.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    names = {stem}
    if "/" in path:
        directory = path.rsplit("/", 1)[0].replace("/", ".")
        names.add(f"{directory}.{stem}")
    return names


def match_path(mention: str, kind: str, paths) -> str | None:
    """Find the repository path a mention names, if any."""
    text = mention.strip().strip("/")
    if not text:
        return None
    best = None
    best_score = 0
    for path in sorted(paths):
        name = path.rsplit("/", 1)[-1]
        stem = name.rsplit(".", 1)[0]
        score = 0
        if text == path:
            score = 6
        elif path.endswith("/" + text) or text.endswith("/" + path):
            score = 5
        elif kind == "path" and text == name:
            score = 4
        elif kind == "module" and text in module_names(path):
            score = 3
        elif kind == "path" and text == stem:
            score = 2
        if score > best_score:
            best, best_score = path, score
    return best


def mentions_in(line: str) -> list:
    """Return the (kind, text) path-like mentions in one changed line."""
    found = []
    for match in QUOTED.finditer(line):
        found.append(("path", match.group(1)))
    for match in MODULE.finditer(line):
        found.append(("module", match.group(1)))
    for match in INCLUDE.finditer(line):
        found.append(("path", match.group(1)))
    for match in FILENAME.finditer(line):
        found.append(("path", match.group(1)))
    return found


def describe(change: FileChange, size, limit: int) -> FileInfo:
    """Read one change against its base size."""
    base_lines, base_bytes = size if size else (None, None)
    info = FileInfo(change=change, file_bytes=base_bytes)
    if change.status == "added":
        info.file_lines = change.added
    elif base_lines is not None:
        info.file_lines = base_lines
    info.over_limit = bool(info.file_lines and info.file_lines > limit)
    if change.binary:
        info.whole_reason = "binary file: a text diff shows nothing about what changed"
    elif change.status == "added":
        info.whole_file = True
        info.whole_reason = "new file: every line is new"
    elif change.status == "deleted":
        info.whole_file = True
        info.whole_reason = "deleted file: a reader must read it to judge the removal"
    elif not change.content_changed:
        info.whole_reason = "no content change"
    elif base_lines:
        share = change.changed_lines / base_lines
        info.changed_share = round(share, 3)
        if share >= WHOLE_FILE_SHARE:
            info.whole_file = True
            info.whole_reason = "the change touches most of the file"
    kinds = {line_kind(line) for line in change.changed_text}
    info.documentation_only = bool(kinds) and kinds <= {"blank", "comment"}
    info.move_only = change.status == "renamed" and not change.content_changed
    info.is_test = is_test_path(change.path)
    return info


def attach_mentions(files, base_paths) -> None:
    """Record what each changed file mentions, and what the reader cannot see."""
    changed = [info.change.path for info in files]
    for info in files:
        seen = []
        for line in info.change.scannable_text:
            for kind, mention in mentions_in(line):
                target = match_path(mention, kind, changed)
                if target and target != info.change.path:
                    if target not in seen:
                        seen.append(target)
                    continue
                other = match_path(mention, kind, base_paths)
                if other and other != info.change.path and other not in seen:
                    info.invisible.append(other)
        info.mentions = sorted(seen)
        info.invisible = sorted(set(info.invisible))


def group_clusters(files, links) -> list:
    """Group files into clusters nothing links, deterministically."""
    parent = {info.change.path: info.change.path for info in files}

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for left, right in links:
        if left in parent and right in parent and left != right:
            first, second = sorted((find(left), find(right)))
            parent[second] = first
    groups = {}
    for info in files:
        groups.setdefault(find(info.change.path), []).append(info)
    ordered = [sorted(group, key=lambda item: item.change.path) for group in groups.values()]
    ordered.sort(key=lambda group: (-sum(item.change.changed_lines for item in group),
                                    group[0].change.path))
    return ordered


def analyse(changes, sizes, base_paths, limit: int, tree=None) -> dict:
    """Build the report from parsed changes and the base tree's sizes."""
    untracked, unstaged = tree if tree else ([], [])
    files = [describe(change, sizes.get(change.path), limit) for change in changes]
    attach_mentions(files, base_paths)
    links = []
    for info in files:
        for target in info.mentions:
            links.append((info.change.path, target))
    clusters = group_clusters(files, links)

    changed_paths = [info.change.path for info in files]
    changed_stems = {stem for stem in (test_stem(path) for path in changed_paths) if stem}
    test_named = {target for info in files if info.is_test for target in info.mentions}
    production_without_test = []
    for info in files:
        if info.is_test or not is_code_path(info.change.path):
            continue
        stem = info.change.path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if stem not in changed_stems and info.change.path not in test_named:
            production_without_test.append(info.change.path)

    documentation_only = [info.change.path for info in files if info.documentation_only]
    move_only = [info.change.path for info in files if info.move_only]
    code_files = [info.change.path for info in files
                  if not info.documentation_only and not info.move_only]
    mixed = bool(documentation_only or move_only) and bool(code_files)

    directories = sorted({info.change.path.rsplit("/", 1)[0] if "/" in info.change.path else "."
                          for info in files})
    subsystems = {}
    for info in files:
        parts = info.change.path.split("/")
        key = parts[0] if len(parts) > 1 else "."
        subsystems[key] = subsystems.get(key, 0) + 1

    churn_total = sum(info.change.changed_lines for info in files)
    ordered = sorted(files, key=lambda info: (-info.change.changed_lines, info.change.path))
    largest = ordered[0] if ordered else None
    holding = 0
    counted = 0
    for info in ordered:
        holding += info.change.changed_lines
        counted += 1
        if churn_total and holding >= churn_total * 0.8:
            break

    actions = []
    for info in files:
        if info.whole_file:
            actions.append({"kind": "whole-file",
                            "detail": f"{info.change.path} must be read whole: {info.whole_reason}"})
        elif info.over_limit:
            actions.append({"kind": "over-limit",
                            "detail": f"{info.change.path} is {info.file_lines} lines, longer than a "
                                      f"bounded reader's limit of {limit}"})
    if len(clusters) > 1:
        for group in clusters[1:]:
            names = ", ".join(info.change.path for info in group)
            actions.append({"kind": "split",
                            "detail": f"{names} could be handed over separately: nothing links them "
                                      f"to the rest of the change"})
    if mixed:
        actions.append({"kind": "mixed",
                        "detail": "documentation-only edits or pure moves are mixed with code changes"})
    for path in production_without_test:
        actions.append({"kind": "no-test",
                        "detail": f"{path} changed with no test file in this change"})
    named_invisible = set()
    for info in files:
        for path in info.invisible:
            if path in named_invisible:
                continue
            named_invisible.add(path)
            actions.append({"kind": "invisible",
                            "detail": f"{path} is in the tree but not in the change a reviewer sees"})
    for path in untracked:
        actions.append({"kind": "untracked",
                        "detail": f"{path} is untracked and would never reach a reviewer"})
    for path in unstaged:
        actions.append({"kind": "unstaged",
                        "detail": f"{path} has unstaged edits that are not part of this change"})

    return {
        "version": VERSION,
        "tool": TOOL,
        "reader_limit": limit,
        "totals": {
            "files": len(files),
            "added": sum(info.change.added for info in files),
            "removed": sum(info.change.removed for info in files),
            "changed_lines": churn_total,
            "whole_file_reads": sum(1 for info in files if info.whole_file),
            "over_reader_limit": sum(1 for info in files if info.over_limit),
            "subsystems": len(subsystems),
            "directories": len(directories),
            "clusters": len(clusters),
            "test_files": sum(1 for info in files if info.is_test),
        },
        "files": [{
            "path": info.change.path,
            "old_path": info.change.old_path,
            "status": info.change.status,
            "added": info.change.added,
            "removed": info.change.removed,
            "changed_lines": info.change.changed_lines,
            "file_lines": info.file_lines,
            "file_bytes": info.file_bytes,
            "changed_share": info.changed_share,
            "whole_file": info.whole_file,
            "whole_file_reason": info.whole_reason,
            "over_reader_limit": info.over_limit,
            "documentation_only": info.documentation_only,
            "move_only": info.move_only,
            "is_test": info.is_test,
            "mentions": info.mentions,
            "invisible": info.invisible,
        } for info in files],
        "dispersion": {
            "subsystems": dict(sorted(subsystems.items())),
            "directories": directories,
            "churn": {
                "total": churn_total,
                "largest_file": largest.change.path if largest else None,
                "largest_share": round(largest.change.changed_lines / churn_total, 3)
                if largest and churn_total else 0.0,
                "files_holding_80_percent": counted,
            },
        },
        "clusters": [{
            "files": [info.change.path for info in group],
            "changed_lines": sum(info.change.changed_lines for info in group),
            "whole_file_files": [info.change.path for info in group if info.whole_file],
            "subsystems": sorted({info.change.path.split("/")[0]
                                  if "/" in info.change.path else "." for info in group}),
        } for group in clusters],
        "flags": {
            "mixed_documentation_and_code": mixed,
            "documentation_only_files": sorted(documentation_only),
            "move_only_files": sorted(move_only),
            "production_files_without_tests": sorted(production_without_test),
            "changed_test_files": sorted(info.change.path for info in files if info.is_test),
            "untracked_files": list(untracked),
            "unstaged_files": list(unstaged),
        },
        "actions": actions,
        "limits": list(LIMITS),
    }


def git_output(root: Path, *args) -> str:
    """Run a Git command and return its text output, or fail with its message."""
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if proc.returncode != 0:
        message = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        raise PreflightError(message[0] if message else f"git {' '.join(args)} failed")
    return proc.stdout.decode("utf-8", "replace")


def base_sizes(root: Path, base: str, changes) -> dict:
    """Line and byte counts of the base version of each changed file."""
    sizes = {}
    for change in changes:
        source = change.old_path or change.path
        proc = subprocess.run(["git", "-C", str(root), "show", f"{base}:{source}"],
                              capture_output=True)
        if proc.returncode != 0:
            continue
        body = proc.stdout
        if b"\0" in body[:65536]:
            sizes[change.path] = (None, len(body))
            continue
        lines = body.count(b"\n")
        if body and not body.endswith(b"\n"):
            lines += 1
        sizes[change.path] = (lines, len(body))
    return sizes


def working_tree(root: Path) -> tuple:
    """Untracked and unstaged paths in the working tree."""
    untracked, unstaged = [], []
    tokens = iter(git_output(root, "status", "--porcelain", "-z").split("\0"))
    for entry in tokens:
        if len(entry) < 4:
            continue
        index, worktree, name = entry[0], entry[1], entry[3:]
        if index in ("R", "C"):
            # Porcelain -z emits the original path as the following NUL record.
            next(tokens, None)
        if index == "?" and worktree == "?":
            untracked.append(name)
        elif index != "!" and worktree not in (" ", "?"):
            unstaged.append(name)
    return sorted(untracked), sorted(unstaged)


def resolve_range(root: Path, revision: str) -> tuple:
    """Turn the command line's revision into a mode, a base and a diff argument."""
    text = (revision or "").strip()
    if not text:
        return "worktree", "HEAD", ["HEAD"], "uncommitted work (HEAD against the working tree)"
    if "..." in text:
        left, _, right = text.partition("...")
        base = git_output(root, "merge-base", left, right).strip()
        if not base:
            raise PreflightError(f"no merge base for {left} and {right}")
        return "range", base, [text], text
    if ".." in text:
        left, _, right = text.partition("..")
        return "range", left, [text], text
    return "worktree", text, [text], f"{text} against the working tree"


def build_report(root: Path, revision: str, limit: int) -> dict:
    """Read the change with Git and build the report."""
    top = git_output(root, "rev-parse", "--show-toplevel").strip()
    if not top:
        raise PreflightError("not inside a Git checkout")
    root = Path(top)
    mode, base, diff_args, label = resolve_range(root, revision)
    diff_text = git_output(root, "diff", "--no-color", "--no-ext-diff", "--no-textconv",
                           "--unified=3", "--find-renames", *diff_args)
    changes = parse_diff(diff_text)
    sizes = base_sizes(root, base, changes)
    base_paths = set(git_output(root, "ls-tree", "-r", "--name-only", base).splitlines())
    untracked, unstaged = working_tree(root)
    if mode == "worktree":
        # The diff of a worktree already contains the unstaged edits, so only
        # untracked content is outside what a reader of this change would see.
        unstaged = []
    report = analyse(changes, sizes, base_paths, limit, (untracked, unstaged))
    report["mode"] = mode
    report["range"] = label
    report["base"] = base
    return report


def render_text(report: dict) -> str:
    """Render the report as plain text."""
    totals = report["totals"]
    lines = []
    lines.append(f"Acceptance preflight - {report['range']}")
    lines.append(LIMITS[0])
    lines.append("")
    lines.append("Summary")
    lines.append(f"  files changed        {totals['files']}")
    lines.append(f"  lines changed        {totals['changed_lines']} "
                 f"(+{totals['added']} -{totals['removed']})")
    lines.append(f"  whole-file reads     {totals['whole_file_reads']}")
    lines.append(f"  over reader limit    {totals['over_reader_limit']}")
    lines.append(f"  subsystems touched   {totals['subsystems']}")
    lines.append(f"  directories touched  {totals['directories']}")
    lines.append(f"  groups nothing links {totals['clusters']}")
    lines.append(f"  test files changed   {totals['test_files']}")
    lines.append("")
    lines.append(f"Reading load (a bounded reader holds {report['reader_limit']} lines)")
    lines.append(f"  {'file':38} {'changed':>7} {'lines':>7}  whole file")
    for entry in report["files"]:
        whole = "yes" if entry["whole_file"] else "no"
        note = entry["whole_file_reason"] if entry["whole_file"] else ""
        if entry["over_reader_limit"]:
            note = (note + "; " if note else "") + "longer than the reader's limit"
        lines.append(f"  {entry['path'][:38]:38} {entry['changed_lines']:>7} "
                     f"{str(entry['file_lines'] if entry['file_lines'] is not None else '-'):>7}  "
                     f"{whole} {note}".rstrip())
    if not report["files"]:
        lines.append("  (no changes)")
    lines.append("")
    lines.append("Dispersion")
    dispersion = report["dispersion"]
    for name, count in dispersion["subsystems"].items():
        lines.append(f"  subsystem {name}: {count} file(s)")
    lines.append(f"  directories: {', '.join(dispersion['directories']) or '(none)'}")
    churn = dispersion["churn"]
    lines.append(f"  churn: {churn['total']} lines, "
                 f"{int(churn['largest_share'] * 100)}% in {churn['largest_file'] or '(none)'}, "
                 f"{churn['files_holding_80_percent']} file(s) hold 80%")
    lines.append("")
    lines.append("Groups nothing links (a possible split)")
    for number, group in enumerate(report["clusters"], 1):
        names = ", ".join(group["files"])
        lines.append(f"  {number}. {names} - {group['changed_lines']} changed lines, "
                     f"{len(group['whole_file_files'])} whole-file read(s)")
    if not report["clusters"]:
        lines.append("  (none)")
    lines.append("")
    lines.append("What you could act on")
    if report["actions"]:
        for number, action in enumerate(report["actions"], 1):
            lines.append(f"  {number}. [{action['kind']}] {action['detail']}")
    else:
        lines.append("  (nothing flagged)")
    lines.append("")
    lines.append("Limits")
    for limit in report["limits"][1:]:
        lines.append(f"  - {limit}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    """Run the command."""
    parser = argparse.ArgumentParser(
        description="Report the reading and reconstruction load of a change.")
    parser.add_argument("revision", nargs="?",
                        help="BASE..HEAD, BASE...HEAD, REF, or nothing for uncommitted work")
    parser.add_argument("--root", default=".",
                        help="the checkout to read (default: the current directory)")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--reader-limit", type=int, default=DEFAULT_READER_LIMIT,
                        help="lines a bounded reader can hold in one window")
    args = parser.parse_args(argv)
    if args.reader_limit < 1:
        print("preflight: the reader limit must be at least one line", file=sys.stderr)
        return 2
    try:
        report = build_report(Path(args.root).resolve(), args.revision, args.reader_limit)
    except PreflightError as error:
        print(f"preflight: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"preflight: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
