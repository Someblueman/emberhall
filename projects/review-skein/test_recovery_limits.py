"""Recovery honors the same explicit blob-size budget as packet export."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import recovery
import skein
from test_skein import SkeinFixture


class RecoveryLimitTests(SkeinFixture):
    def large_packet(self) -> tuple[int, dict[str, bytes]]:
        # One UTF-8 line has fewer characters than the default byte limit, but
        # exactly one byte more than that limit. Keep the HTML fixture small.
        text = "é" * (skein.DEFAULT_MAX_FILE_BYTES // 2) + "\n"
        maximum = len(text.encode("utf-8"))
        self.write("large.txt", text)
        self.commit("a text blob requiring explicit export consent")
        self.head = self.rev_parse("feature")
        self.export(max_file_bytes=maximum)
        skein.add_comment(
            self.packet, "large-note", self.head, "large.txt", "new", 1,
            "Preserve this review across recovery.",
        )
        comments = self.packet / "comments.json"
        # Recovery must preserve accepted noncanonical comments verbatim too.
        comments.write_bytes(json.dumps(json.loads(comments.read_bytes()), indent=4).encode() + b"\r\n")
        return maximum, self.snapshot()

    def snapshot(self) -> dict[str, bytes]:
        return {path.name: path.read_bytes() for path in self.packet.iterdir()}

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(Path(recovery.__file__)), *args],
            capture_output=True, text=True, env=self.environment, timeout=60,
        )

    def test_explicit_limit_diagnoses_and_rebuilds_large_packet(self) -> None:
        maximum, original = self.large_packet()
        default = self.cli("diagnose", str(self.packet), "--json")
        self.assertEqual(default.returncode, 2, default.stderr)
        self.assertEqual(json.loads(default.stdout)["status"], "unrecoverable")
        self.assertIn("above the", " ".join(json.loads(default.stdout)["issues"]))

        report = recovery.diagnose_packet(self.packet, max_file_bytes=maximum)
        self.assertEqual(report["status"], "healthy")
        diagnosed = self.cli("diagnose", str(self.packet), "--max-file-bytes", str(maximum), "--json")
        self.assertEqual(diagnosed.returncode, 0, diagnosed.stderr)
        self.assertEqual(json.loads(diagnosed.stdout)["status"], "healthy")
        self.assertEqual(self.snapshot(), original)

        (self.packet / "review.html").unlink()
        (self.packet / "anchors.json").unlink()
        damaged = self.snapshot()
        output = self.root / "rebuilt"
        refused = self.cli("rebuild", str(self.packet), str(output))
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertIn("above the", refused.stderr)
        self.assertFalse(output.exists())
        rebuilt = self.cli("rebuild", str(self.packet), str(output), "--max-file-bytes", str(maximum), "--json")
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        self.assertEqual(json.loads(rebuilt.stdout)["comments_action"], "intact_v2")
        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, original)
        self.assertEqual(self.snapshot(), damaged)
        self.assertEqual(skein.verify_packet(output), (self.base, self.head))

        existing = self.cli("rebuild", str(self.packet), str(output), "--max-file-bytes", str(maximum))
        self.assertEqual(existing.returncode, 2)
        self.assertIn("refusing to overwrite", existing.stderr)
        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, original)

    def test_insufficient_explicit_limit_preserves_packet_and_output(self) -> None:
        maximum, original = self.large_packet()
        output = self.root / "too-small"
        report = recovery.diagnose_packet(self.packet, max_file_bytes=maximum - 1)
        self.assertEqual(report["status"], "unrecoverable")
        with self.assertRaisesRegex(skein.SkeinError, "above the"):
            recovery.rebuild_packet(self.packet, output, max_file_bytes=maximum - 1)
        result = self.cli("rebuild", str(self.packet), str(output), "--max-file-bytes", str(maximum - 1))
        self.assertEqual(result.returncode, 2)
        self.assertIn("above the", result.stderr)
        self.assertFalse(output.exists())
        self.assertEqual(self.snapshot(), original)

    def test_explicit_limit_also_applies_to_local_repository_recovery(self) -> None:
        maximum, original = self.large_packet()
        (self.packet / "changes.bundle").unlink()
        damaged = self.snapshot()
        args = ("--repo", str(self.repository), "--max-file-bytes", str(maximum))
        report = self.cli("diagnose", str(self.packet), *args, "--json")
        self.assertEqual(report.returncode, 1, report.stderr)
        self.assertEqual(json.loads(report.stdout)["missing_members"], ["changes.bundle"])
        output = self.root / "from-repo"
        rebuilt = self.cli("rebuild", str(self.packet), str(output), *args)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        self.assertEqual(skein.verify_packet(output), (self.base, self.head))
        for name, content in original.items():
            if name != "changes.bundle":
                self.assertEqual((output / name).read_bytes(), content, name)
        self.assertEqual(self.snapshot(), damaged)
        self.assertEqual(self.git("status", "--porcelain").stdout, b"")

    def test_invalid_limits_fail_before_creating_output(self) -> None:
        self.export()
        original = self.snapshot()
        output = self.root / "invalid-limit"
        for invalid in (0, -1, True, 1.5, "1024", None):
            with self.subTest(api_limit=invalid):
                with self.assertRaisesRegex(skein.SkeinError, "positive integer"):
                    recovery.diagnose_packet(self.packet, max_file_bytes=invalid)
                with self.assertRaisesRegex(skein.SkeinError, "positive integer"):
                    recovery.rebuild_packet(self.packet, output, max_file_bytes=invalid)
        for invalid in ("0", "-1", "not-an-integer"):
            for args in (("diagnose", str(self.packet)), ("rebuild", str(self.packet), str(output))):
                with self.subTest(command=args[0], cli_limit=invalid):
                    result = self.cli(*args, "--max-file-bytes", invalid)
                    self.assertEqual(result.returncode, 2)
                    self.assertTrue(result.stderr)
        self.assertFalse(output.exists())
        self.assertEqual(self.snapshot(), original)
