# Safe single-file packet archives (`archive.py`)

`archive.py` packages a verified Review Skein packet directory into one
deterministic `.tar.gz` file for transport across email, chat or USB media,
lets you inspect an archive in memory before extracting it, and verifies the
Git bundle and static HTML before unpacking into a new directory.

Only Python's standard library and `git` are required.

## Pack a verified packet

```sh
python3 projects/review-skein/archive.py pack /path/to/packet /path/to/review.skein.tar.gz
```

`pack`:

- verifies the source packet first with `skein.verify_packet` and `probe.audit`;
- reads only the five canonical regular files (`anchors.json`, `changes.bundle`,
  `comments.json`, `packet.json`, `review.html`), refusing symlinks and
  ignoring ambient extra files such as editor snapshots or `.DS_Store`;
- normalizes gzip/tar metadata (`mtime=0`, zeroed owner IDs, sorted names) so
  packing identical packet directories yields byte-identical `.tar.gz` output;
- refuses to overwrite an existing output path or write inside the source
  packet directory, using atomic staging before rename.

## Inspect an archive without extracting

```sh
python3 projects/review-skein/archive.py inspect /path/to/review.skein.tar.gz
python3 projects/review-skein/archive.py inspect /path/to/review.skein.tar.gz --json
```

`inspect` is strictly read-only and never writes extracted packet files to disk.
It enforces bounded member sizes (`32 MiB` for text/JSON/HTML members and
`--max-bundle-bytes`, defaulting to `128 MiB`, for `changes.bundle`), refuses
symlinks, hardlinks, directories, traversal paths, duplicates, missing or extra
members, validates `packet.json`, `anchors.json` and version-2 `comments.json`,
and checks `review.html` with `probe.audit`.

The reader checks physical 512-byte tar headers before reading any payload.
PAX and GNU extension records are refused, even for small metadata: the five
fixed packet filenames need no extensions. It requires two zero tar end blocks,
permits at most 10 KiB of zero end padding, and rejects nonzero alignment padding
or hidden data after tar EOF. Exactly one complete gzip stream is accepted;
CRC/ISIZE errors, missing footers, concatenated streams (even empty ones), and
trailing compressed bytes are refused before any output directory is created.

Decompression runs in chunks of at most 64 KiB. The total decoded ceiling is
`max_bundle_bytes + 4 * 32 MiB + 5 KiB + 10 KiB` (the five payload limits,
headers/alignment, and end padding); the on-disk ceiling adds 1 MiB for gzip
headers and deflate overhead. Member payloads remain bounded in memory.

## Unpack and verify into a new directory

```sh
python3 projects/review-skein/archive.py unpack /path/to/review.skein.tar.gz /path/to/new-packet
```

`unpack` extracts into a staging directory after member validation, runs
`skein.verify_packet` (isolated bundle clone, `git bundle verify`, commit
checks) and `probe.audit`, and atomically renames the staging directory to the
new destination only when every check passes. Existing destinations and symlinks
are refused without writes.

## Honest boundary

Deterministic archive bytes and SHA-256 digests identify exact packet contents,
not the person who sent them. `archive.py` provides no encryption, signatures
or transport authentication. Do not unpack untrusted archives into shared paths;
use `--max-bundle-bytes` when carrying larger repository histories.

## Build and repair handoff

Yarrow's preserved build `9ec1a792` / `a9de4938` introduced the archive,
comment search/filter and standalone probe features. Tern recovered those
thirteen paths for `skein-archive-boundary-repair` and repaired the independently
reported extension/footer and text-control boundaries. Roundtrip, deterministic
packing and the original viewer/editor/probe behavior remain covered alongside
the rejection tests. This is transport hardening within the ongoing project;
the independent desktop/phone/screen-reader trial in [TRIAL.md](TRIAL.md)
remains open and milestone 2 is not closed.
