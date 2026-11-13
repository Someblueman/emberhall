#!/usr/bin/env python3
"""Deterministic offline kit builder for Blackout Kit.

Builds a standard-library ZIP from an explicit allowlist with fixed
timestamps and permissions so the same source produces byte-identical
output. The builder never modifies inputs, never overwrites existing
output, and needs no packages, network, or house runtime.

Usage:
    python3 projects/blackout/bundle.py build -o /path/to/kit.zip [--root /path/to/source]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

ALLOWLIST = (
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

FIXED_DATE = (1980, 1, 1, 0, 0, 0)
FIXED_EXTERNAL_ATTR = (0o644 & 0xFFFF) << 16
FIXED_CREATE_SYSTEM = 3  # Unix, for deterministic external_attr interpretation
FIXED_COMPRESS_TYPE = zipfile.ZIP_STORED
FIXED_COMPRESS_LEVEL = None  # stored is byte-identical across Python/zlib versions


class BundleError(ValueError):
    pass


def _default_root() -> Path:
    # bundle.py lives at <root>/projects/blackout/bundle.py
    return Path(__file__).resolve().parents[2]


def _resolve_root(value: str | None) -> Path:
    if value is None:
        return _default_root()
    root = Path(value)
    if not root.is_absolute():
        root = (Path.cwd() / root).resolve()
    # Require root to exist and be a directory without following ".." components that escape?
    if not root.is_dir():
        raise BundleError(f"root is not a directory: {value!r}")
    return root.resolve()


def _check_regular_file(root: Path, rel: str) -> Path:
    # Reject absolute or traversal or nonportable names
    if not rel or rel.startswith("/") or ".." in Path(rel).parts:
        raise BundleError(f"unsafe allowlist entry: {rel!r}")
    # Reject backslash, colon, control chars
    if "\\" in rel or ":" in rel or any(ord(c) < 32 or ord(c) == 127 for c in rel):
        raise BundleError(f"nonportable allowlist entry: {rel!r}")
    target = root / rel
    # Walk components for symlink check
    current = root
    parts = Path(rel).parts
    for part in parts:
        current = current / part
        # lstat without following symlink
        try:
            st = os.lstat(current)
        except FileNotFoundError:
            raise BundleError(f"missing allowlist file: {rel!r}") from None
        except OSError as exc:
            raise BundleError(f"cannot stat allowlist file: {rel!r}: {exc}") from exc
        # Use getmode via stat
        import stat as _stat
        if _stat.S_ISLNK(st.st_mode):
            raise BundleError(f"symlink in allowlist path: {rel!r} at {part!r}")
    # Check final is regular file
    import stat as _stat
    final_st = os.lstat(target)
    if not _stat.S_ISREG(final_st.st_mode):
        raise BundleError(f"allowlist entry is not a regular file: {rel!r}")
    return target


def _snapshot_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for rel in ALLOWLIST:
        p = _check_regular_file(root, rel)
        # Read bytes via regular file; use O_NONBLOCK? For small files, simple read is ok
        # Use descriptor-relative safe open? Simpler: open with O_NOFOLLOW
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        try:
            fd = os.open(p, flags)
        except OSError as exc:
            raise BundleError(f"cannot open allowlist file {rel!r}: {exc}") from exc
        try:
            data = b""
            while chunk := os.read(fd, 1 << 20):
                data += chunk
        finally:
            os.close(fd)
        result[rel] = hashlib.sha256(data).hexdigest()
    return result


def build_archive(root: Path, output: Path) -> tuple[str, int]:
    # Refuse existing output (including symlink)
    try:
        # lstat the output parent and output itself
        if output.exists() or os.path.lexists(output):
            raise BundleError(f"output already exists: {output}")
    except BundleError:
        raise
    except Exception as exc:
        raise BundleError(f"cannot check output {output}: {exc}") from exc

    if output.is_absolute():
        out_path = output.resolve()
    else:
        out_path = (Path.cwd() / output).resolve()

    # Ensure parent exists and is directory
    parent = out_path.parent
    if not parent.is_dir():
        raise BundleError(f"output parent is not a directory: {parent}")

    # Re-check output does not exist after resolving
    if os.path.lexists(out_path):
        raise BundleError(f"output already exists: {out_path}")

    # Collect files sorted (allowlist already sorted, but enforce)
    sorted_rels = sorted(ALLOWLIST)
    # Verify each file and capture bytes
    snapshots: list[tuple[str, bytes]] = []
    for rel in sorted_rels:
        p = _check_regular_file(root, rel)
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        try:
            fd = os.open(p, flags)
        except OSError as exc:
            raise BundleError(f"cannot open {rel!r}: {exc}") from exc
        try:
            chunks = []
            while chunk := os.read(fd, 1 << 20):
                chunks.append(chunk)
            data = b"".join(chunks)
        finally:
            os.close(fd)
        snapshots.append((rel, data))

    before_hashes = {rel: hashlib.sha256(data).hexdigest() for rel, data in snapshots}

    # Build deterministically in a same-directory temp file, then publish with
    # atomic no-clobber via hard link. A hard link fails atomically if the
    # destination already exists, avoiding check-then-rename races where a
    # competing writer creates the output after our last check.
    import tempfile
    tmp_fd, tmp_name = tempfile.mkstemp(prefix=".bundle-", suffix=".zip.tmp", dir=str(parent))
    tmp_path = Path(tmp_name)
    try:
        if tmp_path.resolve() == out_path:
            raise BundleError("temporary path collides with output")
        with os.fdopen(tmp_fd, "wb") as fh:
            # Stored entries are byte-identical across runtimes; deflated output
            # depends on the local zlib and would break cross-runtime checks.
            with zipfile.ZipFile(fh, mode="w", compression=FIXED_COMPRESS_TYPE) as zf:
                for rel, data in snapshots:
                    zi = zipfile.ZipInfo(filename=rel, date_time=FIXED_DATE)
                    zi.compress_type = FIXED_COMPRESS_TYPE
                    zi.external_attr = FIXED_EXTERNAL_ATTR
                    zi.create_system = FIXED_CREATE_SYSTEM
                    zi.internal_attr = 0
                    zi.create_version = 20
                    zi.extract_version = 20
                    zi.flag_bits = 0
                    zi.extra = b""
                    zi.comment = b""
                    zi.header_offset = 0
                    zf.writestr(zi, data)
                zf.comment = b""
        tmp_bytes = tmp_path.read_bytes()
        tmp_hash = hashlib.sha256(tmp_bytes).hexdigest()
        after_hashes = _snapshot_hashes(root)
        if after_hashes != before_hashes:
            raise BundleError("input changed during build")
        # Atomic no-clobber publication: link fails if output exists,
        # rename would silently replace it. Hard link creates the name
        # only if it does not already exist.
        try:
            os.link(tmp_path, out_path)
        except FileExistsError:
            raise BundleError(f"output already exists: {out_path}") from None
        except OSError as exc:
            raise BundleError(f"cannot publish archive {out_path}: {exc}") from exc
        # Complete file is now linked; temp can be unlinked without affecting
        # the published name. Unlink failure of the temp is not fatal because
        # the output already exists and the link count keeps the bytes alive.
        try:
            tmp_path.unlink()
        except OSError:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        tmp_path = None
        out_bytes = out_path.read_bytes()
        if hashlib.sha256(out_bytes).hexdigest() != tmp_hash:
            raise BundleError("built archive hash mismatch after publish")
        return tmp_hash, len(snapshots)
    finally:
        if tmp_path is not None and os.path.lexists(tmp_path):
            try:
                tmp_path.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bundle.py", description="Deterministic offline kit builder for Blackout Kit (standard library only).")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="Build deterministic ZIP from allowlist")
    b.add_argument("-o", "--output", required=True, help="Output ZIP path (must not exist)")
    b.add_argument("--root", default=None, help="Source root (default: repository root inferred from bundle.py location)")

    args = parser.parse_args(argv)

    try:
        root = _resolve_root(args.root)
    except BundleError as exc:
        sys.stderr.write(json.dumps({"error": str(exc)}, sort_keys=True) + "\n")
        return 2

    output = Path(args.output)
    # Keep output as provided for error messages, but build_archive resolves internally
    try:
        sha, count = build_archive(root, output)
    except BundleError as exc:
        sys.stderr.write(json.dumps({"error": str(exc)}, sort_keys=True) + "\n")
        return 2
    except Exception as exc:  # defensive: any unexpected failure is exit 2 with no traceback
        sys.stderr.write(json.dumps({"error": f"{type(exc).__name__}: {exc}"}, sort_keys=True) + "\n")
        return 2

    # Deterministic success output: only hash and count, no timestamps or host paths
    # Output path is not echoed to keep stdout deterministic across different destinations
    sys.stdout.write(json.dumps({"built": True, "files": count, "sha256": sha}, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
