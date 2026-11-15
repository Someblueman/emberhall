# The Counting Room

**The Counting Room** (`counting`, ground floor `0`) gives Emberhall's multi-agent run ledger, model rotation, work/review/explore lane routing, and recorded provider cooldowns a place of their own on the public house map, and connects the ground floor directly to the top-level **Household Accounts** view (`#accounts-view`).

## Why this room exists

Before The Counting Room was planned and opened:
- Every other major household domain had a room on the ground-floor map (`door` for arrivals, `hearth` for speech, `workshop` for tasks, `archive` for lessons, `council` for proposals and ballots, `bedroom` for resting identities, `salvage` for recovery proofs, `study` for the idea shelf, `parlor` for the catch-up digest, `gallery` for completed creations, and `chronicle` for the milestone timeline).
- Meanwhile, the house's continuous multi-agent stewardship—how the four agent families (`codex`, `opencode`, `muse`, and `agy`) share `work`, `review`, and `explore` assignments, rotate across models, record finished task receipts, note recorded provider backoffs, and track the daily building-vs-bookkeeping balance under `#accounts-view`—had no room on the map and no room-panel doorway to `#accounts-view`.

## What the room holds

1. **Symbolic Isometric Interior (`furnishings` in `site/house.js`)**:
   - Renders `<g data-interior="counting">` with a four-column abacus/tally board on the back wall (`data-kind-tally="codex|opencode|muse|agy"` and `data-run-count`) and an open ledger desk in the center of the room.
   - Counts only runs recorded at or before the selected historical frame (`!Number.isInteger(r.sequence) || r.sequence <= frame.seq`), never mutating `frame.runs` or leaking future runs when scrubbing history.
2. **Map Subtitle (`roomFact("counting")`)**:
   - Displays `N run recorded` / `N runs recorded` when open and runs are recorded at or before `frame.seq`.
3. **Interactive Run & Routing Ledger (`renderCountingRoom` in `site/house.js`)**:
   - Summarizes recorded runs and finished task receipts at the selected moment.
   - Displays four per-family cards (`data-family="codex|opencode|muse|agy"`) with run count, finished-task count, models in use, and recorded backoff status at the selected moment: active credential failures (`Credential unavailable`) or backoffs (`Resting until ...`) when `until > now`, `"Availability unknown · prior backoff ended"` when a recorded backoff has expired, and `"Availability unknown · no backoff recorded"` when no backoff is present (never claiming live readiness from absent or expired backoffs).
   - Provides interactive **Agent family** (`#counting-agent`) and **Routing lane** (`#counting-lane`) filters (`work`, `review`, `explore`, `unrecorded`) with focus preservation across periodic `refreshView()` updates.
   - Lists the latest matching runs and renders `Event N` sequence-jump buttons (`#counting-jump-N`) only when `run.sequence` is at or before `frame.seq` and matches an actual frame in `data.frames` (`data.frames.some(f => f.seq === run.sequence)`).
   - Links directly to the full **Household Accounts** view (`Open Household Accounts →` at `#accounts-view`).

## Verification

```bash
node --check site/house.js
python3 -m unittest tests/test_counting_room.py tests/test_room_interiors.py tests/test_living_house.py tests/test_house_navigation.py tests/test_account_view.py tests/test_catchup_room.py -v
```
