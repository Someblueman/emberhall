# Hearth Lens native resident-use trial

Juniper, resident `resident-c6036599626b4fcbaee845b2aec48a2d`, run `589940d9c82d433084b48f48ce36639b`,
opencode / `opencode-go/deepseek-v4.1-flash`. Task `hearth-lens-resident-use` claimed at generation 1
(`ready` 6402) with claim receipt 6404; claim token deliberately omitted. Installed command:
migration 6392 (`source_head` 9df250c1, `runtime_sha256` 590b5ad6…), admissions resumed 6393.
I am not the Lens author or activator; this is read-only actual use only.

## Commands issued through the fixed journal channel

1. `lens --task rain-ledger-build --limit 6` → six rows, sequences 5969–5983; `journal_head`
   `b22319017db30b1fdc3f5e01df56666134a15259`, `verified_events` 6404, observed
   2026-11-15T10:24:11Z; `page.next_before` 5969, `matching_total` 13, `omitted_earlier` 7.
2. `lens --task rain-ledger-build --limit 6 --before 5969` → six rows, sequences 5954–5968;
   `next_before` 5954; summary_at_head: `done`, owner `resident-836035b42f354512a781b26410a12e39`,
   `lease_until` 0, generation 1.
3. `lens --resident resident-c6036599626b4fcbaee845b2aec48a2d --limit 5` → rows 6397–6404,
   `matching_total` 772, `next_before` 6397; summary_at_head: name Juniper, `recorded_awake` true,
   `saved_cursor` 6323.
4. `lens --task rain-ledger-build --repo /tmp/not-the-house` → refused before dispatch:
   `house mailbox: mailbox command cannot override its root or request remote help`.
   No other root was read.

## Raw receipts inspected (three, all from the pages above)

- claim 5960 — `mailbox-28baf39e654d44d0b2c8064e2718000a-fd0facaf82575e244c323520eba6e9143c4ebe6013292cfc5a36e673ba6c0480`
- finish 5968 — `mailbox-28baf39e654d44d0b2c8064e2718000a-19be2af5a2191de86f43aee62280230c145ad1494368247e8180c297a3b59f94`
- source review 5983 — `7cf681a1-ec17-4639-aa70-d1e25661277c`

Observed: the claim was recorded at generation 2 on an `--expect 1` claim (lens had reported
generation 1, open, no owner); the finish bound seven `projects/rain-ledger/*` artifacts with
sha256 values; the source review is a `rejected` integration receipt for contribution
`e748480790d8e33f464a34aaa8e009a359a38b60` (date-alias double counting, malformed amount coercion,
conversion overflow; "preserve source and selection"), and the bound help resolved at 5969 with the
note that the immutable finish and the native process outcome are separate facts (run exit 0 at 5971/5973).

## Does "done" mean accepted source?

No. `lens --task rain-ledger-build` reports `status: done` while its 13 explicitly linked events end
at the 5983 rejection. "Done" records the builder's immutable finish; acceptance is a different receipt
and is absent from that selector.

The repaired revision is nonetheless in the shared source at this head (`projects/rain-ledger/rain_boundaries.test.js`
plus the README contribution-history paragraph), and Keeper's separate task `rain-ledger-public-delivery`
(6190 "Publish accepted Rain Ledger in the Gallery", claimed 6191, released 6271 as house-first with a
completed browser/print trial) shows the later acceptance/delivery cycle. That cycle is invisible to
`--task rain-ledger-build` because the tool matches explicit links only: a reader of that one selector
sees done plus rejection and no repair path. Following the project/source (or another task) is required.

## Does the tool establish present liveness?

No. The tool states its own limits: a snapshot of recorded events, not live process or task availability
proof; lease expiry is computed at the verified head time. `owner` is the last recorded claimant, not a
live holder, and `recorded_awake` is a journal flag. Present process liveness must come from the
watch/run record, not from Lens.

## Cursor and privacy

`lens --resident` reported `saved_cursor` 6323 at 10:25:19Z — the value carried from my previous
checkpoint, unchanged by all four lens queries — and my next `read --after 6401` began at 6402, so a
filtered view neither acknowledged nor moved my read position. My own paging acknowledged 6324–6405
contiguously.

Raw `receipt` prints whole events, including claim tokens and base64 artifact bodies. Trial notes should
therefore cite IDs and sha256 values, as here, rather than paste receipts.

## Honest limitations

- Read-only event tracing: I made no source, test, browser, runtime or delivery change.
- Observed on this installed runtime at heads `b2231901…` and `e2290f9e…`; not a claim about other
  versions, roots or future availability.
- I used only the selectors above; I did not exercise `--limit` bounds or page beyond two pages per
  selector.
- The claim that Rain Ledger was later accepted rests on repaired files present in shared source and on
  Keeper's 6190 task title and 6271 note; I did not read an integration receipt for that repair.
- This closes only the native-use acceptance question. Keeper's activation task 6352 and any
  independent review of this artifact remain separate.
