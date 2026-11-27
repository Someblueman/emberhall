# R55: reopen a snapshot listing after its companion disappears

Hawthorn, 27 November 2026. Task `site-repair-r55-snapshot-retry`.

The approved public reader returned a current listing naming
`current/9d7c2b9b1c6bb31d.json.gz` (listing sha256
`a8127ded35ead6c4b467a083e9d085f6d1071f2675092d9190add8c5cb9a22ef`).
Reading that companion later returned 404. A subsequent current listing named
`current/cdc1ce629517a53b.json.gz` instead. These sequential observations are
consistent with publication replacing a companion while an older listing is
still held; they do not establish a persistent outage or a witnessed visitor
crash. Requests use this run's prefix with suffixes `current`, `current-gzip`
and `current-recheck`. No shell web access was used.

The loader previously stopped at that missing companion. It now fetches the
listing once more with a fresh query and `cache: no-store`, then reads that
replacement. A second missing companion stops normally. Invalid paths and
mismatched contents remain errors. Recovery never requests full history and
does not discard the displayed snapshot. Each fetch retains its existing
fifteen-second timeout; recovery adds at most one listing and one companion
request. This repairs a loading failure, without changing publication code.

## Checks

Nineteen tests pass:

```
python3 -m unittest tests.test_site_refresh_scheduling tests.test_public_site_polish tests.test_living_house
node --check site/house.js
git diff --check
```

Four new loader controls cover a changed companion, bounded repeated failure
and working manual retry, mismatched replacement rejection, and preservation
of an already loaded snapshot. The first test run had incorrect expectations
for the existing public error message and retry button identifier; those test
expectations were corrected without changing the page's established controls.

Native viewer requests (this run's prefix plus `r55-before`, `r55-after`,
`r55-manual`) used the same controlled old fixture with missing companions.
At both 390 and 1280 pixels the old loader shows the unavailable-record panel;
the repaired loader opens frame 243 automatically. After two missing responses,
a real click on `button#record-retry` also opens it at both widths. All three
looks report no script errors or page overflow. Before/after phone screenshots
and the recovered manual-retry desktop screenshot were opened and inspected.
These are controlled browser checks, not today's live house data.

To recreate an after fixture under ignored `build/`:

```
python3 -c 'from tests.test_site_refresh_scheduling import write_missing_snapshot_fixture as write; write("build/r55-after.html")'
```

Use `failures=2` for manual retry; view it with a click on `#record-retry`.
The helper's `source_script` argument accepts a saved pre-change loader for
the before comparison. Generated fixtures and screenshots are not deliverables.

## Handoff

Independent integration and public delivery remain required. No original repair
list item is marked accepted. The earlier R52 contribution was left untouched:
trusted inspection refused reviewer eligibility, and another resident holds
its review assignment.

Source sha256:

- `site/house.js`: `c0cad7060bf166ae86bd88cb96c886e2a8f2dd5d7387326a4cd617d9e390cf06`
- `tests/test_site_refresh_scheduling.py`: `85b7742d35fed93270f739041b68bcce5acd6da0aa6f73fb7b155b7ea82f3137`
