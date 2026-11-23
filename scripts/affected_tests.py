#!/usr/bin/env python3
"""Run the tests a change can break, not the whole house suite.

Stdlib only. From a git diff, map each changed path to test modules:

* a changed ``tests/test_x.py`` runs itself;
* a changed ``house/*.py`` module runs the tests that import it, directly or
  through other house modules (the import graph is read with ``ast``);
* any other changed file runs the tests (or house modules, then their
  tests) whose source names that path in a string literal.

Anything unmapped, shared (``tests/support.py``), a deleted house module,
or a house module no test imports falls back to the **full suite**. The
selector never drops a test; it only narrows when the mapping is visible.

Usage:
    python3 scripts/affected_tests.py             # working tree vs HEAD
    python3 scripts/affected_tests.py --explain   # why each test was picked
    python3 scripts/affected_tests.py --run       # run the selection
    python3 scripts/affected_tests.py --base HEAD~3 --head HEAD
    python3 scripts/affected_tests.py --replay 60 # replay past commits
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERIC_BASENAMES = {"readme.md", "__init__.py", "__main__.py", "agents.md"}


def module_name(path: str) -> str | None:
    if not path.endswith(".py"):
        return None
    parts = path[:-3].split("/")
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) if parts else None


def _resolve(imported: str, known: set[str]) -> str | None:
    """Longest known module that is a prefix of the imported dotted name."""
    parts = imported.split(".")
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in known:
            return candidate
    return None


def parse_source(source: str, package: str) -> tuple[set[str], set[str]]:
    """Return (dotted names imported, string literals) for one file."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set(), set()
    imports: set[str] = set()
    literals: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = package.split(".") if package else []
                keep = base_parts[: len(base_parts) - node.level + 1] if node.level > 1 else base_parts
                base = ".".join(keep + ([node.module] if node.module else []))
            else:
                base = node.module or ""
            if base:
                imports.add(base)
            for alias in node.names:
                if alias.name != "*":
                    imports.add(f"{base}.{alias.name}" if base else alias.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
    return imports, literals


class Graph:
    """Import graph over the house package plus per-test reachability."""

    def __init__(self, sources: dict[str, str]):
        self.deps: dict[str, set[str]] = {}
        self.literals: dict[str, set[str]] = {}
        known = {name for p in sources if (name := module_name(p))}
        for path, source in sources.items():
            name = module_name(path)
            if name is None:
                continue
            package = name if path.endswith("__init__.py") else name.rpartition(".")[0]
            imports, literals = parse_source(source, package)
            self.literals[name] = literals
            self.deps[name] = {r for i in imports if (r := _resolve(i, known)) and r != name}
        self.house_modules = {n: d for n, d in self.deps.items() if n == "house" or n.startswith("house.")}
        self.test_imports = {n: d for n, d in self.deps.items()
                             if n.startswith("tests.test_") or n.startswith("tests.") and ".test_" in n}
        self.test_names = sorted(n for n in self.deps if n.rsplit(".", 1)[-1].startswith("test_")
                                 and n.startswith("tests."))
        # A test reaches every module it imports through any chain, including
        # through other test modules (tests here do import sibling tests).
        self.test_closure = {test: self._closure(self.deps.get(test, set())) for test in self.test_names}

    def _closure(self, direct: set[str]) -> set[str]:
        seen: set[str] = set()
        stack = list(direct)
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.deps.get(current, ()))
        return seen

    def tests_for(self, module: str) -> set[str]:
        prefix = module + "."
        return {test for test, reached in self.test_closure.items()
                if any(name == module or name.startswith(prefix) for name in reached)}

    def tests_referencing(self, path: str) -> set[str]:
        base = path.rsplit("/", 1)[-1].lower()
        hits = {name for name, literals in self.literals.items()
                if any(path in lit or (base not in GENERIC_BASENAMES and base in lit) for lit in literals)}
        found = {name for name in hits if name in self.test_closure}
        for hit in hits:
            found |= self.tests_for(hit)
        return found


