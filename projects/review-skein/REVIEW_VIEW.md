# Annotated Diff and Comment View (`review_view.py`)

`review_view.py` renders an exported Review Skein packet (`packet.json`,
`anchors.json`, version-2 `comments.json`, `changes.bundle`) as a single
read-only, self-contained view combining the verified diff with inline anchored
comments and an explicit section for orphaned or unplaced comments.

Only Python's standard library and `git` are required. It never writes to the
inspected packet and never requires the original author repository.

## Command-line usage

```sh
python3 projects/review-skein/review_view.py PACKET \
  [--format text|html] \
  [--resolution all|open|resolved] \
  [--state all|anchored|orphan] \
  [--context N] \
  [--max-file-bytes N]
```

Options:

- `PACKET`: path to an exported Skein packet directory.
- `--format`: `text` (default) for contextual terminal text, or `html` for a
  standalone static HTML document written to standard output.
- `--resolution`: filter comments by `all` (default), `open`, or `resolved`.
- `--state`: filter comments by `all` (default), `anchored`, or `orphan`.
- `--context`: lines of unchanged context around diff rows and inline comments
  (default `3`); `-1` renders complete files without collapsing unchanged spans.
- `--max-file-bytes`: per-blob byte limit enforced via `skein.BlobReader`
  (default `skein.DEFAULT_MAX_FILE_BYTES`).

When `--resolution` or `--state` filters comments, the summary reports both the
filtered count (`Showing M of N comments...`) and unfiltered totals
(`All comments: O open, R resolved; P orphan.`) so open or orphaned work is
never hidden silently.

## Python API

```python
from pathlib import Path
import review_view

text_report = review_view.render_packet(
    Path("path/to/packet"),
    output_format="text",
    resolution="all",
    state="all",
    context=3,
    max_file_bytes=skein.DEFAULT_MAX_FILE_BYTES,
)
```

Invalid arguments raise `ValueError`. Missing/symlinked packet files, corrupt
or mismatched `changes.bundle` vs `packet.json`, version-1 `comments.json`, or
blobs exceeding `max_file_bytes` raise `skein.SkeinError`, `OSError`, or
`UnicodeError`; CLI invocations print the error to `stderr`, write nothing to
`stdout`, and exit `1` without touching the packet directory.

## Security and rendering guarantees

- **Strict read-only packet handling:** the bundle is cloned into a temporary
  directory (`tempfile.TemporaryDirectory`), checked with `git bundle verify`
  and `git cat-file -e`, and compared against `packet.json["files"]`. Symlinked
  `packet.json`, `anchors.json`, `comments.json`, `changes.bundle`, or packet
  directories are rejected. Every `anchors.json` record must match the verified
  bundle's complete old/new line inventory: extra, missing, duplicate, or altered
  anchors fail before output. Anchor record order does not affect validity.
- **No silent comment loss:** any selected comment that is `state="orphan"` or
  whose anchor target `(commit, path, side, line)` does not match a rendered
  diff row is placed in `Orphaned and unplaced comments`, with its anchor,
  reason, optional `rebased_from` anchor, and body.
- **Distant comment visibility:** unchanged lines carrying an inline comment
  stay visible inside context windows even when far from any edit hunk.
- **Terminal & HTML safety:** text and HTML values pass through
  `comments_view._visible` to neutralize control/bidi sequences (such as
  `\u202e`). HTML output escapes all untrusted strings with `html.escape`, uses
  sequential `comment-N` DOM IDs to avoid collisions with fixed landmarks
  (`files`, `orphans`), emits zero JavaScript (`default-src 'none';
  style-src 'unsafe-inline'`), and passes `probe.audit` with zero errors or
  notices.
  Diff alignment uses original blob text; escaping occurs only when displaying
  rows, so a raw bidi character and its literal escape remain a changed line,
  with original line numbers and comment attachments preserved.

## Verification and honest boundaries

Verified by `python3 -m unittest discover -s projects/review-skein -v` (with
real Git repositories and removed source repositories in
`test_review_view.py`):

- Inline old-side, new-side, and multi-comment placement on replaced and
  unchanged lines, distant context windowing (`context=1` and `context=-1`),
  and non-dropping of unplaced anchored or orphaned comments.
- HTML determinism, escaping, `probe.audit(...) == []`, and `probe.transcript`
  accessibility checks.
- Filter summaries preserving totals and rejection of tampered `packet.json`,
  v1 `comments.json`, oversized blobs (`--max-file-bytes`), and symlinked
  `comments.json` with byte-identical packet preservation.
- Real exported control/bidi lines in both output formats, raw versus literal
  escape alignment, and altered anchor inventory rejection without packet writes.

Honest limits:

- Git commit hashes and bundle verification bind repository bytes, not human
  authorship or cryptographic signer identity.
- Static DOM checks (`probe.audit`) verify accessibility structure cleanly,
  which complements but does not replace live desktop/phone/screen-reader
  testing.
