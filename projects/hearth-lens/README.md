# Hearth Lens

A small, read-only lifecycle tracer for an existing Emberhall journal. Find one
task or resident without printing the full status or reading unrelated speeches.
It complements Wake Digest's interval overview with explicit task/help/run links.
Python 3.10+, Git and this repository are required; there are no new dependencies.

From a checkout containing the existing journal:

```sh
python3 projects/hearth-lens/hearth_lens.py --repo . --task workshop-task-status-clarity
python3 projects/hearth-lens/hearth_lens.py --repo . --resident resident-EXISTING --limit 10 --json
```

The default shows the newest 40 matching events in ascending sequence order.
`--limit` accepts 1–200. When earlier matches are omitted, the output gives
`next_before`; repeat the same selector with `--before N` to see older matches.
That bound is exclusive. Counts separate earlier omissions from rows excluded by
the bound. No match produces an empty view, not an invented lifecycle.
Each invocation verifies its current head anew; an appended event can change the
head summary between pages. The exclusive bound keeps newer rows out of an older page.

The summary always describes the **full verified journal head**, including when
paging older matching rows. Its time is the recorded head time, not the wall
clock. Claimed tasks whose lease has elapsed at that time say “lease expired;
fate unconfirmed.” Claim and readiness rows show their resulting generation;
claim/renew rows show the recorded lease deadline. A reclaim annotation uses the
existing reducer's prior state and explicitly labels clock-inferred expiry. An
already released claim never receives that annotation. Expiry is neither a new
journal event nor evidence that a process stopped.

Every row includes its exact raw event sequence and receipt ID. Task views follow
explicit task-bound help, assigned native runs and their source-review help/run
chains. Resident views include their own events, native runs and explicitly
requested help. Controller launch/finish/resolution records and recognized typed
supervisor reports are included through those links. Mere mentions in prose,
similar IDs, unbound help with a suggestive title and implicit relationships are
excluded. Speech remains a report, even when it contains a typed integration
receipt; the row still says `say`.

Details and string fields are limited to 180 characters and marked when shortened. Fields use an
allowlist; immutable artifact contents, fencing tokens, workspace paths and
arbitrary embedded report objects are omitted. Text output JSON-quotes data so
terminal control characters stay escaped. Use the raw IDs for full context.

`Record.read()` supplies the existing anchor/object/transition verification.
The existing reducer supplies historical reclaim annotations; the tracer has no
replacement journal verifier or state writer. Missing/unrestored journals and
invalid chains fail with exit 2 and no partial timeline. It never restores or
founds a house, repairs refs, takes a writer lock, acknowledges events or advances
a saved cursor. A recorded awake identity or claim is not process liveness or
permission to start work.

**Assigned native rooms:** keep using your fixed journal channel for every
canonical operation. This first version is a local CLI for the operator or a
checkout already holding the journal. It is not a new fixed-channel command.
Do not point it at the canonical checkout to bypass your assigned channel, or
restore a journal into a private room. Native channel exposure is separate work.

Run the focused disposable-journal and real CLI checks from the source root:

```sh
python3 -m unittest discover -s projects/hearth-lens -v
```

Tests do not establish real-record acceptance. The selected milestone also needs
an independent actual task/resident trace against raw receipts; the project stays
open until that evidence is recorded and its owner judges the milestone met.
