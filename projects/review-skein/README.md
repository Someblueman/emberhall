# Review Skein — local-first review packets

Skein is a **local-first code-review packet**: an escaped static side-by-side
review, the matching ordinary Git bundle, and comments anchored to exact lines.
It is for an occasional reviewer with no forge, account, daemon or network. It
is not another Git host or identity system.

New here? Run the invented practice workspace in [EXAMPLE.md](EXAMPLE.md)
first; it exercises the main workflow commands on disposable data. The pieces:

| Piece | What it does | Guide |
| --- | --- | --- |
| `skein.py` | Export/verify a packet; add, edit, resolve comments | this file |
| `comments_view.py` | Read comments as terminal text or offline HTML | [COMMENTS.md](COMMENTS.md) |
| `comment_editor.py` | Edit bodies/resolution in a self-contained offline page | [EDITOR.md](EDITOR.md) |
| `exchange.py` | Merge several reviewers' comments; carry them onto a revised patch | [EXCHANGE.md](EXCHANGE.md) |
| `review_view.py` | Read the verified diff with comments inline, as text or offline HTML | [REVIEW_VIEW.md](REVIEW_VIEW.md) |
| `archive.py` | Pack, inspect, and safely unpack verified `.tar.gz` packet archives | [ARCHIVE.md](ARCHIVE.md) |
| `recovery.py` | Diagnose and rebuild a damaged packet; salvage drifted comments | [RECOVERY.md](RECOVERY.md) |
| `comparison.py` | Measure a fixture against raw `git bundle`; outline unbenchmarked Gerrit and Radicle alternatives | [RECOVERY.md](RECOVERY.md) |
| `probe.py` | Audit/transcribe a packet's markup without a browser | [PROBE.md](PROBE.md) |
| `example.py` | Generate a reproducible invented practice workspace | [EXAMPLE.md](EXAMPLE.md) |

Milestones 1–3 are built, reviewed, and closed in the project record (packet and
anchors at 8577; limited milestone 2 phone/desktop reading and editing pass
closed by the owner's recorded assessment at 12546, as [TRIAL.md](TRIAL.md)
itself notes milestone 2 is not closed by a limited pass alone; non-author
two-repository exchange at 12553). Milestone 4 adds the
[EXAMPLE.md](EXAMPLE.md) practice workspace, [RECOVERY.md](RECOVERY.md) damage
diagnosis/rebuild and a measured fixture comparison against raw `git bundle`,
plus an overview of Gerrit and Radicle, which were not run or benchmarked;
the read-only annotated view in [REVIEW_VIEW.md](REVIEW_VIEW.md); and
the independent recipe/recovery trials in [FINAL_REVIEW.md](FINAL_REVIEW.md)
and [MILESTONE_4_TRIAL.md](MILESTONE_4_TRIAL.md). In [TRIAL.md](TRIAL.md) and
[TRIAL_EDITOR.md](TRIAL_EDITOR.md), real keys and measured phone/desktop
layouts passed under the house viewer, while browser zoom and screen-reader
speech remain `NOT RUN` and uncertified.

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

Milestone 2 makes that static page usable without a mouse or
sight of its colours: the first focusable element skips to the changed-files
index, each file section is labelled by its heading, every diff row names its
change kind (`Added`/`Removed`/`Changed`/`Unchanged`) as visually-hidden text
rather than colour alone, links get a visible focus outline, and tables scroll
horizontally on narrow screens instead of being squeezed. Comment/resolution
editing is available through the CLI below, the reader in
[COMMENTS.md](COMMENTS.md) and the offline editor page in
[EDITOR.md](EDITOR.md). Closing milestone 2 rests on the recorded
independent non-author try and the owner's assessment of it.
Use [TRIAL.md](TRIAL.md) for measured phone fit,
real key observations and honest limits; use [TRIAL_EDITOR.md](TRIAL_EDITOR.md)
for composition, editing and the exported-envelope roundtrip. An unknown target,
unpictured control or unmeasured layout stays `NOT RUN` / `NOT RUN / uncertain`.
A full accessibility try additionally requires actual browser zoom and speech;
neither a DOM transcript nor source tests establish those experiences.

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
no automatic guess across duplicate lines. Milestone 3 builds the working
multi-reviewer merge and revised-patch carry on this model — see
[EXCHANGE.md](EXCHANGE.md).

## Edit, resolve and reopen a comment

```sh
python3 projects/review-skein/skein.py edit-comment /path/to/packet \
  --id reviewer-1-note-1 --body "Revised question after reading the second file."
python3 projects/review-skein/skein.py resolve-comment /path/to/packet --id reviewer-1-note-1
python3 projects/review-skein/skein.py reopen-comment /path/to/packet --id reviewer-1-note-1
```

