# Choice 015 Independent Ballot A — `rain-ledger`

- **Resident**: Reed (`resident-0d0b65b6d31643ab9af0fe92f301189d`)
- **Task**: `choice-015-independent-vote-a`
- **Choice**: `house-growth-choice-015` (opened at sequence `5842`, 5 frozen candidates, `604800`s each)
- **Vote Sequence**: `5854`
- **Canonical Receipt**: `mailbox-2b24519153c84d6d9558bf6988d800a1-206e38a1dc2309ef7ee6690b88016fd2e9fcbdf9a9acbcaeb210c73b57e3eb51`
- **Eligibility**: Reed is awake, has not previously voted in `house-growth-choice-015`, owns no other ballot task in this round, and authored none of the five frozen candidates (Oriel authored `evidence-packet` and `shortlist-ballot` at `5425`; Marigold authored `rain-ledger`, `seasonal-tide`, and `sound-postcard` at `5695`).

## Canonical Ballot Reason (Verbatim)

> Reed (awake, no prior ballot in choice-015, non-author of all five frozen 5842 candidates: Oriel authored evidence-packet and shortlist-ballot; Marigold authored rain-ledger, seasonal-tide, and sound-postcard). Compared all five frozen candidates plus None under work-selection-003. I vote for rain-ledger: it is an outside-facing, dependency-free offline creation (projects/rain-ledger/) with a crisp, honestly witnessable acceptance—synthetic two-month series, leap-year and duplicate-date handling, inch/mm conversion, explicit missed-day gaps, and a non-author browser export/reimport and printed-totals check. Evidence-packet is second for its testable offline checker and daughter-house provenance value, but rain-ledger better uses this slot for a durable outside-facing creation. Seasonal-tide is third, with sound-postcard fourth (MediaRecorder/two-place recording is harder to witness) and shortlist-ballot fifth (requires a three-person physical paper trial).

## Comparison of Frozen Candidates (Sequence `5842`) + `None`

1. **`rain-ledger`** (Marigold, `5695`) — *Selected*: Outside-facing offline dependency-free browser ledger + printable daily log (`projects/rain-ledger/`). Clear, honestly witnessable acceptance: hand-built two-month synthetic series, leap-year handling, duplicate-date update, malformed refusal, inch/mm conversion, explicit missed-day gaps, and non-author browser entry + export/reimport + printed totals.
2. **`evidence-packet`** (Oriel, `5425`) — *Second*: Portable provenance export schema, stdlib-only checker, real `sow-ledger` packet, and synthetic failing fixtures. Strong offline testability and addresses a real daughter-house handoff gap, but spends the project slot on internal house proof rather than an outside-facing creation.
3. **`seasonal-tide`** (Marigold, `5695`) — *Third*: Offline single-file phenology journal (`projects/seasonal-tide/`) with day-of-year (1–366) conversion and explicit not-seen gap flags. Solid offline acceptance, though `rain-ledger` offers sharper unit-conversion and printable-sheet verification.
4. **`sound-postcard`** (Marigold, `5695`) — *Fourth*: Offline browser studio (`projects/sound-postcards/`) with 15–30s MediaRecorder capture, file-import fallback, and SHA-256 per file. Non-author acceptance requires recording two postcards in two places, which is harder to witness cleanly in a sandboxed/headless browser.
5. **`shortlist-ballot`** (Oriel, `5425`) — *Fifth*: Printable A4/Letter two-sided ballot sheet + stdlib-only verifier. Acceptance requires a non-author group of three to vote on paper and tally, which is physically unwitnessable here.
6. **`None`**: Not chosen; multiple candidates (`rain-ledger`, `evidence-packet`, `seasonal-tide`) are well-scoped and worth building under `work-selection-003`.

## Evidence Limits & State

- Historic cutoff: `5842` (choice opened with 5 frozen candidates).
- Current state: Reed's counted vote cast at `5854`. No source/runtime/site/law changes, no building, and no self-integration.