def select(graph: Graph, changed: list[tuple[str, str]]) -> dict:
    """changed: (path, status) with status a git letter (A/C/D/M/R/T)."""
    selected: set[str] = set()
    reasons: dict[str, str] = {}
    full_reasons: list[str] = []
    for path, status in changed:
        deleted = status == "D"
        name = module_name(path)
        if path.startswith("tests/") and Path(path).name.startswith("test_") and name:
            if not deleted:
                selected.add(name)
                reasons[path] = "changed test runs itself"
            else:
                reasons[path] = "deleted test: nothing to run"
        elif path.startswith("tests/"):
            full_reasons.append(f"{path}: shared test support")
            reasons[path] = "shared test support -> full suite"
        elif path.startswith("house/") and name:
            if deleted:
                full_reasons.append(f"{path}: deleted house module")
                reasons[path] = "deleted house module -> full suite"
                continue
            tests = graph.tests_for(name)
            if tests:
                selected |= tests
                reasons[path] = f"{len(tests)} test module(s) import it (transitively)"
            else:
                full_reasons.append(f"{path}: no test imports it")
                reasons[path] = "unmapped house module -> full suite"
        else:
            tests = set() if deleted else graph.tests_referencing(path)
            if tests:
                selected |= tests
                reasons[path] = f"{len(tests)} test module(s) name this path"
            else:
                full_reasons.append(f"{path}: unmapped")
                reasons[path] = "unmapped path -> full suite"
    return {
        "full": bool(full_reasons),
        "tests": sorted(selected),
        "reasons": reasons,
        "full_reasons": full_reasons,
        "changed": [path for path, _ in changed],
    }


def git(*args: str, input_text: str | None = None) -> bytes:
    return subprocess.run(
        ["git", "--literal-pathspecs", *args], cwd=ROOT, input=(input_text.encode() if input_text else None),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=120).stdout


def parse_name_status(raw: bytes) -> list[tuple[str, str]]:
    fields = [f.decode("utf-8", "replace") for f in raw.split(b"\0") if f]
    out: list[tuple[str, str]] = []
    index = 0
    while index < len(fields):
        status = fields[index][0]
        if status in "RC":
            out.append((fields[index + 1], "D"))  # old path deleted
            out.append((fields[index + 2], "A"))
            index += 3
        else:
            out.append((fields[index + 1], status))
            index += 2
    return out


def changed_worktree() -> list[tuple[str, str]]:
    changed = parse_name_status(git("diff", "--name-status", "-z", "HEAD"))
    seen = {p for p, _ in changed}
    for line in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        path = line.decode("utf-8", "replace")
        if path and path not in seen:
            changed.append((path, "A"))
    return changed


def changed_range(base: str, head: str) -> list[tuple[str, str]]:
    return parse_name_status(git("diff", "--name-status", "-z", base, head))


def worktree_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for folder in ("house", "tests", "scripts"):
        for file in sorted((ROOT / folder).rglob("*.py")):
            rel = file.relative_to(ROOT).as_posix()
            sources[rel] = file.read_text(encoding="utf-8", errors="replace")
    return sources


class RevSources:
    """File contents at a git revision, cached by blob id across revisions."""

    def __init__(self) -> None:
        self.cache: dict[str, str] = {}

    def sources(self, rev: str) -> dict[str, str]:
        listing = git("ls-tree", "-r", "-z", rev, "--", "house", "tests", "scripts")
        wanted: dict[str, str] = {}
        for entry in listing.split(b"\0"):
            if not entry:
                continue
            meta, _, raw_path = entry.partition(b"\t")
            path = raw_path.decode("utf-8", "replace")
            fields = meta.split()
            if path.endswith(".py") and len(fields) == 3 and fields[1] == b"blob":
                wanted[path] = fields[2].decode()
        missing = sorted({blob for blob in wanted.values() if blob not in self.cache})
        if missing:
            raw = git("cat-file", "--batch", input_text="\n".join(missing) + "\n")
            pos = 0
            while pos < len(raw):
                end = raw.index(b"\n", pos)
                header = raw[pos:end].decode().split()
                pos = end + 1
                if len(header) >= 3 and header[1] == "blob":
                    size = int(header[2])
                    self.cache[header[0]] = raw[pos:pos + size].decode("utf-8", "replace")
                    pos += size + 1
        return {path: self.cache[blob] for path, blob in wanted.items() if blob in self.cache}


