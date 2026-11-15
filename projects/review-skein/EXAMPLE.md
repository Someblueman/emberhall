# Try Skein with an invented patch

This practice workspace is a small fixture corpus you can recreate locally. It
contains an author repository with three commits, two independent reviewer packet
copies and a revised packet. All text, identities and comments are invented.
No Emberhall history or personal repository is copied, and nothing is downloaded.
You need Python 3.10+ and Git 2.29+; run these commands from the source checkout root.

## Make a fresh workspace

Choose a new path in an existing parent directory. The examples below use a shell
variable so paths containing spaces work. Choose a different path for another run.

```sh
practice=/tmp/skein-practice
python3 projects/review-skein/example.py "$practice"
```

The generator refuses every existing output path, including an empty directory,
file or dangling symlink. A failure may leave its **new** directory partially
built for inspection. `example.json` is written last and marks completion; do not
use an incomplete workspace as a successful example. Existing data is never
removed or reused. Do not edit the new workspace while generation is running.

The generator ignores ambient Git repository, identity and global/system config
variables, disables hooks and signing for its Git processes, and fixes commit
dates, text and ref names. Two runs with the same Skein and Git versions produce
the same commit IDs and packet bytes. The `.git` directories and filesystem times
are ordinary local implementation details and are not byte-reproducible archives.

| Path | What to try |
| --- | --- |
| `author/` | Clean synthetic Git worktree with `base`, `feature` and `revised` branches; no remotes |
| `common/` | First patch with six common comments |
| `alice/`, `bob/` | Copies with conflicting greeting edits and one new note each; Bob resolves the door question |
| `merge-target/` | Untouched copy of the common packet; merge into this |
| `revised-packet/` | Revised patch, initially without comments; carry the merged discussion here |
| `example.json` | Commit IDs and the expected final comment states |

Open `common/review.html` directly in a browser to inspect the patch. The side-by-side
view shows a changed greeting/door, Unicode, a literal tab and a renamed-and-edited
file (`notes.txt` → `café.txt`). Each packet also carries its own ordinary Git bundle.

## Recover the first patch on another local path

```sh
python3 projects/review-skein/skein.py verify "$practice/common"
git clone --branch skein-head "$practice/common/changes.bundle" "$practice/reviewer-repo"
git -C "$practice/reviewer-repo" log --oneline --all
```

This clone reads only the local bundle. Its origin points at that bundle, rather
than at the author repository or a network service. `skein-base` and `skein-head`
are the bundle's branch names; `author/` uses the human-facing refs above. A bundle
lets you recover Git objects; it does not recover later comments stored alongside
it. Keep the packet files together when exchanging them.

## Merge two reviews

First ask for explicit conflict rejection:

```sh
python3 projects/review-skein/exchange.py merge "$practice/merge-target" \
  "$practice/alice" "$practice/bob" --base "$practice/common" --on-divergent reject
```

**Expected: exit 2**, naming `greeting`. Both reviewers edited that same ID
differently. The target comments stay unchanged; stop after this command if you
are running a shell with automatic exit-on-error and inspect the expected failure.
Then keep both variants:

```sh
python3 projects/review-skein/exchange.py merge "$practice/merge-target" \
  "$practice/alice" "$practice/bob" --base "$practice/common"
python3 projects/review-skein/comments_view.py "$practice/merge-target/comments.json"
```

There are now **nine comments**. The two greeting variants have deterministic
`greeting--divergent-…` IDs. The `door` question is resolved: Bob changed it while
Alice kept the common record, so `--base` lets that one-sided change reconcile.
Both independent reviewer notes survive. Only the target's `comments.json` changes.

## Carry the discussion onto the revision

```sh
python3 projects/review-skein/exchange.py carry "$practice/revised-packet" "$practice/merge-target"
python3 projects/review-skein/skein.py verify "$practice/revised-packet"
python3 projects/review-skein/comments_view.py "$practice/revised-packet/comments.json"
python3 projects/review-skein/exchange.py compare "$practice/merge-target" "$practice/revised-packet"
```

Inspect these outcomes rather than treating an exit code as the whole result:

- Both greeting variants move to new line 2; `door` moves to line 1 and stays resolved.
- `lantern` becomes an orphan because its text changed.
- `echo` becomes an orphan because its former line now says `signpost` and two
  matching `echo` lines remain. Skein refuses to guess which duplicate was intended.
- `base-note` stays on the unchanged base commit without inventing rebase history.
- The Unicode/tab comment remains anchored; the two new reviewer notes survive.

The result is **nine comments, two orphans (`echo`, `lantern`) and one resolved
comment (`door`)**. Orphans retain a reason and prior anchor. This is deliberately
a case where revision cannot automatically preserve every useful location.

To edit existing comments using labelled controls, generate a self-contained page:

```sh
python3 projects/review-skein/comment_editor.py page \
  "$practice/revised-packet/comments.json" "$practice/editor.html"
```

Open `editor.html` locally. Follow [EDITOR.md](EDITOR.md) to download and apply
edits; the page cannot save directly into the packet or add new comments.
Read-only HTML is also available via `comments_view.py --format html`. An example
or a markup audit is not a desktop, phone or screen-reader acceptance witness.

## What this lets you assess

For this small exchange, Skein adds a readable diff and comment merging to an
ordinary bundle, with no review server. Plain `git bundle` already transports the
commits; compare whether the extra packet files and CLI steps help your reviewer.
This recipe does not establish that Skein is easier than Gerrit, Radicle or your
existing workflow, or that a novice can use it unaided. Those require actual
outside-user comparison. See [EXCHANGE.md](EXCHANGE.md) for the merge contract,
[TRIAL.md](TRIAL.md) for independent interaction checks and [README.md](README.md)
for limitations, including sensitive reachable history when exporting real work.

To check the generator and this real CLI exchange:

```sh
python3 -m unittest discover -s projects/review-skein -p test_example.py -v
```

Generated repositories and bundles belong in your chosen temporary workspace;
they are not source artifacts to commit.
