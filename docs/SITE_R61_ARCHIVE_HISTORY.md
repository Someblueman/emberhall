# R61: load earlier lesson changes from the Archive

Rook, 28 November 2026. Task `site-repair-r61-archive-history`.
Source candidate; independent integration and live acceptance remain.

Snapshot-first loading left Archive's “Follow changes” examining only the
current frame. It displayed that frame as the first available lesson view,
with its visit button disabled. Unlike the catch-up and room-growth panels,
it offered no way to load the older snapshots it needs.

The panel now explicitly says earlier changes are not loaded and offers the
existing validated history loader. After loading it shows the existing trail,
retaining search, comparison and lesson selection. Focus returns to the trail
when the visitor has stayed there; a different focused control keeps focus.
A failed load leaves an enabled retry button and a status message. Closing the
trail remains available before loading. No history is fetched merely by opening
the Archive or following a lesson.

Native controlled reproduction uses the actual page and renderer with two
lesson observations: event 1 has no review and event 243 has one. The initial
record contains only event 243; the history response contains both. Before the
repair “Follow changes” exposed only event 243. After repair, native clicks at
390 and 1280 pixels load both observations, visit event 1 and return to event
243. The search still holds “remember” and focus returns to the event 1 visit
button. Both full-layout trials report no script errors, unlabelled controls
or horizontal overflow. A separate inspection copy hides the preceding house
pane only, to bring the Archive into the phone screenshot limit.

Requests use this run's prefix `4f28dfe7d6444b5a8e5b3c79f1cd677b-`
and suffixes `archive-repro`, `archive-load`, `archive-return`, `archive-inspect`.
Fixtures and screenshots are disposable and are not deliverables.

45 checks pass across `tests.test_archive_lesson_trail`,
`tests.test_archive_lessons`, `tests.test_archive_return_recovery`,
`tests.test_site_refresh_scheduling`, `tests.test_current_house_snapshot` and
`tests.test_event_navigation`. The final Archive-only rerun passes 8 checks.
`node --check site/house.js` and `git diff --check` pass. An initial expanded
test command misspelled the current-snapshot module; the corrected suite is
the 45-check result above.

This is controlled offline behavior, not live-network acceptance. The public
listing at event 59482 was read successfully (SHA256
`817bda86f074603bfe7879b4e02886ec246f5c8aa3844547d4730ba87ade602b`),
but this room lacks the publication ref required to reconstruct its companion.
No matching-public-snapshot replay is claimed. The controlled lesson data is
explicitly constructed, not an observation of historical lesson events.

SHA256:
- `site/house.js`: `a6e5e52e085c56062c6823de2d76245fb9f92cdc3b3e1427df0b64ff46922ac2`
- `tests/test_archive_lesson_trail.py`: `0589fbf5426f60a02d11fb0235707c0b0c8d6f5521dd60a2aaf11ba767bdb8e8`
