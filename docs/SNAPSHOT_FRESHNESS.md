# Snapshot Freshness Cue

The public Emberhall page (`site/index.html`, `site/house.css`, `site/house.js`) now displays a compact `#snapshot-cue` next to `#house-clock` in the top `.eyebrow` bar:

- **Current view**: displays `Snapshot <time> · <age>` (using `data.observed_at` and `data.timezone`), distinguishing the exported snapshot time from the live wall clock without asserting process liveness or inventing error/online states.
- **History view**: displays `Event <time>` (using `frame.at` and `data.timezone`) to identify the selected historical event time.
- **Edge cases**: invalid or missing timestamps render `"Snapshot time unknown"` / `"Event time unknown"`; future timestamps render `"· ahead of clock"` rather than negative ages; `.clock-group` wraps cleanly on narrow/phone viewports.

## Verification & Limitations

- `node --check site/house.js` passed.
- `python3 -m unittest tests/test_snapshot_freshness.py` passed (2 tests, using Node.js to evaluate `snapshotCue` across just-now, minutes, hours, days, future, invalid, and history-view cases).
- **Limitation**: no live browser render or visual layout check was executed in this run.
