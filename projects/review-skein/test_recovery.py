#!/usr/bin/env python3
"""Tests for Skein Milestone 4 packet recovery, comment salvage and workflow comparison."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comparison
import exchange
import probe
import recovery
import skein


class RecoveryAndComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="skein-test-recovery-")
        self.root = Path(self._temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self._orig_env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
            os.environ.pop(key, None)
        os.environ.update({
            "HOME": str(self.root),
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
        self._git("init", "-b", "base")
        self._git("config", "user.name", "Author")
        self._git("config", "user.email", "author@example.invalid")

        src = self.repo / "src"
        src.mkdir()
        (src / "calc.py").write_text(
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "def scale(x):\n"
            "    if x < 0:\n"
            "        return 0\n"
            "    return x * 2\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "Initial base")
        self.base_commit = self._rev_parse("HEAD")

        self._git("checkout", "-b", "feature")
        (src / "calc.py").write_text(
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "def scale(x):\n"
            "    if x < 0:\n"
            "        return None\n"
            "    if x == 0:\n"
            "        return 0\n"
            "    return x * 3\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "Feature v1")
        self.head_commit = self._rev_parse("HEAD")

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._orig_env)
        self._temp.cleanup()

    def _git(self, *args: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            capture_output=True, text=True, check=True,
        )
        return proc.stdout.strip()

    def _rev_parse(self, ref: str) -> str:
        return self._git("rev-parse", ref)

    def _export_sample_packet(self, dest: Path) -> Path:
        skein.export_packet(self.repo, "base", "feature", dest)
        skein.add_comment(
            dest, "note-1", self.head_commit, "src/calc.py", "new", 6,
            "Should negative input return None or raise ValueError?",
        )
        skein.add_comment(
            dest, "note-2", self.head_commit, "src/calc.py", "new", 9,
            "Confirm factor of 3 is intended.",
        )
        skein.update_comment(dest, "note-2", resolution="resolved")
        return dest

    def _run_recovery_cli(self, *args: str) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = recovery.main(list(args))
        return rc, out.getvalue(), err.getvalue()

    def _run_comparison_cli(self, *args: str) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = comparison.main(list(args))
        return rc, out.getvalue(), err.getvalue()

    def test_diagnose_healthy_packet_and_clean_temp_files(self) -> None:
        packet = self._export_sample_packet(self.root / "packet")
        diag = recovery.diagnose_packet(packet)
        self.assertEqual(diag["status"], "healthy")
        self.assertEqual(diag["missing_members"], [])
        self.assertEqual(diag["corrupted_members"], [])
        self.assertEqual(diag["temp_files"], [])
        self.assertEqual(diag["comments_status"], "intact_v2")
        self.assertEqual(diag["issues"], [])
        rc, out, _ = self._run_recovery_cli("diagnose", str(packet))
        self.assertEqual(rc, 0)
        self.assertIn("status=healthy", out)

        # Create leftover atomic temporary files
        temp_comment = packet / ".comments-abc123.tmp"
        temp_comment.write_text("interrupted write\n", encoding="utf-8")
        temp_other = packet / "review.html.tmp"
        temp_other.write_text("partial html\n", encoding="utf-8")

        diag_with_temp = recovery.diagnose_packet(packet)
        self.assertEqual(diag_with_temp["status"], "recoverable")
        self.assertEqual(
            diag_with_temp["temp_files"],
            [".comments-abc123.tmp", "review.html.tmp"],
        )
        rc, _, _ = self._run_recovery_cli("diagnose", str(packet))
        self.assertEqual(rc, 1)

        # Dry-run clean-temp does not delete files
        dry = recovery.clean_temp_files(packet, apply=False)
        self.assertEqual(dry["temp_files"], [".comments-abc123.tmp", "review.html.tmp"])
        self.assertEqual(dry["removed"], [])
        self.assertTrue(temp_comment.exists())

        # --apply removes only temporary files and restores healthy state
        rc, _, _ = self._run_recovery_cli("clean-temp", str(packet), "--apply")
        self.assertEqual(rc, 0)
        self.assertFalse(temp_comment.exists())
        self.assertFalse(temp_other.exists())
        self.assertEqual(recovery.diagnose_packet(packet)["status"], "healthy")

    def test_rebuild_missing_or_corrupted_derived_files_from_bundle(self) -> None:
        original = self._export_sample_packet(self.root / "original")
        expected_bytes = {
            name: (original / name).read_bytes()
            for name in ("packet.json", "anchors.json", "review.html", "comments.json", "changes.bundle")
        }

        # Case 1: review.html and anchors.json deleted; packet.json, comments.json, changes.bundle intact
        damaged_1 = self.root / "damaged-1"
        shutil.copytree(original, damaged_1)
        (damaged_1 / "review.html").unlink()
        (damaged_1 / "anchors.json").unlink()

        diag_1 = recovery.diagnose_packet(damaged_1)
        self.assertEqual(diag_1["status"], "recoverable")
        self.assertEqual(sorted(diag_1["missing_members"]), ["anchors.json", "review.html"])

        rebuilt_1 = self.root / "rebuilt-1"
        rc, _, _ = self._run_recovery_cli("rebuild", str(damaged_1), str(rebuilt_1))
        self.assertEqual(rc, 0)
        for name, content in expected_bytes.items():
            self.assertEqual((rebuilt_1 / name).read_bytes(), content, f"mismatch in {name}")
        skein.verify_packet(rebuilt_1)
        tree, notes = probe.load_packet(rebuilt_1)
        self.assertEqual([f for f in probe.audit(tree, notes) if f.severity == "error"], [])
        # Damaged directory was not modified in place
        self.assertFalse((damaged_1 / "review.html").exists())

        # Case 2: packet.json also corrupted, rebuilt using bundle + explicit ref labels
        damaged_2 = self.root / "damaged-2"
        shutil.copytree(original, damaged_2)
        (damaged_2 / "packet.json").write_text("{corrupted json", encoding="utf-8")
        (damaged_2 / "review.html").write_text("<html>tampered</html>", encoding="utf-8")

        diag_2 = recovery.diagnose_packet(damaged_2)
        self.assertEqual(diag_2["status"], "recoverable")
        self.assertIn("packet.json", diag_2["corrupted_members"])
        self.assertIn("review.html", diag_2["corrupted_members"])

        rebuilt_2 = self.root / "rebuilt-2"
        result_2 = recovery.rebuild_packet(
            damaged_2, rebuilt_2, base_ref="base", head_ref="feature",
        )
        self.assertEqual(result_2["base_commit"], self.base_commit)
        self.assertEqual(result_2["head_commit"], self.head_commit)
        for name in ("packet.json", "anchors.json", "review.html", "comments.json"):
            self.assertEqual((rebuilt_2 / name).read_bytes(), expected_bytes[name])
        skein.verify_packet(rebuilt_2)

    def test_noncanonical_v2_comments_are_healthy_and_rebuilt_verbatim(self) -> None:
        packet = self._export_sample_packet(self.root / "packet")
        skein.update_comment(packet, "note-1", body="Keep Unicode: café 🌱")
        comments_path = packet / "comments.json"
        original = skein.loads_comments(comments_path.read_text(encoding="utf-8"))
        original[0] = skein.reanchor(original[0], self.head_commit, [])
        self.assertEqual(original[0].state, "orphan")
        self.assertIsNotNone(original[0].rebased_from)
        payload = json.loads(skein.dumps_comments(original))
        # Reordered keys, compact JSON, escaped Unicode and CRLF are valid v2.
        payload = dict(reversed(list(payload.items())))
        variants = [
            json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode(),
            (json.dumps(payload, ensure_ascii=False, indent=4) + "\n").replace("\n", "\r\n").encode(),
        ]
        for index, raw in enumerate(variants):
            with self.subTest(index=index):
                self.assertNotEqual(raw, skein.dumps_comments(original).encode())
                comments_path.write_bytes(raw)
                before = {name: (packet / name).read_bytes() for name in recovery.CANONICAL_MEMBERS}
                rc, out, err = self._run_recovery_cli("diagnose", str(packet), "--json")
                self.assertEqual(rc, 0, err)
                self.assertEqual(json.loads(out)["comments_status"], "intact_v2")
                self.assertEqual(json.loads(out)["issues"], [])

                # Recover missing derived data without normalizing human comments.
                (packet / "review.html").unlink()
                self.assertEqual(recovery.diagnose_packet(packet)["status"], "recoverable")
                rebuilt = self.root / f"rebuilt-noncanonical-{index}"
                result = recovery.rebuild_packet(packet, rebuilt)
                self.assertEqual(result["comments_action"], "intact_v2")
                self.assertFalse((packet / "review.html").exists())
                for name, content in before.items():
                    self.assertEqual((rebuilt / name).read_bytes(), content, name)
                self.assertEqual(comments_path.read_bytes(), raw)
                self.assertEqual(skein.loads_comments(raw.decode()), original)
                self.assertEqual(recovery.diagnose_packet(rebuilt)["status"], "healthy")
                (packet / "review.html").write_bytes(before["review.html"])

    def test_rebuild_missing_bundle_from_repo_after_branch_moves(self) -> None:
        original = self._export_sample_packet(self.root / "original")
        expected_bytes = {
            name: (original / name).read_bytes()
            for name in ("packet.json", "anchors.json", "review.html", "comments.json")
        }

        # Advance 'feature' branch in self.repo so branch name no longer points to self.head_commit
        (self.repo / "src" / "calc.py").write_text("def add(a, b):\n    return a + b + 1\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "Later commit on feature")
        self.assertNotEqual(self._rev_parse("feature"), self.head_commit)

        # Remove changes.bundle from a copy of original
        bundleless = self.root / "bundleless"
        shutil.copytree(original, bundleless)
        (bundleless / "changes.bundle").unlink()

        # Without --repo, missing bundle is unrecoverable because Git objects are absent
        diag_no_repo = recovery.diagnose_packet(bundleless)
        self.assertEqual(diag_no_repo["status"], "unrecoverable")
        self.assertEqual(diag_no_repo["missing_members"], ["changes.bundle"])

        # With --repo, diagnose confirms commits exist and derived files match byte-for-byte
        diag_with_repo = recovery.diagnose_packet(bundleless, repo=self.repo)
        self.assertEqual(diag_with_repo["status"], "recoverable")
        self.assertEqual(diag_with_repo["corrupted_members"], [])

        rebuilt = self.root / "rebuilt-from-repo"
        rc, _, _ = self._run_recovery_cli("rebuild", str(bundleless), str(rebuilt), "--repo", str(self.repo))
        self.assertEqual(rc, 0)
        for name, content in expected_bytes.items():
            self.assertEqual((rebuilt / name).read_bytes(), content, f"mismatch in {name}")
        base_oid, head_oid = skein.verify_packet(rebuilt)
        self.assertEqual(base_oid, self.base_commit)
        self.assertEqual(head_oid, self.head_commit)

        # Also check committed sample/milestone-2 directory if present
        sample_dir = Path(__file__).resolve().parent / "sample" / "milestone-2"
        if sample_dir.is_dir():
            sample_before = {p.name: p.read_bytes() for p in sample_dir.iterdir() if p.is_file()}
            sample_diag = recovery.diagnose_packet(sample_dir)
            self.assertEqual(sample_diag["status"], "unrecoverable")
            self.assertEqual(sample_diag["missing_members"], ["changes.bundle"])
            house_root = Path(__file__).resolve().parents[2]
            sample_repo_diag = recovery.diagnose_packet(sample_dir, repo=house_root)
            self.assertEqual(sample_repo_diag["status"], "recoverable")
            # The archived page retains its dated renderer and audit hashes.
            # Diagnosis compares derived HTML with today's renderer, so only
            # that member differs; rebuilding must preserve the carried data.
            self.assertEqual(sample_repo_diag["corrupted_members"], ["review.html"])
            self.assertEqual(sample_repo_diag["comments_status"], "intact_v2")
            restored_sample = self.root / "restored-historical-sample"
            recovery.rebuild_packet(sample_dir, restored_sample, repo=house_root)
            metadata = json.loads(sample_before["packet.json"])
            self.assertEqual(
                (metadata["base"]["commit"], metadata["head"]["commit"]),
                skein.verify_packet(restored_sample),
            )
            for member in ("packet.json", "anchors.json", "comments.json"):
                self.assertEqual(sample_before[member], (restored_sample / member).read_bytes(), member)
            self.assertNotEqual(sample_before["review.html"], (restored_sample / "review.html").read_bytes())
            self.assertEqual(recovery.diagnose_packet(restored_sample)["corrupted_members"], [])
            self.assertEqual(sample_before, {p.name: p.read_bytes() for p in sample_dir.iterdir() if p.is_file()})

    def test_detect_commit_contradiction_between_manifest_and_bundle(self) -> None:
        packet_a = self._export_sample_packet(self.root / "packet-a")

        # Create a second commit and export packet_b
        (self.repo / "src" / "calc.py").write_text("def add(a, b):\n    return a + b + 99\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "Feature v2")
        packet_b = self.root / "packet-b"
        skein.export_packet(self.repo, "base", "feature", packet_b)

        # Mix packet_a's packet.json with packet_b's changes.bundle
        mixed = self.root / "mixed"
        shutil.copytree(packet_a, mixed)
        shutil.copy2(packet_b / "changes.bundle", mixed / "changes.bundle")

        diag = recovery.diagnose_packet(mixed)
        self.assertEqual(diag["status"], "unrecoverable")
        self.assertTrue(any("mismatch" in issue.casefold() for issue in diag["issues"]))

        # Rebuild refuses without --trust-bundle
        out_fail = self.root / "out-fail"
        rc_fail, _, _ = self._run_recovery_cli("rebuild", str(mixed), str(out_fail))
        self.assertEqual(rc_fail, 2)
        self.assertFalse(out_fail.exists())

        # With --trust-bundle and --salvage-comments, rebuild adopts bundle commits and reanchors/orphans comments
        out_trusted = self.root / "out-trusted"
        rc, _, _ = self._run_recovery_cli(
            "rebuild", str(mixed), str(out_trusted),
            "--trust-bundle", "--salvage-comments",
        )
        self.assertEqual(rc, 0)
        skein.verify_packet(out_trusted)
        comments = skein.loads_comments((out_trusted / "comments.json").read_text(encoding="utf-8"))
        self.assertEqual(len(comments), 2)
        self.assertTrue(all(c.state == "orphan" for c in comments))

    def test_migrate_v1_and_salvage_mismatched_or_duplicate_comments(self) -> None:
        packet = self._export_sample_packet(self.root / "packet")

        # Write a v1 comments.json into a copy
        v1_packet = self.root / "v1-packet"
        shutil.copytree(packet, v1_packet)
        v1_payload = {
            "format": skein.COMMENT_FORMAT,
            "version": 1,
            "comments": [
                {
                    "id": "legacy-1",
                    "anchor": {
                        "commit": self.head_commit,
                        "path": "src/calc.py",
                        "side": "new",
                        "line": 6,
                        "text": "        return None",
                    },
                    "body": "Legacy v1 note.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                }
            ],
        }
        (v1_packet / "comments.json").write_text(
            json.dumps(v1_payload, indent=2) + "\n", encoding="utf-8",
        )
        diag_v1 = recovery.diagnose_packet(v1_packet)
        self.assertEqual(diag_v1["status"], "recoverable")
        self.assertEqual(diag_v1["comments_status"], "legacy_v1")

        rebuilt_v1 = self.root / "rebuilt-v1"
        rc_v1, _, _ = self._run_recovery_cli("rebuild", str(v1_packet), str(rebuilt_v1))
        self.assertEqual(rc_v1, 0)
        migrated = skein.loads_comments((rebuilt_v1 / "comments.json").read_text(encoding="utf-8"))
        self.assertEqual(len(migrated), 1)
        self.assertEqual(migrated[0].identifier, "legacy-1")
        self.assertEqual(migrated[0].resolution, "open")

        # Now test salvaging a damaged comments file with:
        # 1. Exact valid anchor
        # 2. Shifted line number on same file/side ("    return x * 3" is at line 9, claimed line 4)
        # 3. Deleted/nonexistent line text on same file/side
        # 4. Wrong commit hash and missing file path
        # 5. Duplicate IDs with divergent bodies
        raw_damaged = {
            "format": skein.COMMENT_FORMAT,
            "version": 2,
            "comments": [
                {
                    "id": "exact-note",
                    "anchor": {
                        "commit": self.head_commit,
                        "path": "src/calc.py",
                        "side": "new",
                        "line": 6,
                        "text": "        return None",
                    },
                    "body": "Exact anchor match.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                    "resolution": "open",
                },
                {
                    "id": "shifted-note",
                    "anchor": {
                        "commit": self.head_commit,
                        "path": "src/calc.py",
                        "side": "new",
                        "line": 4,
                        "text": "    return x * 3",
                    },
                    "body": "Line number drifted from 4 to 9.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                    "resolution": "resolved",
                },
                {
                    "id": "deleted-text-note",
                    "anchor": {
                        "commit": self.head_commit,
                        "path": "src/calc.py",
                        "side": "new",
                        "line": 5,
                        "text": "    nonexistent_call()",
                    },
                    "body": "Line text does not exist in anchors.json.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                    "resolution": "open",
                },
                {
                    "id": "wrong-commit-note",
                    "anchor": {
                        "commit": "f" * 40,
                        "path": "src/missing.py",
                        "side": "new",
                        "line": 1,
                        "text": "x = 1",
                    },
                    "body": "From another commit and file.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                    "resolution": "open",
                },
                {
                    "id": "dup-note",
                    "anchor": {
                        "commit": self.head_commit,
                        "path": "src/calc.py",
                        "side": "new",
                        "line": 2,
                        "text": "    return a + b",
                    },
                    "body": "Reviewer A variant.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                    "resolution": "open",
                },
                {
                    "id": "dup-note",
                    "anchor": {
                        "commit": self.head_commit,
                        "path": "src/calc.py",
                        "side": "new",
                        "line": 2,
                        "text": "    return a + b",
                    },
                    "body": "Reviewer B variant.",
                    "state": "anchored",
                    "rebased_from": None,
                    "orphan_reason": None,
                    "resolution": "open",
                },
            ],
        }
        damaged_comments_Packet = self.root / "damaged-comments-packet"
        shutil.copytree(packet, damaged_comments_Packet)
        (damaged_comments_Packet / "comments.json").write_text(
            json.dumps(raw_damaged, indent=2) + "\n", encoding="utf-8",
        )

        # Without --salvage-comments, rebuild refuses invalid/duplicate comments
        strict_out = self.root / "strict-out"
        rc_strict, _, _ = self._run_recovery_cli("rebuild", str(damaged_comments_Packet), str(strict_out))
        self.assertEqual(rc_strict, 2)
        self.assertFalse(strict_out.exists())

        # Standalone salvage-comments CLI writes rescued comments to a new file
        salvaged_file = self.root / "salvaged-comments.json"
        rc, _, _ = self._run_recovery_cli(
            "salvage-comments",
            str(damaged_comments_Packet / "comments.json"),
            str(packet),
            "--output", str(salvaged_file),
        )
        self.assertEqual(rc, 0)
        salvaged = skein.loads_comments(salvaged_file.read_text(encoding="utf-8"))
        self.assertEqual(len(salvaged), 6)
        by_id = {c.identifier: c for c in salvaged}

        self.assertEqual(by_id["exact-note"].state, "anchored")
        self.assertEqual(by_id["exact-note"].anchor.line, 6)
        self.assertIsNone(by_id["exact-note"].rebased_from)

        self.assertEqual(by_id["shifted-note"].state, "anchored")
        self.assertEqual(by_id["shifted-note"].anchor.line, 9)
        self.assertEqual(by_id["shifted-note"].resolution, "resolved")
        self.assertIsNotNone(by_id["shifted-note"].rebased_from)
        self.assertEqual(by_id["shifted-note"].rebased_from.line, 4)

        self.assertEqual(by_id["deleted-text-note"].state, "orphan")
        self.assertIsNotNone(by_id["deleted-text-note"].orphan_reason)
        self.assertIsNotNone(by_id["deleted-text-note"].rebased_from)

        self.assertEqual(by_id["wrong-commit-note"].state, "orphan")
        self.assertEqual(by_id["wrong-commit-note"].anchor.commit, self.head_commit)
        self.assertEqual(by_id["wrong-commit-note"].rebased_from.commit, "f" * 40)

        divergent = [c for c in salvaged if c.identifier.startswith("dup-note--divergent-")]
        self.assertEqual(len(divergent), 2)
        self.assertEqual({c.body for c in divergent}, {"Reviewer A variant.", "Reviewer B variant."})

        # Also test --in-place salvage on damaged_comments_Packet
        rc_inp, _, _ = self._run_recovery_cli(
            "salvage-comments",
            str(damaged_comments_Packet / "comments.json"),
            str(damaged_comments_Packet),
            "--in-place",
        )
        self.assertEqual(rc_inp, 0)
        self.assertEqual(recovery.diagnose_packet(damaged_comments_Packet)["status"], "healthy")

    def test_reject_symlinks_and_unsafe_outputs(self) -> None:
        packet = self._export_sample_packet(self.root / "packet")
        link_packet = self.root / "link-packet"
        link_packet.symlink_to(packet)

        self.assertEqual(self._run_recovery_cli("diagnose", str(link_packet))[0], 2)
        self.assertEqual(self._run_recovery_cli("rebuild", str(link_packet), str(self.root / "out"))[0], 2)
        # Refuses existing output directory
        existing_out = self.root / "existing-out"
        existing_out.mkdir()
        self.assertEqual(self._run_recovery_cli("rebuild", str(packet), str(existing_out))[0], 2)
        # Refuses output inside packet
        self.assertEqual(self._run_recovery_cli("rebuild", str(packet), str(packet / "nested"))[0], 2)

    def test_comparison_measure_reproducible_metrics_and_formats(self) -> None:
        snapshots = {}
        artifact_sizes = comparison._artifact_sizes

        def capture_artifacts(directory):
            snapshots[(directory.parent.name, directory.name)] = {
                p.name: p.read_bytes() for p in directory.iterdir() if p.is_file()
            }
            return artifact_sizes(directory)

        with patch.object(comparison, "_artifact_sizes", side_effect=capture_artifacts):
            report = comparison.measure_workflows()
        raw_metrics = report["measured"]["raw_git_bundle"]
        skein_metrics = report["measured"]["skein"]
        self.assertEqual(raw_metrics["cli_commands"], 5)
        self.assertEqual(skein_metrics["cli_commands"], 13)
        operation_basis = report["scenario"]["operation_basis"]
        limits = report["scenario"]["comparison_limits"]
        self.assertIn("13 direct Python API calls", operation_basis)
        self.assertIn("not CLI command counts or human effort", operation_basis)
        self.assertIn("raw note writing/merging", operation_basis)
        self.assertIn("Gerrit and Radicle were not run or benchmarked", limits)

        # Count both complete reviewer returns at the same pre-merge revision.
        for workflow, metrics, members in (
            ("raw-workflow", raw_metrics, {"changes.bundle", "review.patch", "notes.json"}),
            ("skein-workflow", skein_metrics, set(recovery.CANONICAL_MEMBERS)),
        ):
            expected_sizes = {}
            for reviewer in ("reviewer-1", "reviewer-2"):
                files = snapshots[(workflow, reviewer)]
                self.assertEqual(set(files), members)
                expected_sizes.update({f"{reviewer}/{name}": len(raw) for name, raw in files.items()})
            self.assertEqual(metrics["reviewer_artifacts"], expected_sizes)
            self.assertEqual(metrics["reviewer_exchange_bytes"], sum(expected_sizes.values()))

        # Every exchanged note, including the shared and colliding variants, is
        # serialized deterministically and included, rather than only in memory.
        for reviewer in ("reviewer-1", "reviewer-2"):
            raw = snapshots[("raw-workflow", reviewer)]["notes.json"]
            notes = json.loads(raw)
            self.assertEqual(raw, (json.dumps(notes, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
            comments = skein.loads_comments(snapshots[("skein-workflow", reviewer)]["comments.json"].decode())
            expected_notes = [
                {"id": c.identifier, "side": c.anchor.side, "line": c.anchor.line,
                 "text": c.anchor.text, "resolution": c.resolution, "body": c.body}
                for c in comments
            ]
            self.assertEqual(notes, expected_notes)
            self.assertEqual(len(notes), 4)
            self.assertIn("collision-note", [note["id"] for note in notes])

        self.assertLess(raw_metrics["reviewer_exchange_bytes"], skein_metrics["reviewer_exchange_bytes"])
        self.assertEqual(raw_metrics["extra_tools_beyond_git"], 0)

        # Raw git bundle + static line notes suffer ID collision and 3 silent post-rebase mis-anchorings
        self.assertEqual(raw_metrics["id_collision_conflicts"], 1)
        self.assertEqual(raw_metrics["silent_misanchored_comments"], 3)

        # Skein preserves both divergent variants, reanchors/orphans accurately with 0 silent mis-anchorings, and recovers deleted HTML/anchors byte-identically
        self.assertEqual(skein_metrics["id_collision_conflicts"], 0)
        self.assertEqual(skein_metrics["divergent_variants_preserved"], 2)
        self.assertEqual(skein_metrics["silent_misanchored_comments"], 0)
        self.assertEqual(skein_metrics["explicit_orphans_with_provenance"], 2)
        self.assertEqual(skein_metrics["accurately_anchored_after_revise"], 5)
        self.assertTrue(skein_metrics["recovery_byte_exact"])

        # Capability matrix covers all 4 systems honestly
        matrix = report["systems"]
        self.assertEqual(set(matrix), {"skein", "raw_git_bundle", "gerrit", "radicle"})
        self.assertFalse(matrix["skein"]["cryptographic_identity"])
        self.assertTrue(matrix["radicle"]["cryptographic_identity"])
        self.assertTrue(matrix["gerrit"]["central_ci_and_acls"])

        # CLI output modes (json, markdown, text) all succeed
        rc_json, out_json, _ = self._run_comparison_cli("measure", "--format", "json")
        self.assertEqual(rc_json, 0)
        repeated = json.loads(out_json)
        self.assertEqual(repeated["scenario"], report["scenario"])
        for workflow, metrics in report["measured"].items():
            self.assertEqual(
                {k: v for k, v in repeated["measured"][workflow].items() if k != "elapsed_ms"},
                {k: v for k, v in metrics.items() if k != "elapsed_ms"},
            )

        rc_md, out_md, _ = self._run_comparison_cli("measure", "--format", "markdown")
        self.assertEqual(rc_md, 0)
        self.assertIn("| Metric |", out_md)
        self.assertIn("| Selected tool operations | 5 | 13 |", out_md)
        self.assertNotIn("CLI commands executed", out_md)
        self.assertIn(operation_basis, out_md)
        self.assertIn(limits, out_md)

        rc_txt, out_txt, _ = self._run_comparison_cli("measure", "--format", "text")
        self.assertEqual(rc_txt, 0)
        self.assertIn("recovery_byte_exact=True", out_txt)
        self.assertIn(operation_basis, out_txt)
        self.assertIn(limits, out_txt)


if __name__ == "__main__":
    unittest.main()
