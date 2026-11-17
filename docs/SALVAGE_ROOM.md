# The Salvage Room

The open room now holds a six-decision practice bench. Visit **The Salvage Room**
on the house map, or use `#room/salvage`. The exercise uses the existing
[Blackout Kit recovery drill](../projects/blackout/examples/recovery-drill/README.md):
a missing winter record, changed invoice, ambiguous duplicate, case-only rename,
same-size corruption and lost letter. All names and bytes are invented.

Compare each target's expected fingerprint with the surviving copies. Choose a
copy or **No matching copy survives**. The answer explains what the match can and
cannot establish; numbered tiles track checked decisions, **Next file** moves
through them, and **Start again** clears the rehearsal. The duplicate accepts
either matching copy while retaining the uncertainty about its origin. Finishing
all six reports seven files that can match and two that remain missing, rather
than pretending the archive is whole.

No files are uploaded or restored. Decisions live only in this page's memory and
survive ordinary house redraws. They are neither resident activity nor journal
events. The exercise appears only when the selected historical frame records the
room as open; the fixed synthetic archive is labelled as practice at every date.
It makes no claim about a backup owned by the visitor. Fingerprint prefixes are a
reading aid, not a replacement for Blackout Kit's full SHA-256 comparison.

The worksheet link opens the repository's complete copy-and-verify rehearsal.
It preserves the surviving archive and uses a fresh destination. A trusted
inventory is still necessary: byte equality proves neither authorship nor
provenance. The room's existing construction and opening receipts remain unchanged.

Verification: `python3 -m unittest tests.test_salvage_room` exercises all six cases,
checks fingerprints against actual surviving bytes and the retained plan, follows
wrong/right/ambiguous/lost choices and reset, and checks historical room gating.
Browser checks are recorded in the task's immutable finish, separately from source
acceptance and public delivery.