New comments start with `resolution: "open"`. Resolution is separate from the
anchor's `state` (`anchored` or `orphan`): resolving an orphan preserves its
missing-line reason and rebase history. Editing preserves the ID and anchor,
and resolving or reopening preserves the body. The Python
`update_comment(packet, identifier, *, body=None, resolution=None)` API supports
the same operations. Unknown IDs and invalid bodies or resolutions fail before
writing; updates atomically replace only `comments.json`. Use one writer at a
time on a single packet copy; to combine several reviewers' copies, merge them
with `exchange.py` ([EXCHANGE.md](EXCHANGE.md)). These commands do not change
the static HTML; for form-based editing, generate the separate offline editor
page in [EDITOR.md](EDITOR.md), whose downloaded edits are validated and
applied atomically by `comment_editor.py apply`.

**Saved comments have a new version.** `comments.json` now uses version 2 with a
required `resolution` field. The packet manifest, anchors and Git bundle keep
their existing formats. For a packet exported by milestone 1, explicitly migrate
its comments before verifying, adding or editing comments with this exporter:

```sh
python3 projects/review-skein/skein.py migrate-comments /path/to/old-packet
```

Migration validates the entire strict version 1 document before atomically
replacing it with version 2, setting every existing comment to open. It preserves
IDs, bodies, anchors, orphan reasons and rebase history, and changes no other
packet member. Repeating migration on valid version 2 comments leaves the bytes
unchanged. Malformed records, duplicate keys/IDs and unsupported versions are
rejected without rewriting the file. Older Skein readers cannot read version 2
comments; keep a copy of the original packet if those readers must still use it.

## Merge reviewers and carry comments to a revised patch

```sh
python3 projects/review-skein/exchange.py merge /path/to/target-packet \
  /path/to/reviewer-1-packet /path/to/reviewer-2-packet
python3 projects/review-skein/exchange.py revise /path/to/worktree \
  BASE_REF NEW_HEAD_REF /path/to/new-packet --from /path/to/old-packet
```

Merging is deterministic and commutative for packets of the same revision;
`--base` reconciles one-sided edits, and genuinely divergent same-ID comments
are kept as both variants or rejected without touching the target, by flag.
`carry`/`revise` reanchor comments onto a revised patch, turning
modified/deleted/duplicate-line anchors into explicit orphans. Full semantics,
flags and the recorded non-author two-repository trial are in
[EXCHANGE.md](EXCHANGE.md). To just read what reviewers said, use
`comments_view.py` ([COMMENTS.md](COMMENTS.md)).

## Read the annotated packet, and recover a damaged one

```sh
python3 projects/review-skein/review_view.py /path/to/packet
python3 projects/review-skein/recovery.py diagnose /path/to/damaged-packet
python3 projects/review-skein/recovery.py rebuild /path/to/damaged-packet /path/to/new-packet
```

`review_view.py` renders the verified diff with its comments inline (orphans
in their own section) as terminal text or offline HTML; it never writes to
the packet — see [REVIEW_VIEW.md](REVIEW_VIEW.md). `recovery.py` diagnoses a
packet read-only (exit 0 healthy, 1 recoverable, 2 unrecoverable) and rebuilds
the derived files byte-for-byte into a new directory from `changes.bundle` or
a local repository, preserving valid comments verbatim — see
[RECOVERY.md](RECOVERY.md), which also records the measured comparison
against raw `git bundle`, Gerrit and Radicle and when those are the better
tool.

## Test and independent trial

The suite creates real temporary Git repositories and checks branch/tag and
object identity, a cloneable full bundle, deterministic re-export, HTML escaping,
renames, Unicode, tabs, duplicate lines, missing anchors and rebase orphans.
It also exercises tracked/staged/untracked dirt, ambiguous refs, symlinks,
unsafe paths, binary/non-UTF-8/oversized blobs, CLI comment editing/resolution,
explicit version 1 migration, rejected-update byte preservation and malformed JSON:

```sh
python3 -m unittest discover -s projects/review-skein -v
```

No package installation or network is used. The suite also covers the comment
viewer/editor, deterministic merge/carry/revise, the annotated packet view,
packet recovery/rebuild and the example generator.
Beyond tests, milestone 3's exchange has a recorded non-author two-repository
trial ([EXCHANGE.md](EXCHANGE.md)), while milestone 2's independent
non-author view-based try of actual keys and measured layout is recorded as a
limited pass, with browser zoom and speech `NOT RUN`; a full real-browser and
screen-reader try remains the stronger evidence ([TRIAL.md](TRIAL.md)). The
packet used for that try is the mixed-change page at
`sample/milestone-2-mixed/review.html` (published at
`https://someblueman.github.io/emberhall/projects/review-skein/sample/milestone-2-mixed/review.html`,
base `f730e964e18e0245862f09f7e0662ab14775e8bd`, head
`7118f31b4d6d4ca429946929d95d9b3d6149f99a`); the older all-added sample
under `sample/milestone-2/` remains an alternate. Neither is an assertion
made by this README.

## Outside-user recipe (your own repository)

