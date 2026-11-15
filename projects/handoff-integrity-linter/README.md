# Handoff integrity checker

Check an explicit draft artifact list against files in a supplied workspace.
Python 3.10+, POSIX and the standard library only. Git is optional unless a claim
requires it. No house runtime, network, journal access or packages are needed.

From the Emberhall repository root:

```sh
python3 -B projects/handoff-integrity-linter/check_handoff.py . projects/handoff-integrity-linter/example.json
python3 -B -m unittest discover -s projects/handoff-integrity-linter -v
```

`example.json` contains actual SHA-256, byte-count and clean-state claims for the
repository's root README at this build. The first command checks that real file.
A later README edit should fail this frozen example; compare the reported actual
values to the intended artifact before revising a claim. The checker never
rewrites a draft to make it pass.

## Claim format

Save UTF-8 JSON, with exactly these top-level keys:

```json
{
  "version": 1,
  "artifacts": [
    {"path": "notes/handoff.md", "bytes": 42, "git": "dirty"},
    {"path": "README.md"}
  ]
}
```

`artifacts` must be nonempty. Every entry requires `path`. Optional fields are:

| Field | Meaning |
| --- | --- |
| `sha256` | Exact 64-character lowercase hexadecimal SHA-256 of file bytes |
| `bytes` | Exact nonnegative integer byte count; booleans are rejected |
| `git` | Expected per-file state, either `clean` or `dirty` |

A path-only entry still verifies that the file exists, is safely readable and is
regular. Every successful file read reports its actual hash and byte count.
All fields present in a claim must match. Unlisted workspace files are outside
the claim list and do not make a listed clean file dirty.

Paths use repository-relative `/` separators. Absolute paths, empty or dot/dotdot
components, backslashes, colons, control characters, Git metadata, duplicate
paths, duplicate JSON keys, unknown fields, invalid types and unknown versions
are rejected. Symlinks in artifact paths (including parent components), FIFOs,
directories and other nonregular artifacts fail. Files are opened relative to a
workspace descriptor with no-follow flags; a changed file detected while reading
fails. Spaces, Unicode, brackets, stars and leading dashes are literal names.

The supplied workspace root is canonicalized, so caller aliases such as macOS
`/tmp` work. Artifact paths are never canonicalized through symlinks. The claim
file itself must also be a regular file, not a symlink or FIFO; its supplied
parent directory is canonicalized like the workspace root.

## Results and exit status

The CLI emits one JSON object. `ok` is true only when every claim passes.
`artifacts` preserves input order, with each entry's observed `sha256`, `bytes`,
`git`, `errors` and `ok`. Unsafe or missing files have no digest or byte count.

- **0:** all claims passed.
- **1:** a file was unsafe, missing or unreadable, an exact claim mismatched,
  or a required Git state was unavailable.
- **2:** malformed JSON/schema, unavailable workspace/input, or unsupported
  platform; an `error` object is emitted on stderr.
- **130:** interrupted.

`git_available` reports whether repository discovery succeeded. Git must discover
exactly the supplied workspace as its top-level; a subdirectory or a non-Git
folder cannot silently inherit the parent's repository. Each artifact reports
`git: "unavailable"` plus a `git_reason` when Git discovery or status fails.
Without a `git` claim, that unavailability is informational and byte checks may
still pass. It never satisfies a `clean` or `dirty` claim.

`clean` means Git tracks the exact path and porcelain status reports no change
for it. Staged changes, unstaged changes, untracked files and ignored files are
`dirty`. A deleted artifact fails existence even if Git calls its deletion dirty.
Renamed destinations are dirty; old paths still have to exist if listed.
This is Git's view: index flags such as assume-unchanged/skip-worktree and Git's
stat cache can hide changes. Use exact SHA-256 claims to check intended bytes.

Git uses literal pathspecs and NUL-delimited output. The checker ignores inherited
`GIT_*` repository/index overrides, disables optional locks/index refresh writes
and filesystem-monitor helpers, and only runs `rev-parse`, `ls-files` and
`status`. Lazy fetching is disabled. A per-command Git timeout is reported as
unavailable. It never runs
add, commit, checkout, hooks, external diff programs, or any house operation.

Use a quiescent workspace. File reads and Git status are separate observations,
not an atomic filesystem/Git snapshot; concurrent renames or writes can invalidate
a result after observation. Reads may update filesystem access times. The tool
does not infer assertions from prose, establish authorship, verify journal
receipts/ancestry, attest a clean whole repository, or authenticate a draft.
Independent source review and a separate real-workspace acceptance check remain
project closure requirements; a passing self-check is not either one.
