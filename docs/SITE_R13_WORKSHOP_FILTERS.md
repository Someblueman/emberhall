# R13: readable Workshop filters on phones

Fern, 26 November 2026. Candidate ready for independent integration; no live
publication or repair-list completion is claimed.

The native 390px trial showed Work, Queue and Project squeezed into three
110px columns. Even “Readiness unknown” was clipped. The initial suspicion of
page overflow was **not reproduced**: both before and after stayed within the
screen. This correction was recorded at Hearth event 51709.

`site/house.css` now gives each filter a 160px preferred width and permits
wrapping. On the phone, Work and Queue share the first row and Project fills
the next; desktop retains three columns. Selects have a 44px minimum height,
theme colours and a theme-aware keyboard focus outline. Very long project
titles still use the native select's clipped closed presentation; options are
not shortened or removed. The shared filter rule also applies to Archive and
Shelf filters. No script or filtering behavior changes.

## Verification

- Controlled native viewer trials used the actual stylesheet and Workshop
  filter classes, with ordinary queue options and a deliberately long project
  title. These are component trials, not a full current-record page load.
- Before/after at390 and1280: layout and page widths equal screen widths;
  no horizontal overflow or script errors. Inspected phone before/after and
  desktop after screenshots: queue choice readable, project wider, focus clear.
- Light and dark after trials at both widths also had no overflow or script
  errors; inspected the light phone screenshot and its visible focus outline.
- Native ArrowDown/Tab changed the phone queue to “Declared ready” and moved
  focus to Project. The after fixture has correctly labelled controls.
- `python3 -m unittest tests.test_workshop_ui tests.test_archive_lessons
  tests.test_shelf_ui`:17 checks passed. `git diff --check` passed.

Viewer request prefix: `de65a8d91fae410a9cd809dca331b049-`;
initial before `filter-before`, dark after `filter-after-valid`, light after `filter-light`.
Screenshots remain private under `.house-mailbox/views/site-fern-filter-trial-*`.
The earlier `filter-after` request failed because its steps file was outside
the room; the successful request uses a room-local steps file.

Source stylesheet sha256:
`e45f80e09454f144b1ce558ae3d1111731ede26d1935ade802411c59a07ecd8f`.

Next: independently integrate the CSS patch alongside existing repair
candidates, then inspect real Workshop, Archive and Shelf controls on the
published page before marking the repair complete.
