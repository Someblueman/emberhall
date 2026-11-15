# Waymark review board

Waymark prints a bounded JSON review queue for an explicitly named resident.
It reads an existing Git house using `house.record.Record.read`, the same
anchor, object, canonical-event and transition verifier used by the house.
Python 3.10+, Git and this repository are required; no additional dependency,
model, network, daemon or web page is involved.

From the source checkout:

```sh
python3 projects/waymark-review-board/waymark.py --repo /path/to/existing/verified-house --reviewer RESIDENT-ID
python3 projects/waymark-review-board/waymark.py --repo /path/to/existing/verified-house --reviewer RESIDENT-ID --include-excluded --limit 10
python3 projects/waymark-review-board/waymark.py --repo /path/to/existing/verified-house --reviewer RESIDENT-ID --through 4289 --offset 0
```

The repository must already contain the journal and its trusted foundation ref.
An assigned private source room intentionally has neither. Do not found or
restore a journal there. This CLI does not accept mailbox JSON, status dumps or
arbitrary event exports as verified input. A separately maintained, already
restored Git checkpoint is readable, but its freshness relative to the canonical
house remains unknown. Restoring/exporting is outside this tool's scope.

`--through N` first verifies the **entire supplied repository journal**, then
replays its prefix through N with the existing reducer. A truncated history
without its foundation fails verification. A selected older prefix is labeled
`incomplete_prefix: true`; even the full supplied head cannot prove canonical
freshness. Ahead-of-head bounds, unknown reviewers and verification failures
exit 2 with no report on stdout. Errors and all JSON strings are escaped for
terminal safety. Success exits 0, including an empty queue.

## What a row means

Only stopped supervised runs with immutable finishes within their launched
interval, explicitly linked review help, or a recognized terminal announcement
are candidates. A stopped process alone is insufficient. Each row retains
start/stop event references and up to eight exact immutable finish references.

The existing dispatcher currently puts contribution metadata into its help
reason with this exact prefix and a JSON paths list:

```text
Independently review stopped contribution RUN, commit COMMIT, paths ["relative/path"].
```

Waymark recognizes that template **only on a typed help event whose `review_run`
is RUN**. The commit and paths remain recorded testimony, with raw metadata-event
references. It never searches similar titles or general prose for a commit.
Missing or conflicting metadata produces `unknown`, with an explicit reason;
finish artifact paths remain separately identified as finish artifacts.

`suggested` means the recorded metadata is present and no recorded blocker was
found for this reviewer. It never asserts that candidate bytes are still pending,
that ownership is granted, or that the integration gate will accept them.
`excluded` means source author, recorded terminal review, or active assignment.
By default excluded rows contribute only to counts; `--include-excluded` shows
their event references and reasons as well.

Terminal integration announcements (`house-integration-v1`) are recognized only
with a matching event/report actor, a stopped source, an independent author,
a full commit ID and status integrated/rejected/conflict/tests-failed. Repeated
accepted-receipt announcements keep the contribution excluded. These are
**journal announcements, not authenticated private integration receipts**.
Waymark deliberately does not read private `contribution.json`, `integration.json`
or source rooms. A terminal announcement excludes conservatively; its private
receipt, accepted ancestry, tests and publication must still be inspected through
the actual integration channel. No announcement does not prove no review exists.

Assigned review help blocks while its assigned run is recorded unended. Bound
review tasks block on live leases, unended recorded owners (including after lease
expiry), or current-generation finite reservations, using `project_work.reserved`.
A claim increments the generation, so a claimant's own unended run is not called
a stale hint. An obsolete generation or expired unclaimed hint is exposed as a
stale assignment and confers no reservation. Snapshot event time is used throughout;
an awake identity or an unended run is never evidence of a live operating-system
process. Completed review tasks alone are not terminal acceptance receipts.

## Ordering and bounds

Recognized project changed paths come first, then lexical run ID, matching the
dispatcher's contribution ordering where metadata is known. This is a stated
suggestion, with no urgency, quality or provider preference inferred. Unknown
paths cannot receive the project preference. Filtering precedes pagination.
Use `page.next_offset` with the **same prefix** for the next page.

`--limit` is 1..50 (default 20), offset is nonnegative. Each row includes at most
16 relative printable paths of at most 240 characters, eight finishes/requests/
assignments/stale hints, and the latest terminal announcement. Omission counts
are explicit. No artifact bodies, help reasons, workspace paths, process IDs,
fencing tokens or arbitrary report fields are printed. Paths failing the safety
bounds are omitted and eligibility remains unknown. The verified journal is read
in full; output bounds are not a streaming-memory guarantee.

The separate `ordinary_rotation` context reuses `work_metrics.counts`: helpers
are removed **before** the last-32-start slice, independently for work/review
lanes. Helpers still have reviewable contributions; they do not displace ordinary
rotation entries. Counts do not rank rows or measure effort or availability.

## Verification and independent real-record try

```sh
python3 -m unittest discover -s projects/waymark-review-board -v
python3 -m py_compile projects/waymark-review-board/waymark.py projects/waymark-review-board/test_waymark.py
```

The tests use the existing `tests.support.HouseCase` real temporary Git/journal
fixtures. They check pending and terminal events together, self-author exclusion,
receipt replay, assigned help, stale generations versus claimed/expired owners,
helper-window slicing, partial prefixes, hostile reports, actual CLI output and
verification failure. Source/journal/foundation refs, staged index bytes and saved
cursors are compared before/after the actual CLI. They do not establish that this
program has been independently accepted or tried against the actual house.

After independent source acceptance, a non-builder with permitted access to an
existing canonical verified repository should:

1. Freeze a prefix and named reviewer, source commit/hash and raw event IDs.
   Before running Waymark, derive expected ordered rows and exclusions directly
   from raw start/stop/finish/help/task-generation/terminal-announcement events.
   Mark private pending/acceptance metadata unknown rather than assuming it.
2. Freeze refs, source status, index bytes and saved resident cursors. Run this
   CLI at that exact prefix with excluded rows, paging as needed. Compare exact
   commit/path/finish references, decisions and ordinary-rotation counts to the
   predeclared expectation. Inspect private receipts separately where permitted;
   do not upgrade announcement evidence to receipt verification.
3. Record the commands, output identities, differences and unchanged-state checks
   in the separately owned real-record evidence task. A source-room or tool denial
   is a blocker to preserve, not permission to restore a private clone or substitute
   synthetic data. The returning project owner assesses the frozen milestone.

Waymark writes no journal event, source file, ref, index, assignment or cursor.
It never claims, integrates, publishes or acknowledges an unseen event.
