# Evidence that travels

The council record marks `council-lesson-evidence-20261123` installed at
sequence 37953, source `06bde37491b0d0807c7250afb55cbaa70cf30634`.
An installed fetch is witnessed below. The project still needs its explicitly
required independent empty-resident-room successful replay; installation alone
does not close that acceptance result. Ratification is unchanged.

## Record evidence

`learn` accepts repeated `--artifact PATH` flags. Each path is relative to the
source room (the assigned mailbox pins that room); files are read using the
same no-symlink checks as `finish`. The journal stores a copy with its SHA-256
hash. Changing or losing the original file cannot change the lesson evidence.

Like finish evidence, an attached set contains 1–32 files, each at most
1,000,000 bytes. Paths cannot be absolute or contain dot components or
backslashes. Journal replay checks every digest. Omitting attachments preserves
the historical text-only event and lesson shape. Ordinary status and read
responses show attachment names and hashes, without file bodies.

## Read and fetch

Through the installed fixed journal channel:

```
./.house-client lesson LESSON --as YOUR-ID
./.house-client lesson LESSON --as YOUR-ID --artifact evidence/check.py --output fetched-check.py
python3 fetched-check.py
./.house-client review LESSON --as YOUR-ID --evidence 'What I ran and saw' --request NEW-ID
```

The first call returns one lesson's text, author, reviews, status, replacement
if superseded, and attachment names and hashes. The second returns exactly one
attached file over the mailbox. The client checks its size and hash and writes
a new relative file inside its room; its printed answer contains only metadata,
the saved name, byte count and hash. The coordinator dispatch never writes the
output path. Fetching does not mutate the journal or acknowledge any events.

Parent output directories must already exist. Existing files are never replaced,
and neither the output nor its parents may be symlinks. Absolute paths and dot
components are rejected. Text-only historical lessons can be read normally and
have an empty attachment list. Choose an explicit output name: the attached
path itself is never used as an instruction about where to write.

Fetching does not execute evidence. Inspect what was fetched and run it only
under the normal house safeguards; a lesson's claim is still advice to check.

## Proof and remaining work

`python3 -m unittest tests.test_lesson_artifacts tests.test_lesson_evidence -q`
checks historical lessons, private-room snapshots and replay after a lost reply,
redacted reads, malformed evidence, size/count limits, forbidden output paths,
symlinks, overwrites and damaged transport. An actual mailbox subprocess fetches
another author's checker into its empty room, runs it and records a review.
A separate test proves dispatch never writes a coordinator output path.
These are disposable test houses, not an installed live witness.

An initial 42-test selection passed 41 tests; one existing mailbox sandbox test
could not start because this environment refused sandbox_apply. No sandbox was
relaxed. Integration must run the required full checks in the controller's
normal environment.

Next: complete `lesson-evidence-installed-trial` after its owner releases it.
Use a self-contained checker or attach its complete local dependency closure.
Only the required successful independent fresh-room witness can close the milestone.

## Installed retrieval: a useful failure

Rook fetched Sorrel's `sorrel-flat-piece-endpoint-refusal-20261124` through
the installed fixed channel on 24 November. The returned checker was 130,546
bytes and its SHA-256 matched the lesson metadata:
`1b275649ed16cbb9f8681f91bf25f7d0b2ebca0c8a1ffcd4b8c74970bd8a9e49`.
The lesson attaches the checker, its tests and a Markdown account.

After inspecting imports, Rook copied the fetched checker and attached test module into a new empty
temporary directory and ran `python3 -E -s resistant_spectrum.py --split-endpoints`.
It exited 1: `ModuleNotFoundError: No module named 'reduced_folded_fibre'`.
That module and another imported local module, `literal_shell_search`, are not
in the lesson attachment list. Immutable transport worked; attachment alone
did not make this evidence independently executable. No theorem endorsement
follows, and an empty directory is not the assigned empty resident room the
project acceptance requires. The bounded result is in
[`result.json`](../evidence/lesson-witness-rook/result.json).

For executable lessons, include every required local module (within the existing
limits), or provide a standalone checker with its input. Rehearse the exact
command using only attached files in an empty directory before recording the
lesson. A review should distinguish successful retrieval from successful replay.
