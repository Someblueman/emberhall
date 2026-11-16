#!/usr/bin/env python3
"""Deterministic, verified single-file archives for air-gapped Review Skein packets."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
from typing import Any, BinaryIO, Iterator
import zlib

import probe
import skein


FORMAT = "review-skein-archive"
VERSION = 1
CANONICAL_MEMBERS = (
    "anchors.json",
    "changes.bundle",
    "comments.json",
    "packet.json",
    "review.html",
)
DEFAULT_MAX_BUNDLE_BYTES = 128 * 1024 * 1024


def _validate_max_bundle_bytes(value: int) -> None:
    if type(value) is not int or value < 1:
        raise skein.SkeinError("max_bundle_bytes must be a positive integer")


def _member_limit(name: str, max_bundle_bytes: int) -> int:
    return max_bundle_bytes if name == "changes.bundle" else skein.JSON_LIMIT


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_regular_bytes(path: Path, limit: int, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise skein.SkeinError(f"{label} must be a regular file, not a symlink")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise skein.SkeinError(f"{label} exceeds {limit} bytes")
    return data


def _file_sha256(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise skein.SkeinError(f"archive must be a regular file, not a symlink: {path.name}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _parse_json_bytes(data: bytes, label: str) -> Any:
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=skein._unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise skein.SkeinError(f"invalid JSON in {label}: {exc}") from exc


def _validate_manifest_and_html(members: dict[str, bytes]) -> tuple[dict[str, Any], list[skein.Comment]]:
    packet_data = _parse_json_bytes(members["packet.json"], "packet.json")
    if (
        not isinstance(packet_data, dict)
        or packet_data.get("format") != skein.FORMAT
        or packet_data.get("version") != skein.VERSION
        or not isinstance(packet_data.get("base"), dict)
        or not isinstance(packet_data.get("head"), dict)
        or not isinstance(packet_data.get("files"), list)
    ):
        raise skein.SkeinError("unsupported packet.json header in archive")
    skein._oid(packet_data["base"].get("commit"), "base commit")
    skein._oid(packet_data["head"].get("commit"), "head commit")

    anchors_data = _parse_json_bytes(members["anchors.json"], "anchors.json")
    if (
        not isinstance(anchors_data, dict)
        or set(anchors_data) != {"format", "version", "anchors"}
        or anchors_data["format"] != skein.ANCHOR_FORMAT
        or anchors_data["version"] != skein.VERSION
        or not isinstance(anchors_data["anchors"], list)
    ):
        raise skein.SkeinError("unsupported anchors.json header in archive")
    for item in anchors_data["anchors"]:
        skein.Anchor.from_dict(item)

    try:
        comments_text = members["comments.json"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise skein.SkeinError(f"comments.json is not valid UTF-8: {exc}") from exc
    comments = skein.loads_comments(comments_text)

    try:
        html_text = members["review.html"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise skein.SkeinError(f"review.html is not valid UTF-8: {exc}") from exc
    findings = probe.audit(probe.parse(html_text))
    errors = [item for item in findings if item.severity == "error"]
    if errors:
        raise skein.SkeinError(f"review.html failed offline probe audit: {errors[0].detail}")
    return packet_data, comments


# Five fixed names need no PAX/GNU extensions. Allow one ordinary tar record
# of zero end padding, and bounded gzip header/deflate overhead on disk.
TAR_PADDING_LIMIT = 10240
GZIP_OVERHEAD_LIMIT = 1024 * 1024


def _gzip_blocks(stream: BinaryIO, limit: int) -> Iterator[bytes]:
    """Yield physical 512-byte tar blocks from exactly one CRC-checked gzip."""
    decoder = zlib.decompressobj(wbits=31)
    physical = total = 0
    pending = b""
    while not decoder.eof:
        compressed = stream.read(65536)
        if not compressed:
            raise skein.SkeinError("incomplete gzip stream or missing footer")
        physical += len(compressed)
        if physical > limit + GZIP_OVERHEAD_LIMIT:
            raise skein.SkeinError("compressed archive exceeds physical byte limit")
        while compressed:
            decoded = decoder.decompress(compressed, 65536)
            compressed = decoder.unconsumed_tail
            total += len(decoded)
            if total > limit:
                raise skein.SkeinError("archive exceeds decompressed byte limit")
            available = pending + decoded
            end = len(available) // 512 * 512
            for offset in range(0, end, 512):
                yield available[offset:offset + 512]
            pending = available[end:]
            if decoder.eof:
                if decoder.unused_data or stream.read(1):
                    raise skein.SkeinError("trailing bytes or concatenated gzip streams")
                break
    if pending:
        raise skein.SkeinError("truncated tar block")


def _read_archive_members(archive: Path, max_bundle_bytes: int) -> tuple[str, dict[str, bytes]]:
    _validate_max_bundle_bytes(max_bundle_bytes)
    archive_raw = archive.expanduser()
    if archive_raw.is_symlink() or not archive_raw.is_file():
        raise skein.SkeinError(f"archive must be a regular file, not a symlink: {archive_raw.name}")
    archive_path = archive_raw.resolve()
    # Payloads, five headers and per-member alignment, then bounded end padding.
    limit = max_bundle_bytes + 4 * skein.JSON_LIMIT + 5 * 1024 + TAR_PADDING_LIMIT
    if archive_path.stat().st_size > limit + GZIP_OVERHEAD_LIMIT:
        raise skein.SkeinError("compressed archive exceeds physical byte limit")
    archive_sha256 = _file_sha256(archive_path)
    members: dict[str, bytes] = {}
    zero = bytes(512)
    try:
        with archive_path.open("rb") as raw_stream:
            blocks = _gzip_blocks(raw_stream, limit)
            for header in blocks:
                if header == zero:
                    if next(blocks, None) != zero:
                        raise skein.SkeinError("tar needs two zero end blocks")
                    padding = 1024
                    # Draining is mandatory: it checks the CRC/footer and rejects
                    # hidden data after tar EOF, even inside the same gzip stream.
                    for block in blocks:
                        padding += 512
                        if block != zero or padding > TAR_PADDING_LIMIT:
                            raise skein.SkeinError("invalid or excessive trailing tar padding")
                    break
                # frombuf parses only this physical header, never extension data.
                member = tarfile.TarInfo.frombuf(header, "utf-8", "strict")
                if member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE):
                    raise skein.SkeinError("archive permits only regular files; no PAX/GNU metadata")
                if member.name not in CANONICAL_MEMBERS:
                    raise skein.SkeinError(f"unexpected or unsafe archive member: {member.name!r}")
                if member.name in members:
                    raise skein.SkeinError(f"duplicate archive member: {member.name}")
                member_limit = _member_limit(member.name, max_bundle_bytes)
                if member.size < 0 or member.size > member_limit:
                    raise skein.SkeinError(f"archive member {member.name} exceeds {member_limit} bytes")
                chunks: list[bytes] = []
                remaining = member.size
                while remaining:
                    block = next(blocks, None)
                    if block is None:
                        raise skein.SkeinError(f"truncated archive member: {member.name}")
                    used = min(remaining, 512)
                    chunks.append(block[:used])
                    if any(block[used:]):
                        raise skein.SkeinError("nonzero member alignment padding")
                    remaining -= used
                members[member.name] = b"".join(chunks)
            else:
                raise skein.SkeinError("missing tar end blocks")
    except skein.SkeinError:
        raise
    except (OSError, EOFError, UnicodeError, zlib.error, tarfile.TarError) as exc:
        raise skein.SkeinError(f"invalid Skein archive: {exc}") from exc

    missing = [name for name in CANONICAL_MEMBERS if name not in members]
    if missing:
        raise skein.SkeinError(f"archive is missing canonical packet file(s): {', '.join(missing)}")
    return archive_sha256, members


def _summary(
    archive_sha256: str,
    packet_data: dict[str, Any],
    comments: list[skein.Comment],
    members: dict[str, bytes],
) -> dict[str, Any]:
    return {
        "format": FORMAT,
        "version": VERSION,
        "archive_sha256": archive_sha256,
        "base": packet_data["base"]["commit"],
        "head": packet_data["head"]["commit"],
        "file_count": len(packet_data["files"]),
        "comment_totals": {
            "total": len(comments),
            "open": sum(item.resolution == "open" for item in comments),
            "resolved": sum(item.resolution == "resolved" for item in comments),
            "anchored": sum(item.state == "anchored" for item in comments),
            "orphan": sum(item.state == "orphan" for item in comments),
        },
        "members": {
            name: {"size": len(members[name]), "sha256": _sha256(members[name])}
            for name in CANONICAL_MEMBERS
        },
    }


def pack_packet(
    packet: Path,
    output: Path,
    *,
    max_bundle_bytes: int = DEFAULT_MAX_BUNDLE_BYTES,
) -> dict[str, Any]:
    """Verify a packet directory and write a deterministic .tar.gz archive."""
    _validate_max_bundle_bytes(max_bundle_bytes)
    packet_raw = packet.expanduser()
    if packet_raw.is_symlink() or not packet_raw.is_dir():
        raise skein.SkeinError(f"packet must be a regular directory, not a symlink: {packet_raw}")
    packet_dir = packet_raw.resolve()

    output_raw = output.expanduser()
    if output_raw.is_symlink() or output_raw.exists():
        raise skein.SkeinError("archive output must be a new path; refusing to overwrite anything")
    output_path = output_raw.resolve()
    if output_path == packet_dir or output_path.is_relative_to(packet_dir):
        raise skein.SkeinError("archive output must be outside the packet directory")

    skein.verify_packet(packet_dir)
    members = {
        name: _read_regular_bytes(packet_dir / name, _member_limit(name, max_bundle_bytes), name)
        for name in CANONICAL_MEMBERS
    }
    packet_data, comments = _validate_manifest_and_html(members)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output_path.name}.tmp-", dir=output_path.parent)
    tmp_path = Path(tmp_name)
    published = False
    try:
        with os.fdopen(fd, "wb") as raw_out:
            with gzip.GzipFile(fileobj=raw_out, mode="wb", compresslevel=9, mtime=0) as gz_out:
                with tarfile.open(fileobj=gz_out, mode="w") as tar:
                    for name in CANONICAL_MEMBERS:
                        payload = members[name]
                        info = tarfile.TarInfo(name)
                        info.size = len(payload)
                        info.mtime = 0
                        info.mode = 0o644
                        info.uid = 0
                        info.gid = 0
                        info.uname = ""
                        info.gname = ""
                        info.type = tarfile.REGTYPE
                        tar.addfile(info, io.BytesIO(payload))
            raw_out.flush()
            os.fsync(raw_out.fileno())
        if output_path.exists() or output_path.is_symlink():
            raise skein.SkeinError("archive output appeared during write; refusing to overwrite")
        archive_sha256 = _file_sha256(tmp_path)
        tmp_path.rename(output_path)
        published = True
        return _summary(archive_sha256, packet_data, comments, members)
    finally:
        if not published and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def inspect_archive(
    archive: Path,
    *,
    max_bundle_bytes: int = DEFAULT_MAX_BUNDLE_BYTES,
) -> dict[str, Any]:
    """Read-only verification and summary of a Skein archive without disk extraction."""
    archive_sha256, members = _read_archive_members(archive, max_bundle_bytes)
    packet_data, comments = _validate_manifest_and_html(members)
    return _summary(archive_sha256, packet_data, comments, members)


def unpack_archive(
    archive: Path,
    output: Path,
    *,
    max_bundle_bytes: int = DEFAULT_MAX_BUNDLE_BYTES,
) -> dict[str, Any]:
    """Validate, extract, and Git-verify a Skein archive into a new directory."""
    _validate_max_bundle_bytes(max_bundle_bytes)
    archive_raw = archive.expanduser()
    if archive_raw.is_symlink() or not archive_raw.is_file():
        raise skein.SkeinError(f"archive must be a regular file, not a symlink: {archive_raw}")
    archive_path = archive_raw.resolve()

    output_raw = output.expanduser()
    if output_raw.is_symlink() or output_raw.exists():
        raise skein.SkeinError("packet output must be a new path; refusing to overwrite anything")
    output_path = output_raw.resolve()
    if archive_path == output_path or archive_path.is_relative_to(output_path):
        raise skein.SkeinError("packet output cannot contain the source archive")

    archive_sha256, members = _read_archive_members(archive_path, max_bundle_bytes)
    packet_data, comments = _validate_manifest_and_html(members)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_path.name}.tmp-", dir=output_path.parent))
    published = False
    try:
        for name in CANONICAL_MEMBERS:
            with (staging / name).open("wb") as stream:
                stream.write(members[name])
        skein.verify_packet(staging)
        tree, notes = probe.load_packet(staging)
        errors = [item for item in probe.audit(tree, notes) if item.severity == "error"]
        if errors:
            raise skein.SkeinError(f"unpacked review.html failed probe audit: {errors[0].detail}")
        if output_path.exists() or output_path.is_symlink():
            raise skein.SkeinError("packet output appeared during unpack; refusing to overwrite")
        staging.rename(output_path)
        published = True
        return _summary(archive_sha256, packet_data, comments, members)
    finally:
        if not published:
            shutil.rmtree(staging, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    pack_cmd = subcommands.add_parser("pack", help="pack a verified packet into a deterministic .tar.gz")
    pack_cmd.add_argument("packet", type=Path)
    pack_cmd.add_argument("archive", type=Path)
    pack_cmd.add_argument("--max-bundle-bytes", type=int, default=DEFAULT_MAX_BUNDLE_BYTES)

    inspect_cmd = subcommands.add_parser("inspect", help="inspect a packet archive without extracting")
    inspect_cmd.add_argument("archive", type=Path)
    inspect_cmd.add_argument("--max-bundle-bytes", type=int, default=DEFAULT_MAX_BUNDLE_BYTES)
    inspect_cmd.add_argument("--json", action="store_true")

    unpack_cmd = subcommands.add_parser("unpack", help="verify and unpack an archive into a new directory")
    unpack_cmd.add_argument("archive", type=Path)
    unpack_cmd.add_argument("output", type=Path)
    unpack_cmd.add_argument("--max-bundle-bytes", type=int, default=DEFAULT_MAX_BUNDLE_BYTES)

    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "pack":
            summary = pack_packet(
                arguments.packet,
                arguments.archive,
                max_bundle_bytes=arguments.max_bundle_bytes,
            )
            print(f"Packed Skein archive to {arguments.archive}")
            print(f"Archive SHA-256: {summary['archive_sha256']}")
            print(f"Base {summary['base']} -> head {summary['head']}")
        elif arguments.command == "inspect":
            summary = inspect_archive(
                arguments.archive,
                max_bundle_bytes=arguments.max_bundle_bytes,
            )
            if arguments.json:
                print(json.dumps(summary, indent=2, sort_keys=True))
            else:
                totals = summary["comment_totals"]
                print(f"Skein archive ({summary['archive_sha256']})")
                print(f"Base {summary['base']} -> head {summary['head']}")
                print(
                    f"Files: {summary['file_count']}. "
                    f"Comments: {totals['total']} ({totals['open']} open, "
                    f"{totals['resolved']} resolved; {totals['orphan']} orphan)."
                )
        else:
            summary = unpack_archive(
                arguments.archive,
                arguments.output,
                max_bundle_bytes=arguments.max_bundle_bytes,
            )
            print(f"Unpacked and verified Skein packet at {arguments.output}")
            print(f"Base {summary['base']} -> head {summary['head']}")
        return 0
    except (skein.SkeinError, OSError) as exc:
        print(f"archive: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
