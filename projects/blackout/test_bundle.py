"""Tests for deterministic offline kit builder (bundle.py).

All tests invoke the real builders and the real extracted blackout.py via
subprocess against temporary directories. No mocked filesystem, no house
runtime, no network. The kit is deliberately small and deterministic.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "projects" / "blackout" / "bundle.py"
BLACKOUT = ROOT / "projects" / "blackout" / "blackout.py"
EXPECTED_ALLOWLIST = (
    "projects/blackout/README.md",
    "projects/blackout/QUICKSTART.md",
    "projects/blackout/blackout.py",
    "projects/blackout/examples/recovery-drill/README.md",
    "projects/blackout/examples/recovery-drill/expected-plan.json",
    "projects/blackout/examples/recovery-drill/manifest.json",
    "projects/blackout/examples/recovery-drill/recovery-worksheet.md",
    "projects/blackout/examples/recovery-drill/original/family/summer.txt",
    "projects/blackout/examples/recovery-drill/original/family/winter.txt",
    "projects/blackout/examples/recovery-drill/original/letters/empty.txt",
    "projects/blackout/examples/recovery-drill/original/letters/lost.txt",
    "projects/blackout/examples/recovery-drill/original/photos/Report.txt",
    "projects/blackout/examples/recovery-drill/original/photos/snow \u2603.dat",
    "projects/blackout/examples/recovery-drill/original/records/copy-a.txt",
    "projects/blackout/examples/recovery-drill/original/records/copy-b.txt",
    "projects/blackout/examples/recovery-drill/original/records/invoice.txt",
    "projects/blackout/examples/recovery-drill/surviving/family/renamed-winter.txt",
    "projects/blackout/examples/recovery-drill/surviving/family/summer.txt",
    "projects/blackout/examples/recovery-drill/surviving/letters/empty.txt",
    "projects/blackout/examples/recovery-drill/surviving/photos/report.txt",
    "projects/blackout/examples/recovery-drill/surviving/photos/snow \u2603.dat",
    "projects/blackout/examples/recovery-drill/surviving/records/copy-b.txt",
    "projects/blackout/examples/recovery-drill/surviving/records/invoice.txt",
    "projects/blackout/examples/recovery-drill/surviving/spares/duplicate.txt",
    "projects/blackout/examples/recovery-drill/surviving/spares/invoice-copy.txt",
)


def run_bundle(*args, **kw) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(BUNDLE), *args]
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def run_blackout_at(root: Path, *args) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(root / "projects" / "blackout" / "blackout.py"), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path, rels) -> dict[str, str]:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in rels}


class BundleTests(unittest.TestCase):
    def test_build_produces_allowlisted_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "kit.zip"
            res = run_bundle("build", "-o", str(out))
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            self.assertTrue(out.is_file())
            # stdout is deterministic JSON with sha and count
            payload = json.loads(res.stdout)
            self.assertEqual(payload["built"], True)
            self.assertEqual(payload["files"], len(EXPECTED_ALLOWLIST))
            self.assertEqual(payload["sha256"], hashlib.sha256(out.read_bytes()).hexdigest())
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
                self.assertEqual(sorted(names), sorted(EXPECTED_ALLOWLIST))
                # Each entry has fixed timestamp and no directory entries
                for info in zf.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertFalse(info.is_dir())
                    self.assertEqual(info.create_system, 3)

    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "kit1.zip"
            out2 = Path(tmp) / "kit2.zip"
            r1 = run_bundle("build", "-o", str(out1))
            r2 = run_bundle("build", "-o", str(out2))
            self.assertEqual(r1.returncode, 0, msg=r1.stderr)
            self.assertEqual(r2.returncode, 0, msg=r2.stderr)
            b1 = out1.read_bytes()
            b2 = out2.read_bytes()
            self.assertEqual(b1, b2, msg="two builds must be byte-identical")
            # stdout bytes without output path must also be identical when sha filtered? 
            # Our stdout contains only sha and count, so identical
            self.assertEqual(r1.stdout, r2.stdout)
            self.assertTrue(len(b1) > 0)

    def test_build_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "kit.zip"
            out.write_bytes(b"existing")
            res = run_bundle("build", "-o", str(out))
            self.assertEqual(res.returncode, 2, msg=f"stdout={res.stdout!r} stderr={res.stderr!r}")
            # Existing file unchanged
            self.assertEqual(out.read_bytes(), b"existing")
            err = json.loads(res.stderr.strip().splitlines()[-1]) if res.stderr.strip() else {}
            self.assertIn("error", err)

    def test_build_preserves_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            before = snapshot(ROOT, EXPECTED_ALLOWLIST)
            out = Path(tmp) / "kit.zip"
            res = run_bundle("build", "-o", str(out))
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            after = snapshot(ROOT, EXPECTED_ALLOWLIST)
            self.assertEqual(before, after)

    def test_extracted_kit_is_byte_identical_and_standalone(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out = tmp_path / "kit.zip"
            res = run_bundle("build", "-o", str(out))
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            extract = tmp_path / "extract"
            extract.mkdir()
            with zipfile.ZipFile(out) as zf:
                zf.extractall(extract)
            # Every allowlisted file byte-identical
            for rel in EXPECTED_ALLOWLIST:
                src = ROOT / rel
                dst = extract / rel
                self.assertTrue(dst.is_file(), msg=f"missing {rel}")
                self.assertEqual(
                    hashlib.sha256(dst.read_bytes()).hexdigest(),
                    hashlib.sha256(src.read_bytes()).hexdigest(),
                    msg=f"bytes differ for {rel}",
                )
            # Exact standalone CLI is present and does not import house modules
            kit_blackout = extract / "projects" / "blackout" / "blackout.py"
            self.assertEqual(kit_blackout.read_bytes(), BLACKOUT.read_bytes())
            text = kit_blackout.read_text(encoding="utf-8")
            self.assertNotIn("from house", text)
            self.assertNotIn("import house", text)
            # Standalone verify/plan run without house/Git/network: use extracted paths via cwd
            extract_resolved = extract.resolve()
            verify = subprocess.run([sys.executable, str(extract_resolved / "projects" / "blackout" / "blackout.py"), "verify", "projects/blackout/examples/recovery-drill/surviving", "projects/blackout/examples/recovery-drill/manifest.json"], cwd=str(extract_resolved), capture_output=True, text=True)
            self.assertEqual(verify.returncode, 1, msg=verify.stderr)
            self.assertIn('"matched": 3', verify.stdout)
            plan = subprocess.run([sys.executable, str(extract_resolved / "projects" / "blackout" / "blackout.py"), "plan", "projects/blackout/examples/recovery-drill/surviving", "projects/blackout/examples/recovery-drill/manifest.json"], cwd=str(extract_resolved), capture_output=True, text=True)
            self.assertEqual(plan.returncode, 1, msg=plan.stderr)
            expected = (extract_resolved / "projects/blackout/examples/recovery-drill/expected-plan.json").read_text(encoding="utf-8")
            # Compare parsed JSON objects, not raw formatting (live is single-line, fixture is pretty)
            self.assertEqual(json.loads(plan.stdout), json.loads(expected), msg="plan differs from expected fixture")
            plan2 = subprocess.run([sys.executable, str(extract_resolved / "projects" / "blackout" / "blackout.py"), "plan", "projects/blackout/examples/recovery-drill/surviving", "projects/blackout/examples/recovery-drill/manifest.json"], cwd=str(extract_resolved), capture_output=True, text=True)
            self.assertEqual(plan.stdout, plan2.stdout)

    def test_extracted_kit_create_and_reuse(self):
        # Exercise create in a fresh temp inside extracted kit: no house needed
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp).resolve()
            out = tmp_path / "kit.zip"
            self.assertEqual(run_bundle("build", "-o", str(out)).returncode, 0)
            extract = tmp_path / "extract"
            extract.mkdir()
            with zipfile.ZipFile(out) as zf:
                zf.extractall(extract)
            extract = extract.resolve()
            src_dir = (tmp_path / "myfiles").resolve()
            src_dir.mkdir()
            (src_dir / "a.txt").write_text("hello\n", encoding="utf-8")
            (src_dir / "sub").mkdir()
            (src_dir / "sub" / "b.bin").write_bytes(bytes(range(256)))
            manifest = (tmp_path / "my.json").resolve()
            # Use absolute resolved paths and run from extract via cwd to avoid symlink components
            create = subprocess.run([sys.executable, str(extract / "projects" / "blackout" / "blackout.py"), "create", str(src_dir), str(manifest)], cwd=str(extract), capture_output=True, text=True)
            self.assertEqual(create.returncode, 0, msg=create.stderr + create.stdout)
            self.assertTrue(manifest.is_file())
            verify = subprocess.run([sys.executable, str(extract / "projects" / "blackout" / "blackout.py"), "verify", str(src_dir), str(manifest)], cwd=str(extract), capture_output=True, text=True)
            self.assertEqual(verify.returncode, 0, msg=verify.stderr)
            self.assertIn('"ok": true', verify.stdout)
            plan = subprocess.run([sys.executable, str(extract / "projects" / "blackout" / "blackout.py"), "plan", str(src_dir), str(manifest)], cwd=str(extract), capture_output=True, text=True)
            self.assertEqual(plan.returncode, 0, msg=plan.stderr)
            self.assertIn('"ok": true', plan.stdout)

    def test_allowlist_excludes_private_and_cache(self):
        # Build must not include .git, __pycache__, or extra source
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "kit.zip"
            res = run_bundle("build", "-o", str(out))
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
            for forbidden in (".git", "__pycache__", ".house-mailbox", ".house-client", "bundle.py", "test_bundle.py"):
                for name in names:
                    self.assertNotIn(forbidden, name, msg=f"forbidden {forbidden} in {name}")

    def test_build_with_explicit_root(self):
        # Building from a copied source root yields same bytes as default root
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Create a minimal source tree copy of allowlist only in a new root
            fake_root = tmp_path / "fakerroot"
            fake_root.mkdir()
            for rel in EXPECTED_ALLOWLIST:
                src = ROOT / rel
                dst = fake_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
            out = tmp_path / "kit.zip"
            res = run_bundle("build", "-o", str(out), "--root", str(fake_root))
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            # Compare to a build from real root
            out2 = tmp_path / "kit2.zip"
            res2 = run_bundle("build", "-o", str(out2))
            self.assertEqual(res2.returncode, 0, msg=res2.stderr)
            self.assertEqual(out.read_bytes(), out2.read_bytes())

    def test_missing_allowlist_file_fails_closed(self):
        # If a required file is missing in a custom root, build must exit 2 without creating output
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_root = tmp_path / "root"
            fake_root.mkdir()
            for rel in EXPECTED_ALLOWLIST:
                if rel.endswith("blackout.py"):
                    continue  # omit one
                src = ROOT / rel
                dst = fake_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
            out = tmp_path / "kit.zip"
            res = run_bundle("build", "-o", str(out), "--root", str(fake_root))
            self.assertEqual(res.returncode, 2, msg=res.stdout + res.stderr)
            self.assertFalse(out.exists())

    def test_output_parent_must_be_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_parent = Path(tmp) / "nope" / "kit.zip"
            res = run_bundle("build", "-o", str(missing_parent))
            self.assertEqual(res.returncode, 2, msg=res.stderr)
            # Output not created through missing parent
            self.assertFalse(missing_parent.exists())

    def test_atomic_no_clobber_competing_writer(self):
        # Inject a real competing entry immediately before the publication syscall.
        # This deterministically exercises Keeper's witnessed last-check race;
        # the original check-then-rename implementation fails this regression.
        import os
        import runpy
        from unittest.mock import patch

        builder = runpy.run_path(str(BUNDLE))
        actual_link = os.link
        for kind in ("file", "symlink", "dangling-symlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                out = root / "kit.zip"
                victim = root / "other-writers-file"
                victim.write_bytes(b"Preserve the other writer's bytes.\n")

                def compete(source, destination):
                    if kind == "file":
                        out.write_bytes(b"A competing output, not this ZIP.\n")
                    else:
                        out.symlink_to(victim if kind == "symlink" else root / "absent")
                    return actual_link(source, destination)

                with patch.object(os, "link", side_effect=compete):
                    with self.assertRaisesRegex(builder["BundleError"], "output already exists"):
                        builder["build_archive"](ROOT, out)
                self.assertEqual(victim.read_bytes(), b"Preserve the other writer's bytes.\n")
                if kind == "file":
                    self.assertEqual(out.read_bytes(), b"A competing output, not this ZIP.\n")
                else:
                    self.assertTrue(out.is_symlink())
                    self.assertEqual(out.readlink(), victim if kind == "symlink" else root / "absent")
                self.assertFalse((root / "absent").exists())
                self.assertEqual(list(root.glob(".bundle-*")), [])


if __name__ == "__main__":
    unittest.main()
