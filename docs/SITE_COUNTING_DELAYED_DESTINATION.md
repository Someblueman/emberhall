# Run-ledger links after deferred history loads

Hawthorn, 28 November 2026. Task `site-counting-delayed-event-destination`.

An older-event button in the Counting Room focused its destination immediately,
while the initial small snapshot was still loading full history. The eventual
redraw removed that focused node. Native phone and desktop trials ended with
no focused element. This is separate from the already delivered snapshot and
Gallery repairs; no repair-list item was reopened.

`visitCountingMoment` now focuses and scrolls in `jumpToSequence`'s completion
callback, after the destination is mounted. Handoff trips reopen the mounted
disclosure. If the run button is absent, the ledger receives focus; if the ledger
is absent, the room record does. A cancelled navigation never runs this callback.
The existing return trail restores the original filters, page and run button.

Verification: 48 focused tests passed (Counting history, work trail and room;
snapshot refresh; house navigation; bookmarks; composed rooms). The delayed
regression failed before the change and passes after it. Added regressions cover
mounted focus and scrolling, cancellation, and an absent destination ledger.
JavaScript syntax and whitespace checks pass. After adding the native-fixture
helper, the nine history-return tests passed again.

Native fixed-channel requests use this run's prefix
`225c945c6bbc4ba9950aa45a3622854f-`, suffixes `counting-before`, `counting-after`
and `counting-return`. At 390 and 1280 pixels: before, focus was absent after the
jump; after, it was on the mounted `counting-runs` region; returning focused
`counting-jump-6`. Both completed patched trials had zero script errors and no
page overflow. Opened phone and desktop screenshots: displayed material is
legible and contained. The phone image cap excludes the lower ledger; focus is
verified by native output, scrolling by the regression, not by that screenshot.

Reproduce in a disposable `build/` page using
`tests.test_counting_history_return.write_deferred_fixture('build/ledger.html')`.
Click `#room-link-counting`, then `#counting-jump-6`, wait 800 ms; optionally
click `#counting-history-return`. It uses retained historical frames with an
explicit synthetic run and Counting Room, delaying history by 250 ms. This is
a controlled renderer trial, not public delivery or an actual historical run.
Independent integration and public verification remain.

SHA256:
- `site/house.js`: `3e9b50414d3be52da657cafd738e0f4ec0e93972da2bcb0e425b9ce847086d7e`
- `tests/test_counting_history_return.py`: `9a4cd17e4222f2bc4e5198cf370af8634b8f524a1b5d1f79d0877df714724945`
