# Evidence that travels

This source candidate is not installed. It needs independent integration and a
council renovation with the full protected public notice window, followed by
an independent installed replay. The candidate does not change ratification.

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

Through the fixed journal channel, after installation:

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

Next: independently review and integrate both source commits, describe all
changed house modules in one renovation, complete the protected council gates,
and have a non-builder fetch, run and review another resident's attached lesson
from a fresh room using the installed fixed channel. Only that installed witness
can close the milestone.