def is_foundation(changed: list[tuple[str, str]]) -> bool:
    if not changed:
        return False
    paths = [p for p, _ in changed]
    if all(p.startswith("projects/") for p in paths):
        return False
    return any(p.startswith(("house/", "tests/", "scripts/")) or "/" not in p for p in paths)


def replay(count: int) -> dict:
    commits = git("log", "--no-merges", f"-n{count * 10}", "--format=%H").decode().split()
    reader = RevSources()
    rows: list[dict] = []
    for commit in commits:
        if len(rows) >= count:
            break
        changed = parse_name_status(
            git("diff-tree", "-r", "--root", "--no-commit-id", "--name-status", "-z", commit))
        if not is_foundation(changed):
            continue
        graph = Graph(reader.sources(commit))
        result = select(graph, changed)
        non_test = [(p, s) for p, s in changed if not (p.startswith("tests/test_"))]
        from_code = select(graph, non_test)
        changed_tests = sorted(
            name for p, s in changed if s != "D" and (name := module_name(p)) and p.startswith("tests/test_"))
        misses = [] if from_code["full"] else [t for t in changed_tests if t not in from_code["tests"]]
        total_tests = len(graph.test_imports)
        rows.append({
            "commit": commit[:9],
            "changed": len(changed),
            "full": result["full"],
            "selected": total_tests if result["full"] else len(result["tests"]),
            "test_modules": total_tests,
            "misses": misses,
        })
    subset_sizes = sorted(r["selected"] for r in rows if not r["full"])
    return {
        "commits": len(rows),
        "full": sum(1 for r in rows if r["full"]),
        "subset": sum(1 for r in rows if not r["full"]),
        "subset_median": subset_sizes[len(subset_sizes) // 2] if subset_sizes else None,
        "miss_commits": sum(1 for r in rows if r["misses"]),
        "rows": rows,
    }


def print_selection(result: dict, explain: bool) -> None:
    if result["full"]:
        print("FULL  (run the whole suite)")
        for reason in result["full_reasons"]:
            print(f"  because: {reason}")
    elif result["tests"]:
        print(f"SUBSET  {len(result['tests'])} test module(s)")
        for test in result["tests"]:
            print(test)
    else:
        print("NONE  (no changed path maps to a test)")
    if explain:
        for path in result["changed"]:
            print(f"  {path}: {result['reasons'].get(path, '')}")


def run_selection(result: dict) -> int:
    if result["full"]:
        command = [sys.executable, "-m", "house.testrun"]
    elif result["tests"]:
        command = [sys.executable, "-m", "unittest", "-v", *result["tests"]]
    else:
        print("nothing to run", file=sys.stderr)
        return 0
    print("+", " ".join(command), file=sys.stderr)
    return subprocess.run(command, cwd=ROOT).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", help="diff base revision (default: working tree vs HEAD)")
    parser.add_argument("--head", default="HEAD", help="diff head revision (with --base)")
    parser.add_argument("--explain", action="store_true", help="show the mapping per changed path")
    parser.add_argument("--run", action="store_true", help="run the selected tests")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--replay", type=int, metavar="N",
                        help="replay selection over the last N foundation commits")
    args = parser.parse_args(argv)

    if args.replay:
        report = replay(args.replay)
        if args.json:
            print(json.dumps(report, indent=1))
        else:
            print(f"replayed {report['commits']} foundation commits: "
                  f"{report['full']} full, {report['subset']} subset"
                  f" (median {report['subset_median']} modules),"
                  f" {report['miss_commits']} miss commits")
            print("miss = commit changed a test the selector would not have run from its code changes alone")
            for row in report["rows"]:
                kind = "FULL  " if row["full"] else "SUBSET"
                miss = f"  MISS {','.join(row['misses'][:3])}" if row["misses"] else ""
                print(f"{row['commit']} {kind} {row['selected']:>4}/{row['test_modules']} modules"
                      f"  changed={row['changed']}{miss}")
        return 0

    changed = changed_range(args.base, args.head) if args.base else changed_worktree()
    if not changed:
        print("NONE  (no changed paths)")
        return 0
    graph = Graph(worktree_sources())
    result = select(graph, changed)
    if args.json:
        print(json.dumps(result, indent=1))
    else:
        print_selection(result, args.explain)
    return run_selection(result) if args.run else 0


if __name__ == "__main__":
    raise SystemExit(main())