Run from the Skein source checkout with Python 3.10+ and Git 2.29+. Start with a
clean repository whose committed branches are `main` (base) and `feature` (patch).
Substitute your own refs if needed. Choose a new review workspace outside that
repository; paths may contain spaces. The bundle includes reachable history:
inspect what you intend to share before transferring it.

Create the workspace, export an untouched author baseline, and give the reviewer
a separate copy. In a real exchange, carry that entire copy to the other machine;
the local copy below rehearses the same packet boundary without network access.
Open the reviewer's `review.html` locally after verifying it.

```sh
repo="/absolute/path/to/your/repository"
review="/absolute/path/to/new/review-workspace"
mkdir "$review"
python3 projects/review-skein/skein.py export "$repo" main feature "$review/original"
cp -R "$review/original" "$review/reviewer"
python3 projects/review-skein/skein.py verify "$review/reviewer"
git clone --branch skein-head "$review/reviewer/changes.bundle" "$review/clone"
```

This walkthrough uses the **CLI comment path** throughout. Read the patch and
choose an existing new-side path and line from `anchors.json`; `app.py` line 3
below is an example to replace for your patch. The cloned branch supplies the
full head commit ID. Choose a unique comment ID and write your actual question.
The command saves directly to the reviewer's `comments.json`; verify and read it
before returning all five packet files to the author.

```sh
head_commit=$(git -C "$review/clone" rev-parse HEAD)
python3 projects/review-skein/skein.py comment "$review/reviewer" \
  --id rev-1 --commit "$head_commit" --path app.py --side new --line 3 \
  --body "Should empty names raise ValueError?"
python3 projects/review-skein/skein.py verify "$review/reviewer"
python3 projects/review-skein/comments_view.py "$review/reviewer/comments.json"
```

For the alternative browser composer, follow the complete [EDITOR.md workflow](EDITOR.md):
create the page, add comments, download or copy/save its JSON, check it, then apply
it to the matching packet. Generating a compose page alone does not save a comment.
That browser/download path is separate from this CLI walkthrough.

Back with the author, make a new merge target from the untouched original before
merging the returned reviewer copy. A second reviewer can return another copy;
[EXCHANGE.md](EXCHANGE.md) explains shared-base and divergent-ID handling.

```sh
cp -R "$review/original" "$review/merged"
python3 projects/review-skein/exchange.py merge "$review/merged" "$review/reviewer"
```

Now make and commit your revised patch on `feature`, keeping `main` unchanged and
the worktree clean. Carry the returned comment onto a new packet and inspect it.
A uniquely moved line is reanchored; changed or ambiguous text becomes an explicit
orphan rather than silently landing on another line.

```sh
python3 projects/review-skein/exchange.py revise "$repo" main feature "$review/revised" --from "$review/merged"
python3 projects/review-skein/skein.py verify "$review/revised"
python3 projects/review-skein/review_view.py "$review/revised"
```

To rehearse recovery, damage only a disposable copy. The diagnosis below is
**expected to exit 1**, saying `status=recoverable`; inspect that result before
continuing, especially if your shell stops on nonzero exits.

```sh
cp -R "$review/revised" "$review/damaged"
rm "$review/damaged/review.html"
python3 projects/review-skein/recovery.py diagnose "$review/damaged"
```

Rebuild into another new directory. Both comparisons should print nothing:
the page is reconstructed byte for byte and the returned comments are preserved.
The damaged copy remains untouched by recovery.

```sh
python3 projects/review-skein/recovery.py rebuild "$review/damaged" "$review/rebuilt"
python3 projects/review-skein/skein.py verify "$review/rebuilt"
cmp "$review/rebuilt/review.html" "$review/revised/review.html"
cmp "$review/rebuilt/comments.json" "$review/revised/comments.json"
```

When only commits need to travel and you do not need reanchored comments, raw
`git bundle` is smaller in the measured fixture ([RECOVERY.md](RECOVERY.md)).
This recipe's actual CLI blocks are exercised on a fresh invented repository by
`test_outside_recipe.py`; that is not a novice, browser-download or general
usability comparison. Final milestone acceptance remains the project owner's
decision after independent review.

## Honest boundary

Skein has no authentication, confidentiality, signatures, live service or
patch application; it carries and merges review comments, and applying the
reviewed change remains ordinary Git work in your own repository. Hashing binds bytes,
not people. A bundle can contain copyrighted or sensitive history, so share it
only with intended reviewers. `git bundle` and static HTML do not make a hostile
Git repository or packet safe; use a trusted local fixture for a first try.
Viewer experience is claimed only where a [TRIAL.md](TRIAL.md) try was actually
performed and recorded. Only executed input with an observed outcome supplies
keyboard evidence. Unmeasured phone geometry remains `NOT RUN / uncertain`;
missing visual coverage remains uninspected, and browser zoom and screen-reader
speech remain `NOT RUN` under the viewer.
