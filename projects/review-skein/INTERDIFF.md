# Revision Interdiff (`interdiff.py`)

`interdiff.py` compares two exported Review Skein packets (`PACKET_V1` and
`PACKET_V2`) strictly read-only, rendering the head-to-head diff (`head_v1 ->
head_v2`) alongside comment transitions (`exchange.compare_packets`), without
needing the author's repository or a network service.

## Command-line usage

```sh
python3 projects/review-skein/interdiff.py PACKET_V1 PACKET_V2 \
  [--format text|html|json] \
  [--resolution all|open|resolved] \
  [--state all|anchored|orphan] \
  [--path PATH] \
  [--search TEXT] \
  [--only-commented] \
  [--context N] \
  [--max-file-bytes N]
```

Options:

- `PACKET_V1`: path to the earlier exported Skein packet directory.
- `PACKET_V2`: path to the revised exported Skein packet directory.
- `--format`: `text` (default), `html` (standalone zero-JS page), or `json`
  (ASCII-safe summary plus selected comment records with origin and transition).
- `--resolution`: filter comment entries by `all` (default), `open`, or `resolved`.
- `--state`: filter comment entries by `all` (default), `anchored`, or `orphan`.
- `--path`: filter revision-changed files and comment entries to an exact path or
  directory prefix (repeatable).
- `--search`: filter comment entries by case-insensitive substring across ID,
  body, path, anchor text, `rebased_from`, `orphan_reason`, origin, or transition.
- `--only-commented`: show only revision-changed files that have matching inline
  comments.
- `--context`: lines of unchanged context around diff rows and inline comments
  (default `3`), or `-1` for full files.
- `--max-file-bytes`: per-blob byte limit enforced via `skein.BlobReader`
  (default `skein.DEFAULT_MAX_FILE_BYTES`).

## How comments and base shifts are shown

- **Base-commit honesty:** if `base_v1 == base_v2`, the summary marks the base
  unchanged between revisions. If `base_v1 != base_v2` (a rebased branch), both
  bases are named and the summary states that the `V1 -> V2` diff includes
  upstream base changes.
- **Inline placement:**
  - Anchored `V2` head comments on revision-changed files appear inline on their
    `V2` line.
  - Newly orphaned `V2` comments whose `rebased_from` points to a `V1` head line
    in a revision-changed file appear inline on that `V1` line so a reviewer can
    immediately inspect the change that orphaned them.
  - `V1-only` comments (not yet carried into `V2`) on revision-changed files
    appear inline on their `V1` line marked `V1-only`.
  - Divergent logical-ID groups keep every distinct older and newer record,
    including when the variant-ID sets differ or the same exact ID has different
    content. Older records are labelled `V1 (divergent)` and placed using their
    V1 anchors; newer records are labelled `V2 (divergent)`. An identical record
    shared by both packets appears once, as V2. These older records are not
    described as `V1-only`, since the logical comment also exists in V2.
    Resolution, state, path and search filters apply separately to each record.
- **Explicit buckets (no silent drops):**
  - Comments on files that were unchanged between `V1` and `V2` appear in
    *Comments on files unchanged between revisions*.
  - `base`-side comments (`side == "old"`) appear in *Base-side comments*.
  - Remaining orphaned or unplaced comments appear in *Orphaned and unplaced
    comments*.

JSON's `comments` array contains each selected record as
`{"origin": "V1", "transition": "divergent", "comment": {...}}`, with the
complete normal Skein comment object. Entries sharing an ID remain separate
array elements. `placements.inline_v1_divergent` names older divergent comments
placed on V1 lines; `inline_v1_only` retains its separate meaning. Transition
counts come directly from `exchange.compare_packets`: a divergent logical group
counts once even when it contains several visible records.

## Security and verification guarantees

- Both packets are verified read-only (`packet.json`, `anchors.json`,
  `comments.json`, `changes.bundle`, symlink checks, and `--max-file-bytes`)
  before any output is written.
- Text and HTML outputs pass untrusted strings through `comments_view._visible`
  to neutralize control/bidi characters without changing diff semantics.
- HTML output emits zero JavaScript (`default-src 'none'; style-src
  'unsafe-inline'`) and passes `probe.audit(...) == []`.
- Verified by real-Git and repository-deleted bundle tests in
  `test_interdiff.py`.

The original interdiff implementation is Yarrow's preserved contribution
`c7c50932`; Sorrel recovered its exact three artifacts before repairing the
divergent-comment omission found in Bracken's independent review.
