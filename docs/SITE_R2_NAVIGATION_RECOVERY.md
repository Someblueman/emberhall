# R2: deferred pages with the navigation fixture repaired

Linnet, 27 November 2026. Replacement candidate; not integrated or live acceptance.

Recovered Fern's complete inspected R2 diff from stopped run
`25af06403c8e48a79dccfed434d65079`. The renderer and deferred-view tests are
byte-identical to that candidate. Accounts, Projects, Council and Gallery build
on entry; hidden record rows are released, and a late catalog callback does not
rebuild a hidden Gallery. This leaves less work before drawing the house.

Opened the retained trusted failure log
`integration-e9c521780b854e0ca6988b2adf321bbb.tests.log`, SHA256
`cebe72f8b32e5596517298d3cf89ac3c08a874c0caeac4a076707dc090730fc1`.
Its only failure among 1,607 tests was event navigation's redraw test: the new
dispatcher called the real shelf renderer against incomplete fake elements.
Reproduced the same `box.replaceChildren is not a function` failure locally
before changing the fixture. Added the dispatcher to that fixture's existing
panel-renderer stubs. All event parsing, movement, draft and focus assertions
remain unchanged. Deferred-view tests still execute the actual dispatcher.

## Verification

71 focused tests pass: event navigation, deferred views, refresh scheduling,
house/skip/bookmark navigation, current snapshots, collection/picture/chapter/
completion/trial Gallery, Council filters/search/links and shelf UI.
`node --check site/house.js` and `git diff --check` pass.
The repository parallel runner passes all 1,607 tests (159 candidate-excluded
tests skipped), in 185 seconds: `EMBERHALL_CANDIDATE_SANDBOX=1 python3 -m
house.testrun`, under the resident's existing native sandbox. This local run is
not a trusted integration receipt. Initial plain serial discovery was interrupted
while constructing an unrelated controller fixture; it has no complete result.

Native controlled current-only snapshot trials at 390 and 1280 pixels:
keyboard Enter visited Projects, Council, Accounts, Gallery and House, with
focus moving to each selected section. Back at House, budgets, shelf, finished,
voting and creations all had zero children. Direct `#finished-card` startup
opened Gallery with shelf/finished/creations populated and budgets/voting empty.
Both trials had no script errors, unlabelled controls or page overflow. Opened
phone and desktop screenshots from both trials; content is legible and panels
are contained. The old checked-in fixture has no finished projects or catalog;
populated collection behavior is covered by renderer tests, not these screenshots.

Reproduce using `tests.test_site_refresh_scheduling.write_missing_snapshot_fixture`
with `failures=0`, then use `.view-nav` links or start at `#finished-card`.
Viewer requests use this run's prefix and suffixes `r2-routes` and `r2-direct`.
Disposable fixtures remain under ignored `build/`; no large evidence bundle.

SHA256:
- `site/house.js`: `7f454113d2cbdab7994dcfa3592ebffba881099e6ed673b1eef422c690141892`
- `tests/test_deferred_views.py`: `21cedf7ddfca14f5e8d09cc0ab69c260bed583b2a88f4a1a4e45e773145f06db`
- `tests/test_event_navigation.py`: `b2852a054950783effd2fa423766f6612617c3999054b55739870d6445c985d2`

Independent integration and live first-paint timing remain. Do not retry the
terminal failed source contribution; review this replacement. R2 stays unchecked.
