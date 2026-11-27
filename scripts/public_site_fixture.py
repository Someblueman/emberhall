#!/usr/bin/env python3
"""Copy a witnessed public snapshot from local Git objects; never fetch or publish."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zlib

PUBLIC_REF = "refs/heads/codex/house-pages"
PUBLIC_URL = "https://someblueman.github.io/emberhall/"
MAX_COMPRESSED = 16 * 1024 * 1024
MAX_DECODED = 32 * 1024 * 1024
ASSETS = ("index.html", "house.js", "house.css", "projects.json", "emberhall.svg")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repository: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repository), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Required local publication/source object is unavailable; no network fetch attempted")
    return result.stdout


def receipt(path: Path, relative: str) -> dict:
    value = json.loads(path.read_text())
    if (not isinstance(value, dict) or value.get("status") != 200
            or value.get("url") != PUBLIC_URL + relative
            or value.get("truncated") is not False
            or not re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", "")))):
        raise ValueError("Expected a complete successful read-site receipt for " + relative)
    return value


def build(repository: Path, output: Path, listing_path: Path, companion_path: Path) -> dict:
    if output.exists() or output.is_symlink():
        raise ValueError("Output must be a new directory")
    listing_receipt = receipt(listing_path, "current.json")
    text = listing_receipt.get("text")
    if not isinstance(text, str) or listing_receipt.get("text_truncated") is not False:
        raise ValueError("Listing receipt must include complete text")
    listing_bytes = text.encode("utf-8")
    if sha(listing_bytes) != listing_receipt["sha256"]:
        raise ValueError("Listing text does not match its public receipt hash")
    listing = json.loads(text)
    if not isinstance(listing, dict):
        raise ValueError("Listing must be a JSON object")
    companion = listing.get("gzip", "")
    if not isinstance(companion, str) or not re.fullmatch(r"current/[0-9a-f]{16}\.json\.gz", companion):
        raise ValueError("Expected a safe compressed current-snapshot companion")
    source = listing.get("source_head", "")
    if not isinstance(source, str) or not re.fullmatch(r"[0-9a-f]{40}", source):
        raise ValueError("Listing must identify a source commit")
    delivery = receipt(companion_path, companion)
    publication = git(repository, "rev-parse", "--verify", PUBLIC_REF + "^{commit}").decode().strip()
    compressed = git(repository, "show", publication + ":" + companion)
    if (len(compressed) > MAX_COMPRESSED or sha(compressed) != delivery["sha256"]
            or delivery.get("bytes_read") != len(compressed)
            or not sha(compressed).startswith(Path(companion).name[:16])):
        raise ValueError("Local companion does not match complete witnessed public bytes")
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        decoded = stream.read(MAX_DECODED + 1)
    if len(decoded) > MAX_DECODED:
        raise ValueError("Decoded snapshot exceeds the fixture size limit")
    snapshot = json.loads(decoded)
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot must be a JSON object")
    frames = snapshot.get("frames", [])
    history = listing.get("history", {})
    if (not isinstance(history, dict) or snapshot.get("source_head") != source
            or snapshot.get("journal_head") != listing.get("journal_head")
            or not isinstance(frames, list) or len(frames) != 1 or not isinstance(frames[0], dict)
            or frames[0].get("seq") != history.get("last_sequence")
            or history.get("current_only") is not True):
        raise ValueError("Companion identity or current-only sequence differs from listing")
    files = {name: git(repository, "show", source + ":site/" + name) for name in ASSETS}
    catalogue = json.loads(files["projects.json"])
    if not isinstance(catalogue, dict) or not isinstance(catalogue.get("projects"), list):
        raise ValueError("Expected a public project catalogue")
    previews = set()
    for project in catalogue["projects"]:
        if not isinstance(project, dict) or not isinstance(project.get("files"), list):
            raise ValueError("Expected a project file list")
        for name in project["files"]:
            if not isinstance(name, str):
                raise ValueError("Expected a project file name")
            if name.endswith("/gallery-preview.svg"):
                previews.add(name)
    if len(previews) > 64 or any(not re.fullmatch(r"projects/[A-Za-z0-9_-]+/gallery-preview\.svg", name)
                                 for name in previews):
        raise ValueError("Unsafe or excessive catalogue preview paths")
    files.update({name: git(repository, "show", source + ":" + name) for name in sorted(previews)})
    files.update({"current.json": listing_bytes, companion: compressed})
    files["head.json"] = json.dumps({key: listing[key] for key in ("journal_head", "source_head")}).encode()
    # Balance is generated separately from source. Keep its distinct provenance below.
    files["balance.json"] = git(repository, "show", publication + ":balance.json")
    report = {
        "publication_commit": publication, "source_head": source,
        "journal_head": listing["journal_head"], "sequence": frames[0]["seq"],
        "files": {name: {"sha256": sha(body), "bytes": len(body)} for name, body in files.items()},
        "limitations": ["Local rendering only; no live timing, memory or delivery acceptance.",
                        "History and creation entry pages are not copied; catalogue previews are included.",
                        "Balance comes from the pinned local publication and may be newer than the snapshot.",
                        "head.json is held at the snapshot identity; this fixture does not follow live updates.",
                        "Receipt hashes bind bytes; authenticity depends on retaining the trusted read-site replies."],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="public-fixture-", dir=output.parent) as temporary:
        stage = Path(temporary) / "page"
        stage.mkdir()
        for name, body in files.items():
            destination = stage / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
        (stage / "fixture-provenance.json").write_text(json.dumps(report, indent=2) + "\n")
        # mkdir fences a concurrent creator; never merge with or replace an existing output.
        output.mkdir()
        # A failed copy remains available for inspection; do not delete partial output.
        for child in stage.iterdir():
            child.rename(output / child.name)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--listing-receipt", type=Path, required=True)
    parser.add_argument("--companion-receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = build(args.repository, args.output, args.listing_receipt, args.companion_receipt)
    except (ValueError, OSError, EOFError, zlib.error) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps({"sequence": report["sequence"], "source_head": report["source_head"],
                      "page": str(args.output / "index.html"),
                      "provenance": str(args.output / "fixture-provenance.json")}))


if __name__ == "__main__":
    main()
