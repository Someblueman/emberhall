# Review Skein — milestone 1: packet and anchors

Skein is a **local-first code-review packet**: an escaped static side-by-side
review, the matching ordinary Git bundle, and comments anchored to exact lines.
It is for an occasional reviewer with no forge, account, daemon or network. It
is not another Git host or identity system.

## Export and read a packet

From a clean, non-bare Git worktree:

```sh
python3 projects/review-skein/skein.py export /path/to/worktree BASE_REF HEAD_REF /path/to/new-packet
```

`BASE_REF` and `HEAD_REF` may name branches, tags or committed object IDs. Skein
resolves each to an immutable full commit ID. It refuses ambiguous short names,
uncommitted/index/untracked changes, an existing output path and output inside
the worktree. The new directory contains:

- `packet.json` — version 1, the two original refs and immutable commit IDs,
  changed-file status and line counts;
- `review.html` — a static escaped side-by-side diff with no JavaScript,
  external assets or network access;
- `anchors.json` — old/base and new/head line text used for comment anchoring;
- `comments.json` — initially empty, versioned comments;
- `changes.bundle` — an ordinary **full**, cloneable Git bundle with complete
  history reachable from the selected base and head. It has no bundle
  prerequisites and does not add unrelated refs.

Only regular UTF-8 text file blobs are rendered. Symlinks, submodules, binary or
non-UTF-8 files, unsafe/nonportable paths and changed blobs over 256 KiB are
rejected with specific errors. The optional `--max-file-bytes N` changes that
per-blob limit. A packet with many or large total changes can still be large;
this first milestone does not pretend otherwise.

Open `review.html` directly in a browser. Its Content Security Policy forbids
external resources. A console-only reader can inspect the JSON directly. Keep
the five files together when carrying the packet.

## Verify the carried Git bytes

```sh
python3 projects/review-skein/skein.py verify /path/to/packet
```

Verification parses the versioned JSON, clones `changes.bundle` into a fresh
local temporary directory, runs `git bundle verify` there, and checks that both
recorded commit IDs exist. It does not trust a running service or require the
original worktree. The comparison can be reproduced by exporting the same clean
refs twice: the initial five files are byte-identical. Editing comments is, of
course, a later change to `comments.json`.

Git's checks establish object consistency, **not authorship**. This command
verifies the bundle and schema; it does not authenticate a person, prove the
HTML was produced by a particular exporter, or detect every malicious packet.
Use a trusted channel or compare a fresh deterministic export when that matters.

## Record a comment offline

Choose a line represented in `anchors.json`, then run, for example:

```sh
python3 projects/review-skein/skein.py comment /path/to/packet \
  --id reviewer-1-note-1 --commit FULL_HEAD_COMMIT_ID \
  --path src/example.py --side new --line 12 \
  --body "Could this failure preserve the original path?"
```

`--side old` addresses a base-side line and `--side new` a head-side line. A
comment must use the packet's base or head commit, an existing rendered path and
line, a nonempty body and a unique safe ID. Comments never silently move to an
another file or unrelated line. Data classes and `dumps_comments` /
`loads_comments` provide strict JSON round trips; duplicate JSON keys and IDs are
invalid.

The `reanchor(comment, new_commit, available_anchors)` API supports a later
rebase: exact path/side/line/text wins, otherwise one unique text match on that
same path and side can move the anchor. Missing or duplicate matches become an
explicit `orphan` with a reason and `rebased_from` history. There is deliberately
no automatic guess across duplicate lines. Milestone 1 exposes this model for
round-trip/orphan behavior; rebase import and multi-reviewer merge are later
work, not a working merge feature.

## Test and independent trial

The suite creates real temporary Git repositories and checks branch/tag and
object identity, a cloneable full bundle, deterministic re-export, HTML escaping,
renames, Unicode, tabs, duplicate lines, missing anchors and rebase orphans.
It also exercises tracked/staged/untracked dirt, ambiguous refs, symlinks,
unsafe paths, binary/non-UTF-8/oversized blobs, CLI comments and malformed JSON:

```sh
python3 -m unittest discover -s projects/review-skein -v
```

No package installation or network is used. The project milestone additionally
requires someone other than the implementation author to export a fixture,
open its HTML without network, verify that the bundle clones, and record one
comment. That independent try is acceptance evidence for the milestone, not an
assertion made by this README.

## Honest boundary

Milestone 1 has no authentication, confidentiality, signatures, live service,
comment merge, patch application or automatic rebase import. Hashing binds bytes,
not people. A bundle can contain copyrighted or sensitive history, so share it
only with intended reviewers. `git bundle` and static HTML do not make a hostile
Git repository or packet safe; use a trusted local fixture for this first try.
