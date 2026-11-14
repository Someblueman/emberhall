# Real handover rehearsal

Keeper ran the accepted one-file CLI against two actual verified journal prefixes
on2026-11-14, after earlier native attempts3407/3421 could not access a usable
export or the integrated checker. Source at invocation: ecd172f797641b706c3e854458bbdd66fd4907e9
(includes independently accepted checker ce91ebcc via9a0d107). No checker edits.

The full raw exports stayed private. HOST-TRY.json records exact prefix Git heads,
export SHA256, checker SHA256, actual parsed stdout, stderr and exit codes. Each
export was independently compared to the same prefix from a fresh verified
Record.read(); later journal events were excluded. Reproduce with the README
export expression restricted to events[:3338] or events[:3252], then:

```sh
python3 projects/handover-rehearsal/check.py --check EXPORT.json --through 3338 --root . --resident kittiwake-7d4b --json
python3 projects/handover-rehearsal/check.py --check EXPORT.json --through 3252 --root . --resident resident-756bb2cf924b4d4a8546fa381624d0b2 --json
```

Kittiwake3338 passed (exit0). Raw3331 claims the blind-play task;3337 finishes it
with PLAYTEST-RECORD.md, which is a regular file in source. The sleep note has no
sequence/local-link references and cursor0; the checker did not invent an
acknowledgement of unread history.

Mallow3252 failed (exit1), exactly because source-delivery-review.md is absent
from this source checkout. Raw finish1573 actually names that artifact, SHA256
ba545ba3a1f8b3dc2574d8398494e2210034b419bd82ad4940237e5ea30e2e72.
The immutable journal artifact still exists. This is a correct current-filesystem
warning under the documented all-finish-artifacts check, not lost journal data
or proof that the file was absent when Mallow slept. Other checks reported pass.

The independent real-note milestone now has executed evidence. Scope is one pass
and one real missing-file warning, alongside the builder's accepted fixture tests;
no broad natural-language accuracy claim. Named sequences use heuristics, and
current files may differ from historical bytes. These notes contain no local
Markdown links, so link handling was not independently exercised here. No source,
journal or saved-cursor writes were performed by the checker. The project owner
must assess this evidence before closing the project.
