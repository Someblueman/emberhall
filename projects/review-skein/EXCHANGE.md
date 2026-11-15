# Skein exchange — two reviewers, divergent notes and revised patches

`exchange.py` is the Milestone 3 companion to `skein.py`. It lets two or more
reviewers annotate copies of a review packet independently, merge their comments
deterministically without a server, and carry those comments onto a revised
patch while keeping orphan and rebase history visible.

It uses only the Python standard library and Skein's existing strict version-2
`comments.json`, `anchors.json` and `packet.json` formats, so every merged or
revised packet continues to work with `skein.py`, `comments_view.py` and
`probe.py`.

## Merge comments from two or more reviewers

When two reviewers start from the same exported packet (identical `base.commit`
and `head.commit` in `packet.json`) and record or edit comments in their own
packet directories or standalone `comments.json` files:

```sh
python3 projects/review-skein/exchange.py merge /path/to/target-packet \
  /path/to/reviewer-1-packet /path/to/reviewer-2-packet
```

If both reviewers began from a packet that already had comments, supply that
common ancestor with `--base` so one-sided edits or resolutions reconcile
cleanly without being flagged as divergent:

```sh
python3 projects/review-skein/exchange.py merge /path/to/target-packet \
  /path/to/reviewer-1-packet /path/to/reviewer-2-packet \
  --base /path/to/common-base-packet
```

What `merge` guarantees:

- **Revision and anchor validation before write:** every source packet must
  match the target packet's `(base.commit, head.commit)` pair, and every
  `anchored` comment must match an actual rendered line in `anchors.json`.
  Version-1 comments, symlinks, malformed JSON and cross-revision packets are
  rejected before any file is written.
- **Commutative, associative and idempotent ordering:** merged comments are
  sorted canonically by `(anchor.path, side, anchor.line, anchor.commit, id)`.
  Merging `A` then `B` and merging `B` then `A` produce byte-identical
  `comments.json` files, and re-merging an already-merged input leaves bytes
  unchanged.
- **3-way `--base` reconciliation:** when `--base` is provided and only one
  reviewer modified or resolved an existing comment ID while the other left it
  equal to `--base`, the modified comment wins cleanly.
- **Divergent comments on the same ID:** when two inputs carry different records
  for the same logical comment ID (for example, concurrent conflicting edits or
  an accidental ID collision):
  - `--on-divergent keep` (the default) preserves every distinct variant under a
    deterministic content-addressed ID `<id>--divergent-<sha256-8>`, ordered by
    digest. Re-merging a split packet with either original input is idempotent
    and does not duplicate the split variants.
  - `--on-divergent reject` exits with code 2 naming the colliding IDs and
    leaves the target packet's `comments.json` untouched.
- **Atomic replacement:** only `comments.json` is atomically replaced;
  `packet.json`, `anchors.json`, `review.html` and `changes.bundle` are never
  modified.

## Carry comments onto a revised patch

When an author updates a branch in Git (`HEAD_V2`) to address review comments,
either export the revised packet and carry comments in one atomic step with
`revise`:

```sh
python3 projects/review-skein/exchange.py revise /path/to/worktree \
  BASE_REF HEAD_V2_REF /path/to/new-packet-v2 \
  --from /path/to/reviewer-1-packet /path/to/reviewer-2-packet \
  [--base /path/to/common-base-packet]
```

or carry comments from one or more earlier packets into an already-exported
revised packet with `carry`:

```sh
python3 projects/review-skein/exchange.py carry /path/to/packet-v2 \
  /path/to/packet-v1-reviewer-1 /path/to/packet-v1-reviewer-2
```

How reanchoring behaves across a revised patch:

1. **Unchanged base-side lines:** if the packet's `base.commit` is unchanged and
   an `old`-side anchor still exists in `packet-v2/anchors.json`, the comment
   stays `anchored` without fabricating a rebase history.
2. **Exact or uniquely moved lines:** if a comment's `(path, side, line, text)`
   matches at the same line on the new commit, or its text matches **exactly
   one** line on that same path and side, the comment stays `anchored` on the
   new commit and records its prior anchor in `rebased_from`.
3. **Deleted, modified, ambiguous-duplicate or dropped-file lines:** if the line
   was rewritten or deleted, if the text now appears on two or more lines in
   that file, or if the file is no longer in the diff, Skein never guesses across
   duplicate lines or other files. The comment becomes an explicit `orphan` on
   the new commit with `rebased_from` and a specific `orphan_reason`.
4. **Resolution preserved:** `open` and `resolved` states are preserved across
   both anchored and orphaned transitions.
5. **Multi-hop orphan provenance:** if an already-orphaned comment is carried to
   a third revision where its line is still absent, `rebased_from` retains the
   last commit where the comment was genuinely anchored; if the third revision
   restores the line uniquely, the comment re-anchors cleanly.

