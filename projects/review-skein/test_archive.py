"""TDD tests for deterministic, verified Skein packet archives (archive.py)."""
from __future__ import annotations

import contextlib
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import skein
from test_skein import SkeinFixture

import archive


def _build_custom_tar_gz(path: Path, entries: list[tuple[tarfile.TarInfo, bytes]]) -> None:
    with gzip.GzipFile(path, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tf:
            for info, payload in entries:
                tf.addfile(info, io.BytesIO(payload) if info.isfile() else None)


def _reg_info(name: str, payload: bytes) -> tuple[tarfile.TarInfo, bytes]:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    info.mode = 0o644
    info.mtime = 0
    return info, payload


class ArchiveTests(SkeinFixture):
    def _export_with_comment(self, packet: Path) -> None:
        self.export(packet)
        skein.add_comment(
            packet,
            "note-1",
            self.head,
            "alpha.txt",
            "new",
            2,
            "Check packed comment roundtrip.",
        )

    def test_pack_is_deterministic_and_ignores_extra_files(self) -> None:
        p1 = self.root / "packet-1"
        p2 = self.root / "packet-2"
        self._export_with_comment(p1)
        self._export_with_comment(p2)
        (p1 / ".DS_Store").write_bytes(b"ignored-ambient-junk")

        a1 = self.root / "one.skein.tar.gz"
        a2 = self.root / "two.skein.tar.gz"
        summary1 = archive.pack_packet(p1, a1)
        summary2 = archive.pack_packet(p2, a2)

        self.assertEqual(a1.read_bytes(), a2.read_bytes())
        self.assertEqual(summary1["archive_sha256"], summary2["archive_sha256"])
        self.assertEqual(
            sorted(summary1["members"]),
            ["anchors.json", "changes.bundle", "comments.json", "packet.json", "review.html"],
        )
        self.assertEqual(summary1["base"], self.base)
        self.assertEqual(summary1["head"], self.head)

    def test_inspect_and_unpack_roundtrip_without_source_repo(self) -> None:
        packet = self.root / "packet-src"
        self._export_with_comment(packet)
        expected = {
            name: (packet / name).read_bytes()
            for name in archive.CANONICAL_MEMBERS
        }
        bundle_path = self.root / "review.skein.tar.gz"
        archive.pack_packet(packet, bundle_path)

        # Remove original packet and repo to prove standalone inspection/unpacking.
        for child in sorted(packet.iterdir()):
            child.unlink()
        packet.rmdir()

        report = archive.inspect_archive(bundle_path)
        self.assertEqual(report["format"], archive.FORMAT)
        self.assertEqual(report["version"], archive.VERSION)
        self.assertEqual(report["base"], self.base)
        self.assertEqual(report["head"], self.head)
        self.assertEqual(report["comment_totals"]["total"], 1)
        self.assertEqual(report["comment_totals"]["open"], 1)
        self.assertEqual(report["comment_totals"]["resolved"], 0)
        self.assertEqual(report["comment_totals"]["orphan"], 0)
        self.assertFalse((self.root / "unpacked").exists())

        unpacked = self.root / "unpacked"
        unpack_summary = archive.unpack_archive(bundle_path, unpacked)
        self.assertEqual(unpack_summary["archive_sha256"], report["archive_sha256"])
        self.assertEqual((self.base, self.head), skein.verify_packet(unpacked))
        for name, raw in expected.items():
            self.assertEqual(raw, (unpacked / name).read_bytes(), name)

    def test_multichunk_gzip_roundtrip_and_footer_validation(self) -> None:
        packet = self.root / "packet"
        self.export(packet)
        for index in range(10):
            body = hashlib.shake_256(f"Skein chunk {index}".encode()).hexdigest(10000)
            skein.add_comment(packet, f"large-note-{index}", self.head, "alpha.txt", "new", 2, body)
        path = self.root / "multichunk.tar.gz"
        archive.pack_packet(packet, path)
        self.assertGreater(path.stat().st_size, 65536)
        report = archive.inspect_archive(path)
        self.assertEqual(report["comment_totals"]["total"], 10)
        target = self.root / "unpacked"
        archive.unpack_archive(path, target)
        for name in archive.CANONICAL_MEMBERS:
            self.assertEqual((target / name).read_bytes(), (packet / name).read_bytes())
        path.write_bytes(path.read_bytes()[:-8])
        self._assert_rejected_without_writes(path)

    def test_pack_rejects_overwrite_inside_packet_symlink_and_size_limit(self) -> None:
        packet = self.root / "packet"
        self._export_with_comment(packet)

        existing = self.root / "existing.tar.gz"
        existing.write_bytes(b"keep")
        with self.assertRaises(skein.SkeinError):
            archive.pack_packet(packet, existing)
        self.assertEqual(existing.read_bytes(), b"keep")

        with self.assertRaises(skein.SkeinError):
            archive.pack_packet(packet, packet / "inside.tar.gz")

        with self.assertRaises(skein.SkeinError):
            archive.pack_packet(packet, self.root / "too-big.tar.gz", max_bundle_bytes=16)
        self.assertFalse((self.root / "too-big.tar.gz").exists())

        symlink_packet = self.root / "symlink-packet"
        symlink_packet.symlink_to(packet)
        with self.assertRaises(skein.SkeinError):
            archive.pack_packet(symlink_packet, self.root / "sym.tar.gz")

    def test_inspect_and_unpack_reject_unsafe_or_tampered_archives_without_writes(self) -> None:
        packet = self.root / "packet"
        self._export_with_comment(packet)
        canonical = {name: (packet / name).read_bytes() for name in archive.CANONICAL_MEMBERS}

        # 1. Path traversal / relative prefix
        bad_traversal = self.root / "traversal.tar.gz"
        entries = [_reg_info(name, raw) for name, raw in canonical.items() if name != "packet.json"]
        entries.append(_reg_info("../packet.json", canonical["packet.json"]))
        _build_custom_tar_gz(bad_traversal, entries)

        # 2. Symlink member
        bad_symlink = self.root / "symlink.tar.gz"
        sym = tarfile.TarInfo("review.html")
        sym.type = tarfile.SYMTYPE
        sym.linkname = "/etc/passwd"
        entries_sym = [_reg_info(name, raw) for name, raw in canonical.items() if name != "review.html"]
        entries_sym.append((sym, b""))
        _build_custom_tar_gz(bad_symlink, entries_sym)

        # 3. Extra unexpected member
        bad_extra = self.root / "extra.tar.gz"
        entries_extra = [_reg_info(name, raw) for name, raw in canonical.items()]
        entries_extra.append(_reg_info("README.txt", b"surprise"))
        _build_custom_tar_gz(bad_extra, entries_extra)

        # 4. Missing canonical member
        bad_missing = self.root / "missing.tar.gz"
        _build_custom_tar_gz(
            bad_missing,
            [_reg_info(name, raw) for name, raw in canonical.items() if name != "changes.bundle"],
        )

        # 5. Duplicate member
        bad_dup = self.root / "dup.tar.gz"
        entries_dup = [_reg_info(name, raw) for name, raw in canonical.items()]
        entries_dup.append(_reg_info("comments.json", canonical["comments.json"]))
        _build_custom_tar_gz(bad_dup, entries_dup)

        # 6. Script injection in review.html (rejected on unpack by probe audit)
        bad_script = self.root / "script.tar.gz"
        tampered_html = canonical["review.html"].replace(b"</body>", b"<script>alert(1)</script></body>")
        entries_script = [
            _reg_info(name, tampered_html if name == "review.html" else raw)
            for name, raw in canonical.items()
        ]
        _build_custom_tar_gz(bad_script, entries_script)

        for bad in (bad_traversal, bad_symlink, bad_extra, bad_missing, bad_dup):
            with self.assertRaises(skein.SkeinError, msg=bad.name):
                archive.inspect_archive(bad)
            target = self.root / f"out-{bad.stem}"
            with self.assertRaises(skein.SkeinError, msg=bad.name):
                archive.unpack_archive(bad, target)
            self.assertFalse(target.exists())

        script_target = self.root / "out-script"
        with self.assertRaises(skein.SkeinError):
            archive.unpack_archive(bad_script, script_target)
        self.assertFalse(script_target.exists())

        # Oversized bundle guard
        good = self.root / "good.tar.gz"
        archive.pack_packet(packet, good)
        with self.assertRaises(skein.SkeinError):
            archive.inspect_archive(good, max_bundle_bytes=16)
        out_limit = self.root / "out-limit"
        with self.assertRaises(skein.SkeinError):
            archive.unpack_archive(good, out_limit, max_bundle_bytes=16)
        self.assertFalse(out_limit.exists())

    def _assert_rejected_without_writes(self, path: Path) -> None:
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        for operation in (
            lambda: archive.inspect_archive(path),
            lambda: archive.unpack_archive(path, self.root / "absent-parent" / "output"),
        ):
            with self.assertRaises(skein.SkeinError, msg=path.name):
                operation()
            self.assertFalse((self.root / "absent-parent").exists())
            after = {p.relative_to(self.root): p.read_bytes()
                     for p in self.root.rglob("*") if p.is_file()}
            self.assertEqual(before, after, path.name)

    def test_extended_headers_are_rejected_before_metadata_parsing(self) -> None:
        packet = self.root / "packet"
        self._export_with_comment(packet)
        canonical = [(name, (packet / name).read_bytes()) for name in archive.CANONICAL_MEMBERS]
        # These are valid tar extensions; tarfile hides them from its iterator.
        for kind in (tarfile.XHDTYPE, tarfile.XGLTYPE, tarfile.GNUTYPE_LONGNAME,
                     tarfile.GNUTYPE_LONGLINK):
            with self.subTest(kind=kind):
                path = self.root / (kind.decode() + ".tar.gz")
                data = b"x" * (skein.JSON_LIMIT + 1024)
                if kind in (tarfile.XHDTYPE, tarfile.XGLTYPE):
                    record = b" comment=" + data + b"\n"
                    size = len(record) + len(str(len(record)))
                    while len(str(size).encode() + record) != size:
                        size = len(str(size).encode() + record)
                    data = str(size).encode() + record
                extension = tarfile.TarInfo("metadata")
                extension.type, extension.size = kind, len(data)
                raw = extension.tobuf() + data
                raw += b"\0" * (-len(data) % 512)
                for name, payload in canonical:
                    info, _ = _reg_info(name, payload)
                    raw += info.tobuf() + payload + b"\0" * (-len(payload) % 512)
                raw += b"\0" * 1024
                path.write_bytes(gzip.compress(raw, mtime=0))
                self._assert_rejected_without_writes(path)

    def test_physical_blocks_are_bounded_and_checked_before_extension_payload(self) -> None:
        for kind in (tarfile.XHDTYPE, tarfile.XGLTYPE, tarfile.GNUTYPE_LONGNAME,
                     tarfile.GNUTYPE_LONGLINK):
            extension = tarfile.TarInfo("metadata")
            extension.type, extension.size = kind, 2 ** 40
            path = self.root / (kind.decode() + "-header-only.gz")
            path.write_bytes(gzip.compress(extension.tobuf(), mtime=0))
            # A payload is absent: rejection must be on the header itself.
            with self.assertRaisesRegex(skein.SkeinError, "no PAX/GNU metadata"):
                archive.inspect_archive(path)
        with self.assertRaisesRegex(skein.SkeinError, "decompressed byte limit"):
            list(archive._gzip_blocks(io.BytesIO(gzip.compress(b"x" * 4096)), 1024))
        with self.assertRaisesRegex(skein.SkeinError, "truncated tar block"):
            list(archive._gzip_blocks(io.BytesIO(gzip.compress(b"x" * 513)), 1024))

    def test_physical_archive_size_limit_precedes_hashing_and_decompression(self) -> None:
        path = self.root / "oversized.gz"
        size = 1 + 4 * skein.JSON_LIMIT + 5 * 1024 + 10240 + 1024 * 1024 + 1
        with path.open("wb") as stream:
            stream.truncate(size)  # Sparse file; do not allocate the ceiling in RAM.
        target = self.root / "no-parent" / "output"
        for operation in (
            lambda: archive.inspect_archive(path, max_bundle_bytes=1),
            lambda: archive.unpack_archive(path, target, max_bundle_bytes=1),
        ):
            with self.assertRaisesRegex(skein.SkeinError, "physical byte limit"):
                operation()
            self.assertFalse(target.parent.exists())
            self.assertEqual(path.stat().st_size, size)

    def test_gzip_footer_and_hidden_trailing_streams_are_rejected(self) -> None:
        packet = self.root / "packet"
        self._export_with_comment(packet)
        good = self.root / "good.tar.gz"
        archive.pack_packet(packet, good)
        data = good.read_bytes()
        tar_bytes = gzip.decompress(data)
        first_size = tarfile.TarInfo.frombuf(tar_bytes[:512], "utf-8", "strict").size
        self.assertNotEqual(first_size % 512, 0)
        alignment = 512 + first_size
        variants = {
            "missing-footer": data[:-8],
            "partial-footer": data[:-1],
            "corrupt-crc": data[:-8] + bytes([data[-8] ^ 1]) + data[-7:],
            "corrupt-isize": data[:-4] + bytes([data[-4] ^ 1]) + data[-3:],
            "second-gzip": data + gzip.compress(b"hidden", mtime=0),
            "empty-second-gzip": data + gzip.compress(b"", mtime=0),
            "trailing-raw": data + b"hidden",
            "trailing-zeros": data + b"\0" * 1024,
            "hidden-tar": gzip.compress(tar_bytes + b"hidden" + b"\0" * 506, mtime=0),
            "unbounded-padding": gzip.compress(tar_bytes + b"\0" * 32768, mtime=0),
            "no-tar-eof": gzip.compress(tar_bytes.rstrip(b"\0"), mtime=0),
            "nonzero-alignment": gzip.compress(tar_bytes[:alignment] + b"X" + tar_bytes[alignment + 1:], mtime=0),
        }
        for name, raw in variants.items():
            with self.subTest(name=name):
                bad = self.root / (name + ".tar.gz")
                bad.write_bytes(raw)
                self._assert_rejected_without_writes(bad)

    def test_cli_pack_inspect_and_unpack(self) -> None:
        packet = self.root / "packet"
        self._export_with_comment(packet)
        arch = self.root / "cli.skein.tar.gz"
        unpacked = self.root / "cli-unpacked"

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(archive.main(["pack", str(packet), str(arch)]), 0)
        self.assertIn("Packed Skein archive", out.getvalue())

        inspect_out = io.StringIO()
        with contextlib.redirect_stdout(inspect_out):
            self.assertEqual(archive.main(["inspect", str(arch), "--json"]), 0)
        parsed = json.loads(inspect_out.getvalue())
        self.assertEqual(parsed["base"], self.base)
        self.assertEqual(parsed["head"], self.head)
        self.assertEqual(parsed["comment_totals"]["total"], 1)

        unpack_out = io.StringIO()
        with contextlib.redirect_stdout(unpack_out):
            self.assertEqual(archive.main(["unpack", str(arch), str(unpacked)]), 0)
        self.assertIn("Unpacked and verified", unpack_out.getvalue())

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(archive.main(["unpack", str(arch), str(unpacked)]), 1)
        self.assertIn("archive:", err.getvalue())

    def test_rejects_corrupt_gzip_symlink_archive_v1_comments_and_bad_limit(self) -> None:
        packet = self.root / "packet"
        self._export_with_comment(packet)
        arch = self.root / "valid.skein.tar.gz"
        archive.pack_packet(packet, arch)

        corrupt = self.root / "corrupt.tar.gz"
        corrupt.write_bytes(b"not-a-gzip-stream")
        with self.assertRaises(skein.SkeinError):
            archive.inspect_archive(corrupt)

        sym_arch = self.root / "sym.tar.gz"
        sym_arch.symlink_to(arch)
        with self.assertRaises(skein.SkeinError):
            archive.inspect_archive(sym_arch)
        with self.assertRaises(skein.SkeinError):
            archive.unpack_archive(sym_arch, self.root / "out-sym")

        canonical = {name: (packet / name).read_bytes() for name in archive.CANONICAL_MEMBERS}
        v1_comments = json.dumps({
            "format": skein.COMMENT_FORMAT,
            "version": 1,
            "comments": [],
        }).encode("utf-8")
        v1_arch = self.root / "v1.tar.gz"
        _build_custom_tar_gz(
            v1_arch,
            [
                _reg_info(name, v1_comments if name == "comments.json" else raw)
                for name, raw in canonical.items()
            ],
        )
        with self.assertRaises(skein.SkeinError):
            archive.inspect_archive(v1_arch)

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(archive.main(["inspect", str(arch), "--max-bundle-bytes", "0"]), 1)
        self.assertIn("max_bundle_bytes", err.getvalue())


if __name__ == "__main__":
    unittest.main()
