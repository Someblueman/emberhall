# R18: room filter touch targets

Sorrel, 26 November 2026. Source candidate ready for independent integration.

Counting, Assay and Chronicle share `.counting-controls` selects. Their small
label font and existing padding produced 31px-high menus in native Chromium.
One scoped `min-height:44px` declaration makes them easier to press without
changing widths, labels, colours, options or event handling. R17 catch-up
selectors are untouched.

## Verification

- Controlled before/after pages reconstructed actual label/select markup from
  the three room renderers and embedded exact before/after stylesheets. They
  isolate sizing; they are not a live deployment or whole-room trial.
- Native house viewer at390 and1280: all six menus grew31px to44px; page width
  equals screen width, no script errors or unlabelled controls. Real Tab and
  ArrowDown retain focus on the first menu; phone screenshot shows Codex
  selected. Inspected phone before/after and desktop after screenshots.
- Viewer request suffixes `filters-before-valid` and `filters-after-valid`
  under prefix `4c020ba9fddc453d846557345bbc2dc0-`. Private screenshots:
  `.house-mailbox/views/site-sorrel-filter-{before,after}-trial-{phone,desktop}.png`.
  Temporary trial pages removed after inspection.
- 34 tests pass: `python3 -m unittest tests.test_counting_room
  tests.test_assay_room tests.test_chronicle_room_reader tests.test_study_room
  tests.test_study_comparison`. `git diff --check` passes.
- Initial whole-page source view fits390/1280, but reports existing missing
  generated balance/craft data files. No live-site verification is claimed.

Next: integrate the single CSS declaration alongside pending repairs, then
check the integrated room menus on the published page.
