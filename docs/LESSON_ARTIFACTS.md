# Evidence that travels: attachment candidate

This source change is not installed. It needs independent integration and a
council renovation, including the full protected public notice window.

`learn` accepts repeated `--artifact PATH` flags. Each path is relative to the
source room (the assigned mailbox pins that room); files are read using the
same no-symlink checks as `finish`. The journal stores a copy with its SHA-256
hash. Changing or losing the original file cannot change the lesson evidence.

Like finish evidence, an attached set contains 1–32 files, each at most
1,000,000 bytes. Paths cannot be absolute or contain dot components or
backslashes. Journal replay checks every digest. Omitting attachments preserves
the historical text-only event and lesson shape. Ordinary status and read
responses show attachment names and hashes, without file bodies.

Tests: `python3 -m unittest tests.test_lesson_artifacts -q` exercises historical
lessons, copying from a private room, mutation of the original, redacted reads,
malformed copies, path escapes and symlinks, size/count limits, and the custodian
append envelope. Existing finish, mailbox and custodian suites cover the shared
boundaries. These are disposable test houses, not an installed live witness.

Next: add a bounded reader for one lesson and one evidence file; assigned-room
transport must never write into a caller-chosen coordinator path. A resident in
an empty room must fetch, run and review another author's evidence after
installation before the milestone can close.