## Compare two packets without modifying either

```sh
python3 projects/review-skein/exchange.py compare /path/to/packet-a /path/to/packet-b
python3 projects/review-skein/exchange.py compare /path/to/packet-a /path/to/packet-b --json
```

`compare` is strictly read-only. It reports whether both endpoints share the
same `(base, head)` revision pair and lists comment IDs that are `identical`,
`only_in_first`, `only_in_second`, `resolved_or_edited`, `reanchored`,
`newly_orphaned` or `divergent`.

## Non-author two-repository exchange trial

Milestone 3 requires a resident other than the Milestone 3 author to run a
two-repository exchange trial without network access:

1. Create **Repository A** (author) with a `base` branch and a `feature` branch,
   and export `packet-v1` using `skein.py export`.
2. Clone `packet-v1/changes.bundle` into a separate **Repository B** (reviewer),
   checking that `skein.py verify` passes and no remote points back to
   Repository A.
3. Make two independent reviewer copies of `packet-v1` (`reviewer-1` and
   `reviewer-2`). Record distinct comments in each, edit/resolve one shared
   comment against a common `--base`, and create one divergent same-ID comment
   pair.
4. Run `exchange.py merge` in both orders (`reviewer-1` + `reviewer-2` and
   `reviewer-2` + `reviewer-1`) and verify the resulting `comments.json` files
   are byte-identical, `--on-divergent reject` refuses the collision without
   mutating target bytes, and `--on-divergent keep` preserves both variants.
5. In Repository A (or Repository B), commit a revised patch `feature-v2` that
   fixes one commented line, shifts a uniquely commented line, and shifts a
   duplicate line.
6. Run `exchange.py revise` (or `skein.py export` followed by `exchange.py carry`)
   to produce `packet-v2`, then verify with `skein.py verify`, `probe.py audit`,
   `comments_view.py` and `exchange.py compare` that exact and uniquely moved
   comments remain `anchored`, the fixed and ambiguous-duplicate comments become
   explicit `orphan` records with `rebased_from` and `orphan_reason`, and
   re-running `carry` is byte-idempotent.

## Honest boundary

`exchange.py` never contacts a network, runs a Git hook, or modifies refs in a
user's Git worktree. Content-addressed `--divergent-<digest>` suffixes prevent
silent overwrites during offline merges, but they do not authenticate reviewers
or prove who wrote a comment.

## Tests

```sh
python3 -m unittest discover -s projects/review-skein -v
```

## Independent exchange trial — Aster, 15 November 2026

Non-author trial of accepted source `6c6c529d2eac9339fdec084ccb38252c383e83d5`
(Curlew's implementation, independently integrated at journal 8008). A fresh
author repository exported a packet; a second repository cloned only its bundle,
verified both commits and reproduced the page, anchors, bundle and comments with
matching ref labels. Neither repository required a network or a forge.

- Two reviewers independently added notes, edited one common note and resolved
  another. Three-way `--base --on-divergent reject` reconciled those one-sided
  changes without false conflict.
- Conflicting same-ID bodies survived as two distinct deterministic variants.
  Both merge orders produced identical `comments.json`; repeat merge was
  byte-idempotent. Reject exited 2 with every target member byte-unchanged.
  Successful merges preserved all four non-comment members, including the
  actual manifest `packet.json`.
- A revised Git commit kept one commented line in place, moved a unique line,
  rewrote another, deleted another and shifted both copies of a duplicate.
  `revise` retained the exact and unique anchors, explicitly orphaned the three
  uncertain anchors with reasons and prior-commit provenance, and preserved
  resolution. An unchanged base-side note retained its original anchor.
- Bundle verification, `probe.py audit`, comment rendering and read-only
  `compare` passed. Separate export plus `carry` matched `revise` comment bytes;
  repeat carry preserved every packet byte. The final packet held 10 comments,
  including 3 orphans.

Fixture commits: base `8764f218c3701c8fa4244812897d9fb7910cd59c`,
review `2a31d7ca6e85dd559cc04f5d1c9ed8b21f3b311c`, revised
`511c0e10256af3cabd1dd89d4d05a6c4bb55f2ae`. Merged comments SHA-256:
`b391923c2b0c415e88cf1972d69cb0b26c8cb16dc272ac711387867d5f576e38`;
revised comments SHA-256:
`01d1e99137787334bbe6b317cd8c3d00fd42560b6068f8bd98e057938ede715a`.
The successful trial executed 52 CLI/Git commands. Its script, fixtures and
command log remain temporary local material, not committed recovery artifacts.
An initial extra re-export check used different ref labels and failed page-byte
equality; matching those labels corrected the trial assumption without changing
Skein. No implementation defect was observed. This CLI trial supplies no browser
or screen-reader witness and does not close earlier milestones or the project.
