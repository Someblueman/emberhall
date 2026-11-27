# Open an event that is already loaded

Aster, 27 November 2026. Source candidate; independent integration remains.

The event-number form requested full history even for the latest event already
present in the small current snapshot. With history unavailable, entering 243
on a loaded event-243 page produced “Try again when the house history is
available.” The native viewer reproduced this at 390 and 1280 pixels.

The form now opens that loaded latest moment directly. Numbers beyond the
published upper bound receive the existing range error without a history
request. Older events still load history. The direct latest jump cancels an
older pending jump; an older frame retained after a failed refresh does not
qualify as the latest snapshot.

Checks:

- 38 focused tests pass across event navigation, snapshot refresh, room
  bookmarks, catch-up rooms/paging, Workshop history, Counting history return,
  and public history. A regression assertion failed against the original code:
  opening the loaded latest event called the history loader once, rather than
  zero times. One initial test invocation included a nonexistent module name;
  the corrected eight-module run passed.
- JavaScript syntax and `git diff --check` pass.
- Native viewer before/after uses the real page and renderer with the old
  checked-in 243-event fixture, not today's public record. Older history is
  unavailable in the current-event fixture. After the repair, both widths say
  “Opened event 243, the latest published moment” with no script errors,
  unlabelled controls or page overflow. A history request in the repaired
  fixture deliberately throws, so it cannot silently satisfy this lookup.
- Additional native trials at both widths reject event 244 with the range
  1–243 and open event 1 when the full old fixture is available. Both have
  zero script errors, unlabelled controls and page overflow. Phone range-error
  and desktop historical-page screenshots were inspected.

Viewer requests use this run's prefix `1594a1d462534f41939db572ca00c9c3-`
and suffixes `event-before`, `event-after`, `event-future`, `event-history`.
Fixtures and screenshots are disposable and are not deliverables. Recreate
with `tests.test_gallery_catalog_recovery.write_fixture(..., failures=0)`;
select House, fill `#event-number`, and click `#event-open`.

Source SHA256:

- site/index.html: `7f0c4ca079d0cc1463694eaac26d3f2ddd176ef8929d30cb4143990932cfe472`
- site/house.js: `6221878c50b92c49ea12109e20d594c7636adccdbcd2afbf86fc9ced86a84eb6`
- tests/test_event_navigation.py: `4627651ea84992ffbccc9def6b0c4b54b828255465d102f7e1798418eb9a0392`

Review only these three files and this note. No publisher/runtime change or
repair-list acceptance is claimed.
