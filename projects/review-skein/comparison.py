#!/usr/bin/env python3
"""Skein milestone 4: measure a local fixture against raw git bundle.

Executes a two-repository, two-reviewer and revised-patch review scenario using
both raw git bundle + static line-number notes and Skein's export/merge/revise/recovery
tools, measuring artifact sizes, selected tool operations, ID collisions and
post-rebase anchors. Gerrit and Radicle appear only in an unbenchmarked overview.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

import exchange
import recovery
import skein


SYSTEM_CAPABILITIES: dict[str, dict[str, Any]] = {
    "skein": {
        "name": "Review Skein (stdlib CLI + static packet)",
        "requires_server_or_daemon": False,
        "works_across_air_gap": True,
        "extra_tools_beyond_git": "Python 3.10+ (stdlib only)",
        "deterministic_multi_reviewer_merge": True,
        "rebase_line_reanchoring_and_orphans": True,
        "self_contained_offline_html_diff": True,
        "packet_rebuild_from_bundle": True,
        "cryptographic_identity": False,
        "central_ci_and_acls": False,
        "best_when": (
            "1 to 3 reviewers exchange reviews across an air gap, USB drive, email or "
            "shared folder with no server, forge account or background daemon, and "
            "need comments to survive rebases with explicit orphan provenance."
        ),
        "worse_when": (
            "You need cryptographic reviewer signatures (use Radicle or GPG-signed tags), "
            "automated CI gatekeeping and centralized ACLs (use Gerrit), or the smallest "
            "possible byte payload with zero scripts beyond git (use raw git bundle)."
        ),
    },
    "raw_git_bundle": {
        "name": "Raw git bundle + git diff/range-diff + static notes",
        "requires_server_or_daemon": False,
        "works_across_air_gap": True,
        "extra_tools_beyond_git": "None (git only)",
        "deterministic_multi_reviewer_merge": False,
        "rebase_line_reanchoring_and_orphans": False,
        "self_contained_offline_html_diff": False,
        "packet_rebuild_from_bundle": True,
        "cryptographic_identity": False,
        "central_ci_and_acls": False,
        "best_when": (
            "You only need to transfer commits offline or inspect a quick patch in a "
            "terminal with zero Python scripts and minimal file size, without tracking "
            "line-anchored comments across multiple reviewers or revised commits."
        ),
        "worse_when": (
            "Multiple reviewers annotate the same patch independently or the author "
            "rebases/amends the branch: static (file, line) notes silently drift onto "
            "the wrong lines after insertions/deletions and ID collisions require manual merge."
        ),
    },
    "gerrit": {
        "name": "Gerrit Code Review",
        "requires_server_or_daemon": True,
        "works_across_air_gap": False,
        "extra_tools_beyond_git": "Java server, database, commit-msg hook, browser/account",
        "deterministic_multi_reviewer_merge": True,
        "rebase_line_reanchoring_and_orphans": True,
        "self_contained_offline_html_diff": False,
        "packet_rebuild_from_bundle": False,
        "cryptographic_identity": True,
        "central_ci_and_acls": True,
        "best_when": (
            "Teams share continuous network access to a central server and need "
            "authenticated accounts, fine-grained branch ACLs, Change-Id patchset "
            "history, and automated CI label voting."
        ),
        "worse_when": (
            "Reviewers are disconnected or air-gapped, cannot run or reach a central "
            "Java/HTTP server, or want a zero-account review artifact stored as plain files."
        ),
    },
    "radicle": {
        "name": "Radicle (peer-to-peer local-first forge)",
        "requires_server_or_daemon": False,
        "works_across_air_gap": False,
        "extra_tools_beyond_git": "rad CLI + rad-node P2P daemon + Ed25519 keypair",
        "deterministic_multi_reviewer_merge": True,
        "rebase_line_reanchoring_and_orphans": False,
        "self_contained_offline_html_diff": False,
        "packet_rebuild_from_bundle": False,
        "cryptographic_identity": True,
        "central_ci_and_acls": False,
        "best_when": (
            "Distributed teams want cryptographic peer-to-peer identity (DIDs and "
            "Ed25519-signed collaborative objects) replicated over a gossip network."
        ),
        "worse_when": (
            "Participants cannot install a custom Rust binary/daemon, have no peer "
            "network route (sneakernet/air-gap), or want a static HTML diff that opens "
            "directly without initializing a node identity."
        ),
    },
}


def _git_env(home: Path) -> dict[str, str]:
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
        env.pop(key, None)
    env.update({
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "LC_ALL": "C",
        "GIT_AUTHOR_NAME": "Author",
        "GIT_AUTHOR_EMAIL": "author@example.invalid",
        "GIT_COMMITTER_NAME": "Author",
        "GIT_COMMITTER_EMAIL": "author@example.invalid",
        "GIT_AUTHOR_DATE": "1700000000 +0000",
        "GIT_COMMITTER_DATE": "1700000000 +0000",
    })
    return env


def _git_run(cwd: Path, *args: str, home: Path | None = None) -> str:
    proc = subprocess.run(
        ["git", "--no-pager", "-C", str(cwd), *args],
        capture_output=True, text=True, check=True, timeout=60,
        env=_git_env(home or cwd),
    )
    return proc.stdout.strip()


def _artifact_sizes(directory: Path) -> dict[str, int]:
    return {p.name: p.stat().st_size for p in sorted(directory.iterdir()) if p.is_file()}


def measure_workflows() -> dict[str, Any]:
    """Run the same 2-reviewer + revised-patch scenario on raw git bundle vs Skein."""
    with tempfile.TemporaryDirectory(prefix="skein-comparison-") as tmp:
        root = Path(tmp)
        repo_a = root / "author-repo"
        repo_a.mkdir()
        _git_run(repo_a, "init", "-b", "base")
        _git_run(repo_a, "config", "user.name", "Author")
        _git_run(repo_a, "config", "user.email", "author@example.invalid")

        src = repo_a / "src"
        src.mkdir()
        (src / "service.py").write_text(
            "def normalize(name):\n"
            "    return name.strip()\n"
            "\n"
            "def lookup(table, key):\n"
            "    if not key:\n"
            "        return None\n"
            "    return table.get(key)\n",
            encoding="utf-8",
        )
        _git_run(repo_a, "add", ".")
        _git_run(repo_a, "commit", "-m", "Initial base")
        base_commit = _git_run(repo_a, "rev-parse", "HEAD")

        _git_run(repo_a, "checkout", "-b", "feature")
        v1_lines = [
            "def normalize(name):",
            "    return name.strip().lower()",
            "",
            "def lookup(table, key):",
            "    if not key:",
            "        return None",
            "    if key == 'root':",
            "        return None",
            "    return table[key]",
        ]
        (src / "service.py").write_text("\n".join(v1_lines) + "\n", encoding="utf-8")
        _git_run(repo_a, "add", ".")
        _git_run(repo_a, "commit", "-m", "Feature v1")
        v1_commit = _git_run(repo_a, "rev-parse", "HEAD")

        # --- Workflow 1: Raw git bundle + static line-number JSON notes ---
        t0_raw = time.monotonic()
        raw_dir = root / "raw-workflow"
        raw_dir.mkdir()
        raw_commands = 0

        raw_bundle = raw_dir / "changes.bundle"
        _git_run(repo_a, "bundle", "create", str(raw_bundle), "base", "feature")
        raw_commands += 1
        raw_diff = raw_dir / "review.patch"
        raw_diff.write_text(_git_run(repo_a, "diff", "base", "feature") + "\n", encoding="utf-8")
        raw_commands += 1

        # Clone into Reviewer B
        raw_clone = root / "raw-reviewer-clone"
        _git_run(root, "clone", "--quiet", str(raw_bundle), str(raw_clone))
        raw_commands += 1
        _git_run(raw_clone, "bundle", "verify", str(raw_bundle))
        raw_commands += 1

        # Static line notes from Reviewer 1 and Reviewer 2
        raw_r1_notes = [
            {"id": "shared-1", "side": "old", "line": 2, "text": "    return name.strip()", "resolution": "resolved", "body": "Old normalization kept case."},
            {"id": "r1-exact", "side": "new", "line": 2, "text": "    return name.strip().lower()", "resolution": "open", "body": "Lowercase key is good."},
            {"id": "r1-shifted", "side": "new", "line": 9, "text": "    return table[key]", "resolution": "open", "body": "Direct indexing raises KeyError."},
            {"id": "collision-note", "side": "new", "line": 2, "text": "    return name.strip().lower()", "resolution": "open", "body": "Reviewer 1 note on line 2."},
        ]
        raw_r2_notes = [
            {"id": "shared-1", "side": "old", "line": 2, "text": "    return name.strip()", "resolution": "open", "body": "Old normalization kept case."},
            {"id": "r2-fixed", "side": "new", "line": 5, "text": "    if not key:", "resolution": "open", "body": "Check isinstance(key, str) too."},
            {"id": "r2-duplicate", "side": "new", "line": 8, "text": "        return None", "resolution": "open", "body": "Second return None branch."},
            {"id": "collision-note", "side": "new", "line": 2, "text": "    return name.strip().lower()", "resolution": "open", "body": "Reviewer 2 different note on line 2."},
        ]
        # Measure two complete reviewer returns at v1, just as for Skein below.
        # Each return includes the shared bundle/patch plus that reviewer's full
        # ordered note list (sorted JSON keys, indent=2, UTF-8, trailing LF).
        raw_artifacts = {}
        for number, notes in enumerate((raw_r1_notes, raw_r2_notes), 1):
            reviewer = raw_dir / f"reviewer-{number}"
            reviewer.mkdir()
            shutil.copy2(raw_bundle, reviewer / raw_bundle.name)
            shutil.copy2(raw_diff, reviewer / raw_diff.name)
            skein._write(reviewer / "notes.json", skein._json_text(notes))
            raw_artifacts.update({
                f"{reviewer.name}/{name}": size
                for name, size in _artifact_sizes(reviewer).items()
            })
        # Naive dictionary merge by ID detects 1 collision
        merged_raw_by_id: dict[str, dict[str, Any]] = {}
        raw_id_collisions = 0
        for note in raw_r1_notes + raw_r2_notes:
            nid = note["id"]
            if nid in merged_raw_by_id and merged_raw_by_id[nid]["body"] != note["body"]:
                raw_id_collisions += 1
            merged_raw_by_id[nid] = note

        # Author creates feature-v2 on repo_a
        _git_run(repo_a, "checkout", "-b", "feature-v2", "feature")
        v2_lines = [
            "def normalize(name):",
            "    return name.strip().lower()",
            "",
            "# Added context lines shifting lookup() down by 3 lines",
            "DEFAULT_KEY = 'guest'",
            "",
            "def lookup(table, key):",
            "    if not isinstance(key, str) or not key:",
            "        return None",
            "    if key == 'root':",
            "        return None",
            "    return table[key]",
        ]
        (src / "service.py").write_text("\n".join(v2_lines) + "\n", encoding="utf-8")
        _git_run(repo_a, "add", ".")
        _git_run(repo_a, "commit", "-m", "Feature v2 addressing review")
        v2_commit = _git_run(repo_a, "rev-parse", "HEAD")

        _git_run(repo_a, "range-diff", "base..feature", "base..feature-v2")
        raw_commands += 1

        # Check static line numbers from merged_raw_by_id against v2_lines
        raw_silent_misanchored = 0
        raw_still_matching = 0
        for note in merged_raw_by_id.values():
            if note["side"] == "old":
                raw_still_matching += 1
                continue
            line_idx = note["line"] - 1
            actual_line = v2_lines[line_idx] if 0 <= line_idx < len(v2_lines) else ""
            if actual_line == note["text"]:
                raw_still_matching += 1
            else:
                raw_silent_misanchored += 1
        raw_elapsed_ms = round((time.monotonic() - t0_raw) * 1000, 2)

        # --- Workflow 2: Skein zero-service exchange + recovery ---
        t0_skein = time.monotonic()
        skein_dir = root / "skein-workflow"
        skein_dir.mkdir()
        skein_commands = 0

        packet_base = skein_dir / "packet-base"
        skein.export_packet(repo_a, "base", "feature", packet_base)
        skein_commands += 1
        skein.add_comment(
            packet_base, "shared-1", base_commit, "src/service.py", "old", 2,
            "Old normalization kept case.",
        )
        skein_commands += 1

        # Clone bundle in Reviewer B and verify
        skein.verify_packet(packet_base)
        skein_commands += 1

        rev1 = skein_dir / "reviewer-1"
        rev2 = skein_dir / "reviewer-2"
        shutil.copytree(packet_base, rev1)
        shutil.copytree(packet_base, rev2)

        skein.update_comment(rev1, "shared-1", resolution="resolved")
        skein.add_comment(rev1, "r1-exact", v1_commit, "src/service.py", "new", 2, "Lowercase key is good.")
        skein.add_comment(rev1, "r1-shifted", v1_commit, "src/service.py", "new", 9, "Direct indexing raises KeyError.")
        skein.add_comment(rev1, "collision-note", v1_commit, "src/service.py", "new", 2, "Reviewer 1 note on line 2.")
        skein_commands += 4

        skein.add_comment(rev2, "r2-fixed", v1_commit, "src/service.py", "new", 5, "Check isinstance(key, str) too.")
        skein.add_comment(rev2, "r2-duplicate", v1_commit, "src/service.py", "new", 8, "Second return None branch.")
        skein.add_comment(rev2, "collision-note", v1_commit, "src/service.py", "new", 2, "Reviewer 2 different note on line 2.")
        skein_commands += 3

        skein_artifacts = {
            f"{reviewer.name}/{name}": size
            for reviewer in (rev1, rev2)
            for name, size in _artifact_sizes(reviewer).items()
        }

        merged_pkt = skein_dir / "packet-merged"
        shutil.copytree(packet_base, merged_pkt)
        merge_res = exchange.merge_comments(
            merged_pkt, [rev1, rev2], base=packet_base, on_divergent="keep",
        )
        skein_commands += 1

        # Revise packet to feature-v2 carrying merged comments
        packet_v2 = skein_dir / "packet-v2"
        _, revise_res = exchange.revise_packet(
            repo_a, "base", "feature-v2", packet_v2, sources=[merged_pkt],
        )
        skein_commands += 1

        v2_anchors = set(skein._load_anchors(packet_v2))
        skein_silent_misanchored = 0
        for c in revise_res.comments:
            if c.state == "anchored" and c.anchor not in v2_anchors:
                skein_silent_misanchored += 1

        # Damage packet_v2 by deleting review.html and anchors.json, then rebuild from bundle
        damaged_v2 = skein_dir / "damaged-v2"
        shutil.copytree(packet_v2, damaged_v2)
        (damaged_v2 / "review.html").unlink()
        (damaged_v2 / "anchors.json").unlink()
        rebuilt_v2 = skein_dir / "rebuilt-v2"
        recovery.rebuild_packet(damaged_v2, rebuilt_v2)
        skein_commands += 1

        recovery_exact = all(
            (packet_v2 / name).read_bytes() == (rebuilt_v2 / name).read_bytes()
            for name in recovery.CANONICAL_MEMBERS
        )
        skein_elapsed_ms = round((time.monotonic() - t0_skein) * 1000, 2)

    return {
        "scenario": {
            "operation_basis": (
                "Selected tool operations, not CLI command counts or human effort. "
                "The existing cli_commands JSON fields retain their names: raw counts five "
                "Git subprocesses (bundle, diff, clone, verify, range-diff); Skein counts "
                "13 direct Python API calls (export, eight comment writes, verify, merge, "
                "revise, rebuild). Excludes fixture setup and revision commits, file copies, "
                "raw note writing/merging, reading and nested tool calls. The totals do not "
                "measure equivalent work."
            ),
            "comparison_limits": (
                "This is a scripted local fixture with a naive static-note baseline, "
                "not a novice or general ease-of-use trial. Gerrit and Radicle were not "
                "run or benchmarked; their capability matrix is an overview."
            ),
            "byte_basis": (
                "Sum of two complete reviewer returns at feature v1, after annotations and "
                "before merge: each raw return contains changes.bundle, review.patch and "
                "notes.json; each Skein return contains all five packet files. Counts shared "
                "files once per return; excludes working repositories, merged/revised/recovery "
                "outputs, transport and filesystem overhead."
            ),
            "description": (
                "Two local reviewer copies model disconnected exchange of base..feature "
                "(1 shared comment resolved by "
                "Reviewer 1, 4 distinct line comments, 1 colliding same-ID comment pair), then "
                "author commits feature-v2 (1 unchanged line, 1 line shifted by +3, 1 rewritten "
                "line, 1 duplicate line shifted) and recovers a packet missing review.html and anchors.json."
            ),
            "base_commit": base_commit,
            "v1_commit": v1_commit,
            "v2_commit": v2_commit,
        },
        "measured": {
            "raw_git_bundle": {
                "cli_commands": raw_commands,
                "reviewer_exchange_bytes": sum(raw_artifacts.values()),
                "reviewer_artifacts": raw_artifacts,
                "extra_tools_beyond_git": 0,
                "id_collision_conflicts": raw_id_collisions,
                "divergent_variants_preserved": 1,
                "accurately_anchored_after_revise": raw_still_matching,
                "explicit_orphans_with_provenance": 0,
                "silent_misanchored_comments": raw_silent_misanchored,
                "elapsed_ms": raw_elapsed_ms,
            },
            "skein": {
                "cli_commands": skein_commands,
                "reviewer_exchange_bytes": sum(skein_artifacts.values()),
                "reviewer_artifacts": skein_artifacts,
                "extra_tools_beyond_git": 1,
                "id_collision_conflicts": 0,
                "divergent_variants_preserved": sum("--divergent-" in c.identifier for c in merge_res.comments),
                "accurately_anchored_after_revise": sum(c.state == "anchored" for c in revise_res.comments),
                "explicit_orphans_with_provenance": sum(
                    c.state == "orphan" and c.rebased_from is not None and bool(c.orphan_reason)
                    for c in revise_res.comments
                ),
                "silent_misanchored_comments": skein_silent_misanchored,
                "recovery_byte_exact": recovery_exact,
                "elapsed_ms": skein_elapsed_ms,
            },
        },
        "systems": SYSTEM_CAPABILITIES,
    }


def render_comparison(report: dict[str, Any], *, output_format: str = "text") -> str:
    if output_format == "json":
        return skein._json_text(report)

    raw = report["measured"]["raw_git_bundle"]
    sk = report["measured"]["skein"]

    if output_format == "markdown":
        lines = [
            "# Skein workflow comparison (live fixture measurement)",
            "",
            f"Scenario: {report['scenario']['description']}",
            f"Byte basis: {report['scenario']['byte_basis']}",
            f"Operation basis: {report['scenario']['operation_basis']}",
            f"Limits: {report['scenario']['comparison_limits']}",
            "",
            "## Measured two-reviewer + revised-patch run",
            "",
            "| Metric | Raw `git bundle` + static notes | Review Skein (`skein` + `exchange` + `recovery`) |",
            "| --- | ---: | ---: |",
            f"| Two complete reviewer returns (bytes) | {raw['reviewer_exchange_bytes']} B | {sk['reviewer_exchange_bytes']} B |",
            f"| Extra tools beyond `git` | {raw['extra_tools_beyond_git']} | {sk['extra_tools_beyond_git']} (Python 3.10+ stdlib) |",
            f"| Selected tool operations | {raw['cli_commands']} | {sk['cli_commands']} |",
            f"| Same-ID merge collisions lost/conflicted | {raw['id_collision_conflicts']} | {sk['id_collision_conflicts']} ({sk['divergent_variants_preserved']} variants kept) |",
            f"| Accurately anchored comments on `feature-v2` | {raw['accurately_anchored_after_revise']} | {sk['accurately_anchored_after_revise']} |",
            f"| Explicit orphans with `rebased_from` provenance | {raw['explicit_orphans_with_provenance']} | {sk['explicit_orphans_with_provenance']} |",
            f"| **Silent mis-anchored comments on `feature-v2`** | **{raw['silent_misanchored_comments']}** | **{sk['silent_misanchored_comments']}** |",
            f"| Byte-exact rebuild of deleted `review.html` + `anchors.json` | n/a | `{sk['recovery_byte_exact']}` |",
            "",
            "## Capability matrix across `git bundle`, Skein, Gerrit and Radicle",
            "",
            "| System | Server / daemon required | Air-gap / sneakernet | Rebase reanchoring & orphans | Cryptographic identity | Central CI & ACLs |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for key in ("skein", "raw_git_bundle", "gerrit", "radicle"):
            sys_info = report["systems"][key]
            lines.append(
                f"| {sys_info['name']} | "
                f"{'Yes' if sys_info['requires_server_or_daemon'] else 'No'} | "
                f"{'Yes' if sys_info['works_across_air_gap'] else 'No'} | "
                f"{'Yes' if sys_info['rebase_line_reanchoring_and_orphans'] else 'No'} | "
                f"{'Yes' if sys_info['cryptographic_identity'] else 'No'} | "
                f"{'Yes' if sys_info['central_ci_and_acls'] else 'No'} |"
            )
        lines.append("")
        for key in ("skein", "raw_git_bundle", "gerrit", "radicle"):
            sys_info = report["systems"][key]
            lines.extend([
                f"### {sys_info['name']}",
                f"- **When it wins:** {sys_info['best_when']}",
                f"- **When not to use it:** {sys_info['worse_when']}",
                "",
            ])
        return "\n".join(lines)

    # Default text output
    lines = [
        "Skein workflow comparison",
        f"Scenario: {report['scenario']['description']}",
        f"Byte basis: {report['scenario']['byte_basis']}",
        f"Operation basis: {report['scenario']['operation_basis']}",
        f"Limits: {report['scenario']['comparison_limits']}",
        "",
        f"Raw git bundle + static notes: {raw['reviewer_exchange_bytes']} B, "
        f"{raw['id_collision_conflicts']} ID collision(s), "
        f"{raw['silent_misanchored_comments']} silent mis-anchored comment(s) after feature-v2.",
        f"Review Skein: {sk['reviewer_exchange_bytes']} B, "
        f"{sk['id_collision_conflicts']} ID collisions ({sk['divergent_variants_preserved']} divergent variants kept), "
        f"{sk['accurately_anchored_after_revise']} anchored + {sk['explicit_orphans_with_provenance']} explicit orphans, "
        f"{sk['silent_misanchored_comments']} silent mis-anchored comments, "
        f"recovery_byte_exact={sk['recovery_byte_exact']}.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    measure_p = subcommands.add_parser(
        "measure", help="run the reproducible two-reviewer + revised-patch comparison",
    )
    measure_p.add_argument(
        "--format", choices=("text", "markdown", "json"), default="text", dest="output_format",
    )
    args = parser.parse_args(argv)
    try:
        report = measure_workflows()
        sys.stdout.write(render_comparison(report, output_format=args.output_format))
        sys.stdout.flush()
        return 0
    except (skein.SkeinError, OSError, subprocess.SubprocessError) as exc:
        print(f"comparison: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
